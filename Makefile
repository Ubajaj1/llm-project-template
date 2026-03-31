.PHONY: install ingest evals test lint format check

install:
	pip install -e ".[dev]"

ingest:
	python scripts/ingest.py

evals:
	python scripts/run_evals.py

test:
	pytest tests/ -v --cov=. --cov-report=term-missing

lint:
	ruff check .
	mypy .

format:
	ruff format .
	ruff check --fix .

check: lint test
