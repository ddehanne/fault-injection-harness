"""Offline invariant checks over explicit, disposable test inputs."""
import json
from enum import Enum
from pathlib import Path


class InvariantResult(Enum):
    PASS = "pass"
    FAIL = "fail"
    FAULT_DETECTED = "fault_detected"


class InvariantChecker:
    def __init__(self, ledger_path: Path):
        self.ledger_path = Path(ledger_path)

    def _entries(self):
        # A missing or malformed ledger is not evidence of integrity.
        with self.ledger_path.open(encoding="utf-8") as handle:
            entries = [json.loads(line) for line in handle if line.strip()]
        if not all(isinstance(entry, dict) for entry in entries):
            raise ValueError("Ledger lines must be JSON objects")
        return entries

    def check_ledger_integrity(self):
        try:
            self._entries()
        except (OSError, ValueError, TypeError):
            return ("ledger_integrity", InvariantResult.FAIL)
        return ("ledger_integrity", InvariantResult.PASS)

    def check_monotone_timestamps(self):
        try:
            entries = self._entries()
            times = [entry["timestamp"] for entry in entries]
            if any(isinstance(t, bool) or not isinstance(t, (int, float)) for t in times):
                raise ValueError("Non-numeric timestamp")
            if any(b <= a for a, b in zip(times, times[1:])):
                return ("monotone_timestamps", InvariantResult.FAIL)
        except (OSError, ValueError, TypeError, KeyError):
            return ("monotone_timestamps", InvariantResult.FAIL)
        return ("monotone_timestamps", InvariantResult.PASS)

    def check_no_duplicate_orders(self):
        try:
            entries = self._entries()
            ids = [entry["order_id"] for entry in entries if "order_id" in entry]
            if len(ids) != len(set(ids)):
                return ("no_duplicate_orders", InvariantResult.FAIL)
        except (OSError, ValueError, TypeError):
            return ("no_duplicate_orders", InvariantResult.FAIL)
        return ("no_duplicate_orders", InvariantResult.PASS)

    def check_broker_ledger_sync(self, broker_pos: dict, ledger_pos: dict):
        try:
            if not isinstance(broker_pos, dict) or not isinstance(ledger_pos, dict):
                raise TypeError("Positions must be mappings")
            if any(type(x) not in (int, float) for x in (*broker_pos.values(), *ledger_pos.values())):
                raise TypeError("Position quantities must be numeric")
            return ("broker_ledger_sync", InvariantResult.PASS if broker_pos == ledger_pos else InvariantResult.FAIL)
        except (TypeError, ValueError):
            return ("broker_ledger_sync", InvariantResult.FAIL)

    def check_position_conservation(self, positions_ledger: dict):
        """Basic input check only; not proof of economic position conservation."""
        valid = isinstance(positions_ledger, dict) and all(
            isinstance(k, str) and k and type(v) in (int, float)
            for k, v in positions_ledger.items()
        )
        return ("position_input_valid", InvariantResult.PASS if valid else InvariantResult.FAIL)

    def validate_all(self):
        checks = [
            self.check_ledger_integrity(),
            self.check_monotone_timestamps(),
            self.check_no_duplicate_orders(),
        ]
        passed = sum(v is InvariantResult.PASS for _, v in checks)
        return {"total": len(checks), "passed": passed,
                "failed": len(checks) - passed,
                "fault_detected": 0, "all_pass": passed == len(checks),
                "results": [(k, v.value) for k, v in checks]}
