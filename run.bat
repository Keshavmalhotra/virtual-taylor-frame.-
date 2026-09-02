@echo off
setlocal
cd /d "%~dp0"

where pythonw >nul 2>nul
if %ERRORLEVEL% equ 0 (
    start "" pythonw main.pyw %*
    exit /b 0
)

where pyw >nul 2>nul
if %ERRORLEVEL% equ 0 (
    start "" pyw main.pyw %*
    exit /b 0
)

where python >nul 2>nul
if %ERRORLEVEL% equ 0 (
    start "" python main.py %*
    exit /b 0
)

where py >nul 2>nul
if %ERRORLEVEL% equ 0 (
    start "" py main.py %*
    exit /b 0
)

echo [ERROR] Python launcher (pythonw / pyw / python) was not found in your PATH.
echo Please install Python 3.10+ and check 'Add python.exe to PATH'.
pause
exit /b 1
