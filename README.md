# Does Forgiveness Pay? Cooperation in the Repeated Prisoner's Dilemma under Noise and Evolution

A Python simulator of the repeated Prisoner's Dilemma with implementation noise, round-robin
tournaments and evolutionary dynamics. It tests whether forgiving strategies beat unforgiving
ones under noise, and how much forgiveness is best.

> Work in progress: milestone M1 (engine, strategies, tests) is complete. The full README
> (how to run every experiment, how to add a strategy) is written at milestone M7.

## Setup

```bash
python3.12 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/pytest -q          # all tests must pass
```

## Where things are

- `pd/`: the simulator (engine, strategies, theory benchmarks)
- `tests/`: pytest suite with exactly known answers
- `docs/`: **study folder**: decisions, derivations, milestone write-ups, presentation Q&A
- `notes/`: predictions (written before experiments) and findings
