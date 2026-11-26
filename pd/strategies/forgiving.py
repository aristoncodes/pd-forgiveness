"""Known forgiving and adaptive strategies: GTFT, TF2T, WSLS, STFT, CTFT, JOSS."""

from __future__ import annotations

from .base import C, D, Strategy, register


@register
class GenerousTFT(Strategy):
    """Generous Tit-for-Tat GTFT(g). Rule: C in round 1; after an opponent C play C;
    after an opponent D cooperate anyway with probability g, else D.

    g is the forgiveness "dial": g = 0 is TFT, g = 1 is ALLC. Random forgiveness breaks
    TFT's echo of retaliation after a noise error, while g < 1 still punishes defectors on
    average. Nowak & Sigmund (1992) find the best generosity
    g* = min(1 - (T-R)/(R-S), (R-P)/(T-P)) = 1/3 for default payoffs (benchmark B5).
    Source: Nowak & Sigmund (1992); Molander (1985).
    """

    code = "GTFT"

    def __init__(self, g: float = 1 / 3):
        super().__init__()
        self.g = g
        self.name = f"GTFT({g:.2f})"

    def move(self, my_hist, opp_hist):
        if not opp_hist or opp_hist[-1] == C:
            return C
        return C if self.rng.random() < self.g else D


@register
class TitForTwoTats(Strategy):
    """Tit-for-Two-Tats. Rule: defect only if the opponent defected in both of the last
    two rounds; otherwise cooperate.

    Deterministic forgiveness: a single (possibly accidental) D is ignored. The cost is
    that an opponent who defects every other round exploits it for free.
    Source: Axelrod (1984), sample strategy in the first tournament.
    """

    code = "TF2T"

    def move(self, my_hist, opp_hist):
        return D if opp_hist[-2:] == [D, D] else C


@register
class WinStayLoseShift(Strategy):
    """Win-Stay Lose-Shift (Pavlov). Rule: C in round 1; if last round's payoff was R or T
    ("win") repeat the last move, if it was P or S ("lose") switch.

    A win happens exactly when the opponent cooperated, so next = my_last XOR opp_last.
    After a single error between two WSLS players: (C,D) -> (D,D) -> (C,C), back to
    cooperation in two rounds. It also exploits unconditional cooperators (after an error
    against ALLC it keeps defecting, because T is a win).
    Weakness (benchmark B6): against ALLD it alternates C, D, so ALLD earns (T+P)/2.
    Source: Nowak & Sigmund (1993); Kraines & Kraines (1989).
    """

    code = "WSLS"

    def move(self, my_hist, opp_hist):
        if not my_hist:
            return C
        return my_hist[-1] ^ opp_hist[-1]


@register
class SuspiciousTFT(Strategy):
    """Suspicious Tit-for-Tat. Rule: D in round 1, then copy the opponent's previous move.

    Not nice: its opening D locks it into alternating D/C with TFT forever, showing the cost
    of a nasty opening. Source: Axelrod (1984); Boyd & Lorberbaum (1987).
    """

    code = "STFT"

    def move(self, my_hist, opp_hist):
        return opp_hist[-1] if opp_hist else D


@register
class ContriteTFT(Strategy):
    """Contrite Tit-for-Tat. Rule: play TFT, but if my own last D was a mistake (I intended
    C and noise flipped it), accept the opponent's next retaliation without retaliating.

    Unlike TFT, a contrite player knows its own intentions. After its own error it plays C
    for two rounds (the normal TFT reply, then one "apology" C in place of retaliating to
    the punishment it provoked), which stops the echo. Against TFT or another CTFT,
    cooperation is restored right away after a CTFT error.
    Implementation note: this is the operational "accept one punishment" rule from the PRD,
    a simplification of Boyd's (1989) "standing" formulation.
    Source: Wu & Axelrod (1995); Boyd (1989); Sugden (1986).
    """

    code = "CTFT"

    def reset(self, rng):
        super().reset(rng)
        self.last_intended = C
        self.absorb = False  # True = ignore the opponent's next move (accept punishment)

    def move(self, my_hist, opp_hist):
        if not my_hist:
            intended = C
        else:
            my_mistake = my_hist[-1] == D and self.last_intended == C
            if self.absorb:
                intended = C
                self.absorb = False
            else:
                intended = opp_hist[-1]
            if my_mistake:
                self.absorb = True
        self.last_intended = intended
        return intended


@register
class Joss(Strategy):
    """Joss. Rule: play TFT, but when TFT says C, defect anyway with probability p (0.1).

    A "sneaky" exploiter: it tries to grab occasional T payoffs. Against TFT its sneaky
    defections start echoes, so it usually does worse than plain TFT.
    Source: Axelrod (1980), first tournament entry by Johann Joss.
    """

    code = "JOSS"

    def __init__(self, p: float = 0.1):
        super().__init__()
        self.p = p
        self.name = "JOSS" if p == 0.1 else f"JOSS({p:.2f})"

    def move(self, my_hist, opp_hist):
        if opp_hist and opp_hist[-1] == D:
            return D
        return D if self.rng.random() < self.p else C
