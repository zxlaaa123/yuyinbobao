@echo off
echo ========================================
echo   AI 知识点学习与音频播报系统
echo ========================================
echo.

if not exist "D:\yuyinbobao\backend\.venv" (
    echo [提示] 后端虚拟环境不存在，请先运行 D:\yuyinbobao\scripts\init_backend.bat
    pause
    exit /b 1
)

if not exist "D:\yuyinbobao\frontend\node_modules" (
    echo [提示] 前端依赖未安装，请先运行 D:\yuyinbobao\scripts\init_frontend.bat
    pause
    exit /b 1
)

echo 正在启动后端...
start cmd /k "cd /d D:\yuyinbobao\backend && .venv\Scripts\activate && uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"

echo 正在启动前端...
start cmd /k "cd /d D:\yuyinbobao\frontend && npm run dev"

echo.
echo 后端地址：http://127.0.0.1:8000
echo 前端地址：http://localhost:5173
echo.
pause
