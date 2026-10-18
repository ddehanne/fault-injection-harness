# Offline-only Python test suite. No service/network fault injection.
.PHONY: help test test-fault
help:
	@echo "Offline unit tests only: make test"
test:
	python3 -m pytest tests/ -q
test-fault:
	python3 -m pytest tests/ -q -m fault
