# MiniMax 代码审查发现的问题

审查日期：2026-05-10

## 高优先级问题

### 1. N+1 查询问题（多处）

**位置**：
- `backend/app/api/routes/wrong_questions.py` 第 24-31 行
- `backend/app/api/routes/knowledge_points.py` 第 97-100 行
- `backend/app/api/routes/practice_sessions.py` 第 48-49 行
- `backend/app/api/routes/materials.py` 第 35-37 行
- `backend/app/api/routes/export.py` 第 145-146 行

**问题描述**：
在循环内逐条查询关联数据，例如：
```python
for wq in wqs:
    q = db.query(Question).filter(Question.id == wq.question_id).first()  # N+1
    kp = db.query(KnowledgePoint).filter(...).first()  # N+1
```

**影响**：对于大量数据，列表查询性能极差。

**建议修复**：使用 `joinedload` 或 `in_` 批量查询替代循环内单条查询。

---

### 2. AnswerRecord 缺少唯一约束

**位置**：`backend/app/models/answer_record.py`

**问题描述**：`AnswerRecord` 表只有 `id` 作为主键，没有唯一约束防止重复记录。如果用户重复提交同一答案，会产生多条记录。

**影响**：数据冗余，统计分析可能不准确。

**建议**：如业务需要唯一约束，添加 `__table_args__` 或唯一索引。

---

### 3. materials.py 大文件内存问题

**位置**：`backend/app/api/routes/materials.py` 第 76 行

**问题描述**：
```python
raw = await file.read(MAX_UPLOAD_SIZE_BYTES + 1)
if len(raw) > MAX_UPLOAD_SIZE_BYTES:
    raise HTTPException(...)
```
先读取整个文件到内存再检查大小，如果文件过大会占满内存。

**建议修复**：使用 `file.seek(0, 2)` 获取文件大小，或使用流式读取。

---

## 中优先级问题

### 4. tts_service.py 循环内重复 import json

**位置**：`backend/app/services/tts_service.py` 第 18-56 行

**问题描述**：`build_text_from_knowledge_points` 函数在 `for` 循环内对 `exam_points`、`confusing_points`、`memory_tips`、`examples` 四个字段的处理中，每次都用 `import json` 引入模块。

**建议**：将 `import json` 移到函数顶部。

---

### 5. WrongQuestion unique 约束位置错误

**位置**：`backend/app/models/wrong_question.py` 第 10 行

**问题描述**：
```python
question_id = Column(Integer, ForeignKey("questions.id"), nullable=False, unique=True, index=True)
```
`unique=True` 放在 ForeignKey 同一行是列级属性而非表级约束。需使用 `__table_args__` 定义表级唯一约束。

---

### 6. 全局异常处理隐藏调试信息

**位置**：`backend/app/main.py` 第 46-48 行

**问题描述**：
```python
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    return error_response(500, "服务器内部错误，请稍后重试", code="INTERNAL_ERROR")
```
所有未处理异常返回相同信息，真实错误未记录日志。

**建议**：将真实错误写入日志，返回通用信息给前端。

---

### 7. 死代码（mock mp3 分支）

**位置**：`backend/app/services/tts_service.py` 第 149-152 行

**问题描述**：
```python
if audio_format == "wav":
    return _mock_wav(text)
if audio_format == "pcm16":
    return b"\x00\x00" * _mock_sample_count(text)

mp3_header = b'\xff\xfb\x90\x00'  # 永远不会执行
```
mp3 分支永远不会被执行，因为 `normalize_audio_format` 只返回 wav 或 pcm16。

---

## 低优先级问题

| # | 问题 | 位置 |
|---|------|------|
| 8 | `.env.example` 缺少 `VITE_API_TIMEOUT` 定义 | `.env.example` |
| 9 | `review_task` 的 `source` 字段无枚举约束 | `backend/app/models/review_task.py` |
| 10 | 前端取消请求处理与错误处理不一致 | `frontend/src/utils/error.ts` 第 30-32 行 |
| 11 | `ilike` 大小写敏感依赖数据库 collation | `knowledge_points.py` 第 91 行 |
| 12 | `flashcards.py` AI 调用可能无超时保护 | `backend/app/api/routes/flashcards.py` 第 111 行 |

---

## 建议优先修复顺序

1. **高优先级**：N+1 查询（影响列表页性能）
2. **高优先级**：AnswerRecord 唯一约束
3. **中优先级**：tts_service.py 循环内 import json
4. **中优先级**：materials.py 大文件内存问题
5. **中优先级**：全局异常处理添加日志记录
6. **低优先级**：清理死代码（mock mp3 分支）
