# Fault Injection Harness Makefile

.PHONY: help install test coverage clean lint report

help:
	@echo "Fault Injection Harness — QS1-XSMR Infrastructure Validation"
	@echo ""
	@echo "Targets:"
	@echo "  install       Install test dependencies"
	@echo "  test          Run all fault injection tests"
	@echo "  test-fault    Run only @pytest.mark.fault tests"
	@echo "  coverage      Run tests with coverage report"
	@echo "  lint          Lint Python code"
	@echo "  clean         Remove test artifacts"
	@echo "  report        Generate HTML coverage report"

install:
	pip install -q -r requirements-test.txt

test: install
	pytest tests/ -v --tb=short

test-fault: install
	pytest tests/ -v -m "fault" --tb=short

coverage: install
	pytest tests/ --cov=harness --cov-report=html --cov-report=term-missing

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .coverage htmlcov

report:
	@if [ -f htmlcov/index.html ]; then \
		echo "Coverage report: htmlcov/index.html"; \
	else \
		echo "Run 'make coverage' first"; \
	fi
