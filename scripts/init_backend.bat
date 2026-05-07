@echo off
echo 初始化后端环境...

cd /d D:\yuyinbobao\backend

python -m venv .venv
call .venv\Scripts\activate

pip install -r requirements.txt

echo.
echo 后端初始化完成。
pause
