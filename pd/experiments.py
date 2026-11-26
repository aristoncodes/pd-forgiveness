"""Experiments E1-E7. Each function takes a config dict and an output folder, runs the
simulation and saves raw results as CSV. No plotting here (see analysis/make_figures.py).
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from .game import Payoffs
from .tournament import TournamentResult, run_tournament


def to_markdown(df: pd.DataFrame, floatfmt: str = ".3f") -> str:
    """Render a DataFrame as a GitHub Markdown table (no extra dependency)."""

    def fmt(v):
        return format(v, floatfmt) if isinstance(v, float) else str(v)

    lines = ["| " + " | ".join(df.columns) + " |", "|" + "---|" * len(df.columns)]
    lines += ["| " + " | ".join(fmt(v) for v in row) + " |" for row in df.itertuples(index=False)]
    return "\n".join(lines) + "\n"


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
    ranking.to_csv(out / "ranking.csv", index=False)
    (out / "ranking.md").write_text(to_markdown(ranking))
    return ranking


def e1(cfg: dict, out: Path) -> None:
    """E1 baseline tournament, no noise: ranking, payoff matrix, cooperation matrix."""
    res = run_tournament(
        cfg["pool"],
        Payoffs(**cfg["payoffs"]),
        cfg["delta"],
        cfg["epsilon"],
        cfg["n_reps"],
        cfg["seed"],
    )
    print(save_tournament(res, out).to_string(index=False))
