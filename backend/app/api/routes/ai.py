from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import json
from ...core.database import get_db
from ...core.config import get_setting, AI_API_KEY, AI_BASE_URL, AI_MODEL, AI_TEMPERATURE, AI_TIMEOUT, AI_SEGMENT_SIZE, AI_MAX_SEGMENTS
from ...models.material import Material
from ...models.knowledge_point import KnowledgePoint
from ...models.question import Question
from ...services.ai_service import AIService
from ...services.dedup_service import normalize_title, normalize_stem
from ...services.text_splitter import split_text

router = APIRouter(prefix="/api/ai", tags=["ai"])


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
    return AIService(api_key=api_key, base_url=base_url, model=model, temperature=temperature, timeout=timeout)


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


@router.post("/extract-points")
async def extract_points(body: dict, db: Session = Depends(get_db)):
    material_id = body.get("material_id")
    if not material_id:
        raise HTTPException(status_code=400, detail="缺少 material_id")
    material = db.query(Material).filter(Material.id == material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="资料不存在")

    enable_split = body.get("enable_split", False)
    ai_service = _get_ai_service(db)

    # 确定分段参数
    segment_size = int(get_setting(db, "AI_SEGMENT_SIZE", str(AI_SEGMENT_SIZE)))
    max_segments = int(get_setting(db, "AI_MAX_SEGMENTS", str(AI_MAX_SEGMENTS)))

    if enable_split:
        segments = split_text(material.content, segment_size=segment_size, max_segments=max_segments)
    else:
        segments = [material.content]

    split_used = len(segments) > 1
    segment_count = len(segments)
    all_created = []
    skipped_count = 0

    for seg_idx, segment in enumerate(segments):
        try:
            result = await ai_service.extract_knowledge_points(
                knowledge_base_name="",
                material_title=material.title,
                material_content=segment,
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"AI 调用失败（第 {seg_idx + 1}/{segment_count} 段）：{str(e)}")

        knowledge_points = result.get("knowledge_points", [])

        for kp in knowledge_points:
            if not kp.get("title"):
                skipped_count += 1
                continue
            # 去重：标准化 title 比较
            kp_normalized = normalize_title(kp["title"])
            existing_kps = db.query(KnowledgePoint).filter(
                KnowledgePoint.material_id == material.id,
            ).all()
            is_dup = any(normalize_title(ep.title) == kp_normalized for ep in existing_kps)
            if is_dup:
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
                importance=kp.get("importance", "medium") if kp.get("importance") in ("low", "medium", "high") else "medium",
                tags=_dump_json(kp.get("tags")),
            )
            db.add(point)
            all_created.append(point)

    material.extracted_count = len(all_created)
    db.commit()

    return {
        "material_id": material.id,
        "split_used": split_used,
        "segment_count": segment_count,
        "created_count": len(all_created),
        "skipped_count": skipped_count,
        "knowledge_points": [
            {"id": p.id, "title": p.title, "importance": p.importance, "tags": _load_json(p.tags)}
            for p in all_created
        ],
    }


@router.post("/generate-questions")
async def generate_questions(body: dict, db: Session = Depends(get_db)):
    kp_id = body.get("knowledge_point_id")
    if not kp_id:
        raise HTTPException(status_code=400, detail="缺少 knowledge_point_id")

    question_types = body.get("question_types", ["single_choice"])
    count = body.get("count", 5)

    if not isinstance(count, int) or count < 1 or count > 20:
        raise HTTPException(status_code=400, detail="题目数量必须在 1 到 20 之间")

    valid_types = {"single_choice", "true_false"}
    for qt in question_types:
        if qt not in valid_types:
            raise HTTPException(status_code=400, detail=f"不支持的题型：{qt}")

    kp = db.query(KnowledgePoint).filter(KnowledgePoint.id == kp_id).first()
    if not kp:
        raise HTTPException(status_code=404, detail="知识点不存在")

    ai_service = _get_ai_service(db)
    try:
        result = await ai_service.generate_questions(
            title=kp.title,
            summary=kp.summary or "",
            detail=kp.detail or "",
            exam_points=_load_json(kp.exam_points),
            confusing_points=_load_json(kp.confusing_points),
            memory_tips=_load_json(kp.memory_tips),
            examples=_load_json(kp.examples),
            question_types=question_types,
            count=count,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI 调用失败：{str(e)}")

    raw_questions = result.get("questions", [])
    if not raw_questions:
        raise HTTPException(status_code=500, detail="AI 未返回有效题目")

    created = []
    skipped = 0
    for q in raw_questions:
        qt = q.get("question_type")
        stem = q.get("stem", "").strip()
        answer = q.get("answer", "").strip()
        options = q.get("options", [])

        if not stem or not answer:
            skipped += 1
            continue

        # 去重：同知识点下相同 stem 不重复插入
        stem_normalized = normalize_stem(stem)
        existing_questions = db.query(Question).filter(
            Question.knowledge_point_id == kp_id,
        ).all()
        is_dup = any(normalize_stem(eq.stem) == stem_normalized for eq in existing_questions)
        if is_dup:
            skipped += 1
            continue

        # 校验单选题
        if qt == "single_choice":
            keys = {o.get("key") for o in options}
            if keys != {"A", "B", "C", "D"}:
                skipped += 1
                continue
            if answer not in ("A", "B", "C", "D"):
                skipped += 1
                continue

        # 校验判断题
        elif qt == "true_false":
            keys = {o.get("key") for o in options}
            if keys != {"true", "false"}:
                skipped += 1
                continue
            if answer not in ("true", "false"):
                skipped += 1
                continue
        else:
            skipped += 1
            continue

        difficulty = q.get("difficulty", "medium")
        if difficulty not in ("easy", "medium", "hard"):
            difficulty = "medium"

        question = Question(
            knowledge_base_id=kp.knowledge_base_id,
            knowledge_point_id=kp.id,
            question_type=qt,
            stem=stem,
            options=json.dumps(options, ensure_ascii=False),
            answer=answer,
            analysis=q.get("analysis", ""),
            difficulty=difficulty,
        )
        db.add(question)
        created.append(question)

    if not created:
        raise HTTPException(status_code=500, detail="AI 返回的题目格式不符合要求，请重试")

    db.commit()

    return {
        "knowledge_point_id": kp.id,
        "created_count": len(created),
        "skipped_count": skipped,
        "questions": [
            {
                "id": q.id,
                "question_type": q.question_type,
                "stem": q.stem,
                "options": json.loads(q.options) if q.options else [],
                "answer": q.answer,
                "analysis": q.analysis,
                "difficulty": q.difficulty,
            }
            for q in created
        ],
    }
