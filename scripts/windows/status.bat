@echo off
setlocal enabledelayedexpansion

echo.
echo ========================================
echo   Dexto Status Check
echo ========================================
echo.

call dexto --version >nul 2>&1
if %errorLevel% equ 0 (
    for /f "tokens=*" %%i in ('dexto --version') do set DEXTO_VERSION=%%i
    echo [OK] Dexto !DEXTO_VERSION! installed
) else (
    echo [ERROR] Dexto not installed
    pause
    exit /b 1
)

echo.
echo Checking for running processes...
set "RUNNING=0"
for /f "tokens=2" %%i in ('tasklist /FI "IMAGENAME eq node.exe" /FO LIST 2^>nul ^| findstr "PID:"') do (
    set "PID=%%i"
    wmic process where "ProcessId=!PID!" get CommandLine 2>nul | findstr /i "dexto" >nul
    if !errorLevel! equ 0 (
        echo [RUNNING] PID !PID!
        set /a RUNNING+=1
    )
)
if !RUNNING! equ 0 (
    echo [STOPPED] No Dexto processes running
) else (
    echo [ACTIVE] !RUNNING! Dexto process(es) running
)

echo.
echo Checking ports...
netstat -ano | findstr ":3000 " >nul 2>&1
if !errorLevel! equ 0 (
    echo [OK] Port 3000 in use
) else (
    echo [INFO] Port 3000 not in use
)

echo.
pause
