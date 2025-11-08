@echo off
setlocal enabledelayedexpansion

REM ============================================
REM Configure Dexto Settings
REM ============================================

echo.
echo ========================================
echo   Dexto Configuration
echo ========================================
echo.

REM Check if dexto is installed
call dexto --version >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Dexto not found. Please run install.bat first.
    pause
    exit /b 1
)

REM Menu
echo What would you like to configure?
echo.
echo   1. Run full setup wizard (recommended)
echo   2. Set API keys manually
echo   3. Configure default agent
echo   4. View current configuration
echo   5. Exit
echo.
set /p CHOICE="Enter choice (1-5): "

if "!CHOICE!"=="1" goto setup_wizard
if "!CHOICE!"=="2" goto set_api_keys
if "!CHOICE!"=="3" goto set_agent
if "!CHOICE!"=="4" goto view_config
if "!CHOICE!"=="5" goto end
echo Invalid choice
pause
exit /b 1

:setup_wizard
echo.
echo Running setup wizard...
call dexto setup
goto end

:set_api_keys
echo.
echo ========================================
echo   API Key Configuration
echo ========================================
echo.
echo Enter your API keys (leave blank to skip):
echo.

set /p OPENAI_KEY="OpenAI API Key: "
if not "!OPENAI_KEY!"=="" (
    setx OPENAI_API_KEY "!OPENAI_KEY!" >nul
    echo [OK] OpenAI API key saved
)

set /p ANTHROPIC_KEY="Anthropic API Key: "
if not "!ANTHROPIC_KEY!"=="" (
    setx ANTHROPIC_API_KEY "!ANTHROPIC_KEY!" >nul
    echo [OK] Anthropic API key saved
)

set /p GOOGLE_KEY="Google Generative AI API Key: "
if not "!GOOGLE_KEY!"=="" (
    setx GOOGLE_GENERATIVE_AI_API_KEY "!GOOGLE_KEY!" >nul
    echo [OK] Google API key saved
)

echo.
echo [OK] API keys configured
echo Restart your terminal for changes to take effect
goto end

:set_agent
echo.
echo Available agents:
call dexto list-agents --installed
echo.
set /p AGENT="Enter default agent name: "
call dexto setup --default-agent "!AGENT!" --no-interactive
goto end

:view_config
echo.
echo Current configuration:
echo.
if exist "%USERPROFILE%\.dexto\config\global.yml" (
    type "%USERPROFILE%\.dexto\config\global.yml"
) else (
    echo [INFO] No configuration file found
    echo Run setup wizard to create configuration
)
echo.
goto end

:end
echo.
pause
