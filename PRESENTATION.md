# Fault Injection Harness — Technical Presentation

## Executive Summary

**Problem:** Trading infrastructure can fail through process crashes, broker disconnects, duplicate execution instances, state divergence, or timestamp anomalies.

**Solution:** A deterministic fault-injection harness that validates selected operational invariants under five controlled failure scenarios.

**Result:** Five reproducible tests validate core safeguards around ledger integrity, duplicate-order prevention, single-writer execution, broker-state reconciliation, and monotonic event ordering.

This harness is used for QS1-XSMR paper-environment validation. It does not claim production readiness, live-capital safety, institutional capacity, or real-money execution quality.

---

## The Problem

During QS1-XSMR operational testing, prior incidents and maintenance work highlighted two critical infrastructure risks:

- **INFRA-002:** single-writer execution guard  
  Prevents concurrent execution instances from writing to the ledger or submitting orders.

- **INFRA-003:** broker reconciliation gate  
  Detects divergence between local state and broker-reported state before further execution.

Traditional unit tests are not sufficient for these failure modes. The system also needs deterministic failure scenarios that reproduce operational faults and validate explicit invariants.

---

## Five Failure Modes

| Fault | Scenario | Main Detection / Control |
|---|---|---|
| FAULT-01 | SIGKILL during ledger write | Corrupted JSON detection and recovery to last valid checkpoint |
| FAULT-02 | Broker disconnect | Bounded retry behavior and duplicate-order prevention |
| FAULT-03 | Concurrent instance race | Single-writer lock prevents overlapping execution writers |
| FAULT-04 | Phantom broker position | Broker-ledger divergence detected and execution blocked |
| FAULT-05 | Clock skew | Monotonic event-order validation |

---

## Invariant Checks

Every fault scenario is validated against operational invariants.

1. **Monotone timestamps**  
   Ledger event ordering must preserve causality.

2. **No duplicate paper orders**  
   No order ID should be emitted twice for the same intended action.

3. **Ledger integrity**  
   Ledger entries must remain valid JSON or be rejected during recovery.

4. **Position-state consistency**  
   Local state and broker-reported state must be compared during reconciliation.

5. **Broker-ledger reconciliation**  
   Divergence must be detected and escalated before further paper-order submission.

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

## Implementation Metrics

```text
Test count:        5 deterministic fault tests
Total code size:   491 lines
Code coverage:     66%
Test runtime:      ~3.7 seconds
Result:            all current tests passing
```

Coverage is treated as a supporting diagnostic, not a standalone quality claim. The harness prioritizes critical-path validation over vanity coverage metrics.

---

## Why This Matters

The harness provides technical evidence that selected operational failure modes are:

- reproducible;
- detectable;
- bounded;
- validated against explicit invariants;
- useful for regression testing and operational hardening.

It is designed to support engineering discipline around trading infrastructure, not to market live-capital readiness.

---

## Running the Tests

```bash
cd /opt/trading/fault-injection

# Install dependencies
make install

# Run all tests
make test

# Run only fault tests
make test-fault

# Generate coverage report
make coverage
```

Example output:

```text
tests/test_fault_01_ledger_recovery.py::test_fault_01_ledger_recovery PASSED        [ 20%]
tests/test_fault_02_broker_disconnect.py::test_fault_02_broker_disconnect_recovery PASSED     [ 40%]
tests/test_fault_03_concurrent_start.py::test_fault_03_concurrent_start_lock PASSED           [ 60%]
tests/test_fault_04_phantom_position.py::test_fault_04_phantom_position_detection PASSED      [ 80%]
tests/test_fault_05_clock_skew.py::test_fault_05_clock_skew_monotone PASSED                   [100%]
===== 5 passed in 3.74s =====
```

---

## Files Included

```text
/opt/trading/fault-injection/
├── README.md                    [Full documentation]
├── PRESENTATION.md              [This file]
├── Makefile                     [Easy test execution]
├── pytest.ini                   [pytest configuration]
├── requirements-test.txt        [Dependencies]
├── .github/workflows/test.yml   [CI/CD stub]
├── harness/
│   ├── __init__.py
│   ├── chaos_monkey.py          [166 lines, 91% coverage]
│   └── invariant_checker.py     [126 lines, 36% coverage*]
├── tests/
│   ├── __init__.py
│   ├── test_fault_01_ledger_recovery.py
│   ├── test_fault_02_broker_disconnect.py
│   ├── test_fault_03_concurrent_start.py
│   ├── test_fault_04_phantom_position.py
│   └── test_fault_05_clock_skew.py
├── htmlcov/
│   └── index.html               [Coverage report]
└── reports/
    └── pytest.log               [Test execution log]
```

\* Lower coverage on `invariant_checker.py` reflects defensive branches and edge cases that are not all exercised in the current public test set. The current validation focuses on critical paths across the five deterministic fault scenarios.

---

## Technical Notes

### INFRA-002 — Single-Writer Execution Guard

FAULT-03 validates that concurrent execution attempts do not create overlapping writers.

Expected behavior:

- one execution instance acquires the session lock;
- the second instance exits or blocks cleanly;
- no interleaved ledger writes occur;
- no duplicate paper orders are submitted.

### INFRA-003 — Broker Reconciliation Gate

FAULT-02 and FAULT-04 validate broker-state divergence handling.

Expected behavior:

- broker disconnects do not produce duplicate paper orders;
- broker/local state mismatches are detected;
- execution is blocked or halted when divergence is unresolved;
- reconciliation events are appended rather than rewriting history.

---

## Design Principles

1. **Deterministic fault injection**  
   Faults are intentional, reproducible, and measurable.

2. **Invariant-based validation**  
   Pass/fail criteria are tied to operational rules, not implementation convenience.

3. **Failure containment**  
   Uncertain or divergent states should block further execution rather than silently continue.

4. **Append-only audit trail**  
   Corrections and reconciliation actions are represented as new events.

5. **Paper-environment discipline**  
   The harness validates behavior in a paper-trading context and does not claim live-capital readiness.

---

## Limitations

This harness validates selected failure modes only.

It does not prove:

- production readiness;
- live-capital safety;
- real-money execution quality;
- institutional capacity;
- absence of undiscovered failure modes;
- correctness of the underlying trading strategy.

---

## Next Steps

1. Expand broker-disconnect scenarios.
2. Add partial-fill and stale-order failure cases.
3. Add exchange-calendar edge cases.
4. Improve public test artifacts and coverage reporting.
5. Integrate the harness as an acceptance test suite for future operational-hardening work.

---

## Date

2026-07-09

**Repository:** Public research repository  
**Tag:** `v0.1.0-harness`
