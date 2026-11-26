"""Engine and strategy tests with exactly known answers (PRD section 10)."""

import numpy as np
import pytest

from pd import theory
from pd.game import C, D, Payoffs, draw_length, play_match
from pd.strategies import Strategy, make

P = Payoffs()


def match(a, b, n=10, eps=0.0, seed=0, delta=0.99):
    s1 = make(a) if isinstance(a, str) else a
    s2 = make(b) if isinstance(b, str) else b
    return play_match(s1, s2, P, delta, eps, np.random.default_rng(seed), n_rounds=n)


class Scripted(Strategy):
    """Test helper: plays a fixed sequence of moves."""

    code = "SCRIPT"

    def __init__(self, moves):
        super().__init__()
        self.moves = moves

    def move(self, my_hist, opp_hist):
        return self.moves[len(my_hist)]


# ---------- payoffs ----------


def test_invalid_payoffs_rejected():
    with pytest.raises(ValueError):
        Payoffs(T=3, R=5, P=1, S=0)  # not T > R
    with pytest.raises(ValueError):
        Payoffs(T=7, R=3, P=1, S=0)  # 2R < T + S


# ---------- deterministic unit tests (fixed rounds, no noise) ----------


def test_allc_vs_alld():
    r = match("ALLC", "ALLD")
    assert r.score1 == 0 and r.score2 == 5


def test_tft_vs_alld():
    r = match("TFT", "ALLD")
    assert r.hist1 == [C] + [D] * 9
    assert r.score1 == pytest.approx(0.9) and r.score2 == pytest.approx(1.4)


@pytest.mark.parametrize("code", ["TFT", "GRIM", "WSLS", "TF2T", "GTFT", "CTFT"])
def test_nice_self_play_always_cooperates(code):
    r = match(code, code, n=50)
    assert set(r.hist1) == {C} and set(r.hist2) == {C}
    assert r.score1 == 3 and r.score2 == 3


def test_wsls_vs_alld_alternates():
    r = match("WSLS", "ALLD")
    assert r.hist1 == [C, D] * 5
    assert r.score2 == pytest.approx(theory.alld_vs_wsls(P)) == 3


def test_tf2t_forgives_one_d_punishes_two():
    r = match("TF2T", Scripted([C, D, C, D, D, C, C]), n=7)
    # reacts to the opponent's two previous moves: only after D, D (rounds 4-5) does it defect
    assert r.hist1 == [C, C, C, C, C, D, C]


def test_grim_never_forgives():
    r = match("GRIM", Scripted([C, D] + [C] * 8))
    assert r.hist1 == [C, C] + [D] * 8


def test_stft_vs_tft_alternates_forever():
    r = match("STFT", "TFT")
    assert r.hist1 == [D, C] * 5 and r.hist2 == [C, D] * 5


def test_gtft_zero_is_tft_and_one_is_allc():
    for opp in ["RAND", "JOSS", "ALLD"]:
        g0 = match(make("GTFT", g=0.0), opp, n=200, eps=0.05, seed=7)
        tft = match("TFT", opp, n=200, eps=0.05, seed=7)
        assert g0.hist1 == tft.hist1 and g0.hist2 == tft.hist2
        g1 = match(make("GTFT", g=1.0), opp, n=200, eps=0.05, seed=7)
        allc = match("ALLC", opp, n=200, eps=0.05, seed=7)
        assert g1.hist1 == allc.hist1 and g1.hist2 == allc.hist2


def test_ctft_accepts_one_punishment_after_own_mistake():
    s = make("CTFT")
    s.reset(np.random.default_rng(0))
    assert s.move([], []) == C
    # round 1: CTFT intended C but noise made it D; opponent cooperated
    assert s.move([D], [C]) == C  # normal TFT reply to the opponent's C
    # round 2: opponent punishes CTFT's accidental D
    assert s.move([D, C], [C, D]) == C  # contrite: does not retaliate
    # round 3: a genuine opponent D is punished again
    assert s.move([D, C, C], [C, D, D]) == D


def test_joss_defects_about_ten_percent_against_allc():
    r = match("JOSS", "ALLC", n=20000, seed=3)
    assert 1 - r.coop1 == pytest.approx(0.1, abs=0.01)


def test_registry_builds_parameterised_strategies():
    s = make("GTFT", g=0.2)
    assert s.g == 0.2 and s.name == "GTFT(0.20)"
    with pytest.raises(KeyError):
        make("NOPE")


# ---------- reproducibility ----------


def test_same_seed_same_histories_different_seed_different():
    a = match("RAND", "JOSS", n=100, eps=0.05, seed=1)
    b = match("RAND", "JOSS", n=100, eps=0.05, seed=1)
    c = match("RAND", "JOSS", n=100, eps=0.05, seed=2)
    assert a.hist1 == b.hist1 and a.hist2 == b.hist2
    assert a.hist1 != c.hist1


# ---------- statistical tests ----------


def test_noise_flip_rate():
    r = match("ALLC", "ALLC", n=500_000, eps=0.05, seed=11)  # 1,000,000 moves
    assert r.noise_events / 1_000_000 == pytest.approx(0.05, abs=0.001)
    # ALLC always intends C, so every D in the history is a flip
    assert (sum(r.hist1) + sum(r.hist2)) == r.noise_events


@pytest.mark.parametrize("delta", [0.9, 0.99])
def test_mean_game_length(delta):
    rng = np.random.default_rng(5)
    lengths = [draw_length(delta, rng) for _ in range(100_000)]
    expected = theory.expected_rounds(delta)
    assert abs(np.mean(lengths) - expected) / expected < 0.02
    assert min(lengths) >= 1


def test_tft_vs_tft_noise_tends_to_225():
    scores = [match("TFT", "TFT", n=2000, eps=0.05, seed=s).score1 for s in range(30)]
    assert np.mean(scores) == pytest.approx(theory.tft_noise_payoff(P), abs=0.05)


@pytest.mark.parametrize("code", ["WSLS", "CTFT"])
def test_error_correcting_strategies_stay_near_3(code):
    scores = [match(code, code, n=2000, eps=0.01, seed=s).score1 for s in range(30)]
    assert np.mean(scores) > 2.85


def test_play_match_draws_geometric_length_when_not_fixed():
    s1, s2 = make("TFT"), make("TFT")
    lengths = [
        play_match(s1, s2, P, 0.9, 0.0, np.random.default_rng(s)).n_rounds for s in range(3000)
    ]
    assert np.mean(lengths) == pytest.approx(10, rel=0.05)
