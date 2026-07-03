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
	uv venv

.PHONY: install
install: ## Sync runtime dependencies into .venv
	uv sync

.PHONY: test
test: ## Run tests
	uv run --group dev pytest -q

.PHONY: docs
docs: ## Build Sphinx docs with warnings treated as errors
	uv run --extra docs sphinx-build -b html -W docs/source docs/build/html

.PHONY: build
build: ## Build wheel and sdist
	uv build

.PHONY: release-dry-run
release-dry-run: ## Dry-run Python Semantic Release version detection
	uv run --frozen --group dev semantic-release --noop version --no-vcs-release

.PHONY: release
release: ## Real release button: push main and let CI/CD release if needed
	git push origin main

.PHONY: release-existing
release-existing: ## Publish current pyproject version via manual PyPI workflow
	gh workflow run pypi.yml --ref main -f publish_existing=true

.PHONY: clean
clean: ## Remove build artifacts
	rm -rf build dist *.egg-info .pytest_cache .coverage htmlcov docs/build
	find . -name "__pycache__" -type d -exec rm -rf {} +
