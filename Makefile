.PHONY: help lint format typecheck install pre-commit clean build up down test

PYTHON_DIRS = dags plugins

help:
	@echo "Available commands:"
	@echo "  make install       Install dependencies using poetry"
	@echo "  make lint          Run all linters (black, isort, flake8, pylint, mypy)"
	@echo "  make format        Format code using black and isort"
	@echo "  make typecheck     Run mypy type checking"
	@echo "  make pre-commit    Install pre-commit hooks"
	@echo "  make clean         Remove build artifacts and cache directories"
	@echo "  make build         Build Docker images"
	@echo "  make up            Start Docker containers"
	@echo "  make down          Stop Docker containers"
	@echo "  make test          Run tests"

install:
	@poetry install

lint:
	@chmod +x scripts/lint.sh
	@./scripts/lint.sh

format:
	@echo "Formatting Python code with black..."
	@poetry run black $(PYTHON_DIRS)
	@echo "Sorting imports with isort..."
	@poetry run isort $(PYTHON_DIRS) --profile black

typecheck:
	@echo "Type checking with mypy..."
	@poetry run mypy $(PYTHON_DIRS)

pre-commit:
	@poetry run pre-commit install

clean:
	@echo "Cleaning up..."
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type d -name "*.egg-info" -exec rm -rf {} +
	@find . -type d -name "*.eggs" -exec rm -rf {} +
	@find . -type f -name "*.pyc" -delete
	@find . -type f -name "*.pyo" -delete
	@find . -type f -name "*.pyd" -delete
	@find . -type f -name ".coverage" -delete
	@find . -type d -name "*.cover" -exec rm -rf {} +
	@find . -type d -name "htmlcov" -exec rm -rf {} +
	@find . -type d -name ".pytest_cache" -exec rm -rf {} +
	@find . -type d -name ".coverage" -exec rm -rf {} +
	@find . -type d -name ".mypy_cache" -exec rm -rf {} +
	@rm -rf build/
	@rm -rf dist/

build:
	@docker-compose build

up:
	@docker-compose up -d

down:
	@docker-compose down

test:
	@poetry run pytest tests/
