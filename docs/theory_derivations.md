# Theory derivations: benchmarks B1–B6

Study these. They are the "theory" half of every theory-vs-simulation comparison, and the
formulas are implemented in `pd/theory.py`.

Default payoffs: T = 5 (temptation), R = 3 (reward), P = 1 (punishment), S = 0 (sucker).

## Tool: the value of a payoff stream

The game continues after each round with probability δ. A payoff stream u₀, u₁, u₂, … is
worth V = u₀ + δu₁ + δ²u₂ + … in expectation, because round t is reached with probability δᵗ.
Two series we use again and again:

- constant x forever: x + δx + δ²x + … = **x / (1 − δ)**
- x now, then y forever: **x + δy / (1 − δ)**

Multiplying V by (1 − δ) gives the **average payoff per round** (E[total] / E[rounds]), which
is what the simulator reports.

---

## B1. Grim Trigger vs. a defector: δ ≥ (T − R)/(T − P) = 0.5

Against GRIM, a player who keeps cooperating gets R forever: **R / (1 − δ)**.
A player who defects gets T once, then GRIM punishes forever, so the best reply is to keep
defecting and get P: **T + δP / (1 − δ)**.

Cooperating is at least as good when

R/(1−δ) ≥ T + δP/(1−δ) ⟺ R ≥ (1−δ)T + δP ⟺ δ(T − P) ≥ T − R ⟺ **δ ≥ (T−R)/(T−P)**.

With defaults: (5−3)/(5−1) = 2/4 = **0.5**. *Intuition:* gain from cheating once (T − R = 2)
versus the loss per future round (R − P = 2), weighted by how much the future counts.

## B2. TFT is collectively stable: δ ≥ max((T−R)/(T−P), (T−R)/(R−S)) = 2/3

TFT must resist two kinds of cheats (Axelrod 1984 shows these are the two that matter):

1. **Always defect.** TFT then defects forever too, so this is exactly B1: δ ≥ 0.5.
2. **Alternate D, C, D, C, …** TFT plays C, D, C, D in reply, so the cheat earns T, S, T, S, …
   Value: (T + δS)/(1 − δ²). Cooperating earns R/(1−δ) = R(1+δ)/(1−δ²). Cooperating is at
   least as good when R(1+δ) ≥ T + δS ⟺ **δ ≥ (T−R)/(R−S)** = 2/3 ≈ 0.667.

TFT needs both, so δ ≥ 0.667. It is more demanding than GRIM because TFT forgives after a
single C, which an alternator can exploit.
**Prediction for E6:** cooperation should rise sharply between δ = 0.5 and δ = 0.667.

## B3. ALLD is always an equilibrium

Against ALLD, cooperating in any round gives S instead of P now and does not change ALLD's
future play. So D is the best reply in every round, at every δ: (ALLD, ALLD) is a Nash
equilibrium. A single TFT mutant in an ALLD population earns S + δP/(1−δ), less than the
P/(1−δ) the defectors earn among themselves, so it cannot invade alone. Cooperation needs a
**critical mass** of cooperators to begin with (tested in M4).

## B4. TFT vs. TFT under noise → (R+S+T+P)/4 = 2.25

Describe the pair by last round's actual moves (a, b): one of CC, CD, DC, DD. Both play TFT,
so next round they intend (b, a), the swap. Each intended move is then flipped with
probability ε.

- The swap is a permutation (it moves states around without merging them).
- The noise step is "doubly stochastic": every state is equally likely to be reached.

So the whole transition matrix is doubly stochastic, and the unique long-run distribution of
an ergodic doubly stochastic chain is **uniform**: each of CC, CD, DC, DD has probability 1/4.
Average payoff = (R + S + T + P)/4 = (3+0+5+1)/4 = **2.25**.

Notice: this holds for **any** ε > 0; ε only controls how fast the pair gets there (about
1/(2ε) rounds before the first error). One error causes the "echo"
(C,D) → (D,C) → (C,D) …, which only another error can end, and that error is as likely to
lead to DD as back to CC.

**WSLS recovers instead:** after an error (C,D): player 1 got S (lose → switch to D); player 2
got T (win → stay on D). Next (D,D): both lose → both switch → (C,C). Back to cooperation in
two rounds, so WSLS vs WSLS stays near R = 3.

## B5. Optimal generosity g* = min(1 − (T−R)/(R−S), (R−P)/(T−P)) = 1/3

More generosity g means faster recovery from noise errors, so we want g as large as
possible, but GTFT must not be invadable by cheats (long games, δ → 1, small noise):

1. **vs ALLD:** GTFT cooperates with probability g, so ALLD earns gT + (1−g)P per round. It
   must earn less than R: g < (R−P)/(T−P) = 2/4 = **1/2**.
2. **vs an alternator (D, C, D, C):** every two rounds the alternator earns T (when GTFT
   cooperates after its C) plus gR + (1−g)S (GTFT forgives its D with probability g). This
   must be less than 2R: g(R−S) < 2R − T − S ⟺ g < 1 − (T−R)/(R−S) = **1/3**.

The most generous rule that still resists both is g* = min(1/3, 1/2) = **1/3**
(Nowak & Sigmund 1992). **Prediction for E4:** an interior optimum near g = 1/3; very high g
gets exploited by ALLD.

## B6. WSLS vs ALLD: (T + P)/2 = 3 = R, so ALLD is *neutral*

WSLS against ALLD: C (gets S, lose → switch), D (gets P, lose → switch), C, D, …
ALLD earns T, P, T, P: average **(T + P)/2 = 3**, exactly R. A WSLS population earns R = 3.
So with default payoffs ALLD does **exactly as well** as WSLS inside a WSLS population: it
is neutral and can drift in. WSLS is strictly stable only if **R > (T+P)/2**. With T = 4.5:
(4.5 + 1)/2 = 2.75 < 3, so WSLS becomes strictly stable. **Test in M4:** rerun evolution with
T = 4.5 and compare.

---

## Extra: critical mass (used for B3 and B6 checks)

With two strategies and payoff matrix [[a, b], [c, d]] (rows/cols = strategy 1, strategy 2),
strategy 1 at share x has fitness x·a + (1−x)·b, and strategy 2 has x·c + (1−x)·d. Strategy 1
does better exactly when

**x > x* = (d − b) / ((a − c) + (d − b))**.

**TFT vs ALLD** (per-round payoffs at δ, from `theory.tft_alld_matrix`): a = R = 3,
b = (1−δ)S + δP, c = (1−δ)T + δP, d = P = 1. At δ = 0.99: b = 0.99, c = 1.04, so
x* = 0.01/1.97 ≈ **0.51 %**. A tiny cluster of TFT can take over an ALLD world, but a single
mutant in an infinite population cannot (B3). The simulated matrix gives 0.53 %. Noise
raises it (1.2 % at ε = 0.01, 5.1 % at ε = 0.05) because TFT earns less against itself.

**WSLS vs ALLD:** with T = 5, a = 3, c = (T+P)/2 = 3, b = 0.5, d = 1, so
x* = 0.5/(0 + 0.5) = 1: WSLS would need 100 % of the population (neutral to first order;
ALLD wins on the second-order term). With T = 4.5, c = 2.75, so x* = 0.5/(0.25 + 0.5) = 2/3.
WSLS resists as long as ALLD has under 1/3 of the population.
