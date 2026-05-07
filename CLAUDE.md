# CLAUDE.md

# AI Study Cast 开发规则

你正在协助开发一个本地运行的 AI 知识点学习与音频播报系统。

项目目标：

```text
导入资料 → AI 提取知识点 → AI 生成题目 → 刷题 → 错题本 → TTS 生成音频 → 网页播放复习
```

默认运行地址：

```text
后端：http://localhost:8000
前端：http://localhost:5173
```

---

## 1. 技术栈

前端：

```text
Vue 3 + Vite + TypeScript + Element Plus + Vue Router + Pinia + Axios
```

后端：

```text
Python + FastAPI + SQLAlchemy + SQLite + Pydantic + Uvicorn + httpx + python-dotenv
```

数据库：

```text
data/app.db
```

本地文件：

```text
data/audio/
data/uploads/
data/vector_store/
```

AI：

```text
OpenAI-compatible Chat Completions
```

TTS：

```text
先支持 mock provider，再预留 XiaomiTTSProvider
```

---

## 2. 最高优先级规则

必须遵守：

```text
1. 每次只做一个阶段。
2. 不要一次性开发完整项目。
3. 不要提前开发后续阶段。
4. 不要重写整个项目。
5. 不要删除已有可运行代码。
6. 不要反复无意义修改同一个文件。
7. 不要使用 Docker。
8. 不要做登录注册。
9. 不要做多用户权限。
10. 不要部署云服务器。
11. 不要引入 Redis、Celery、微服务、消息队列。
12. 不要把 API Key 写死进代码。
13. 不要让前端直接调用 AI 或 TTS 外部 API。
14. 所有 AI / TTS 调用必须走后端。
15. 优先保证能运行，再优化界面。
```

---

## 3. 开发前先读

优先阅读：

```text
docs/README_使用顺序_精简版.md
docs/00_项目总览_精简版.md
docs/01_需求说明_PRD_精简版.md
docs/02_技术架构_精简版.md
docs/08_开发阶段计划.md
docs/11_阶段提示词合集.md
```

按需阅读：

```text
docs/03_数据库设计.md
docs/04_接口设计.md
docs/05_AI与提示词设计.md
docs/06_TTS音频生成设计.md
docs/07_前端页面设计_精简版.md
docs/09_环境变量与模型配置_精简版.md
docs/10_验收清单.md
```

如果存在：

```text
docs/ui-prototype.html
```

它只是 UI 视觉参考。正式前端必须写在 `frontend/` 中，不要直接在 HTML 原型上堆业务逻辑。

---

## 4. 开发阶段

严格按阶段推进：

```text
阶段 0：初始化项目结构
阶段 1：后端最小服务
阶段 2：前端最小页面
阶段 3：前后端联通
阶段 4：数据库初始化
阶段 5：知识库管理
阶段 6：资料保存
阶段 7：AI 知识点提取
阶段 8：知识点页面
阶段 9：AI 题目生成
阶段 10：刷题练习
阶段 11：错题本
阶段 12：TTS 音频生成
阶段 13：音频播报页面
阶段 14：设置页面
阶段 15：一键启动脚本
阶段 16：整体联调
阶段 17：界面与体验优化
阶段 18：最终验收
```

当前只做用户指定阶段。

如果用户只说“继续”，根据：

```text
docs/08_开发阶段计划.md
docs/11_阶段提示词合集.md
```

继续下一个阶段。

---

## 5. 开始开发前必须说明

修改文件前先输出：

```text
1. 当前阶段
2. 本阶段目标
3. 计划创建或修改的文件
4. 本阶段不会做哪些后续功能
```

不要直接大规模写代码。

---

## 6. 完成后必须输出

每次完成后必须输出：

```text
1. 本次完成了什么
2. 修改了哪些文件
3. 如何启动后端
4. 如何启动前端
5. 如何测试本阶段
6. 当前未完成或需要用户配置的内容
7. 下一阶段建议
```

---

## 7. 推荐目录结构

```text
ai-study-cast/
├─ frontend/
├─ backend/
├─ data/
│  ├─ uploads/
│  ├─ audio/
│  └─ vector_store/
├─ docs/
├─ scripts/
├─ start.bat
├─ .env.example
├─ .gitignore
├─ CLAUDE.md
└─ README.md
```

后端：

```text
backend/app/
├─ api/routes/
├─ core/
├─ models/
├─ schemas/
├─ services/
├─ utils/
└─ main.py
```

前端：

```text
frontend/src/
├─ api/
├─ components/
├─ layouts/
├─ router/
├─ stores/
├─ types/
├─ utils/
├─ views/
├─ App.vue
└─ main.ts
```

---

## 8. 后端规则

后端使用 FastAPI。

必须遵守：

```text
1. API 路由放在 backend/app/api/routes/。
2. 数据模型放在 backend/app/models/。
3. Pydantic schema 放在 backend/app/schemas/。
4. 业务逻辑放在 backend/app/services/。
5. 配置放在 backend/app/core/config.py。
6. 数据库连接放在 backend/app/core/database.py。
7. 路径管理放在 backend/app/core/paths.py。
8. 工具函数放在 backend/app/utils/。
9. main.py 只负责创建 app、注册路由、配置 CORS、挂载静态文件。
10. 不要把大量业务逻辑写进 main.py。
```

健康检查：

```http
GET /api/health
```

至少返回：

```json
{
  "status": "ok"
}
```

后端启动：

```bash
cd backend
.venv\Scripts\activate
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

---

## 9. 前端规则

前端使用 Vue3 + Vite + TypeScript + Element Plus。

必须遵守：

```text
1. 页面放在 frontend/src/views/。
2. 通用组件放在 frontend/src/components/。
3. 布局组件放在 frontend/src/layouts/。
4. API 封装放在 frontend/src/api/。
5. 类型定义放在 frontend/src/types/。
6. 路由配置放在 frontend/src/router/。
7. Pinia store 放在 frontend/src/stores/。
8. 不要在页面里写大量重复 axios 代码。
9. 不要让前端直接请求 AI 或 TTS 外部服务。
10. 所有外部能力都通过后端 API 调用。
```

前端启动：

```bash
cd frontend
npm run dev
```

---

## 10. API 规则

所有业务接口以 `/api` 开头。

示例：

```text
GET /api/health
GET /api/dashboard/summary
GET /api/knowledge-bases
POST /api/materials
POST /api/ai/extract-points
POST /api/ai/generate-questions
POST /api/tts/generate
```

音频静态路径不使用 `/api`：

```text
/audio/xxx.mp3
```

后端应挂载：

```text
/audio → data/audio
```

---

## 11. 数据库规则

数据库使用 SQLite。

数据库文件必须位于：

```text
data/app.db
```

不能创建到：

```text
backend/data/app.db
```

必须通过 `core/paths.py` 统一管理路径。

V1 核心表：

```text
knowledge_bases
materials
knowledge_points
questions
answer_records
wrong_questions
audio_files
app_settings
```

V1 可用：

```text
Base.metadata.create_all(bind=engine)
```

暂时不要引入 Alembic，除非用户明确要求。

---

## 12. 配置与密钥规则

必须提供：

```text
.env.example
```

必须忽略：

```text
.env
data/
```

真实 API Key 只能放在：

```text
.env
app_settings 数据库表
```

禁止：

```text
把真实 API Key 写进代码
把真实 API Key 写进 README
把真实 API Key 写进 docs
把真实 API Key 打印到日志
把真实 API Key 暴露给前端
```

前端只能保存后端地址：

```text
VITE_API_BASE_URL=http://localhost:8000
```

禁止：

```text
VITE_AI_API_KEY
VITE_XIAOMI_TTS_API_KEY
```

---

## 13. AI 规则

AI 能力由后端封装。

V1 只实现：

```text
AI 提取知识点
AI 生成题目
AI 连接测试
```

必须：

```text
1. 使用 OpenAI-compatible Chat Completions。
2. AI 输出尽量要求 JSON。
3. 后端必须容错解析 JSON。
4. 必须有 json_parser.py。
5. AI 失败时不要保存空数据或脏数据。
6. AI 请求必须有 timeout。
7. AI 长耗时操作前端必须有 loading。
```

后端至少支持解析：

```text
纯 JSON
Markdown JSON 代码块
前后有额外文本的 JSON
```

---

## 14. TTS 规则

TTS 能力由后端封装。

V1 必须支持：

```text
mock provider
xiaomi provider 预留
```

如果真实小米 TTS 接口文档不明确，不要写死接口地址。

正确做法：

```text
1. 先实现 mock provider 打通流程。
2. 预留 XiaomiTTSProvider。
3. 从配置读取 XIAOMI_TTS_BASE_URL 和 XIAOMI_TTS_API_KEY。
4. 由用户后续填入真实接口参数。
```

音频保存目录：

```text
data/audio/
```

音频命名：

```text
kp_{knowledge_point_id}_{timestamp}.mp3
```

数据库保存：

```text
file_path
file_url
status
error_message
```

---

## 15. 页面规则

V1 页面：

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

路由：

```text
/dashboard
/knowledge-bases
/materials/import
/knowledge-points
/knowledge-points/:id
/practice
/wrong-questions
/audio
/settings
```

左侧菜单：

```text
首页
知识库
资料导入
知识点
刷题练习
错题本
音频播报
设置
```

---

## 16. Loading 与错误提示

以下操作必须有 loading：

```text
保存资料
保存并提取知识点
AI 生成题目
TTS 生成音频
提交答案
测试 AI 连接
测试 TTS 连接
删除数据
```

以下情况必须有中文错误提示：

```text
后端连接失败
AI API Key 未配置
AI 接口调用失败
AI JSON 解析失败
TTS API Key 未配置
TTS 生成失败
资料标题为空
资料正文为空
未选择知识库
没有题目
没有错题
没有音频
```

不要只显示：

```text
失败
error
undefined
```

---

## 17. 删除操作

所有删除操作必须二次确认：

```text
删除知识库
删除资料
删除知识点
删除题目
删除错题
删除音频
```

删除音频时：

```text
删除数据库记录
尝试删除本地音频文件
如果文件不存在，不报致命错误
```

删除知识库时，V1 推荐：

```text
非空知识库禁止删除
```

---

## 18. Git 规则

每次修改后提醒用户检查：

```bash
git status
```

不要提交：

```text
.env
data/
app.db
node_modules/
.venv/
dist/
__pycache__/
```

建议按阶段提交：

```text
feat: initialize project structure
feat: add backend health api
feat: add frontend dashboard
feat: add knowledge base crud
```

---

## 19. 报错处理

如果用户给出报错，只做最小修复。

必须：

```text
1. 先解释报错原因。
2. 指出可能涉及的文件。
3. 只修改必要文件。
4. 不要重构整个项目。
5. 修复后给出重新测试命令。
```

---

## 20. 进入循环时

如果反复修改同一个文件、反复失败、反复重写，立即停止。

输出：

```text
我可能进入了循环。
当前已经修改的文件：
当前卡住的问题：
最小修复方案：
下一步只改哪些文件：
如何测试：
```

---

## 21. 阶段完成标准

每个阶段完成后必须保证：

```text
1. 当前阶段功能能测试。
2. 没有破坏之前已完成功能。
3. 前端能启动。
4. 后端能启动。
5. 关键接口能访问。
6. 有明确测试步骤。
```

无法完成时必须说明：

```text
哪些完成了
哪些没完成
卡在哪里
需要用户提供什么
下一步如何修复
```

---

## 22. 最终目标

V1 最终必须跑通：

```text
启动前端和后端
打开网页
新建知识库
导入学习资料
AI 提取知识点
查看知识点
AI 生成题目
刷题
答错进入错题本
生成知识点音频
网页播放音频
重启后数据仍然存在
```

开发优先级：

```text
能运行 > 能保存 > 能调用 > 能展示 > 好看 > 功能丰富
```
