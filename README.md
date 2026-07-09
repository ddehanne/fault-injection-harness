# Fault Injection Deterministic Harness

## Overview

Deterministic fault-injection harness for validating trading-infrastructure invariants under controlled failure scenarios.

The harness is designed to test operational safeguards around:

- single-writer execution;
- broker-state reconciliation;
- append-only ledger integrity;
- duplicate-order prevention;
- controlled recovery after failure.

It validates selected infrastructure invariants, including:

- `INFRA-002`: single-writer execution guard;
- `INFRA-003`: broker reconciliation gate.

**Purpose:** provide reproducible technical evidence that specific failure modes are detected, bounded, and handled without corrupting local state or generating duplicate paper orders.

This harness is used for IBKR paper-environment validation. It does not demonstrate live-capital readiness, real-money execution quality, or production-grade reliability.

---

## Architecture

```text
System Under Test
        │
        ▼
Fault Injector
├── FAULT-01: SIGKILL during ledger write
├── FAULT-02: Broker disconnect
├── FAULT-03: Concurrent instance race
├── FAULT-04: Phantom position anomaly
└── FAULT-05: Clock skew
        │
        ▼
Invariant Checker
├── Monotone timestamps
├── No duplicate paper orders
├── Ledger integrity
├── Position-state consistency
└── Broker-ledger reconciliation
        │
        ▼
Test Results + Coverage Report
```

---

## Fault Classes

### FAULT-01: SIGKILL During Ledger Write

**Scenario:** Process termination during ledger persistence, such as a forced kill, timeout, or host-level interruption.

**Injection:** Truncate `ledger.jsonl` with an incomplete JSON line.

**Invariant:** Recovery detects the corrupted line, rejects it, and restores state to the last valid checkpoint.

**Expected result:** Ledger corruption is detected and bounded. Historical valid entries are preserved.

**Test:** `test_fault_01_ledger_recovery.py`

```bash
make test-fault -k "fault_01"
```

---

### FAULT-02: Broker Disconnect During Rebalance

**Scenario:** IBKR connection drops during broker-state read or paper-order submission.

**Injection:** Block or interrupt the broker connection for a controlled time window.

**Invariant:** The system retries within bounded limits and does not generate duplicate paper orders.

**Expected result:** Broker-state reconciliation validates local state after reconnect.

**Test:** `test_fault_02_broker_disconnect.py`

```bash
make test-fault -k "fault_02"
```

---

### FAULT-03: Double Instance Concurrent Start

**Scenario:** A restart race attempts to start two execution instances concurrently.

**Injection:** Trigger two start commands within a short time window.

**Invariant:** The single-writer guard allows only one execution instance to acquire the session lock.

**Expected result:** The second instance exits cleanly without writing to the ledger or submitting paper orders.

**Test:** `test_fault_03_concurrent_start.py`

```bash
make test-fault -k "fault_03"
```

---

### FAULT-04: Phantom Position Anomaly

**Scenario:** Broker-reported position differs from local ledger-derived state.

**Injection:** Inject a symbol or quantity mismatch into the broker-state fixture.

**Invariant:** The reconciliation gate detects divergence and blocks new paper-order submission until the discrepancy is handled.

**Expected result:** Execution is halted or blocked, state is preserved, and a reconciliation event is recorded.

**Test:** `test_fault_04_phantom_position.py`

```bash
make test-fault -k "fault_04"
```

---

### FAULT-05: Clock Skew

**Scenario:** System clock jumps during an execution or reconciliation cycle.

**Injection:** Simulate a forward clock offset during the test.

**Invariant:** Ledger ordering remains monotonic through logical sequencing or timestamp validation.

**Expected result:** No backward causality appears in the ledger or decision log.

**Test:** `test_fault_05_clock_skew.py`

```bash
make test-fault -k "fault_05"
```

---

## Invariant Checks

### Core Invariants

1. **Monotone Timestamps**  
   Ledger entries preserve event ordering.

2. **No Duplicate Paper Orders**  
   No order ID is emitted twice for the same intended action.

3. **Ledger Integrity**  
   Ledger entries remain valid JSON or are rejected during recovery.

4. **Position-State Consistency**  
   Local state and broker-reported state are compared during reconciliation.

5. **Broker-Ledger Reconciliation**  
   Divergence is detected and escalated before further paper-order submission.

---

## Running Checks

```python
from harness.invariant_checker import InvariantChecker

checker = InvariantChecker()
summary = checker.validate_all()
print(summary)
```

Example output:

```json
{
  "total": 5,
  "passed": 5,
  "failed": 0,
  "all_pass": true
}
```

---

## Quick Start

### Install Dependencies

```bash
make install
```

### Run All Tests

```bash
make test
```

Example output:

```text
tests/test_fault_01_ledger_recovery.py::test_fault_01_ledger_recovery PASSED
tests/test_fault_02_broker_disconnect.py::test_fault_02_broker_disconnect_recovery PASSED
tests/test_fault_03_concurrent_start.py::test_fault_03_concurrent_start_lock PASSED
tests/test_fault_04_phantom_position.py::test_fault_04_phantom_position_detection PASSED
tests/test_fault_05_clock_skew.py::test_fault_05_clock_skew_monotone PASSED
===== 5 passed in 3.24s =====
```

### Run Only Fault Tests

```bash
make test-fault
```

### Generate Coverage Report

```bash
make coverage
```

---

## Files Included

```text
/opt/trading/fault-injection/
├── README.md                    [Full documentation]
├── PRESENTATION.md              [Short project overview]
├── Makefile                     [Easy test execution]
├── pytest.ini                   [pytest configuration]
├── requirements-test.txt        [Dependencies]
├── .github/workflows/test.yml   [CI/CD stub]
├── harness/
│   ├── __init__.py
│   ├── chaos_monkey.py
│   └── invariant_checker.py
├── tests/
│   ├── __init__.py
│   ├── test_fault_01_ledger_recovery.py
│   ├── test_fault_02_broker_disconnect.py
│   ├── test_fault_03_concurrent_start.py
│   ├── test_fault_04_phantom_position.py
│   └── test_fault_05_clock_skew.py
├── htmlcov/
│   └── index.html
└── reports/
    └── pytest.log
```

---

## Design Principles

1. **Deterministic fault injection**  
   Faults are reproducible and measurable rather than random.

2. **Invariant-based validation**  
   Pass/fail criteria are based on operational invariants, not implementation convenience.

3. **Failure containment**  
   Failure states should block further execution rather than silently continue.

4. **Append-only audit trail**  
   Recovery and reconciliation actions are represented as new events rather than historical rewrites.

5. **Paper-environment discipline**  
   The harness validates operational behavior in a paper-trading context and does not claim live-capital readiness.

---

## CI/CD Integration

GitHub Actions stub:

```yaml
name: Fault Injection Tests

on:
  push:
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.10"

      - run: make install
      - run: make test-fault
      - run: make coverage
```

---

## Roadmap

- [x] INFRA-002: single-writer lock validation
- [x] INFRA-003: broker reconciliation gate
- [ ] Expanded broker-disconnect scenarios
- [ ] Partial-fill and stale-order scenarios
- [ ] Public test artifact cleanup
- [ ] Monitoring hooks for fault-detection metrics

---

## References

- `live_loop.py` — system under test
- `ledger.jsonl` — append-only event log
- `executor_positions.json` — local position state
- `ibkr_positions_live.json` — broker-side state fixture
- `docs/PM-015-INCIDENT.md` — incident analysis

---

## Date

2026-07-09

---

## Validation Status

Current status: validated in the current test harness.

The harness provides evidence for selected operational invariants under controlled paper-environment failure scenarios. It does not prove production readiness, institutional capacity, or live-capital safety.

---

# PRESENTATION.md

# Fault Injection Deterministic Harness

## Summary

This module is a deterministic fault-injection harness used to validate selected operational invariants in the QS1-XSMR paper-environment infrastructure.

It focuses on failure scenarios that can compromise trading-system integrity:

- process death during ledger persistence;
- broker disconnects;
- duplicate execution instances;
- broker/local state divergence;
- clock skew and event-ordering issues.

The goal is not to claim production readiness. The goal is to show that specific operational failure modes are reproducible, detectable, bounded, and tested against explicit invariants.

---

## Validated Infrastructure Invariants

- `INFRA-002`: single-writer execution guard
- `INFRA-003`: broker reconciliation gate
- append-only ledger integrity
- duplicate paper-order prevention
- monotonic event ordering
- controlled reconciliation after divergence

---

## Fault Scenarios

| Fault | Scenario | Main Invariant |
|---|---|---|
| FAULT-01 | SIGKILL during ledger write | Ledger corruption is detected and bounded |
| FAULT-02 | Broker disconnect | No duplicate paper orders after reconnect |
| FAULT-03 | Concurrent instance race | Only one writer can control execution |
| FAULT-04 | Phantom broker position | Divergence blocks further execution |
| FAULT-05 | Clock skew | Ledger ordering remains monotonic |

---

## Architecture

```text
System Under Test
        │
        ▼
Fault Injector
        │
        ▼
Invariant Checker
        │
        ▼
Test Results + Coverage Report
```

---

## Files Included

```text
/opt/trading/fault-injection/
├── README.md                    [Full documentation]
├── PRESENTATION.md              [Short project overview]
├── Makefile                     [Easy test execution]
├── pytest.ini                   [pytest configuration]
├── requirements-test.txt        [Dependencies]
├── .github/workflows/test.yml   [CI/CD stub]
├── harness/
│   ├── __init__.py
│   ├── chaos_monkey.py
│   └── invariant_checker.py
├── tests/
│   ├── __init__.py
│   ├── test_fault_01_ledger_recovery.py
│   ├── test_fault_02_broker_disconnect.py
│   ├── test_fault_03_concurrent_start.py
│   ├── test_fault_04_phantom_position.py
│   └── test_fault_05_clock_skew.py
├── htmlcov/
│   └── index.html
└── reports/
    └── pytest.log
```

---

## Test Execution

```bash
make install
make test
make test-fault
make coverage
```

Example result:

```text
===== 5 passed in 3.24s =====
```

---

## Design Principle

The harness uses deterministic chaos rather than random chaos.

Each fault is intentionally constructed, replayable, and judged against a specific invariant. This makes the test output useful for debugging, regression testing, and operational hardening.

---

## Limitations

This harness validates selected failure modes in a paper-environment context.

It does not prove:

- live-capital readiness;
- real-money execution quality;
- production-grade reliability;
- institutional capacity;
- absence of undiscovered failure modes.

---

## Date

2026-07-09
