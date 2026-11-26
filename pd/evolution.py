"""Evolutionary dynamics on a tournament payoff matrix.

Replicator dynamics (discrete time): a strategy's share grows in proportion to how much
better than average it does against the current population.

    f_i  = sum_j A_ij x_j        fitness of i = expected payoff against a random opponent
    fbar = sum_i x_i f_i         average fitness
    x_i <- x_i * f_i / fbar      above-average strategies grow, below-average ones shrink

Shares stay non-negative and sum to 1 automatically. A strategy with share 0 can never
come back (replicator dynamics has no mutation), so initial conditions matter.
"""

from __future__ import annotations

import numpy as np

EXTINCT = 1e-6  # shares below this count as extinct (PRD FR4.2)


def replicator(
    A: np.ndarray, x0: np.ndarray, generations: int = 1000, tol: float = 1e-9
) -> np.ndarray:
    """Run replicator dynamics. Returns the history of shares, shape (T + 1, k).

    Stops early when no share changes by more than `tol` in a generation.
    """
    x = np.asarray(x0, dtype=float) / np.sum(x0)
    history = [x]
    for _ in range(generations):
        f = A @ x
        new = x * f / (x @ f)
        history.append(new)
        if np.max(np.abs(new - x)) < tol:
            break
        x = new
    return np.array(history)


def initial_shares(codes: list[str], scenario: str) -> np.ndarray:
    """Starting population: the three PRD scenarios plus a B6 test.

    uniform:        every strategy equally common.
    many_defectors: ALLD has 50 %, the rest share the other 50 % equally.
    invasion:       ALLD 95 %, TFT 5 %, everyone else absent (can TFT invade?).
    wsls_resident:  WSLS 99 %, ALLD 1 % (benchmark B6: can ALLD invade WSLS?).
    """
    k = len(codes)
    if scenario == "uniform":
        return np.full(k, 1 / k)
    alld = codes.index("ALLD")
    x = np.zeros(k)
    if scenario == "many_defectors":
        x[:] = 0.5 / (k - 1)
        x[alld] = 0.5
    elif scenario == "invasion":
        x[alld], x[codes.index("TFT")] = 0.95, 0.05
    elif scenario == "wsls_resident":
        x[alld], x[codes.index("WSLS")] = 0.01, 0.99
    else:
        raise ValueError(f"Unknown scenario {scenario!r}")
    return x


def cooperation_rate(x: np.ndarray, C: np.ndarray) -> float:
    """Fraction of moves that are C when individuals meet at random: x^T C x."""
    return float(x @ C @ x)
