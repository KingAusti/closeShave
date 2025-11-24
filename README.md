# CloseShave - Web Scraper PWA

A comprehensive web scraper Progressive Web Application that searches across major merchant sites to find the cheapest products with a Matrix/Cyberpunk aesthetic UI.

## Features

- 🔍 Search products across Amazon, eBay, Walmart, Target, Best Buy, and Newegg
- 💰 Price comparison with shipping and tax calculation based on your location
- 🎨 Matrix/Cyberpunk themed UI with neon effects and glitch animations
- 📱 Progressive Web App - installable and works offline
- ⚡ Fast hybrid scraping (requests + Playwright)
- 💾 SQLite caching for faster results
- 🖼️ Image proxying with direct links
- 📊 Out of stock indicators

## Quick Start

### 🚀 Easy Installation (Docker Hub - Recommended)

The easiest way to get started is using pre-built Docker images:

> **Note for maintainers:** Before sharing, replace `YOUR_USERNAME` with your actual GitHub username in the URLs below.

**Option 1: One-line install script**
```bash
curl -fsSL https://raw.githubusercontent.com/YOUR_USERNAME/closeshave/main/scripts/install-public.sh | bash
```

**Option 2: Manual Docker Compose**
```bash
# Download the public compose file
curl -fsSL https://raw.githubusercontent.com/YOUR_USERNAME/closeshave/main/docker-compose.public.yml -o docker-compose.yml

# Start the application
docker-compose up -d
```

That's it! The app will be available at:
- Frontend: `http://localhost`
- Backend API: `http://localhost:8000`

**Useful commands:**
```bash
# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Update to latest version
docker-compose pull && docker-compose up -d
```

### 🛠️ Development Setup (Build from Source)

If you want to build from source or contribute:

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/closeshave.git
cd closeshave

# Start with Docker Compose (builds images locally)
docker-compose up
```

### 💻 Local Development

If you prefer running locally:

```bash
# Install dependencies
./scripts/install.sh    # Mac/Linux
.\scripts\install.ps1   # Windows

# Start the app
./scripts/start.sh      # Mac/Linux
.\start.bat              # Windows
```

## Configuration

Edit `backend/config/settings.json` to customize:
- Enabled merchants
- Request delays
- Cache TTL
- IP geolocation API key

When using Docker, edit the file and restart:
```bash
docker-compose restart backend
```

## Project Structure

- `backend/` - Python FastAPI server with scrapers
- `frontend/` - React + Vite PWA
- `scripts/` - Installation and startup scripts
- `docker-compose.yml` - Docker Compose configuration
- `backend/Dockerfile` - Backend container definition
- `frontend/Dockerfile` - Frontend container definition

## Deployment

### Publishing to Docker Hub

To publish your own images to Docker Hub for easy distribution, see [DEPLOY.md](DEPLOY.md).

### Production Deployment

For production deployment options, see [DOCKER.md](DOCKER.md).

## License

MIT

