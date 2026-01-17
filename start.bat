@echo off
REM RAG System Startup Script for Windows
REM This script starts both backend and frontend servers

echo ========================================
echo RAG Document Assistant - Starting...
echo ========================================
echo.

REM Check if .env file exists
if not exist ".env" (
    echo ERROR: .env file not found!
    echo Please create a .env file in the rag-system directory with:
    echo GOOGLE_API_KEY=your_api_key_here
    echo.
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv\\Scripts\\activate.bat" (
    echo ERROR: Virtual environment not found!
    echo Please run: python -m venv venv
    echo Then: .\\venv\\Scripts\\activate
    echo And: pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

echo [1/2] Starting Backend Server...
echo.
start "RAG Backend" cmd /k "cd /d %~dp0backend && ..\\venv\\Scripts\\activate && python -m uvicorn api.main:app --reload --host 127.0.0.1 --port 8000"

REM Wait a bit for backend to start
timeout /t 3 /nobreak >nul

echo [2/2] Starting Frontend Server...
echo.
start "RAG Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo ========================================
echo Both servers are starting!
echo ========================================
echo.
echo Backend:  http://127.0.0.1:8000
echo Frontend: http://localhost:3000
echo API Docs: http://127.0.0.1:8000/docs
echo.
echo Press any key to exit this window...
echo (The servers will continue running in separate windows)
pause >nul
