# 01_需求说明_PRD_精简版

# AI 知识点学习与音频播报系统 - 需求说明 PRD

## 1. 文档目的

本文档用于明确 V1 版本要做什么、不做什么，以及每个核心功能的边界。

项目核心闭环：

```text
知识库 → 学习资料 → AI 提取知识点 → AI 生成题目 → 刷题 → 错题本 → TTS 音频 → 播放复习
```

---

## 2. 项目背景

用户在备考三支一扶、公基、时政、管理学、法律、经济、古文等内容时，常见问题是：

```text
资料多
整理慢
考点不清
出题麻烦
错题分散
想听知识点但生成音频麻烦
```

本项目用 AI 辅助完成：

```text
资料整理
知识点提取
题目生成
错题沉淀
音频复习
```

---

## 3. V1 产品目标

V1 目标是完成最小可用学习闭环：

```text
新建知识库
导入资料
AI 提取知识点
查看知识点
AI 生成题目
刷题练习
记录错题
生成音频
播放音频
保存配置
本地持久化
```

V1 第一原则：

```text
能运行
流程通
数据不丢
错误有提示
```

---

## 4. V1 不做内容

V1 暂不做：

```text
登录注册
多用户权限
云同步
Docker
手机 App
浏览器插件
支付系统
复杂 RAG
批量 PDF 深度解析
Word 深度解析
OCR
桌面打包
```

---

## 5. 用户角色

V1 只有一个角色：

```text
本机使用者
```

不做账号系统、管理员、权限分组。

---

## 6. 使用环境

优先支持：

```text
Windows 10 / Windows 11
```

运行方式：

```text
后端 FastAPI：http://localhost:8000
前端 Vite：http://localhost:5173
浏览器访问使用
```

---

## 7. 核心业务对象

```text
知识库
学习资料
知识点
题目
答题记录
错题
音频文件
系统设置
```

---

# 8. 功能需求

## 8.1 首页仪表盘

### 功能

展示学习数据概览。

### 显示内容

```text
知识库数量
学习资料数量
知识点数量
题目数量
错题数量
音频数量
后端连接状态
```

### 接口

```http
GET /api/dashboard/summary
```

返回示例：

```json
{
  "knowledge_base_count": 3,
  "material_count": 12,
  "knowledge_point_count": 58,
  "question_count": 120,
  "wrong_question_count": 9,
  "audio_count": 14
}
```

---

## 8.2 知识库管理

### 功能

用于分类管理学习资料。

示例：

```text
三支一扶
公共基础知识
时政
管理学
法律常识
经济常识
古文
```

### 字段

```text
id
name
description
sort_order
created_at
updated_at
```

### 页面功能

```text
查看列表
新建知识库
编辑名称和描述
删除知识库
查看资料数量和知识点数量
```

### 删除规则

V1 推荐：

```text
非空知识库禁止删除
```

### 接口

```http
GET    /api/knowledge-bases
POST   /api/knowledge-bases
GET    /api/knowledge-bases/{id}
PUT    /api/knowledge-bases/{id}
DELETE /api/knowledge-bases/{id}
```

---

## 8.3 资料导入

### 功能

V1 只支持：

```text
手动粘贴文本
```

暂不支持：

```text
PDF
Word
网页抓取
OCR
批量导入
```

### 表单字段

```text
所属知识库：必选
资料标题：必填
资料正文：必填
资料来源：选填
备注：选填
```

### 操作按钮

```text
保存资料
保存并提取知识点
清空
```

### 字段

```text
id
knowledge_base_id
title
content
source
note
material_type
file_path
content_length
extracted_count
created_at
updated_at
```

### 接口

```http
GET    /api/materials
POST   /api/materials
GET    /api/materials/{id}
PUT    /api/materials/{id}
DELETE /api/materials/{id}
POST   /api/materials/import-and-extract
```

---

## 8.4 AI 知识点提取

### 功能

根据资料正文生成结构化知识点。

### 输入

```text
知识库名称
资料标题
资料正文
```

### 输出字段

```text
title
summary
detail
exam_points
confusing_points
memory_tips
examples
importance
tags
```

### importance 可选值

```text
low
medium
high
```

### tags

使用中文标签数组，例如：

```json
["公基", "政府职能"]
```

### 接口

```http
POST /api/ai/extract-points
```

请求示例：

```json
{
  "material_id": 1
}
```

### 异常处理

必须处理：

```text
AI API Key 未配置
AI 请求失败
AI 返回不是 JSON
AI 返回空结果
资料过长
```

---

## 8.5 知识点管理

### 页面

```text
/knowledge-points
/knowledge-points/:id
```

### 列表页功能

```text
按知识库筛选
关键词搜索
按重要程度筛选
按标签筛选
查看摘要
进入详情
删除知识点
```

### 详情页展示

```text
标题
摘要
详细解释
高频考点
易混点
记忆方法
示例
标签
重要程度
来源资料
关联题目
关联音频
```

### 详情页按钮

```text
编辑
删除
生成题目
生成音频
播放音频
返回列表
```

### 接口

```http
GET    /api/knowledge-points
GET    /api/knowledge-points/{id}
PUT    /api/knowledge-points/{id}
DELETE /api/knowledge-points/{id}
```

---

## 8.6 AI 题目生成

### V1 支持题型

```text
single_choice
true_false
```

暂不做：

```text
multiple_choice
short_answer
```

### 题目字段

```text
id
knowledge_base_id
knowledge_point_id
question_type
stem
options
answer
analysis
difficulty
created_at
updated_at
```

### difficulty 可选值

```text
easy
medium
hard
```

### 单选题要求

```text
必须有 A/B/C/D 四个选项
只能有一个正确答案
answer 必须是 A/B/C/D
```

### 判断题要求

```text
options 使用 true / false
answer 必须是 true 或 false
```

### 接口

```http
POST /api/ai/generate-questions
```

请求示例：

```json
{
  "knowledge_point_id": 1,
  "question_types": ["single_choice", "true_false"],
  "count": 5
}
```

---

## 8.7 刷题练习

### 页面

```text
/practice
```

### 功能

```text
选择知识库
选择知识点
选择题型
设置题目数量
开始练习
提交答案
查看解析
下一题
显示结果
```

### 提交流程

```text
查询题目
对比答案
保存 answer_records
如果答错，新增或更新 wrong_questions
返回正确答案和解析
```

### 接口

```http
GET  /api/practice/questions
POST /api/practice/answer
```

请求示例：

```json
{
  "question_id": 1,
  "user_answer": "B"
}
```

---

## 8.8 错题本

### 页面

```text
/wrong-questions
```

### 功能

```text
查看错题
查看答案和解析
显示错误次数
重新练习
标记已掌握
取消掌握
删除错题记录
```

### 规则

同一道题多次答错：

```text
不重复新增记录
wrong_count + 1
更新 last_wrong_answer
更新 last_wrong_at
is_mastered = false
```

### 接口

```http
GET    /api/wrong-questions
POST   /api/wrong-questions/{id}/mark-mastered
POST   /api/wrong-questions/{id}/unmark-mastered
DELETE /api/wrong-questions/{id}
```

---

## 8.9 TTS 音频生成

### 功能

将知识点转换成播报音频。

### 流程

```text
选择知识点
构建播报文本
调用 TTS
保存到 data/audio
写入 audio_files
前端播放
```

### 音频命名

```text
kp_{knowledge_point_id}_{timestamp}.mp3
```

### 状态

```text
pending
success
failed
```

### 接口

```http
POST /api/tts/generate
```

请求示例：

```json
{
  "knowledge_point_id": 1
}
```

返回示例：

```json
{
  "audio_id": 1,
  "status": "success",
  "file_url": "/audio/kp_1_20260506_153000.mp3"
}
```

---

## 8.10 音频播放

### 页面

```text
/audio
```

### 功能

```text
查看音频列表
按知识库筛选
播放音频
删除音频
重新生成
查看关联知识点
```

### 播放方式

```html
<audio controls src="音频地址"></audio>
```

### 接口

```http
GET    /api/audio-files
GET    /api/audio-files/{id}
DELETE /api/audio-files/{id}
```

---

## 8.11 系统设置

### 页面

```text
/settings
```

### AI 设置

```text
AI_PROVIDER
AI_API_KEY
AI_BASE_URL
AI_MODEL
AI_TEMPERATURE
AI_TIMEOUT
```

### TTS 设置

```text
TTS_PROVIDER
XIAOMI_TTS_API_KEY
XIAOMI_TTS_BASE_URL
XIAOMI_TTS_VOICE
XIAOMI_TTS_FORMAT
XIAOMI_TTS_SPEED
```

### 安全规则

```text
API Key 不完整展示
留空敏感字段时保留旧值
真实 Key 不写进代码
```

### 接口

```http
GET  /api/settings
PUT  /api/settings
POST /api/settings/test-ai
POST /api/settings/test-tts
```

---

## 8.12 错误提示

常见错误必须有中文提示：

```text
后端连接失败
AI Key 未配置
AI 调用失败
AI JSON 解析失败
TTS Key 未配置
TTS 生成失败
数据库保存失败
资料正文为空
未选择知识库
题目数量不合法
音频文件不存在
```

---

# 9. V1 页面清单

```text
首页仪表盘
知识库页面
资料导入页面
知识点列表页
知识点详情页
刷题练习页
错题本页面
音频播报页面
设置页面
```

如果存在：

```text
docs/ui-prototype.html
```

它只作为视觉参考，正式前端仍写在 `frontend/` 中。

---

# 10. V1 接口清单

```http
GET /api/health
GET /api/dashboard/summary

GET    /api/knowledge-bases
POST   /api/knowledge-bases
GET    /api/knowledge-bases/{id}
PUT    /api/knowledge-bases/{id}
DELETE /api/knowledge-bases/{id}

GET    /api/materials
POST   /api/materials
GET    /api/materials/{id}
PUT    /api/materials/{id}
DELETE /api/materials/{id}
POST   /api/materials/import-and-extract

GET    /api/knowledge-points
GET    /api/knowledge-points/{id}
PUT    /api/knowledge-points/{id}
DELETE /api/knowledge-points/{id}

POST /api/ai/extract-points
POST /api/ai/generate-questions

GET    /api/questions
GET    /api/questions/{id}
DELETE /api/questions/{id}

GET  /api/practice/questions
POST /api/practice/answer

GET    /api/wrong-questions
POST   /api/wrong-questions/{id}/mark-mastered
POST   /api/wrong-questions/{id}/unmark-mastered
DELETE /api/wrong-questions/{id}

POST   /api/tts/generate
GET    /api/audio-files
GET    /api/audio-files/{id}
DELETE /api/audio-files/{id}

GET  /api/settings
PUT  /api/settings
POST /api/settings/test-ai
POST /api/settings/test-tts
```

---

# 11. V1 验收标准

V1 完成后必须满足：

```text
后端可以启动
前端可以启动
首页可以访问
可以新建知识库
可以保存资料
可以 AI 提取知识点
可以查看知识点
可以 AI 生成题目
可以刷题
答错进入错题本
可以生成音频
可以播放音频
可以保存设置
重启后数据仍存在
API Key 不会进入代码或 Git
```

---

# 12. 开发注意事项

```text
不要一次性做完所有功能
每次只做一个阶段
优先保证能运行
不要使用 Docker
不要做登录注册
不要引入 Redis / Celery / 微服务
不要让前端直接调用 AI 或 TTS
不要把 API Key 写死
```

---

# 13. 总结

V1 的核心需求是：

```text
把学习资料交给 AI
让 AI 整理成知识点
让 AI 生成题目
让用户刷题
让错题沉淀
让知识点变成音频
让用户可以听着复习
```

第一版只要把这条链路跑通，就是成功。
