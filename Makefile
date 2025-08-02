.PHONY: help install install-dev test lint format type-check clean build docs serve-docs

# Default target
help:
	@echo "Available commands:"
	@echo "  install      - Install the package"
	@echo "  install-dev  - Install development dependencies"
	@echo "  test         - Run tests"
	@echo "  lint         - Run linting"
	@echo "  format       - Format code"
	@echo "  type-check   - Run type checking"
	@echo "  clean        - Clean build artifacts"
	@echo "  build        - Build the package"
	@echo "  pre-commit   - Install pre-commit hooks"
	@echo "  check-all    - Run all checks (lint, type-check, test)"

# Installation
install:
	uv sync

install-dev:
	uv sync --dev

# Testing
test:
	pytest tests/ -v --cov=src/crack --cov-report=html --cov-report=term

test-fast:
	pytest tests/ -x -v

# Code quality
lint:
	ruff check src/ tests/
	pylint src/crack/

format:
	black src/ tests/
	ruff check --fix src/ tests/

type-check:
	mypy src/crack/

# Development tools
pre-commit:
	pre-commit install

check-all: lint type-check test

# Cleaning
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

# Building
build: clean
	uv build

# JetBrains specific commands
jetbrains-generate:
	python -m crack.jetbrains.jetbrains

jetbrains-server:
	python -m crack.jetbrains.server

jetbrains-update-plugins:
	python -m crack.jetbrains.plugins

# DBeaver specific commands
dbeaver-generate:
	python -m crack.dbeaver.dbeaver

# Development server
dev-server:
	uvicorn crack.jetbrains.server:app --reload --host 0.0.0.0 --port 5000
