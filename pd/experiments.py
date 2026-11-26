"""Experiments E1-E7 and robustness checks R1-R2.

Each public function `eN(cfg, out)` takes a config dict and an output folder, runs the
simulation and saves raw results as CSV (+ Markdown summaries). No plotting here: figures
are drawn by analysis/make_figures.py from the saved files.

Sweeps run their tournaments in parallel across CPU cores with joblib. Every point of a
sweep uses the same base seed, so the game lengths are identical across points (common
random numbers across the sweep as well as within a tournament).
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from joblib import Parallel, delayed

from analysis.stats import mean_ci

from . import theory
from .evolution import EXTINCT, cooperation_rate, initial_shares, replicator
from .game import Payoffs, play_match
from .strategies import make
from .tournament import TournamentResult, build, run_tournament

# ---------------------------------------------------------------- helpers


def to_markdown(df: pd.DataFrame, floatfmt: str = ".3f") -> str:
    """Render a DataFrame as a GitHub Markdown table (no extra dependency)."""

    def fmt(v):
        return format(v, floatfmt) if isinstance(v, float) else str(v)

    lines = ["| " + " | ".join(map(str, df.columns)) + " |", "|" + "---|" * len(df.columns)]
    lines += ["| " + " | ".join(fmt(v) for v in row) + " |" for row in df.itertuples(index=False)]
    return "\n".join(lines) + "\n"


def save_table(df: pd.DataFrame, path: Path) -> None:
    """Save a summary table as both CSV and Markdown (PRD FR6.4)."""
    df.to_csv(path.with_suffix(".csv"), index=False)
    path.with_suffix(".md").write_text(to_markdown(df))


def payoffs(cfg: dict, T: float | None = None) -> Payoffs:
    p = dict(cfg["payoffs"])
    if T is not None:
        p["T"] = T
    return Payoffs(**p)


def parallel_tournaments(jobs: list[dict]) -> list[TournamentResult]:
    """Run many tournaments (keyword-argument dicts for run_tournament) on all cores."""
    return Parallel(n_jobs=-1)(delayed(run_tournament)(**job) for job in jobs)


def matrices_long(res: TournamentResult, **keys) -> pd.DataFrame:
    """Payoff and cooperation matrices as a long table, tagged with sweep keys."""
    k = len(res.labels)
    df = pd.DataFrame(
        {
            "player": np.repeat(res.labels, k),
            "opponent": np.tile(res.labels, k),
            "payoff": res.payoff_matrix.ravel(),
            "cooperation": res.coop_matrix.ravel(),
        }
    )
    for name, value in reversed(keys.items()):
        df.insert(0, name, value)
    return df


def save_tournament(res: TournamentResult, out: Path) -> pd.DataFrame:
    """Save matrices, raw matches and ranking (CSV + Markdown). Returns the ranking."""
    pd.DataFrame(res.payoff_matrix, index=res.labels, columns=res.labels).to_csv(
        out / "payoff_matrix.csv"
    )
    pd.DataFrame(res.coop_matrix, index=res.labels, columns=res.labels).to_csv(
        out / "coop_matrix.csv"
    )
    res.matches().to_csv(out / "matches.csv", index=False)
    ranking = res.ranking()
    save_table(ranking, out / "ranking")
    return ranking


# ---------------------------------------------------------------- reusable experiment cores


def noise_sweep(pool, pay: Payoffs, delta, epsilons, n_reps, seed):
    """Tournament at every noise level. Returns (scores, matrices) long tables."""
    jobs = [
        dict(pool=pool, payoffs=pay, delta=delta, epsilon=e, n_reps=n_reps, seed=seed)
        for e in epsilons
    ]
    results = parallel_tournaments(jobs)
    scores = pd.concat(
        [r.ranking().assign(epsilon=e) for e, r in zip(epsilons, results)], ignore_index=True
    )
    mats = pd.concat([matrices_long(r, epsilon=e) for e, r in zip(epsilons, results)])
    return scores, mats


def rank_table(scores: pd.DataFrame, value: str = "rank") -> pd.DataFrame:
    """Strategies × epsilon table of rank (or score), ordered by the no-noise rank."""
    t = scores.pivot(index="strategy", columns="epsilon", values=value)
    t = t.loc[scores[scores.epsilon == scores.epsilon.min()].sort_values("rank").strategy]
    t.columns = [f"eps={c:g}" for c in t.columns]
    return t.reset_index()


def evolution_runs(pool, pay_by_T: dict, delta, epsilons, scenarios, n_reps, seed, gens):
    """Replicator dynamics on the tournament matrix for every (T, epsilon, scenario).

    Returns (shares, survivors, matrices): full share histories, final surviving shares,
    and the payoff matrices used.
    """
    keys = [(T, e) for T in pay_by_T for e in epsilons]
    jobs = [
        dict(pool=pool, payoffs=pay_by_T[T], delta=delta, epsilon=e, n_reps=n_reps, seed=seed)
        for T, e in keys
    ]
    shares, survivors, mats = [], [], []
    for (T, e), res in zip(keys, parallel_tournaments(jobs)):
        mats.append(matrices_long(res, T=T, epsilon=e))
        for sc in scenarios:
            hist = replicator(res.payoff_matrix, initial_shares(res.codes, sc), gens)
            hist = np.vstack([hist, np.repeat(hist[-1:], gens + 1 - len(hist), axis=0)])
            g, s = np.meshgrid(np.arange(gens + 1), np.arange(len(res.labels)), indexing="ij")
            shares.append(
                pd.DataFrame(
                    {
                        "T": T,
                        "epsilon": e,
                        "scenario": sc,
                        "generation": g.ravel(),
                        "strategy": np.array(res.labels)[s.ravel()],
                        "share": hist.ravel(),
                    }
                )
            )
            final = hist[-1]
            coop = cooperation_rate(final, res.coop_matrix)
            for lab, x in sorted(zip(res.labels, final), key=lambda t: -t[1]):
                if x >= EXTINCT:
                    survivors.append(
                        dict(
                            T=T,
                            epsilon=e,
                            scenario=sc,
                            strategy=lab,
                            final_share=x,
                            population_cooperation=coop,
                        )
                    )
    return pd.concat(shares, ignore_index=True), pd.DataFrame(survivors), pd.concat(mats)


def _equilibrium(job: dict, gens: int) -> dict:
    """One tournament + replicator from a uniform start; summary of the end state."""
    res = run_tournament(**job)
    x = replicator(res.payoff_matrix, initial_shares(res.codes, "uniform"), gens)[-1]
    top = int(np.argmax(x))
    row = dict(
        epsilon=job["epsilon"],
        delta=job["delta"],
        seed=job["seed"],
        T=job["payoffs"].T,
        cooperation=cooperation_rate(x, res.coop_matrix),
        mean_payoff=float(x @ res.payoff_matrix @ x),
        dominant=res.labels[top],
        dominant_share=float(x[top]),
    )
    row.update({f"share_{lab}": float(v) for lab, v in zip(res.labels, x)})
    return row


def shadow_sweep(pool, pays, deltas, epsilons, n_seeds, n_reps, seed, gens) -> pd.DataFrame:
    """Evolutionary equilibrium for every (T, epsilon, delta, seed): one row each."""
    jobs = [
        dict(pool=pool, payoffs=p, delta=d, epsilon=e, n_reps=n_reps, seed=seed + s)
        for p in pays
        for e in epsilons
        for d in deltas
        for s in range(n_seeds)
    ]
    rows = Parallel(n_jobs=-1, batch_size=4)(delayed(_equilibrium)(j, gens) for j in jobs)
    return pd.DataFrame(rows)


def summarise_seeds(eq: pd.DataFrame) -> pd.DataFrame:
    """Mean and 95 % CI of equilibrium cooperation over seeds, per (T, epsilon, delta)."""
    rows = []
    for (T, e, d), g in eq.groupby(["T", "epsilon", "delta"]):
        m, lo, hi = mean_ci(g["cooperation"].to_numpy())
        rows.append(
            dict(
                T=T,
                epsilon=e,
                delta=d,
                cooperation=m,
                ci_low=lo,
                ci_high=hi,
                n_seeds=len(g),
                dominant=g["dominant"].mode().iloc[0],
            )
        )
    return pd.DataFrame(rows)


# ---------------------------------------------------------------- experiments


def e1(cfg: dict, out: Path) -> None:
    """E1 baseline tournament, no noise: ranking, payoff matrix, cooperation matrix."""
    res = run_tournament(
        cfg["pool"], payoffs(cfg), cfg["delta"], cfg["epsilon"], cfg["n_reps"], cfg["seed"]
    )
    print(save_tournament(res, out).to_string(index=False))


def e2(cfg: dict, out: Path) -> None:
    """E2 noise sweep: every strategy's tournament score at each epsilon."""
    scores, mats = noise_sweep(
        cfg["pool"], payoffs(cfg), cfg["delta"], cfg["epsilons"], cfg["n_reps"], cfg["seed"]
    )
    scores.to_csv(out / "scores.csv", index=False)
    mats.to_csv(out / "matrices.csv", index=False)
    save_table(rank_table(scores), out / "rank_by_epsilon")
    save_table(rank_table(scores, "score"), out / "score_by_epsilon")
    print(rank_table(scores).to_string(index=False))


def _intended_moves(code: str, h_me: list[int], h_opp: list[int]) -> list[int]:
    """Replay a deterministic strategy to recover the moves it intended each round."""
    s = make(code)
    s.reset(np.random.default_rng(0))
    return [s.move(h_me[:t], h_opp[:t]) for t in range(len(h_me))]


def one_error_trace(code: str, n: int, eps: float, window: tuple[int, int]) -> pd.DataFrame:
    """Find the first seed whose self-play match has exactly one noise error, inside
    `window` of rounds, and return its move trace (round, player, move, error)."""
    for seed in range(100_000):
        m = play_match(
            make(code), make(code), Payoffs(), 0.99, eps, np.random.default_rng(seed), n_rounds=n
        )
        err1 = [a != b for a, b in zip(m.hist1, _intended_moves(code, m.hist1, m.hist2))]
        err2 = [a != b for a, b in zip(m.hist2, _intended_moves(code, m.hist2, m.hist1))]
        rounds = [t for t in range(n) if err1[t] or err2[t]]
        if len(rounds) == 1 and window[0] <= rounds[0] <= window[1]:
            rows = [
                dict(
                    pair=f"{code} vs {code}",
                    seed=seed,
                    round=t + 1,
                    player=p,
                    move="CD"[h[t]],
                    error=e[t],
                )
                for p, h, e in ((1, m.hist1, err1), (2, m.hist2, err2))
                for t in range(n)
            ]
            return pd.DataFrame(rows)
    raise RuntimeError("no single-error match found")


def e3(cfg: dict, out: Path) -> None:
    """E3 echo effect: self-play of TFT, WSLS (and GTFT, CTFT) in long matches across ε."""
    pay, rows = payoffs(cfg), []
    for a, code in enumerate(cfg["strategies"]):
        for b, eps in enumerate(cfg["epsilons"]):
            reps = np.random.SeedSequence(cfg["seed"], spawn_key=(a, b)).spawn(cfg["n_reps"])
            for r, ss in enumerate(reps):
                m = play_match(
                    make(code),
                    make(code),
                    pay,
                    0.99,
                    eps,
                    np.random.default_rng(ss),
                    n_rounds=cfg["n_rounds"],
                )
                rows.append(
                    dict(
                        pair=f"{code} vs {code}",
                        epsilon=eps,
                        rep=r,
                        payoff=(m.score1 + m.score2) / 2,
                        cooperation=(m.coop1 + m.coop2) / 2,
                        noise_events=m.noise_events,
                    )
                )
    raw = pd.DataFrame(rows)
    raw.to_csv(out / "echo_raw.csv", index=False)
    summary = []
    for (pair, eps), g in raw.groupby(["pair", "epsilon"], sort=False):
        mean, lo, hi = mean_ci(g["payoff"].to_numpy())
        summary.append(
            dict(
                pair=pair,
                epsilon=eps,
                payoff=mean,
                ci_low=lo,
                ci_high=hi,
                cooperation=g["cooperation"].mean(),
            )
        )
    summary = pd.DataFrame(summary)
    save_table(summary, out / "echo_summary")
    traces = pd.concat(
        [
            one_error_trace(
                c, cfg["trace_rounds"], cfg["trace_epsilon"], tuple(cfg["trace_window"])
            )
            for c in cfg["trace_strategies"]
        ]
    )
    traces.to_csv(out / "traces.csv", index=False)
    print(summary.pivot(index="epsilon", columns="pair", values="payoff").round(3))


def e4(cfg: dict, out: Path) -> None:
    """E4 forgiveness dial: GTFT(g) takes the GTFT slot of the full pool, for every
    (delta, epsilon, g). Records GTFT(g)'s score and how ALLD fares against it."""
    pool, pay = cfg["pool"], payoffs(cfg)
    slot = next(i for i, s in enumerate(pool) if isinstance(s, dict) and s["code"] == "GTFT")
    alld = pool.index("ALLD")
    keys = [(d, e, g) for d in cfg["deltas"] for e in cfg["epsilons"] for g in cfg["gs"]]
    jobs = []
    for d, e, g in keys:
        p = list(pool)
        p[slot] = {"code": "GTFT", "g": g}
        jobs.append(
            dict(pool=p, payoffs=pay, delta=d, epsilon=e, n_reps=cfg["n_reps"], seed=cfg["seed"])
        )
    rows = []
    for (d, e, g), res in zip(keys, parallel_tournaments(jobs)):
        rk = res.ranking().set_index("code").loc["GTFT"]
        A = res.payoff_matrix
        rows.append(
            dict(
                delta=d,
                epsilon=e,
                g=g,
                score=rk.score,
                ci_low=rk.ci_low,
                ci_high=rk.ci_high,
                rank=int(rk["rank"]),
                gtft_self=A[slot, slot],
                gtft_vs_alld=A[slot, alld],
                alld_vs_gtft=A[alld, slot],
            )
        )
    df = pd.DataFrame(rows)
    df.to_csv(out / "gtft_scores.csv", index=False)
    best = df.loc[
        df.groupby(["delta", "epsilon"])["score"].idxmax(),
        ["delta", "epsilon", "g", "score", "ci_low", "ci_high", "rank"],
    ]
    best = best.rename(columns={"g": "best_g"})
    save_table(best, out / "best_g")
    print(best.to_string(index=False))


def e5(cfg: dict, out: Path) -> None:
    """E5 evolution: replicator dynamics for each (T, epsilon, initial condition)."""
    pays = {T: payoffs(cfg, T) for T in cfg["T_values"]}
    shares, surv, mats = evolution_runs(
        cfg["pool"],
        pays,
        cfg["delta"],
        cfg["epsilons"],
        cfg["scenarios"],
        cfg["n_reps"],
        cfg["seed"],
        cfg["generations"],
    )
    shares.to_csv(out / "shares.csv", index=False)
    mats.to_csv(out / "matrices.csv", index=False)
    save_table(surv, out / "survivors")
    save_table(invasion_table(mats, cfg["delta"]), out / "invasion_thresholds")
    print(surv.to_string(index=False))


def invasion_table(mats: pd.DataFrame, delta: float) -> pd.DataFrame:
    """Two-strategy invasion thresholds read off the simulated matrices (B3, B6):
    the share of TFT (resp. WSLS) needed to beat ALLD, next to the noise-free theory."""
    rows = []
    for (T, e), m in mats.groupby(["T", "epsilon"]):
        A = m.pivot(index="player", columns="opponent", values="payoff")
        row = dict(T=T, epsilon=e)
        for s in ("TFT", "WSLS"):
            M = A.loc[[s, "ALLD"], [s, "ALLD"]].to_numpy()
            row[f"{s}_self"], row[f"ALLD_vs_{s}"] = M[0, 0], M[1, 0]
            row[f"{s}_share_needed"] = theory.invasion_threshold(M)
        row["TFT_share_needed_theory_eps0"] = theory.invasion_threshold(
            theory.tft_alld_matrix(delta, Payoffs(T=T))
        )
        rows.append(row)
    return pd.DataFrame(rows)


def e6(cfg: dict, out: Path) -> None:
    """E6 shadow of the future: equilibrium cooperation vs delta, per epsilon."""
    eq = shadow_sweep(
        cfg["pool"],
        [payoffs(cfg)],
        cfg["deltas"],
        cfg["epsilons"],
        cfg["n_seeds"],
        cfg["n_reps"],
        cfg["seed"],
        cfg["generations"],
    )
    eq.to_csv(out / "equilibria.csv", index=False)
    summary = summarise_seeds(eq)
    save_table(summary, out / "cooperation_vs_delta")
    print(summary.pivot(index="delta", columns="epsilon", values="cooperation").round(3))


def e7(cfg: dict, out: Path) -> None:
    """E7 original strategies: rerun E2 (noise), E5 (evolution) and E6 (shadow of the
    future, on a finer epsilon grid for the niche map F9) with the originals added."""
    pool, pay = cfg["pool"], payoffs(cfg)
    scores, _ = noise_sweep(pool, pay, cfg["delta"], cfg["epsilons"], cfg["n_reps"], cfg["seed"])
    scores.to_csv(out / "noise_scores.csv", index=False)
    save_table(rank_table(scores), out / "noise_rank_by_epsilon")
    print(rank_table(scores).to_string(index=False))

    shares, surv, _ = evolution_runs(
        pool,
        {pay.T: pay},
        cfg["delta"],
        cfg["evo_epsilons"],
        cfg["scenarios"],
        cfg["n_reps"],
        cfg["seed"],
        cfg["generations"],
    )
    shares.to_csv(out / "evolution_shares.csv", index=False)
    save_table(surv, out / "evolution_survivors")
    print(surv.to_string(index=False))

    eq = shadow_sweep(
        pool,
        [pay],
        cfg["deltas"],
        cfg["niche_epsilons"],
        cfg["n_seeds"],
        cfg["n_reps"],
        cfg["seed"],
        cfg["generations"],
    )
    eq.to_csv(out / "niche_equilibria.csv", index=False)
    save_table(summarise_seeds(eq), out / "niche_summary")


def _pool_variants(cfg: dict) -> dict[str, list]:
    """Named pools for R1; the random subset is drawn reproducibly from the base pool."""
    pools = dict(cfg["pools"])
    spec = cfg["random_subset"]
    idx = np.sort(
        np.random.default_rng(spec["seed"]).choice(
            len(cfg["base_pool"]), spec["size"], replace=False
        )
    )
    pools[f"random{spec['size']}"] = [cfg["base_pool"][i] for i in idx]
    return pools


def r1(cfg: dict, out: Path) -> None:
    """R1 robustness to the pool: rerun E1/E2 (noise sweep) and E5 (evolution) with
    (a) only nice strategies, (b) many exploiters, (c) a random 8-strategy subset."""
    pay, scores, survs = payoffs(cfg), [], []
    for name, pool in _pool_variants(cfg).items():
        sc, _ = noise_sweep(pool, pay, cfg["delta"], cfg["epsilons"], cfg["n_reps"], cfg["seed"])
        scores.append(sc.assign(pool=name))
        scen = (
            ["uniform"]
            if "ALLD" not in [s if isinstance(s, str) else s["code"] for s in pool]
            else cfg["scenarios"]
        )
        _, surv, _ = evolution_runs(
            pool,
            {pay.T: pay},
            cfg["delta"],
            cfg["evo_epsilons"],
            scen,
            cfg["n_reps"],
            cfg["seed"],
            cfg["generations"],
        )
        survs.append(surv.assign(pool=name))
        print(f"-- pool {name}: {[build(s).name for s in pool]}")
        print(rank_table(sc).to_string(index=False))
    pd.concat(scores).to_csv(out / "pool_scores.csv", index=False)
    save_table(pd.concat(survs), out / "pool_survivors")


def r2(cfg: dict, out: Path) -> None:
    """R2 robustness to payoffs: T = 4.5 and T = 5.9. Noise sweep, evolution, and the
    delta sweep (do the cooperation thresholds move as B1/B2 predict?)."""
    pays = {T: payoffs(cfg, T) for T in cfg["T_values"]}
    scores = pd.concat(
        [
            noise_sweep(cfg["pool"], p, cfg["delta"], cfg["epsilons"], cfg["n_reps"], cfg["seed"])[
                0
            ].assign(T=T)
            for T, p in pays.items()
        ]
    )
    scores.to_csv(out / "payoff_scores.csv", index=False)
    _, surv, _ = evolution_runs(
        cfg["pool"],
        pays,
        cfg["delta"],
        cfg["evo_epsilons"],
        cfg["scenarios"],
        cfg["n_reps"],
        cfg["seed"],
        cfg["generations"],
    )
    save_table(surv, out / "payoff_survivors")
    print(surv.to_string(index=False))
    eq = shadow_sweep(
        cfg["pool"],
        list(pays.values()),
        cfg["deltas"],
        cfg["shadow_epsilons"],
        cfg["n_seeds"],
        cfg["n_reps"],
        cfg["seed"],
        cfg["generations"],
    )
    eq.to_csv(out / "payoff_equilibria.csv", index=False)
    save_table(summarise_seeds(eq), out / "payoff_cooperation_vs_delta")
