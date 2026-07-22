@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo The virtual environment is missing. Run setup_windows.bat first.
    exit /b 1
)

.venv\Scripts\python.exe -m streamlit run streamlit_app.py
endlocal
