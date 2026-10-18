"""Safe, local-only fault fixtures. No host networking, services, or broker I/O."""
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import tempfile


class FaultType(Enum):
    SIGKILL_LEDGER_WRITE = "sigkill_ledger_write"
    BROKER_TCP_DISCONNECT = "broker_tcp_disconnect"
    CONCURRENT_INSTANCE = "concurrent_instance"
    PHANTOM_POSITION = "phantom_position"
    CLOCK_SKEW = "clock_skew"


@dataclass(frozen=True)
class FaultConfig:
    fault_type: FaultType
    parameters: dict


class ChaosMorkey:
    """Local JSONL truncation fixture; not an actual SIGKILL or integration test."""

    def __init__(self, ledger_path: Path):
        resolved = Path(ledger_path).resolve()
        root = Path(tempfile.gettempdir()).resolve()
        if not resolved.is_relative_to(root) or resolved == root:
            raise ValueError("Test ledger must be inside the system temporary directory")
        self.ledger_path = resolved
        self.config = None

    def sigkill_ledger_write(self, delay_before_kill_ms: int = 0):
        """Configure a torn JSONL tail simulation, not process termination."""
        self.config = FaultConfig(FaultType.SIGKILL_LEDGER_WRITE, {})
        return self

    def execute(self, system_under_test=None):
        if self.config is None:
            raise ValueError("No fault configured")
        if self.config.fault_type is not FaultType.SIGKILL_LEDGER_WRITE:
            raise NotImplementedError("Only disposable-file corruption is implemented")
        if not self.ledger_path.is_file():
            raise FileNotFoundError(self.ledger_path)
        with self.ledger_path.open('a', encoding='utf-8') as out:
            out.write('{"incomplete":')
        return {"fault_type": self.config.fault_type.value, "injected": True}
