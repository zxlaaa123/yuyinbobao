# 06_TTS音频生成设计_V2

# AI 知识点学习与音频播报系统 - V2 TTS 音频生成设计

## 1. 文档目的

本文档定义 V2 的 TTS 音频增强方案。

V2 不替换 V1 单个知识点音频能力，而是在其基础上扩展：

```text
批量知识点音频
每日复习音频
错题复习音频
音频类型管理
语速、音色、格式配置
播放队列
```

---

## 2. 与 V1 的关系

V1 已有流程：

```text
知识点 → 播报文本 → TTS → MP3 → data/audio → 前端播放
```

V2 继续复用：

```text
tts_service.py
audio_service.py
audio_files 表
data/audio/
/audio/xxx.mp3 静态文件访问
AudioView
SettingsView
```

V2 新增：

```text
多个知识点 → 合集播报文本 → TTS → 合集音频
复习任务 → 每日播报文本 → TTS → 每日复习音频
错题 → 错题复习文本 → TTS → 错题音频
```

---

## 3. V2 功能范围

### 3.1 必做

```text
1. 多知识点批量生成一个音频
2. 每日复习任务生成音频
3. 错题生成复习音频
4. 音频列表按 audio_type 筛选
5. 批量生成数量限制
```

### 3.2 推荐

```text
1. 播放队列
2. 语速配置
3. 音色配置
4. 音频标题编辑
```

### 3.3 可选

```text
1. 多段音频顺序播放
2. 音频合并
3. 播放进度记忆
4. 倍速播放
5. 后台异步生成
```

V2 初期不做：

```text
后台任务队列
复杂音频剪辑
音频转字幕
云端存储
```

---

## 4. 音频类型

V2 新增 `audio_type` 概念。

可选值：

```text
knowledge_point 单个知识点音频
collection 多知识点合集音频
daily_review 每日复习音频
wrong_question 错题复习音频
```

兼容 V1：

```text
audio_type 为空时，按 knowledge_point 处理。
```

---

## 5. 目录设计

继续使用：

```text
data/audio/
```

可选按类型分目录：

```text
data/audio/knowledge_points/
data/audio/collections/
data/audio/daily_reviews/
data/audio/wrong_questions/
```

V2 初期推荐：

```text
仍统一放在 data/audio/
通过文件名区分类型。
```

原因：

```text
不破坏 V1 静态文件访问。
删除逻辑简单。
```

---

## 6. 文件命名规则

V1 保持：

```text
kp_{knowledge_point_id}_{timestamp}.mp3
```

V2 新增：

```text
collection_{timestamp}.mp3
daily_review_{date}_{timestamp}.mp3
wrong_questions_{timestamp}.mp3
```

示例：

```text
collection_20260507_103000.mp3
daily_review_20260507_20260507_103000.mp3
wrong_questions_20260507_103000.mp3
```

推荐 filename 函数：

```python
generate_audio_filename(audio_type: str, source_id: int | None = None, date: str | None = None, ext: str = "mp3") -> str
```

---

## 7. 数据库字段建议

建议扩展 `audio_files`：

```text
audio_type string nullable
title string nullable
source_ids text nullable
```

说明：

```text
audio_type 保存音频类型。
title 用于音频列表展示。
source_ids 保存 JSON 字符串。
```

source_ids 示例：

```json
[1, 2, 3]
```

如果暂时不改表：

```text
knowledge_point_id 为空表示非单点音频。
text_content 保存来源说明。
```

---

## 8. 静态文件访问

继续使用 V1：

```text
http://localhost:8000/audio/xxx.mp3
```

前端仍使用：

```text
file_url
```

示例：

```json
{
  "file_url": "/audio/collection_20260507_103000.mp3"
}
```

前端拼接：

```text
VITE_API_BASE_URL + file_url
```

---

## 9. 批量知识点音频

### 9.1 功能说明

用户在知识点列表勾选多个知识点，生成一个合集音频。

### 9.2 入口

```text
KnowledgePointListView
AudioView
```

### 9.3 接口

```http
POST /api/tts/generate-batch
```

### 9.4 请求体

```json
{
  "knowledge_point_ids": [1, 2, 3],
  "title": "三支一扶重点知识合集",
  "audio_type": "collection"
}
```

### 9.5 流程

```text
前端提交 knowledge_point_ids
↓
后端校验数量
↓
查询知识点
↓
生成合集播报文本
↓
校验文本长度
↓
调用 TTS
↓
保存文件到 data/audio
↓
写入 audio_files
↓
返回 file_url
```

### 9.6 数量限制

默认：

```text
TTS_BATCH_MAX_POINTS=20
TTS_BATCH_MAX_CHARS=12000
```

超限错误：

```json
{
  "detail": "单次最多选择 20 个知识点"
}
```

---

## 10. 每日复习音频

### 10.1 功能说明

根据当天待复习任务生成音频。

### 10.2 数据来源

```text
review_tasks
knowledge_points
wrong_questions
questions
```

### 10.3 接口

```http
POST /api/tts/generate-daily-review
```

### 10.4 请求体

```json
{
  "date": "2026-05-07",
  "knowledge_base_id": 1
}
```

### 10.5 流程

```text
查询 date 当天 pending / overdue 复习任务
↓
按 priority 排序
↓
生成复习播报文本
↓
调用 TTS
↓
写入 audio_files
```

### 10.6 没有任务

返回：

```json
{
  "detail": "今日没有待复习任务"
}
```

---

## 11. 错题复习音频

### 11.1 功能说明

把错题本中的错题生成音频。

### 11.2 入口

```text
WrongQuestionView
AudioView
```

### 11.3 接口

```http
POST /api/tts/generate-wrong-questions
```

### 11.4 请求体

```json
{
  "wrong_question_ids": [1, 2, 3],
  "include_mastered": false
}
```

### 11.5 播报内容

```text
题干
用户错误答案
正确答案
解析
关联知识点
```

### 11.6 规则

```text
默认不包含 mastered=true 的错题。
用户手动选择时可以包含。
数量上限复用 TTS_BATCH_MAX_POINTS。
```

---

## 12. 播报文本生成规则

V2 推荐优先模板生成，不默认调用 AI 润色。

原因：

```text
稳定
低成本
不会扩写
便于排错
```

### 12.1 知识点合集模板

```text
本期学习音频包含 {count} 个知识点。

第 {index} 个知识点：{title}

摘要：
{summary}

重点：
{key_points}

易混点：
{confusing_points}

记忆方法：
{mnemonics}

示例：
{examples}
```

### 12.2 每日复习模板

```text
今天共有 {count} 个复习任务。

下面开始复习。

第 {index} 项：
{content}

请在听完后回忆该知识点，并在系统中完成复习任务。
```

### 12.3 错题复习模板

```text
下面开始错题复习。

第 {index} 道错题：
题目：{stem}
你的答案：{user_answer}
正确答案：{correct_answer}
解析：{explanation}
关联知识点：{knowledge_point_title}
```

---

## 13. 文本清洗规则

继续沿用 V1：

```text
去除多余空白
去除 Markdown 标题符号
去除过长分隔线
替换不适合朗读的符号
```

V2 增加：

```text
列表转自然朗读文本
JSON 字符串转普通文本
空字段跳过
连续换行最多保留 2 个
```

示例：

```text
["社会管理", "公共服务"]
```

转为：

```text
社会管理、公共服务
```

---

## 14. 文本长度限制

配置：

```text
TTS_BATCH_MAX_CHARS=12000
```

校验：

```text
生成播报文本后检查长度。
超过限制时提示减少知识点数量。
```

错误：

```json
{
  "detail": "批量音频文本过长，请减少知识点数量"
}
```

可选策略：

```text
拆成多段音频。
前端按顺序播放。
```

V2 初期推荐：

```text
先报错，不自动拆。
```

---

## 15. TTS Provider 扩展

继续支持：

```text
mock
xiaomi
```

后续可扩展：

```text
edge
openai
azure
```

V2 不强制新增 Provider。

重点是：

```text
批量文本输入
语速配置
音色配置
格式配置
```

---

## 16. 语速、音色、格式配置

新增配置：

```text
TTS_SPEED=1.0
TTS_FORMAT=mp3
XIAOMI_TTS_VOICE=
```

设置页字段：

```text
TTS Provider
TTS API Key
TTS Voice
TTS Speed
TTS Format
批量音频最大知识点数量
批量音频最大文本长度
```

校验：

```text
TTS_SPEED 建议范围 0.5 到 2.0
TTS_FORMAT 默认 mp3
TTS_BATCH_MAX_POINTS 建议 1 到 50
TTS_BATCH_MAX_CHARS 建议 1000 到 30000
```

---

## 17. audio_service.py 设计

建议新增函数：

```python
def generate_audio_filename(audio_type: str, source_id: int | None = None, date: str | None = None, ext: str = "mp3") -> str:
    ...

def build_audio_file_url(filename: str) -> str:
    ...

def save_audio_record(db, audio_type, title, source_ids, file_path, file_url, text_content, status):
    ...
```

兼容 V1：

```text
generate_audio_filename("knowledge_point", source_id=12)
```

生成：

```text
kp_12_20260507_103000.mp3
```

---

## 18. tts_service.py 设计

建议新增：

```python
def build_collection_tts_text(knowledge_points: list) -> str:
    ...

def build_daily_review_tts_text(review_tasks: list) -> str:
    ...

def build_wrong_question_tts_text(wrong_questions: list) -> str:
    ...

def generate_tts_audio(text: str, filename: str, settings: dict) -> bytes:
    ...
```

Provider 接口继续保持：

```python
def synthesize(text: str, output_path: str, settings: dict) -> None:
    ...
```

---

## 19. API 接口设计

### 19.1 批量生成音频

```http
POST /api/tts/generate-batch
```

### 19.2 每日复习音频

```http
POST /api/tts/generate-daily-review
```

### 19.3 错题复习音频

```http
POST /api/tts/generate-wrong-questions
```

### 19.4 音频列表增强

```http
GET /api/audio-files?audio_type=collection
```

### 19.5 删除音频

继续使用 V1：

```http
DELETE /api/audio-files/{id}
```

---

## 20. 前端页面设计要求

### 20.1 KnowledgePointListView

新增：

```text
表格多选
批量生成音频按钮
已选择数量提示
```

### 20.2 ReviewView

新增：

```text
生成今日复习音频按钮
```

### 20.3 WrongQuestionView

新增：

```text
勾选错题
生成错题复习音频按钮
```

### 20.4 AudioView

新增：

```text
audio_type 筛选
音频标题
来源数量
播放队列
```

### 20.5 SettingsView

新增：

```text
TTS Speed
TTS Format
TTS_BATCH_MAX_POINTS
TTS_BATCH_MAX_CHARS
```

---

## 21. 播放队列

V2 推荐实现简单播放队列。

功能：

```text
点击播放某个音频
播放结束后自动播放下一条
支持暂停
支持切换上一条 / 下一条
```

V2 初期可选。

最小实现：

```text
仍使用浏览器 audio controls。
```

---

## 22. Loading 与防重复点击

以下按钮必须 loading：

```text
批量生成音频
生成每日复习音频
生成错题复习音频
测试 TTS 连接
```

规则：

```text
loading 时禁用按钮。
同一请求完成前不能重复点击。
失败后恢复按钮。
```

---

## 23. 错误处理

常见错误：

```text
未配置 TTS
知识点不存在
错题不存在
今日没有待复习任务
选择数量超过限制
播报文本超过长度限制
TTS Provider 调用失败
音频文件保存失败
```

错误提示：

```json
{
  "detail": "请选择至少 1 个知识点"
}
```

```json
{
  "detail": "单次最多选择 20 个知识点"
}
```

```json
{
  "detail": "批量音频文本过长，请减少知识点数量"
}
```

---

## 24. 音频生成失败记录

V1 已有 status：

```text
pending
success
failed
```

V2 继续使用。

建议：

```text
生成前先创建 pending 记录。
成功后更新为 success。
失败后更新为 failed，并保存错误信息。
```

如果 audio_files 没有 error_message 字段：

```text
V2 初期可以只返回错误，不写失败记录。
```

---

## 25. 重新生成规则

同一个知识点或合集允许重复生成。

原因：

```text
用户可能修改知识点内容、语速或音色。
```

音频列表中按创建时间倒序展示。

可选功能：

```text
删除旧版本
```

V2 初期不做自动删除。

---

## 26. 安全要求

```text
TTS API Key 不返回明文
TTS API Key 不写入日志
音频文件只保存在 data/audio
删除音频时只能删除 data/audio 下文件
不能根据用户传入路径删除任意文件
```

文件删除必须校验：

```text
目标路径 resolve 后仍在 AUDIO_DIR 内
```

---

## 27. 日志建议

记录：

```text
audio_type
source_ids 数量
文本长度
provider
生成成功 / 失败
耗时
```

不记录：

```text
API Key
完整请求头
敏感配置
```

---

## 28. V2 TTS 验收标准

通过标准：

```text
1. V1 单个知识点音频仍可生成
2. 可以选择多个知识点生成合集音频
3. 超过数量限制时有明确提示
4. 今日无复习任务时生成每日音频有明确提示
5. 可以生成错题复习音频
6. 音频文件保存到 data/audio
7. file_url 可以正常播放
8. AudioView 能区分 audio_type
9. 删除音频时数据库记录和本地文件同步处理
10. TTS 设置能保存语速、格式、批量限制
```

不通过条件：

```text
1. 批量生成无数量限制
2. TTS Key 明文返回前端
3. 音频生成失败没有提示
4. 删除接口可删除 data/audio 外文件
5. 改坏 V1 单知识点音频
```

---

## 29. 推荐开发顺序

```text
1. audio_files 兼容 audio_type / title / source_ids
2. build_collection_tts_text
3. POST /api/tts/generate-batch
4. KnowledgePointListView 批量生成音频
5. AudioView audio_type 筛选
6. POST /api/tts/generate-daily-review
7. ReviewView 生成每日音频
8. POST /api/tts/generate-wrong-questions
9. WrongQuestionView 生成错题音频
10. TTS 设置增强
```

---

## 30. 总结

V2 TTS 的重点是从“单个知识点播放”升级为“复习场景音频”：

```text
多个知识点可以听
每日复习可以听
错题可以听
音频可以按类型管理
批量操作有上限
```

建议先做：

```text
批量知识点音频
AudioView 类型筛选
每日复习音频
```

错题音频和播放队列可以后置。
