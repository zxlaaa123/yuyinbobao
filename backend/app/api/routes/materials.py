from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ...core.database import get_db
from ...models.material import Material
from ...models.knowledge_base import KnowledgeBase
from ...schemas.material import MaterialCreate, MaterialUpdate, MaterialResponse

router = APIRouter(prefix="/api/materials", tags=["materials"])


@router.get("", response_model=list[MaterialResponse])
def list_materials(knowledge_base_id: int | None = None, db: Session = Depends(get_db)):
    query = db.query(Material)
    if knowledge_base_id:
        query = query.filter(Material.knowledge_base_id == knowledge_base_id)
    materials = query.order_by(Material.id.desc()).all()
    result = []
    for m in materials:
        kb = db.query(KnowledgeBase).filter(KnowledgeBase.id == m.knowledge_base_id).first()
        result.append(_to_response(m, kb.name if kb else ""))
    return result


@router.post("", response_model=MaterialResponse)
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


@router.get("/{material_id}", response_model=MaterialResponse)
def get_material(material_id: int, db: Session = Depends(get_db)):
    material = db.query(Material).filter(Material.id == material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="资料不存在")
    kb = db.query(KnowledgeBase).filter(KnowledgeBase.id == material.knowledge_base_id).first()
    return _to_response(material, kb.name if kb else "")


@router.put("/{material_id}", response_model=MaterialResponse)
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


def _to_response(m: Material, kb_name: str) -> dict:
    return {
        "id": m.id,
        "knowledge_base_id": m.knowledge_base_id,
        "knowledge_base_name": kb_name,
        "title": m.title,
        "content": m.content,
        "source": m.source,
        "note": m.note,
        "material_type": m.material_type,
        "content_length": m.content_length,
        "extracted_count": m.extracted_count,
        "created_at": m.created_at,
        "updated_at": m.updated_at,
    }
