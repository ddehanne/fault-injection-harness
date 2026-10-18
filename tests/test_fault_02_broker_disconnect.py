"""FAULT-02: offline broker stub, not a TCP or real trading-loop test."""
import pytest


class OfflineBroker:
    def __init__(self):
        self.connected = False
        self.sent = []

    def submit(self, order_id):
        if not self.connected:
            raise ConnectionError("Broker offline")
        if order_id not in self.sent:
            self.sent.append(order_id)


@pytest.mark.fault
def test_offline_stub_rejects_and_retry_deduplicates():
    broker = OfflineBroker()
    with pytest.raises(ConnectionError):
        broker.submit("order-1")
    assert broker.sent == []
    broker.connected = True
    broker.submit("order-1")
    broker.submit("order-1")
    assert broker.sent == ["order-1"]
