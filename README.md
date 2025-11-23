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

## Development

### Linting and Formatting

#### Backend (Python)

We use `ruff` for linting and formatting, and `mypy` for type checking.

```bash
cd backend

# Install dev dependencies
make install
# or
uv venv && source .venv/bin/activate && uv pip install -e ".[dev]"

# Check linting
make lint
# or
ruff check .

# Format code
make format
# or
ruff format .

# Check formatting without changes
make format-check

# Type checking
make type-check
# or
mypy app

# Auto-fix issues
make fix
```

#### Frontend (TypeScript/React)

We use `ESLint` for linting and `Prettier` for formatting.

```bash
cd frontend

# Install dependencies
npm install

# Run ESLint
npm run lint

# Fix ESLint issues automatically
npm run lint:fix

# Format code with Prettier
npm run format

# Check formatting without changes
npm run format:check

# Type checking
npm run type-check
```

### GitHub Actions

The project includes a GitHub Actions workflow (`.github/workflows/lint.yml`) that automatically runs linting and formatting checks on:
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches

The workflow checks:
- Python: `ruff` linting and formatting, `mypy` type checking
- Frontend: `ESLint`, `Prettier`, and TypeScript type checking

## Project Structure

- `backend/` - Python FastAPI server with scrapers
- `frontend/` - React + Vite PWA
- `scripts/` - Installation and startup scripts
- `.github/workflows/` - GitHub Actions CI/CD workflows

## Configuration

Edit `backend/config/settings.json` to customize:
- Enabled merchants
- Request delays
- Cache TTL
- IP geolocation API key

## License

MIT

