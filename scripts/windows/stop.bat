@echo off
setlocal enabledelayedexpansion

REM ============================================
REM Stop Dexto Application
REM ============================================

echo.
echo Stopping Dexto processes...
echo.

REM Find and kill dexto processes
set "KILLED=0"

REM Kill node processes running dexto
for /f "tokens=2" %%i in ('tasklist /FI "IMAGENAME eq node.exe" /FO LIST ^| findstr "PID:"') do (
    set "PID=%%i"
    REM Check if this node process is running dexto
    wmic process where "ProcessId=!PID!" get CommandLine 2>nul | findstr /i "dexto" >nul
    if !errorLevel! equ 0 (
        echo Killing process !PID!...
        taskkill /F /PID !PID! >nul 2>&1
        if !errorLevel! equ 0 (
            set /a KILLED+=1
        )
    )
)

if !KILLED! equ 0 (
    echo [INFO] No Dexto processes found running
) else (
    echo [OK] Stopped !KILLED! Dexto process(es)
)

echo.
pause
