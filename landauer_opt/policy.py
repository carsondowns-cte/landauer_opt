# landauer_opt/policy.py
"""
Policies that translate fidelity targets into concrete shot budgets
or choose which parity basis to measure next.

Exported symbols
----------------
adaptive_parity_policy  – online “least-sampled” selector  (Phase-2)
greedy_parity_shots     – coarse analytic budget (Phase-1)
"""

from __future__ import annotations
from math import log


# ---------------------------------------------------------------------------
# 1.  Online adaptive policy (OSB Phase-2)
# ---------------------------------------------------------------------------


def adaptive_parity_policy(
    history: list[str], targets=("X", "Y", "Z")
) -> str:  # noqa: D401
    """
    Return the Pauli basis that has been requested *least often* so far.

    Parameters
    ----------
    history
        List of single-character labels ("X", "Y", "Z") representing the
        bases already measured.
    targets
        Iterable of allowed Pauli bases (defaults to the full XYZ set).

    Examples
    --------
    >>> hist = []
    >>> adaptive_parity_policy(hist)
    'X'
    >>> hist.append("X"); adaptive_parity_policy(hist)
    'Y'
    """
    if not history:  # first call → pick deterministic starting basis
        return targets[0]

    counts = {b: history.count(b) for b in targets}
    # tie-break deterministically by the order in *targets*
    return min(targets, key=lambda b: (counts[b], targets.index(b)))


# ---------------------------------------------------------------------------
# 2.  Analytic one-shot estimate (Phase-1, still used in tests & examples)
# ---------------------------------------------------------------------------


def greedy_parity_shots(target_fidelity: float) -> int:
    """
    Quick upper-bound on the number of parity shots needed to reach a
    **global** fidelity target on an unknown qubit.

    Assumes:
      • Each parity shot rules out ½ of the remaining state-space.
      • Error probability ε ≈ 1 − fidelity.

    Returns the *total* number of shots (summed over X/Y/Z) required.

    Notes
    -----
    This is intentionally conservative; the adaptive policy generally
    stops *earlier* for typical states.
    """
    if not (0 < target_fidelity < 1):
        raise ValueError("fidelity must be in (0, 1)")

    eps = 1.0 - target_fidelity
    # information-theoretic: need log₂(1/ε) bits → same number of shots
    bits_needed = log(1 / eps, 2)
    return int(bits_needed) + 1  # round up


__all__ = ["adaptive_parity_policy", "greedy_parity_shots"]
