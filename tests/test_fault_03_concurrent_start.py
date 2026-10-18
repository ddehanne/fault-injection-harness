"""FAULT-03: local lock stub; does not test systemd or a production lock."""
import threading
import pytest


@pytest.mark.fault
def test_second_writer_refused_while_lock_held():
    lock = threading.Lock()
    assert lock.acquire(blocking=False)
    try:
        results = []
        contender = threading.Thread(target=lambda: results.append(lock.acquire(blocking=False)))
        contender.start()
        contender.join(timeout=2)
        assert not contender.is_alive()
        assert results == [False]
    finally:
        lock.release()
