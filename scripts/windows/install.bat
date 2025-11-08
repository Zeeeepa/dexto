@echo off
setlocal enabledelayedexpansion

REM ============================================
REM Dexto Windows Installation Script
REM ============================================
REM This script automates the complete installation
REM of Dexto on Windows systems.
REM ============================================

echo.
echo ========================================
echo   Dexto Installation for Windows
echo ========================================
echo.

REM Check for administrator privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [WARNING] Running without administrator privileges
    echo Some operations may fail. Consider running as Administrator.
    echo.
    timeout /t 3 >nul
)

REM Step 1: Check Prerequisites
echo [1/6] Checking prerequisites...
call "%~dp0check_prerequisites.bat"
if %errorLevel% neq 0 (
    echo.
    echo [ERROR] Prerequisites check failed!
    echo Please install missing requirements and try again.
    pause
    exit /b 1
)
echo [OK] Prerequisites verified
echo.

REM Step 2: Check if already installed
if exist "%~dp0..\..\node_modules" (
    echo [WARNING] Dexto appears to be already installed
    set /p REINSTALL="Do you want to reinstall? (y/N): "
    if /i not "!REINSTALL!"=="y" (
        echo Installation cancelled.
        pause
        exit /b 0
    )
)

REM Step 3: Install dependencies
echo [2/6] Installing dependencies...
cd /d "%~dp0..\.."
call pnpm install
if %errorLevel% neq 0 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)
echo [OK] Dependencies installed
echo.

REM Step 4: Build all packages
echo [3/6] Building all packages (this may take 1-2 minutes)...
call pnpm run build:all
if %errorLevel% neq 0 (
    echo [ERROR] Build failed
    pause
    exit /b 1
)
echo [OK] Build completed
echo.

REM Step 5: Install CLI globally
echo [4/6] Installing CLI globally...
call pnpm run install-cli
if %errorLevel% neq 0 (
    echo [ERROR] Failed to install CLI globally
    pause
    exit /b 1
)
echo [OK] CLI installed globally
echo.

REM Step 6: Verify installation
echo [5/6] Verifying installation...
call dexto --version >nul 2>&1
if %errorLevel% neq 0 (
    echo [WARNING] dexto command not found in PATH
    echo You may need to restart your terminal or add npm global path to PATH
    echo.
    echo To add to PATH manually:
    for /f "tokens=*" %%i in ('npm config get prefix') do set NPM_PREFIX=%%i
    echo   set PATH=%%PATH%%;!NPM_PREFIX!
    echo.
) else (
    for /f "tokens=*" %%i in ('dexto --version') do set DEXTO_VERSION=%%i
    echo [OK] Dexto !DEXTO_VERSION! installed successfully
)
echo.

REM Step 7: Setup configuration (optional)
echo [6/6] Initial configuration...
set /p RUN_SETUP="Would you like to run setup now? (Y/n): "
if /i not "!RUN_SETUP!"=="n" (
    echo.
    echo Running setup wizard...
    call dexto setup
) else (
    echo.
    echo Skipping setup. You can run 'dexto setup' later.
)

echo.
echo ========================================
echo   Installation Complete!
echo ========================================
echo.
echo Next steps:
echo   1. Open a new terminal window
echo   2. Run: dexto
echo   3. Access Web UI at http://localhost:3000
echo.
echo For more information:
echo   - Quick Start: docs\deployment\QUICK_START.md
echo   - Windows Guide: docs\deployment\WINDOWS_DEPLOYMENT.md
echo   - CLI Reference: docs\deployment\CLI_REFERENCE.md
echo.
pause
