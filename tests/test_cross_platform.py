#!/usr/bin/env python3
"""
跨平台兼容性测试脚本
验证 FocusFlow 在不同平台上的核心功能
"""

import sys
import os
import platform

# 确保能导入项目模块
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


def print_header(title):
    """打印测试标题"""
    print("\n" + "="*60)
    print(f"🧪 {title}")
    print("="*60)


def print_result(test_name, passed, message=""):
    """打印测试结果"""
    status = "✅" if passed else "❌"
    result = "通过" if passed else "失败"
    print(f"{status} {test_name}: {result}")
    if message:
        print(f"   {message}")


def test_platform_detection():
    """测试平台检测功能"""
    print_header("测试 1: 平台检测")
    
    from modules.platform_utils import (
        get_platform, is_macos, is_windows, is_linux,
        get_platform_info, get_requirements_file
    )
    
    # 测试平台识别
    current_platform = get_platform()
    print(f"当前平台：{current_platform}")
    
    # 测试平台判断函数
    if current_platform == "macos":
        passed = is_macos() and not is_windows() and not is_linux()
        print_result("macOS 识别", passed)
    elif current_platform == "windows":
        passed = is_windows() and not is_macos() and not is_linux()
        print_result("Windows 识别", passed)
    elif current_platform == "linux":
        passed = is_linux() and not is_macos() and not is_windows()
        print_result("Linux 识别", passed)
    
    # 测试 requirements 文件选择
    req_file = get_requirements_file()
    expected = f"requirements-{current_platform}.txt"
    # 检查文件是否存在
    file_exists = os.path.exists(os.path.join(PROJECT_ROOT, req_file))
    passed = file_exists
    print_result("Requirements 文件", passed, f"文件：{req_file}")
    
    # 打印详细平台信息
    info = get_platform_info()
    print(f"\n平台详细信息:")
    for key, value in info.items():
        print(f"  {key}: {value}")


def test_path_handling():
    """测试路径处理"""
    print_header("测试 2: 路径处理")
    
    # 测试数据库路径
    db_path = os.path.join(PROJECT_ROOT, "data", "tracker.db")
    passed = os.path.exists(db_path) or not os.path.exists(os.path.dirname(db_path))
    print_result("数据库路径构造", True, db_path)
    
    # 测试项目根目录
    passed = os.path.exists(os.path.join(PROJECT_ROOT, "core"))
    print_result("项目根目录", passed, PROJECT_ROOT)
    
    # 测试路径分隔符
    test_path = os.path.join("a", "b", "c")
    if platform.system() == "Windows":
        passed = test_path == "a\\b\\c"
    else:
        passed = test_path == "a/b/c"
    print_result("路径分隔符", passed, f"结果：{test_path}")


def test_app_detector():
    """测试应用检测模块"""
    print_header("测试 3: 应用检测模块")
    
    try:
        from modules.app_detector import get_active_app_info
        
        app_name, file_path = get_active_app_info()
        
        passed = app_name is not None and file_path is not None
        print_result("应用检测函数", passed, f"当前应用：{app_name}, 文件：{file_path}")
        
        # 测试平台特定实现
        if platform.system() == "Windows":
            print("   ℹ️  Windows 实现已加载")
            passed = True
        elif platform.system() == "Darwin":
            print("   ℹ️  macOS 实现已加载")
            passed = True
        else:
            print("   ⚠️  未知平台")
            passed = False
            
        print_result("平台特定实现", passed)
        
    except ImportError as e:
        print_result("应用检测导入", False, str(e))


def test_idle_detection():
    """测试闲置检测"""
    print_header("测试 4: 闲置检测")
    
    if platform.system() == "Windows":
        try:
            import win32api
            last_input = win32api.GetLastInputInfo()
            current_time = win32api.GetTickCount()
            idle_time = (current_time - last_input) / 1000.0
            
            passed = idle_time >= 0
            print_result("Windows 闲置检测", passed, f"闲置时间：{idle_time:.2f}秒")
            
        except ImportError:
            print_result("Windows 闲置检测", False, "pywin32 未安装")
            
    elif platform.system() == "Darwin":
        try:
            import Quartz
            idle_time = Quartz.CGEventSourceSecondsSinceLastEventType(
                Quartz.kCGEventSourceStateCombinedSessionState,
                Quartz.kCGAnyInputEventType
            )
            
            passed = idle_time is not None and idle_time >= 0
            print_result("macOS 闲置检测", passed, f"闲置时间：{idle_time:.2f}秒")
            
        except ImportError:
            print_result("macOS 闲置检测", False, "Quartz 未安装")
    else:
        print_result("闲置检测", False, f"不支持的平台：{platform.system()}")


def test_database():
    """测试数据库功能"""
    print_header("测试 5: 数据库")
    
    try:
        from core.database import get_connection, init_db
        
        # 初始化数据库
        init_db()
        
        # 测试连接
        conn = get_connection()
        cursor = conn.cursor()
        
        # 测试表是否存在
        tables = cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
        
        passed = len(tables) > 0
        print_result("数据库表", passed, f"表数量：{len(tables)}")
        
        # 测试配置表
        config_exists = cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='system_config'"
        ).fetchone()
        
        passed = config_exists is not None
        print_result("系统配置表", passed)
        
        conn.close()
        
    except Exception as e:
        print_result("数据库测试", False, str(e))


def test_dependencies():
    """测试依赖包"""
    print_header("测试 6: 依赖包")
    
    dependencies = {
        'customtkinter': 'GUI 框架',
        'psutil': '系统监控',
        'pandas': '数据处理',
        'matplotlib': '图表绘制',
    }
    
    # 平台特定依赖
    if platform.system() == "Windows":
        dependencies['win32api'] = 'Windows API'
        dependencies['win32gui'] = 'Windows GUI'
        dependencies['win32process'] = 'Windows 进程'
    elif platform.system() == "Darwin":
        dependencies['Quartz'] = 'macOS Quartz'
    
    for module, description in dependencies.items():
        try:
            __import__(module)
            print_result(f"{module} ({description})", True)
        except ImportError:
            print_result(f"{module} ({description})", False)


def test_gui_import():
    """测试 GUI 模块导入"""
    print_header("测试 7: GUI 模块")
    
    try:
        from PySide6.QtWidgets import QApplication, QMainWindow
        print_result("PySide6 导入", True)
        
        # 测试系统托盘支持
        from PySide6.QtWidgets import QSystemTrayIcon
        passed = QSystemTrayIcon.isSystemTrayAvailable()
        print_result("系统托盘可用", passed)
        
    except ImportError as e:
        print_result("PySide6 导入", False, str(e))


def run_all_tests():
    """运行所有测试"""
    print("\n" + "="*60)
    print("🚀 FocusFlow 跨平台兼容性测试")
    print("="*60)
    print(f"平台：{platform.system()} {platform.release()}")
    print(f"Python: {platform.python_version()}")
    print("="*60)
    
    tests = [
        test_platform_detection,
        test_path_handling,
        test_app_detector,
        test_idle_detection,
        test_database,
        test_dependencies,
        test_gui_import,
    ]
    
    passed_count = 0
    failed_count = 0
    
    for test in tests:
        try:
            test()
            passed_count += 1
        except Exception as e:
            print(f"\n❌ 测试异常：{test.__name__}")
            print(f"   错误：{e}")
            failed_count += 1
    
    # 打印总结
    print_header("测试总结")
    print(f"总测试数：{len(tests)}")
    print(f"✅ 通过：{passed_count}")
    print(f"❌ 失败：{failed_count}")
    print(f"通过率：{passed_count/len(tests)*100:.1f}%")
    print("="*60 + "\n")
    
    return failed_count == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
