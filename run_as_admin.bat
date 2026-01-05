@echo off
chcp 65001 >nul
echo 永恒之塔2 守护星辅助脚本
echo.

REM 检查是否以管理员身份运行
net session >nul 2>&1
if %errorLevel% == 0 (
    echo 以管理员身份运行...
    goto :start_script
) else (
    echo 未以管理员身份运行，正在请求管理员权限...
    goto :elevate
)

:elevate
REM 重新运行脚本并请求管理员权限
powershell -Command "Start-Process cmd -ArgumentList '/k', 'cd /d', '%~dp0', '&&', 'python', 'main_new.py' -Verb RunAs"
exit /b

:start_script
REM 运行Python脚本
python main_new.py
pause