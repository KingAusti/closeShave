@echo off
cd /d "%~dp0"

echo Starting CloseShave...

cd backend
start "CloseShave Backend" cmd /k ".venv\Scripts\activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
cd ..

timeout /t 2 /nobreak >nul

cd frontend
start "CloseShave Frontend" cmd /k "pnpm run dev"
cd ..

echo.
echo CloseShave is running!
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:5173
echo.
echo Close the command windows to stop
pause

