@echo off
REM S.O.I.L.E.R. - Run Script for Windows
REM Usage: scripts\run.cmd [mode]
REM Modes: cli (default), web, test

setlocal

cd /d "%~dp0\.."

if "%1"=="" goto cli
if "%1"=="cli" goto cli
if "%1"=="web" goto web
if "%1"=="test" goto test
if "%1"=="install" goto install

echo Unknown mode: %1
echo Usage: scripts\run.cmd [cli^|web^|test^|install]
exit /b 1

:install
echo Installing dependencies...
pip install -r requirements.txt
pip install pytest ruff
exit /b 0

:cli
echo Running S.O.I.L.E.R. CLI...
set PYTHONIOENCODING=utf-8
python main.py %2 %3 %4
exit /b %errorlevel%

:web
echo Starting S.O.I.L.E.R. Web Dashboard...
streamlit run streamlit_app.py
exit /b %errorlevel%

:test
echo Running tests...
pytest -v
exit /b %errorlevel%
