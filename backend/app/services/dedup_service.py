import re


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


def is_duplicate_kp_title(db, material_id: int, title: str) -> bool:
    """检查同 material 下是否已有相同 title 的知识点"""
    from ..models.knowledge_point import KnowledgePoint
    normalized = normalize_title(title)
    if not normalized:
        return False
    existing = db.query(KnowledgePoint).filter(
        KnowledgePoint.material_id == material_id,
    ).all()
    for kp in existing:
        if normalize_title(kp.title) == normalized:
            return True
    return False


def is_duplicate_question_stem(db, knowledge_point_id: int, stem: str) -> bool:
    """检查同知识点下是否已有相同 stem 的题目"""
    from ..models.question import Question
    normalized = normalize_stem(stem)
    if not normalized:
        return False
    existing = db.query(Question).filter(
        Question.knowledge_point_id == knowledge_point_id,
    ).all()
    for q in existing:
        if normalize_stem(q.stem) == normalized:
            return True
    return False
