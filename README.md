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

### Docker (Recommended)

```bash
docker-compose up
```

That's it! The app will be available at:
- Frontend: `http://localhost`
- Backend API: `http://localhost:8000`

**Other useful commands:**
```bash
# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Rebuild after changes
docker-compose up --build
```

### Local Development

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

For production deployment, see [DOCKER.md](DOCKER.md).

## License

MIT

