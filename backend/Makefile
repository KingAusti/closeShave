.PHONY: lint format type-check test install

install:
	uv venv
	source .venv/bin/activate && uv pip install -e ".[dev]"

lint:
	source .venv/bin/activate && ruff check .

format:
	source .venv/bin/activate && ruff format .

format-check:
	source .venv/bin/activate && ruff format --check .

type-check:
	source .venv/bin/activate && mypy app

test:
	source .venv/bin/activate && pytest

fix:
	source .venv/bin/activate && ruff check --fix . && ruff format .

