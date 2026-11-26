# Predictions (written before any experiment was run)

Committed to Git at milestone M1, before tournament or experiment code existed. Each later
result in `notes/findings.md` is checked against the matching line here.

| ID | Question | Prediction | Basis | Experiment |
|----|----------|-----------|-------|-----------|
| RQ1 | No noise: who wins the round-robin? | Nice, retaliating strategies (TFT, GRIM, and the TFT-like CTFT/GTFT/TF2T/WSLS) finish near the top; ALLD wins its head-to-head matches but scores low overall. | Axelrod (1984) | E1 |
| RQ2 | How does noise change the ranking? | As ε rises, TFT and GRIM fall; GTFT, TF2T and WSLS overtake them already at small ε (≈ 0.01–0.02). | Echo effect (B4) | E2 |
| RQ3 | TFT vs TFT under noise? | Long-run payoff falls from 3 toward 2.25 = (R+S+T+P)/4; WSLS vs WSLS stays near 3 for small ε. | B4 | E3 |
| RQ4 | How much forgiveness is optimal? | GTFT's best g* is above 0 and near 1/3; g → 1 is exploited by ALLD. The optimum shifts with ε. | B5 | E4 |
| RQ5 | Who survives evolution? | ε = 0: TFT-like strategies take over once defectors die out. With noise: WSLS or GTFT dominate. Cycles (ALLC → ALLD → TFT) may appear. With default payoffs ALLD is neutral against WSLS (B6); with T = 4.5 WSLS is strictly stable. | B3, B6, Nowak & Sigmund (1993) | E5 |
| RQ6 | How does δ affect cooperation? | Cooperation collapses below δ ≈ 0.5 and is stable above δ ≈ 0.667, rising sharply in between. | B1, B2 | E6 |
| RQ7 | Do original strategies beat known ones anywhere in (ε, δ)? | See the per-strategy predictions below (written at M6, before E7 ran). | Design rationale | E7 |

## RQ7: original strategies (written at M6, before E7 was run)

Context at the time of writing: E1–E6 had been run with the 11 known strategies, so these
predictions could use what E2–E6 showed about the known strategies (CTFT dominates
evolution under noise, GTFT's optimum is flat at g ≈ 0.15–0.35), but **nothing about how
the originals perform**. Only their scripted unit tests had run.

| Strategy | One-line rule | Predicted niche | Specific, checkable predictions |
|---|---|---|---|
| **AF** Adaptive Forgiver | TFT, but forgive a D with prob. g = ½ · (surprise Ds + 1)/(all Ds + 2) | Moderate noise (0.005 ≤ ε ≤ 0.1), long games | (a) Scores within the CI of GTFT(1/3) or above it for 0.005 ≤ ε ≤ 0.1. (b) Scores higher than GTFT against ALLD (punishes harder). (c) Survives evolution at ε = 0.01 alongside CTFT/GTFT, but loses to CTFT at ε = 0.05. |
| **GWA** Grudger with Amnesty (k=5, m=3) | GRIM with a 5-round sentence; parole if the opponent cooperated ≥ 3 of those rounds | Low–moderate noise in pools of forgiving players | (a) PRD's prediction: beats GRIM's tournament score for every ε > 0. (b) My caveat: still ranks below TFT and the forgiving strategies under noise, because retaliators answer its punishment with punishment, so parole rarely triggers. (c) Does not survive evolution at ε ≥ 0.01. |
| **PF** Prober-Forgiver | Open C, D, C, C; exploit if no retaliation, otherwise WSLS | Low noise, pools with unconditional cooperators | (a) Highest score of all against ALLC. (b) Mid-table overall (ranks 5–10): GRIM never forgives the probe, and the probe costs against TFT-like players. (c) Dies out in evolution: once ALLC is extinct, its exploitation pays nothing. |
| **REP** Reputation Tracker (α=0.2, threshold 0.5) | Cooperate iff the opponent's exponentially weighted cooperation score > 0.5 | Moderate–high noise (0.02 ≤ ε ≤ 0.1) | (a) Top half of the ranking for 0.02 ≤ ε ≤ 0.1. (b) Small loss vs ALLD (4 sucker rounds per game). (c) Close to TF2T's score at every ε, since both ignore a single D. |

Niche map (F9) prediction: CTFT keeps the noisy, long-game region (it won E5 at ε = 0.05).
AF or GTFT may share the low-noise region. No original takes over at δ < 0.5, where ALLD-like
behaviour wins (B1).
