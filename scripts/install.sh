#!/bin/bash

# CloseShave Installation Script for Mac/Linux
set -e

echo "=========================================="
echo "CloseShave Web Scraper - Installation"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check Python
echo "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed. Please install Python 3.10 or higher.${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
REQUIRED_VERSION="3.10"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo -e "${RED}Error: Python 3.10 or higher is required. Found: $PYTHON_VERSION${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Python $PYTHON_VERSION found${NC}"

# Check/Install uv
echo ""
echo "Checking uv installation..."
if ! command -v uv &> /dev/null; then
    echo "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
    if ! command -v uv &> /dev/null; then
        echo -e "${RED}Error: Failed to install uv${NC}"
        exit 1
    fi
fi

echo -e "${GREEN}✓ uv found${NC}"

# Install backend dependencies
echo ""
echo "Installing backend dependencies..."
cd backend
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt

# Install Playwright browsers
echo "Installing Playwright browsers..."
uv run playwright install chromium

echo -e "${GREEN}✓ Backend dependencies installed${NC}"

# Check Node.js
echo ""
echo "Checking Node.js installation..."
if ! command -v node &> /dev/null; then
    echo -e "${RED}Error: Node.js is not installed. Please install Node.js 18 or higher.${NC}"
    echo "Visit: https://nodejs.org/"
    exit 1
fi

NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
REQUIRED_NODE="18"

if [ "$NODE_VERSION" -lt "$REQUIRED_NODE" ]; then
    echo -e "${RED}Error: Node.js 18 or higher is required. Found: $(node --version)${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Node.js $(node --version) found${NC}"

# Install frontend dependencies
echo ""
echo "Installing frontend dependencies..."
cd ../frontend
npm install

echo -e "${GREEN}✓ Frontend dependencies installed${NC}"

# Create start script
echo ""
echo "Creating start script..."
cd ..
cat > start.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"

echo "Starting CloseShave Web Scraper..."
echo ""

# Start backend
echo "Starting backend server..."
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 3

# Start frontend
echo "Starting frontend server..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "=========================================="
echo "CloseShave is running!"
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop"
echo "=========================================="

# Wait for user interrupt
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM
wait
EOF

chmod +x start.sh

echo -e "${GREEN}✓ Start script created${NC}"

echo ""
echo -e "${GREEN}=========================================="
echo "Installation Complete!"
echo "==========================================${NC}"
echo ""
echo "To start the application, run:"
echo "  ./start.sh"
echo ""
echo "Or manually:"
echo "  Backend:  cd backend && source .venv/bin/activate && uvicorn app.main:app --reload"
echo "  Frontend: cd frontend && npm run dev"
echo ""

