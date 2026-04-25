.PHONY: dev lint typecheck test check clean

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

dev: $(VENV)/bin/activate

lint: $(VENV)/bin/activate
	$(RUFF) check .

typecheck: $(VENV)/bin/activate
	$(MYPY) src tests

test: $(VENV)/bin/activate
	$(PYTEST)

check: lint typecheck test

clean:
	rm -rf $(VENV) .mypy_cache .pytest_cache .ruff_cache src/*.egg-info
