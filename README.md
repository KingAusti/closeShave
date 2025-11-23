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

## Installation

### Docker (Recommended)

The easiest way to run CloseShave is using Docker Compose:

**Quick Start:**
```bash
# Mac/Linux
./scripts/docker-start.sh

# Windows
.\scripts\docker-start.ps1
```

**Manual Docker Commands:**
```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

The application will be available at:
- Frontend: `http://localhost`
- Backend API: `http://localhost:8000`

For detailed Docker documentation, see [DOCKER.md](DOCKER.md).

### Local Development

#### Mac/Linux

```bash
chmod +x scripts/install.sh
./scripts/install.sh
```

#### Windows

```powershell
.\scripts\install.ps1
```

## Usage

### Docker

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Rebuild after code changes
docker-compose up -d --build

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Local Development

After installation, start the application:

```bash
./scripts/start.sh
```

Or manually:

```bash
# Terminal 1 - Backend
cd backend
uv run uvicorn app.main:app --reload

# Terminal 2 - Frontend
cd frontend
pnpm run dev
```

Then open your browser to `http://localhost:5173`

## Project Structure

- `backend/` - Python FastAPI server with scrapers
- `frontend/` - React + Vite PWA
- `scripts/` - Installation and startup scripts
- `docker-compose.yml` - Docker Compose configuration
- `backend/Dockerfile` - Backend container definition
- `frontend/Dockerfile` - Frontend container definition

## Configuration

Edit `backend/config/settings.json` to customize:
- Enabled merchants
- Request delays
- Cache TTL
- IP geolocation API key

### Docker Configuration

When using Docker, configuration files are mounted as volumes. Edit `backend/config/settings.json` on the host machine and restart the container:

```bash
docker-compose restart backend
```

## Deployment

### Docker Deployment

See [DOCKER.md](DOCKER.md) for comprehensive Docker deployment instructions including:
- Production configuration
- Kubernetes deployment
- Docker Swarm setup
- Security best practices
- Monitoring and troubleshooting

## License

MIT

