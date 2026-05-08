.PHONY: help dev lint typecheck test check clean

VENV = .venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip
RUFF = $(VENV)/bin/ruff
MYPY = $(VENV)/bin/mypy
PYTEST = $(VENV)/bin/pytest

$(VENV)/bin/activate:
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -e '.[dev]'

help: ## List available repo-local Makefile targets with short descriptions.
	@awk 'BEGIN {FS = ":.*## "}; /^[a-zA-Z0-9_.-]+:.*## / {printf "  %-24s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

dev: $(VENV)/bin/activate ## Create or refresh the local development environment.

lint: $(VENV)/bin/activate ## Run Ruff lint checks.
	$(RUFF) check .

typecheck: $(VENV)/bin/activate ## Run MyPy type checks.
	$(MYPY) src tests

test: $(VENV)/bin/activate ## Run the test suite.
	$(PYTEST)

check: lint typecheck test ## Run canonical local validation.

clean: ## Remove local development artifacts.
	rm -rf $(VENV) .mypy_cache .pytest_cache .ruff_cache src/*.egg-info
