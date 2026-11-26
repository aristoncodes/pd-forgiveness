"""Analytic benchmarks B1-B6. Tests and plots both use these, so theory and simulation are
always compared on identical numbers. Derivations are in docs/theory_derivations.md.
"""

from __future__ import annotations

import numpy as np

from .game import Payoffs

DEFAULT = Payoffs()  # Axelrod payoffs (T, R, P, S) = (5, 3, 1, 0); frozen, safe to share


def expected_rounds(delta: float) -> float:
    """Mean game length when the game continues with probability delta: 1 / (1 - delta)."""
    return 1 / (1 - delta)


def grim_threshold(p: Payoffs = DEFAULT) -> float:
    """B1. Mutual GRIM is an equilibrium iff delta >= (T - R) / (T - P).

    Defecting once gains T - R today but costs R - P in every later round forever.
    """
    return (p.T - p.R) / (p.T - p.P)


def tft_threshold(p: Payoffs = DEFAULT) -> float:
    """B2. TFT is collectively stable iff delta >= max((T-R)/(T-P), (T-R)/(R-S)).

    The first term stops a permanent defector (ALLD); the second stops an alternator
    (D, C, D, C, ...) who exploits TFT's quick forgiveness.
    """
    return max((p.T - p.R) / (p.T - p.P), (p.T - p.R) / (p.R - p.S))


def tft_noise_payoff(p: Payoffs = DEFAULT) -> float:
    """B4. Long-run payoff per round of TFT vs TFT under small noise: (R + S + T + P) / 4.

    Each error shifts the pair between the states CC, CD/DC echo and DD; in the long run
    all four outcomes are equally likely.
    """
    return (p.R + p.S + p.T + p.P) / 4


def optimal_generosity(p: Payoffs = DEFAULT) -> float:
    """B5. Nowak & Sigmund (1992) optimal GTFT generosity:
    g* = min(1 - (T - R) / (R - S), (R - P) / (T - P)).
    """
    return min(1 - (p.T - p.R) / (p.R - p.S), (p.R - p.P) / (p.T - p.P))


def alld_vs_wsls(p: Payoffs = DEFAULT) -> float:
    """B6. ALLD's average payoff against WSLS, which alternates C, D: (T + P) / 2."""
    return (p.T + p.P) / 2


def wsls_strictly_stable(p: Payoffs = DEFAULT) -> bool:
    """B6. WSLS resists ALLD strictly only if R > (T + P) / 2."""
    return p.R > alld_vs_wsls(p)


def tft_alld_matrix(delta: float, p: Payoffs = DEFAULT) -> np.ndarray:
    """B3. Average per-round payoffs of TFT and ALLD against each other, rows/cols [TFT, ALLD].

    TFT vs ALLD: S in round 1, then P: (1 - delta) S + delta P per round.
    ALLD vs TFT: T in round 1, then P: (1 - delta) T + delta P per round.
    """
    return np.array(
        [[p.R, (1 - delta) * p.S + delta * p.P], [(1 - delta) * p.T + delta * p.P, p.P]]
    )


def invasion_threshold(M: np.ndarray) -> float:
    """Critical starting share of strategy 0 against strategy 1 in a 2-strategy population.

    With M = [[a, b], [c, d]], strategy 0 does better exactly when its share x satisfies
    x a + (1 - x) b > x c + (1 - x) d, i.e. x > (d - b) / ((a - c) + (d - b)).
    Below the threshold replicator dynamics goes to all-1, above it to all-0 (bistability).
    """
    (a, b), (c, d) = M
    return (d - b) / ((a - c) + (d - b))
