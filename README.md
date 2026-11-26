# Does Forgiveness Pay? Cooperation in the Repeated Prisoner's Dilemma under Noise and Evolution

A Python simulator of the repeated Prisoner's Dilemma with implementation noise, round-robin
tournaments and replicator dynamics. It tests one claim: **under noise, forgiving strategies
beat unforgiving ones, and the right amount of forgiveness depends on the noise rate ε and
the shadow of the future δ.** Every headline result is compared against an analytic
benchmark (B1–B6).

**Short answer** (details in `notes/findings.md`): yes, when mistakes are rare but present
(ε ≈ 0.005–0.05), in moderate doses (forgive about 15–35 % of defections, never more than
half). Under evolution the winning kind is *contrition* (Contrite TFT) rather than
generosity. Nothing works unless δ is above about 0.5–0.67.

## Setup

```bash
python3.12 -m venv .venv            # Python 3.11+ works
.venv/bin/pip install -r requirements.txt
.venv/bin/pytest -q                 # 54 tests, all must pass
```

## Reproduce everything (about 2 minutes on a laptop)

```bash
.venv/bin/python run.py all && .venv/bin/python analysis/make_figures.py
```

Every run is seeded; re-running gives byte-identical `results/` and `figures/`.

## Run one experiment

| Command | What it does | Figures |
|---|---|---|
| `python run.py E1` | Baseline tournament, no noise | F1 payoff matrix, F2 ranking |
| `python run.py E2` | Noise sweep ε ∈ {0 … 0.2} | F3 score vs ε |
| `python run.py E3` | Echo effect: self-play in 2,000-round matches | F4 vs B4, F5 move traces |
| `python run.py E4` | Forgiveness dial: GTFT(g) over (g, ε, δ) | F6 heatmap, F6b exploitation |
| `python run.py E5` | Replicator dynamics, 4 starting populations, T = 5 and 4.5 | F7 shares, F7b B6 test |
| `python run.py E6` | Shadow of the future: equilibrium cooperation vs δ | F8 vs B1/B2 |
| `python run.py E7` | Original strategies added; reruns E2, E5, E6 | F9 niche map, F9b |
| `python run.py R1` | Robustness: three other strategy pools | F11 |
| `python run.py R2` | Robustness: payoffs T = 4.5 and 5.9 | F10 |

Then `python analysis/make_figures.py` redraws the figures from the saved results (it never
re-simulates). Each experiment's parameters live in `configs/<id>_*.yaml`, and a copy is
saved next to its results.

## Folder layout

```
run.py                 python run.py E2 | all
configs/               one YAML per experiment (pool, payoffs, δ, ε, reps, seed)
pd/
  game.py              Payoffs, play_match (geometric length, implementation noise)
  strategies/
    base.py            Strategy interface + registry: make("GTFT", g=0.2)
    classic.py         ALLC, ALLD, RAND, TFT, GRIM
    forgiving.py       GTFT, TF2T, WSLS, STFT, CTFT, JOSS
    original.py        AF, GWA, PF, REP (+ a template for your own)
  tournament.py        round-robin → payoff matrix, cooperation matrix, ranking with CIs
  evolution.py         replicator dynamics, initial populations
  theory.py            benchmark formulas B1–B6 and invasion thresholds
  experiments.py       E1–E7, R1–R2
analysis/
  make_figures.py      all figures (reads results/ only)
  stats.py             normal and bootstrap confidence intervals
tests/                 54 pytest tests with exactly known answers
results/<ID>/          raw CSVs + Markdown summaries + config copy
figures/               F1–F11 as PNG and PDF
notes/                 predictions.md (written before experiments), findings.md
docs/                  study folder: PRD, decisions, derivations, milestone notes, Q&A, slides
report/
  report.md            the written report (source; edit this)
  report.pdf           built report (A4, 15 pages + appendices)
  report.docx          the same report as an editable Word file
  build_report.py      report.md → report.pdf (needs Google Chrome)
  build_docx.js        → report.docx (needs Node and `npm install docx`)
  outline.md           report structure
```

## Rebuild the report after editing `report/report.md`

```bash
.venv/bin/python report/build_report.py   # writes report.pdf
node report/build_docx.js                 # writes report.docx (after `npm install docx` once)
```


## Add a new strategy

1. Open `pd/strategies/original.py` and copy the **TODO template** at the bottom:
   ```python
   @register
   class MyStrategy(Strategy):
       """My Strategy. Source: original. Rule: ... Intuition: ... Predicted niche: ..."""
       code = "MINE"
       def reset(self, rng):
           super().reset(rng)            # clear memory here
       def move(self, my_hist, opp_hist):
           return C                      # 0 = C, 1 = D; you see actual moves only
   ```
   Parameters go in `__init__` (see `AdaptiveForgiver`). Use `self.rng` for randomness.
2. Write its predicted niche in `notes/predictions.md` **before** running anything.
3. Add a test with an exactly known answer in `tests/test_originals.py` and run `pytest`.
4. Add `MINE` (or `{code: MINE, my_param: 0.3}`) to the pool in `configs/e7_originals.yaml`.
5. `python run.py E7 && python analysis/make_figures.py`

## Conventions

Moves: 0 = C, 1 = D. Strategies return their *intended* move; the engine applies noise, and
both histories record actual moves. "Payoff per round" = total payoff ÷ total rounds over
all repetitions (equals the discounted payoff the theory uses). CIs are 95 %. Formatted with
`black`, linted with `ruff`.

## Study material

Start at `docs/README.md`.
