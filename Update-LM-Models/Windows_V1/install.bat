@echo off
echo Installing OpenCode Model Updater Windows V1...

:: Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in your PATH.
    echo Please install Python 3 from python.org
    pause
    exit /b 1
)

:: Create Shortcut
set "SCRIPT_PATH=%~dp0updater_gui.py"
set "SHORTCUT_PATH=%USERPROFILE%\Desktop\OpenCode Model Updater.lnk"
set "ICON_PATH=%SystemRoot%\System32\shell32.dll,1"

echo Creating shortcut on Desktop...

powershell -Command "$s=(New-Object -COM WScript.Shell).CreateShortcut('%SHORTCUT_PATH%');$s.TargetPath='pythonw.exe';$s.Arguments='\"%SCRIPT_PATH%\"';$s.IconLocation='%ICON_PATH%';$s.Save()"

echo.
echo Installation Complete!
echo You can now launch the updater from your Desktop.
pause
