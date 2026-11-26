# Does Forgiveness Pay? Cooperation in the Repeated Prisoner's Dilemma under Noise and Evolution

A Python simulator of the repeated Prisoner's Dilemma with implementation noise, round-robin
tournaments and evolutionary dynamics. It tests whether forgiving strategies beat unforgiving
ones under noise, and how much forgiveness is best.

> Work in progress: milestones M1 (engine, strategies, tests) and M2 (tournament, E1) are complete. The full README
> (how to run every experiment, how to add a strategy) is written at milestone M7.

## Setup

```bash
python3.12 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/pytest -q          # all tests must pass
.venv/bin/python run.py E1   # run an experiment (or: all)
.venv/bin/python analysis/make_figures.py
```

## Where things are

- `pd/`: the simulator (engine, strategies, tournament, experiments, theory benchmarks)
- `configs/`: one YAML per experiment; `results/`: raw CSVs; `figures/`: PNG + PDF
- `analysis/`: statistics and figure making (reads saved results only)
- `tests/`: pytest suite with exactly known answers
- `docs/`: **study folder**: decisions, derivations, milestone write-ups, presentation Q&A
- `notes/`: predictions (written before experiments) and findings
