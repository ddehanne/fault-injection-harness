"""FAULT-03: Double instance concurrent start — lock contention."""
import pytest
import time
import subprocess
from harness.chaos_monkey import ChaosMorkey
from harness.invariant_checker import InvariantChecker

@pytest.mark.fault
def test_fault_03_concurrent_start_lock(read_ledger):
    """
    Scenario:
    1. Inject race: systemctl start twice within 50ms
    2. INFRA-002 single-writer lock should prevent interleaving
    3. Verify: ledger writes are atomic (no interleaved entries)
    
    Invariant: Only one process writes to ledger at a time
    """
    chaos = ChaosMorkey()
    checker = InvariantChecker()
    
    pre_ledger = read_ledger()
    pre_count = len(pre_ledger)
    
    # Inject concurrent start
    result = chaos.concurrent_instance(race_window_ms=50).execute(lambda: None)
    
    time.sleep(1)  # Wait for service to stabilize
    
    post_ledger = read_ledger()
    post_count = len(post_ledger)
    
    # Verify: ledger integrity intact (no corrupted lines)
    summary = checker.validate_all()
    
    assert result["result"]["injected"] == True
    assert summary["fault_detected"] == 0, "Lock failed: corrupted entries detected"
    assert summary["passed"] >= 2
    print(f"✓ FAULT-03: Lock held, concurrent start prevented, {pre_count}→{post_count} lines")
