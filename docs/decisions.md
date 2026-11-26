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
