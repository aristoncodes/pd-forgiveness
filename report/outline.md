# Report outline: Does Forgiveness Pay?

Target 8–15 pages. Each results subsection follows **prediction → figure → agreement →
explanation**. Numbers come from `notes/findings.md` (which cites the result files).

## 1. Abstract (150 words)
Question: does forgiveness pay in the repeated Prisoner's Dilemma under implementation
noise, and how much? Method: a reproducible simulator; 15 strategies (11 classic + 4
original); round-robin tournaments over noise ε and continuation probability δ; replicator
dynamics; comparison with six analytic benchmarks. Three findings with numbers:
1. Noise ruins strict reciprocity: TFT vs TFT falls from 3 to 2.25 for any ε > 0 (B4
   confirmed), and forgiving strategies lead tournaments up to ε = 0.05, but not at ε = 0.2.
2. Optimal generosity is a plateau g ≈ 0.15–0.35 around Nowak & Sigmund's 1/3; ALLD exploits
   g > ½ exactly as B5 predicts.
3. Cooperation emerges between δ = 0.5 and 0.667 (B1/B2) and the thresholds shift with T;
   under noise evolution selects Contrite TFT, while our Reputation Tracker wins
   tournaments but not evolution.

## 2. Introduction
- The cooperation puzzle; the one-shot PD; why repetition helps (shadow of the future).
- Axelrod's tournaments (1980, 1984): TFT, the properties nice/retaliatory/forgiving/clear.
- Why noise matters: real interactions contain mistakes; the echo of TFT; Nowak & Sigmund's
  GTFT (1992) and WSLS (1993); Wu & Axelrod's CTFT (1995); Boyd (1989).
- Research questions RQ1–RQ7 (from `notes/predictions.md`).

## 3. Model
- Stage game and PD conditions; geometric game length with mean 1/(1−δ); implementation
  noise ε.
- Strategies: appendix table; code interface.
- Tournament: round-robin with self-play, 50 repetitions, common random numbers; the
  payoff-per-round estimator (ratio of sums = normalised discounted payoff, D14); bootstrap
  CIs.
- Evolution: discrete replicator dynamics; initial conditions; extinction threshold.

## 4. Theory
Derivations B1–B6 from `docs/theory_derivations.md`, plus the invasion-threshold formula.
State each prediction explicitly.

## 5. Results
- 5.1 E1 baseline (F1, F2): nice > nasty; ALLD's paradox; TF2T on top, explained by JOSS/STFT.
- 5.2 E2 noise sweep (F3): forgivers lead; GRIM collapses; high-noise inversion.
- 5.3 E3 echo (F4, F5): B4 confirmed; WSLS/CTFT self-repair.
- 5.4 E4 forgiveness dial (F6, F6b): plateau around 1/3; exact ½ bound; shift with δ and ε.
- 5.5 E5 evolution (F7, F7b): neutrality without noise; CTFT under noise (Boyd 1989); critical
  mass rising with noise; B6 at T = 5 vs 4.5.
- 5.6 E6 shadow of the future (F8): transition inside [0.5, 0.667]; noise delays it.

## 6. Original strategies (E7; F9, F9b)
Design rationale and pre-registered niche for AF, GWA, PF, REP; prediction-vs-result table;
explanations (REP's reputation filter; why CTFT still invades it; AF's contaminated
evidence; GWA's misdirected amnesty; PF's vanishing prey).

## 7. Robustness and limitations
- R1 pools (F11): which conclusions hold (all core ones) and which don't (the single winner).
- R2 payoffs (F10): thresholds move with T; the T = 5.9 alternation effect; why T = 6 is
  invalid.
- Limitations: infinite population (no Moran/drift), no mutation (no cycles), implementation
  noise only, fixed hand-designed pools, memory-limited strategies, discrete-time replicator
  dynamics.
- Future work: Moran process (N = 50, 200), perception noise, Zero-Determinant extortioners,
  mutation–selection balance.

## 8. Conclusion
Answer directly (from findings → "Answer to the title question"): forgiveness pays when
mistakes are rare but present, in doses around 1/3 and never above ½. Under evolution the
winning form is contrition rather than generosity. It all requires δ above about 0.5–0.67.

## 9. References and appendix
References: PRD section 14 (verify volumes and pages). Appendix: strategy table (rule,
nice?, source), parameter tables (`configs/`), test list, reproducibility statement
(117 s, byte-identical rerun).
