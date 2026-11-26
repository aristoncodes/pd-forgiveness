# Findings

Each result: **prediction → figure → agree / disagree → game-theoretic explanation.**
Every number here comes from a saved file in `results/`.

## E1: Baseline tournament, no noise (RQ1)

**Prediction** (`predictions.md`): nice, retaliating strategies (TFT, GRIM) finish near the
top; ALLD wins head-to-head but scores low overall.

**Figures:** `figures/F1_payoff_matrix.png`, `figures/F2_ranking.png`.
**Data:** `results/E1/ranking.csv`, `payoff_matrix.csv`, `coop_matrix.csv`.

**Result** (mean payoff per round, 95 % bootstrap CI, δ = 0.99, ε = 0, 50 reps):

| Rank | Strategy | Score | 95 % CI | Head-to-head wins |
|---|---|---|---|---|
| 1 | TF2T | 2.674 | [2.660, 2.687] | 0 |
| 2 | GTFT(0.33) | 2.653 | [2.647, 2.657] | 0 |
| 3 | ALLC | 2.560 | [2.553, 2.565] | 0 |
| 4 | TFT | 2.560 | [2.550, 2.576] | 0 |
| 5 | CTFT | 2.546 | [2.536, 2.562] | 0 |
| 6 | WSLS | 2.520 | [2.515, 2.525] | 0 |
| 7 | GRIM | 2.475 | [2.468, 2.485] | 1 |
| 8 | RAND | 2.222 | [2.215, 2.234] | 6 |
| 9 | STFT | 2.051 | [2.043, 2.067] | 8 |
| 10 | JOSS | 1.922 | [1.871, 1.998] | 8 |
| 11 | ALLD | 1.878 | [1.868, 1.897] | 9 |

**Verdict: mostly agrees.**
- ✅ **All 7 nice strategies outrank all 4 non-nice ones.** This is Axelrod's central
  finding, reproduced exactly.
- ✅ **ALLD has the most head-to-head wins (9 of 10) yet finishes last.** TFT wins *zero*
  head-to-head contests but finishes 4th. You do well in the IPD by eliciting
  cooperation, not by beating opponents.
- ⚠️ **TFT is 4th, not 1st, and GRIM is last among the nice strategies.** TF2T and GTFT beat
  TFT; TFT ties ALLC (2.560 each, overlapping CIs).

**Explanation of the surprise:**
1. **JOSS's random defections act like noise even at ε = 0.** TFT vs JOSS = 1.41 and
   CTFT vs JOSS = 1.29: each sneaky D starts an echo of retaliation. TF2T (2.60) and GTFT
   (2.56) absorb isolated defections and keep cooperating. GRIM (1.23) is worse still, since
   one sneaky D ends cooperation for good. *This previews the noise result of E2.*
2. **STFT's opening D.** TFT and CTFT get stuck in endless D/C alternation with STFT (2.49),
   while TF2T and GTFT forgive the first D and reach mutual cooperation (2.97). GRIM punishes
   forever (1.03).
3. **Few exploiters in the pool.** Only ALLD and RAND seriously punish over-forgiving
   strategies, so forgiveness costs little here. That is why even ALLC places 3rd. This
   matches Axelrod (1984, ch. 2): TF2T *would have won* his first tournament had it been
   entered, yet it is exploitable by strategies that defect every other round. **Rankings
   depend on the pool**; the robustness checks in M6 test this.

**Literature check:** consistent with Axelrod (1984): nice strategies dominate, ALLD loses
overall despite winning every head-to-head match, and TF2T's hypothetical win in tournament 1.
