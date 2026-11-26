"""Original strategies tested on scripted opponents with exactly known answers."""

import numpy as np
import pytest

from pd.game import C, D, Payoffs, play_match
from pd.strategies import Strategy, make

P = Payoffs()


class Scripted(Strategy):
    code = "SCRIPT"

    def __init__(self, moves):
        super().__init__()
        self.moves = moves

    def move(self, my_hist, opp_hist):
        return self.moves[len(my_hist)]


def match(a, b, n=10, eps=0.0, seed=0):
    s1 = make(a) if isinstance(a, str) else a
    s2 = make(b) if isinstance(b, str) else b
    return play_match(s1, s2, P, 0.99, eps, np.random.default_rng(seed), n_rounds=n)


@pytest.mark.parametrize("code", ["AF", "GWA", "REP"])
def test_nice_originals_cooperate_with_themselves(code):
    r = match(code, code, n=50)
    assert set(r.hist1) == {C} and r.score1 == 3


def test_af_becomes_unforgiving_against_alld():
    r = match("AF", "ALLD", n=2000, seed=1)
    assert r.coop1 < 0.02  # g = 0.5·2/(d+2) → 0 as defections pile up


def test_af_forgives_noise_better_than_tft():
    af = np.mean([match("AF", "TFT", n=2000, eps=0.01, seed=s).score1 for s in range(20)])
    tft = np.mean([match("TFT", "TFT", n=2000, eps=0.01, seed=s).score1 for s in range(20)])
    assert af > tft + 0.2  # measured: 2.50 vs 2.24


def test_gwa_grants_amnesty_after_good_behaviour():
    r = match("GWA", Scripted([C, D, C, C, C, C, C, C, C]), n=9)
    # punishes rounds 3-7 for the D in round 2; opponent cooperated in all 5 → amnesty
    assert r.hist1 == [C, C, D, D, D, D, D, C, C]


def test_gwa_never_forgives_alld():
    r = match("GWA", "ALLD", n=30)
    assert r.hist1 == [C] + [D] * 29


def test_pf_exploits_allc():
    r = match("PF", "ALLC")
    assert r.hist1 == [C, D, C, C] + [D] * 6


def test_pf_makes_peace_with_tft():
    r = match("PF", "TFT")
    assert r.hist1 == [C, D, C, C] + [C] * 6
    assert r.hist2 == [C, C, D, C] + [C] * 6


def test_pf_switches_to_wsls_when_exploited_victim_fights_back():
    r = match("PF", "TF2T", n=8)
    # TF2T ignores the probe, PF exploits (rounds 5-7), TF2T answers PF's two Ds in round 7,
    # so PF turns WSLS and, after mutual D, cooperates in round 8
    assert r.hist1 == [C, D, C, C, D, D, D, C]
    assert r.hist2 == [C, C, C, C, C, C, D, D]


def test_rep_cuts_off_alld_after_four_rounds():
    r = match("REP", "ALLD")
    assert r.hist1 == [C, C, C, C] + [D] * 6


def test_rep_ignores_a_single_defection():
    r = match("REP", Scripted([C, D] + [C] * 8))
    assert r.hist1 == [C] * 10
