# AI 知识点学习与音频播报系统

本地运行的 AI 知识点学习与音频播报系统。

**核心流程：**

```
导入资料 → AI 提取知识点 → AI 生成题目 → 刷题 → 错题本 → TTS 生成音频 → 网页播放复习
```

## 默认地址

- 后端：http://localhost:8000
- 前端：http://localhost:5173

## 技术栈

- 前端：Vue 3 + Vite + TypeScript + Element Plus
- 后端：Python + FastAPI + SQLite

## 项目结构

```
ai-study-cast/
├── frontend/          # Vue3 前端
│   └── src/
│       ├── api/       # Axios 封装 + 接口调用
│       └── App.vue    # 首页
├── backend/           # FastAPI 后端
│   └── app/
│       ├── core/      # paths.py, database.py
│       ├── models/    # 8 个 SQLAlchemy 模型
│       └── main.py    # 入口 + 路由
├── data/              # 本地数据
│   ├── app.db         # SQLite 数据库
│   ├── audio/         # TTS 音频文件
│   ├── uploads/       # 上传文件
│   └── vector_store/  # 向量存储（预留）
└── docs/              # 开发文档（未提交）
```

## 已完成阶段

- [x] 阶段 0：初始化项目结构
- [x] 阶段 1：后端最小服务（FastAPI + /api/health）
- [x] 阶段 2：前端最小页面（Vue3 + Element Plus）
- [x] 阶段 3：前后端联通（Axios + 健康检查状态条）
- [x] 阶段 4：数据库初始化（SQLite + 8 张表）

## 快速启动

### 首次安装

```powershell
# 后端
cd D:\yuyinbobao\backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt

# 前端
cd D:\yuyinbobao\frontend
npm install
```

### 日常启动

```powershell
# 后端
cd D:\yuyinbobao\backend
.\.venv\Scripts\activate
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# 前端
cd D:\yuyinbobao\frontend
npm run dev
```

### 一键启动

```
双击 D:\yuyinbobao\start.bat
```

## 验证

```powershell
# 后端健康检查
python -c "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:8000/api/health').read().decode())"

# 数据库检查
python -c "import sqlite3; conn=sqlite3.connect(r'D:\yuyinbobao\data\app.db'); c=conn.cursor(); c.execute('SELECT name FROM sqlite_master WHERE type=\"table\"'); print([r[0] for r in c.fetchall()]); conn.close()"
```

## 开发阶段

按 `docs/08_开发阶段计划.md` 分阶段开发，每次只做一个阶段。
