"""Strategy interface and registry.

Every strategy sees only the history of *actual* moves (its own and the opponent's) and its
own random number generator. It returns its *intended* move; the engine applies noise.
"""

from __future__ import annotations

import numpy as np

C, D = 0, 1

REGISTRY: dict[str, type[Strategy]] = {}


def register(cls: type[Strategy]) -> type[Strategy]:
    """Class decorator: add a strategy to the registry under its `code`."""
    REGISTRY[cls.code] = cls
    return cls


def make(code: str, **params) -> Strategy:
    """Build a strategy by code, e.g. make("GTFT", g=0.2)."""
    if code not in REGISTRY:
        raise KeyError(f"Unknown strategy {code!r}. Known: {sorted(REGISTRY)}")
    return REGISTRY[code](**params)


class Strategy:
    """Base class. Subclasses set `code` and implement `move`.

    `name` is the display label (includes parameters, e.g. "GTFT(0.33)").
    """

    code: str = "BASE"

    def __init__(self) -> None:
        self.name = self.code
        self.rng: np.random.Generator | None = None

    def reset(self, rng: np.random.Generator) -> None:
        """Called at the start of every match. Clears memory and stores the rng."""
        self.rng = rng

    def move(self, my_hist: list[int], opp_hist: list[int]) -> int:
        """Return the intended move (0 = C, 1 = D) given both actual histories."""
        raise NotImplementedError
