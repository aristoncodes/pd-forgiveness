# Presentation plan (12 slides, about 12–15 minutes)

One message per slide. Every number comes from `notes/findings.md`.

| # | Title | Show | Say (the one sentence to land) |
|---|---|---|---|
| 1 | Does forgiveness pay? | Title; "Aditya Yadav · Game Theory · Instructor: Akash Chauhan"; one-line answer: "Yes, when mistakes are rare, in moderate doses, and contrition beats generosity." | Repeated PD with noise and evolution, tested against six theory benchmarks. |
| 2 | The dilemma and the shadow of the future | Payoff table (T=5, R=3, P=1, S=0); δ = continuation probability, mean 1/(1−δ) rounds | Defecting wins any single round; only the future makes cooperation rational. |
| 3 | Why noise matters | F5 (move traces) | One accidental D makes TFT echo forever; WSLS repairs it in two rounds. |
| 4 | Method | Pipeline diagram (docs/M7_wrap_up.md); 11 known + 4 original strategies; 50 reps, 95 % CIs, fixed seeds, 54 tests | We trust the code because it reproduces exact answers first (TFT vs ALLD = 0.9 / 1.4). |
| 5 | Baseline: Axelrod reproduced | F2 | All 7 nice strategies beat all 4 nasty ones; ALLD wins 9 of 10 duels yet comes last. |
| 6 | Theory check: the echo | F4 | TFT vs TFT drops to 2.25 = (R+S+T+P)/4 for *any* noise, exactly as derived. |
| 7 | Noise reshuffles the ranking | F3 | Forgivers lead up to 5 % noise; GRIM collapses; at 20 % noise the unforgiving win again. |
| 8 | How much forgiveness? | F6 + F6b | Best generosity 0.15–0.35, around 1/3; above ½ ALLD out-earns cooperators, exactly the B5 bound. |
| 9 | Evolution | F7 + F7b | Under noise Contrite TFT takes over; WSLS loses to ALLD unless R > (T+P)/2 (T = 5 vs 4.5). |
| 10 | Theory vs simulation: shadow of the future | F8 (+ F10 as backup) | Cooperation switches on between δ = 0.5 and 0.667, where B1 and B2 say it should, and the switch moves with T. |
| 11 | Our original strategies | F9b + F9 | Reputation Tracker wins the tournament, but evolution still picks CTFT; two originals failed, for instructive reasons. |
| 12 | Conclusion and limitations | 4 bullets from findings → "Answer to the title question"; F11 for robustness | Holds across 4 pools and 3 payoff sets; not tested: Moran, perception noise, ZD. |

**Backup slides:** F1 (payoff matrix), F10 (thresholds vs T), F11 (pools), the B4 derivation,
the invasion-threshold table (`results/E5/invasion_thresholds.md`).
