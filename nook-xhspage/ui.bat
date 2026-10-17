@echo off
chcp 65001 >nul
cd /d "%~dp0scripts"
python xhs.py ui
if errorlevel 1 (
  echo.
  echo 启动失败。第一次使用请先双击 setup.bat。
  pause
)
