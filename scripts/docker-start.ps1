# Docker start script for CloseShave (Windows)

Set-Location $PSScriptRoot\..

Write-Host "Starting CloseShave..." -ForegroundColor Cyan

try {
    docker info | Out-Null
} catch {
    Write-Host "Error: Docker is not running" -ForegroundColor Red
    exit 1
}

docker-compose up -d --build

Write-Host ""
Write-Host "✅ CloseShave is running!" -ForegroundColor Green
Write-Host "Frontend: http://localhost" -ForegroundColor Cyan
Write-Host "Backend: http://localhost:8000" -ForegroundColor Cyan
Write-Host ""
Write-Host "View logs: docker-compose logs -f" -ForegroundColor Yellow
Write-Host "Stop: docker-compose down" -ForegroundColor Yellow
