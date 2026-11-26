# M1: Engine, strategies and tests

**Status:** done. 28/28 tests pass, `ruff` is clean, code is formatted with `black`.

## What was built

| File | What it does |
|------|--------------|
| `pd/game.py` | `Payoffs` (validated T > R > P > S, 2R > T + S), `draw_length` (Geometric game length), `play_match` (one match with noise) and `MatchResult` (histories, totals, per-round averages, cooperation rates, noise count). |
| `pd/strategies/base.py` | `Strategy` interface (`reset`, `move`), `register` decorator, `make("GTFT", g=0.2)` registry. |
| `pd/strategies/classic.py` | ALLC, ALLD, RAND, TFT, GRIM |
| `pd/strategies/forgiving.py` | GTFT(g), TF2T, WSLS, STFT, CTFT, JOSS(p) |
| `pd/theory.py` | Benchmark formulas B1–B6 (derived in `theory_derivations.md`). |
| `tests/test_game.py`, `tests/test_theory.py` | 28 tests with exactly known answers. |

## How one match works (walk through this in the presentation)

```
play_match(s1, s2, payoffs, delta, epsilon, rng, n_rounds=None)
  1. split rng into 3 independent streams: noise | s1's dice | s2's dice
  2. n = n_rounds, or draw n ~ Geometric(1 - delta)        (mean 1/(1-delta))
  3. reset both strategies (clear memory, hand them their dice)
  4. pre-draw an n×2 table of noise flips (True with probability epsilon)
  5. for each round:
        a = s1.move(h1, h2)   b = s2.move(h2, h1)      # intended moves
        h1.append(a XOR flip1) h2.append(b XOR flip2)   # actual moves (both see these)
  6. payoff table [[R,S],[T,P]] looked up for every round → totals and averages
```

Key point: strategies return what they **intend**; the engine decides what **happens**. A
strategy cannot see the noise, only the resulting actual moves. The one exception is the
strategy's own memory of what it meant to do, which CTFT uses (decision D8).

## The 11 strategies at a glance

| Code | Nice? | Retaliates? | Forgives? | One-line rule |
|------|-------|-------------|-----------|---------------|
| ALLC | yes | no | always | Always C |
| ALLD | no | — | never | Always D |
| RAND | — | — | — | C with prob. 0.5 |
| TFT | yes | yes, at once | after one C | Copy the opponent's last move |
| GRIM | yes | yes, forever | never | C until the first opponent D, then D forever |
| GTFT(g) | yes | usually | randomly (prob. g) | TFT, but forgive a D with prob. g |
| TF2T | yes | after 2 Ds | yes | D only after two opponent Ds in a row |
| WSLS | yes | yes | yes, self-correcting | Repeat my move after R/T, switch after P/S |
| STFT | no | yes | after one C | D first, then copy |
| CTFT | yes | yes | apologises for its own errors | TFT, but accept one punishment after my own mistake |
| JOSS | no (sneaky) | yes | after one C | TFT, but defect 10 % of the time instead of cooperating |

"Nice" = never the first to defect (Axelrod's term).

## What the tests prove (and why each matters)

| Test | Known answer | Why it matters |
|------|-------------|----------------|
| ALLC vs ALLD, 10 rounds | 0 and 5 per round | Payoff table is wired correctly |
| TFT vs ALLD, 10 rounds | TFT plays C then 9 Ds; 0.9 vs 1.4 | History is passed in the right order |
| TFT/GRIM/WSLS/TF2T/GTFT/CTFT self-play | always C, 3 per round | No "nice" strategy defects first |
| WSLS vs ALLD | C, D, C, D…; ALLD gets 3 | Benchmark B6 holds in the engine |
| TF2T vs a scripted opponent | ignores a single D, punishes D, D | Deterministic forgiveness works |
| GRIM vs one D | D forever | Grim never forgives |
| STFT vs TFT | locked in D/C alternation | Cost of a nasty opening |
| GTFT(0) = TFT, GTFT(1) = ALLC | identical histories, **with noise** | The dial's endpoints are right and the rng streams are separate (D4) |
| CTFT script | apologises once, then punishes real Ds | Contrition logic |
| JOSS vs ALLC | defects ≈ 10 % | Sneak rate |
| Same seed / different seed | identical / different | Reproducibility (FR1.5) |
| 10⁶ moves at ε = 0.05 | flip rate 0.05 ± 0.001 | Noise is applied correctly |
| Mean length, δ = 0.9, 0.99 | within 2 % of 10 and 100 | Game length is right |
| TFT vs TFT, ε = 0.05, 2000 rounds | ≈ 2.25 | Benchmark B4 (the echo effect) |
| WSLS, CTFT self-play, ε = 0.01 | > 2.85 | Error-correcting strategies recover |

Test output:

```
$ pytest -q
............................                                             [100%]
28 passed in 0.37s
```

## Things worth saying out loud in the presentation

1. **We trust the code because it reproduces exact answers first.** Every experiment depends
   on these tests passing.
2. **TFT vs TFT drops to exactly 2.25 under noise, whatever ε is.** The derivation (B4) is a
   neat Markov-chain argument, and the test confirms it in simulation.
3. **Separating random streams (D4) is what makes comparisons fair.** GTFT(0) and TFT give
   identical games, not just similar averages.
