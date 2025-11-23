#!/bin/bash
cd "$(dirname "$0")/.."

echo "Starting CloseShave..."

# Start backend
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

sleep 2

# Start frontend
cd frontend
pnpm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ CloseShave is running!"
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop"

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM
wait
