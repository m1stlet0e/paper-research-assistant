@echo off
REM AI论文全自动预研助手 - 可视化界面启动脚本 (Windows)

echo ==========================================
echo AI论文全自动预研助手
echo 可视化界面启动
echo ==========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误：未找到Python
    echo 请先安装Python 3.x
    echo 下载地址：https://www.python.org/downloads/
    pause
    exit /b 1
)

REM 检查index.html是否存在
if not exist "index.html" (
    echo ❌ 错误：index.html不存在
    echo 请确保在docs目录下运行此脚本
    pause
    exit /b 1
)

REM 启动本地服务器
echo 🚀 启动本地HTTP服务器...
echo 服务器地址：http://localhost:8000
echo.
echo 按 Ctrl+C 停止服务器
echo ==========================================
echo.

python -m http.server 8000

pause
