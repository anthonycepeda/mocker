.PHONY: install format lint test run

install:
	uv sync

format:
	uv run ruff format .
	uv run ruff check . --fix

lint:
	uv run ruff check .
	uv run ruff format --check .

test:
	uv run pytest

run:
	uv run python asgi.py

run-reload:
	uv run uvicorn asgi:app --host 0.0.0.0 --port 8080 --reload
