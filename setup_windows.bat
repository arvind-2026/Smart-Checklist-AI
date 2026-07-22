@echo off
setlocal
cd /d "%~dp0"

where py >nul 2>nul
if errorlevel 1 (
    echo Python Launcher was not found. Install Python 3.11 before continuing.
    exit /b 1
)

echo Creating the Windows virtual environment...
py -3.11 -m venv .venv
if errorlevel 1 exit /b 1

echo Installing project dependencies...
.venv\Scripts\python.exe -m pip install --upgrade pip
if errorlevel 1 exit /b 1

.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 exit /b 1

echo Setup complete. Run run_windows.bat to start the application.
endlocal
