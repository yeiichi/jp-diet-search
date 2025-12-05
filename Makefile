PROJECT_NAME := jp-diet-search

.DEFAULT_GOAL := help

.PHONY: help
help: ## Show this help
	@echo "$(PROJECT_NAME) - helper targets"
	@echo
	@awk 'BEGIN {FS = ":.*##"; printf "Available targets:

"} 		/^[a-zA-Z0-9_.-]+:.*##/ { printf "  [36m%-18s[0m %s
", $$1, $$2 }' $(MAKEFILE_LIST)

.PHONY: venv
venv: ## Create virtualenv in .venv
	python -m venv .venv

.PHONY: install
install: ## Install package in editable mode (requires activated venv)
	pip install -e .

.PHONY: test
test: ## Run tests
	pytest -q

.PHONY: build
build: ## Build wheel and sdist
	python -m build

.PHONY: clean
clean: ## Remove build artifacts
	rm -rf build dist *.egg-info .pytest_cache .coverage htmlcov
	find . -name "__pycache__" -type d -exec rm -rf {} +
