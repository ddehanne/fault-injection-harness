"""Disposable test inputs; never touch host trading state."""
from pathlib import Path
import json
import pytest


@pytest.fixture
def ledger_path(tmp_path: Path) -> Path:
    path = tmp_path / "ledger.jsonl"
    path.write_text("", encoding="utf-8")
    return path


@pytest.fixture
def read_ledger(ledger_path: Path):
    def _read():
        with ledger_path.open(encoding="utf-8") as handle:
            return [json.loads(line) for line in handle if line.strip()]
    return _read


@pytest.fixture
def positions_file(tmp_path: Path) -> Path:
    path = tmp_path / "positions.json"
    path.write_text("{}", encoding="utf-8")
    return path
