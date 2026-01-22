# S.O.I.L.E.R. Web UI Launcher for Windows PowerShell
# This script ensures UTF-8 encoding works correctly regardless of terminal

# Change to project root directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location (Join-Path $scriptDir "..")

# Set UTF-8 encoding environment variables
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"

# Set PowerShell output encoding to UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host ""
Write-Host "================================================"
Write-Host " S.O.I.L.E.R. Web Dashboard"
Write-Host " Starting Streamlit server..."
Write-Host "================================================"
Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path ".venv\Scripts\python.exe")) {
    Write-Host "ERROR: Virtual environment not found at .venv\" -ForegroundColor Red
    Write-Host "Please run: python -m venv .venv"
    Write-Host "Then: .venv\Scripts\pip install -r requirements.txt"
    exit 1
}

# Start Streamlit with proper settings
& ".venv\Scripts\python.exe" -m streamlit run streamlit_app.py --server.port 8501 --server.headless true
