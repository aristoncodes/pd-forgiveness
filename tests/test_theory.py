"""Benchmark formulas give the values quoted in the PRD for default payoffs."""

import pytest

from pd import theory
from pd.game import Payoffs


def test_default_benchmarks():
    p = Payoffs()
    assert theory.grim_threshold(p) == 0.5  # B1
    assert theory.tft_threshold(p) == pytest.approx(2 / 3)  # B2
    assert theory.tft_noise_payoff(p) == 2.25  # B4
    assert theory.optimal_generosity(p) == pytest.approx(1 / 3)  # B5
    assert theory.alld_vs_wsls(p) == 3  # B6
    assert not theory.wsls_strictly_stable(p)  # B6: exactly neutral at T = 5


def test_wsls_strictly_stable_with_lower_temptation():
    assert theory.wsls_strictly_stable(Payoffs(T=4.5))  # (4.5 + 1) / 2 = 2.75 < 3


def test_expected_rounds():
    assert theory.expected_rounds(0.9) == pytest.approx(10)
    assert theory.expected_rounds(0.99) == pytest.approx(100)
