# Run all linting checks (Windows PowerShell)

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Running Linting Checks" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Backend linting
Write-Host "Backend Linting (Python)..." -ForegroundColor Yellow
Set-Location backend

if (-not (Test-Path ".venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    uv venv
}

& .\.venv\Scripts\Activate.ps1

Write-Host "Installing dev dependencies..." -ForegroundColor Yellow
uv pip install -e ".[dev]" 2>&1 | Out-Null

Write-Host "Running ruff check..." -ForegroundColor Yellow
& .\.venv\Scripts\ruff.exe check .
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Ruff check failed. Run 'ruff check --fix .' to auto-fix issues." -ForegroundColor Red
    exit 1
}

Write-Host "Running ruff format check..." -ForegroundColor Yellow
& .\.venv\Scripts\ruff.exe format --check .
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Code formatting check failed. Run 'ruff format .' to format code." -ForegroundColor Red
    exit 1
}

Write-Host "Running mypy..." -ForegroundColor Yellow
& .\.venv\Scripts\mypy.exe app
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Mypy found type issues (non-blocking)" -ForegroundColor Yellow
}

Write-Host "✅ Backend linting passed!" -ForegroundColor Green
Write-Host ""

# Frontend linting
Set-Location ..\frontend
Write-Host "Frontend Linting (TypeScript/React)..." -ForegroundColor Yellow

if (-not (Test-Path "node_modules")) {
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    pnpm install
}

Write-Host "Running ESLint..." -ForegroundColor Yellow
pnpm run lint
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ ESLint check failed. Run 'pnpm run lint:fix' to auto-fix issues." -ForegroundColor Red
    exit 1
}

Write-Host "Running Prettier format check..." -ForegroundColor Yellow
pnpm run format:check
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Prettier format check failed. Run 'pnpm run format' to format code." -ForegroundColor Red
    exit 1
}

Write-Host "Running TypeScript type check..." -ForegroundColor Yellow
pnpm run type-check
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ TypeScript type check failed." -ForegroundColor Red
    exit 1
}

Write-Host "✅ Frontend linting passed!" -ForegroundColor Green
Write-Host ""

Set-Location ..
Write-Host "==========================================" -ForegroundColor Green
Write-Host "✅ All linting checks passed!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green

