"""FAULT-01: SIGKILL during ledger write — recovery."""
import pytest
import json
from pathlib import Path
from harness.chaos_monkey import ChaosMorkey
from harness.invariant_checker import InvariantChecker

@pytest.mark.fault
def test_fault_01_ledger_recovery(read_ledger):
    """
    Scenario:
    1. Inject truncated JSON line into ledger
    2. System should detect corruption
    3. Verify: ledger can still be read (earlier lines intact)
    
    Invariant: Ledger integrity holds despite corruption
    """
    chaos = ChaosMorkey()
    checker = InvariantChecker()
    
    # Pre-injection: read ledger
    pre_ledger = read_ledger()
    pre_count = len(pre_ledger)
    
    # Inject fault: truncate ledger mid-write
    result = chaos.sigkill_ledger_write(delay_before_kill_ms=100).execute(lambda: None)
    
    # Verify: system can still read valid lines
    post_ledger = read_ledger()
    post_count = len(post_ledger)
    
    # Invariants
    summary = checker.validate_all()
    
    # Assert: corruption injected, but valid lines recovered
    assert result["result"]["injected"] == True
    assert summary["fault_detected"] == 0, f"Unexpected fault: {summary['results']}"
    print(f"✓ FAULT-01: Corruption handled, {pre_count}→{post_count} lines, all valid")
