#!/bin/bash
cd "$(dirname "$0")/.."

echo "Starting CloseShave..."

if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker is not running"
    exit 1
fi

docker-compose up -d --build

echo ""
echo "✅ CloseShave is running!"
echo "Frontend: http://localhost"
echo "Backend: http://localhost:8000"
echo ""
echo "View logs: docker-compose logs -f"
echo "Stop: docker-compose down"
