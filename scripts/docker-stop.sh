#!/bin/bash
# Docker stop script for CloseShave

set -e

cd "$(dirname "$0")/.."

# Use docker compose (v2) if available, otherwise docker-compose (v1)
if docker compose version > /dev/null 2>&1; then
    COMPOSE_CMD="docker compose"
else
    COMPOSE_CMD="docker-compose"
fi

echo "Stopping CloseShave services..."
$COMPOSE_CMD down

echo "✅ Services stopped"

