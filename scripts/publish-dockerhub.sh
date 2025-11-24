#!/bin/bash
# Build and publish CloseShave images to Docker Hub
# Usage: ./scripts/publish-dockerhub.sh [version]
# Example: ./scripts/publish-dockerhub.sh v0.1.0

set -e

# Configuration - Update these with your Docker Hub username
DOCKERHUB_USERNAME="${DOCKERHUB_USERNAME:-closeshave}"
VERSION="${1:-latest}"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}🐳 Building and publishing CloseShave images${NC}"
echo -e "${YELLOW}Docker Hub username: ${DOCKERHUB_USERNAME}${NC}"
echo -e "${YELLOW}Version: ${VERSION}${NC}"
echo ""

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if logged into Docker Hub
if ! docker info | grep -q "Username"; then
    echo "⚠️  Not logged into Docker Hub. Attempting to login..."
    docker login
fi

# Build backend
echo -e "${GREEN}📦 Building backend image...${NC}"
docker build -t "${DOCKERHUB_USERNAME}/backend:${VERSION}" ./backend
docker tag "${DOCKERHUB_USERNAME}/backend:${VERSION}" "${DOCKERHUB_USERNAME}/backend:latest"

# Build frontend
echo -e "${GREEN}📦 Building frontend image...${NC}"
docker build -t "${DOCKERHUB_USERNAME}/frontend:${VERSION}" ./frontend
docker tag "${DOCKERHUB_USERNAME}/frontend:${VERSION}" "${DOCKERHUB_USERNAME}/frontend:latest"

# Push images
echo -e "${GREEN}🚀 Pushing images to Docker Hub...${NC}"
docker push "${DOCKERHUB_USERNAME}/backend:${VERSION}"
docker push "${DOCKERHUB_USERNAME}/backend:latest"
docker push "${DOCKERHUB_USERNAME}/frontend:${VERSION}"
docker push "${DOCKERHUB_USERNAME}/frontend:latest"

echo ""
echo -e "${GREEN}✅ Successfully published images!${NC}"
echo ""
echo "Images published:"
echo "  - ${DOCKERHUB_USERNAME}/backend:${VERSION}"
echo "  - ${DOCKERHUB_USERNAME}/backend:latest"
echo "  - ${DOCKERHUB_USERNAME}/frontend:${VERSION}"
echo "  - ${DOCKERHUB_USERNAME}/frontend:latest"
echo ""
echo "💡 Don't forget to update docker-compose.public.yml with your username!"

