# Contributing to CloseShave

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Development Setup

1. Fork and clone the repository
2. Follow the installation instructions in the README
3. Install development dependencies (see below)

## Code Style and Linting

### Python (Backend)

We use `ruff` for linting and formatting, and `mypy` for type checking.

**Before committing:**
```bash
cd backend
make fix  # Auto-fixes linting issues and formats code
make type-check  # Check types
```

**Manual commands:**
```bash
ruff check .          # Check for linting issues
ruff format .         # Format code
ruff check --fix .    # Auto-fix linting issues
mypy app              # Type checking
```

### TypeScript/React (Frontend)

We use `ESLint` for linting and `Prettier` for formatting.

**Before committing:**
```bash
cd frontend
npm run lint:fix      # Auto-fix ESLint issues
npm run format        # Format code with Prettier
npm run type-check    # TypeScript type checking
```

**Manual commands:**
```bash
npm run lint          # Check for linting issues
npm run lint:fix      # Auto-fix linting issues
npm run format        # Format code
npm run format:check  # Check formatting without changes
npm run type-check    # TypeScript type checking
```

## Pre-commit Hooks (Optional)

Install pre-commit hooks to automatically run linting before commits:

```bash
pip install pre-commit
pre-commit install
```

This will automatically run linting and formatting checks before each commit.

## GitHub Actions

All pull requests automatically run linting and formatting checks via GitHub Actions. The workflow will fail if:
- Python code doesn't pass `ruff` checks
- Python code isn't properly formatted
- Frontend code doesn't pass `ESLint` checks
- Frontend code isn't properly formatted with `Prettier`
- TypeScript type checking fails

## Commit Messages

Please write clear, descriptive commit messages:
- Use the imperative mood ("Add feature" not "Added feature")
- Keep the first line under 50 characters
- Add more details in the body if needed

## Pull Requests

1. Create a feature branch from `main` or `develop`
2. Make your changes
3. Ensure all linting and formatting checks pass
4. Submit a pull request with a clear description of changes

