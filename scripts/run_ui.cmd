@echo off
REM S.O.I.L.E.R. Web UI Launcher for Windows
REM This script ensures UTF-8 encoding works correctly regardless of terminal

setlocal

REM Change to project root directory
cd /d "%~dp0\.."

REM Set UTF-8 encoding environment variables
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8

REM Optional: Set console code page to UTF-8 (may not work in all terminals)
chcp 65001 >nul 2>&1

echo.
echo ================================================
echo  S.O.I.L.E.R. Web Dashboard
echo  Starting Streamlit server...
echo ================================================
echo.

REM Check if virtual environment exists
if not exist ".venv\Scripts\python.exe" (
    echo ERROR: Virtual environment not found at .venv\
    echo Please run: python -m venv .venv
    echo Then: .venv\Scripts\pip install -r requirements.txt
    exit /b 1
)

REM Start Streamlit with proper settings
.venv\Scripts\python.exe -m streamlit run streamlit_app.py --server.port 8501 --server.headless true

endlocal
