import sys
print("Python path:", sys.path)

# 测试 PySide6 导入
try:
    import PySide6
    print("PySide6 version:", PySide6.__version__)
    
    # 测试 QtGui 导入
    try:
        from PySide6 import QtGui
        print("QtGui imported successfully")
    except ImportError as e:
        print("QtGui import error:", e)
        
    # 测试 QtWidgets 导入
    try:
        from PySide6 import QtWidgets
        print("QtWidgets imported successfully")
    except ImportError as e:
        print("QtWidgets import error:", e)
        
except ImportError as e:
    print("PySide6 import error:", e)
