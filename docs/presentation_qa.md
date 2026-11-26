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
