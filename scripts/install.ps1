# CloseShave Installation Script for Windows

Write-Host "Installing CloseShave..." -ForegroundColor Cyan

# Check Python
try {
    python --version | Out-Null
} catch {
    Write-Host "Error: Python 3 is required. Install from https://www.python.org/" -ForegroundColor Red
    exit 1
}

# Install uv if needed
try {
    uv --version | Out-Null
} catch {
    Write-Host "Installing uv..." -ForegroundColor Yellow
    Invoke-WebRequest -Uri "https://astral.sh/uv/install.ps1" -UseBasicParsing | Invoke-Expression
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")
}

# Install backend
Write-Host "Installing backend..." -ForegroundColor Yellow
Set-Location backend
uv venv
& .\.venv\Scripts\Activate.ps1
uv pip install -r requirements.txt
uv run playwright install chromium
Set-Location ..

# Check Node.js
try {
    node --version | Out-Null
} catch {
    Write-Host "Error: Node.js is required. Install from https://nodejs.org/" -ForegroundColor Red
    exit 1
}

# Install pnpm if needed
try {
    pnpm --version | Out-Null
} catch {
    corepack enable
    corepack prepare pnpm@latest --activate
}

# Install frontend
Write-Host "Installing frontend..." -ForegroundColor Yellow
Set-Location frontend
pnpm install
Set-Location ..

Write-Host ""
Write-Host "✅ Installation complete!" -ForegroundColor Green
Write-Host "Start with: .\start.bat" -ForegroundColor Cyan
