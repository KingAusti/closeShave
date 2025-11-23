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

### Mac/Linux

```bash
chmod +x scripts/install.sh
./scripts/install.sh
```

### Windows

```powershell
.\scripts\install.ps1
```

## Usage

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
npm run dev
```

Then open your browser to `http://localhost:5173`

## Project Structure

- `backend/` - Python FastAPI server with scrapers
- `frontend/` - React + Vite PWA
- `scripts/` - Installation and startup scripts

## Configuration

Edit `backend/config/settings.json` to customize:
- Enabled merchants
- Request delays
- Cache TTL
- IP geolocation API key

## License

MIT

