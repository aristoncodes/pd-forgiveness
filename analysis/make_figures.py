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
    for ext in ("png", "pdf"):
        fig.savefig(FIGURES / f"{name}.{ext}", bbox_inches="tight")
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


FIGURES_BY_EXPERIMENT = {"E1": [f1_payoff_heatmap, f2_ranking]}

if __name__ == "__main__":
    for exp, makers in FIGURES_BY_EXPERIMENT.items():
        if not (RESULTS / exp).exists():
            print(f"skip {exp}: no results (run `python run.py {exp}` first)")
            continue
        print(exp)
        for make in makers:
            make()
