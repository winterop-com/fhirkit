.PHONY: help install generate lint check test coverage docs docs-serve clean

GRAMMAR_DIR := grammars
GENERATED_DIR := generated

help:
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  install    Install Python dependencies"
	@echo "  generate   Generate ANTLR parsers (Python)"
	@echo "  lint       Format and lint code"
	@echo "  check      Check code without fixing"
	@echo "  test       Run parser tests"
	@echo "  coverage   Run tests with coverage report"
	@echo "  docs       Build documentation"
	@echo "  docs-serve Serve documentation locally"
	@echo "  clean      Remove generated files and caches"

install:
	@echo ">>> Installing Python dependencies"
	@uv sync

# Generate both parsers - fhirpath first since cql imports it
generate: generate-fhirpath generate-cql

generate-fhirpath:
	@echo ">>> Generating FHIRPath Python parser"
	@mkdir -p $(GENERATED_DIR)/fhirpath
	@cd $(GRAMMAR_DIR) && antlr -Dlanguage=Python3 -visitor \
		-o ../$(GENERATED_DIR)/fhirpath \
		fhirpath.g4

generate-cql:
	@echo ">>> Generating CQL Python parser"
	@mkdir -p $(GENERATED_DIR)/cql
	@cd $(GRAMMAR_DIR) && antlr -Dlanguage=Python3 -visitor \
		-o ../$(GENERATED_DIR)/cql \
		cql.g4

lint:
	@echo ">>> Formatting and linting"
	@uv run ruff format .
	@uv run ruff check . --fix
	@echo ">>> Running mypy"
	@uv run mypy src
	@echo ">>> Running pyright"
	@uv run pyright

check:
	@echo ">>> Checking code"
	@uv run ruff check .
	@uv run ruff format --check .
	@uv run mypy src
	@uv run pyright

test:
	@echo ">>> Running tests"
	@uv run pytest tests/ -v

coverage:
	@echo ">>> Running tests with coverage"
	@uv run pytest tests/ --cov=src/fhir_cql --cov-report=term-missing --cov-report=html
	@echo ">>> HTML report generated in htmlcov/"

docs:
	@echo ">>> Building documentation"
	@uv run --group docs mkdocs build

docs-serve:
	@echo ">>> Serving documentation at http://127.0.0.1:8000"
	@uv run --group docs mkdocs serve

clean:
	@echo ">>> Cleaning"
	@rm -rf $(GENERATED_DIR)
	@rm -rf .ruff_cache
	@rm -rf .mypy_cache
	@rm -rf .pytest_cache
	@rm -rf .coverage
	@rm -rf htmlcov
	@rm -rf coverage.xml
	@rm -rf site
	@rm -rf .venv
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

.DEFAULT_GOAL := help
