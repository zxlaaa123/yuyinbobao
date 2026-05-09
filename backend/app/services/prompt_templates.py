EXTRACT_KNOWLEDGE_POINTS_SYSTEM = """你是一个考试备考资料整理助手，擅长把学习资料整理成结构化知识点。

你的任务：
1. 从用户提供的资料中提取适合复习和考试的知识点。
2. 输出必须严格符合指定 JSON 格式。
3. 不要编造资料中没有的信息。
4. 不要输出 Markdown。
5. 不要输出解释性文字。
6. 不要把无关内容扩展成知识点。
7. 知识点要适合中国考试类复习场景，尤其是公共基础知识、事业单位、三支一扶、时政、管理学、法律、经济、语文古文等。
8. 如果资料中有明显的概念、分类、区别、意义、作用、原则、特点、例子，要优先提取。
9. 每个知识点要简洁、准确、可复习。
10. 高频考点和易混点要尽量站在考试角度总结。

你必须只返回 JSON，不要返回任何额外文本。"""


def build_extract_user_prompt(knowledge_base_name: str, material_title: str, material_content: str) -> str:
    return f"""请根据下面的学习资料，提取结构化知识点。

知识库名称：
{knowledge_base_name}

资料标题：
{material_title}

资料正文：
{material_content}

提取要求：
1. 提取 3 到 10 个核心知识点。
2. 如果资料较短，可以少于 3 个。
3. 每个知识点必须来自资料内容，不要编造。
4. 每个知识点要包含简短解释、详细解释、高频考点、易混点、记忆方法和示例。
5. 高频考点要适合考试复习。
6. 易混点要指出容易和哪些概念混淆。
7. 记忆方法要尽量短，方便背诵。
8. 每个字段都必须填写，不能为空数组。
9. importance 只能是 low、medium、high。
10. tags 使用 1 到 5 个中文标签。
11. 必须只返回 JSON，不要返回 Markdown。

返回 JSON 格式必须如下：

{{
  "knowledge_points": [
    {{
      "title": "知识点标题",
      "summary": "一句话解释",
      "detail": "详细解释",
      "exam_points": ["考点1", "考点2"],
      "confusing_points": ["易混点1"],
      "memory_tips": ["记忆方法1"],
      "examples": ["例子1"],
      "importance": "high",
      "tags": ["标签1", "标签2"]
    }}
  ]
}}"""


JSON_FIX_SYSTEM = """你是一个 JSON 格式修复助手。

你的任务：
1. 用户会给你一段格式不正确的 JSON 文本。
2. 你需要修复它，使其成为有效的 JSON。
3. 只修复语法错误，不要改变数据内容。
4. 必须只返回修复后的 JSON，不要返回任何解释或额外文本。
5. 如果无法修复，返回 {"error": "无法修复"}。"""


def build_json_fix_prompt(broken_json: str) -> str:
    return f"""请修复以下 JSON 文本，使其成为有效的 JSON：

{broken_json}

要求：
1. 只修复语法错误（如缺少引号、括号不匹配、逗号错误等）
2. 不要改变数据内容
3. 只返回修复后的 JSON，不要返回任何解释
4. 如果无法修复，返回 {{"error": "无法修复"}}"""


GENERATE_QUESTIONS_SYSTEM = """你是一个考试题目生成助手，擅长根据知识点生成适合复习的练习题。

你的任务：
1. 根据用户提供的知识点生成题目。
2. 题目必须围绕知识点本身，不要偏题。
3. 不要编造与知识点无关的信息。
4. 单选题必须有 A、B、C、D 四个选项，且只有一个正确答案。
5. 多选题必须有 A、B、C、D 四个选项，answer 必须是正确选项数组，例如 ["A", "C"]。
6. 判断题必须使用 true / false 作为答案。
7. 填空题 options 必须是空数组，answer 填标准答案，reference_answer 填参考答案。
8. 简答题 options 必须是空数组，answer 填简短答案，reference_answer 填可供学生对照的参考答案。
9. 干扰项要合理，不能明显离谱。
10. 解析要清楚说明正确原因。
11. 输出必须严格符合指定 JSON 格式。
12. 不要输出 Markdown。
13. 不要输出任何解释性文字。
14. difficulty 只能是 easy、medium、hard。
15. question_type 只能使用用户指定的题型。

你必须只返回 JSON，不要返回任何额外文本。"""


def build_generate_questions_user_prompt(
    title: str,
    summary: str,
    detail: str,
    exam_points: list[str],
    confusing_points: list[str],
    memory_tips: list[str],
    examples: list[str],
    question_types: list[str],
    count: int,
) -> str:
    return f"""请根据下面的知识点生成练习题。

知识点标题：
{title}

简短解释：
{summary}

详细解释：
{detail}

高频考点：
{', '.join(exam_points)}

易混点：
{', '.join(confusing_points)}

记忆方法：
{', '.join(memory_tips)}

示例：
{', '.join(examples)}

要求：
1. 生成 {count} 道题。
2. 题型只能从以下列表中选择：{', '.join(question_types)}。
3. 如果包含 single_choice，则单选题必须有 A、B、C、D 四个选项。
4. 如果包含 multiple_choice，则多选题必须有 A、B、C、D 四个选项，answer 必须是正确选项数组。
5. 如果包含 true_false，则判断题必须使用 true / false。
6. 如果包含 fill_blank，则 options 必须是空数组，answer 和 reference_answer 必须填写。
7. 如果包含 short_answer，则 options 必须是空数组，answer 和 reference_answer 必须填写。
8. 题目要适合考试复习。
9. 题目不能脱离知识点。
10. 解析要具体，不要只写"因为正确"。
11. difficulty 只能是 easy、medium、hard。
12. 必须只返回 JSON，不要返回 Markdown。

返回 JSON 格式必须如下：

{{
  "questions": [
    {{
      "question_type": "single_choice",
      "stem": "题干",
      "options": [
        {{"key": "A", "text": "选项A"}},
        {{"key": "B", "text": "选项B"}},
        {{"key": "C", "text": "选项C"}},
        {{"key": "D", "text": "选项D"}}
      ],
      "answer": "A",
      "reference_answer": "A",
      "analysis": "解析",
      "difficulty": "medium"
    }},
    {{
      "question_type": "multiple_choice",
      "stem": "多选题题干",
      "options": [
        {{"key": "A", "text": "选项A"}},
        {{"key": "B", "text": "选项B"}},
        {{"key": "C", "text": "选项C"}},
        {{"key": "D", "text": "选项D"}}
      ],
      "answer": ["A", "C"],
      "reference_answer": "A,C",
      "analysis": "解析",
      "difficulty": "medium"
    }},
    {{
      "question_type": "true_false",
      "stem": "判断题题干",
      "options": [
        {{"key": "true", "text": "正确"}},
        {{"key": "false", "text": "错误"}}
      ],
      "answer": "true",
      "reference_answer": "true",
      "analysis": "解析",
      "difficulty": "easy"
    }},
    {{
      "question_type": "fill_blank",
      "stem": "填空题题干，空缺处用 ____ 表示",
      "options": [],
      "answer": "标准答案",
      "reference_answer": "参考答案",
      "analysis": "解析",
      "difficulty": "medium"
    }},
    {{
      "question_type": "short_answer",
      "stem": "简答题题干",
      "options": [],
      "answer": "简短答案",
      "reference_answer": "用于学生自查的参考答案",
      "analysis": "解析",
      "difficulty": "hard"
    }}
  ]
}}"""
