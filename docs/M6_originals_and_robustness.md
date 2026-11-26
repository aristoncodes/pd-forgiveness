# M6: Original strategies (E7) and robustness (R1, R2)

**Status:** done. Figures F9, F9b, F10, F11. Predictions committed before testing (commit
d1ba747). Two robustness checks (pools and payoffs).

## The four originals (code: `pd/strategies/original.py`)
| Code | Rule | Idea |
|---|---|---|
| **AF** Adaptive Forgiver | TFT, but forgive a D with prob. ½·(surprise Ds + 1)/(all Ds + 2) | Defections "out of nowhere" look like noise; repeated ones look deliberate |
| **GWA** Grudger with Amnesty | GRIM with a 5-round sentence; parole if the opponent cooperated ≥ 3 of those 5 rounds | Keep the threat, allow redemption |
| **PF** Prober-Forgiver | Open C, D, C, C; exploit if no retaliation, else WSLS | Find and farm unconditional cooperators |
| **REP** Reputation Tracker | r ← 0.8 r + 0.2·[opponent cooperated]; cooperate iff r > 0.5 | Judge the recent record, not the last move |

## Results
- **REP wins the tournament** for every ε ≤ 0.05 (tied with GTFT within the CIs). It never
  dominates evolution.
- **AF:** consistently top 5, harder on ALLD than GTFT (0.96 vs 0.65), but 0.05–0.10 below
  GTFT under noise. Extinct in evolution.
- **GWA:** *worse* than GRIM under noise, which refutes the PRD's prediction. It does lead
  some mixed populations at δ = 0.7–0.75 with low noise (F9).
- **PF:** as predicted. Best against ALLC (4.94), mid-table overall, dies out in evolution.
- **Niche map (F9):** ALLD owns δ ≤ 0.55 regardless of noise. CTFT owns the noisy
  long-game region. Low-noise cells are mixed, neutral populations of nice strategies.

Full prediction-vs-result table: `notes/findings.md` → E7.

## Robustness
- **R1 pools (F11):** the main conclusions hold in all four pools: nice > non-nice,
  forgivers beat TFT under noise, GRIM collapses, and unforgiving strategies win at
  ε = 0.2. The identity of the single best strategy changes with the pool.
- **R2 payoffs (F10):** thresholds move as B1/B2 predict. At T = 5.9 half-cooperative
  alternating populations appear, because (T+S)/2 ≈ R. B6 holds at both T values.

## Why (the game theory)
- **REP** separates rare from persistent defection with an exponentially weighted average.
  But in evolution every forgiving strategy is invaded by CTFT, which punishes their errors
  while they forgive its punishments. **Tournament success ≠ evolutionary success.**
- **AF's flaw:** when AF punishes, the opponent's retaliation counts as "non-surprise"
  defection, so AF becomes less forgiving exactly when forgiving would end the echo. Your
  own behaviour contaminates the evidence you use to judge intent.
- **GWA's flaw:** parole goes to opponents who cooperate while being punished. Retaliators
  never do; unconditional cooperators always do, and those are exactly the opponents GRIM
  was profitably exploiting. Amnesty forgives the wrong people.

## Talking points
1. "Our Reputation Tracker beat every classic strategy in the noisy tournament, but
   evolution still picks Contrite TFT. Winning tournaments and being evolutionarily stable
   are different things."
2. "Two of our originals failed, and the failures teach the most: forgiveness based on
   inferred intent fails when your own actions shape the evidence (AF), and amnesty helps
   only those who didn't need it (GWA)."
