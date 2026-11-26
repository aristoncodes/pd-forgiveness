# Glossary

**Prisoner's Dilemma (PD):** two players choose C or D at the same time. T > R > P > S, so D
is better for you whatever the other does, yet mutual C (R, R) beats mutual D (P, P).

**T, R, P, S:** Temptation (5, defect on a cooperator), Reward (3, mutual C), Punishment (1,
mutual D), Sucker (0, cooperate against a defector).

**Repeated / iterated PD:** the stage game played many times against the same opponent.

**δ (delta), continuation probability, "shadow of the future":** chance the game goes on
after each round. Expected length 1/(1−δ).

**ε (epsilon), implementation noise:** chance an intended move is flipped.

**Perception noise (stretch goal):** the move is played as intended, but the *other* player
misreads it.

**Nice:** never the first to defect. **Retaliatory:** punishes a defection.
**Forgiving:** returns to cooperation after punishing. **Clear:** easy to recognise.
(Axelrod's four properties of TFT.)

**Echo effect:** under TFT, one error causes endless alternating retaliation.

**Nash equilibrium:** no player gains by changing strategy alone.

**Collectively stable (Axelrod):** a population playing the strategy cannot be invaded by a
single mutant that does better against it.

**Evolutionarily stable strategy (ESS):** a strategy that resists invasion by any small
group of mutants.

**Round-robin tournament:** every strategy plays every strategy, including itself.

**Payoff matrix A:** A[i][j] = average per-round payoff of strategy i against strategy j.

**Replicator dynamics:** strategies grow in proportion to how much better than average they
score: x_i ← x_i · f_i / f̄.

**Moran process (stretch goal):** finite-population evolution where one individual reproduces
and one dies each step.

**Common random numbers (CRN):** using the same random game lengths for all pairings, so
differences between strategies are not blurred by different luck.

**95 % confidence interval (CI):** a range that, over repeated experiments, contains the true
mean 95 % of the time.

**Zero-Determinant (ZD) strategy (stretch goal):** a memory-one strategy that fixes a linear
relation between its own and its opponent's payoffs (Press & Dyson 2012); "extortioners"
guarantee themselves more than the opponent.
