"""
Landauer cost metric.

Defines :func:`landauer_cost`, the minimum heat (Joules) dissipated when
`bits` logically irreversible operations (measure/reset) occur.
"""

from math import log

_kB = 1.380_649e-23  # J K⁻¹
_LOG2 = log(2)  # natural log 2


def landauer_cost(
    bits: int,
    T: float = 0.02,
    eta: float = 0.05,
) -> float:
    """
    Return minimum heat **in joules** for `bits` erased.

    Parameters
    ----------
    bits
        Number of logically irreversible bit erasures (≥ 0).
    T
        Bath temperature in kelvin (default 20 mK = 0.02 K).
    eta
        Thermodynamic efficiency 0 < η ≤ 1.
        η = 1 → quasistatic (Landauer limit); real hardware η ≲ 0.05.

    Notes
    -----
    *Landauer 1961* : ΔQ ≥ k\_B T ln 2 per erased bit.

    """
    if bits < 0:
        raise ValueError("bits must be non-negative")
    if not (0 < eta <= 1):
        raise ValueError("eta must be 0 < η ≤ 1")
    return bits * _kB * T * _LOG2 / eta
