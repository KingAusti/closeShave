#!/bin/bash

# Run all linting checks
set -e

echo "=========================================="
echo "Running Linting Checks"
echo "=========================================="
echo ""

# Backend linting
echo "Backend Linting (Python)..."
cd backend

if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    uv venv
fi

source .venv/bin/activate

echo "Installing dev dependencies..."
uv pip install -e ".[dev]" > /dev/null 2>&1 || uv pip install -e ".[dev]"

echo "Running ruff check..."
ruff check . || {
    echo "❌ Ruff check failed. Run 'ruff check --fix .' to auto-fix issues."
    exit 1
}

echo "Running ruff format check..."
ruff format --check . || {
    echo "❌ Code formatting check failed. Run 'ruff format .' to format code."
    exit 1
}

echo "Running mypy..."
mypy app || echo "⚠️  Mypy found type issues (non-blocking)"

echo "✅ Backend linting passed!"
echo ""

# Frontend linting
cd ../frontend
echo "Frontend Linting (TypeScript/React)..."

if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    pnpm install
fi

echo "Running ESLint..."
pnpm run lint || {
    echo "❌ ESLint check failed. Run 'pnpm run lint:fix' to auto-fix issues."
    exit 1
}

echo "Running Prettier format check..."
pnpm run format:check || {
    echo "❌ Prettier format check failed. Run 'pnpm run format' to format code."
    exit 1
}

echo "Running TypeScript type check..."
pnpm run type-check || {
    echo "❌ TypeScript type check failed."
    exit 1
}

echo "✅ Frontend linting passed!"
echo ""

cd ..
echo "=========================================="
echo "✅ All linting checks passed!"
echo "=========================================="

