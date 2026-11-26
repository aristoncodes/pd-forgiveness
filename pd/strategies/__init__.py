"""Strategy library. Importing this package fills the registry used by `make`."""

from . import classic, forgiving, original  # noqa: F401  (imported to register strategies)
from .base import REGISTRY, Strategy, make

__all__ = ["REGISTRY", "Strategy", "make"]
