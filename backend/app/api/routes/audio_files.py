from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import json
from ...core.database import get_db
from ...models.audio_file import AudioFile
from ...services.audio_service import delete_audio_file

router = APIRouter(prefix="/api/audio-files", tags=["audio-files"])


@router.get("")
def list_audio_files(
    knowledge_base_id: int | None = None,
    knowledge_point_id: int | None = None,
    status: str | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(AudioFile)
    if knowledge_point_id:
        query = query.filter(AudioFile.knowledge_point_id == knowledge_point_id)
    if status:
        query = query.filter(AudioFile.status == status)

    files = query.order_by(AudioFile.id.desc()).all()
    result = []
    for f in files:
        item = {
            "id": f.id,
            "knowledge_point_id": f.knowledge_point_id,
            "title": f.title,
            "text_content": f.text_content,
            "file_path": f.file_path,
            "file_url": f.file_url,
            "duration": f.duration,
            "status": f.status,
            "error_message": f.error_message,
            "created_at": f.created_at,
            "updated_at": f.updated_at,
        }
        # 如果有知识库筛选，检查关联
        if knowledge_base_id:
            from ...models.knowledge_point import KnowledgePoint
            kp = db.query(KnowledgePoint).filter(KnowledgePoint.id == f.knowledge_point_id).first()
            if kp and kp.knowledge_base_id != knowledge_base_id:
                continue
        result.append(item)
    return result


@router.get("/{audio_id}")
def get_audio_file(audio_id: int, db: Session = Depends(get_db)):
    f = db.query(AudioFile).filter(AudioFile.id == audio_id).first()
    if not f:
        raise HTTPException(status_code=404, detail="音频记录不存在")
    return {
        "id": f.id,
        "knowledge_point_id": f.knowledge_point_id,
        "title": f.title,
        "text_content": f.text_content,
        "file_path": f.file_path,
        "file_url": f.file_url,
        "duration": f.duration,
        "status": f.status,
        "error_message": f.error_message,
        "created_at": f.created_at,
        "updated_at": f.updated_at,
    }


@router.delete("/{audio_id}")
def delete_audio_file_api(audio_id: int, db: Session = Depends(get_db)):
    f = db.query(AudioFile).filter(AudioFile.id == audio_id).first()
    if not f:
        raise HTTPException(status_code=404, detail="音频记录不存在")
    # 删除本地文件
    if f.file_path:
        delete_audio_file(f.file_path)
    db.delete(f)
    db.commit()
    return {"success": True, "message": "音频已删除"}
