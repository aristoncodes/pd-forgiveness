# PRD: Does Forgiveness Pay? Repeated Prisoner's Dilemma Simulation

Nov 26, 2026 · @Anushka

*(Markdown transcription of the original PDF. This is the full spec; where the build prompt
and the PRD differ, the PRD wins. Deviations made during the build are logged in
`decisions.md`.)*

## 1. Overview

Build a Python simulator of the repeated Prisoner's Dilemma (PD) and use it to test one
claim: **under noise, forgiving strategies beat unforgiving ones, and the right amount of
forgiveness depends on the noise rate and the shadow of the future.**

**Track:** B (Computational / Simulation)

**What you are building:**

1. A game engine that plays two strategies against each other for a random number of
   rounds, with optional noise.
2. An Axelrod-style round-robin tournament between classic strategies, known forgiving
   strategies and 2–3 original strategies.
3. Evolutionary dynamics (replicator dynamics, optionally a Moran process) where strategy
   shares grow with success.
4. Parameter sweeps over noise (ε) and continuation probability (δ), with plots compared
   against game-theoretic predictions.

### Goals

- **G1.** Reproduce the classic Axelrod result (Tit-for-Tat does well with no noise) as a
  check that the code works.
- **G2.** Show quantitatively when and why forgiveness beats strict retaliation as noise
  rises.
- **G3.** Show which strategies survive evolution, and how that changes with ε and δ.
- **G4.** Match simulated cooperation thresholds against analytically derived ones.
- **G5.** Design original strategies and explain their success or failure with game theory.

### Success criteria

- Every headline result has a stated prediction, a figure, and an explanation of agreement
  or disagreement.
- At least one "theory vs. simulation" plot where a derived threshold is drawn on top of
  simulated data.
- All results are reproducible from one command with fixed seeds.
- Results report means with 95% confidence intervals over at least 30 independent runs.

## 2. Research questions and hypotheses

Each hypothesis is written before any simulation so the results can confirm or refute it.

| ID | Research question | Hypothesis / prediction | Tested in |
|----|-------------------|-------------------------|-----------|
| RQ1 | With no noise, which strategies win a round-robin tournament? | Nice, retaliating strategies (TFT, Grim) finish near the top; Always Defect wins head-to-head but scores low overall. | E1 |
| RQ2 | How does noise change rankings? | As ε rises, TFT and Grim fall; Generous TFT, Tit-for-Two-Tats and Win-Stay Lose-Shift overtake them. | E2 |
| RQ3 | What does noise do to TFT vs. TFT? | One error starts an echo of alternating retaliation; long-run average payoff drops from 3 toward 2.25. | E3 |
| RQ4 | How much forgiveness is optimal? | GTFT's best forgiveness probability g* is above 0 and near the theoretical 1/3 (section 4, B5); too much forgiveness invites exploitation by defectors. | E4 |
| RQ5 | Which strategies survive evolution? | With no noise, TFT-like strategies take over after defectors die out; with noise, WSLS or GTFT dominate; cycles (ALLC → ALLD → TFT) can appear. | E5 |
| RQ6 | How does δ (shadow of the future) affect cooperation? | Cooperation collapses below δ ≈ 0.5 and is stable above δ ≈ 0.67 (derived in section 4). | E6 |
| RQ7 | Do my original strategies beat known ones in any region of (ε, δ)? | Open question; each original strategy gets a stated design rationale and a predicted niche. | E7 |

## 3. Scope

### In scope (must have)

- Two-player repeated PD with a random game length set by δ.
- Implementation noise: each intended move is flipped with probability ε.
- 12–15 strategies (section 5), including 2–3 original ones.
- Round-robin tournament with self-play and repeated runs.
- Discrete-time replicator dynamics on the tournament payoff matrix.
- Sweeps over ε, δ and GTFT's forgiveness probability.
- Figures, a written report and a reproducible code repository.

### Stretch goals (if time allows)

- Moran process in a finite population (N = 50–200), compared with replicator dynamics.
- Perception noise (a player misreads the opponent's move) compared with implementation
  noise.
- A Zero-Determinant strategy (Press & Dyson, 2012), e.g. an extortioner.
- Mutation in the evolutionary model (small rate μ of random strategy switches).
- A small interactive dashboard to explore parameters.

### Out of scope

- More than two players per game (public goods games, n-player PD).
- Spatial or network-structured populations.
- Learning agents (Q-learning, neural networks).
- Asymmetric payoffs between players.

## 4. Game model and theory

The model uses standard Axelrod payoffs, a geometric game length and implementation noise;
six analytic benchmarks give predictions the simulation must match.

### 4.1 Stage game

|                    | Opponent cooperates (C) | Opponent defects (D) |
|--------------------|-------------------------|----------------------|
| **You cooperate (C)** | R = 3, 3 (Reward)    | S = 0, T = 5 (Sucker) |
| **You defect (D)**    | T = 5, S = 0 (Temptation) | P = 1, 1 (Punishment) |

A valid PD needs T > R > P > S and 2R > T + S (so taking turns exploiting each other is
worse than mutual cooperation). Payoffs must be configurable, with these as defaults.

### 4.2 Repetition and the shadow of the future

After each round, the game continues with probability δ and ends with probability 1 − δ.
The number of rounds is geometric with mean

E[rounds] = 1 / (1 − δ)

So δ = 0.9 gives 10 rounds on average and δ = 0.99 gives 100. Do not use a fixed, known
number of rounds: by backward induction, defecting in every round is then the only
equilibrium. Always report **average payoff per round**, so games of different lengths are
comparable.

*Implementation tip:* draw the game length once per match from a geometric distribution,
and use the same lengths for every pairing in a run (common random numbers), which reduces
variance in comparisons.

### 4.3 Noise

- **Implementation noise (required):** with probability ε, the move actually played is the
  opposite of the intended move. Both players see the move that was actually played.
- **Perception noise (stretch):** the move is played as intended, but each player misreads
  the opponent's move with probability ε. Players' histories then disagree.
- Sweep ε over {0, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2}.

### 4.4 Analytic benchmarks (derive these in the report)

**B1. Grim Trigger vs. Always Defect.** Mutual Grim is an equilibrium when the one-time
gain from defecting is outweighed by permanent punishment:
δ ≥ (T − R)/(T − P) = (5 − 3)/(5 − 1) = 0.5

**B2. Tit-for-Tat stability (Axelrod).** TFT must also resist a cheater who alternates D,
C, D, C. TFT is collectively stable when:
δ ≥ max((T − R)/(T − P), (T − R)/(R − S)) = max(0.5, 0.667) = 0.667
Prediction for E6: cooperation should rise sharply between δ = 0.5 and δ = 0.67.

**B3. Always Defect is always an equilibrium.** Against ALLD, defecting is always the best
reply, at every δ. Cooperation therefore needs a critical mass of cooperators to start; it
cannot invade from one mutant.

**B4. TFT vs. TFT under noise.** One mistake starts an echo: (C,D) → (D,C) → (C,D)… until
another mistake. The four outcomes become equally likely in the long run, so the average
payoff per round tends to (R + S + T + P)/4 = (3 + 0 + 5 + 1)/4 = 2.25.
Win-Stay Lose-Shift (WSLS) recovers from one error in two rounds, so WSLS vs. WSLS stays
close to R = 3 for small ε.

**B5. Optimal generosity (Nowak & Sigmund, 1992).** For small noise and long games, the best
forgiveness probability for Generous TFT is:
g* = min(1 − (T − R)/(R − S), (R − P)/(T − P)) = min(1/3, 1/2) = 1/3
E4 checks whether the simulated optimum matches 1/3 and how it shifts at larger ε or
smaller δ.

**B6. A subtle point about WSLS.** Against ALLD, WSLS alternates C and D, so ALLD earns
(T + P)/2 = 3 per round. That equals R = 3, so with default payoffs ALLD is exactly neutral
in a WSLS population. WSLS is only strictly stable when R > (T + P)/2. Test this by
rerunning E5 with T = 4.5: a good example of theory explaining a surprising simulation
result.

## 5. Strategy library

The pool needs 12–15 strategies across four families, because tournament rankings depend
heavily on who else is playing. Every strategy sees only the full history of actual moves
(plus its own random number generator).

### 5.1 Classic strategies (required)

| Name | Code | Rule | Forgiving? |
|------|------|------|------------|
| Always Cooperate | ALLC | Always C. | Yes (unconditionally) |
| Always Defect | ALLD | Always D. | No |
| Random | RAND | C with probability 0.5. | n/a |
| Tit-for-Tat | TFT | C first, then copy opponent's last move. | Partly (forgives after one C) |
| Grim Trigger | GRIM | C until opponent defects once, then D forever. | No |

### 5.2 Known forgiving and adaptive strategies (required)

| Name | Code | Rule | Why include it |
|------|------|------|----------------|
| Generous TFT | GTFT(g) | Like TFT, but after opponent's D, cooperate with probability g. | Main forgiveness "dial"; default g = 1/3. |
| Tit-for-Two-Tats | TF2T | Defect only after two consecutive opponent Ds. | Deterministic forgiveness. |
| Win-Stay Lose-Shift (Pavlov) | WSLS | Repeat last move if payoff was R or T; otherwise switch. | Self-corrects errors; strong under noise. |
| Suspicious TFT | STFT | D first, then copy opponent. | Shows the cost of a nasty opening. |
| Contrite TFT | CTFT | TFT, but if its own D was a mistake, accept one punishment without retaliating. | Designed for implementation noise. |
| Joss | JOSS | TFT, but defects 10% of the time when it would cooperate. | A "sneaky" exploiter. |
| Extortioner (stretch) | ZDGTFT / EXT2 | Zero-Determinant memory-one strategy. | Modern angle (Press & Dyson, 2012). |

### 5.3 Original strategies (2–3 required)

Each original strategy needs: a one-line rule, the intuition behind it, and a predicted
niche (where in (ε, δ) it should do well) written down *before* testing. Starting ideas:

1. **Adaptive Forgiver.** Estimates the noise rate from how often the opponent "defects out
   of nowhere" after mutual cooperation, and sets its forgiveness probability to match.
   Prediction: matches GTFT at its best g across all ε.
2. **Grudger with Amnesty.** Plays like Grim, but resets to cooperation after k rounds of
   punishment if the opponent has cooperated in at least m of those rounds. Prediction:
   beats Grim under noise while keeping Grim's resistance to ALLD.
3. **Prober-Forgiver.** Opens with C, D, C, C to test the opponent. Exploits strategies that
   never retaliate (ALLC); otherwise switches to WSLS. Prediction: wins tournaments that
   include many ALLC players, but is penalised by TFT and Grim.
4. **Reputation Tracker.** Keeps a running cooperation score for the opponent
   (exponentially weighted) and cooperates when the score is above a threshold.
   Prediction: robust to noise, slow to punish.

### 5.4 Interface every strategy must implement

```python
class Strategy:
    name: str
    def reset(self, rng) -> None: ...             # called at the start of each match
    def move(self, my_hist, opp_hist) -> int: ... # returns 0 = C, 1 = D (intended move)
```

Strategies return the *intended* move; the engine applies noise. A registry maps codes to
classes so experiments can select pools by name.

## 6. Functional requirements

Six modules, each testable on its own: game engine, strategies, tournament, evolution,
experiments and analysis.

### FR1. Game engine (`game.py`)

- **FR1.1** `play_match(s1, s2, payoffs, delta, epsilon, rng, n_rounds=None)` plays one
  match and returns both move histories and both per-round average payoffs.
- **FR1.2** Game length is drawn from Geometric(1 − δ), or fixed by `n_rounds` (used only in
  tests).
- **FR1.3** Noise is applied after each strategy picks its intended move; both histories
  record the actual moves.
- **FR1.4** Optionally record the cooperation rate and the number of noise events per match.
- **FR1.5** A match must be fully determined by its seed.

### FR2. Strategies (`strategies/`)

- **FR2.1** All strategies in section 5 implement the common interface.
- **FR2.2** Parameterised strategies (GTFT(g), Joss, Adaptive Forgiver) take parameters in
  their constructor.
- **FR2.3** A registry function returns strategies by code, e.g. `make("GTFT", g=0.2)`.
- **FR2.4** Each strategy has a docstring with its rule and a source citation (or
  "original").

### FR3. Tournament (`tournament.py`)

- **FR3.1** Round-robin: every strategy plays every other strategy, and itself (self-play is
  required for evolution).
- **FR3.2** Each pairing is repeated `n_reps` times (default 50); report the mean and 95% CI.
- **FR3.3** Output: a payoff matrix A, where A[i][j] = average per-round payoff of strategy i
  against strategy j, plus a ranking table.
- **FR3.4** Also output a cooperation-rate matrix (how often i cooperates against j).

### FR4. Evolutionary dynamics (`evolution.py`)

- **FR4.1 Replicator dynamics (required).** Using the tournament matrix A and population
  shares x: f_i = Σ_j A_ij x_j, f̄ = Σ_i x_i f_i, x_i(t+1) = x_i(t) · f_i / f̄.
- **FR4.2** Run for a set number of generations (default 1,000) or until shares change by
  less than 1e−9. Shares below 1e−6 count as extinct.
- **FR4.3** Configurable initial shares (uniform by default; also "many defectors" and "one
  cooperator invading ALLD" scenarios).
- **FR4.4 Moran process (stretch).** Finite population of size N. Each step: pick a strategy
  to reproduce with probability proportional to fitness 1 − w + w·f, and replace a random
  individual. Track fixation probabilities over many runs.
- **FR4.5 Mutation (stretch).** With rate μ, an offspring adopts a random strategy.

### FR5. Experiment runner (`experiments/`, `run.py`)

- **FR5.1** Each experiment (section 8) is defined by a YAML or Python config: strategy pool,
  payoffs, δ values, ε values, number of repetitions, seed.
- **FR5.2** `python run.py E2` runs one experiment; `python run.py all` runs everything.
- **FR5.3** Raw results are saved to `results/<experiment>/` as CSV or Parquet, with the
  config copied next to them.
- **FR5.4** Sweeps run in parallel across CPU cores (`multiprocessing` or `joblib`).

### FR6. Analysis and plotting (`analysis/`)

- **FR6.1** Plotting reads saved results only; it never re-runs simulations.
- **FR6.2** Produces every figure in section 11 as PNG and PDF.
- **FR6.3** Theoretical thresholds and benchmarks (section 4) are drawn on the relevant
  plots as dashed lines.
- **FR6.4** Summary tables (rankings, survivors) are exported as CSV and Markdown.

## 7. Architecture and code structure

*One command turns a config into figures.* Results flow left to right; the engine underneath
plays every match:

Config (configs/E1–E7: δ, ε, pool, seed) → **Tournament** (tournament.py, round-robin →
matrix A) → Evolution (evolution.py, replicator, Moran stretch) → Results (results/, CSV +
config) → Analysis (analysis/, figures F1–F9, summary tables).
Underneath: Strategies (15 rules, 1 API) → Game engine (game.py, δ length, ε noise) plays
matches for the tournament; Tests (pytest, exact answers) verify the engine and evolution.

The tournament is the core: it uses the engine and strategies to build payoff matrix A,
which feeds evolution; results are saved before any plotting.

```
pd-forgiveness/
├── README.md
├── requirements.txt
├── run.py                  # python run.py E2 | all
├── configs/                # e1_baseline.yaml … e7_originals.yaml
├── pd/
│   ├── game.py             # play_match, payoffs, noise
│   ├── tournament.py       # round-robin, payoff + cooperation matrices
│   ├── evolution.py        # replicator dynamics, Moran process
│   ├── theory.py           # benchmark formulas B1–B6
│   └── strategies/
│       ├── base.py         # Strategy interface + registry
│       ├── classic.py      # ALLC, ALLD, RAND, TFT, GRIM
│       ├── forgiving.py    # GTFT, TF2T, WSLS, CTFT, STFT, JOSS
│       └── original.py     # your strategies
├── analysis/
│   ├── make_figures.py
│   └── stats.py            # confidence intervals, bootstrap
├── tests/
├── results/                # generated, one folder per experiment
├── figures/                # generated PNG + PDF
└── report/
```

Putting the formulas in `theory.py` lets plots and tests use the same benchmark values, so
theory and simulation are always compared on identical numbers.

## 8. Experiment plan

Seven experiments, run in order; each changes one thing from the one before it. Defaults
unless stated: payoffs (5, 3, 1, 0), δ = 0.99, full strategy pool, 50 repetitions per
pairing, base seed 42.

| ID | Experiment | What varies | Metrics | Expected result | Answers |
|----|-----------|-------------|---------|-----------------|---------|
| E1 | Baseline tournament (no noise) | Nothing; ε = 0 | Ranking, payoff matrix, cooperation matrix | TFT/GRIM near top; ALLD near bottom; matches Axelrod | RQ1 |
| E2 | Noise sweep | ε ∈ {0, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2} | Mean score per strategy vs. ε; rank changes | Crossover: forgiving strategies overtake TFT/GRIM at small ε | RQ2 |
| E3 | Echo effect | TFT vs. TFT and WSLS vs. WSLS across ε, 2,000-round matches | Average payoff vs. ε; sample move traces | TFT vs. TFT falls toward 2.25; WSLS stays near 3 | RQ3 |
| E4 | Forgiveness dial | GTFT g ∈ {0, 0.05, …, 1.0} × ε grid | Score of GTFT(g) in the full pool; heatmap over (g, ε) | Interior optimum near g = 1/3; ALLD exploits g → 1 | RQ4 |
| E5 | Evolution | ε ∈ {0, 0.01, 0.05}; 3 initial conditions | Share of each strategy over generations; survivors | No noise: TFT-like win; with noise: WSLS/GTFT win | RQ5 |
| E6 | Shadow of the future | δ ∈ {0.1, 0.2, …, 0.9, 0.95, 0.99} × ε ∈ {0, 0.01, 0.05} | Population cooperation rate at evolutionary equilibrium vs. δ | Sharp rise between δ = 0.5 and 0.67 (B1, B2) | RQ6 |
| E7 | Original strategies | Add originals to the pool; rerun E2, E5, E6 | Rank and survival vs. known strategies; their niche in (ε, δ) | Each original's predicted niche confirmed or refuted | RQ7 |

### Robustness checks (run at least two)

- **Different pools:** rerun E1, E2 and E5 with (a) only nice strategies, (b) many
  exploiters, (c) a random 8-strategy subset. Report which conclusions hold.
- **Different payoffs:** T = 4.5 (makes WSLS strictly stable, see B6) and T = 6 (stronger
  temptation).
- **Replicator vs. Moran:** compare survivors for N = 50 and N = 200 (stretch).
- **Implementation vs. perception noise:** rerun E2 with perception noise (stretch).

### Compute budget

A full tournament with 15 strategies is 120 pairings. At 50 repetitions and about 100 rounds
each, that is 600,000 rounds, which takes seconds in plain Python. The largest sweep (E4: 21
values of g × 7 values of ε) is about 150 tournaments, so a few minutes on a laptop. Use
NumPy or Numba only if profiling shows it is needed.

## 9. Non-functional requirements

| Area | Requirement |
|------|-------------|
| Reproducibility | Every run takes a seed; use `numpy.random.default_rng(seed)` and derive child seeds per match with `SeedSequence.spawn`. Same seed → identical results. |
| Reproducibility | Pin dependencies in `requirements.txt` (Python 3.11+, numpy, pandas, matplotlib, pyyaml, pytest; optional joblib, numba, seaborn). |
| Reproducibility | One command regenerates all results and figures: `python run.py all && python analysis/make_figures.py`. |
| Performance | Full experiment suite runs in under 30 minutes on a laptop. |
| Code quality | Type hints and docstrings on public functions; formatted with `black`; linted with `ruff`. |
| Code quality | No experiment logic inside strategy classes; no simulation inside plotting code. |
| Version control | Git from day one; commit after each milestone; tag the final version used in the report. |
| Documentation | README covering setup, how to run each experiment, folder layout and how to add a new strategy. |
| Statistics | Report means with 95% confidence intervals (normal approximation or bootstrap) over at least 30 runs; never a single run. |

## 10. Testing and validation

The code is trusted only once it reproduces results whose answers are known exactly. Write
these as `pytest` tests.

### Unit tests (deterministic, fixed rounds, ε = 0)

- [ ] ALLC vs. ALLD over 10 rounds: payoffs 0 and 5 per round.
- [ ] TFT vs. ALLD: TFT plays C then D forever; over 10 rounds TFT averages 0.9 and ALLD
  averages 1.4.
- [ ] TFT vs. TFT and GRIM vs. GRIM: always C, payoff 3.
- [ ] WSLS vs. ALLD: WSLS alternates C, D; ALLD averages 3 per round (B6).
- [ ] TF2T forgives a single D but punishes two in a row.
- [ ] GTFT with g = 0 behaves exactly like TFT; with g = 1 exactly like ALLC.
- [ ] Same seed gives identical histories; different seeds give different ones.

### Statistical tests

- [ ] Noise: over 1,000,000 moves with ε = 0.05, the observed flip rate is within
  0.05 ± 0.001.
- [ ] Game length: mean number of rounds is within 2% of 1/(1 − δ) for δ = 0.9 and 0.99.
- [ ] TFT vs. TFT with ε = 0.05 over long matches: average payoff close to 2.25 (B4).

### Evolution tests

- [ ] Population shares always sum to 1 and stay non-negative.
- [ ] A two-strategy population of ALLD and ALLC goes to 100% ALLD.
- [ ] A population of only TFT and ALLC stays fixed (equal payoffs, neutral).
- [ ] With δ = 0.99 and ε = 0, TFT invades a mostly-ALLD population only above a critical
  starting share (compute it and check).

### Validation against literature

- [ ] E1 ranking is broadly consistent with Axelrod's tournaments.
- [ ] E3 and E5 under noise are consistent with Nowak & Sigmund (1993) on WSLS.
- [ ] Optional: cross-check a few match results against the open-source `axelrod` Python
  library.

## 11. Figures, deliverables and report

### 11.1 Required figures

| Fig. | Experiment | Chart | What it shows |
|------|-----------|-------|---------------|
| F1 | E1 | Heatmap of payoff matrix A (strategies × strategies) | Who beats whom with no noise |
| F2 | E1 | Horizontal bar chart of mean scores with 95% CI | Baseline ranking |
| F3 | E2 | Line chart: mean score vs. ε, one line per strategy (log x-axis) | Where forgiving strategies overtake TFT/GRIM |
| F4 | E3 | Line chart: TFT-vs-TFT and WSLS-vs-WSLS payoff vs. ε, with 2.25 and 3 as dashed lines | The echo effect vs. theory |
| F5 | E3 | Move trace (two rows of coloured squares) for a TFT vs. TFT match with one error | The echo, visually |
| F6 | E4 | Heatmap of GTFT score over (g, ε), g = 1/3 marked | The optimal amount of forgiveness |
| F7 | E5 | Stacked area chart of population shares over generations, one panel per ε | Who survives evolution |
| F8 | E6 | Line chart: equilibrium cooperation rate vs. δ, one line per ε, with δ = 0.5 and 0.667 as dashed lines | Theory vs. simulation for the shadow of the future |
| F9 | E7 | Heatmap over (ε, δ) showing which strategy dominates | Niches, including original strategies |

Every figure has axis labels with units, a legend, a caption stating the parameters, and
error bars or bands where applicable.

### 11.2 Deliverables

1. **Code repository** with the structure in section 7, tests, README and pinned
   requirements.
2. **Results folder** with raw CSVs and configs for every experiment.
3. **Written report** (8–15 pages, structure below).
4. **Presentation** (10–12 slides) if your course requires one.
5. Optional: a short demo notebook that runs a small tournament end to end.

### 11.3 Report structure

1. **Abstract** (150 words): question, method, the three main findings with numbers.
2. **Introduction:** the cooperation puzzle, Axelrod's tournaments, why noise matters.
3. **Model:** stage game, δ, noise, strategies, tournament and evolutionary dynamics.
4. **Theory:** derivations of benchmarks B1–B6 and the predictions they imply.
5. **Results:** one subsection per experiment, each in the form prediction → figure →
   agreement or disagreement → explanation.
6. **Original strategies:** design rationale, predicted niche, outcome.
7. **Robustness and limitations:** pool dependence, payoff choices, model simplifications.
8. **Conclusion:** answer the title question directly: does forgiveness pay, when, and how
   much?
9. **References** and an **appendix** with strategy definitions and parameter tables.

## 12. Timeline and milestones

*Core results are frozen at week 6; weeks 7–10 go to originals and writing.* Suggested
10-week plan; shift the weeks to fit your deadline.

| Milestone | Weeks |
|-----------|-------|
| M0 Setup and reading | 1 |
| M1 Engine, strategies, tests | 2–3 |
| M2 Tournament, E1 | 3–4 |
| M3 Noise, E2–E3 | 4–5 |
| **M4 GTFT dial E4, evolution E5** | 5–6 (core results frozen at end of M4) |
| M5 Shadow of future, E6 | 7 |
| M6 Originals E7, robustness | 7–8 |
| M7 Figures, report draft | 8–9 |
| M8 Final report, slides | 10 |

Experiments E1–E5 are done by week 6, so a slip still leaves time for the writeup. Each
milestone is done when:

- **M0:** environment set up, Git repo created, Axelrod (1984) ch. 1–3 and Nowak & Sigmund
  (1993) read.
- **M1:** engine and all section 5.1–5.2 strategies pass every unit test in section 10.
- **M2:** E1 ranking and payoff heatmap (F1, F2) produced and consistent with Axelrod.
- **M3:** F3, F4 and F5 produced; TFT-vs-TFT matches the 2.25 benchmark.
- **M4:** F6 and F7 produced. Core results frozen; stretch goals allowed only after this
  point.
- **M5:** F8 produced with B1/B2 thresholds overlaid.
- **M6:** originals tested with predictions recorded beforehand; at least two robustness
  checks done.
- **M7:** all figures final; full report draft written.
- **M8:** report revised, slides ready, repo tagged.

## 13. Risks and mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Results only restate known findings | Project looks unoriginal | Lead with theory-vs-simulation plots (F4, F6, F8), the B6 WSLS edge case and original strategies with stated predictions. |
| Rankings depend on the strategy pool | Conclusions don't generalise | Robustness checks with three different pools; state clearly which findings survive. |
| Single runs give noisy, misleading results | Wrong conclusions | At least 30 repetitions, 95% CIs, common random numbers across strategies. |
| Subtle bug in history or noise handling | All results invalid | Unit tests with exact known answers (section 10) before running any experiment. |
| Strategy bugs, e.g. a strategy reading its own noisy move wrongly | Unfair comparisons | Each strategy tested on a scripted opponent; move traces inspected by eye for a few matches. |
| Replicator dynamics with zero payoffs divides by zero | Crash or NaN | All default payoffs are ≥ 0 and A always has positive entries; add a small baseline fitness if needed. |
| Scope creep (Moran, perception noise, ZD, dashboard) | Core experiments unfinished | Finish E1–E6 first; stretch goals only after milestone M4. |
| Original strategies perform poorly | Feels like a failure | A clearly explained failure is still a result; the report explains *why* using game theory. |
| Slow sweeps | Missed deadlines | Profile first; parallelise across cores; reduce repetitions for exploration and use full counts for final figures. |

## 14. References

Core reading, cited from memory; check volume and page numbers before citing them in the
report.

1. Axelrod, R. & Hamilton, W. D. (1981). The evolution of cooperation. *Science*, 211,
   1390–1396.
2. Axelrod, R. (1984). *The Evolution of Cooperation*. Basic Books. Chapters 1–3 cover the
   tournaments and the stability conditions in B2.
3. Boyd, R. (1989). Mistakes allow evolutionary stability in the repeated Prisoner's Dilemma
   game. *Journal of Theoretical Biology*, 136, 47–56.
4. Nowak, M. A. & Sigmund, K. (1992). Tit for tat in heterogeneous populations. *Nature*,
   355, 250–253. Source for Generous TFT and B5.
5. Nowak, M. A. & Sigmund, K. (1993). A strategy of win-stay, lose-shift that outperforms
   tit-for-tat in the Prisoner's Dilemma game. *Nature*, 364, 56–58.
6. Wu, J. & Axelrod, R. (1995). How to cope with noise in the iterated Prisoner's Dilemma.
   *Journal of Conflict Resolution*, 39(1), 183–189. Source for Contrite TFT.
7. Nowak, M. A. (2006). Five rules for the evolution of cooperation. *Science*, 314,
   1560–1563.
8. Nowak, M. A. (2006). *Evolutionary Dynamics*. Harvard University Press. Replicator
   dynamics and the Moran process.
9. Press, W. H. & Dyson, F. J. (2012). Iterated Prisoner's Dilemma contains strategies that
   dominate any evolutionary opponent. *PNAS*, 109(26), 10409–10413.
10. Knight, V. et al. (2016). An open framework for the reproducible study of the iterated
    Prisoner's Dilemma. *Journal of Open Research Software*. The
    [Axelrod Python library](https://github.com/Axelrod-Python/Axelrod), useful for
    cross-checking.
