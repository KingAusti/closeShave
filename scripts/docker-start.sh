#!/bin/bash
# Docker start script for CloseShave

set -e

cd "$(dirname "$0")/.."

echo "=========================================="
echo "Starting CloseShave with Docker"
echo "=========================================="
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose > /dev/null 2>&1 && ! docker compose version > /dev/null 2>&1; then
    echo "❌ Docker Compose is not installed."
    exit 1
fi

# Use docker compose (v2) if available, otherwise docker-compose (v1)
if docker compose version > /dev/null 2>&1; then
    COMPOSE_CMD="docker compose"
else
    COMPOSE_CMD="docker-compose"
fi

# Build and start services
echo "Building and starting services..."
$COMPOSE_CMD up -d --build

echo ""
echo "Waiting for services to be healthy..."
sleep 5

# Check service status
echo ""
echo "Service Status:"
$COMPOSE_CMD ps

echo ""
echo "=========================================="
echo "✅ CloseShave is running!"
echo "=========================================="
echo ""
echo "Frontend: http://localhost"
echo "Backend API: http://localhost:8000"
echo ""
echo "View logs: $COMPOSE_CMD logs -f"
echo "Stop services: $COMPOSE_CMD down"
echo "=========================================="

