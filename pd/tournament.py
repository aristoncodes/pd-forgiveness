"""Axelrod-style round-robin tournament: payoff matrix, cooperation matrix and ranking.

Every strategy plays every strategy, including a copy of itself (self-play is needed for
evolution: in a population, you often meet your own kind). Each pairing is repeated n_reps
times. In repetition r every pairing uses the same game length L_r (common random numbers),
so differences between strategies are not blurred by luck in game length.

Average payoff per round is computed as (total payoff over all repetitions) / (total rounds
over all repetitions). This equals the normalised expected discounted payoff that the theory
benchmarks use (see docs/decisions.md, D14).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from analysis.stats import bootstrap_ratio_ci

from .game import Payoffs, play_match
from .strategies import Strategy, make


def build(spec: str | dict) -> Strategy:
    """Turn a pool entry into a fresh strategy: "TFT" or {"code": "GTFT", "g": 0.2}."""
    return make(spec) if isinstance(spec, str) else make(**spec)


def draw_lengths(delta: float, n_reps: int, seed: int) -> np.ndarray:
    """One Geometric(1 - delta) game length per repetition, shared by all pairings."""
    rng = np.random.default_rng(np.random.SeedSequence(seed, spawn_key=(0,)))
    return rng.geometric(1 - delta, size=n_reps)


def play_pairing(
    spec_i, spec_j, payoffs: Payoffs, epsilon: float, lengths: np.ndarray, seed: int, key: tuple
) -> np.ndarray:
    """Play one pairing for every repetition.

    Returns an array of shape (n_reps, 4): total_i, total_j, coops_i, coops_j, where coops
    count the rounds in which each player actually cooperated. Each repetition gets its own
    child seed, spawned from (seed, key), so a pairing's games do not depend on which other
    pairings were played.
    """
    reps = np.random.SeedSequence(seed, spawn_key=(1, *key)).spawn(len(lengths))
    s_i, s_j = build(spec_i), build(spec_j)  # fresh objects: self-play needs two copies
    out = np.empty((len(lengths), 4))
    for r, (ss, n) in enumerate(zip(reps, lengths)):
        m = play_match(s_i, s_j, payoffs, 0.0, epsilon, np.random.default_rng(ss), int(n))
        out[r] = (m.total1, m.total2, n - sum(m.hist1), n - sum(m.hist2))
    return out


@dataclass
class TournamentResult:
    """Raw per-repetition totals; matrices and rankings are computed from them."""

    labels: list[str]
    codes: list[str]
    totals: np.ndarray  # (n_reps, k, k): total payoff of i against j in repetition r
    coops: np.ndarray  # (n_reps, k, k): rounds in which i cooperated against j
    lengths: np.ndarray  # (n_reps,): game length of repetition r

    @property
    def payoff_matrix(self) -> np.ndarray:
        """A[i, j] = average per-round payoff of strategy i against strategy j."""
        return self.totals.sum(0) / self.lengths.sum()

    @property
    def coop_matrix(self) -> np.ndarray:
        """C[i, j] = fraction of rounds in which strategy i cooperated against j."""
        return self.coops.sum(0) / self.lengths.sum()

    def ranking(self) -> pd.DataFrame:
        """Mean score against the whole pool (uniform over opponents, self included), 95%
        bootstrap CI over repetitions, and number of head-to-head wins."""
        A = self.payoff_matrix
        lo, hi = bootstrap_ratio_ci(self.totals.mean(axis=2), self.lengths)
        wins = (A > A.T + 1e-12).sum(axis=1)
        df = pd.DataFrame(
            {
                "strategy": self.labels,
                "code": self.codes,
                "score": A.mean(axis=1),
                "ci_low": lo,
                "ci_high": hi,
                "head_to_head_wins": wins,
                "cooperation": self.coop_matrix.mean(axis=1),
            }
        )
        df = df.sort_values("score", ascending=False).reset_index(drop=True)
        df.insert(0, "rank", np.arange(1, len(df) + 1))
        return df

    def matches(self) -> pd.DataFrame:
        """Long table of raw results: one row per (repetition, i, j)."""
        n_reps, k, _ = self.totals.shape
        r, i, j = np.meshgrid(np.arange(n_reps), np.arange(k), np.arange(k), indexing="ij")
        return pd.DataFrame(
            {
                "rep": r.ravel(),
                "player": np.array(self.labels)[i.ravel()],
                "opponent": np.array(self.labels)[j.ravel()],
                "total_payoff": self.totals.ravel(),
                "cooperations": self.coops.ravel(),
                "n_rounds": self.lengths[r.ravel()],
            }
        )


def run_tournament(
    pool: list,
    payoffs: Payoffs,
    delta: float,
    epsilon: float,
    n_reps: int = 50,
    seed: int = 42,
) -> TournamentResult:
    """Round-robin of every pool entry against every entry, itself included."""
    k = len(pool)
    lengths = draw_lengths(delta, n_reps, seed)
    totals = np.zeros((n_reps, k, k))
    coops = np.zeros((n_reps, k, k))
    for i in range(k):
        for j in range(i, k):
            out = play_pairing(pool[i], pool[j], payoffs, epsilon, lengths, seed, (i, j))
            if i == j:  # self-play: both copies are the same strategy, so average them
                totals[:, i, i] = (out[:, 0] + out[:, 1]) / 2
                coops[:, i, i] = (out[:, 2] + out[:, 3]) / 2
            else:
                totals[:, i, j], totals[:, j, i] = out[:, 0], out[:, 1]
                coops[:, i, j], coops[:, j, i] = out[:, 2], out[:, 3]
    strategies = [build(s) for s in pool]
    return TournamentResult(
        labels=[s.name for s in strategies],
        codes=[s.code for s in strategies],
        totals=totals,
        coops=coops,
        lengths=lengths,
    )
