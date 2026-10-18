"""FAULT-01: injected torn JSONL tail must be detected, not silently cleaned."""
import json
import pytest
from harness.chaos_monkey import ChaosMorkey
from harness.invariant_checker import InvariantChecker, InvariantResult


@pytest.mark.fault
def test_truncated_tail_detected(ledger_path):
    original = {"timestamp": 1, "order_id": "o1"}
    ledger_path.write_text(json.dumps(original) + "\n", encoding="utf-8")
    result = ChaosMorkey(ledger_path).sigkill_ledger_write().execute()
    checker = InvariantChecker(ledger_path)
    assert result["injected"] is True
    assert checker.check_ledger_integrity()[1] is InvariantResult.FAIL
    assert ledger_path.read_text(encoding="utf-8").splitlines()[0] == json.dumps(original)


@pytest.mark.fault
def test_missing_ledger_is_failure(tmp_path):
    assert InvariantChecker(tmp_path / "missing.jsonl").validate_all()["all_pass"] is False
