#!/bin/bash
# Install CloseShave using pre-built Docker images from Docker Hub
# This script downloads and runs CloseShave without requiring source code

set -e

echo "🚀 Installing CloseShave..."
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first:"
    echo "   https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first:"
    echo "   https://docs.docker.com/compose/install/"
    exit 1
fi

# Determine compose command
if docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
else
    COMPOSE_CMD="docker-compose"
fi

# Determine where to save the compose file
COMPOSE_FILE="${HOME}/.closeshave/docker-compose.yml"
mkdir -p "$(dirname "$COMPOSE_FILE")"

# Download the public compose file
echo "📥 Downloading configuration..."
curl -fsSL https://raw.githubusercontent.com/YOUR_USERNAME/closeshave/main/docker-compose.public.yml -o "$COMPOSE_FILE"

# Pull and start the containers
echo "🐳 Pulling Docker images..."
cd "$(dirname "$COMPOSE_FILE")"
$COMPOSE_CMD -f "$COMPOSE_FILE" pull

echo "🚀 Starting CloseShave..."
$COMPOSE_CMD -f "$COMPOSE_FILE" up -d

echo ""
echo "✅ CloseShave is now running!"
echo ""
echo "📍 Access the application at:"
echo "   Frontend: http://localhost"
echo "   Backend API: http://localhost:8000"
echo ""
echo "📋 Useful commands:"
echo "   View logs: $COMPOSE_CMD -f $COMPOSE_FILE logs -f"
echo "   Stop: $COMPOSE_CMD -f $COMPOSE_FILE down"
echo "   Restart: $COMPOSE_CMD -f $COMPOSE_FILE restart"
echo "   Update: $COMPOSE_CMD -f $COMPOSE_FILE pull && $COMPOSE_CMD -f $COMPOSE_FILE up -d"
echo ""
echo "💡 Compose file saved to: $COMPOSE_FILE"

