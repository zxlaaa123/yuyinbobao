from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ...core.database import get_db
from ...models.knowledge_base import KnowledgeBase
from ...models.material import Material
from ...models.knowledge_point import KnowledgePoint
from ...schemas.knowledge_base import (
    KnowledgeBaseCreate,
    KnowledgeBaseUpdate,
    KnowledgeBaseResponse,
)

router = APIRouter(prefix="/api/knowledge-bases", tags=["knowledge-bases"])


@router.get("", response_model=list[KnowledgeBaseResponse])
def list_knowledge_bases(db: Session = Depends(get_db)):
    kbs = db.query(KnowledgeBase).order_by(KnowledgeBase.sort_order, KnowledgeBase.id).all()
    result = []
    for kb in kbs:
        material_count = db.query(Material).filter(Material.knowledge_base_id == kb.id).count()
        kp_count = db.query(KnowledgePoint).filter(KnowledgePoint.knowledge_base_id == kb.id).count()
        result.append({
            "id": kb.id,
            "name": kb.name,
            "description": kb.description,
            "sort_order": kb.sort_order,
            "material_count": material_count,
            "knowledge_point_count": kp_count,
            "created_at": kb.created_at,
            "updated_at": kb.updated_at,
        })
    return result


@router.post("", response_model=KnowledgeBaseResponse)
def create_knowledge_base(body: KnowledgeBaseCreate, db: Session = Depends(get_db)):
    if not body.name or not body.name.strip():
        raise HTTPException(status_code=400, detail="知识库名称不能为空")
    existing = db.query(KnowledgeBase).filter(KnowledgeBase.name == body.name.strip()).first()
    if existing:
        raise HTTPException(status_code=400, detail="知识库名称已存在")
    kb = KnowledgeBase(name=body.name.strip(), description=body.description)
    db.add(kb)
    db.commit()
    db.refresh(kb)
    return {
        "id": kb.id,
        "name": kb.name,
        "description": kb.description,
        "sort_order": kb.sort_order,
        "material_count": 0,
        "knowledge_point_count": 0,
        "created_at": kb.created_at,
        "updated_at": kb.updated_at,
    }


@router.get("/{kb_id}", response_model=KnowledgeBaseResponse)
def get_knowledge_base(kb_id: int, db: Session = Depends(get_db)):
    kb = db.query(KnowledgeBase).filter(KnowledgeBase.id == kb_id).first()
    if not kb:
        raise HTTPException(status_code=404, detail="知识库不存在")
    material_count = db.query(Material).filter(Material.knowledge_base_id == kb.id).count()
    kp_count = db.query(KnowledgePoint).filter(KnowledgePoint.knowledge_base_id == kb.id).count()
    return {
        "id": kb.id,
        "name": kb.name,
        "description": kb.description,
        "sort_order": kb.sort_order,
        "material_count": material_count,
        "knowledge_point_count": kp_count,
        "created_at": kb.created_at,
        "updated_at": kb.updated_at,
    }


@router.put("/{kb_id}", response_model=KnowledgeBaseResponse)
def update_knowledge_base(kb_id: int, body: KnowledgeBaseUpdate, db: Session = Depends(get_db)):
    kb = db.query(KnowledgeBase).filter(KnowledgeBase.id == kb_id).first()
    if not kb:
        raise HTTPException(status_code=404, detail="知识库不存在")
    if body.name is not None:
        if not body.name.strip():
            raise HTTPException(status_code=400, detail="知识库名称不能为空")
        existing = db.query(KnowledgeBase).filter(KnowledgeBase.name == body.name.strip(), KnowledgeBase.id != kb_id).first()
        if existing:
            raise HTTPException(status_code=400, detail="知识库名称已存在")
        kb.name = body.name.strip()
    if body.description is not None:
        kb.description = body.description
    db.commit()
    db.refresh(kb)
    material_count = db.query(Material).filter(Material.knowledge_base_id == kb.id).count()
    kp_count = db.query(KnowledgePoint).filter(KnowledgePoint.knowledge_base_id == kb.id).count()
    return {
        "id": kb.id,
        "name": kb.name,
        "description": kb.description,
        "sort_order": kb.sort_order,
        "material_count": material_count,
        "knowledge_point_count": kp_count,
        "created_at": kb.created_at,
        "updated_at": kb.updated_at,
    }


@router.delete("/{kb_id}")
def delete_knowledge_base(kb_id: int, db: Session = Depends(get_db)):
    kb = db.query(KnowledgeBase).filter(KnowledgeBase.id == kb_id).first()
    if not kb:
        raise HTTPException(status_code=404, detail="知识库不存在")
    material_count = db.query(Material).filter(Material.knowledge_base_id == kb.id).count()
    kp_count = db.query(KnowledgePoint).filter(KnowledgePoint.knowledge_base_id == kb.id).count()
    if material_count > 0 or kp_count > 0:
        raise HTTPException(status_code=400, detail="该知识库下还有资料或知识点，请先清空后再删除")
    db.delete(kb)
    db.commit()
    return {"success": True, "message": "知识库已删除"}
