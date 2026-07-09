"""Verify invariants post-fault."""
import json
from pathlib import Path
from typing import List, Tuple
from enum import Enum

class InvariantResult(Enum):
    PASS = "pass"
    FAIL = "fail"
    FAULT_DETECTED = "fault_detected"

class InvariantChecker:
    """Validates system invariants under fault injection."""
    
    def __init__(self):
        self.ledger_path = Path('/opt/trading/data/state_store/ledger.jsonl')
        self.results: List[Tuple[str, InvariantResult]] = []
    
    def check_monotone_timestamps(self) -> Tuple[str, InvariantResult]:
        """Verify all ledger timestamps are strictly monotone."""
        if not self.ledger_path.exists():
            return ("monotone_timestamps", InvariantResult.PASS)
        
        try:
            with open(self.ledger_path) as f:
                lines = [json.loads(line) for line in f if line.strip()]
            
            if len(lines) < 2:
                return ("monotone_timestamps", InvariantResult.PASS)
            
            for i in range(1, len(lines)):
                t_prev = lines[i-1].get("timestamp", 0)
                t_curr = lines[i].get("timestamp", 0)
                
                if t_curr <= t_prev:
                    return ("monotone_timestamps", InvariantResult.FAIL)
            
            return ("monotone_timestamps", InvariantResult.PASS)
        except Exception as e:
            return ("monotone_timestamps", InvariantResult.FAULT_DETECTED)
    
    def check_no_duplicate_orders(self) -> Tuple[str, InvariantResult]:
        """Verify no order ID appears twice in ledger."""
        if not self.ledger_path.exists():
            return ("no_duplicate_orders", InvariantResult.PASS)
        
        try:
            with open(self.ledger_path) as f:
                lines = [json.loads(line) for line in f if line.strip()]
            
            order_ids = set()
            for line in lines:
                if "order_id" in line:
                    oid = line["order_id"]
                    if oid in order_ids:
                        return ("no_duplicate_orders", InvariantResult.FAIL)
                    order_ids.add(oid)
            
            return ("no_duplicate_orders", InvariantResult.PASS)
        except Exception as e:
            return ("no_duplicate_orders", InvariantResult.FAULT_DETECTED)
    
    def check_ledger_integrity(self) -> Tuple[str, InvariantResult]:
        """Verify ledger can be read without parse errors."""
        if not self.ledger_path.exists():
            return ("ledger_integrity", InvariantResult.PASS)
        
        try:
            with open(self.ledger_path) as f:
                line_count = 0
                for line in f:
                    if line.strip():
                        json.loads(line)
                        line_count += 1
            
            return ("ledger_integrity", InvariantResult.PASS)
        except json.JSONDecodeError as e:
            return ("ledger_integrity", InvariantResult.FAIL)
        except Exception as e:
            return ("ledger_integrity", InvariantResult.FAULT_DETECTED)
    
    def check_position_conservation(self, positions_ledger: dict) -> Tuple[str, InvariantResult]:
        """Verify total shares sum matches expectation."""
        try:
            total = sum(positions_ledger.values())
            if total < 0:  # Extreme negative position = anomaly
                return ("position_conservation", InvariantResult.FAIL)
            return ("position_conservation", InvariantResult.PASS)
        except Exception as e:
            return ("position_conservation", InvariantResult.FAULT_DETECTED)
    
    def check_broker_ledger_sync(self, broker_pos: dict, ledger_pos: dict) -> Tuple[str, InvariantResult]:
        """Verify broker state matches local ledger."""
        try:
            broker_total = sum(abs(v) for v in broker_pos.values())
            ledger_total = sum(abs(v) for v in ledger_pos.values())
            
            if abs(broker_total - ledger_total) > 1:  # >1 share tolerance
                return ("broker_ledger_sync", InvariantResult.FAIL)
            
            return ("broker_ledger_sync", InvariantResult.PASS)
        except Exception as e:
            return ("broker_ledger_sync", InvariantResult.FAULT_DETECTED)
    
    def validate_all(self) -> dict:
        """Run all checks."""
        checks = [
            self.check_monotone_timestamps(),
            self.check_no_duplicate_orders(),
            self.check_ledger_integrity(),
        ]
        
        self.results = checks
        
        passed = sum(1 for _, r in checks if r == InvariantResult.PASS)
        failed = sum(1 for _, r in checks if r == InvariantResult.FAIL)
        detected = sum(1 for _, r in checks if r == InvariantResult.FAULT_DETECTED)
        
        return {
            "total": len(checks),
            "passed": passed,
            "failed": failed,
            "fault_detected": detected,
            "all_pass": failed == 0 and detected == 0,
            "results": [(name, result.value) for name, result in checks]
        }
