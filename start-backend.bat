@echo off
REM Start only the Backend Server

echo Starting RAG Backend Server...
echo.

REM Navigate to backend directory
cd /d "%~dp0backend"

REM Activate virtual environment and start server
call ..\venv\Scripts\activate.bat
python -m uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
