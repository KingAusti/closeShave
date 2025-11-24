# Linting Setup Documentation

This document describes the linting and formatting setup for the CloseShave project.

## Overview

The project uses automated linting and formatting for both Python (backend) and TypeScript/React (frontend) code, with GitHub Actions CI/CD integration.

## Python Linting (Backend)

### Tools
- **Ruff**: Fast Python linter and formatter (replaces black, flake8, isort)
- **MyPy**: Static type checker
- **Bandit**: Security linter for Python
- **Pytest**: Testing framework

### Configuration
- Configuration in `backend/pyproject.toml` under `[tool.ruff]` and `[tool.mypy]`
- Line length: 100 characters
- Target Python version: 3.10+

### Commands

```bash
cd backend

# Install dev dependencies
make install
# or
uv venv && source .venv/bin/activate && uv pip install -e ".[dev]"

# Check for linting issues
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

# Security scanning
bandit -r app

# Run tests
make test
# or
pytest

# Auto-fix issues
make fix
```

## TypeScript/React Linting (Frontend)

### Tools
- **ESLint**: JavaScript/TypeScript linter
- **Prettier**: Code formatter
- **TypeScript**: Built-in type checker
- **Vitest**: Testing framework

### Configuration
- ESLint: `frontend/.eslintrc.cjs`
- Prettier: `frontend/.prettierrc`
- TypeScript: `frontend/tsconfig.json`

### Commands

```bash
cd frontend

# Install dependencies
npm install

# Run ESLint
npm run lint

# Auto-fix ESLint issues
npm run lint:fix

# Format code with Prettier
npm run format

# Check formatting without changes
npm run format:check

# Type checking
npm run type-check

# Run tests
pnpm run test

# Run tests in watch mode
pnpm run test:watch
```

## Quick Lint Scripts

Run all linting checks at once:

**Mac/Linux:**
```bash
chmod +x scripts/lint.sh
./scripts/lint.sh
```

**Windows:**
```powershell
.\scripts\lint.ps1
```

## GitHub Actions CI/CD

### Workflow File
`.github/workflows/ci.yml`

### Triggers
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches

### What It Checks

The CI workflow runs multiple jobs in parallel:

1. **Backend Linting:**
   - Ruff linting (`ruff check`)
   - Ruff formatting (`ruff format --check`)
   - MyPy type checking (non-blocking, logs issues)

2. **Backend Security:**
   - Bandit security scanning (`bandit -r app`)

3. **Backend Tests:**
   - Pytest test suite (`pytest -v`)

4. **Backend Build:**
   - Verifies backend can start successfully

5. **Frontend Linting:**
   - ESLint (`pnpm run lint`)
   - Prettier formatting (`pnpm run format:check`)
   - TypeScript type checking (`pnpm run type-check`)

6. **Frontend Security:**
   - pnpm audit for dependency vulnerabilities

7. **Frontend Tests:**
   - Vitest test suite (`pnpm run test`)

8. **Frontend Build:**
   - Verifies frontend can build successfully (`pnpm run build`)

### Dependency Installation

The CI workflow automatically installs all required dependencies:

- **Backend:**
  - Installs Python 3.11
  - Installs `uv` package manager
  - Creates virtual environment
  - Installs all dependencies including dev dependencies
  - Installs Playwright browsers if needed for tests

- **Frontend:**
  - Installs Node.js 18
  - Enables corepack and sets up pnpm 9.0.0
  - Installs all dependencies with `--frozen-lockfile`

### Viewing Results
- Go to the "Actions" tab in your GitHub repository
- Click on the workflow run to see detailed results
- Failed checks will block merging (if branch protection is enabled)

## Pre-commit Hooks (Optional)

Install pre-commit hooks to automatically run linting before each commit:

```bash
pip install pre-commit
pre-commit install
```

Configuration: `.pre-commit-config.yaml`

## IDE Integration

### VS Code

**Python:**
- Install "Ruff" extension
- Install "Pylance" or "Python" extension for type checking

**TypeScript/React:**
- Install "ESLint" extension
- Install "Prettier" extension
- Enable "Format on Save" in settings

### Recommended VS Code Settings

Create `.vscode/settings.json`:
```json
{
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.fixAll": "explicit"
    }
  },
  "[typescript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "[typescriptreact]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  }
}
```

## Troubleshooting

### Python Issues

**"ruff: command not found"**
- Install dev dependencies: `uv pip install -e ".[dev]"`

**"mypy: command not found"**
- Install dev dependencies: `uv pip install -e ".[dev]"`

### Frontend Issues

**"ESLint errors"**
- Run `npm run lint:fix` to auto-fix most issues
- Check `.eslintrc.cjs` for configuration

**"Prettier formatting errors"**
- Run `npm run format` to format code
- Check `.prettierrc` for configuration

**"TypeScript errors"**
- Run `npm run type-check` to see detailed errors
- Check `tsconfig.json` for configuration

## Best Practices

1. **Run linting before committing:**
   ```bash
   ./scripts/lint.sh  # or .\scripts\lint.ps1 on Windows
   ```

2. **Fix issues automatically when possible:**
   - Backend: `make fix` or `ruff check --fix . && ruff format .`
   - Frontend: `npm run lint:fix && npm run format`

3. **Check GitHub Actions before merging PRs:**
   - Ensure all checks pass
   - Fix any failing checks locally

4. **Keep dependencies updated:**
   - Backend: `uv pip install -e ".[dev]" --upgrade`
   - Frontend: `pnpm update`

5. **Run tests before committing:**
   - Backend: `pytest`
   - Frontend: `pnpm run test`

6. **Check security vulnerabilities:**
   - Backend: `bandit -r app`
   - Frontend: `pnpm audit`

## Testing

### Backend Tests

Tests are located in `backend/tests/` and use pytest.

```bash
cd backend
source .venv/bin/activate
pytest -v
```

### Frontend Tests

Tests are located in `frontend/src/**/__tests__/` and use Vitest.

```bash
cd frontend
pnpm run test
```

For watch mode during development:

```bash
pnpm run test:watch
```

### Writing Tests

**Backend:**
- Use pytest fixtures from `conftest.py`
- Test files should be named `test_*.py`
- Test functions should be named `test_*`

**Frontend:**
- Use Vitest and React Testing Library
- Test files should be named `*.test.ts` or `*.test.tsx`
- Place tests in `__tests__` directories next to the code they test

## Docker Hot Reload Development

For local development with hot reload, use the development Docker Compose file:

```bash
docker-compose -f docker-compose.dev.yml up
```

This will:
- Mount source code as volumes for both backend and frontend
- Enable hot reload on code changes
- Backend: Uses `uvicorn --reload` for automatic restarts
- Frontend: Uses Vite dev server with HMR (Hot Module Replacement)

Access:
- Backend: http://localhost:8000
- Frontend: http://localhost:5173

Changes to source code will automatically trigger reloads without rebuilding containers.

