#!/usr/bin/env python3
"""
平台检测工具模块
提供跨平台的系统信息检测和工具函数
"""

import platform
import sys
import os


def get_platform():
    """
    获取当前平台名称
    
    Returns:
        str: 'macos', 'windows', 'linux', 或 'unknown'
    """
    system = platform.system()
    if system == "Darwin":
        return "macos"
    elif system == "Windows":
        return "windows"
    elif system == "Linux":
        return "linux"
    else:
        return "unknown"


def is_macos():
    """检查是否在 macOS 上运行"""
    return platform.system() == "Darwin"


def is_windows():
    """检查是否在 Windows 上运行"""
    return platform.system() == "Windows"


def is_linux():
    """检查是否在 Linux 上运行"""
    return platform.system() == "Linux"


def get_python_version():
    """
    获取 Python 版本信息
    
    Returns:
        tuple: (major, minor, micro)
    """
    return sys.version_info[:3]


def check_python_version(min_version=(3, 8)):
    """
    检查 Python 版本是否满足要求
    
    Args:
        min_version: 最低版本要求，默认 (3, 8)
    
    Returns:
        bool: 是否满足版本要求
    """
    current = get_python_version()
    return current >= min_version


def get_requirements_file():
    """
    获取当前平台对应的 requirements 文件
    
    Returns:
        str: requirements 文件名
    """
    if is_macos():
        return "requirements-mac.txt"
    elif is_windows():
        return "requirements-windows.txt"
    else:
        return "requirements.txt"


def get_platform_info():
    """
    获取详细的平台信息
    
    Returns:
        dict: 包含平台信息的字典
    """
    return {
        'platform': get_platform(),
        'system': platform.system(),
        'release': platform.release(),
        'version': platform.version(),
        'machine': platform.machine(),
        'processor': platform.processor(),
        'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        'architecture': '64bit' if sys.maxsize > 2**32 else '32bit'
    }


def print_platform_info():
    """打印平台信息（用于调试）"""
    info = get_platform_info()
    print("\n" + "="*50)
    print("🖥️  系统信息")
    print("="*50)
    print(f"平台：{info['platform']}")
    print(f"系统：{info['system']} {info['release']}")
    print(f"架构：{info['architecture']}")
    print(f"Python: {info['python_version']}")
    print(f"机器：{info['machine']}")
    print(f"处理器：{info['processor']}")
    print("="*50 + "\n")


# 模块级别的常量
CURRENT_PLATFORM = get_platform()
IS_MACOS = is_macos()
IS_WINDOWS = is_windows()
IS_LINUX = is_linux()


if __name__ == "__main__":
    print_platform_info()
