from fastapi import APIRouter, Depends
from sqlalchemy import or_
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...models.knowledge_point import KnowledgePoint
from ...models.material import Material

router = APIRouter(prefix="/api/search", tags=["search"])


def _brief(value: str | None, limit: int = 80) -> str:
    if not value:
        return ""
    text = " ".join(value.split())
    return text if len(text) <= limit else f"{text[:limit]}..."


@router.get("")
def search(q: str = "", db: Session = Depends(get_db)):
    keyword = q.strip()
    if not keyword:
        return {"query": keyword, "results": []}

    like = f"%{keyword}%"
    knowledge_points = (
        db.query(KnowledgePoint)
        .filter(
            or_(
                KnowledgePoint.title.ilike(like),
                KnowledgePoint.summary.ilike(like),
                KnowledgePoint.detail.ilike(like),
                KnowledgePoint.tags.ilike(like),
            )
        )
        .order_by(KnowledgePoint.id.desc())
        .limit(10)
        .all()
    )
    materials = (
        db.query(Material)
        .filter(Material.title.ilike(like))
        .order_by(Material.id.desc())
        .limit(10)
        .all()
    )

    results = [
        {
            "type": "knowledge_point",
            "id": kp.id,
            "title": kp.title,
            "summary": _brief(kp.summary or kp.detail),
            "target_url": f"/knowledge-points/{kp.id}",
        }
        for kp in knowledge_points
    ]
    results.extend(
        {
            "type": "material",
            "id": material.id,
            "title": material.title,
            "summary": "资料",
            "target_url": f"/knowledge-points?material_id={material.id}",
        }
        for material in materials
    )

    return {"query": keyword, "results": results}
