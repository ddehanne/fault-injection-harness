"""FAULT-05: validate timestamp monotonicity in synthetic records."""
import json
import pytest
from harness.invariant_checker import InvariantChecker, InvariantResult


@pytest.mark.fault
def test_backward_and_equal_timestamps_rejected(ledger_path):
    checker = InvariantChecker(ledger_path)
    for timestamps in ([1, 0], [1, 1]):
        ledger_path.write_text("".join(json.dumps({"timestamp": t}) + "\n" for t in timestamps), encoding="utf-8")
        assert checker.check_monotone_timestamps()[1] is InvariantResult.FAIL
    ledger_path.write_text('{"timestamp": 1}\n{"timestamp": 2}\n', encoding="utf-8")
    assert checker.check_monotone_timestamps()[1] is InvariantResult.PASS
