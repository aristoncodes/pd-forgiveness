# Likely presentation questions, with answers

Grows with each milestone. Practise answering these without notes.

## Model and code (M1)

**Q: Why a random game length instead of, say, 100 rounds?**
With a known last round, defecting in round 100 is dominant. Knowing that, round 99 is
effectively the last, and so on back to round 1 (backward induction). The only equilibrium is
always-defect. A random end, continuing with probability δ, removes the "last round", so
cooperation can be sustained.

**Q: What does δ mean intuitively?**
How much the future matters (the "shadow of the future"). The expected number of rounds is
1/(1−δ): δ = 0.9 gives 10 rounds, δ = 0.99 gives 100. It also works like a discount factor.

**Q: Why report average payoff per round?**
Games have different lengths, so totals are not comparable. The average puts every match on
the same 0–5 scale, where R = 3 is "full cooperation".

**Q: What is implementation noise?**
A "trembling hand": you mean to cooperate, but with probability ε a defection comes out (or
the reverse). Both players see what actually happened, but not what was intended.

**Q: How do you know the simulator is correct?**
28 automated tests check exactly known answers (e.g. TFT vs ALLD over 10 rounds = 0.9 vs
1.4) and statistical properties (flip rate, mean game length, TFT-vs-TFT = 2.25 under noise).
Experiments run only after the tests pass.

**Q: How is it reproducible?**
Every run starts from a seed. Each match gets its own seed, split into independent
streams for noise and for each player. Same seed gives a bit-for-bit identical result.

**Q: Why does TFT vs TFT go to 2.25 and not to 1 (mutual defection)?**
One error starts an echo (C,D)→(D,C)→…; the next error is equally likely to send the pair to
(D,D) or back to (C,C). In the long run all four outcomes are equally likely, so the average
is (3+0+5+1)/4. See `theory_derivations.md`, B4.

**Q: Isn't CTFT cheating, since it knows its own intended move?**
No. Any real player knows what they *meant* to do. CTFT never sees the opponent's intentions
or the noise itself.

## Tournament and E1 (M2)

**Q: TFT is famous for winning Axelrod's tournaments. Why is it only 4th here?**
Our pool contains JOSS (random sneaky defections) and STFT (opening D). Both trigger TFT's
echo of retaliation. TF2T and GTFT forgive isolated defections and recover. Axelrod himself
noted that TF2T would have won his first tournament. Rankings depend on who else is playing.
The robust result is that *nice* strategies beat non-nice ones, and that holds perfectly
here (all 7 above all 4).

**Q: How can ALLD win almost every head-to-head match but come last?**
Head-to-head, ALLD never scores less than its opponent: it never gets S. But it scores
about 1 per round against anyone who retaliates, while nice strategies earn 3 among
themselves. The IPD rewards eliciting cooperation, not beating your opponent.

**Q: Why do you include self-play?**
For evolution: a common strategy mostly meets copies of itself, so A[i][i] is what a
population of i earns. The PRD requires it (FR3.1).

**Q: How exactly is "average payoff per round" computed?**
Total payoff over all 50 repetitions divided by total rounds over all 50 repetitions. That
equals the normalised discounted payoff in the theory, so the two compare like for like.
(Decision D14.)

**Q: What are common random numbers?**
In each repetition, every pairing plays a game of the same random length. Differences
between strategies then come from their behaviour, not from luckier game lengths.

**Q: Where do the confidence intervals come from?**
A bootstrap: resample the 50 repetitions with replacement 2,000 times, recompute the score
each time, and take the 2.5th and 97.5th percentiles.

## Noise and echo (M3)

**Q: Why does TFT's payoff not keep falling as noise increases?**
B4: once a single error has happened, TFT vs TFT wanders uniformly over CC, CD, DC, DD, so
it averages 2.25 whatever ε is. More noise only gets it there faster.

**Q: Why do unforgiving strategies win at ε = 0.2?**
With 20 % random moves, a defection says almost nothing about intent. Forgiving it mostly
rewards exploiters, and the cooperation being protected is mostly gone anyway.

## Forgiveness dial and evolution (M4)

**Q: The theory says g* = 1/3, you found 0.2–0.3. Is the theory wrong?**
No. B5 is the most generosity a *population* can have while resisting invasion. Our measure
is a tournament score against a fixed pool that includes ALLD, RAND and JOSS, which profit
from every extra unit of generosity. The plateau (0.15–0.35) contains 1/3, and the separate
B5 bound g = ½ against ALLD is reproduced exactly (F6b).

**Q: Why does CTFT, not WSLS or GTFT, win evolution?**
Evolution rewards doing well against whatever becomes common. CTFT fixes its own errors
instantly and cannot be invaded by generous strategies: they forgive CTFT's justified
punishments, while CTFT punishes their errors. At ε = 0.05, CTFT earns 2.907 against itself
and the forgivers earn about 2.81 against CTFT. WSLS loses to ALLD (B6). This matches Boyd
(1989).

**Q: What is B6 and why is it interesting?**
WSLS alternates C/D against ALLD, giving ALLD (T+P)/2 = 3 = R. ALLD is then neutral among
WSLS players and wins outright against itself, so it takes over. Lowering T to 4.5 makes
(T+P)/2 = 2.75 < 3, and WSLS repels it. A tiny payoff change flips the outcome, as the
algebra predicts (F7b).

**Q: What is the "critical mass" for TFT?**
The share of TFT above which it beats ALLD: x* = (d−b)/((a−c)+(d−b)) from the 2×2 payoff
matrix. At δ = 0.99 it is only 0.51 % without noise, but 5.1 % at ε = 0.05. That is why 5 % TFT
invades at low noise and fails at ε = 0.05.

**Q: Why no cycles?**
Replicator dynamics without mutation cannot bring back an extinct strategy. Cycles like
ALLC → ALLD → TFT need mutation (a stretch goal).

## Shadow of the future (M5)

**Q: Why is the transition a ramp, not a sharp step at 0.5 or 0.667?**
B1/B2 say when cooperation *can* be an equilibrium. Our populations start from a uniform mix
and evolve; near the thresholds several outcomes are possible, so the average over 30 seeds
is intermediate. The ramp sits inside the predicted band (50 % cooperation at δ ≈ 0.57).

**Q: How do you know it is not a coincidence?**
F10: change T and the thresholds move as the formulas say. T = 4.5 switches on at about 0.5
(B2 = 0.5); T = 5.9 needs about 0.9 (B2 = 0.97).

## Original strategies (M6)

**Q: Your Reputation Tracker wins the tournament. Is it the best strategy?**
Not in evolution. It ties with GTFT for first in tournaments, but CTFT invades it (3.035
against REP vs REP's 2.947 against itself). Tournament ranking measures performance against
a fixed field; evolutionary stability measures resistance to invasion. They differ.

**Q: Why did Grudger with Amnesty do worse than GRIM?**
Parole requires cooperating while being punished. Retaliators never do, so GWA ≈ GRIM
against them. Unconditional cooperators always do, and GRIM was exploiting them after noise
triggered it (GRIM vs ALLC 4.40). GWA pardons them and loses that income (3.25).

**Q: Why did Adaptive Forgiver underperform GTFT?**
It estimates "accidental vs deliberate" from the opponent's defections, but when AF itself
punishes, the opponent's retaliation looks deliberate. Its forgiveness drops exactly when
it should forgive, so it gets stuck in echoes, e.g. against JOSS (1.85 vs GTFT's 2.56).

**Q: Weren't you tempted to change predictions after seeing results?**
The RQ7 predictions were committed (commit d1ba747) before E7 ran; Git timestamps prove it.
Three of AF's and GWA's predictions failed, and we report that.

## Robustness and limitations (M6–M7)

**Q: Do results depend on which strategies you included?**
Rankings do; conclusions don't. In four pools (full, nice only, many exploiters, random 8),
forgivers beat TFT under noise, GRIM collapses, and unforgiving strategies win at ε = 0.2
(F11).

**Q: Why T = 5.9 instead of T = 6?**
T = 6 with R = 3, S = 0 gives 2R = T + S, so it is not a strict Prisoner's Dilemma. At
T = 5.9 we even *see* the problem: alternating C/D pays almost as much as cooperating, and
alternating populations appear.

**Q: What are the main limitations?**
Infinite-population replicator dynamics (no drift; the Moran process was not done);
implementation noise only (no perception noise); no mutation; tournament rankings depend
on the pool; strategies are hand-designed rather than evolved.
