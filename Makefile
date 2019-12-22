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

.PHONY: mypy
mypy:
	$(PYTHON) -m mypy src/pywarmup \
		--ignore-missing-imports \
		--disallow-untyped-calls \
		--disallow-untyped-defs \
		--disallow-incomplete-defs \
		--check-untyped-defs \
		--warn-redundant-casts \
		--warn-return-any \
		--warn-unused-ignores \
		--warn-unused-configs \
		--no-implicit-optional

.PHONY: types
types: PYTEST_ARGS := $(PYTEST_ARGS) --monkeytype-output=./monkeytype.sqlite3
types:
	$(PYTHON) -m pytest $(PYTEST_ARGS) tests
	$(PYTHON) -m monkeytype list-modules |\
		xargs -n1 $(PYTHON) -m monkeytype --verbose apply
