@echo off
setlocal enabledelayedexpansion

REM ============================================
REM Start Dexto Application
REM ============================================

echo.
echo Starting Dexto...
echo.

REM Check if dexto is installed
call dexto --version >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Dexto not found. Please run install.bat first.
    pause
    exit /b 1
)

REM Parse command line arguments
set "MODE=web"
set "WEB_PORT=3000"
set "API_PORT=3001"
set "EXTRA_ARGS="

:parse_args
if "%~1"=="" goto end_parse
if /i "%~1"=="--mode" (
    set "MODE=%~2"
    shift
    shift
    goto parse_args
)
if /i "%~1"=="--web-port" (
    set "WEB_PORT=%~2"
    shift
    shift
    goto parse_args
)
if /i "%~1"=="--api-port" (
    set "API_PORT=%~2"
    shift
    shift
    goto parse_args
)
set "EXTRA_ARGS=!EXTRA_ARGS! %~1"
shift
goto parse_args
:end_parse

REM Display startup info
echo Mode: !MODE!
if /i "!MODE!"=="web" (
    echo Web UI: http://localhost:!WEB_PORT!
    echo API Server: http://localhost:!API_PORT!
)
if /i "!MODE!"=="server" (
    echo API Server: http://localhost:!API_PORT!
)
echo.

REM Check if port is already in use (web mode only)
if /i "!MODE!"=="web" (
    netstat -ano | findstr ":!WEB_PORT!" >nul 2>&1
    if !errorLevel! equ 0 (
        echo [WARNING] Port !WEB_PORT! is already in use
        set /p CONTINUE="Continue anyway? (y/N): "
        if /i not "!CONTINUE!"=="y" (
            echo Cancelled.
            pause
            exit /b 1
        )
    )
)

REM Start Dexto
echo Starting Dexto in !MODE! mode...
echo Press Ctrl+C to stop
echo.

if /i "!MODE!"=="web" (
    call dexto --mode web --web-port !WEB_PORT! --api-port !API_PORT! !EXTRA_ARGS!
) else if /i "!MODE!"=="cli" (
    call dexto --mode cli !EXTRA_ARGS!
) else if /i "!MODE!"=="server" (
    call dexto --mode server --api-port !API_PORT! !EXTRA_ARGS!
) else (
    call dexto --mode !MODE! !EXTRA_ARGS!
)

echo.
echo Dexto stopped.
pause
