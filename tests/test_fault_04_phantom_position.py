"""FAULT-04: symbol-level mismatch detection with synthetic positions."""
import pytest
from harness.invariant_checker import InvariantChecker, InvariantResult


@pytest.mark.fault
def test_mismatched_symbols_fail_reconciliation(ledger_path):
    checker = InvariantChecker(ledger_path)
    assert checker.check_broker_ledger_sync({"AAPL": 10}, {"MSFT": 10})[1] is InvariantResult.FAIL
    assert checker.check_broker_ledger_sync({"AAPL": 10}, {"AAPL": 10})[1] is InvariantResult.PASS
    assert checker.check_broker_ledger_sync({"AAPL": 10}, {"AAPL": 11})[1] is InvariantResult.FAIL
