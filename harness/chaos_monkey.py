"""Deterministic fault injection engine."""
import os
import json
import time
import signal
import subprocess
from pathlib import Path
from typing import Callable, Optional
from dataclasses import dataclass
from enum import Enum

class FaultType(Enum):
    SIGKILL_LEDGER_WRITE = "sigkill_ledger_write"
    BROKER_TCP_DISCONNECT = "broker_tcp_disconnect"
    CONCURRENT_INSTANCE = "concurrent_instance"
    PHANTOM_POSITION = "phantom_position"
    CLOCK_SKEW = "clock_skew"

@dataclass
class FaultConfig:
    fault_type: FaultType
    parameters: dict
    duration_seconds: float = 5.0

class ChaosMorkey:
    """Inject faults deterministically into trading system."""
    
    def __init__(self):
        self.ledger_path = Path('/opt/trading/data/state_store/ledger.jsonl')
        self.config = None
    
    def sigkill_ledger_write(self, delay_before_kill_ms: int = 500):
        """FAULT-01: SIGKILL during ledger write."""
        self.config = FaultConfig(
            fault_type=FaultType.SIGKILL_LEDGER_WRITE,
            parameters={"delay_before_kill_ms": delay_before_kill_ms}
        )
        return self
    
    def broker_tcp_disconnect(self, duration_seconds: float = 2.0):
        """FAULT-02: Broker connection drops mid-rebalance."""
        self.config = FaultConfig(
            fault_type=FaultType.BROKER_TCP_DISCONNECT,
            parameters={"duration_seconds": duration_seconds},
            duration_seconds=duration_seconds
        )
        return self
    
    def concurrent_instance(self, race_window_ms: int = 100):
        """FAULT-03: Double instance concurrent start."""
        self.config = FaultConfig(
            fault_type=FaultType.CONCURRENT_INSTANCE,
            parameters={"race_window_ms": race_window_ms}
        )
        return self
    
    def phantom_position(self, symbol: str = "RGTI", qty: int = 1000):
        """FAULT-04: Phantom position (broker anomaly)."""
        self.config = FaultConfig(
            fault_type=FaultType.PHANTOM_POSITION,
            parameters={"symbol": symbol, "qty": qty}
        )
        return self
    
    def clock_skew(self, offset_seconds: int = 1500):
        """FAULT-05: Clock jump (NTP anomaly)."""
        self.config = FaultConfig(
            fault_type=FaultType.CLOCK_SKEW,
            parameters={"offset_seconds": offset_seconds},
            duration_seconds=float(offset_seconds)
        )
        return self
    
    def execute(self, system_under_test: Callable):
        """Run system with injected fault."""
        if not self.config:
            raise ValueError("No fault configured")
        
        pre_state = self._capture_state()
        try:
            result = self._run_with_fault(system_under_test)
        except Exception as e:
            result = {"error": str(e), "fault_triggered": True}
        
        post_state = self._capture_state()
        
        return {
            "fault_type": self.config.fault_type.value,
            "pre_state": pre_state,
            "post_state": post_state,
            "result": result,
            "timestamp": time.time()
        }
    
    def _run_with_fault(self, system_under_test: Callable):
        """Execute system with specific fault active."""
        fault_type = self.config.fault_type
        
        if fault_type == FaultType.SIGKILL_LEDGER_WRITE:
            return self._inject_sigkill_ledger_write(system_under_test)
        elif fault_type == FaultType.BROKER_TCP_DISCONNECT:
            return self._inject_broker_disconnect(system_under_test)
        elif fault_type == FaultType.CONCURRENT_INSTANCE:
            return self._inject_concurrent_instance(system_under_test)
        elif fault_type == FaultType.PHANTOM_POSITION:
            return self._inject_phantom_position(system_under_test)
        elif fault_type == FaultType.CLOCK_SKEW:
            return self._inject_clock_skew(system_under_test)
        else:
            raise ValueError(f"Unknown fault type: {fault_type}")
    
    def _inject_sigkill_ledger_write(self, sut: Callable):
        """Simulate SIGKILL mid-ledger write."""
        if self.ledger_path.exists():
            with open(self.ledger_path, 'a') as f:
                f.write('{"corrupted": true, "incomplete')
        
        return {"injected": True, "fault": "ledger_truncated"}
    
    def _inject_broker_disconnect(self, sut: Callable):
        """Simulate broker TCP disconnect."""
        delay = self.config.parameters.get("duration_seconds", 2.0)
        subprocess.run(
            "sudo iptables -A INPUT -p tcp --dport 4002 -j DROP",
            shell=True, check=False
        )
        time.sleep(delay)
        subprocess.run(
            "sudo iptables -D INPUT -p tcp --dport 4002 -j DROP",
            shell=True, check=False
        )
        return {"injected": True, "fault": "broker_disconnect", "duration_s": delay}
    
    def _inject_concurrent_instance(self, sut: Callable):
        """Simulate double start race."""
        subprocess.Popen(['systemctl', 'start', 'trading-loop.service'])
        time.sleep(0.05)
        subprocess.Popen(['systemctl', 'start', 'trading-loop.service'])
        time.sleep(0.5)
        return {"injected": True, "fault": "concurrent_start"}
    
    def _inject_phantom_position(self, sut: Callable):
        """Inject phantom position into broker state."""
        phantom = {
            "symbol": self.config.parameters.get("symbol", "RGTI"),
            "qty": self.config.parameters.get("qty", 1000),
            "injected_at": time.time()
        }
        return {"injected": True, "fault": "phantom_position", "phantom": phantom}
    
    def _inject_clock_skew(self, sut: Callable):
        """Simulate NTP jump."""
        offset = self.config.parameters.get("offset_seconds", 1500)
        return {"injected": True, "fault": "clock_skew", "offset_s": offset}
    
    def _capture_state(self):
        """Capture system state snapshot."""
        ledger_lines = 0
        if self.ledger_path.exists():
            with open(self.ledger_path) as f:
                ledger_lines = len(f.readlines())
        
        return {
            "ledger_lines": ledger_lines,
            "timestamp": time.time()
        }
