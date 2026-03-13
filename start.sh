#!/bin/bash

# FocusFlow 启动脚本
# 用法：./start.sh

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 激活虚拟环境
source venv/bin/activate

# 检查后台服务是否已在运行
if pgrep -f "service_daemon.py" > /dev/null; then
    echo "✅ 后台服务已在运行"
else
    echo "🚀 启动后台服务..."
    # 使用 nohup 让服务在后台独立运行，不受终端关闭影响
    nohup python service_daemon.py > /dev/null 2>&1 &
    sleep 1
    
    # 检查是否启动成功
    if pgrep -f "service_daemon.py" > /dev/null; then
        echo "✅ 后台服务已启动"
    else
        echo "❌ 后台服务启动失败"
        exit 1
    fi
fi

# 启动 GUI 界面
echo "🖥️  启动 FocusFlow 界面..."
python gui/dashboard_v2.py
