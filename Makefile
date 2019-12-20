python_files := $(shell find . -name \*.py -not -path '*/\.*')

PYTHON ?= python
PYTEST_ARGS ?= -vv

.PHONY: format
format:
	$(PYTHON) -m isort $(python_files)
	$(PYTHON) -m black $(python_files)

.PHONY: lint
lint:
	$(PYTHON) -m isort --check $(python_files)
	$(PYTHON) -m black --check $(python_files)

.PHONY: test
test:
	$(PYTHON) -m pytest $(PYTEST_ARGS) tests