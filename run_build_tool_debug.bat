@echo off
echo ========================================
echo FocusFlow Build Tool - Debug Mode
echo ========================================
echo.

echo Starting build tool...
echo Debug log will be saved to: tools\logs\build_tool_debug.log
echo.

python tools\build_tool.py

echo.
echo ========================================
echo Program exited
echo ========================================
echo.

echo Viewing debug log:
type tools\logs\build_tool_debug.log

echo.
echo Press any key to exit...
pause >nul
