@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo 需要 Python 3.10 或更高版本（python.org，安装时勾选 Add Python to PATH）。
python -m pip install -r requirements.txt
python -m playwright install chromium
echo.
echo 安装结束。运行自检：进入 scripts 目录，运行 python xhs.py selftest
pause
