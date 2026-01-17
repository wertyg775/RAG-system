# RAG System Startup Script for Windows (PowerShell)
# This script starts both backend and frontend servers

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "RAG Document Assistant - Starting..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Get script directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path

# Check if .env file exists
if (-not (Test-Path "$scriptPath\.env")) {
    Write-Host "ERROR: .env file not found!" -ForegroundColor Red
    Write-Host "Please create a .env file in the rag-system directory with:" -ForegroundColor Yellow
    Write-Host "GOOGLE_API_KEY=your_api_key_here" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if virtual environment exists
if (-not (Test-Path "$scriptPath\venv\Scripts\Activate.ps1")) {
    Write-Host "ERROR: Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please run the following commands:" -ForegroundColor Yellow
    Write-Host "  python -m venv venv" -ForegroundColor Yellow
    Write-Host "  .\venv\Scripts\Activate.ps1" -ForegroundColor Yellow
    Write-Host "  pip install -r requirements.txt" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if node_modules exists
if (-not (Test-Path "$scriptPath\frontend\node_modules")) {
    Write-Host "WARNING: node_modules not found in frontend!" -ForegroundColor Yellow
    Write-Host "Please run 'npm install' in the frontend directory" -ForegroundColor Yellow
    Write-Host ""
}

# Start Backend Server
Write-Host "[1/2] Starting Backend Server..." -ForegroundColor Green
Write-Host ""
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$scriptPath\backend'; & '$scriptPath\venv\Scripts\Activate.ps1'; python -m uvicorn api.main:app --reload --host 127.0.0.1 --port 8000" -WindowStyle Normal

# Wait for backend to start
Write-Host "Waiting for backend to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

# Start Frontend Server
Write-Host "[2/2] Starting Frontend Server..." -ForegroundColor Green
Write-Host ""
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$scriptPath\frontend'; npm run dev" -WindowStyle Normal

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Both servers are starting!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Backend:  " -NoNewline
Write-Host "http://127.0.0.1:8000" -ForegroundColor Blue
Write-Host "Frontend: " -NoNewline
Write-Host "http://localhost:3000" -ForegroundColor Blue
Write-Host "API Docs: " -NoNewline
Write-Host "http://127.0.0.1:8000/docs" -ForegroundColor Blue
Write-Host ""
Write-Host "Press any key to exit this window..." -ForegroundColor Gray
Write-Host "(The servers will continue running in separate windows)" -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
