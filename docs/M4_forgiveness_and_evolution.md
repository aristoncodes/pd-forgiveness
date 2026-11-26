# M4: Forgiveness dial (E4) and evolution (E5)

**Status:** done. Figures F6, F6b, F7, F7b. B5 and B6 checked, including the T = 4.5 run.

## What was built
- `pd/evolution.py`: `replicator()` (discrete replicator dynamics, stops at max change
  < 1e-9), `initial_shares()` (uniform / many_defectors / invasion / wsls_resident),
  `cooperation_rate()` = xᵀCx.
- `theory.tft_alld_matrix()` and `theory.invasion_threshold()`: the critical share of TFT
  needed to beat ALLD (B3) from the 2×2 sub-matrix.
- `experiments.e4`: 21 values of g × 7 values of ε × 2 values of δ = 294 tournaments,
  with GTFT(g) in the GTFT slot (D26).
- `experiments.e5`: a tournament at each (T, ε), then replicator dynamics from 4 starting
  populations; also `invasion_table()`.
- 8 evolution tests (all PRD evolution tests + B6 at T = 5 vs 4.5).

## Results in one breath
- **E4:** the best generosity is a flat plateau g ≈ 0.15–0.35 (contains 1/3). g = 0 (TFT)
  is clearly worse. ALLD out-earns a GTFT population once g > 0.5, *exactly* the B5 bound.
  Shorter games want less forgiveness (δ = 0.9: g = 0.2), and very noisy games want none
  (ε = 0.2: g ≈ 0).
- **E5:** without noise, defectors die out and seven nice strategies coexist (neutral).
  With noise, **CTFT** takes over (100 % at ε = 0.05). TFT invades ALLD from 5 % only while
  noise is low (threshold 0.5 % → 1.2 % → 5.1 %). **B6:** ALLD conquers a WSLS population at
  T = 5 but is repelled at T = 4.5.

## How to read the figures
- **F6:** rows are noise levels, columns generosity g; darker = higher score. White dots
  mark the best g in each row; they sit just left of the dashed 1/3 line. Each row is
  pale at both ends (g = 0 and g = 1) and dark in the middle: the interior optimum.
- **F6b:** solid line = what ALLD earns against GTFT(g); dotted = what GTFT(g) earns
  against itself. Where solid crosses dotted, ALLD can invade. Without noise that happens
  at g = 0.5.
- **F7:** stacked shares over generations (log scale). Columns: noise; rows: starting
  population. The teal (CTFT) area swallows everything at ε = 0.05.
- **F7b:** the B6 experiment. The top row (T = 5) turns red (ALLD); the bottom row
  (T = 4.5) stays yellow (WSLS).

## Why (the game theory)
- **Optimal generosity:** forgiving breaks echoes (good under noise), but every forgiven
  defection is a gift to real defectors. B5: ALLD earns gT + (1−g)P, which equals R at
  g = (R−P)/(T−P) = ½. An alternator caps g at 1/3. The tournament optimum sits slightly
  below 1/3 because this pool contains several exploiters.
- **Why CTFT wins evolution:** in evolution you must do well against the strategy that is
  becoming common, eventually yourself. CTFT recovers from its own errors at once
  (apology), and it is not invadable by generous strategies. They forgive CTFT's
  justified punishments, while CTFT does not let *their* errors go unpunished. Boyd (1989)
  proved contrite strategies are evolutionarily stable under implementation errors.
- **B6:** ALLD vs WSLS gives ALLD (T+P)/2 per round. At T = 5 that equals R = 3, so ALLD does
  as well as WSLS among WSLS players, and strictly better when meeting ALLD (1 vs 0.5). So it
  spreads. At T = 4.5, (T+P)/2 = 2.75 < 3, and WSLS wins.

## Talking points
1. "Simulation reproduces the 'exactly ½' generosity bound to two decimals (F6b)."
2. "Our biggest surprise: evolution's winner under noise is Contrite TFT, not WSLS. Theory
   (Boyd 1989, and B6 for WSLS) explains both halves of that."
3. "Half a point of temptation, T = 5 → 4.5, decides whether WSLS survives. Theory predicted
   it, simulation confirms it."
