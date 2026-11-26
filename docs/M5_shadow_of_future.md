# M5: Shadow of the future (E6)

**Status:** done. Figure F8 with the B1/B2 thresholds overlaid: the PRD's main
"theory vs simulation" plot.

## What was built
- `experiments.shadow_sweep()`: for every (ε, δ, seed) it runs a full tournament at that
  δ, then replicator dynamics from a uniform start (2,000 generations), and records the
  final cooperation rate xᵀCx, the dominant strategy and all final shares.
  16 δ values × 3 ε values × 30 seeds = 1,440 tournaments, in parallel (35 s).
- `summarise_seeds()`: mean and 95 % CI over the 30 seeds.

## Results
| δ | 0.40 | 0.45 | 0.50 | 0.55 | 0.60 | 0.65 | 0.70 | 0.80 | 0.85+ |
|---|---|---|---|---|---|---|---|---|---|
| cooperation, ε = 0 | 0.00 | 0.08 | 0.28 | 0.37 | 0.69 | 0.78 | 0.86 | 0.96 | 1.00 |
| cooperation, ε = 0.05 | 0.11 | 0.14 | 0.20 | 0.24 | 0.28 | 0.47 | 0.68 | 0.75 | 0.81–0.91 |

Cooperation is absent below δ = 0.45 and rises steeply through the predicted band
[0.5, 0.667], passing 50 % at δ ≈ 0.57. Noise flattens and delays the rise.

## Why
- **B1 (δ ≥ 0.5):** below it, even the harshest punishment (GRIM) cannot deter a one-shot
  defection, so ALLD takes over (the equilibrium populations at δ ≤ 0.4 are mostly ALLD).
- **B2 (δ ≥ 0.667):** TFT, which forgives quickly, also needs to deter alternating cheats.
  Between 0.5 and 0.667 cooperation is possible but fragile, so we see mixed populations.
- **A ramp, not a step:** the thresholds are equilibrium conditions. The simulation starts
  from a uniform mix, and near the threshold the outcome depends on early luck, giving
  intermediate averages with wide CIs.
- **Noise:** retaliation is also triggered by errors, so more future is needed to make
  cooperation pay.
- **Robustness (R2, F10):** with T = 4.5 the switch moves down to about δ = 0.5 = B2(4.5),
  and with T = 5.9 full cooperation needs δ ≈ 0.9 (B2 = 0.97). The thresholds move the way
  the formulas say.

## Talking point
"The dashed lines come from two lines of algebra; the curves come from 1,440 simulated
tournaments plus evolution. They agree on where cooperation becomes possible."
