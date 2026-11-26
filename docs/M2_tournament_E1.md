# M2: Tournament and E1 (baseline, no noise)

**Status:** done. 34/34 tests pass (6 new tournament tests). E1 runs in 0.2 s. F1 and F2
are produced.

## What was built

| File | What it does |
|------|--------------|
| `pd/tournament.py` | `run_tournament(pool, payoffs, delta, epsilon, n_reps, seed)` plays the round-robin with self-play. `TournamentResult` holds raw per-repetition totals and computes `payoff_matrix`, `coop_matrix`, `ranking()` and `matches()`. |
| `analysis/stats.py` | `mean_ci` (normal 95 % CI) and `bootstrap_ratio_ci` (bootstrap CI for a ratio of sums). |
| `pd/experiments.py` | One function per experiment (so far `e1`) plus `save_tournament` (CSV + Markdown). |
| `run.py` | `python run.py E1` / `python run.py all`. Reads `configs/e1_baseline.yaml`, writes `results/E1/` with a copy of the config. |
| `configs/e1_baseline.yaml` | Pool, payoffs, δ = 0.99, ε = 0, 50 reps, seed 42. |
| `analysis/make_figures.py` | Reads saved results only and draws F1 and F2 (PNG + PDF). |
| `tests/test_tournament.py` | Exact matrix values without noise, ranking, reproducibility, CRN, CIs. |

## How the tournament works

```
lengths = one Geometric(1-δ) length per repetition         # common random numbers
for every pair (i, j) with i ≤ j:                           # 11·12/2 = 66 pairings
    for each repetition r:                                  # own seed per (i, j, r)
        play_match(fresh i, fresh j, n_rounds = lengths[r])
        store totals and cooperation counts
A[i, j] = Σ_r total_ij / Σ_r L_r                            # average payoff per round
score_i = mean_j A[i, j]                                    # vs the whole pool, self included
CI      = bootstrap over repetitions
```

**Why "Σ total / Σ rounds"?** (decision D14) It equals the expected discounted payoff the
theory uses, so simulation and theory measure the same thing. Averaging per-match averages
would overweight short games.

**Why self-play?** In evolution, a strategy that is common mostly meets its own kind. A[i, i]
is what a population of i earns.

## Results

The full table and explanation are in `notes/findings.md` (E1 section). Key points:

1. **All 7 nice strategies beat all 4 non-nice ones.** Axelrod's main result is reproduced.
2. **ALLD wins 9 of its 10 head-to-head matches and still comes last** (1.88). TFT wins none
   and comes 4th (2.56).
3. **TF2T (2.67) and GTFT (2.65) beat TFT** because JOSS's random defections and STFT's
   opening D trigger TFT's echo. Forgiveness already pays without noise once the pool
   contains "noisy" strategies.

## Reading the figures

- **F1 (heatmap):** rows are sorted by rank. The top-left block of 3.00s is the "club of
  nice strategies": they all cooperate fully with each other. The rankings are decided in
  the right-hand columns (RAND, STFT, JOSS, ALLD), i.e. how a strategy handles difficult
  opponents. Compare the TFT row (1.41 vs JOSS) with the TF2T row (2.60 vs JOSS).
- **F2 (bars):** the blue/orange split is clean: nice strategies on top. CIs are narrow
  because there is no noise. The only randomness comes from game lengths, RAND and JOSS.

## Presentation talking points

- "TFT never beats anyone, yet does well; ALLD beats everyone, yet comes last." This is the
  core paradox of the repeated PD.
- "Even with zero noise, forgiveness already helps. JOSS behaves like a noisy player, and
  TFT's strict retaliation turns each of its sneaky defections into an echo."
- "Rankings depend on the pool. With few exploiters, even ALLC places 3rd. We test this in
  the robustness checks."
