"""Pytest fixtures for fault injection harness."""
import pytest
import subprocess
import time
import os
import json
from pathlib import Path

@pytest.fixture(scope="session")
def trading_service():
    """Ensure trading-loop.service is available."""
    yield
    # Cleanup after all tests
    subprocess.run(['systemctl', 'stop', 'trading-loop.service'], check=False)

@pytest.fixture
def ledger_path():
    """Path to ledger.jsonl."""
    return Path('/opt/trading/data/state_store/ledger.jsonl')

@pytest.fixture
def read_ledger(ledger_path):
    """Helper to read ledger safely."""
    def _read():
        if not ledger_path.exists():
            return []
        try:
            with open(ledger_path) as f:
                return [json.loads(line) for line in f if line.strip()]
        except json.JSONDecodeError:
            return []
        except Exception as e:
            return []
    return _read

@pytest.fixture
def positions_file():
    """Path to executor positions file."""
    return Path('/opt/trading/data/system/executor_positions.json')

@pytest.fixture
def read_positions(positions_file):
    """Helper to read positions safely."""
    def _read():
        if not positions_file.exists():
            return {}
        try:
            with open(positions_file) as f:
                return json.load(f)
        except Exception:
            return {}
    return _read

@pytest.fixture(autouse=True)
def cleanup_ledger_corruption(ledger_path):
    """Auto-cleanup ledger corruption after each test."""
    yield
    # Remove truncated lines (corruption artifacts from FAULT-01)
    if ledger_path.exists():
        try:
            with open(ledger_path) as f:
                lines = f.readlines()
            
            valid_lines = []
            for line in lines:
                if line.strip():
                    try:
                        json.loads(line)
                        valid_lines.append(line)
                    except json.JSONDecodeError:
                        pass  # Skip corrupted line
            
            if len(valid_lines) != len(lines):
                with open(ledger_path, 'w') as f:
                    f.writelines(valid_lines)
        except Exception:
            pass
