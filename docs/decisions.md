# Decision log

Every design choice, why it was made, and what the alternatives were. Newest decisions go at
the bottom of each milestone section. Format: **D#. Decision**, then *Why* and *Alternatives*.

---

## M1: Engine, strategies, tests

**D1. Python 3.12 in a virtualenv (`.venv/`), versions pinned in `requirements.txt`.**
*Why:* the PRD asks for 3.11+. The Mac's default Python is 3.14, which is very new; 3.12 is
the safest choice for numpy/pandas/matplotlib wheels. *Alternatives:* conda (heavier), system
Python (unpinned, not reproducible).

**D2. Moves are integers 0 = C, 1 = D.**
*Why:* given in the spec. It also makes two tricks possible: noise is `move ^ flip`
(XOR flips 0↔1), and the WSLS rule becomes `my_last ^ opp_last` (see D7).

**D3. Payoffs are a frozen dataclass that checks T > R > P > S and 2R > T + S on creation.**
*Why:* an invalid payoff set would silently produce meaningless results. The checks are the
definition of a Prisoner's Dilemma (PRD 4.1). Frozen = cannot be changed by accident.

**D4. `play_match` splits its rng into three independent child streams: noise, player 1,
player 2 (`Generator.spawn(3)`).**
*Why:* without this, a strategy that draws random numbers (GTFT, JOSS, RAND) would shift the
noise sequence, so comparing two strategies would compare different noise too. With separate
streams, GTFT(g=0) vs X produces **exactly** the same histories as TFT vs X, even with noise
(this is tested). Same seed → same match (PRD FR1.5).
*Alternatives:* one shared rng (simpler but breaks exact comparisons).

**D5. Noise for the whole match is drawn up front as one array.**
*Why:* one vectorised numpy call is far faster than one call per move. Measured speed:
0.43 µs per round, so the whole experiment suite fits the 30-minute budget without
Numba. *Alternative:* `rng.random()` per move (slower, same statistics).

**D6. `play_match` accepts a fixed `n_rounds`, and the tournament will use it.**
*Why:* the PRD says `n_rounds` is "used only in tests", but it also recommends common random
numbers (CRN): all pairings in one repetition should share the same game length. The cleanest
way to do that is for the tournament to draw the length once per repetition and pass it in.
When `n_rounds=None` the engine draws Geometric(1 − δ) itself, as FR1.2 requires.
This small deviation from the PRD wording serves the PRD's own advice.

**D7. WSLS is implemented as `next = my_last XOR opp_last`.**
*Why:* "win" (payoff R or T) happens exactly when the opponent cooperated. Win → keep my move;
lose → switch it. Checking the four cases: (C,C)→C, (D,C)→D, (C,D)→D, (D,D)→C. That is XOR.

**D8. Contrite TFT uses an operational "accept one punishment" rule.**
*Why:* the PRD defines CTFT as "TFT, but if its own D was a mistake, accept one punishment
without retaliating." A player always knows what it *intended*, so the strategy remembers its
last intended move and compares it with the move that was actually played. If it meant C but
played D, then in the round after next it plays C instead of retaliating against the
punishment it provoked.
*Alternatives:* Boyd's (1989) full "standing" bookkeeping (good/bad standing for each player).
In the one-error case it behaves the same, but it is harder to explain. The simplification is
written in the docstring.

**D9. TF2T defects only if the opponent's last two moves were both D; JOSS's sneak rate `p`
and GTFT's `g` are constructor parameters (defaults 0.1 and 1/3).**
*Why:* PRD FR2.2. Display names include the parameter, e.g. `GTFT(0.33)`, so results tables
are unambiguous.

**D10. All strategies open with C except STFT (D) and RAND (random).**
*Why:* follows the PRD rules. GTFT and CTFT are "TFT-like", so they open with C.

**D11. Benchmarks B1–B6 live only in `pd/theory.py`.**
*Why:* tests, plots and notes then use the same numbers, so theory and simulation can never
drift apart (PRD section 7).

**D12. Statistical test tolerances.**
*Why:* a statistical test must almost never fail by chance. Noise flip rate over 10⁶ moves
has standard error √(0.05·0.95/10⁶) ≈ 0.00022, so ±0.001 is about 4.5 SE. Game length uses
100,000 draws: SE ≈ 99.5/√100000 ≈ 0.31 rounds for δ = 0.99, well inside the 2 % (= 2 rounds)
band. All tests use fixed seeds, so they are also deterministic.

**D13. Predictions are written in `notes/predictions.md` and committed before any experiment
code runs.**
*Why:* the PRD says hypotheses come before simulations. The Git timestamp proves the order.

---

## M2: Tournament and E1

**D14. "Average payoff per round" = total payoff over all repetitions ÷ total rounds over
all repetitions (a ratio of sums), not the mean of each match's per-round average.**
*Why:* the theory benchmarks use the normalised discounted payoff (1−δ)·Σ δᵗ uₜ. Because
round t is reached with probability δᵗ and E[L] = 1/(1−δ), that is exactly
E[total payoff] / E[rounds]. The ratio of sums estimates this directly. A mean of per-match
averages weights a 2-round game as heavily as a 300-round game, so it overweights short
games. At δ = 0.99 the two differ only slightly, but at δ = 0.5 (E6) the mean of averages
would move the thresholds. Example: TFT vs ALLD has E[1 − 1/L], which is 0.31 at δ = 0.5,
against the theoretical δ = 0.5.
*Alternative:* mean of per-match averages (simpler, but biased against the theory).

**D15. 95 % CIs on tournament scores use a percentile bootstrap over repetitions (2,000
resamples).**
*Why:* the score is a ratio (D14), so the plain "mean ± 1.96·SE" formula does not apply
directly. Resampling whole repetitions keeps the common-random-number structure intact.
`analysis/stats.py` also has the normal-approximation `mean_ci` for plain means (used from
M3 on).

**D16. Common random numbers: one game length per repetition, shared by every pairing.**
*Why:* PRD 4.2. In repetition r every strategy plays games of the same length L_r, so a
difference between two strategies is never caused by one of them getting luckier game
lengths. (Implemented with `n_rounds`, see D6.)

**D17. Seeds for each pairing come from `SeedSequence(seed, spawn_key=(1, i, j)).spawn(n_reps)`.**
*Why:* `spawn_key` is the mechanism behind `SeedSequence.spawn` (PRD section 9). Keying by
the pairing's indices means a pairing's games do not depend on which other pairings were
played, or in what order. Adding a strategy at the end of the pool leaves every existing
match bit-for-bit identical (tested). That keeps E1 and E7 directly comparable.

**D18. A single tournament runs serially; parallelism (joblib) is applied across the
tournaments of a sweep (E2, E4, E6).**
*Why:* one 11-strategy tournament takes 0.2 s. Process start-up would cost more than it
saves. Sweeps run dozens of tournaments, which is where cores help (PRD FR5.4).

**D19. Experiments E1–E6 use the 11 known strategies (PRD 5.1 + 5.2); the originals join in
E7.**
*Why:* the PRD's E7 is "add originals to the pool; rerun E2, E5, E6". So the baseline pool
must exclude them, otherwise E7 would have nothing to compare against. GTFT in the pool uses
g = 1/3 (the PRD default).

**D20. Experiment code lives in `pd/experiments.py` (one function per experiment), with
configs in `configs/*.yaml`.**
*Why:* each experiment is about 10–30 lines, so one module is easier to read than an
`experiments/` package with seven tiny files. `run.py E1` finds `configs/e1_*.yaml`, copies
it into `results/E1/` and calls `experiments.e1`.

**D21. The ranking table also reports head-to-head wins and the cooperation rate.**
*Why:* RQ1 claims "ALLD wins head-to-head but scores low overall", which needs a head-to-head
count to test. Head-to-head win = A[i][j] > A[j][i].

**D22. Figure style: colour-blind-safe categorical palette in a fixed slot order (blue,
orange, aqua, …) and a single-hue blue ramp for heatmaps; captions state every parameter.**
*Why:* PRD 11.1 asks for colour-blind-safe figures with parameter captions. A single-hue ramp
reads light = low, dark = high without a legend lookup. In F2, colour encodes a property
(nice vs not nice) that the RQ1 argument depends on.

---

## M3–M5: Noise, echo, forgiveness dial, evolution, shadow of the future

**D23. Every point of a sweep uses the same base seed.**
*Why:* game lengths are then identical across ε (and across g in E4), and the noise
uniforms are the same random numbers compared against a different ε. Differences between
sweep points come from the parameter, not from luck: common random numbers across the
sweep.

**D24. Noise axes use a "symlog" scale: linear near 0, logarithmic above 0.005.**
*Why:* the PRD asks for a log x-axis, but ε = 0 (the no-noise baseline) cannot sit on a
log scale.

**D25. E3 also includes CTFT and GTFT self-play** (the PRD names TFT and WSLS).
*Why:* it costs under a second and shows which error-correcting mechanism is best (CTFT).

**D26. E4 replaces the pool's GTFT(1/3) with GTFT(g)** rather than adding a second GTFT.
*Why:* "GTFT(g) in the full pool" then means the same 11-strategy pool at every g, and the
GTFT slot keeps its index, so all opponents' matches use the same seeds across g (D17). A
second panel at δ = 0.9 shows how the optimum shifts in shorter games (PRD B5).

**D27. Replicator dynamics never zeroes small shares; 1e-6 is only the threshold for
*reporting* a strategy as extinct.**
*Why:* zeroing would change the dynamics and could hide a slow comeback. The PRD's
"shares below 1e-6 count as extinct" is applied to the survivor tables.

**D28. Extra evolution scenario `wsls_resident` (WSLS 99 %, ALLD 1 %) and an
invasion-threshold table in E5.**
*Why:* the PRD's B6 test ("rerun E5 with T = 4.5") needs a WSLS population to test whether
ALLD can invade it. In the uniform start WSLS is never resident, so the test would be
indirect. The threshold table (critical share from the 2×2 sub-matrix,
x* = (d−b)/((a−c)+(d−b))) turns the B3 and B6 arguments into numbers that can be checked.

**D29. E6 uses a finer δ grid (adds 0.45, 0.55, 0.65, 0.75, 0.85) and 30 independent seeds
per point.**
*Why:* the PRD's grid has only 0.5, 0.6 and 0.7 inside the predicted transition
[0.5, 0.667]. The PRD asks for means and CIs over ≥ 30 runs, so each point repeats the whole
pipeline (tournament + evolution) with 30 different seeds. Each run starts from a uniform
population (the PRD does not specify; uniform is its default). 2,000 generations, because
short games converge more slowly.

## M6: Originals and robustness

**D30. Original strategy designs** (full rationale in each docstring):
- *AF*: forgiveness g = ½·(surprise Ds + 1)/(all Ds + 2). The PRD's idea ("estimate the
  noise rate, set forgiveness to match") needs an observable proxy. The share of the
  opponent's defections that came "out of nowhere" after mutual cooperation is one. The cap
  ½ is B5's anti-ALLD bound; the +1/+2 prior starts at "half accidental".
- *GWA*: k = 5, m = 3 as in the prompt. Punishment blocks are re-evaluated every k rounds.
- *PF*: "never retaliated" = no D in rounds 3–4 (the replies to the round-2 probe).
  Exploitation stops the first time the victim defects.
- *REP*: α = 0.2 and threshold 0.5 as in the prompt; reputation starts at 1 (trust).

**D31. The originals are appended after the 11 known strategies in E7's pool.**
*Why:* with index-keyed seeds (D17), every match between known strategies in E7 is
identical to E2, so differences come only from adding the originals.

**D32. RQ7 predictions were committed (d1ba747) after the originals' unit tests passed but
before E7 ran.**
*Why:* the PRD requires predictions before testing. Unit tests only check rules on scripted
opponents and say nothing about performance.

**D33. T = 5.9 instead of the PRD's T = 6 in the payoff robustness check.**
*Why:* with R = 3 and S = 0, T = 6 gives 2R = T + S. That violates the strict PD condition
2R > T + S, and `Payoffs` rejects it. T = 5.9 is the closest valid value and still tests
"stronger temptation". R2's results show why the condition matters: at T = 5.9 alternation
pays (T+S)/2 = 2.95 ≈ R, and half-cooperative alternating populations appear.

**D34. Robustness pools.** *Nice only:* the 7 nice known strategies. *Many exploiters:*
6 exploiters (ALLD, STFT, RAND, JOSS at 10/30/50 % sneak rates) vs 5 reciprocators, using
parameter variants instead of duplicates so labels stay unique. *Random 8:* drawn
reproducibly with `default_rng(7)` from the 11 known strategies.

**D35. Not done (PRD stretch goals):** Moran process, perception noise, Zero-Determinant
strategy, mutation, dashboard.
*Why:* the core experiments, originals and two robustness checks came first, as the PRD
requires. These are the natural next steps; see `report/outline.md` → Limitations.

## M7: Reproducibility

**D36. Figures are saved without a PDF creation timestamp.**
*Why:* with the timestamp, re-running `make_figures.py` changed every PDF even though
nothing else changed. Now the whole pipeline is byte-for-byte reproducible. Verified: a
clean `python run.py all` reproduced every file in `results/` exactly (117 s on an Apple M3,
8 cores).

**D37. Ruff rule C408 (`dict(a=1)` → `{"a": 1}`) is disabled.**
*Why:* keyword-style `dict(...)` reads better in the many result-row constructions. A
style preference, not a correctness issue.
