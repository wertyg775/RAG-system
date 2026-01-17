@echo off
REM Start only the Frontend Server

echo Starting RAG Frontend Server...
echo.

REM Navigate to frontend directory
cd /d "%~dp0frontend"

REM Start development server
npm run dev
