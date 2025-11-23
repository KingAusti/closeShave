# Docker start script for CloseShave (Windows PowerShell)

Set-Location $PSScriptRoot\..

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Starting CloseShave with Docker" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is running
try {
    docker info | Out-Null
} catch {
    Write-Host "❌ Docker is not running. Please start Docker and try again." -ForegroundColor Red
    exit 1
}

# Check if Docker Compose is available
$composeAvailable = $false
try {
    docker compose version | Out-Null
    $COMPOSE_CMD = "docker compose"
    $composeAvailable = $true
} catch {
    try {
        docker-compose --version | Out-Null
        $COMPOSE_CMD = "docker-compose"
        $composeAvailable = $true
    } catch {
        Write-Host "❌ Docker Compose is not installed." -ForegroundColor Red
        exit 1
    }
}

# Build and start services
Write-Host "Building and starting services..." -ForegroundColor Yellow
Invoke-Expression "$COMPOSE_CMD up -d --build"

Write-Host ""
Write-Host "Waiting for services to be healthy..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Check service status
Write-Host ""
Write-Host "Service Status:" -ForegroundColor Yellow
Invoke-Expression "$COMPOSE_CMD ps"

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "✅ CloseShave is running!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Frontend: http://localhost" -ForegroundColor Cyan
Write-Host "Backend API: http://localhost:8000" -ForegroundColor Cyan
Write-Host ""
Write-Host "View logs: $COMPOSE_CMD logs -f" -ForegroundColor Yellow
Write-Host "Stop services: $COMPOSE_CMD down" -ForegroundColor Yellow
Write-Host "==========================================" -ForegroundColor Green

