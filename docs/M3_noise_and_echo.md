# M3: Noise sweep (E2) and echo effect (E3)

**Status:** done. Figures F3, F4, F5. TFT vs TFT matches the 2.25 benchmark (B4).

## What was built
- `experiments.e2` → `noise_sweep()`: one full tournament per noise level ε ∈ {0, 0.005,
  0.01, 0.02, 0.05, 0.1, 0.2}, run in parallel (joblib), all with seed 42 (common random
  numbers across the sweep, D23). Saves `scores.csv` (rank, score, CI per ε),
  `matrices.csv`, `rank_by_epsilon.md` and `score_by_epsilon.md`.
- `experiments.e3`: self-play of TFT, WSLS, CTFT and GTFT in 2,000-round matches, 50 per ε,
  with a normal 95 % CI. `one_error_trace()` searches seeds for a 24-round match with
  *exactly one* noise error, used for the move-trace picture F5.

## Results in one breath
- Forgiving strategies (TF2T, GTFT, CTFT) lead every tournament up to ε = 0.05. GRIM
  collapses (2.48 → 2.04). TFT's score barely moves after the first bit of noise.
- TFT vs TFT: 3.000 → 2.351 (ε = 0.005) → 2.247 (ε = 0.01), and about 2.25 from then on.
  Exactly B4.
- WSLS vs WSLS stays near 3 for small noise (2.95 at ε = 0.01). CTFT is the best
  self-player at every ε.
- **At ε = 0.2 the ranking flips: ALLD 1st, GRIM 2nd.** Forgiveness stops paying when
  noise drowns the signal.

## How to read the figures
- **F3:** each line is a strategy's tournament score. The pink/orange lines (TF2T, GTFT)
  stay on top until about ε = 0.1. The green GRIM line dives. The red ALLD line rises and
  crosses everyone at ε = 0.2.
- **F4:** the blue TFT line falls off a cliff at the first noise point and lies on the
  dashed 2.25 line. The others decline gently from 3.
- **F5:** coloured squares are actual moves. One outlined error makes TFT alternate C/D for
  the rest of the match, while WSLS needs two rounds to repair it.

## Why (the game theory)
- **Echo:** TFT copies the last move, so an accidental D is answered with D, which is
  answered with D, and so on. The state CD ↔ DC alternates until another error. B4's
  Markov-chain argument (doubly stochastic transitions) gives a uniform long-run
  distribution over CC, CD, DC, DD, so the average is 2.25 regardless of ε.
- **WSLS self-repair:** after (C, D) both "lose" or "win" in a way that sends them to
  (D, D), where both lose and switch back to (C, C).
- **High-noise inversion:** a defection is informative only if it's unlikely to be an
  accident. At ε = 0.2 a fifth of all moves are random, so a forgiving player keeps
  absorbing exploitation it cannot detect.

## Talking points
1. "One error costs TFT a quarter of its payoff for the rest of the match, and it doesn't
   matter how rare errors are."
2. "Forgiveness wins the noisy tournament, but there is a limit: at 20 % noise the
   unforgiving win again."
