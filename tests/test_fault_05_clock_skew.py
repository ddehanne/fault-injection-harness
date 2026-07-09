"""FAULT-05: Clock skew +1500ms (NTP jump) — monotone time."""
import pytest
import json
import time
from harness.chaos_monkey import ChaosMorkey
from harness.invariant_checker import InvariantChecker

@pytest.mark.fault
def test_fault_05_clock_skew_monotone(read_ledger):
    """
    Scenario:
    1. Inject clock jump: +1500ms mid-cycle
    2. System continues trading under skewed time
    3. Verify: ledger timestamps remain strictly monotone (no backwards time)
    
    Invariant: Logical time >= wall time (causality preserved)
    """
    chaos = ChaosMorkey()
    checker = InvariantChecker()
    
    pre_ledger = read_ledger()
    pre_time = time.time()
    
    # Inject clock skew: +1500ms
    result = chaos.clock_skew(offset_seconds=1500).execute(lambda: None)
    
    post_ledger = read_ledger()
    post_time = time.time()
    
    # Verify: timestamps in ledger are still monotone
    summary = checker.validate_all()
    
    assert result["result"]["injected"] == True
    assert result["result"]["fault"] == "clock_skew"
    # Critical: monotone_timestamps must pass despite skew
    results_dict = {name: status for name, status in summary["results"]}
    assert results_dict.get("monotone_timestamps") == "pass", "Clock skew broke causality"
    assert summary["fault_detected"] == 0, "System should handle skew gracefully"
    print(f"✓ FAULT-05: Clock skew +1500ms, causality preserved, {len(post_ledger)} lines monotone")
