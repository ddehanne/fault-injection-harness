# Fault-Injection Harness — Offline Demonstration

This repository contains **isolated Python demonstrations**, not verified safeguards of a running trading system. The historical version described paper-trading infrastructure validation and included host-level commands. Those claims have been withdrawn for this public version.

## What is actually tested

| Case | Verifiable local property | NOT demonstrated |
| --- | --- | --- |
| FAULT-01 | Truncated JSONL is detected and earlier data remains | Actual SIGKILL recovery, durable writes |
| FAULT-02 | A minimal offline broker stub rejects requests and deduplicates retries | IBKR disconnection/reconnect, real executor behavior |
| FAULT-03 | A Python lock stub rejects a second concurrent holder | systemd, cross-process/single-writer enforcement |
| FAULT-04 | Synthetic broker/ledger symbol mismatch is detected | Production reconciliation and kill-switch activation |
| FAULT-05 | Backward/equal synthetic timestamps are rejected | NTP disruptions or production logical-clock recovery |

No tests contact a real broker, trading service or production ledger. All writes in the suite use pytest temporary paths. The corruption injector refuses non-temporary paths.

## Run locally

Python **3.10+** and `pytest` are required. In an isolated virtual environment:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-test.txt
.venv/bin/python -m pytest tests/ -q
```

This suite exercises **local simulations and checker logic only**. A passing result must not be interpreted as proof that the historical live/paper execution loop was safe, that real order submissions were deduplicated or that trading could resume safely after failure.

## Scope and next validation steps

To establish a real safety guarantee, integrate an explicit system-under-test adapter, collect evidence of broker acknowledgments, expose lock acquisition outcomes, test failure propagation to the order gate, and exercise each injected fault against that adapter in an isolated environment. None of those integration guarantees are established here.
