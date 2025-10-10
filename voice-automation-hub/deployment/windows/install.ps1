# Voice Automation Hub - Windows Installation Script
# Installs dependencies and sets up the environment

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "Voice Automation Hub - Installation" -ForegroundColor Cyan
Write-Host "======================================`n" -ForegroundColor Cyan

# Check Python
Write-Host "Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found! Please install Python 3.11+" -ForegroundColor Red
    Write-Host "Download from: https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

# Check Node.js
Write-Host "`nChecking Node.js installation..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version 2>&1
    Write-Host "✅ Found: Node.js $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js not found! Please install Node.js 20+" -ForegroundColor Red
    Write-Host "Download from: https://nodejs.org/" -ForegroundColor Yellow
    exit 1
}

# Navigate to project root
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Join-Path $scriptPath "..\.."
Set-Location $projectRoot

Write-Host "`n📦 Installing backend dependencies..." -ForegroundColor Yellow
Set-Location "backend"

# Install Python dependencies
try {
    pip install -r requirements.txt
    Write-Host "✅ Backend dependencies installed" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to install backend dependencies" -ForegroundColor Red
    exit 1
}

Set-Location $projectRoot

Write-Host "`n📦 Installing frontend dependencies..." -ForegroundColor Yellow
Set-Location "frontend"

# Install Node dependencies
try {
    npm install
    Write-Host "✅ Frontend dependencies installed" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to install frontend dependencies" -ForegroundColor Red
    exit 1
}

Set-Location $projectRoot

# Create .env file if it doesn't exist
if (-not (Test-Path ".env")) {
    Write-Host "`n⚙️  Creating .env configuration file..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    
    Write-Host "`n⚠️  IMPORTANT: Please edit .env and add your OPENAI_API_KEY" -ForegroundColor Red
    Write-Host "   Edit the file: .\.env" -ForegroundColor Yellow
    Write-Host "   Get your API key from: https://platform.openai.com/api-keys" -ForegroundColor Yellow
} else {
    Write-Host "`n✅ .env file already exists" -ForegroundColor Green
}

Write-Host "`n======================================" -ForegroundColor Cyan
Write-Host "✅ Installation Complete!" -ForegroundColor Green
Write-Host "======================================`n" -ForegroundColor Cyan

Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Edit .env and add your OPENAI_API_KEY" -ForegroundColor White
Write-Host "2. Run: .\deployment\windows\start.bat" -ForegroundColor White
Write-Host "3. Open: http://localhost:5173`n" -ForegroundColor White

