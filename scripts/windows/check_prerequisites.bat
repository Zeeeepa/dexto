@echo off
setlocal enabledelayedexpansion

REM ============================================
REM Check Prerequisites for Dexto Installation
REM ============================================

set "ERROR_COUNT=0"

REM Check Node.js
node --version >nul 2>&1
if %errorLevel% equ 0 (
    for /f "tokens=*" %%i in ('node --version') do set NODE_VERSION=%%i
    echo [OK] Node.js !NODE_VERSION! found
) else (
    echo [ERROR] Node.js not found
    echo Please install Node.js 20 or later from https://nodejs.org/
    set /a ERROR_COUNT+=1
)

REM Check npm
npm --version >nul 2>&1
if %errorLevel% equ 0 (
    for /f "tokens=*" %%i in ('npm --version') do set NPM_VERSION=%%i
    echo [OK] npm !NPM_VERSION! found
) else (
    echo [ERROR] npm not found
    set /a ERROR_COUNT+=1
)

REM Check pnpm
pnpm --version >nul 2>&1
if %errorLevel% equ 0 (
    for /f "tokens=*" %%i in ('pnpm --version') do set PNPM_VERSION=%%i
    echo [OK] pnpm !PNPM_VERSION! found
) else (
    echo [WARNING] pnpm not found
    echo Installing pnpm globally...
    call npm install -g pnpm
    if !errorLevel! equ 0 (
        echo [OK] pnpm installed successfully
    ) else (
        echo [ERROR] Failed to install pnpm
        set /a ERROR_COUNT+=1
    )
)

REM Check Git (optional but recommended)
git --version >nul 2>&1
if %errorLevel% equ 0 (
    for /f "tokens=*" %%i in ('git --version') do set GIT_VERSION=%%i
    echo [OK] !GIT_VERSION! found
) else (
    echo [WARNING] Git not found (optional but recommended)
    echo Install from https://git-scm.com/
)

if !ERROR_COUNT! gtr 0 (
    echo.
    echo [FAILED] !ERROR_COUNT! required prerequisite(s) missing
    exit /b 1
)

exit /b 0
