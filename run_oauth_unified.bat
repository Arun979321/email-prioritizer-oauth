@echo off
title Gmail OAuth Email Prioritizer - Unified Server
cd /d "C:\Projects\Email Management Oath"

echo ============================================
echo 🚀 Launching Gmail OAuth Email Prioritizer
echo ============================================
echo.

echo [1/2] Activating virtual environment...
call backend\venv\Scripts\activate
if errorlevel 1 (
    echo ❌ Failed to activate virtual environment!
    pause
    exit /b
)
echo ✅ Virtual environment activated.
echo.

echo [2/2] Starting FastAPI unified server on port 8000...
cd backend
start cmd /k "uvicorn app:app --reload --host 127.0.0.1 --port 8000"

timeout /t 5 /nobreak >nul
start "" "http://127.0.0.1:8000"

pause
