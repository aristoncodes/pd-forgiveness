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
| RQ7 | Do original strategies beat known ones anywhere in (ε, δ)? | Filled in at M6, before the originals are tested. | Design rationale | E7 |
