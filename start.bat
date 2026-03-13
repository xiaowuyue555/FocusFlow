@echo off
REM FocusFlow Windows 启动脚本
REM 用法：双击运行 start.bat

cd /d "%~dp0"

REM 激活虚拟环境
call venv\Scripts\activate.bat

REM 检查后台服务是否已在运行
tasklist /FI "IMAGENAME eq *service_daemon.py*" | find "service_daemon.py" >nul
if %errorlevel% equ 0 (
    echo ✅ 后台服务已在运行
) else (
    echo 🚀 启动后台服务...
    REM 使用 start /B 在后台启动服务
    start /B python service_daemon.py
    timeout /t 2 /nobreak >nul
    
    REM 检查是否启动成功
    tasklist /FI "IMAGENAME eq *service_daemon.py*" | find "service_daemon.py" >nul
    if %errorlevel% equ 0 (
        echo ✅ 后台服务已启动
    ) else (
        echo ❌ 后台服务启动失败
        pause
        exit /b 1
    )
)

REM 启动 GUI 界面
echo 🖥️  启动 FocusFlow 界面...
python gui/dashboard_v2.py
