"""Make every figure from saved results (never re-runs simulations).

    python analysis/make_figures.py

Figures whose experiment has not been run yet are skipped. Output: figures/F*.png and .pdf.
Colours: a colour-blind-safe categorical palette (validated, fixed slot order) and a
single-hue blue ramp for heatmaps.
"""

from __future__ import annotations

import textwrap
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml
from matplotlib.colors import LinearSegmentedColormap

ROOT = Path(__file__).resolve().parent.parent
RESULTS, FIGURES = ROOT / "results", ROOT / "figures"

# Categorical slots, always used in this order (blue, orange, aqua, yellow, ...).
PALETTE = ["#257de0", "#f47230", "#00b894", "#f2a600", "#ee7fac", "#008a17", "#6a4ce2"]
BLUES = LinearSegmentedColormap.from_list(
    "blues", ["#cce3fd", "#84b9f3", "#338ced", "#2370cd", "#1757ac", "#0e3d7e"]
)
TEXT, MUTED, GRID = "#191919", "#666666", "#e6e6e6"
NICE = {"ALLC", "TFT", "GRIM", "GTFT", "TF2T", "WSLS", "CTFT"}  # never defect first

# One fixed colour per strategy in every figure (colour follows the entity, never its rank).
# The eight categorical slots go to the strategies the story is about; the rest are greys
# and always carry a direct label or legend entry, so colour is never the only cue.
COLOR = {
    "TFT": "#257de0",
    "GTFT(0.33)": "#f47230",
    "CTFT": "#00b894",
    "WSLS": "#f2a600",
    "TF2T": "#ee7fac",
    "GRIM": "#008a17",
    "REP": "#6a4ce2",
    "ALLD": "#ec4647",
}
GREYS = {
    "AF": "#4d4d4d",
    "GWA": "#8c8c8c",
    "PF": "#b3b3b3",
    "ALLC": "#999999",
    "RAND": "#bfbfbf",
    "STFT": "#7a7a7a",
    "JOSS": "#a6a6a6",
}
EPS_TICKS = [0, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2]


def color(label: str) -> str:
    return COLOR.get(label, GREYS.get(label, "#999999"))


def eps_axis(ax) -> None:
    """Log-like noise axis that still shows epsilon = 0 (symlog, linear below 0.005)."""
    ax.set_xscale("symlog", linthresh=0.005, linscale=0.4)
    ax.set_xticks(EPS_TICKS, [f"{e:g}" for e in EPS_TICKS])
    ax.set_xlim(-0.0005, 0.22)
    ax.set_xlabel("Noise ε (probability each move is flipped; log scale above 0.005)")


def title(ax, text: str) -> None:
    ax.set_title(text, loc="left", color=TEXT, fontsize=12)


plt.rcParams.update(
    {
        "font.size": 10,
        "axes.edgecolor": MUTED,
        "axes.labelcolor": TEXT,
        "xtick.color": MUTED,
        "ytick.color": MUTED,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": False,
        "grid.color": GRID,
        "figure.dpi": 150,
    }
)


def load_config(exp: str) -> dict:
    return yaml.safe_load((RESULTS / exp / "config.yaml").read_text())


def params_caption(cfg: dict) -> str:
    p = cfg["payoffs"]
    eps = cfg.get("epsilon", cfg.get("epsilons"))
    return (
        f"Payoffs T={p['T']}, R={p['R']}, P={p['P']}, S={p['S']}; δ={cfg['delta']} "
        f"(mean {1 / (1 - cfg['delta']):.0f} rounds); ε={eps}; "
        f"{cfg['n_reps']} repetitions per pairing; seed {cfg['seed']}."
    )


def save(fig, name: str, caption: str) -> None:
    # placed below the axes (negative y); bbox_inches="tight" grows the canvas to include it
    fig.text(0.01, -0.01, textwrap.fill(caption, 125), fontsize=8, color=MUTED, va="top")
    FIGURES.mkdir(exist_ok=True)
    fig.savefig(FIGURES / f"{name}.png", bbox_inches="tight")
    # no creation timestamp, so re-running produces byte-identical PDFs
    fig.savefig(FIGURES / f"{name}.pdf", bbox_inches="tight", metadata={"CreationDate": None})
    plt.close(fig)
    print(f"  wrote figures/{name}.png/.pdf")


def f1_payoff_heatmap() -> None:
    """F1: who beats whom with no noise."""
    cfg = load_config("E1")
    A = pd.read_csv(RESULTS / "E1" / "payoff_matrix.csv", index_col=0)
    order = pd.read_csv(RESULTS / "E1" / "ranking.csv")["strategy"].tolist()
    A = A.loc[order, order]  # sort rows and columns by tournament rank

    fig, ax = plt.subplots(figsize=(8, 7.2))
    im = ax.imshow(A.values, cmap=BLUES, vmin=0, vmax=5)
    ax.set_xticks(range(len(order)), order, rotation=45, ha="right")
    ax.set_yticks(range(len(order)), order)
    ax.set_xlabel("Opponent (column j)")
    ax.set_ylabel("Player (row i), sorted by tournament rank")
    for i in range(len(order)):
        for j in range(len(order)):
            v = A.values[i, j]
            ax.text(
                j,
                i,
                f"{v:.2f}",
                ha="center",
                va="center",
                fontsize=7.5,
                color="white" if v > 2.6 else TEXT,
            )
    cb = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.03)
    cb.set_label("Average payoff per round of row vs column (0 to 5)")
    ax.set_title("F1. Payoff matrix A, no noise (E1)", loc="left", color=TEXT, fontsize=12)
    save(
        fig,
        "F1_payoff_matrix",
        "Cell (i, j) = average per-round payoff of row strategy i against column strategy j. "
        + params_caption(cfg),
    )


def f2_ranking() -> None:
    """F2: baseline ranking with 95% CIs, nice vs not-nice strategies."""
    cfg = load_config("E1")
    rk = pd.read_csv(RESULTS / "E1" / "ranking.csv").iloc[::-1]  # best at the top
    nice = rk["code"].isin(NICE)
    colors = np.where(nice, PALETTE[0], PALETTE[1])
    err = [rk["score"] - rk["ci_low"], rk["ci_high"] - rk["score"]]

    fig, ax = plt.subplots(figsize=(8, 5.5))
    y = np.arange(len(rk))
    ax.barh(
        y,
        rk["score"],
        height=0.62,
        color=colors,
        xerr=err,
        error_kw={"ecolor": TEXT, "elinewidth": 1, "capsize": 3},
    )
    ax.set_yticks(y, rk["strategy"])
    for yi, s in zip(y, rk["score"]):
        ax.text(0.05, yi, f"{s:.2f}", va="center", ha="left", fontsize=8, color="white")
    ax.set_xlim(0, 3.2)
    ax.axvline(3, color=MUTED, ls="--", lw=1)
    ax.text(3.02, len(rk) - 0.6, "R = 3\n(full cooperation)", fontsize=8, color=MUTED, va="top")
    ax.set_xlabel("Mean payoff per round against the whole pool (95% bootstrap CI)")
    ax.grid(axis="x")
    ax.set_axisbelow(True)
    handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in PALETTE[:2]]
    ax.legend(handles, ["Nice (never defects first)", "Not nice"], loc="lower right", frameon=False)
    ax.set_title("F2. Tournament ranking, no noise (E1)", loc="left", color=TEXT, fontsize=12)
    save(
        fig,
        "F2_ranking",
        "Score = mean over all opponents, including self-play. " + params_caption(cfg),
    )


def f3_noise_sweep() -> None:
    """F3: mean tournament score vs noise, one line per strategy."""
    df = pd.read_csv(RESULTS / "E2" / "scores.csv")
    fig, ax = plt.subplots(figsize=(9, 5.8))
    order = df[df.epsilon == 0].sort_values("rank").strategy
    for lab in order:
        d = df[df.strategy == lab].sort_values("epsilon")
        key = lab in COLOR
        ax.plot(
            d.epsilon,
            d.score,
            color=color(lab),
            lw=2 if key else 1.2,
            ls="-" if key else "--",
            marker="o",
            ms=4,
            label=lab,
            zorder=3 if key else 2,
        )
        if key:
            ax.fill_between(d.epsilon, d.ci_low, d.ci_high, color=color(lab), alpha=0.15, lw=0)
    eps_axis(ax)
    ax.set_ylabel("Mean payoff per round vs the whole pool")
    ax.grid(axis="y")
    ax.legend(
        frameon=False,
        fontsize=8.5,
        loc="upper left",
        bbox_to_anchor=(1.01, 1),
        title="ranked at ε = 0",
    )
    title(ax, "F3. Tournament score vs noise (E2)")
    cfg = load_config("E2")
    save(
        fig,
        "F3_noise_sweep",
        "Bands: 95% bootstrap CI (shown for coloured strategies; grey dashed = non-reciprocal "
        "strategies). " + params_caption(cfg),
    )


def f4_echo() -> None:
    """F4: self-play payoff vs noise against the B4 benchmarks."""
    df = pd.read_csv(RESULTS / "E3" / "echo_summary.csv")
    cfg = load_config("E3")
    fig, ax = plt.subplots(figsize=(8.5, 5.2))
    for code in cfg["strategies"]:
        lab = "GTFT(0.33)" if code == "GTFT" else code
        d = df[df.pair == f"{code} vs {code}"]
        ax.errorbar(
            d.epsilon,
            d.payoff,
            yerr=[d.payoff - d.ci_low, d.ci_high - d.payoff],
            color=color(lab),
            lw=2,
            marker="o",
            ms=5,
            capsize=3,
            label=f"{lab} vs {lab}",
        )
    for y, text, dy in (
        (3, "R = 3 (full cooperation)", 0.02),
        (2.25, "B4: (R+S+T+P)/4 = 2.25 (TFT echo)", -0.03),
    ):
        ax.axhline(y, color=MUTED, ls="--", lw=1)
        ax.text(
            0.21,
            y + dy,
            text,
            ha="right",
            va="bottom" if dy > 0 else "top",
            fontsize=8.5,
            color=MUTED,
        )
    eps_axis(ax)
    ax.set_ylim(2.1, 3.1)
    ax.set_ylabel("Average payoff per round (self-play)")
    ax.grid(axis="y")
    ax.legend(frameon=False, loc="center left", bbox_to_anchor=(0.12, 0.55))
    title(ax, "F4. The echo effect: self-play under noise vs theory (E3)")
    save(
        fig,
        "F4_echo_effect",
        f"Each point: mean of {cfg['n_reps']} matches of {cfg['n_rounds']} rounds, 95% normal "
        "CI. TFT drops to 2.25 for any ε > 0 (B4); error-correcting strategies stay near R. "
        f"Payoffs T=5, R=3, P=1, S=0; seed {cfg['seed']}.",
    )


def f5_trace() -> None:
    """F5: move traces with one error: TFT echoes, WSLS recovers."""
    tr = pd.read_csv(RESULTS / "E3" / "traces.csv")
    cfg = load_config("E3")
    pairs = list(tr.pair.unique())
    fig, axes = plt.subplots(len(pairs), 1, figsize=(10, 1.9 * len(pairs) + 0.6))
    cmap = {"C": COLOR["TFT"], "D": COLOR["GTFT(0.33)"]}
    for ax, pair in zip(np.atleast_1d(axes), pairs):
        d = tr[tr.pair == pair]
        n = d["round"].max()
        for _, r in d.iterrows():
            y = 2 - r.player
            ax.add_patch(
                plt.Rectangle((r["round"] - 0.45, y - 0.4), 0.9, 0.8, color=cmap[r.move], lw=0)
            )
            ax.text(
                r["round"],
                y,
                r.move,
                ha="center",
                va="center",
                color="white",
                fontsize=8,
                fontweight="bold",
            )
            if r.error:
                ax.add_patch(
                    plt.Rectangle(
                        (r["round"] - 0.5, y - 0.48), 1.0, 0.96, fill=False, ec=TEXT, lw=2
                    )
                )
                ax.annotate(
                    "noise error",
                    (r["round"], y + 0.5),
                    (r["round"] + 1.5, 1.75),
                    fontsize=8,
                    color=TEXT,
                    arrowprops={"arrowstyle": "->", "color": TEXT, "lw": 0.8},
                )
        ax.set_xlim(0.4, n + 0.6)
        ax.set_ylim(-0.6, 1.9)
        ax.set_yticks([1, 0], ["Player 1", "Player 2"])
        ax.set_xticks(range(1, n + 1, 2))
        ax.spines[["left", "bottom"]].set_visible(False)
        ax.tick_params(length=0)
        ax.set_title(pair, loc="left", fontsize=10, color=TEXT)
    np.atleast_1d(axes)[-1].set_xlabel("Round")
    handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in cmap.values()]
    fig.legend(handles, ["C (cooperate)", "D (defect)"], loc="upper right", frameon=False, ncol=2)
    fig.suptitle(
        "F5. One error: TFT echoes forever, WSLS recovers in two rounds (E3)",
        x=0.01,
        ha="left",
        fontsize=12,
        color=TEXT,
    )
    fig.tight_layout()
    save(
        fig,
        "F5_move_traces",
        f"Self-play matches of {cfg['trace_rounds']} rounds at ε = {cfg['trace_epsilon']}, "
        "chosen (first seed) to contain exactly one noise error, outlined in black. Squares "
        "show actual moves.",
    )


def f6_forgiveness_dial() -> None:
    """F6: GTFT(g) score over (g, epsilon); best g per row and the B5 optimum 1/3."""
    df = pd.read_csv(RESULTS / "E4" / "gtft_scores.csv")
    cfg = load_config("E4")
    deltas = cfg["deltas"]
    fig, axes = plt.subplots(1, len(deltas), figsize=(13, 4.8), sharey=True)
    for ax, d in zip(axes, deltas):
        t = df[df.delta == d].pivot(index="epsilon", columns="g", values="score")
        im = ax.imshow(t.values, cmap=BLUES, aspect="auto", origin="lower")
        gs = t.columns.to_numpy()
        ax.set_xticks(range(0, len(gs), 2), [f"{g:.1f}" for g in gs[::2]])
        ax.set_yticks(range(len(t.index)), [f"{e:g}" for e in t.index])
        best = t.values.argmax(axis=1)
        ax.plot(
            best, range(len(t.index)), "o", color="white", mec=TEXT, ms=7, label="best g for this ε"
        )
        third = np.interp(1 / 3, gs, range(len(gs)))
        ax.axvline(third, color="white", ls="--", lw=1.5)
        ax.text(third + 0.2, 0.25, "B5: g* = 1/3", color="white", fontsize=9)
        ax.set_xlabel("Generosity g (probability of forgiving a defection)")
        ax.set_title(f"δ = {d} (mean {1 / (1 - d):.0f} rounds)", loc="left", fontsize=10)
        cb = fig.colorbar(im, ax=ax, fraction=0.05, pad=0.02)
        cb.set_label("GTFT(g) mean payoff per round")
    axes[0].set_ylabel("Noise ε")
    axes[0].legend(loc="lower right", fontsize=8, framealpha=0.9)
    fig.suptitle(
        "F6. How much forgiveness pays: GTFT(g) in the full pool (E4)",
        x=0.01,
        ha="left",
        fontsize=12,
        color=TEXT,
    )
    fig.tight_layout()
    save(
        fig,
        "F6_forgiveness_dial",
        "Each cell: tournament score of GTFT(g) replacing GTFT(1/3) in the 11-strategy pool. "
        "Colour scale per panel. White dots: best g per noise level; dashed: Nowak-Sigmund "
        f"optimum. Payoffs T=5, R=3, P=1, S=0; {cfg['n_reps']} reps; seed {cfg['seed']}.",
    )


def f6b_exploitation() -> None:
    """F6b: why too much forgiveness fails: what ALLD earns against GTFT(g)."""
    df = pd.read_csv(RESULTS / "E4" / "gtft_scores.csv")
    df = df[df.delta == 0.99]
    fig, ax = plt.subplots(figsize=(8, 4.8))
    for e, c in zip([0.0, 0.05, 0.2], [COLOR["TFT"], COLOR["GTFT(0.33)"], COLOR["CTFT"]]):
        d = df[df.epsilon == e]
        ax.plot(d.g, d.alld_vs_gtft, color=c, lw=2, label=f"ALLD vs GTFT(g), ε = {e:g}")
        ax.plot(d.g, d.gtft_self, color=c, lw=2, ls=":", label=f"GTFT(g) vs itself, ε = {e:g}")
    ax.axvline(0.5, color=MUTED, ls="--", lw=1)
    ax.text(
        0.51, 1.2, "g = (R−P)/(T−P) = 1/2:\nALLD earns R against GTFT", fontsize=8.5, color=MUTED
    )
    ax.axvline(1 / 3, color=MUTED, ls="--", lw=1)
    ax.text(0.34, 4.4, "g* = 1/3", fontsize=8.5, color=MUTED)
    ax.set_xlabel("Generosity g")
    ax.set_ylabel("Average payoff per round")
    ax.grid(axis="y")
    ax.legend(frameon=False, fontsize=8, ncol=2, loc="upper left")
    ax.set_ylim(0.8, 5.2)
    title(ax, "F6b. Too much forgiveness invites exploitation (E4)")
    save(
        fig,
        "F6b_exploitation",
        "Solid: ALLD's payoff against GTFT(g); dotted: what a GTFT(g) population earns. Once "
        "ALLD earns more than GTFT earns against itself, ALLD can invade. δ = 0.99, payoffs "
        "T=5, R=3, P=1, S=0.",
    )


def stacked_shares(ax, d: pd.DataFrame, keep: set[str]) -> list:
    """Stacked area of shares over generations; strategies not in `keep` lumped as Other."""
    d = d.assign(lab=np.where(d.strategy.isin(keep), d.strategy, "Other"))
    t = d.pivot_table(index="generation", columns="lab", values="share", aggfunc="sum")
    cols = [c for c in COLOR if c in t.columns] + [c for c in t.columns if c not in COLOR]
    t = t[cols]
    x = t.index.to_numpy() + 1
    polys = ax.stackplot(
        x,
        t.T.values,
        colors=[color(c) if c != "Other" else "#d9d9d9" for c in cols],
        labels=cols,
        lw=0,
    )
    ax.set_xscale("log")
    ax.set_xlim(1, x.max())
    ax.set_ylim(0, 1)
    return polys


def f7_evolution() -> None:
    """F7: population shares over generations, one panel per (scenario, epsilon), T = 5."""
    sh = pd.read_csv(RESULTS / "E5" / "shares.csv")
    cfg = load_config("E5")
    sh = sh[sh["T"] == 5]
    scen, eps = cfg["scenarios"], cfg["epsilons"]
    final = sh[sh.generation == sh.generation.max()]
    keep = set(final[final.share > 0.02].strategy) | {"ALLD", "TFT", "WSLS"}
    fig, axes = plt.subplots(
        len(scen), len(eps), figsize=(12, 2.4 * len(scen) + 0.8), sharex=True, sharey=True
    )
    for i, sc in enumerate(scen):
        for j, e in enumerate(eps):
            ax = axes[i, j]
            stacked_shares(ax, sh[(sh.scenario == sc) & (sh.epsilon == e)], keep)
            if i == 0:
                ax.set_title(f"ε = {e:g}", fontsize=10)
            if j == 0:
                ax.set_ylabel(f"{sc.replace('_', ' ')}\nshare", fontsize=9)
            if i == len(scen) - 1:
                ax.set_xlabel("Generation + 1 (log)")
    labels = [c for c in [*COLOR, *GREYS] if c in keep]
    handles = [plt.Rectangle((0, 0), 1, 1, color=color(c)) for c in labels]
    handles.append(plt.Rectangle((0, 0), 1, 1, color="#d9d9d9"))
    labels.append("Other")
    fig.legend(
        handles,
        labels,
        loc="upper center",
        ncol=len(labels),
        frameon=False,
        bbox_to_anchor=(0.5, 1.0),
    )
    fig.suptitle(
        "F7. Who survives evolution (replicator dynamics, E5)",
        x=0.01,
        y=1.04,
        ha="left",
        fontsize=12,
        color=TEXT,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    save(
        fig,
        "F7_evolution",
        "Rows: initial population (uniform; ALLD 50%; ALLD 95% + TFT 5%; WSLS 99% + ALLD 1%). "
        f"Columns: noise. Payoff matrix from a tournament at δ = {cfg['delta']}, T=5, R=3, P=1, "
        f"S=0, {cfg['n_reps']} reps; {cfg['generations']} generations.",
    )


def f7b_wsls_b6() -> None:
    """F7b: benchmark B6, ALLD invades WSLS at T = 5 but not at T = 4.5."""
    sh = pd.read_csv(RESULTS / "E5" / "shares.csv")
    sh = sh[sh.scenario == "wsls_resident"]
    eps = sorted(sh.epsilon.unique())
    fig, axes = plt.subplots(2, len(eps), figsize=(11, 4.6), sharex=True, sharey=True)
    for i, T in enumerate([5.0, 4.5]):
        for j, e in enumerate(eps):
            ax = axes[i, j]
            stacked_shares(ax, sh[(sh["T"] == T) & (sh.epsilon == e)], {"WSLS", "ALLD"})
            if i == 0:
                ax.set_title(f"ε = {e:g}", fontsize=10)
            if j == 0:
                ax.set_ylabel(f"T = {T:g}\n(T+P)/2 = {(T + 1) / 2:g}\nshare", fontsize=9)
            if i == 1:
                ax.set_xlabel("Generation + 1 (log)")
    handles = [plt.Rectangle((0, 0), 1, 1, color=color(c)) for c in ("WSLS", "ALLD")]
    fig.legend(handles, ["WSLS", "ALLD"], loc="upper right", ncol=2, frameon=False)
    fig.suptitle(
        "F7b. Benchmark B6: ALLD invades WSLS unless R > (T+P)/2",
        x=0.01,
        ha="left",
        fontsize=12,
        color=TEXT,
    )
    fig.tight_layout()
    save(
        fig,
        "F7b_wsls_vs_alld",
        "Start: WSLS 99%, ALLD 1%. With T = 5, ALLD earns (T+P)/2 = 3 = R against WSLS (neutral) "
        "and does better against itself, so it takes over. With T = 4.5, (T+P)/2 = 2.75 < R, so "
        "WSLS repels it. δ = 0.99, 50 reps.",
    )


def threshold_lines(ax, T: float, c: str, label_y: float) -> None:
    b1, b2 = (T - 3) / (T - 1), max((T - 3) / (T - 1), (T - 3) / 3)
    for x, name, ls in ((b1, "B1", ":"), (b2, "B2", "--")):
        ax.axvline(x, color=c, ls=ls, lw=1.2)
        ax.text(
            x + 0.005,
            label_y,
            f"{name} = {x:.3g}",
            rotation=90,
            fontsize=8,
            color=TEXT,
            va="bottom",
        )


def f8_shadow() -> None:
    """F8: equilibrium cooperation vs delta, with the B1 and B2 thresholds."""
    df = pd.read_csv(RESULTS / "E6" / "cooperation_vs_delta.csv")
    cfg = load_config("E6")
    fig, ax = plt.subplots(figsize=(8.5, 5.2))
    for e, c in zip(cfg["epsilons"], PALETTE):
        d = df[df.epsilon == e]
        ax.plot(d.delta, d.cooperation, color=c, lw=2, marker="o", ms=4, label=f"ε = {e:g}")
        ax.fill_between(
            d.delta, d.ci_low.clip(0, 1), d.ci_high.clip(0, 1), color=c, alpha=0.15, lw=0
        )
    threshold_lines(ax, 5, MUTED, 0.02)
    ax.axvspan(0.5, 2 / 3, color=MUTED, alpha=0.08, lw=0)
    ax.set_xlabel("Continuation probability δ (shadow of the future)")
    ax.set_ylabel("Cooperation rate at evolutionary equilibrium")
    ax.set_ylim(-0.02, 1.05)
    ax.grid(axis="y")
    ax.legend(frameon=False, loc="upper left")
    title(ax, "F8. Theory vs simulation: the shadow of the future (E6)")
    save(
        fig,
        "F8_shadow_of_future",
        "Replicator dynamics (uniform start, "
        f"{cfg['generations']} generations) on the tournament matrix at each δ; mean and 95% CI "
        f"over {cfg['n_seeds']} independent seeds. Dashed: B2 = (T−R)/(R−S) = 0.667; dotted: "
        "B1 = (T−R)/(T−P) = 0.5. Payoffs T=5, R=3, P=1, S=0, 50 reps per pairing.",
    )


def f9_niches() -> None:
    """F9: which strategy dominates evolution in each (epsilon, delta) cell, originals in."""
    eq = pd.read_csv(RESULTS / "E7" / "niche_equilibria.csv")
    eq = eq[eq.delta >= 0.4]
    rows = []
    for (d, e), g in eq.groupby(["delta", "epsilon"]):
        mode = g.dominant.mode().iloc[0]
        rows.append(dict(delta=d, epsilon=e, dominant=mode, share=g[f"share_{mode}"].mean()))
    t = pd.DataFrame(rows)
    deltas, epss = sorted(t.delta.unique()), sorted(t.epsilon.unique())
    fig, ax = plt.subplots(figsize=(9, 7))
    for _, r in t.iterrows():
        x, y = epss.index(r.epsilon), deltas.index(r.delta)
        mixed = r.share < 0.5
        ax.add_patch(
            plt.Rectangle(
                (x - 0.48, y - 0.48),
                0.96,
                0.96,
                color=color(r.dominant),
                alpha=0.35 if mixed else 1,
                lw=0,
            )
        )
        txt = f"{r.dominant}\n{r.share:.2f}"
        ax.text(
            x,
            y,
            txt,
            ha="center",
            va="center",
            fontsize=7.5,
            color=TEXT if mixed or r.dominant in GREYS else "white",
        )
    ax.set_xlim(-0.5, len(epss) - 0.5)
    ax.set_ylim(-0.5, len(deltas) - 0.5)
    ax.set_xticks(range(len(epss)), [f"{e:g}" for e in epss])
    ax.set_yticks(range(len(deltas)), [f"{d:g}" for d in deltas])
    ax.set_xlabel("Noise ε")
    ax.set_ylabel("Continuation probability δ")
    for name, b in (("B1", 0.5), ("B2", 2 / 3)):
        y = np.interp(b, deltas, range(len(deltas)))
        ax.axhline(y, color=TEXT, ls="--" if name == "B2" else ":", lw=1)
        ax.text(len(epss) - 0.45, y, f" {name}", va="center", fontsize=9)
    title(ax, "F9. Niche map: the dominant strategy after evolution (E7, 15 strategies)")
    save(
        fig,
        "F9_niche_map",
        "Cell: most common winner over 10 seeds (replicator dynamics from a uniform start, 2000 "
        "generations, 15-strategy pool incl. originals AF, GWA, PF, REP) and its mean final share. "
        "Pale cells: no strategy above 50% (a mixed, often neutral population). Payoffs T=5, R=3, "
        "P=1, S=0.",
    )


def f9b_originals_noise() -> None:
    """F9b: tournament score vs noise with the original strategies in the pool."""
    df = pd.read_csv(RESULTS / "E7" / "noise_scores.csv")
    show = ["REP", "AF", "GWA", "PF", "GTFT(0.33)", "TFT", "CTFT", "GRIM"]
    fig, ax = plt.subplots(figsize=(9, 5.5))
    for lab in show:
        d = df[df.strategy == lab].sort_values("epsilon")
        original = lab in {"REP", "AF", "GWA", "PF"}
        ax.plot(
            d.epsilon,
            d.score,
            color=color(lab),
            lw=2.4 if original else 1.3,
            ls="-" if original else "--",
            marker="o",
            ms=4,
            label=lab,
        )
        ax.fill_between(d.epsilon, d.ci_low, d.ci_high, color=color(lab), alpha=0.12, lw=0)
    eps_axis(ax)
    ax.set_ylabel("Mean payoff per round vs the whole pool")
    ax.grid(axis="y")
    ax.legend(
        frameon=False,
        fontsize=8.5,
        ncol=2,
        loc="lower left",
        title="solid = original, dashed = known",
    )
    title(ax, "F9b. Original strategies under noise (E7 rerun of E2)")
    save(
        fig,
        "F9b_originals_noise",
        "15-strategy pool (11 known + 4 originals). Bands: 95% bootstrap CI. δ = 0.99, payoffs "
        "T=5, R=3, P=1, S=0, 50 reps per pairing, seed 42.",
    )


def f10_payoff_thresholds() -> None:
    """F10: do the cooperation thresholds move with T as B1/B2 predict?"""
    r2 = pd.read_csv(RESULTS / "R2" / "payoff_cooperation_vs_delta.csv")
    e6 = pd.read_csv(RESULTS / "E6" / "cooperation_vs_delta.csv")
    df = pd.concat([r2, e6])
    df = df[df.epsilon == 0]
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.6), sharey=True)
    for ax, T, c in zip(axes, [4.5, 5.0, 5.9], PALETTE):
        d = df[df["T"] == T].sort_values("delta")
        ax.plot(d.delta, d.cooperation, color=c, lw=2, marker="o", ms=4)
        ax.fill_between(
            d.delta, d.ci_low.clip(0, 1), d.ci_high.clip(0, 1), color=c, alpha=0.15, lw=0
        )
        threshold_lines(ax, T, MUTED, 0.02)
        ax.set_title(f"T = {T:g}   ((T+S)/2 = {T / 2:g} vs R = 3)", loc="left", fontsize=10)
        ax.set_xlabel("Continuation probability δ")
        ax.grid(axis="y")
    axes[0].set_ylabel("Cooperation rate at evolutionary equilibrium")
    fig.suptitle(
        "F10. Thresholds move with the temptation T (robustness R2, ε = 0)",
        x=0.01,
        ha="left",
        fontsize=12,
        color=TEXT,
    )
    fig.tight_layout()
    save(
        fig,
        "F10_payoff_thresholds",
        "Same method as F8 at ε = 0 (T = 5 from E6 with 30 seeds; T = 4.5 and 5.9 from R2 with 10 "
        "seeds). Dotted: B1 = (T−R)/(T−P); dashed: B2 = max(B1, (T−R)/(R−S)). At T = 5.9 "
        "alternating exploitation pays (T+S)/2 = 2.95 ≈ R, so half-cooperative STFT/JOSS/TFT "
        "populations appear early.",
    )


def f11_robustness_pools() -> None:
    """F11: rank of each strategy in each pool, without noise and at epsilon = 0.05."""
    df = pd.read_csv(RESULTS / "R1" / "pool_scores.csv")
    e2 = pd.read_csv(RESULTS / "E2" / "scores.csv").assign(pool="full (E2)")
    df = pd.concat([e2, df])
    df = df[df.epsilon.isin([0.0, 0.05])]
    df["col"] = df.pool + "\nε=" + df.epsilon.map("{:g}".format)
    cols = list(dict.fromkeys(df.col))
    order = e2[e2.epsilon == 0].sort_values("rank").strategy.tolist()
    order += [s for s in df.strategy.unique() if s not in order]
    t = df.pivot(index="strategy", columns="col", values="rank").loc[order, cols]
    fig, ax = plt.subplots(figsize=(11, 6.5))
    ax.imshow(t.values, cmap=BLUES.reversed(), aspect="auto", vmin=1, vmax=12)
    for i in range(t.shape[0]):
        for j in range(t.shape[1]):
            v = t.values[i, j]
            if not np.isnan(v):
                ax.text(
                    j,
                    i,
                    f"{v:.0f}",
                    ha="center",
                    va="center",
                    fontsize=8,
                    color="white" if v <= 5 else TEXT,
                )
    ax.set_xticks(range(len(cols)), cols, fontsize=8)
    ax.set_yticks(range(len(order)), order)
    ax.set_xlabel("Pool and noise level (blank = strategy not in that pool)")
    title(ax, "F11. Robustness: tournament rank in four different pools (R1)")
    save(
        fig,
        "F11_robustness_pools",
        "Rank 1 = best (dark). Pools: full 11-strategy pool (E2); nice only; many exploiters "
        "(6 exploiters incl. JOSS at 10/30/50% sneak rate); a random 8-strategy subset. δ = 0.99, "
        "payoffs T=5, R=3, P=1, S=0, 50 reps, seed 42.",
    )


FIGURES_BY_EXPERIMENT = {
    "E1": [f1_payoff_heatmap, f2_ranking],
    "E2": [f3_noise_sweep],
    "E3": [f4_echo, f5_trace],
    "E4": [f6_forgiveness_dial, f6b_exploitation],
    "E5": [f7_evolution, f7b_wsls_b6],
    "E6": [f8_shadow],
    "E7": [f9_niches, f9b_originals_noise],
    "R1": [f11_robustness_pools],
    "R2": [f10_payoff_thresholds],
}

if __name__ == "__main__":
    for exp, makers in FIGURES_BY_EXPERIMENT.items():
        if not (RESULTS / exp).exists():
            print(f"skip {exp}: no results (run `python run.py {exp}` first)")
            continue
        print(exp)
        for make in makers:
            make()
