# 🦾 CloseShave - Cyberpunk Deal Hunter

> *Wake up, Samurai. We have deals to burn.*

A high-tech, **Matrix/Cyberpunk-themed** Progressive Web Application (PWA) that hacks into the mainframe of major merchant sites to extract the absolute lowest prices. Now powered by **DuckDuckGo** for stealthy deal reconnaissance.

![Cyberpunk UI](https://img.shields.io/badge/Style-Cyberpunk-00f3ff?style=for-the-badge)
![Status](https://img.shields.io/badge/System-ONLINE-00ff41?style=for-the-badge)
![Docker](https://img.shields.io/badge/Container-SECURE-ff00ff?style=for-the-badge)

## ⚡ System Capabilities

- **🔍 Multi-Vector Search**: Infiltrate Amazon, eBay, Walmart, Target, Best Buy, Newegg, and **DuckDuckGo Deals**.
- **🦆 Stealth Mode**: Use the new "Search Deals" toggle to leverage DuckDuckGo for finding hidden sales.
- **💰 Neural Price Analysis**: Automatic calculation of shipping and tax based on your geolocation.
- **🎨 Netrunner UI**: Immersive Matrix/Cyberpunk interface with neon effects, glitch animations, and terminal aesthetics.
- **🛡️ Error Interceptors**: Advanced modal pop-ups for system diagnostics and error handling.
- **📱 Offline Protocol**: Fully functional PWA that works even when the grid is down.
- **⚡ Hybrid Extraction**: Combines high-speed requests with Playwright for rendering heavy JS sites.
- **💾 Data Cache**: SQLite caching layer for instant data retrieval.

## 🚀 Quick Start: Jack In

### 🐳 Docker Deployment (Recommended)

Initialize the system using Docker containers. This is the cleanest way to run the stack.

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/closeshave.git
cd closeshave

# Build and deploy the stack
docker-compose -f docker-compose.dev.yml up --build
```

The system will be accessible at:
- **Frontend Interface**: `http://localhost:5173`
- **Backend Mainframe**: `http://localhost:8000`

### 🛠️ Manual Override (Local Dev)

If you prefer to run the binaries directly on your local machine:

```bash
# Install dependencies
./scripts/install.sh    # Mac/Linux
.\scripts\install.ps1   # Windows

# Initiate startup sequence
./scripts/start.sh      # Mac/Linux
.\start.bat             # Windows
```

## ⚙️ System Configuration

Access the mainframe settings at `backend/config/settings.json` to customize your rig:

- **Merchants**: Enable/disable specific target sites (including `duckduckgo`).
- **Scraping Protocols**: Adjust request delays and timeouts to avoid detection.
- **Geolocation**: Configure IP geolocation provider.

## 📂 Architecture

- `backend/` - **The Core**: Python FastAPI server with advanced scrapers.
- `frontend/` - **The Interface**: React + Vite PWA with cyberpunk styling.
- `scripts/` - **Executables**: Installation and startup scripts.
- `docker-compose.yml` - **Container Config**: Docker orchestration.

## 🤝 Contributing

Join the resistance. Fork the repo, hack the code, and submit a pull request.

## 📄 License

MIT - Free for all netrunners.
