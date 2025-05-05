"""Landauer-aware optimization toolkit for Qiskit circuits."""

from importlib.metadata import version
from .metrics import landauer_cost
from .optimizer import optimize

__all__ = ["landauer_cost", "optimize", "__version__"]
__version__ = version("landauer_opt")
