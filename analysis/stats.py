"""Confidence intervals: normal approximation and bootstrap for ratio estimators."""

from __future__ import annotations

import numpy as np


def mean_ci(samples: np.ndarray, axis: int = 0, z: float = 1.96):
    """Mean and normal-approximation 95% CI (mean ± 1.96 · sd / √n) along `axis`."""
    samples = np.asarray(samples, dtype=float)
    n = samples.shape[axis]
    mean = samples.mean(axis=axis)
    half = z * samples.std(axis=axis, ddof=1) / np.sqrt(n)
    return mean, mean - half, mean + half


def bootstrap_ratio_ci(
    numer: np.ndarray, denom: np.ndarray, n_boot: int = 2000, level: float = 0.95, seed: int = 0
):
    """Percentile bootstrap CI for the ratio sum(numer) / sum(denom), resampling repetitions.

    numer has shape (n_reps, ...) and denom shape (n_reps,). We use this for "average payoff
    per round" = total payoff over all repetitions / total rounds over all repetitions, which
    is the quantity game theory predicts (see docs/decisions.md, D14).
    """
    numer = np.asarray(numer, dtype=float)
    denom = np.asarray(denom, dtype=float)
    n = len(denom)
    idx = np.random.default_rng(seed).integers(0, n, size=(n_boot, n))
    extra = (1,) * (numer.ndim - 1)
    ratios = numer[idx].sum(axis=1) / denom[idx].sum(axis=1).reshape(n_boot, *extra)
    alpha = (1 - level) / 2
    return np.quantile(ratios, alpha, axis=0), np.quantile(ratios, 1 - alpha, axis=0)
