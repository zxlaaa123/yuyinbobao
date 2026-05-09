# AI Study Cast

本地运行的 AI 知识点学习、刷题复习与音频播报系统。

核心目标不是做一个聊天工具，而是把学习资料变成可长期复习的结构化资产：

```text
资料导入 -> AI 提取知识点 -> AI 生成题目 -> 多题型练习 -> 错题沉淀
-> 间隔复习 -> 学习会话总结 -> 音频复习 -> 数据导出
```

当前主线版本：V4。V4 的定位是把 V3 的“可用系统”升级成“可长期学习的本地学习系统”。

---

## 1. 当前状态

已完成到：阶段 55。

V4 已完成：

```text
AI 日志增强
间隔重复复习字段与服务
答题结果联动复习计划
首页复习概览
五种题型生成与作答
学习会话记录
练习结束总结页
练习历史页
```

V4 未完成：

```text
阶段 56：PDF 文本导入
阶段 57：CSV 导出增强
阶段 58：音频播放列表增强
阶段 59：设置页增强
阶段 60：V4 回归测试与验收
```

---

## 2. 技术栈

前端：

```text
Vue 3
Vite
TypeScript
Element Plus
Vue Router
Pinia
Axios
```

后端：

```text
Python
FastAPI
SQLAlchemy
SQLite
Pydantic
Uvicorn
httpx
python-dotenv
```

AI：

```text
OpenAI-compatible Chat Completions
```

TTS：

```text
mock provider
XiaomiTTSProvider 预留
```

---

## 3. 默认地址

```text
后端：http://localhost:8000
前端：http://localhost:5173
数据库：data/app.db
音频目录：data/audio/
上传目录：data/uploads/
```

健康检查：

```http
GET /api/health
```

---

## 4. 快速启动

### 4.1 首次安装

后端：

```powershell
cd D:\yuyinbobao\backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

前端：

```powershell
cd D:\yuyinbobao\frontend
npm install
```

### 4.2 日常启动

后端：

```powershell
cd D:\yuyinbobao\backend
.\.venv\Scripts\activate
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

前端：

```powershell
cd D:\yuyinbobao\frontend
npm run dev
```

一键启动：

```text
双击 start.bat
```

---

## 5. 环境配置

真实密钥不要写进代码、README 或前端环境变量。

可配置位置：

```text
.env
app_settings 数据库表
```

参考文件：

```text
.env.example
docs4/09_环境变量与模型配置_V4.md
```

前端只保存后端地址：

```text
VITE_API_BASE_URL=http://localhost:8000
```

禁止：

```text
VITE_AI_API_KEY
VITE_XIAOMI_TTS_API_KEY
```

---

## 6. 项目结构

```text
yuyinbobao/
├─ backend/
│  └─ app/
│     ├─ api/routes/          # FastAPI 路由
│     ├─ core/                # 配置、数据库、路径、迁移补字段
│     ├─ models/              # SQLAlchemy 模型
│     ├─ schemas/             # Pydantic schema
│     ├─ services/            # AI、TTS、复习、解析等业务服务
│     ├─ utils/               # 工具函数
│     └─ main.py              # 应用入口
├─ frontend/
│  └─ src/
│     ├─ api/                 # Axios API 封装
│     ├─ components/          # 通用组件
│     ├─ layouts/             # 页面布局
│     ├─ router/              # 路由配置
│     ├─ stores/              # Pinia 状态
│     ├─ types/               # 类型定义
│     ├─ utils/               # 前端工具
│     └─ views/               # 页面
├─ data/
│  ├─ app.db                  # SQLite 数据库
│  ├─ audio/                  # 本地音频文件
│  ├─ uploads/                # 上传文件
│  └─ vector_store/           # 向量存储预留
├─ docs3/                     # V3 文档
├─ docs4/                     # V4 文档
├─ scripts/
├─ start.bat
├─ .env.example
└─ README.md
```

---

## 7. 主要页面

```text
/dashboard              首页仪表盘
/knowledge-bases        知识库
/materials/import       资料导入
/knowledge-points       知识点列表
/knowledge-points/:id   知识点详情
/practice               刷题练习
/practice-sessions      练习历史
/practice-sessions/:id  练习会话详情
/wrong-questions        错题本
/review                 复习计划
/audio                  音频播报
/ai-call-logs           AI 日志
/settings               设置
```

---

## 8. V4 功能说明

### 8.1 AI 日志增强

AI 调用会记录：

```text
调用类型
模型名称
base_url host
状态 success / failed
错误类型
错误信息摘要
输入摘要
输出摘要
JSON 解析状态
token 用量
耗时
创建时间
```

安全规则：

```text
不保存 API Key
不向前端返回 API Key
不打印完整密钥
失败日志不污染业务表
```

相关页面：

```text
/ai-call-logs
```

### 8.2 间隔重复复习

知识点新增复习字段：

```text
mastery_level
review_count
correct_streak
wrong_streak
last_reviewed_at
next_review_at
review_status
```

答题联动规则：

```text
答对：提高熟练度，延后下次复习
答错：降低熟练度，提前复习，并进入错题本
```

相关接口：

```http
GET /api/review/today
POST /api/practice/answer
```

### 8.3 多题型

支持题型：

```text
single_choice    单选题
multiple_choice  多选题
true_false       判断题
fill_blank       填空题
short_answer     简答题
```

说明：

```text
简答题 V4 只展示参考答案。
不做 AI 自动判分。
```

### 8.4 学习会话

练习结束后保存：

```text
总题数
正确数
错误数
正确率
耗时
涉及知识点
薄弱知识点
错题列表
建议复习内容
每题作答明细
```

相关页面：

```text
/practice-sessions
/practice-sessions/:id
```

---

## 9. API 概览

基础：

```http
GET /api/health
GET /api/dashboard/summary
```

知识库 / 资料 / 知识点：

```http
GET    /api/knowledge-bases
POST   /api/knowledge-bases
GET    /api/materials
POST   /api/materials
GET    /api/knowledge-points
GET    /api/knowledge-points/{id}
```

AI：

```http
POST /api/ai/extract-points
POST /api/ai/generate-questions
GET  /api/ai-call-logs
GET  /api/ai-call-logs/{id}
DELETE /api/ai-call-logs/{id}
```

练习：

```http
GET  /api/practice/questions
POST /api/practice/answer
POST /api/practice/sessions
GET  /api/practice/sessions
GET  /api/practice/sessions/{id}
```

复习：

```http
GET /api/review/today
```

错题 / 音频 / 导出：

```http
GET    /api/wrong-questions
POST   /api/tts/generate
GET    /api/audio-files
GET    /api/export/questions.csv
GET    /api/export/wrong-questions.csv
GET    /api/export/knowledge-points.csv
```

---

## 10. 阶段进度

### V1 / V2 / V3 基础能力

| 阶段 | 状态 | 内容 |
|---|---:|---|
| 阶段 0 | 已完成 | 初始化项目结构 |
| 阶段 1 | 已完成 | 后端最小服务，提供 `/api/health` |
| 阶段 2 | 已完成 | 前端最小页面 |
| 阶段 3 | 已完成 | 前后端联通 |
| 阶段 4 | 已完成 | SQLite 数据库初始化 |
| 阶段 5 | 已完成 | 知识库管理 |
| 阶段 6 | 已完成 | 资料保存 |
| 阶段 7 | 已完成 | AI 知识点提取 |
| 阶段 8 | 已完成 | 知识点列表、详情、编辑、删除 |
| 阶段 9 | 已完成 | AI 题目生成 |
| 阶段 10 | 已完成 | 刷题练习 |
| 阶段 11 | 已完成 | 错题本 |
| 阶段 12 | 已完成 | TTS 音频生成 |
| 阶段 13 | 已完成 | 音频播报页面 |
| 阶段 14 | 已完成 | 设置页面 |
| 阶段 15 | 已完成 | 一键启动脚本 |
| 阶段 16 | 已完成 | 整体联调 |
| 阶段 17 | 已完成 | 界面与体验优化 |
| 阶段 18 | 已完成 | V1 验收闭环 |

### V4 阶段

| 阶段 | 状态 | 内容 |
|---|---:|---|
| 阶段 43 | 已完成 | 创建 `docs4/` 文档与 V4 范围说明 |
| 阶段 44 | 已完成 | AI 日志增强设计 |
| 阶段 45 | 已完成 | AI 日志后端接口 |
| 阶段 46 | 已完成 | AI 日志前端页面 |
| 阶段 47 | 已完成 | 知识点复习计划数据库字段 |
| 阶段 48 | 已完成 | 间隔重复服务与 `/api/review/today` |
| 阶段 49 | 已完成 | 答题结果联动复习计划 |
| 阶段 50 | 已完成 | 首页复习概览 |
| 阶段 51 | 已完成 | 多题型数据结构 |
| 阶段 52 | 已完成 | AI 多题型生成 |
| 阶段 53 | 已完成 | 刷题页多题型支持 |
| 阶段 54 | 已完成 | 学习会话记录 |
| 阶段 55 | 已完成 | 练习结束总结页与练习历史页 |
| 阶段 56 | 未开始 | PDF 文本导入 |
| 阶段 57 | 未开始 | CSV 导出增强 |
| 阶段 58 | 未开始 | 音频播放列表增强 |
| 阶段 59 | 未开始 | 设置页增强 |
| 阶段 60 | 未开始 | V4 回归测试与验收 |

---

## 11. 测试与检查

后端编译检查：

```powershell
python -m compileall backend/app
```

前端构建检查：

```powershell
cd frontend
npm run build
```

健康检查：

```powershell
python -c "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:8000/api/health').read().decode())"
```

数据库表检查：

```powershell
python -c "import sqlite3; conn=sqlite3.connect(r'D:\yuyinbobao\data\app.db'); c=conn.cursor(); c.execute('SELECT name FROM sqlite_master WHERE type=\"table\"'); print([r[0] for r in c.fetchall()]); conn.close()"
```

---

## 12. Git 与本地数据

不要提交：

```text
.env
data/
node_modules/
.venv/
dist/
__pycache__/
```

提交前检查：

```powershell
git status
```

---

## 13. 重要约束

项目当前坚持：

```text
本地单用户
SQLite
不引入 Alembic
不使用 Docker
不做登录注册
不做多用户权限
不引入 Redis / Celery
不做云同步
前端不直接调用 AI / TTS 外部 API
```

外部 AI / TTS 调用必须走后端。

---

## 14. 文档入口

V4 推荐阅读顺序：

```text
docs4/README_使用顺序_V4.md
docs4/01_需求说明_PRD_V4.md
docs4/02_技术架构_V4.md
docs4/03_数据库设计_V4.md
docs4/04_接口设计_V4.md
docs4/08_开发阶段计划_V4.md
docs4/10_验收清单_V4.md
docs4/11_阶段提示词合集_V4.md
```
