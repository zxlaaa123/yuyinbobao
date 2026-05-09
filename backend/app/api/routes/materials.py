import json
import time
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from ...core.config import AI_MAX_SEGMENTS, AI_SEGMENT_SIZE, get_setting
from ...core.database import get_db
from ...core.paths import UPLOAD_DIR
from ...models.knowledge_base import KnowledgeBase
from ...models.knowledge_point import KnowledgePoint
from ...models.material import Material
from ...models.question import Question
from ...models.answer_record import AnswerRecord
from ...models.wrong_question import WrongQuestion
from ...models.audio_file import AudioFile
from ...schemas.material import MaterialCreate, MaterialUpdate
from ...services.audio_service import delete_audio_file
from ...services.dedup_service import build_existing_kp_title_set, normalize_title
from ...services.text_splitter import split_text
from .ai import _get_ai_service, _dump_json, _load_json

router = APIRouter(prefix="/api/materials", tags=["materials"])

SUPPORTED_TEXT_SUFFIXES = {".txt", ".md", ".markdown"}


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


@router.post("/upload-text", response_model=dict)
async def upload_text_material(file: UploadFile = File(...)):
    original_name = Path(file.filename or "").name
    suffix = Path(original_name).suffix.lower()
    if suffix not in SUPPORTED_TEXT_SUFFIXES:
        raise HTTPException(status_code=400, detail="仅支持 TXT 或 Markdown 文件")

    raw = await file.read()
    if not raw:
        raise HTTPException(status_code=400, detail="上传文件内容为空")

    try:
        content = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        try:
            content = raw.decode("gb18030")
        except UnicodeDecodeError:
            raise HTTPException(status_code=400, detail="文件编码不支持，请使用 UTF-8 或 GB18030")

    content = content.replace("\r\n", "\n").replace("\r", "\n").strip()
    if not content:
        raise HTTPException(status_code=400, detail="资料正文不能为空")

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    safe_stem = _safe_filename(Path(original_name).stem or "material")
    saved_name = f"{safe_stem}_{int(time.time())}_{uuid4().hex[:8]}{suffix}"
    saved_path = UPLOAD_DIR / saved_name
    saved_path.write_bytes(raw)

    return {
        "title": Path(original_name).stem or "未命名资料",
        "content": content,
        "source": original_name,
        "file_name": original_name,
        "saved_path": f"data/uploads/{saved_name}",
        "content_length": len(content),
    }


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

    enable_split = body.get("enable_split", False)
    print(f"[EXTRACT] enable_split={enable_split}, content_length={len(content)}", flush=True)

    segment_size_raw = get_setting(db, "AI_SEGMENT_SIZE", str(AI_SEGMENT_SIZE))
    max_segments_raw = get_setting(db, "AI_MAX_SEGMENTS", str(AI_MAX_SEGMENTS))
    print(f"[EXTRACT] segment_size_raw={segment_size_raw}, max_segments_raw={max_segments_raw}", flush=True)
    segment_size = int(segment_size_raw or str(AI_SEGMENT_SIZE))
    max_segments = int(max_segments_raw or str(AI_MAX_SEGMENTS))
    print(f"[EXTRACT] segment_size={segment_size}, max_segments={max_segments}", flush=True)

    if enable_split:
        segments = split_text(content, segment_size=segment_size, max_segments=max_segments)
    else:
        segments = [content]

    split_used = len(segments) > 1
    segment_count = len(segments)
    print(f"[EXTRACT] segments={segment_count}, split_used={split_used}", flush=True)

    ai_service = _get_ai_service(db)
    extracted_items = []
    skipped_count = 0

    try:
        existing_titles = set()

        for seg_idx, segment in enumerate(segments):
            print(f"[EXTRACT] processing segment {seg_idx + 1}/{segment_count}, length={len(segment)}", flush=True)
            try:
                result = await ai_service.extract_knowledge_points(
                    knowledge_base_name=kb.name,
                    material_title=title,
                    material_content=segment,
                    related_type="material_import",
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

                extracted_items.append(kp)
                existing_titles.add(normalized_title)

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
        db.flush()

        existing_titles = build_existing_kp_title_set(db, material.id)
        all_created = []
        for kp in extracted_items:
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
    except HTTPException:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        raise

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
    knowledge_points = db.query(KnowledgePoint).filter(KnowledgePoint.material_id == material.id).all()
    for kp in knowledge_points:
        questions = db.query(Question).filter(Question.knowledge_point_id == kp.id).all()
        for q in questions:
            db.query(AnswerRecord).filter(AnswerRecord.question_id == q.id).delete()
            db.query(WrongQuestion).filter(WrongQuestion.question_id == q.id).delete()
            db.delete(q)

        audio_files = db.query(AudioFile).filter(AudioFile.knowledge_point_id == kp.id).all()
        for audio in audio_files:
            if audio.file_path:
                delete_audio_file(audio.file_path)
            db.delete(audio)

        db.delete(kp)
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


def _safe_filename(value: str) -> str:
    keep = []
    for char in value.strip():
        if char.isalnum() or char in ("-", "_"):
            keep.append(char)
        else:
            keep.append("_")
    name = "".join(keep).strip("_")
    return name[:80] or "material"
