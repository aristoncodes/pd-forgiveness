"""Game engine: the stage game, random game length and implementation noise.

Moves are integers: 0 = C (cooperate), 1 = D (defect).

Game theory recap
-----------------
* Stage game: each round both players pick C or D at the same time. Payoffs follow the
  Prisoner's Dilemma ordering T > R > P > S (Temptation > Reward > Punishment > Sucker).
  Defecting is the best reply to anything in a *single* round, yet mutual defection (P, P)
  is worse for both than mutual cooperation (R, R). That is the dilemma.
* Shadow of the future: after every round the game continues with probability delta.
  The number of rounds L is Geometric(1 - delta), mean 1 / (1 - delta). Because nobody
  knows which round is the last, backward induction cannot unravel cooperation.
* Implementation noise: with probability epsilon a player's intended move is flipped
  ("trembling hand"). Both players see the move that was actually played.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

C, D = 0, 1


@dataclass(frozen=True)
class Payoffs:
    """Prisoner's Dilemma payoffs. Defaults are Axelrod's (T, R, P, S) = (5, 3, 1, 0)."""

    T: float = 5.0
    R: float = 3.0
    P: float = 1.0
    S: float = 0.0

    def __post_init__(self) -> None:
        if not (self.T > self.R > self.P > self.S):
            raise ValueError("A Prisoner's Dilemma needs T > R > P > S")
        if not (2 * self.R > self.T + self.S):
            raise ValueError("Need 2R > T + S, so alternating exploitation is worse than R")

    def table(self) -> np.ndarray:
        """Row player's payoff, indexed as table[my_move, opp_move]."""
        return np.array([[self.R, self.S], [self.T, self.P]], dtype=float)


@dataclass
class MatchResult:
    """Everything recorded about one match."""

    hist1: list[int]  # actual moves of player 1
    hist2: list[int]  # actual moves of player 2
    total1: float  # total payoff of player 1 over the match
    total2: float
    n_rounds: int
    noise_events: int  # how many moves were flipped by noise

    @property
    def score1(self) -> float:
        """Average payoff per round of player 1."""
        return self.total1 / self.n_rounds

    @property
    def score2(self) -> float:
        return self.total2 / self.n_rounds

    @property
    def coop1(self) -> float:
        """Fraction of rounds in which player 1 actually cooperated."""
        return 1 - sum(self.hist1) / self.n_rounds

    @property
    def coop2(self) -> float:
        return 1 - sum(self.hist2) / self.n_rounds


def draw_length(delta: float, rng: np.random.Generator) -> int:
    """Number of rounds when the game continues with probability delta after each round.

    P(L = k) = delta^(k-1) (1 - delta), so L >= 1 and E[L] = 1 / (1 - delta).
    """
    return int(rng.geometric(1 - delta))


def play_match(
    s1,
    s2,
    payoffs: Payoffs,
    delta: float,
    epsilon: float,
    rng: np.random.Generator,
    n_rounds: int | None = None,
) -> MatchResult:
    """Play one match between two strategy objects and return both histories and payoffs.

    The rng is split into three independent child streams (noise, strategy 1, strategy 2),
    so a strategy that uses random numbers never changes the noise the other one sees.
    The match is fully determined by the rng's seed.

    n_rounds fixes the length; when None it is drawn from Geometric(1 - delta).
    The tournament passes n_rounds so all pairings in one repetition share the same
    length (common random numbers).
    """
    noise_rng, rng1, rng2 = rng.spawn(3)
    n = draw_length(delta, rng) if n_rounds is None else n_rounds
    s1.reset(rng1)
    s2.reset(rng2)

    if epsilon > 0:
        flips = (noise_rng.random((n, 2)) < epsilon).astype(int).tolist()
    else:
        flips = [[0, 0]] * n

    h1: list[int] = []
    h2: list[int] = []
    for f1, f2 in flips:
        a = s1.move(h1, h2)  # intended moves, chosen simultaneously
        b = s2.move(h2, h1)
        h1.append(a ^ f1)  # ^ flips the move when noise hits
        h2.append(b ^ f2)

    table = payoffs.table()
    m1, m2 = np.array(h1), np.array(h2)
    return MatchResult(
        hist1=h1,
        hist2=h2,
        total1=float(table[m1, m2].sum()),
        total2=float(table[m2, m1].sum()),
        n_rounds=n,
        noise_events=int(np.sum(flips)) if epsilon > 0 else 0,
    )
