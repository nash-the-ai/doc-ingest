.PHONY: install dev test lint clean docker-build docker-run

install:
	pip install -e .

dev:
	pip install -e ".[dev]"

test:
	pytest tests/ -v

lint:
	ruff check src/
	ruff format --check src/

format:
	ruff format src/

clean:
	rm -rf build/ dist/ *.egg-info/ .pytest_cache/ .ruff_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +

# Docker
docker-build:
	docker build -t doc-ingest .

docker-run:
	docker run -it --rm -v $(PWD)/data:/data doc-ingest /data

# Quick test with sample docs
demo:
	doc-ingest ./examples/sample-docs --query "vacation policy" --stats
