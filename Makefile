.PHONY: help install lint typecheck test check build clean run site site-dev site-preview
.DEFAULT_GOAL := help

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'

install: ## Create venv and install deps
	uv venv && uv pip install -e ".[dev]"

lint: ## Run ruff linter
	uv run ruff check src/ tests/

typecheck: ## Run mypy --strict
	uv run mypy src/

test: ## Run tests with coverage
	uv run pytest tests/ -v --cov=src --cov-report=term-missing

check: lint typecheck test ## Lint + typecheck + test

build: check ## Check + build package
	uv build

clean: ## Remove build artifacts
	rm -rf dist/ .venv/ *.egg-info/ .ruff_cache/ .mypy_cache/ .pytest_cache/ htmlcov/ .coverage coverage.xml site/dist/ site/node_modules/

run: ## Run channel analysis (requires .env)
	uv run youtube-toolkit channels

site: ## Build documentation site (requires Node.js)
	cd site && npm ci && npm run build

site-dev: ## Start documentation dev server
	cd site && npm run dev

site-preview: ## Preview documentation production build
	cd site && npm run preview
