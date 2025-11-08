@echo off
setlocal enabledelayedexpansion

REM ============================================
REM Dexto Windows Advanced Installation Script
REM ============================================
REM Features:
REM - Retry logic with exponential backoff
REM - Automatic rollback on failure
REM - Detailed error logging
REM - Health check validation
REM - API key validation
REM ============================================

REM Initialize logging
set "LOG_DIR=%USERPROFILE%\.dexto\logs"
set "LOG_FILE=%LOG_DIR%\installation_%DATE:~-4%%DATE:~4,2%%DATE:~7,2%_%TIME:~0,2%%TIME:~3,2%%TIME:~6,2%.log"
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

echo.
echo ========================================
echo   Dexto Advanced Installation for Windows
echo ========================================
echo.
echo Log file: %LOG_FILE%
echo.

REM Log function
:log
echo [%DATE% %TIME%] %~1 >> "%LOG_FILE%"
echo %~1
goto :eof

call :log "[INFO] Starting advanced installation process"

REM Check for administrator privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    call :log "[WARNING] Running without administrator privileges"
    echo Some operations may fail. Consider running as Administrator.
    echo.
    timeout /t 3 >nul
)

REM ============================================
REM Step 1: Check Prerequisites
REM ============================================
call :log "[1/8] Checking prerequisites..."
echo [1/8] Checking prerequisites...

call "%~dp0check_prerequisites.bat" >> "%LOG_FILE%" 2>&1
if %errorLevel% neq 0 (
    call :log "[ERROR] Prerequisites check failed!"
    call :log "[RECOVERY] Please install missing requirements and try again"
    pause
    exit /b 1
)
call :log "[OK] Prerequisites verified"
echo [OK] Prerequisites verified
echo.

REM ============================================
REM Step 2: Backup Existing Installation  
REM ============================================
call :log "[2/8] Checking for existing installation..."
echo [2/8] Checking for existing installation...

cd /d "%~dp0..\.."
set "BACKUP_DIR=%~dp0..\..\node_modules.backup"

if exist "%~dp0..\..\node_modules" (
    call :log "[INFO] Existing installation found"
    echo [INFO] Existing installation detected
    
    set /p REINSTALL="Do you want to reinstall? (y/N): "
    if /i not "!REINSTALL!"=="y" (
        call :log "[INFO] Installation cancelled by user"
        echo Installation cancelled.
        pause
        exit /b 0
    )
    
    call :log "[INFO] Creating backup of existing installation..."
    echo [INFO] Creating backup...
    
    if exist "%BACKUP_DIR%" (
        call :log "[INFO] Removing old backup"
        rmdir /s /q "%BACKUP_DIR%"
    )
    
    move "%~dp0..\..\node_modules" "%BACKUP_DIR%" >nul 2>&1
    if !errorLevel! equ 0 (
        call :log "[OK] Backup created successfully"
        echo [OK] Backup created
    ) else (
        call :log "[WARNING] Backup failed, continuing without backup"
        echo [WARNING] Could not create backup
    )
) else (
    call :log "[INFO] No existing installation found"
    echo [INFO] Fresh installation
)
echo.

REM ============================================
REM Step 3: Install Dependencies with Retry
REM ============================================
call :log "[3/8] Installing dependencies..."
echo [3/8] Installing dependencies (with retry)...

set "RETRY_COUNT=0"
set "MAX_RETRIES=3"
set "RETRY_DELAY=5"

:install_dependencies
set /a "RETRY_COUNT+=1"
call :log "[ATTEMPT %RETRY_COUNT%/%MAX_RETRIES%] Running pnpm install..."
echo [ATTEMPT %RETRY_COUNT%/%MAX_RETRIES%] Installing...

call pnpm install >> "%LOG_FILE%" 2>&1
if %errorLevel% equ 0 (
    call :log "[OK] Dependencies installed successfully"
    echo [OK] Dependencies installed
    goto install_success
)

call :log "[ERROR] Attempt %RETRY_COUNT% failed with error level %errorLevel%"
echo [WARNING] Attempt %RETRY_COUNT% failed

if %RETRY_COUNT% lss %MAX_RETRIES% (
    call :log "[INFO] Retrying in %RETRY_DELAY% seconds..."
    echo [INFO] Retrying in %RETRY_DELAY% seconds...
    timeout /t %RETRY_DELAY% /nobreak >nul
    set /a "RETRY_DELAY*=2"
    goto install_dependencies
)

REM Installation failed after retries - rollback
call :log "[ERROR] Installation failed after %MAX_RETRIES% attempts"
echo [ERROR] Installation failed after %MAX_RETRIES% attempts
goto rollback

:install_success
echo.

REM ============================================
REM Step 4: Build All Packages with Retry
REM ============================================
call :log "[4/8] Building all packages..."
echo [4/8] Building all packages (this may take 1-2 minutes)...

set "RETRY_COUNT=0"
set "RETRY_DELAY=5"

:build_packages
set /a "RETRY_COUNT+=1"
call :log "[ATTEMPT %RETRY_COUNT%/%MAX_RETRIES%] Running pnpm run build:all..."
echo [ATTEMPT %RETRY_COUNT%/%MAX_RETRIES%] Building...

call pnpm run build:all >> "%LOG_FILE%" 2>&1
if %errorLevel% equ 0 (
    call :log "[OK] Build completed successfully"
    echo [OK] Build completed
    goto build_success
)

call :log "[ERROR] Build attempt %RETRY_COUNT% failed with error level %errorLevel%"
echo [WARNING] Build attempt %RETRY_COUNT% failed

if %RETRY_COUNT% lss %MAX_RETRIES% (
    call :log "[INFO] Retrying build in %RETRY_DELAY% seconds..."
    echo [INFO] Retrying in %RETRY_DELAY% seconds...
    timeout /t %RETRY_DELAY% /nobreak >nul
    set /a "RETRY_DELAY*=2"
    goto build_packages
)

REM Build failed - rollback
call :log "[ERROR] Build failed after %MAX_RETRIES% attempts"
echo [ERROR] Build failed after %MAX_RETRIES% attempts
goto rollback

:build_success
echo.

REM ============================================
REM Step 5: Install CLI Globally
REM ============================================
call :log "[5/8] Installing CLI globally..."
echo [5/8] Installing CLI globally...

call pnpm run install-cli >> "%LOG_FILE%" 2>&1
if %errorLevel% neq 0 (
    call :log "[ERROR] Failed to install CLI globally"
    echo [ERROR] Failed to install CLI globally
    goto rollback
)
call :log "[OK] CLI installed globally"
echo [OK] CLI installed globally
echo.

REM ============================================
REM Step 6: Verify Installation
REM ============================================
call :log "[6/8] Verifying installation..."
echo [6/8] Verifying installation...

call dexto --version >nul 2>&1
if %errorLevel% neq 0 (
    call :log "[WARNING] dexto command not found in PATH"
    echo [WARNING] dexto command not found in PATH
    echo You may need to restart your terminal or add npm global path to PATH
    echo.
    echo To add to PATH manually:
    for /f "tokens=*" %%i in ('npm config get prefix') do set NPM_PREFIX=%%i
    echo   set PATH=%%PATH%%;!NPM_PREFIX!
    echo.
    call :log "[INFO] PATH issue detected - user may need to restart terminal"
) else (
    for /f "tokens=*" %%i in ('dexto --version') do set DEXTO_VERSION=%%i
    call :log "[OK] Dexto !DEXTO_VERSION! installed successfully"
    echo [OK] Dexto !DEXTO_VERSION! installed successfully
)
echo.

REM ============================================
REM Step 7: Validate API Keys (Optional)
REM ============================================
call :log "[7/8] Validating API keys..."
echo [7/8] API key validation...

set "API_KEY_VALID=0"

REM Check for at least one valid API key
if defined OPENAI_API_KEY (
    if not "!OPENAI_API_KEY!"=="" (
        call :log "[OK] OpenAI API key found"
        echo [OK] OpenAI API key configured
        set "API_KEY_VALID=1"
    )
)

if defined ANTHROPIC_API_KEY (
    if not "!ANTHROPIC_API_KEY!"=="" (
        call :log "[OK] Anthropic API key found"
        echo [OK] Anthropic API key configured
        set "API_KEY_VALID=1"
    )
)

if defined GOOGLE_GENERATIVE_AI_API_KEY (
    if not "!GOOGLE_GENERATIVE_AI_API_KEY!"=="" (
        call :log "[OK] Google API key found"
        echo [OK] Google API key configured
        set "API_KEY_VALID=1"
    )
)

if !API_KEY_VALID! equ 0 (
    call :log "[WARNING] No API keys configured"
    echo [WARNING] No API keys found
    echo You'll need to configure API keys to use Dexto
    echo Run: scripts\windows\configure.bat
    echo.
)
echo.

REM ============================================
REM Step 8: Initial Configuration
REM ============================================
call :log "[8/8] Initial configuration..."
echo [8/8] Initial configuration...

set /p RUN_SETUP="Would you like to run setup now? (Y/n): "
if /i not "!RUN_SETUP!"=="n" (
    call :log "[INFO] Running setup wizard"
    echo.
    echo Running setup wizard...
    call dexto setup >> "%LOG_FILE%" 2>&1
) else (
    call :log "[INFO] Setup skipped by user"
    echo.
    echo Skipping setup. You can run 'dexto setup' later.
)

REM ============================================
REM Installation Successful - Cleanup Backup
REM ============================================
call :log "[SUCCESS] Installation completed successfully"
echo.
echo ========================================
echo   Installation Complete!
echo ========================================
echo.

if exist "%BACKUP_DIR%" (
    echo Removing backup...
    call :log "[INFO] Removing backup directory"
    rmdir /s /q "%BACKUP_DIR%"
)

call :log "[INFO] Next steps: Open new terminal and run 'dexto'"
echo Next steps:
echo   1. Open a new terminal window
echo   2. Run: dexto
echo   3. Access Web UI at http://localhost:3000
echo.
echo Installation log: %LOG_FILE%
echo.
pause
exit /b 0

REM ============================================
REM Rollback on Failure
REM ============================================
:rollback
call :log "[ROLLBACK] Installation failed. Rolling back changes..."
echo.
echo ========================================
echo   Rollback in Progress
echo ========================================
echo.

REM Remove failed installation
if exist "%~dp0..\..\node_modules" (
    call :log "[ROLLBACK] Removing failed installation"
    echo Removing failed installation...
    rmdir /s /q "%~dp0..\..\node_modules"
)

REM Restore backup if exists
if exist "%BACKUP_DIR%" (
    call :log "[ROLLBACK] Restoring backup"
    echo Restoring previous installation...
    move "%BACKUP_DIR%" "%~dp0..\..\node_modules" >nul 2>&1
    if !errorLevel! equ 0 (
        call :log "[OK] Rollback successful - previous installation restored"
        echo [OK] Previous installation restored
    ) else (
        call :log "[ERROR] Rollback failed - could not restore backup"
        echo [ERROR] Could not restore backup
    )
) else (
    call :log "[INFO] No backup to restore"
    echo No previous installation to restore
)

call :log "[FAILED] Installation failed. Check log file: %LOG_FILE%"
echo.
echo Installation failed. Check log file for details:
echo %LOG_FILE%
echo.
echo Common issues and solutions:
echo   - Network failure: Check internet connection and retry
echo   - Permission issues: Run as Administrator
echo   - Disk space: Ensure 2+ GB free space
echo   - Antivirus: Temporarily disable and retry
echo.
pause
exit /b 1

