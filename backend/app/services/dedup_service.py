import re

from ..models.knowledge_point import KnowledgePoint
from ..models.question import Question


def normalize_title(title: str) -> str:
    """标准化 title 用于去重比较"""
    if not title:
        return ""
    # 去除首尾空白、转小写、去除多余空格
    t = title.strip().lower()
    t = re.sub(r'\s+', '', t)  # 去除所有空格
    t = re.sub(r'[《》「」『』（）\(\)]', '', t)  # 去除书名号、括号等
    return t


def normalize_stem(stem: str) -> str:
    """标准化题目 stem 用于去重比较"""
    if not stem:
        return ""
    t = stem.strip().lower()
    t = re.sub(r'\s+', '', t)
    # 去除末尾的标点
    t = re.sub(r'[。？！?.!]+$', '', t)
    return t


def build_existing_kp_title_set(db, material_id: int) -> set[str]:
    """加载同 material 下现有知识点的标准化标题集合"""
    existing = db.query(KnowledgePoint).filter(
        KnowledgePoint.material_id == material_id,
    ).all()
    return {
        normalized
        for kp in existing
        for normalized in [normalize_title(kp.title)]
        if normalized
    }


def build_existing_question_stem_set(db, knowledge_point_id: int) -> set[str]:
    """加载同知识点下现有题目的标准化题干集合"""
    existing = db.query(Question).filter(
        Question.knowledge_point_id == knowledge_point_id,
    ).all()
    return {
        normalized
        for q in existing
        for normalized in [normalize_stem(q.stem)]
        if normalized
    }


def is_duplicate_kp_title(db, material_id: int, title: str) -> bool:
    """检查同 material 下是否已有相同 title 的知识点"""
    normalized = normalize_title(title)
    if not normalized:
        return False
    return normalized in build_existing_kp_title_set(db, material_id)


def is_duplicate_question_stem(db, knowledge_point_id: int, stem: str) -> bool:
    """检查同知识点下是否已有相同 stem 的题目"""
    normalized = normalize_stem(stem)
    if not normalized:
        return False
    return normalized in build_existing_question_stem_set(db, knowledge_point_id)
