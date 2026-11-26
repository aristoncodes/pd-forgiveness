"""Classic strategies from Axelrod's tournaments: ALLC, ALLD, RAND, TFT, GRIM."""

from __future__ import annotations

from .base import C, D, Strategy, register


@register
class AllC(Strategy):
    """Always Cooperate. Rule: play C every round.

    Unconditionally nice and forgiving, but never retaliates, so any defector exploits it.
    Source: standard benchmark (Axelrod 1984).
    """

    code = "ALLC"

    def move(self, my_hist, opp_hist):
        return C


@register
class AllD(Strategy):
    """Always Defect. Rule: play D every round.

    D is the dominant move in a single round, and ALLD is a Nash equilibrium of the
    repeated game at every delta (benchmark B3): against ALLD nothing does better than D.
    Source: standard benchmark (Axelrod 1984).
    """

    code = "ALLD"

    def move(self, my_hist, opp_hist):
        return D


@register
class Random(Strategy):
    """Random. Rule: play C with probability 0.5, independently every round.

    A "noise" baseline: neither nice nor retaliatory. Source: Axelrod (1980) tournament.
    """

    code = "RAND"

    def move(self, my_hist, opp_hist):
        return C if self.rng.random() < 0.5 else D


@register
class TitForTat(Strategy):
    """Tit-for-Tat. Rule: C in round 1, then copy the opponent's previous move.

    Axelrod's four virtues: nice (never defects first), retaliatory (punishes a D at once),
    forgiving (returns to C as soon as the opponent does), clear (easy to recognise).
    Winner of both Axelrod tournaments (Rapoport's entry). Weakness: under noise a single
    error starts an "echo" of alternating retaliation (benchmark B4).
    Source: Axelrod (1984).
    """

    code = "TFT"

    def move(self, my_hist, opp_hist):
        return opp_hist[-1] if opp_hist else C


@register
class Grim(Strategy):
    """Grim Trigger. Rule: C until the opponent defects once, then D forever.

    The harshest possible punishment, so it supports cooperation for the widest range of
    delta (benchmark B1: delta >= (T-R)/(T-P)). Never forgives, so under noise one error
    destroys cooperation for the rest of the match.
    Source: Friedman (1971); Axelrod (1984).
    """

    code = "GRIM"

    def reset(self, rng):
        super().reset(rng)
        self.triggered = False

    def move(self, my_hist, opp_hist):
        if opp_hist and opp_hist[-1] == D:
            self.triggered = True
        return D if self.triggered else C
