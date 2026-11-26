"""Replicator dynamics tests (PRD section 10, evolution tests)."""

import numpy as np
import pytest

from pd import theory
from pd.evolution import cooperation_rate, initial_shares, replicator
from pd.game import Payoffs
from pd.tournament import run_tournament

P = Payoffs()


def test_shares_sum_to_one_and_stay_non_negative():
    rng = np.random.default_rng(0)
    A = rng.uniform(0, 5, size=(8, 8))
    hist = replicator(A, rng.dirichlet(np.ones(8)), generations=500)
    assert np.allclose(hist.sum(axis=1), 1)
    assert (hist >= 0).all()


def test_alld_takes_over_allc():
    A = run_tournament(["ALLC", "ALLD"], P, 0.99, 0.0, n_reps=30, seed=1).payoff_matrix
    final = replicator(A, [0.5, 0.5], generations=1000)[-1]
    assert final[1] > 1 - 1e-6


def test_tft_and_allc_are_neutral_without_noise():
    A = run_tournament(["TFT", "ALLC"], P, 0.99, 0.0, n_reps=30, seed=1).payoff_matrix
    hist = replicator(A, [0.3, 0.7])
    assert np.allclose(hist, [0.3, 0.7])  # equal payoffs: nothing changes


def test_tft_invades_alld_only_above_critical_share():
    x_theory = theory.invasion_threshold(theory.tft_alld_matrix(0.99))
    assert x_theory == pytest.approx(0.01 / 1.97)  # about 0.5 % TFT needed
    A = run_tournament(["TFT", "ALLD"], P, 0.99, 0.0, n_reps=300, seed=2).payoff_matrix
    x_sim = theory.invasion_threshold(A)
    assert x_sim == pytest.approx(x_theory, rel=0.15)
    above = replicator(A, [2 * x_sim, 1 - 2 * x_sim], generations=5000)[-1]
    below = replicator(A, [x_sim / 2, 1 - x_sim / 2], generations=5000)[-1]
    assert above[0] > 0.99 and below[1] > 0.99


def test_initial_scenarios():
    codes = ["ALLC", "ALLD", "TFT", "WSLS"]
    assert np.allclose(initial_shares(codes, "uniform"), 0.25)
    assert np.allclose(initial_shares(codes, "many_defectors"), [1 / 6, 0.5, 1 / 6, 1 / 6])
    assert np.allclose(initial_shares(codes, "invasion"), [0, 0.95, 0.05, 0])
    assert np.allclose(initial_shares(codes, "wsls_resident"), [0, 0.01, 0, 0.99])


@pytest.mark.parametrize("T, alld_wins", [(5.0, True), (4.5, False)])
def test_b6_alld_invades_wsls_only_when_t_plus_p_over_2_reaches_r(T, alld_wins):
    A = run_tournament(["WSLS", "ALLD"], Payoffs(T=T), 0.99, 0.0, n_reps=50, seed=4)
    final = replicator(A.payoff_matrix, [0.99, 0.01], generations=5000)[-1]
    assert (final[1] > 0.5) == alld_wins


def test_cooperation_rate():
    C = np.array([[1.0, 1.0], [0.0, 0.0]])  # ALLC always C, ALLD never
    assert cooperation_rate(np.array([0.25, 0.75]), C) == pytest.approx(0.25)
