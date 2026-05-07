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
