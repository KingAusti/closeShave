# Docker stop script for CloseShave (Windows PowerShell)

Set-Location $PSScriptRoot\..

# Use docker compose (v2) if available, otherwise docker-compose (v1)
$COMPOSE_CMD = $null
try {
    docker compose version | Out-Null
    $COMPOSE_CMD = "docker compose"
} catch {
    try {
        docker-compose --version | Out-Null
        $COMPOSE_CMD = "docker-compose"
    } catch {
        Write-Host "❌ Docker Compose is not installed." -ForegroundColor Red
        exit 1
    }
}

Write-Host "Stopping CloseShave services..." -ForegroundColor Yellow
Invoke-Expression "$COMPOSE_CMD down"

Write-Host "✅ Services stopped" -ForegroundColor Green

