# 06_TTS音频生成设计

# AI 知识点学习与音频播报系统 - TTS 音频生成设计

## 1. 文档目的

本文档用于定义本项目 V1 版本的 TTS 音频生成方案。

它主要回答：

```text
TTS 在项目里负责什么？
知识点怎么变成播报文本？
后端如何封装 TTS 服务？
音频文件保存在哪里？
前端如何播放音频？
小米 TTS API 如何接入？
失败时如何处理？
后续如何扩展其他 TTS 服务？
```

V1 的目标不是做复杂的音频编辑软件，而是完成：

```text
知识点 → 播报文本 → TTS 生成音频 → 保存本地 MP3 → 网页播放
```

---

## 2. TTS 功能定位

TTS 是本项目的重要增强功能。

它的作用是把文字知识点转成音频，让用户可以：

```text
走路时听
睡前听
重复听
碎片时间复习
把知识点变成自己的学习播客
```

TTS 不是本项目的唯一核心，核心还是：

```text
资料整理
知识点提取
题目练习
错题复习
```

但 TTS 可以让这个项目比普通知识库更有特色。

---

## 3. V1 功能范围

V1 必须实现：

```text
1. 根据知识点生成播报文本。
2. 调用 TTS 服务生成音频。
3. 将音频保存到 data/audio/。
4. 在 audio_files 表中保存音频记录。
5. 前端可以播放音频。
6. 生成失败时记录错误信息。
7. 设置页可以配置 TTS API Key。
```

V1 暂不实现：

```text
多角色配音
背景音乐
音频剪辑
音频合并
批量生成整套课程音频
变速播放
字幕同步
声纹克隆
手机端下载
```

后续版本可以逐步扩展。

---

## 4. 技术原则

TTS 模块必须遵守：

```text
前端不直接调用 TTS API
TTS API Key 不写死在代码里
音频文件统一保存到 data/audio/
数据库只保存音频元数据和路径
TTS 调用封装在后端 service 中
TTS Provider 设计成可替换
```

推荐后端服务文件：

```text
backend/app/services/tts_service.py
```

推荐音频业务服务：

```text
backend/app/services/audio_service.py
```

---

## 5. 整体流程

用户点击“生成音频”后的流程：

```text
前端点击生成音频
↓
POST /api/tts/generate
↓
后端读取 knowledge_point
↓
后端拼接播报文本
↓
后端创建 audio_files 记录，status = pending
↓
后端调用 TTS Provider
↓
TTS 返回音频二进制或音频 URL
↓
后端保存 MP3 到 data/audio/
↓
后端更新 audio_files，status = success
↓
后端返回 file_url
↓
前端显示播放器
```

失败流程：

```text
TTS 调用失败
↓
后端更新 audio_files，status = failed
↓
保存 error_message
↓
前端显示失败提示
```

---

## 6. 目录设计

音频文件保存目录：

```text
data/audio/
```

建议项目目录：

```text
ai-study-cast/
├─ data/
│  ├─ audio/
│  │  ├─ kp_1_20260506_153000.mp3
│  │  ├─ kp_2_20260506_154500.mp3
│  │  └─ ...
│  └─ app.db
```

后端启动时必须确保目录存在：

```text
data/
data/audio/
```

---

## 7. 音频文件命名规则

不要直接使用中文标题作为文件名，避免路径兼容问题。

推荐格式：

```text
kp_{knowledge_point_id}_{timestamp}.mp3
```

示例：

```text
kp_12_20260506_153000.mp3
```

字段说明：

```text
kp                  knowledge point 缩写
12                  知识点 ID
20260506_153000     生成时间
mp3                 音频格式
```

后续如果支持资料整篇播报，可以使用：

```text
material_{material_id}_{timestamp}.mp3
```

如果支持知识库合集播报，可以使用：

```text
kb_{knowledge_base_id}_{timestamp}.mp3
```

---

## 8. 静态文件访问

后端需要把音频目录暴露为静态资源。

映射规则：

```text
/audio → data/audio
```

示例：

```text
data/audio/kp_1_20260506_153000.mp3
```

对应访问地址：

```text
http://localhost:8000/audio/kp_1_20260506_153000.mp3
```

数据库中建议保存相对 URL：

```text
/audio/kp_1_20260506_153000.mp3
```

前端播放时拼接后端地址：

```text
http://localhost:8000 + file_url
```

---

## 9. 数据库表设计

音频记录保存到：

```text
audio_files
```

字段参考：

```text
id
knowledge_point_id
title
text_content
file_path
file_url
duration
status
error_message
created_at
updated_at
```

---

## 10. status 状态设计

音频生成状态：

```text
pending
success
failed
```

说明：

```text
pending    已创建任务，正在生成或等待生成
success    生成成功，可以播放
failed     生成失败，需要查看 error_message
```

V1 可以同步生成，不引入任务队列。

后续如果批量生成音频，可以引入异步任务。

---

## 11. 播报文本生成规则

TTS 不应直接把知识点所有字段粗暴拼接，而是生成一段适合听的播报文本。

播报文本要满足：

```text
自然
简洁
适合听
重点突出
不要有复杂 JSON 符号
不要有 Markdown 标记
不要有太多括号
```

---

## 12. 单个知识点播报文本模板

推荐模板：

```text
知识点：{{title}}。

简要解释：{{summary}}

详细说明：{{detail}}

高频考点包括：
第一，{{exam_point_1}}
第二，{{exam_point_2}}
第三，{{exam_point_3}}

易混点：
{{confusing_points}}

记忆方法：
{{memory_tips}}

例子：
{{examples}}

本知识点播报结束。
```

如果某些字段为空，应自动跳过。

---

## 13. 播报文本示例

知识点：

```text
政府社会职能
```

生成播报文本：

```text
知识点：政府社会职能。

简要解释：政府社会职能，是指政府在社会公共事务管理中承担的职能。

详细说明：政府社会职能主要包括社会保障、公共服务、生态环境保护、社会秩序维护等方面，重点体现政府对民生和社会公共事务的管理与服务。

高频考点包括：
第一，社会保障属于政府社会职能。
第二，公共服务供给属于政府社会职能。
第三，生态环境保护通常也可以归入政府社会职能。

易混点：注意不要把政府社会职能和政府经济职能混淆。宏观调控、市场监管、产业调节更偏经济职能。

记忆方法：看到民生、保障、环境、公共服务，优先想到社会职能。

本知识点播报结束。
```

---

## 14. 文本清洗规则

调用 TTS 前，需要对文本进行清洗。

建议清洗：

```text
去掉 Markdown 标题符号
去掉多余的 *
去掉多余的 #
去掉 JSON 符号
把列表转成自然语言
压缩连续空行
限制文本长度
```

不建议清洗：

```text
不要删除中文标点
不要删除必要的换行
不要删除题目中的 A/B/C/D
```

建议工具文件：

```text
backend/app/utils/text_utils.py
```

方法：

```python
clean_text_for_tts(text: str) -> str
```

---

## 15. 文本长度限制

不同 TTS 服务可能有不同长度限制。

V1 建议后端先设置一个通用限制：

```text
单次 TTS 文本不超过 3000 中文字
```

如果超过，返回提示：

```json
{
  "detail": "播报文本过长，请精简知识点内容后再生成音频"
}
```

后续可扩展：

```text
自动分段生成多个音频
自动合并音频
按章节生成
```

---

## 16. TTS Provider 设计

虽然 V1 主要接入小米 TTS，但后端设计应保留可替换能力。

推荐 Provider 枚举：

```text
xiaomi
mock
```

后续可扩展：

```text
edge
openai
azure
volcengine
aliyun
```

V1 推荐先实现：

```text
mock provider
xiaomi provider
```

其中 mock provider 用于无 API Key 时测试流程。

---

## 17. Mock TTS 设计

为了让项目即使没有小米 TTS API Key 也能先跑通流程，可以实现一个 mock TTS。

Mock TTS 的作用：

```text
不真正调用外部 API
生成一个占位音频文件
或者返回明确提示
```

更推荐 V1 做法：

```text
mock 模式下生成一个简单的空白 mp3 或 wav 占位文件
```

如果实现占位音频麻烦，也可以：

```text
mock 模式只创建 failed 记录并提示需要配置 TTS
```

更利于开发调试的做法：

```text
优先实现 mock provider，生成一个很短的测试音频。
```

这样前端播放流程可以先调通。

---

## 18. 小米 TTS Provider 设计

### 18.1 说明

小米 TTS API 的具体请求地址、鉴权方式、参数名称，应以用户实际申请到的官方文档为准。

本文档不固定写死具体 endpoint。

后端应将这些信息设计成配置项，方便后续调整。

---

### 18.2 配置项建议

```env
TTS_PROVIDER=xiaomi
XIAOMI_TTS_API_KEY=
XIAOMI_TTS_BASE_URL=
XIAOMI_TTS_VOICE=default
XIAOMI_TTS_FORMAT=mp3
XIAOMI_TTS_SPEED=1.0
```

如果小米 TTS 需要额外参数，可以继续增加：

```env
XIAOMI_TTS_APP_ID=
XIAOMI_TTS_SECRET=
XIAOMI_TTS_LANGUAGE=zh-CN
```

---

### 18.3 后端读取配置

配置来源优先级：

```text
数据库 app_settings > .env > 默认值
```

设置页中允许配置：

```text
TTS_PROVIDER
XIAOMI_TTS_API_KEY
XIAOMI_TTS_BASE_URL
XIAOMI_TTS_VOICE
XIAOMI_TTS_FORMAT
XIAOMI_TTS_SPEED
```

---

### 18.4 Provider 接口建议

定义统一接口：

```python
class BaseTTSProvider:
    async def synthesize(self, text: str, options: dict) -> bytes:
        raise NotImplementedError
```

小米实现：

```python
class XiaomiTTSProvider(BaseTTSProvider):
    async def synthesize(self, text: str, options: dict) -> bytes:
        # 读取配置
        # 调用小米 TTS API
        # 返回音频 bytes
        pass
```

Mock 实现：

```python
class MockTTSProvider(BaseTTSProvider):
    async def synthesize(self, text: str, options: dict) -> bytes:
        # 返回测试音频 bytes
        pass
```

---

## 19. tts_service.py 设计

文件位置：

```text
backend/app/services/tts_service.py
```

建议结构：

```python
class TTSService:
    def __init__(self, settings_service):
        self.settings_service = settings_service

    async def test_connection(self) -> dict:
        pass

    def build_text_from_knowledge_point(self, knowledge_point) -> str:
        pass

    async def generate_audio_for_knowledge_point(self, db, knowledge_point_id: int) -> dict:
        pass

    async def synthesize(self, text: str, options: dict | None = None) -> bytes:
        pass
```

核心职责：

```text
读取知识点
构建播报文本
选择 TTS Provider
调用 Provider 生成音频 bytes
保存音频文件
更新 audio_files 表
返回 file_url
```

---

## 20. audio_service.py 设计

文件位置：

```text
backend/app/services/audio_service.py
```

建议职责：

```text
生成安全文件名
保存音频 bytes 到 data/audio
删除音频文件
查询音频列表
拼接 file_url
```

建议方法：

```python
generate_audio_filename(knowledge_point_id: int, ext: str = "mp3") -> str
save_audio_file(filename: str, content: bytes) -> str
delete_audio_file(file_path: str) -> bool
```

---

## 21. API 接口设计

### 21.1 生成音频

```http
POST /api/tts/generate
```

请求体：

```json
{
  "knowledge_point_id": 1
}
```

返回成功：

```json
{
  "audio_id": 1,
  "knowledge_point_id": 1,
  "title": "政府社会职能",
  "status": "success",
  "file_url": "/audio/kp_1_20260506_153000.mp3"
}
```

返回失败：

```json
{
  "detail": "TTS API Key 未配置，请先到设置页配置"
}
```

---

### 21.2 获取音频列表

```http
GET /api/audio-files
```

查询参数：

```text
knowledge_base_id
knowledge_point_id
status
```

返回：

```json
[
  {
    "id": 1,
    "knowledge_point_id": 1,
    "knowledge_point_title": "政府社会职能",
    "title": "政府社会职能",
    "file_url": "/audio/kp_1_20260506_153000.mp3",
    "duration": null,
    "status": "success",
    "error_message": null,
    "created_at": "2026-05-06T15:30:00"
  }
]
```

---

### 21.3 删除音频

```http
DELETE /api/audio-files/{id}
```

返回：

```json
{
  "success": true,
  "message": "音频已删除"
}
```

删除时：

```text
删除数据库记录
尝试删除本地音频文件
本地文件不存在时不报致命错误
```

---

### 21.4 测试 TTS 连接

```http
POST /api/settings/test-tts
```

返回成功：

```json
{
  "success": true,
  "message": "TTS 连接正常"
}
```

返回失败：

```json
{
  "success": false,
  "message": "TTS 连接失败：API Key 未配置"
}
```

---

## 22. 前端页面设计要求

TTS 相关页面主要有两个：

```text
知识点详情页
音频播报页面
```

---

### 22.1 知识点详情页

按钮：

```text
生成音频
播放音频
重新生成
```

展示：

```text
最近生成的音频
生成状态
播放器
错误信息
```

如果没有音频：

```text
显示“暂无音频，点击生成音频”
```

如果生成中：

```text
按钮 loading
显示“正在生成音频，请稍候”
```

如果失败：

```text
显示失败原因
提供重新生成按钮
```

---

### 22.2 音频播报页面

展示音频列表：

```text
音频标题
关联知识点
生成时间
状态
播放按钮
删除按钮
```

V1 可用 HTML5 audio：

```html
<audio controls :src="audioUrl"></audio>
```

---

## 23. 前端音频地址处理

后端返回：

```text
/audio/kp_1_20260506_153000.mp3
```

前端拼接：

```typescript
const backendBaseUrl = 'http://localhost:8000'
const audioUrl = `${backendBaseUrl}${file_url}`
```

后续可以把后端地址放到配置：

```env
VITE_API_BASE_URL=http://localhost:8000
```

---

## 24. Loading 与防重复点击

以下操作必须有 loading：

```text
生成音频
重新生成音频
测试 TTS 连接
删除音频
```

生成音频期间：

```text
按钮禁用
显示 loading
防止重复点击生成多个相同音频
```

---

## 25. 错误处理

### 25.1 常见错误

```text
知识点不存在
知识点内容为空
TTS_PROVIDER 未配置
TTS API Key 未配置
TTS Base URL 未配置
TTS 请求超时
TTS 返回空音频
音频保存失败
音频文件不存在
```

---

### 25.2 错误提示示例

```json
{
  "detail": "知识点不存在"
}
```

```json
{
  "detail": "TTS API Key 未配置，请先到设置页配置"
}
```

```json
{
  "detail": "TTS 生成失败，请检查接口配置"
}
```

```json
{
  "detail": "音频保存失败，请检查 data/audio 目录权限"
}
```

---

## 26. 音频生成失败记录

即使生成失败，也建议保存 audio_files 记录：

```text
status = failed
error_message = 错误原因
```

这样前端可以展示失败历史，方便排错。

但如果知识点不存在，则不需要创建记录。

---

## 27. 重新生成规则

当用户点击重新生成时：

```text
创建新的 audio_files 记录
生成新的音频文件
不覆盖旧音频
```

优点：

```text
保留历史版本
避免覆盖失败导致旧音频丢失
```

后续可以提供“删除旧版本”功能。

---

## 28. 文本到音频的字段映射

知识点字段：

```text
title
summary
detail
exam_points
confusing_points
memory_tips
examples
```

播报文本使用优先级：

```text
title 必须使用
summary 有则使用
detail 有则使用
exam_points 有则使用
confusing_points 有则使用
memory_tips 有则使用
examples 可选使用
```

不建议把：

```text
tags
importance
ai_raw_response
```

直接播报出来。

---

## 29. 多知识点音频扩展设计

V1 只做单个知识点。

V2 可以做：

```text
选中多个知识点
生成合集播报文本
分段调用 TTS
合并音频
生成一整期学习音频
```

接口可以扩展为：

```http
POST /api/tts/generate-batch
```

请求：

```json
{
  "knowledge_point_ids": [1, 2, 3]
}
```

---

## 30. 每日音频学习包扩展设计

后续可以做：

```text
今日待复习知识点
↓
自动生成播报稿
↓
生成每日音频
↓
音频播报页面播放
```

对应功能：

```text
每日学习播报
错题音频复习
考前冲刺音频
```

V1 不做。

---

## 31. 语速、音色、格式扩展

V1 可以预留配置项：

```text
XIAOMI_TTS_VOICE
XIAOMI_TTS_SPEED
XIAOMI_TTS_FORMAT
```

设置页可先只展示：

```text
TTS Provider
TTS API Key
TTS Voice
```

后续再加：

```text
语速
音量
音调
格式
```

---

## 32. 安全要求

TTS API Key 属于敏感信息。

要求：

```text
不写死在代码中
不提交到 Git
设置页显示时脱敏
后端日志不要打印完整 Key
.env.example 只放空值
```

`.gitignore` 必须包含：

```text
.env
data/
```

---

## 33. 日志建议

TTS 相关日志可以记录：

```text
开始生成音频
knowledge_point_id
音频文件名
生成成功
生成失败原因
```

不要记录：

```text
完整 API Key
过长播报文本
用户敏感资料全文
```

---

## 34. V1 开发顺序建议

推荐按以下顺序实现：

```text
1. 创建 audio_files 数据表和模型。
2. 后端挂载 /audio 静态目录。
3. 实现 audio_service 保存音频文件。
4. 实现 build_text_from_knowledge_point。
5. 实现 mock TTS provider。
6. 打通 POST /api/tts/generate。
7. 前端知识点详情页增加生成音频按钮。
8. 前端播放生成的音频。
9. 实现音频列表页面。
10. 接入小米 TTS provider。
11. 设置页增加 TTS 配置和测试连接。
```

这样即使小米 TTS 暂时没接好，前端和数据库流程也可以先跑通。

---

## 35. 给 Claude Code / Codex 的开发提示词

可以这样要求 AI 编程工具实现：

```text
请根据 docs/06_TTS音频生成设计.md 实现 TTS 音频生成模块。

要求：
1. 创建 audio_files 数据模型和接口。
2. 后端启动时自动创建 data/audio 目录。
3. 在 FastAPI 中挂载 /audio 静态文件目录。
4. 创建 audio_service.py，负责保存和删除音频文件。
5. 创建 tts_service.py，负责构建播报文本和调用 TTS Provider。
6. 先实现 mock TTS Provider，用于打通流程。
7. 预留 XiaomiTTSProvider，但不要写死具体接口地址。
8. TTS API Key 从设置或 .env 读取，不要写死。
9. 实现 POST /api/tts/generate。
10. 实现 GET /api/audio-files。
11. 实现 DELETE /api/audio-files/{id}。
12. 前端知识点详情页可以点击生成音频并播放。
13. 前端音频页面可以查看和播放音频列表。
14. 失败时要保存 error_message 并在前端显示。
15. 完成后告诉我如何测试。
```

---

## 36. V1 验收标准

TTS 模块完成后，应满足：

```text
1. 后端启动时自动创建 data/audio 目录。
2. 后端可以通过 /audio 访问音频文件。
3. 知识点详情页有“生成音频”按钮。
4. 点击生成音频后，后端创建 audio_files 记录。
5. 后端能根据知识点生成自然播报文本。
6. 音频文件保存到 data/audio。
7. 数据库保存 file_path 和 file_url。
8. 前端可以播放生成的音频。
9. 音频播报页面可以显示音频列表。
10. 可以删除音频记录和本地文件。
11. TTS API Key 不写死在代码里。
12. TTS 调用失败时，前端能看到清晰错误提示。
13. 没有真实 TTS Key 时，mock provider 也能帮助打通流程。
```

---

## 37. 总结

TTS 模块的核心闭环是：

```text
知识点
↓
播报文本
↓
TTS 生成
↓
本地音频文件
↓
网页播放
```

V1 不追求复杂音频功能。

优先保证：

```text
能生成
能保存
能播放
能失败提示
能后续替换 Provider
```

这样项目就能从普通知识库升级成真正的“AI 知识点音频学习系统”。
