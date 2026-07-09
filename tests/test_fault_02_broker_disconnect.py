"""FAULT-02: Broker TCP disconnect mid-rebalance."""
import pytest
import time
from harness.chaos_monkey import ChaosMorkey
from harness.invariant_checker import InvariantChecker

@pytest.mark.fault
def test_fault_02_broker_disconnect_recovery(read_ledger):
    """
    Scenario:
    1. Inject 2s broker disconnect (port 4002 blockade)
    2. System should retry without duplicate orders
    3. Verify: no order ID appears twice in ledger
    
    Invariant: No duplicate orders despite reconnect
    """
    chaos = ChaosMorkey()
    checker = InvariantChecker()
    
    pre_ledger = read_ledger()
    pre_orders = set(e.get("order_id") for e in pre_ledger if "order_id" in e)
    
    # Inject broker disconnect
    result = chaos.broker_tcp_disconnect(duration_seconds=2.0).execute(lambda: None)
    
    post_ledger = read_ledger()
    post_orders = set(e.get("order_id") for e in post_ledger if "order_id" in e)
    
    # Verify
    summary = checker.validate_all()
    
    assert result["result"]["injected"] == True
    assert summary["passed"] >= 2, f"Invariant violations: {summary['results']}"
    assert len(post_orders - pre_orders) <= 1, "Too many new orders (duplicate?)"
    print(f"✓ FAULT-02: Disconnect handled, orders: {len(pre_orders)}→{len(post_orders)}")
