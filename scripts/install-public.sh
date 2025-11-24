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

# Check for required GitHub username
if [ -z "$GITHUB_USERNAME" ]; then
    echo "❌ Error: GITHUB_USERNAME environment variable is not set."
    echo ""
    echo "Please set your GitHub username before running this script:"
    echo "   export GITHUB_USERNAME=your-github-username"
    echo "   curl -fsSL https://raw.githubusercontent.com/\$GITHUB_USERNAME/closeshave/main/scripts/install-public.sh | bash"
    echo ""
    echo "Or run it directly:"
    echo "   GITHUB_USERNAME=your-github-username bash <(curl -fsSL https://raw.githubusercontent.com/your-github-username/closeshave/main/scripts/install-public.sh)"
    exit 1
fi

# Check for required Docker Hub username
if [ -z "$DOCKERHUB_USERNAME" ]; then
    echo "❌ Error: DOCKERHUB_USERNAME environment variable is not set."
    echo ""
    echo "Please set your Docker Hub username before running this script:"
    echo "   export DOCKERHUB_USERNAME=your-dockerhub-username"
    echo "   export GITHUB_USERNAME=your-github-username"
    echo "   curl -fsSL https://raw.githubusercontent.com/\$GITHUB_USERNAME/closeshave/main/scripts/install-public.sh | bash"
    echo ""
    echo "Or run it directly:"
    echo "   DOCKERHUB_USERNAME=your-dockerhub-username GITHUB_USERNAME=your-github-username bash <(curl -fsSL https://raw.githubusercontent.com/your-github-username/closeshave/main/scripts/install-public.sh)"
    exit 1
fi

# Determine where to save the compose file
COMPOSE_FILE="${HOME}/.closeshave/docker-compose.yml"
mkdir -p "$(dirname "$COMPOSE_FILE")"

# Download the public compose file
echo "📥 Downloading configuration..."
curl -fsSL "https://raw.githubusercontent.com/${GITHUB_USERNAME}/closeshave/main/docker-compose.public.yml" -o "$COMPOSE_FILE"

# Substitute Docker Hub username placeholder in the compose file
echo "🔧 Configuring Docker Hub username..."
# Use awk for safe substitution that handles all special characters correctly
# awk doesn't require escaping for sed metacharacters and doesn't do shell variable expansion
# Use a temporary file for cross-platform compatibility
TEMP_FILE=$(mktemp)
awk -v username="$DOCKERHUB_USERNAME" '{gsub(/YOUR_DOCKERHUB_USERNAME/, username)}1' "$COMPOSE_FILE" > "$TEMP_FILE"
mv "$TEMP_FILE" "$COMPOSE_FILE"

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

