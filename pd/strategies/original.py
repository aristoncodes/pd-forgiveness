"""Original strategies (PRD 5.3). Each docstring gives the rule, the intuition and the
predicted niche; the predictions were committed in notes/predictions.md before E7 ran.

Want to add or change your own? See the TODO template at the bottom of this file.
"""

from __future__ import annotations

from .base import C, D, Strategy, register


@register
class AdaptiveForgiver(Strategy):
    """Adaptive Forgiver AF(g_max). Source: original (idea from the PRD, section 5.3).

    Rule: C in round 1; after an opponent C play C; after an opponent D cooperate with
    probability g = g_max · (s + 1) / (d + 2), where d counts the opponent's defections and
    s counts the "surprise" ones, i.e. defections that came right after a round of mutual
    cooperation (round 1 counts as following mutual cooperation).

    Intuition: a noise error looks like a defection "out of nowhere", while a deliberate
    defector keeps defecting after being punished. The share of surprise defections, s/d,
    estimates how much of the opponent's bad behaviour is accidental, and forgiveness is
    set to match. Against ALLD only the first D is a surprise, so g falls toward 0 (harder on
    defectors than GTFT). Against a noisy TFT most defections are surprises, so g stays near
    g_max (as forgiving as GTFT). The (+1, +2) terms are a prior of "half accidental" before
    any evidence. Default g_max = 1/2 is B5's upper bound (R − P)/(T − P).

    Predicted niche: moderate noise (0.005 ≤ ε ≤ 0.1) with long games; should match or beat
    GTFT(1/3). Weakness: JOSS's and RAND's sneaky defections also look like "surprises".
    """

    code = "AF"

    def __init__(self, g_max: float = 0.5):
        super().__init__()
        self.g_max = g_max
        self.name = "AF" if g_max == 0.5 else f"AF({g_max:.2f})"

    def reset(self, rng):
        super().reset(rng)
        self.defections = 0
        self.surprises = 0

    def move(self, my_hist, opp_hist):
        if not opp_hist:
            return C
        if opp_hist[-1] == C:
            return C
        self.defections += 1
        after_mutual_c = len(opp_hist) < 2 or (my_hist[-2] == C and opp_hist[-2] == C)
        self.surprises += after_mutual_c
        g = self.g_max * (self.surprises + 1) / (self.defections + 2)
        return C if self.rng.random() < g else D


@register
class GrudgerAmnesty(Strategy):
    """Grudger with Amnesty GWA(k, m). Source: original (idea from the PRD, section 5.3).

    Rule: cooperate until the opponent defects; then defect for a block of k rounds. At the
    end of the block, if the opponent cooperated in at least m of those k rounds, grant
    amnesty and return to cooperation; otherwise punish another k rounds and check again.
    Defaults k = 5, m = 3.

    Intuition: GRIM's permanent punishment turns one noise error into a lifetime of mutual
    defection. A fixed sentence with parole for good behaviour keeps the threat (an
    unrepentant defector like ALLD is punished forever) but lets a remorseful opponent back.

    Predicted niche (PRD): beats GRIM under noise while keeping GRIM's resistance to ALLD.
    Caveat (my own prediction): parole needs the opponent to cooperate *while being
    punished*, and retaliators (TFT, CTFT, GRIM) don't, so amnesty mostly helps against
    forgiving opponents.
    """

    code = "GWA"

    def __init__(self, k: int = 5, m: int = 3):
        super().__init__()
        self.k, self.m = k, m
        self.name = "GWA" if (k, m) == (5, 3) else f"GWA({k},{m})"

    def reset(self, rng):
        super().reset(rng)
        self.punishing = False
        self.seen = 0  # opponent moves observed in the current punishment block
        self.coops = 0  # how many of them were C

    def move(self, my_hist, opp_hist):
        if not opp_hist:
            return C
        if not self.punishing:
            if opp_hist[-1] == D:
                self.punishing, self.seen, self.coops = True, 0, 0
                return D
            return C
        self.seen += 1
        self.coops += opp_hist[-1] == C
        if self.seen == self.k:
            if self.coops >= self.m:
                self.punishing = False  # amnesty
                return C
            self.seen, self.coops = 0, 0  # another block
        return D


@register
class ProberForgiver(Strategy):
    """Prober-Forgiver PF. Source: original (idea from the PRD, section 5.3).

    Rule: open with C, D, C, C. If the opponent did not retaliate for the probe (no D in
    rounds 3-4), exploit it by defecting, until it fights back once; from then on, or
    straight away if it did retaliate, play WSLS.

    Intuition: unconditional cooperators are free money; a single probe finds them. WSLS
    afterwards repairs the relationship with retaliators (after the probe, TFT's one
    retaliation is followed by mutual cooperation).

    Predicted niche (PRD): wins in pools with many ALLC players, penalised by TFT and GRIM
    (GRIM never forgives the probe). Expected to die out in evolution once ALLC is gone.
    """

    code = "PF"
    OPENING = (C, D, C, C)

    def reset(self, rng):
        super().reset(rng)
        self.mode = None  # None during the opening, then "exploit" or "wsls"

    def move(self, my_hist, opp_hist):
        t = len(my_hist)
        if t < len(self.OPENING):
            return self.OPENING[t]
        if self.mode is None:
            self.mode = "wsls" if D in opp_hist[2:4] else "exploit"
        if self.mode == "exploit":
            if opp_hist[-1] == C:
                return D
            self.mode = "wsls"  # it fought back
        return my_hist[-1] ^ opp_hist[-1]  # WSLS


@register
class ReputationTracker(Strategy):
    """Reputation Tracker REP(alpha, threshold). Source: original (idea from the PRD, 5.3).

    Rule: keep a reputation score r for the opponent, starting at 1 (trust). After each round
    r <- (1 − alpha) r + alpha · [opponent cooperated]. Cooperate iff r > threshold.
    Defaults alpha = 0.2, threshold = 0.5.

    Intuition: judge the opponent on its recent record, not its last move. One defection only
    drops r from 1 to 0.8, so isolated noise errors are ignored and no echo starts. A
    persistent defector is cut off after 4 rounds (1 → 0.8 → 0.64 → 0.51 → 0.41 < 0.5). It
    is an exponentially weighted moving average, the "memory" of reputation.

    Predicted niche (PRD): robust to noise, slow to punish. Should do well at moderate to
    high noise (0.02 ≤ ε ≤ 0.1); pays a small price against ALLD (4 sucker rounds per game).
    """

    code = "REP"

    def __init__(self, alpha: float = 0.2, threshold: float = 0.5):
        super().__init__()
        self.alpha, self.threshold = alpha, threshold
        self.name = "REP" if (alpha, threshold) == (0.2, 0.5) else f"REP({alpha},{threshold})"

    def reset(self, rng):
        super().reset(rng)
        self.reputation = 1.0

    def move(self, my_hist, opp_hist):
        if opp_hist:
            cooperated = opp_hist[-1] == C
            self.reputation = (1 - self.alpha) * self.reputation + self.alpha * cooperated
        return C if self.reputation > self.threshold else D


# ---------------------------------------------------------------------------------------
# TODO(you): add your own original strategy here. Copy this template, uncomment it and
# fill it in:
#
# @register
# class MyStrategy(Strategy):
#     """My Strategy. Source: original.
#
#     Rule: <one line>.
#     Intuition: <why it should work, in game-theory terms>.
#     Predicted niche: <where in (epsilon, delta) it should do well, and why>.
#     """
#
#     code = "MINE"                        # short unique code used in configs
#
#     def __init__(self, my_param: float = 0.5):
#         super().__init__()
#         self.my_param = my_param
#
#     def reset(self, rng):                # called at the start of every match
#         super().reset(rng)               # keeps self.rng for random choices
#         # clear any memory here
#
#     def move(self, my_hist, opp_hist):   # actual moves so far; return 0 = C or 1 = D
#         return C
#
# Then:
#   1. write its prediction in notes/predictions.md (before running anything!),
#   2. add a test with an exactly known answer in tests/test_originals.py,
#   3. add "MINE" (or {code: MINE, my_param: 0.3}) to the pool in configs/e7_originals.yaml,
#   4. python run.py E7 && python analysis/make_figures.py
# ---------------------------------------------------------------------------------------
