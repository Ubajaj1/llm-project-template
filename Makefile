.PHONY: install ingest evals test lint format check warmup

install:
	pip install -e ".[dev]"

ingest:
	python scripts/ingest.py

evals:
	python scripts/run_evals.py

warmup:
	python scripts/warmup.py

test:
	pytest tests/ -v --cov=. --cov-report=term-missing

lint:
	ruff check .
	mypy .

format:
	ruff format .
	ruff check --fix .

check: lint test
