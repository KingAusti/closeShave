#!/bin/bash
set -e

echo "Installing CloseShave..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required. Install from https://www.python.org/"
    exit 1
fi

# Install uv if needed
if ! command -v uv &> /dev/null; then
    echo "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
fi

# Install backend
echo "Installing backend..."
cd backend
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
uv run playwright install chromium
cd ..

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "Error: Node.js is required. Install from https://nodejs.org/"
    exit 1
fi

# Install pnpm if needed
if ! command -v pnpm &> /dev/null; then
    corepack enable
    corepack prepare pnpm@latest --activate
fi

# Install frontend
echo "Installing frontend..."
cd frontend
pnpm install
cd ..

echo ""
echo "✅ Installation complete!"
echo "Start with: ./scripts/start.sh"
