"""Regression tests for malformed offline ledger inputs."""

import json

import pytest

from harness.invariant_checker import InvariantChecker, InvariantResult


@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf")])
def test_nonfinite_timestamps_rejected(ledger_path, value):
    ledger_path.write_text(
        json.dumps({"timestamp": 1}) + "\n"
        + json.dumps({"timestamp": value}) + "\n",
        encoding="utf-8",
    )
    checker = InvariantChecker(ledger_path)
    assert checker.check_monotone_timestamps()[1] is InvariantResult.FAIL


@pytest.mark.parametrize("order_id", [[], {}, None, 123, ""])
def test_invalid_order_ids_rejected(ledger_path, order_id):
    ledger_path.write_text(
        json.dumps({"order_id": order_id}) + "\n",
        encoding="utf-8",
    )
    checker = InvariantChecker(ledger_path)
    assert checker.check_no_duplicate_orders()[1] is InvariantResult.FAIL
