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

---

## E2: Noise sweep (RQ2)

**Prediction:** as ε rises, TFT and GRIM fall; GTFT, TF2T and WSLS overtake them at small ε.
**Figure:** `figures/F3_noise_sweep.png`. **Data:** `results/E2/scores.csv`,
`rank_by_epsilon.md`, `score_by_epsilon.md`.

| ε | 1st | 2nd | 3rd | TFT | GRIM | ALLD |
|---|---|---|---|---|---|---|
| 0 | TF2T 2.674 | GTFT 2.653 | ALLC 2.560 | 4th, 2.560 | 7th, 2.475 | 11th, 1.878 |
| 0.005 | TF2T 2.540 | GTFT 2.513 | CTFT 2.390 | 4th, 2.374 | 8th, 2.141 | 11th |
| 0.01 | TF2T 2.488 | GTFT 2.473 | CTFT 2.363 | 5th, 2.338 | 9th, 2.088 | 11th |
| 0.05 | TF2T 2.362 [2.347, 2.387] | GTFT 2.337 | CTFT 2.325 | 4th, 2.281 [2.265, 2.306] | 10th, 2.059 | 11th |
| 0.2 | **ALLD 2.339** | **GRIM 2.323** | JOSS 2.280 | 4th, 2.266 | **2nd** | **1st** |

**Verdict: agrees for small and moderate noise, with two surprises.**
- ✅ **GRIM collapses** under noise (2.475 → 2.041 at ε = 0.02). One error ends cooperation
  for good.
- ✅ **The forgiving strategies stay on top.** TF2T and GTFT lead at every ε ≤ 0.05, and
  CTFT overtakes TFT from ε = 0.005. At ε = 0.05, TF2T's CI [2.347, 2.387] lies entirely
  above TFT's [2.265, 2.306].
- ⚠️ **WSLS barely overtakes TFT.** It is ahead at ε = 0.01–0.02, but within the CIs, and
  behind again at ε = 0.05. WSLS's weakness against ALLD, JOSS and RAND (B6: it alternates
  C/D against defectors) cancels its self-correction advantage in this pool.
- ⚠️ **TFT's score is almost flat in ε** (2.37 → 2.27 from ε = 0.005 to 0.2), while its rank
  stays 4–5. This is B4 again: TFT vs TFT drops to 2.25 for *any* ε > 0, so after the first
  drop extra noise costs TFT little.
- ❗ **At very high noise (ε = 0.2) the ranking inverts.** ALLD and GRIM go first and second,
  TF2T and GTFT fall to 10th and 9th. When 20 % of moves are random, an opponent's
  defection carries almost no information about its intentions, so forgiving it mostly
  means being exploited. Forgiveness pays only while mistakes are rare enough to be
  told apart from intent.

## E3: Echo effect (RQ3, B4)

**Prediction:** TFT vs TFT drops from 3 toward 2.25; WSLS vs WSLS stays near 3 for small ε.
**Figures:** `F4_echo_effect.png`, `F5_move_traces.png`. **Data:** `results/E3/echo_summary.csv`,
`traces.csv`.

| ε | TFT vs TFT | WSLS vs WSLS | CTFT vs CTFT | GTFT vs GTFT |
|---|---|---|---|---|
| 0 | 3.000 | 3.000 | 3.000 | 3.000 |
| 0.005 | 2.351 | 2.974 | 2.990 | 2.985 |
| 0.01 | 2.247 | 2.950 | 2.981 | 2.971 |
| 0.05 | 2.265 | 2.776 | 2.896 | 2.860 |
| 0.2 | 2.246 | 2.376 | 2.608 | 2.559 |

(2,000-round matches, 50 per point.)

**Verdict: agrees exactly.** TFT jumps from 3 to about 2.25 as soon as ε > 0 and stays
there; every point from ε = 0.01 on is within 0.05 of the B4 value. At ε = 0.005 it is
slightly higher (2.351) because a pair starts in mutual cooperation and needs about
1/(2ε) = 100 rounds to see its first error. WSLS stays near 3 for small ε (2.95 at
ε = 0.01). CTFT is the best self-player at every noise level.
**F5 shows the mechanism:** after one error, TFT alternates C/D forever (both players get
(T+S)/2 = 2.5, not 3), while WSLS goes (C,D) → (D,D) → (C,C) and is back to cooperation in
two rounds.

## E4: Forgiveness dial (RQ4, B5)

**Prediction:** GTFT's best g* is above 0 and near 1/3; g → 1 is exploited by ALLD.
**Figures:** `F6_forgiveness_dial.png`, `F6b_exploitation.png`. **Data:**
`results/E4/gtft_scores.csv`, `best_g.md`.

| ε | best g (δ = 0.99) | best g (δ = 0.9) |
|---|---|---|
| 0 | 0.20 | 0.20 |
| 0.005 | 0.15 | 0.20 |
| 0.01 | 0.20 | 0.20 |
| 0.02 | 0.30 | 0.20 |
| 0.05 | 0.25 | 0.20 |
| 0.1 | 0.30 | 0.20 |
| 0.2 | 0.05 | 0.00 |

**Verdict: agrees qualitatively; the simulated optimum is a flat plateau slightly below 1/3.**
- ✅ **Interior optimum.** g = 0 (TFT) is always worse for ε ≤ 0.1. At δ = 0.99, ε = 0.01:
  2.250 at g = 0 vs 2.478 at g = 0.2.
- ✅ **1/3 lies on the plateau.** At δ = 0.99 the score is within about 0.01 of the best for
  every g from 0.15 to 0.35 (e.g. ε = 0.05: 2.340 at g = 0.25–0.30 vs 2.334 at g = 0.35).
- ✅ **Too much forgiveness is exploited (F6b).** Without noise, ALLD's payoff against
  GTFT(g) crosses the GTFT population's own payoff (3) at **exactly g = 0.5**. That is B5's
  bound against ALLD, (R−P)/(T−P) = 1/2, reproduced by simulation.
- ↘ **The optimum shifts.** It moves lower in shorter games (δ = 0.9: always 0.2), because
  there is less future to protect. It collapses to g ≈ 0 at ε = 0.2, the same "noise too
  high" effect as in E2.
- *Why below 1/3?* B5 is a population-stability argument (the most generosity that still
  resists invasion). A tournament score instead rewards doing well against *this* pool,
  which contains ALLD, RAND and JOSS: each extra unit of generosity is a gift to them.

## E5: Evolution (RQ5, B3, B6)

**Prediction:** ε = 0: TFT-like strategies win once defectors die out. With noise: WSLS or
GTFT dominate. B6: ALLD is neutral in a WSLS population at T = 5; WSLS strictly stable at
T = 4.5.
**Figures:** `F7_evolution.png`, `F7b_wsls_vs_alld.png`. **Data:** `results/E5/survivors.md`,
`invasion_thresholds.md`, `shares.csv`.

| ε | uniform start | ALLD 50 % start | ALLD 95 % + TFT 5 % | WSLS 99 % + ALLD 1 % |
|---|---|---|---|---|
| 0 | 7 nice strategies coexist (12–17 % each), cooperation 1.00 | same 7 coexist | **TFT 100 %** | **ALLD 100 %** |
| 0.01 | GTFT 62 %, CTFT 19 %, TF2T 19 % (still moving) | **CTFT 83 %** | TFT 100 % | ALLD 100 % |
| 0.05 | **CTFT 100 %** | **CTFT 100 %** | **ALLD 100 %** | ALLD 100 % |

**Verdict: partly agrees; the noisy-evolution winner is CTFT, not WSLS.**
- ✅ **No noise: defectors die out and nice strategies remain.** They all earn exactly 3
  against each other, so selection is neutral among them. The final mix just reflects
  who did best during the brief period when defectors were still around.
- ❌→ **With noise, CTFT wins, not WSLS.** CTFT takes 100 % at ε = 0.05 from both
  starts. *Why:* evolution rewards doing well against whatever becomes common. CTFT
  vs CTFT recovers instantly from its own errors (2.896 at ε = 0.05), and forgiving rivals
  cannot invade it. In the E7 matrices at ε = 0.05, CTFT earns 2.907 against itself, while
  REP, GTFT, TF2T and AF earn only 2.81, 2.82, 2.82 and 2.67 against CTFT. Meanwhile CTFT
  earns more against each forgiver than they earn among themselves (e.g. 3.035 vs REP).
  Forgivers swallow CTFT's legitimate punishments; CTFT never swallows theirs. This matches
  **Boyd (1989)**: contrition is evolutionarily stable under implementation errors. WSLS
  loses because of B6 (see below).
- ✅ **B3, critical mass.** TFT invades ALLD from 5 % at ε = 0 and 0.01, but not at 0.05.
  The thresholds read off the matrices (`invasion_thresholds.md`) explain this exactly:
  TFT needs 0.53 % without noise (theory: 0.01/1.97 = 0.51 %), 1.2 % at ε = 0.01 and
  **5.1 % at ε = 0.05**, just above the 5 % starting share. Noise raises the critical mass
  because it erodes TFT's self-play payoff (2.39 at ε = 0.05).
- ✅ **B6, exactly as derived (F7b).** At T = 5 ALLD invades a 99 % WSLS population at
  *every* ε. ALLD earns (T+P)/2 = 3.008 ≈ R against WSLS (neutral to first order) and does
  better against itself than WSLS does against ALLD (1 vs 0.5). The computed WSLS share
  needed to resist is 1.017, which is impossible. **At T = 4.5, (T+P)/2 = 2.757 < 3, and WSLS
  repels ALLD at every ε**, needing only 67 % share. A tiny payoff change flips the outcome,
  precisely as the theory says.
- ⚠️ **No cycles** (ALLC → ALLD → TFT) appeared: replicator dynamics without mutation cannot
  re-introduce extinct strategies, so a cycle cannot restart once ALLC is gone.

## E6: Shadow of the future (RQ6, B1, B2)

**Prediction:** cooperation collapses below δ ≈ 0.5 and is stable above δ ≈ 0.667.
**Figure:** `F8_shadow_of_future.png` (the main theory-vs-simulation plot). **Data:**
`results/E6/cooperation_vs_delta.md`, `equilibria.csv`.

Equilibrium cooperation (mean of 30 seeds, ε = 0): 0.00 for δ ≤ 0.40 · 0.08 at 0.45 ·
**0.28 at 0.50** · 0.37 at 0.55 · 0.69 at 0.60 · **0.78 at 0.65** · 0.86 at 0.70 ·
≥ 0.96 from 0.80 · 1.00 from 0.85.

**Verdict: agrees.** Cooperation is zero below δ = 0.45 and rises steeply across the
predicted band [0.5, 0.667], passing 50 % at δ ≈ 0.57 (inside the band). It is near-total
from δ ≈ 0.8. With noise the curve is lower and less steep (ε = 0.05: 0.20 at δ = 0.5,
0.47 at 0.65, 0.91 at 0.99). Noise raises the δ needed for cooperation, because
retaliation is triggered by errors as well as by cheating. The transition is a ramp rather
than a step because B1/B2 describe *equilibria*, while the simulation starts from a
uniform mix and lands in mixed populations near the thresholds.

## E7: Original strategies (RQ7)

**Predictions:** `predictions.md` (RQ7 section, committed before E7 ran).
**Figures:** `F9_niche_map.png`, `F9b_originals_noise.png`. **Data:** `results/E7/`.

Tournament rank among 15 strategies (`noise_rank_by_epsilon.md`):

| ε | 0 | 0.005 | 0.01 | 0.02 | 0.05 | 0.1 | 0.2 |
|---|---|---|---|---|---|---|---|
| **REP** | **1** | **1** | **1** | **1** | **1** | 2 | 7 |
| **AF** | 3 | 4 | 4 | 4 | 5 | 5 | 12 |
| **PF** | 10 | 9 | 9 | 9 | 10 | 9 | 13 |
| **GWA** | 9 | 13 | 14 | 14 | 15 | 15 | 8 |
| GTFT (ref.) | 2 | 2 | 2 | 2 | 2 | 3 | 9 |
| GRIM (ref.) | 8 | 10 | 12 | 13 | 13 | 13 | 2 |

| Strategy | Prediction | Result | Verdict |
|---|---|---|---|
| **REP** | (a) top half at 0.02 ≤ ε ≤ 0.1 | **1st for every ε ≤ 0.05**, 2nd at 0.1 | ✅ better than predicted. But its lead over GTFT is within the CIs (ε = 0.01: 2.548 [2.519, 2.587] vs 2.543 [2.519, 2.577]): a statistical tie for first. |
| | (b) small loss vs ALLD | 0.958 vs TFT's 0.990 | ✅ |
| | (c) close to TF2T at every ε | clearly *above* TF2T (2.750 vs 2.662 at ε = 0); 7th vs 14th at ε = 0.2 | ❌ REP is less exploitable than TF2T (vs PF: 2.48 vs 1.51) |
| **AF** | (a) within CI of GTFT or above, 0.005 ≤ ε ≤ 0.1 | 0.05–0.10 below GTFT; CIs just miss (ε = 0.01: 2.441 [2.387, 2.510] vs 2.543) | ❌ |
| | (b) harder on ALLD than GTFT | 0.959 vs GTFT's 0.654 | ✅ |
| | (c) survives evolution at ε = 0.01 | extinct; CTFT 80 %, GTFT 10 %, TF2T 9 % | ❌ |
| **GWA** | (a, PRD) beats GRIM for every ε > 0 | **below GRIM at every ε > 0** (e.g. 1.912 vs 2.007 at ε = 0.05) | ❌ |
| | (b, mine) ranks below TFT and the forgivers | yes, last or nearly last | ✅ |
| | (c) dies out in evolution at ε ≥ 0.01 | yes | ✅ |
| **PF** | (a) best score vs ALLC | 4.937, second only to ALLD (5.0) | ✅ (best non-trivial) |
| | (b) mid-table, ranks 5–10 | ranks 9–10 for ε ≤ 0.1 | ✅ |
| | (c) dies out in evolution | yes | ✅ |
| **Niche map** | CTFT holds noisy long games; no original wins at δ < 0.5 | CTFT dominates ε ≥ 0.01, δ ≥ 0.85; ALLD dominates every cell δ ≤ 0.55; originals only lead mixed, low-share cells (AF at ε = 0.005, δ = 0.85–0.9; GWA at δ = 0.7–0.75) | ✅ |

**Explanations (the game theory):**
- **REP wins tournaments** because a reputation (exponentially weighted average) separates
  *rare* defections from *persistent* ones. One noise error moves it from 1 to 0.8 (no
  retaliation, no echo). A persistent defector is cut off after 4 rounds. Unlike TF2T it is
  not fooled by alternating exploitation (PF, STFT). **But it does not win evolution**,
  because forgiving strategies are invadable by CTFT (see E5).
  **Lesson: tournament success ≠ evolutionary success.**
- **AF falls short** because its noise estimator confuses *retaliation for its own
  punishment* with *deliberate defection*. When AF punishes a TFT-like player, the replies
  are "non-surprise" defections, so AF's forgiveness g drops exactly when forgiving
  would end the echo (AF vs JOSS: 1.85 vs GTFT's 2.56). Inferring intent from behaviour is
  hard when your own behaviour shapes the evidence.
- **GWA is worse than GRIM**, refuting the PRD's prediction (`results/E7/noise_matrices.csv`,
  ε = 0.05). Parole requires the opponent to cooperate *while being punished*. Retaliators
  (TFT, CTFT) never do, so against them GWA behaves like GRIM. The opponents who *do*
  cooperate under punishment are the unconditional ones that GRIM profitably exploits after
  a noise trigger (GRIM vs ALLC 4.40, WSLS 2.90, RAND 2.89). GWA gives that profit back by
  pardoning them (3.25, 2.73, 2.67). Amnesty is offered to exactly the opponents who don't
  need it.
- **PF** confirms the PRD: probing pays only when unconditional cooperators exist, which
  evolution removes.

## R1: Robustness to the strategy pool

**Figure:** `F11_robustness_pools.png`. **Data:** `results/R1/pool_scores.csv`,
`pool_survivors.md`.

| Conclusion | Full pool | Nice only | Many exploiters | Random 8 | Holds? |
|---|---|---|---|---|---|
| Nice strategies above non-nice, ε = 0 | ✅ | n/a | ✅ (top 5 all nice) | ✅ | **Yes** |
| A forgiving strategy (GTFT/TF2T/CTFT) beats TFT at ε = 0.05 | ✅ | ✅ (CTFT 1st) | ✅ (TF2T 1st) | ✅ (TF2T 1st) | **Yes** |
| GRIM collapses under noise | 7th→10th | 3rd→7th | 5th→9th | 6th→8th | **Yes** |
| GTFT or TF2T is the top tournament strategy at ε = 0 | ✅ | ❌ (all score exactly 3: ranks are ties) | ✅ | ✅ | Yes where ranks are meaningful |
| CTFT dominates noisy evolution | ✅ | ✅ (ε = 0.05) | CTFT not in pool: **GTFT 61 % + TF2T 33 %** win | ✅ | **Yes, or forgivers win when CTFT is absent** |
| Defectors win at ε = 0.2 | ✅ ALLD 1st | GRIM 1st | JOSS(0.3) 1st, ALLD 2nd | STFT 1st | **Yes** (a non-forgiving strategy wins) |

The core claims survive every pool. Only the identity of the single best strategy depends
on the pool.

## R2: Robustness to payoffs (T = 4.5, T = 5.9)

**Figure:** `F10_payoff_thresholds.png`. **Data:** `results/R2/payoff_cooperation_vs_delta.md`,
`payoff_survivors.md`, `payoff_equilibria.csv`.

*Note:* the PRD's T = 6 is not a valid Prisoner's Dilemma with R = 3, S = 0 (2R = T + S),
so T = 5.9 was used (decision D33).

- ✅ **The thresholds move with T as B1/B2 predict.**
  - **T = 4.5** (B1 = 0.43, B2 = 0.50): cooperation is 0 up to δ = 0.45, then 0.23 at
    0.50 and 0.73 at 0.55. It switches on right at B2.
  - **T = 5** (B2 = 0.667): rises 0.45 → 0.70.
  - **T = 5.9** (B1 = 0.59, B2 = 0.97): full cooperation (≥ 0.98) only from δ = 0.90.
- ❗ **A surprise at T = 5.9, explained:** partial cooperation (about 0.5) appears *early*, at
  δ = 0.5–0.7. The equilibrium populations there are STFT (30–43 %), JOSS (12–32 %) and
  TFT/CTFT, which lock into C/D alternation. With T = 5.9 alternation pays
  (T+S)/2 = 2.95, almost R = 3, so "taking turns" is nearly as good as cooperating. This is
  exactly why a PD requires 2R > T + S, and why T = 6 had to be excluded.
- ✅ **B6 again:** WSLS repels ALLD at T = 4.5 and is invaded at T = 5.9, just as at T = 5.
- ✅ **CTFT still wins noisy evolution** (ε = 0.05) at both T values.

---

## Answer to the title question: does forgiveness pay?

**Yes, when mistakes happen but are rare, and in moderate doses.**
1. **When:** with any noise at all (ε ≥ 0.005), strict retaliation is costly. TFT vs TFT drops
   from 3 to 2.25 (B4, confirmed), GRIM collapses, and forgiving strategies lead every
   tournament up to ε = 0.05 in every pool tested. But at ε = 0.2 defections carry no
   information, and unforgiving strategies (ALLD, GRIM) win.
2. **How much:** forgiving about 15–35 % of defections is best (GTFT plateau, E4), close to
   Nowak & Sigmund's 1/3. Beyond 1/2, ALLD earns more than cooperators (exactly the B5 bound,
   F6b). Less forgiveness is needed in shorter games (δ = 0.9: best g = 0.2).
3. **What kind:** in evolution, the winning "forgiveness" is *contrition*, forgiving the
   opponent's punishment of *your own* mistakes (CTFT), rather than generosity toward the
   opponent's mistakes. Generous strategies win tournaments but are invaded by contrite ones.
4. **Shadow of the future:** none of this works unless δ exceeds about 0.5–0.67 (B1/B2,
   confirmed in F8 and F10). Below that, ALLD takes over regardless of forgiveness.
