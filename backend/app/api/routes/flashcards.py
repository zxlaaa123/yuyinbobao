from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ...core.database import get_db
from ...models.flashcard import Flashcard
from ...models.knowledge_point import KnowledgePoint
from ...schemas.flashcard import FlashcardCreate, FlashcardUpdate
from ...services.ai_service import AIService
from ...core.config import get_setting, AI_API_KEY, AI_BASE_URL, AI_MODEL, AI_TEMPERATURE, AI_TIMEOUT
from ...utils.json_helpers import load_json as _load_json
from ...services.json_parser import extract_json_from_text

router = APIRouter(prefix="/api/flashcards", tags=["flashcards"])


def _get_ai_service(db: Session) -> AIService:
    api_key = get_setting(db, "AI_API_KEY", AI_API_KEY)
    base_url = get_setting(db, "AI_BASE_URL", AI_BASE_URL)
    model = get_setting(db, "AI_MODEL", AI_MODEL)
    temperature = float(get_setting(db, "AI_TEMPERATURE", str(AI_TEMPERATURE)))
    timeout = int(get_setting(db, "AI_TIMEOUT", str(AI_TIMEOUT)))
    if not api_key:
        raise HTTPException(status_code=400, detail="AI API Key 未配置，请先到设置页配置")
    if not base_url:
        raise HTTPException(status_code=400, detail="AI Base URL 未配置，请先到设置页配置")
    return AIService(api_key=api_key, base_url=base_url, model=model, temperature=temperature, timeout=timeout, db=db)


def _to_response(fc: Flashcard) -> dict:
    return {
        "id": fc.id,
        "knowledge_point_id": fc.knowledge_point_id,
        "front": fc.front,
        "back": fc.back,
        "flashcard_type": fc.flashcard_type,
        "created_at": fc.created_at,
        "updated_at": fc.updated_at,
    }


@router.get("")
def list_flashcards(knowledge_point_id: int, db: Session = Depends(get_db)):
    fcs = db.query(Flashcard).filter(
        Flashcard.knowledge_point_id == knowledge_point_id
    ).order_by(Flashcard.id.desc()).all()
    return [_to_response(fc) for fc in fcs]


@router.post("")
def create_flashcard(body: FlashcardCreate, knowledge_point_id: int, db: Session = Depends(get_db)):
    if not body.front.strip():
        raise HTTPException(status_code=400, detail="闪卡正面不能为空")
    if not body.back.strip():
        raise HTTPException(status_code=400, detail="闪卡背面不能为空")
    if body.flashcard_type not in ("basic", "reverse", "cloze"):
        raise HTTPException(status_code=400, detail="闪卡类型只能是 basic、reverse、cloze")

    # 重复 front 跳过
    existing = db.query(Flashcard).filter(
        Flashcard.knowledge_point_id == knowledge_point_id,
        Flashcard.front == body.front.strip()
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="该正面内容的闪卡已存在")

    fc = Flashcard(
        knowledge_point_id=knowledge_point_id,
        front=body.front.strip(),
        back=body.back.strip(),
        flashcard_type=body.flashcard_type,
    )
    db.add(fc)
    db.commit()
    db.refresh(fc)
    return _to_response(fc)


@router.put("/{fc_id}")
def update_flashcard(fc_id: int, body: FlashcardUpdate, db: Session = Depends(get_db)):
    fc = db.query(Flashcard).filter(Flashcard.id == fc_id).first()
    if not fc:
        raise HTTPException(status_code=404, detail="闪卡不存在")
    if body.front is not None:
        if not body.front.strip():
            raise HTTPException(status_code=400, detail="闪卡正面不能为空")
        fc.front = body.front.strip()
    if body.back is not None:
        if not body.back.strip():
            raise HTTPException(status_code=400, detail="闪卡背面不能为空")
        fc.back = body.back.strip()
    if body.flashcard_type is not None:
        if body.flashcard_type not in ("basic", "reverse", "cloze"):
            raise HTTPException(status_code=400, detail="闪卡类型只能是 basic、reverse、cloze")
        fc.flashcard_type = body.flashcard_type
    db.commit()
    db.refresh(fc)
    return _to_response(fc)


@router.delete("/{fc_id}")
def delete_flashcard(fc_id: int, db: Session = Depends(get_db)):
    fc = db.query(Flashcard).filter(Flashcard.id == fc_id).first()
    if not fc:
        raise HTTPException(status_code=404, detail="闪卡不存在")
    db.delete(fc)
    db.commit()
    return {"success": True, "message": "闪卡已删除"}


@router.post("/generate-from-point/{knowledge_point_id}")
async def generate_flashcards_from_point(knowledge_point_id: int, db: Session = Depends(get_db)):
    kp = db.query(KnowledgePoint).filter(KnowledgePoint.id == knowledge_point_id).first()
    if not kp:
        raise HTTPException(status_code=404, detail="知识点不存在")

    ai_service = _get_ai_service(db)

    from ...services.prompt_templates import GENERATE_FLASHCARDS_SYSTEM, build_generate_flashcards_user_prompt

    user_prompt = build_generate_flashcards_user_prompt(
        title=kp.title,
        summary=kp.summary or "",
        detail=kp.detail or "",
        exam_points=_load_json(kp.exam_points),
        confusing_points=_load_json(kp.confusing_points),
        memory_tips=_load_json(kp.memory_tips),
        examples=_load_json(kp.examples),
    )

    try:
        raw = await ai_service.chat(
            GENERATE_FLASHCARDS_SYSTEM,
            user_prompt,
            operation="generate_flashcards",
            related_type="knowledge_point",
            related_id=kp.id,
        )
        result = extract_json_from_text(raw)
    except ValueError:
        raise HTTPException(status_code=400, detail="AI JSON 解析失败，请稍后重试")
    except Exception:
        raise HTTPException(status_code=500, detail="AI 调用失败，请检查模型配置或稍后重试")

    raw_cards = result.get("flashcards", [])
    if not raw_cards:
        raise HTTPException(status_code=500, detail="AI 未返回有效闪卡")

    created = []
    skipped = 0
    for card in raw_cards:
        front = card.get("front", "").strip()
        back = card.get("back", "").strip()
        fc_type = card.get("type", "basic")
        if not front or not back:
            skipped += 1
            continue
        if fc_type not in ("basic", "reverse", "cloze"):
            fc_type = "basic"
        # 重复 front 跳过
        existing = db.query(Flashcard).filter(
            Flashcard.knowledge_point_id == knowledge_point_id,
            Flashcard.front == front,
        ).first()
        if existing:
            skipped += 1
            continue
        fc = Flashcard(
            knowledge_point_id=knowledge_point_id,
            front=front,
            back=back,
            flashcard_type=fc_type,
        )
        db.add(fc)
        created.append(fc)

    db.commit()
    return {
        "knowledge_point_id": knowledge_point_id,
        "created_count": len(created),
        "skipped_count": skipped,
        "flashcards": [_to_response(fc) for fc in created],
    }
