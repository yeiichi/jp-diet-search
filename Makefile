PROJECT_NAME := jp-diet-search

.DEFAULT_GOAL := help

# -----------------------------------------------------------
# Help
# -----------------------------------------------------------
.PHONY: help help-all

help: ## Show this help
	@echo "$(PROJECT_NAME) - helper targets"
	@echo
	@awk 'BEGIN {FS = ":.*##"; printf "Available targets:\n\n"} \
		/^[a-zA-Z0-9_-]+:.*##/ { printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

help-all: ## Show all targets (including internal ones)
	@echo "$(PROJECT_NAME) - all targets (including internal)"
	@awk 'BEGIN {FS=":"} /^[a-zA-Z0-9_.-]+:/ {print "  "$$1}' $(MAKEFILE_LIST) | sort -u


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
