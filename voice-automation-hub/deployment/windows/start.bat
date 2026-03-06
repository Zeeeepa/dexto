@echo off
echo.
echo 🎤 Voice Automation Hub - Starting Services
echo ============================================================
echo.

cd /d "%~dp0..\.."

echo 📋 Checking environment...
if not exist ".env" (
    echo ❌ .env file not found!
    echo Please run install.ps1 first and configure .env
    pause
    exit /b 1
)

echo ✅ Environment configured
echo.
echo 🚀 Starting backend server...
start "Voice Hub Backend" cmd /k "cd backend && python -m uvicorn app.main:app --reload --port 8000"

timeout /t 3 /nobreak >nul

echo.
echo 🎨 Starting frontend server...
start "Voice Hub Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ============================================================
echo ✨ Services started!
echo.
echo   Backend:  http://localhost:8000
echo   Frontend: http://localhost:5173
echo   API Docs: http://localhost:8000/docs
echo.
echo Press any key to stop all services...
pause >nul

echo.
echo 🛑 Stopping services...
taskkill /FI "WINDOWTITLE eq Voice Hub Backend*" /T /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq Voice Hub Frontend*" /T /F >nul 2>&1

echo ✅ Services stopped
echo.

