@echo off
REM Voice Automation Hub - Windows Start Script

echo ======================================
echo Voice Automation Hub - Starting
echo ======================================
echo.

REM Get the project root (2 levels up from this script)
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%\..\.."

REM Check if .env exists
if not exist ".env" (
    echo ERROR: .env file not found!
    echo Please run install.ps1 first and configure your API keys
    pause
    exit /b 1
)

echo Starting backend server...
start "Voice Automation Backend" cmd /k "cd backend && python -m uvicorn app.main:app --reload --port 8000"

timeout /t 3 /nobreak >nul

echo Starting frontend development server...
start "Voice Automation Frontend" cmd /k "cd frontend && npm run dev"

timeout /t 2 /nobreak >nul

echo.
echo ======================================
echo Services Started!
echo ======================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:5173
echo.
echo Press Ctrl+C in each window to stop the servers
echo.

REM Wait for user input
pause

