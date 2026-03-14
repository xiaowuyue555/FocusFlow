#!/usr/bin/env python3
"""
Windows 专用启动器 - 无窗口残留版本
使用方法：双击 launcher.pyw 启动（注意是 .pyw 扩展名）

.pyw 文件在 Windows 上运行不会打开控制台窗口
"""

import subprocess
import sys
import os
import time

def main():
    # 获取项目根目录
    if getattr(sys, 'frozen', False):
        # 如果是打包后的 exe
        PROJECT_ROOT = os.path.dirname(sys.executable)
    else:
        PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
    
    os.chdir(PROJECT_ROOT)
    
    # 检查虚拟环境
    venv_python = os.path.join(PROJECT_ROOT, "venv", "Scripts", "python.exe")
    if os.path.exists(venv_python):
        python_exe = venv_python
    else:
        python_exe = sys.executable
    
    # 检查后台服务是否已在运行（防止重复启动）
    import psutil
    service_running = False
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
            # 检查是否是 service_daemon.py 进程，且不是当前进程
            if 'service_daemon.py' in cmdline and proc.info['pid'] != os.getpid():
                service_running = True
                print(f"ℹ️  后台服务已在运行 (PID: {proc.info['pid']})")
                break
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    if not service_running:
        print("🚀 启动后台服务...")
        # 启动后台服务（无窗口）
        subprocess.Popen(
            [python_exe, "service_daemon.py"],
            creationflags=subprocess.CREATE_NO_WINDOW,
            cwd=PROJECT_ROOT
        )
        # 等待服务启动
        time.sleep(1)
        print("✅ 后台服务已启动")
    else:
        print("✅ 后台服务已在运行")
    
    # 启动 GUI
    from gui.dashboard_v2 import DashboardV2
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import Qt
    
    # 启用高 DPI 支持
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    app = QApplication(sys.argv)
    app.setApplicationName("FocusFlow")
    
    # 创建主窗口
    window = DashboardV2()
    window.show()
    
    # 运行事件循环
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
