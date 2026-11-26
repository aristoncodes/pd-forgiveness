"""Tournament tests: exact matrices without noise, reproducibility, CI sanity."""

import numpy as np
import pytest

from analysis.stats import bootstrap_ratio_ci, mean_ci
from pd.game import Payoffs
from pd.tournament import run_tournament

P = Payoffs()
POOL = ["ALLC", "ALLD", "TFT"]


@pytest.fixture(scope="module")
def res():
    return run_tournament(POOL, P, delta=0.95, epsilon=0.0, n_reps=30, seed=1)


def test_exact_payoff_matrix_without_noise(res):
    A = res.payoff_matrix
    n_rounds = res.lengths.sum()
    n_reps = len(res.lengths)
    assert A[0, 1] == 0 and A[1, 0] == 5  # ALLC vs ALLD
    assert A[0, 0] == A[2, 2] == A[0, 2] == A[2, 0] == 3  # cooperators together
    assert A[1, 1] == 1  # ALLD vs ALLD
    # TFT loses only round 1 against ALLD (S = 0), then gets P = 1 every round
    assert A[2, 1] == pytest.approx((n_rounds - n_reps) / n_rounds)
    assert A[1, 2] == pytest.approx((5 * n_reps + n_rounds - n_reps) / n_rounds)


def test_coop_matrix(res):
    C = res.coop_matrix
    assert np.all(C[0] == 1) and np.all(C[1] == 0)
    # TFT cooperates against ALLD only in round 1 of each match
    assert C[2, 1] == pytest.approx(len(res.lengths) / res.lengths.sum())


def test_ranking_table(res):
    rk = res.ranking()
    assert list(rk["rank"]) == [1, 2, 3]
    assert rk.iloc[-1]["strategy"] == "ALLC"
    assert (rk["ci_low"] <= rk["score"]).all() and (rk["score"] <= rk["ci_high"]).all()
    alld = rk[rk.strategy == "ALLD"].iloc[0]
    assert alld.head_to_head_wins == 2  # ALLD beats both others head-to-head


def test_same_seed_reproducible_and_pool_independent():
    a = run_tournament(POOL + ["JOSS"], P, 0.9, 0.05, n_reps=10, seed=3)
    b = run_tournament(POOL + ["JOSS"], P, 0.9, 0.05, n_reps=10, seed=3)
    assert np.array_equal(a.totals, b.totals)
    # games between the first three strategies don't change when a 5th one joins
    c = run_tournament(POOL + ["JOSS", "WSLS"], P, 0.9, 0.05, n_reps=10, seed=3)
    assert np.array_equal(a.totals[:, :4, :4], c.totals[:, :4, :4])


def test_common_random_numbers_share_lengths(res):
    m = res.matches()
    per_rep = m.groupby("rep")["n_rounds"].nunique()
    assert (per_rep == 1).all()


def test_mean_ci_and_bootstrap():
    x = np.random.default_rng(0).normal(3, 1, size=(1000, 2))
    _, lo, hi = mean_ci(x)
    assert np.all(lo < 3) and np.all(hi > 3) and np.all(hi - lo < 0.2)
    num = np.random.default_rng(1).normal(300, 10, size=50)
    lo, hi = bootstrap_ratio_ci(num, np.full(50, 100.0))
    assert lo < num.sum() / 5000 < hi
