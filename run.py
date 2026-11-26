"""Run experiments from their configs.

    python run.py E1        # one experiment
    python run.py all       # every experiment, in order

Each experiment reads configs/e<N>_*.yaml and writes results/<ID>/ with a copy of the config.
"""

from __future__ import annotations

import shutil
import sys
import time
from pathlib import Path

import yaml

from pd import experiments

ROOT = Path(__file__).parent


def config_path(exp_id: str) -> Path:
    """configs/e1_baseline.yaml for "E1", etc."""
    matches = sorted((ROOT / "configs").glob(f"{exp_id.lower()}_*.yaml"))
    if len(matches) != 1:
        raise SystemExit(f"Expected one config for {exp_id}, found {matches}")
    return matches[0]


def run(exp_id: str) -> None:
    path = config_path(exp_id)
    cfg = yaml.safe_load(path.read_text())
    out = ROOT / "results" / exp_id
    out.mkdir(parents=True, exist_ok=True)
    shutil.copy(path, out / "config.yaml")
    print(f"== {exp_id}: {cfg['description']}")
    t0 = time.time()
    getattr(experiments, exp_id.lower())(cfg, out)
    print(f"== {exp_id} done in {time.time() - t0:.1f}s -> {out.relative_to(ROOT)}/\n")


def all_ids() -> list[str]:
    return sorted(p.name.split("_")[0].upper() for p in (ROOT / "configs").glob("e*_*.yaml"))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    arg = sys.argv[1]
    for exp_id in all_ids() if arg == "all" else [arg.upper()]:
        run(exp_id)
