# Linting Setup Documentation

This document describes the linting and formatting setup for the CloseShave project.

## Overview

The project uses automated linting and formatting for both Python (backend) and TypeScript/React (frontend) code, with GitHub Actions CI/CD integration.

## Python Linting (Backend)

### Tools
- **Ruff**: Fast Python linter and formatter (replaces black, flake8, isort)
- **MyPy**: Static type checker

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

# Auto-fix issues
make fix
```

## TypeScript/React Linting (Frontend)

### Tools
- **ESLint**: JavaScript/TypeScript linter
- **Prettier**: Code formatter
- **TypeScript**: Built-in type checker

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
1. **Python Backend:**
   - Ruff linting (`ruff check`)
   - Ruff formatting (`ruff format --check`)
   - MyPy type checking (non-blocking)

2. **Frontend:**
   - ESLint (`npm run lint`)
   - Prettier formatting (`npm run format:check`)
   - TypeScript type checking (`npm run type-check`)

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
   - Frontend: `npm update`

