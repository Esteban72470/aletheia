.PHONY: help install dev test lint format clean docker-build docker-up docker-down

help:
	@echo "Aletheia Development Commands"
	@echo "=============================="
	@echo "install      - Install all dependencies"
	@echo "dev          - Start development environment"
	@echo "test         - Run all tests"
	@echo "lint         - Run linters"
	@echo "format       - Format code"
	@echo "clean        - Clean build artifacts"
	@echo "docker-build - Build Docker images"
	@echo "docker-up    - Start Docker services"
	@echo "docker-down  - Stop Docker services"

install:
	cd sidecar && pip install -e .
	cd cli && pip install -e .
	cd extension/vscode && pnpm install

dev:
	docker-compose up -d
	cd extension/vscode && pnpm run watch

test:
	cd sidecar && pytest
	cd cli && pytest
	cd extension/vscode && pnpm run test

lint:
	cd sidecar && ruff check .
	cd cli && ruff check .
	cd extension/vscode && pnpm run lint

format:
	cd sidecar && ruff format .
	cd cli && ruff format .
	cd extension/vscode && pnpm run format

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name "node_modules" -exec rm -rf {} +
	find . -type d -name "out" -exec rm -rf {} +
	find . -type d -name "dist" -exec rm -rf {} +

docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down
