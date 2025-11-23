# CloseShave Installation Script for Windows
# Run this script in PowerShell: .\scripts\install.ps1

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "CloseShave Web Scraper - Installation" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
Write-Host "Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Python not found"
    }
    Write-Host "✓ $pythonVersion found" -ForegroundColor Green
    
    # Check version
    $versionMatch = $pythonVersion -match "Python (\d+)\.(\d+)"
    if ($versionMatch) {
        $major = [int]$matches[1]
        $minor = [int]$matches[2]
        if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 10)) {
            Write-Host "Error: Python 3.10 or higher is required" -ForegroundColor Red
            exit 1
        }
    }
} catch {
    Write-Host "Error: Python 3 is not installed. Please install Python 3.10 or higher." -ForegroundColor Red
    Write-Host "Visit: https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

# Check/Install uv
Write-Host ""
Write-Host "Checking uv installation..." -ForegroundColor Yellow
try {
    $uvVersion = uv --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "uv not found"
    }
    Write-Host "✓ uv found" -ForegroundColor Green
} catch {
    Write-Host "Installing uv..." -ForegroundColor Yellow
    $installScript = Invoke-WebRequest -Uri "https://astral.sh/uv/install.ps1" -UseBasicParsing
    Invoke-Expression $installScript.Content
    
    # Refresh PATH
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")
    
    try {
        $uvVersion = uv --version 2>&1
        Write-Host "✓ uv installed" -ForegroundColor Green
    } catch {
        Write-Host "Error: Failed to install uv. Please install manually." -ForegroundColor Red
        Write-Host "Visit: https://github.com/astral-sh/uv" -ForegroundColor Yellow
        exit 1
    }
}

# Install backend dependencies
Write-Host ""
Write-Host "Installing backend dependencies..." -ForegroundColor Yellow
Set-Location backend
uv venv
& .\.venv\Scripts\Activate.ps1
uv pip install -r requirements.txt

# Install Playwright browsers
Write-Host "Installing Playwright browsers..." -ForegroundColor Yellow
uv run playwright install chromium

Write-Host "✓ Backend dependencies installed" -ForegroundColor Green

# Check Node.js
Write-Host ""
Write-Host "Checking Node.js installation..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version
    if ($LASTEXITCODE -ne 0) {
        throw "Node.js not found"
    }
    
    $versionMatch = $nodeVersion -match "v(\d+)"
    if ($versionMatch) {
        $major = [int]$matches[1]
        if ($major -lt 18) {
            Write-Host "Error: Node.js 18 or higher is required" -ForegroundColor Red
            exit 1
        }
    }
    
    Write-Host "✓ Node.js $nodeVersion found" -ForegroundColor Green
} catch {
    Write-Host "Error: Node.js is not installed. Please install Node.js 18 or higher." -ForegroundColor Red
    Write-Host "Visit: https://nodejs.org/" -ForegroundColor Yellow
    exit 1
}

# Install frontend dependencies
Write-Host ""
Write-Host "Installing frontend dependencies..." -ForegroundColor Yellow
Set-Location ..\frontend
npm install

Write-Host "✓ Frontend dependencies installed" -ForegroundColor Green

# Create start script
Write-Host ""
Write-Host "Creating start script..." -ForegroundColor Yellow
Set-Location ..

$startScript = @"
@echo off
cd /d "%~dp0"

echo Starting CloseShave Web Scraper...
echo.

REM Start backend
echo Starting backend server...
cd backend
call .venv\Scripts\activate.bat
start "CloseShave Backend" cmd /k "uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
cd ..

timeout /t 3 /nobreak >nul

REM Start frontend
echo Starting frontend server...
cd frontend
start "CloseShave Frontend" cmd /k "npm run dev"
cd ..

echo.
echo ==========================================
echo CloseShave is running!
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:5173
echo.
echo Close the command windows to stop
echo ==========================================
pause
"@

$startScript | Out-File -FilePath "start.bat" -Encoding ASCII

Write-Host "✓ Start script created" -ForegroundColor Green

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "Installation Complete!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""
Write-Host "To start the application, run:" -ForegroundColor Yellow
Write-Host "  .\start.bat" -ForegroundColor Cyan
Write-Host ""
Write-Host "Or manually:" -ForegroundColor Yellow
Write-Host "  Backend:  cd backend && .venv\Scripts\activate && uvicorn app.main:app --reload" -ForegroundColor Cyan
Write-Host "  Frontend: cd frontend && npm run dev" -ForegroundColor Cyan
Write-Host ""

Set-Location ..

