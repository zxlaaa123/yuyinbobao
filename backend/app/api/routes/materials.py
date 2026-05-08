import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ...core.config import AI_MAX_SEGMENTS, AI_SEGMENT_SIZE, get_setting
from ...core.database import get_db
from ...models.knowledge_base import KnowledgeBase
from ...models.knowledge_point import KnowledgePoint
from ...models.material import Material
from ...schemas.material import MaterialCreate, MaterialUpdate
from ...services.dedup_service import build_existing_kp_title_set, normalize_title
from ...services.text_splitter import split_text
from .ai import _get_ai_service, _dump_json, _load_json

router = APIRouter(prefix="/api/materials", tags=["materials"])


@router.get("", response_model=list[dict])
def list_materials(knowledge_base_id: int | None = None, db: Session = Depends(get_db)):
    query = db.query(Material)
    if knowledge_base_id:
        query = query.filter(Material.knowledge_base_id == knowledge_base_id)
    materials = query.order_by(Material.id.desc()).all()
    result = []
    for material in materials:
        kb = db.query(KnowledgeBase).filter(KnowledgeBase.id == material.knowledge_base_id).first()
        result.append(_to_response(material, kb.name if kb else ""))
    return result


@router.post("", response_model=dict)
def create_material(body: MaterialCreate, db: Session = Depends(get_db)):
    if not body.knowledge_base_id:
        raise HTTPException(status_code=400, detail="请选择知识库")
    kb = db.query(KnowledgeBase).filter(KnowledgeBase.id == body.knowledge_base_id).first()
    if not kb:
        raise HTTPException(status_code=400, detail="知识库不存在")
    if not body.title or not body.title.strip():
        raise HTTPException(status_code=400, detail="资料标题不能为空")
    if not body.content or not body.content.strip():
        raise HTTPException(status_code=400, detail="资料正文不能为空")

    material = Material(
        knowledge_base_id=body.knowledge_base_id,
        title=body.title.strip(),
        content=body.content,
        source=body.source,
        note=body.note,
        material_type="text",
        content_length=len(body.content),
        extracted_count=0,
    )
    db.add(material)
    db.commit()
    db.refresh(material)
    return _to_response(material, kb.name)


@router.post("/import-and-extract")
async def import_and_extract(body: dict, db: Session = Depends(get_db)):
    knowledge_base_id = body.get("knowledge_base_id")
    title = (body.get("title") or "").strip()
    content = (body.get("content") or "").strip()
    source = body.get("source")
    note = body.get("note")

    if not knowledge_base_id:
        raise HTTPException(status_code=400, detail="请选择知识库")
    kb = db.query(KnowledgeBase).filter(KnowledgeBase.id == knowledge_base_id).first()
    if not kb:
        raise HTTPException(status_code=400, detail="知识库不存在")
    if not title:
        raise HTTPException(status_code=400, detail="资料标题不能为空")
    if not content:
        raise HTTPException(status_code=400, detail="资料正文不能为空")

    material = Material(
        knowledge_base_id=knowledge_base_id,
        title=title,
        content=content,
        source=source,
        note=note,
        material_type="text",
        content_length=len(content),
        extracted_count=0,
    )
    db.add(material)
    db.commit()
    db.refresh(material)

    enable_split = body.get("enable_split", False)
    print(f"[EXTRACT] enable_split={enable_split}, content_length={len(material.content)}", flush=True)

    segment_size_raw = get_setting(db, "AI_SEGMENT_SIZE", str(AI_SEGMENT_SIZE))
    max_segments_raw = get_setting(db, "AI_MAX_SEGMENTS", str(AI_MAX_SEGMENTS))
    print(f"[EXTRACT] segment_size_raw={segment_size_raw}, max_segments_raw={max_segments_raw}", flush=True)
    segment_size = int(segment_size_raw or str(AI_SEGMENT_SIZE))
    max_segments = int(max_segments_raw or str(AI_MAX_SEGMENTS))
    print(f"[EXTRACT] segment_size={segment_size}, max_segments={max_segments}", flush=True)

    if enable_split:
        segments = split_text(material.content, segment_size=segment_size, max_segments=max_segments)
    else:
        segments = [material.content]

    split_used = len(segments) > 1
    segment_count = len(segments)
    print(f"[EXTRACT] segments={segment_count}, split_used={split_used}", flush=True)

    ai_service = _get_ai_service(db)
    all_created = []
    skipped_count = 0
    existing_titles = build_existing_kp_title_set(db, material.id)

    for seg_idx, segment in enumerate(segments):
        print(f"[EXTRACT] processing segment {seg_idx + 1}/{segment_count}, length={len(segment)}", flush=True)
        try:
            result = await ai_service.extract_knowledge_points(
                knowledge_base_name=kb.name,
                material_title=material.title,
                material_content=segment,
            )
        except HTTPException:
            raise
        except Exception as exc:
            print(f"[EXTRACT] segment {seg_idx + 1} failed: {exc}", flush=True)
            raise HTTPException(
                status_code=500,
                detail=f"AI 调用失败（第 {seg_idx + 1}/{segment_count} 段）：{str(exc)}",
            )

        knowledge_points = result.get("knowledge_points", [])
        for kp in knowledge_points:
            if not kp.get("title"):
                skipped_count += 1
                continue

            normalized_title = normalize_title(kp["title"])
            if not normalized_title or normalized_title in existing_titles:
                skipped_count += 1
                continue

            point = KnowledgePoint(
                knowledge_base_id=material.knowledge_base_id,
                material_id=material.id,
                title=kp["title"],
                summary=kp.get("summary", ""),
                detail=kp.get("detail", ""),
                exam_points=_dump_json(kp.get("exam_points")),
                confusing_points=_dump_json(kp.get("confusing_points")),
                memory_tips=_dump_json(kp.get("memory_tips")),
                examples=_dump_json(kp.get("examples")),
                importance=kp.get("importance", "medium")
                if kp.get("importance") in ("low", "medium", "high")
                else "medium",
                tags=_dump_json(kp.get("tags")),
            )
            db.add(point)
            all_created.append(point)
            existing_titles.add(normalized_title)

    material.extracted_count = len(all_created)
    db.commit()

    return {
        "material_id": material.id,
        "split_used": split_used,
        "segment_count": segment_count,
        "created_count": len(all_created),
        "skipped_count": skipped_count,
        "knowledge_points": [
            {"id": point.id, "title": point.title, "importance": point.importance, "tags": _load_json(point.tags)}
            for point in all_created
        ],
    }


@router.get("/{material_id}", response_model=dict)
def get_material(material_id: int, db: Session = Depends(get_db)):
    material = db.query(Material).filter(Material.id == material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="资料不存在")
    kb = db.query(KnowledgeBase).filter(KnowledgeBase.id == material.knowledge_base_id).first()
    return _to_response(material, kb.name if kb else "")


@router.put("/{material_id}", response_model=dict)
def update_material(material_id: int, body: MaterialUpdate, db: Session = Depends(get_db)):
    material = db.query(Material).filter(Material.id == material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="资料不存在")
    if body.knowledge_base_id is not None:
        kb = db.query(KnowledgeBase).filter(KnowledgeBase.id == body.knowledge_base_id).first()
        if not kb:
            raise HTTPException(status_code=400, detail="知识库不存在")
        material.knowledge_base_id = body.knowledge_base_id
    if body.title is not None:
        if not body.title.strip():
            raise HTTPException(status_code=400, detail="资料标题不能为空")
        material.title = body.title.strip()
    if body.content is not None:
        if not body.content.strip():
            raise HTTPException(status_code=400, detail="资料正文不能为空")
        material.content = body.content
        material.content_length = len(body.content)
    if body.source is not None:
        material.source = body.source
    if body.note is not None:
        material.note = body.note
    db.commit()
    db.refresh(material)
    kb = db.query(KnowledgeBase).filter(KnowledgeBase.id == material.knowledge_base_id).first()
    return _to_response(material, kb.name if kb else "")


@router.delete("/{material_id}")
def delete_material(material_id: int, db: Session = Depends(get_db)):
    material = db.query(Material).filter(Material.id == material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="资料不存在")
    db.delete(material)
    db.commit()
    return {"success": True, "message": "资料已删除"}


def _to_response(material: Material, kb_name: str) -> dict:
    return {
        "id": material.id,
        "knowledge_base_id": material.knowledge_base_id,
        "knowledge_base_name": kb_name,
        "title": material.title,
        "content": material.content,
        "source": material.source,
        "note": material.note,
        "material_type": material.material_type,
        "content_length": material.content_length,
        "extracted_count": material.extracted_count,
        "created_at": material.created_at,
        "updated_at": material.updated_at,
    }


def _dump_json(value) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False)


def _load_json(value: str | None) -> list:
    if not value:
        return []
    try:
        return json.loads(value)
    except Exception:
        return []
