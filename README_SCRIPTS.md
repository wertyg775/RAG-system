# RAG System - Startup Scripts Guide

## Quick Start Scripts

This directory contains several startup scripts to make running the RAG system easier.

### 🚀 Main Startup Scripts

#### `start.bat` (Recommended for Windows)
**Double-click to run** both backend and frontend servers automatically.
- Opens two separate command windows (backend + frontend)
- Checks for .env file in rag-system directory and virtual environment
- Provides helpful error messages if setup is incomplete

**Usage**:
```bash
.\start.bat
```

#### `start.ps1` (PowerShell Alternative)
PowerShell version with colored output and better error handling.

**Usage**:
```powershell
.\start.ps1
```

> **Note**: If you get an execution policy error, run:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

---

### 📦 Individual Server Scripts

#### `start-backend.bat`
Start only the backend server (useful for development).

**Usage**:
```bash
.\start-backend.bat
```

Runs on: `http://127.0.0.1:8000`

#### `start-frontend.bat`
Start only the frontend server (useful for development).

**Usage**:
```bash
.\start-frontend.bat
```

Runs on: `http://localhost:3000`

---

## 📋 Prerequisites

Before running any startup script, ensure:

1. ✅ **Virtual Environment** is created and dependencies installed:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. ✅ **Node Modules** are installed:
   ```bash
   cd frontend
   npm install
   ```

3. ✅ **Environment File** exists at `.env` with:
   ```
   GOOGLE_API_KEY=your_google_api_key_here
   ```

---

## 🌐 Server URLs

After starting, the system will be available at:

- **Frontend**: http://localhost:3000
- **Backend API**: http://127.0.0.1:8000
- **API Documentation**: http://127.0.0.1:8000/docs (Swagger UI)

---

## 🛑 Stopping the Servers

To stop the servers:
1. Go to each terminal window
2. Press `Ctrl+C`
3. Or simply close the terminal windows

---

## 🐛 Troubleshooting

### Script Won't Run
- Ensure you're in the `rag-system` directory
- Check that `venv` folder exists
- Verify `.env` file is in the rag-system directory

### Backend Fails to Start
- Check if port 8000 is already in use
- Verify Google API key is valid in `.env`
- Check Python version: `python --version` (needs 3.9+)

### Frontend Fails to Start
- Check if port 3000 is already in use
- Run `npm install` in frontend directory
- Verify Node version: `node --version` (needs 18+)

### PowerShell Execution Policy Error
Run PowerShell as Administrator and execute:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## 🔄 Manual Startup (Alternative)

If scripts don't work, you can start manually:

**Terminal 1 - Backend**:
```bash
cd backend
..\venv\Scripts\activate
python -m uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
```

**Terminal 2 - Frontend**:
```bash
cd frontend
npm run dev
```
