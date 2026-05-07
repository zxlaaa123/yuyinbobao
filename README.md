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

## 开发阶段

按 `docs/08_开发阶段计划.md` 分阶段开发，每次只做一个阶段。

## 快速启动

1. 复制 `.env.example` 为 `.env`，填写 API Key
2. 初始化后端：`scripts/init_backend.bat`
3. 初始化前端：`scripts/init_frontend.bat`
4. 启动：`start.bat`
