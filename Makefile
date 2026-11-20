SHELL = /bin/bash

include .make/all.mk

.PHONY: all
all: format lint test ## Format, lint and test the repository

.PHONY: test
test: ## Run the unit tests
	pytest tests/unit -q

.PHONY: clean
clean: ## Remove the generated coverage reports and caches
	rm -rf coverage.xml .coverage htmlcov .pytest_cache .ruff_cache .hypothesis
