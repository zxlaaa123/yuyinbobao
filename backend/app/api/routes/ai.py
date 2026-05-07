from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ...core.database import get_db
from ...core.config import get_setting, AI_API_KEY, AI_BASE_URL, AI_MODEL, AI_TEMPERATURE, AI_TIMEOUT
from ...models.material import Material
from ...models.knowledge_point import KnowledgePoint
from ...services.ai_service import AIService

router = APIRouter(prefix="/api/ai", tags=["ai"])


def _get_ai_service(db: Session) -> AIService:
    api_key = get_setting(db, "AI_API_KEY") or AI_API_KEY
    base_url = get_setting(db, "AI_BASE_URL") or AI_BASE_URL
    model = get_setting(db, "AI_MODEL") or AI_MODEL
    temperature = float(get_setting(db, "AI_TEMPERATURE") or AI_TEMPERATURE)
    timeout = int(get_setting(db, "AI_TIMEOUT") or AI_TIMEOUT)
    if not api_key:
        raise HTTPException(status_code=400, detail="AI API Key 未配置，请先到设置页配置")
    if not base_url:
        raise HTTPException(status_code=400, detail="AI Base URL 未配置，请先到设置页配置")
    return AIService(api_key=api_key, base_url=base_url, model=model, temperature=temperature, timeout=timeout)


@router.post("/extract-points")
async def extract_points(body: dict, db: Session = Depends(get_db)):
    material_id = body.get("material_id")
    if not material_id:
        raise HTTPException(status_code=400, detail="缺少 material_id")
    material = db.query(Material).filter(Material.id == material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="资料不存在")

    ai_service = _get_ai_service(db)
    try:
        result = await ai_service.extract_knowledge_points(
            knowledge_base_name="",
            material_title=material.title,
            material_content=material.content,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI 调用失败：{str(e)}")

    knowledge_points = result.get("knowledge_points", [])
    if not knowledge_points:
        raise HTTPException(status_code=500, detail="AI 未返回有效知识点")

    created = []
    for kp in knowledge_points:
        if not kp.get("title"):
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
            importance=kp.get("importance", "medium") if kp.get("importance") in ("low", "medium", "high") else "medium",
            tags=_dump_json(kp.get("tags")),
        )
        db.add(point)
        created.append(point)

    material.extracted_count = len(created)
    db.commit()

    return {
        "material_id": material.id,
        "created_count": len(created),
        "knowledge_points": [
            {"id": p.id, "title": p.title, "importance": p.importance, "tags": _load_json(p.tags)}
            for p in created
        ],
    }


def _dump_json(value) -> str | None:
    import json
    if value is None:
        return None
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False)


def _load_json(value: str | None) -> list:
    import json
    if not value:
        return []
    try:
        return json.loads(value)
    except Exception:
        return []
