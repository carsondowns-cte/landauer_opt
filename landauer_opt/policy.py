"""
Simple adaptive policy:

estimate shots required in X/Y/Z parities to reach
target Bloch-vector fidelity for a single logical qubit
encoded in a GHZ-like screen.
"""


def greedy_parity_shots(target_fidelity: float = 0.95) -> int:
    """
    Return minimal integer `n` s.t. 1 – 1⁄(2n+1) ≥ target.

    Crude variance model: fidelity ≈ 1 – 1⁄(2N) after N balanced shots.
    """
    if not (0 < target_fidelity < 1):
        raise ValueError("target_fidelity must be 0 < f < 1")
    n = 0
    while 1 - 1 / (2 * n + 1) < target_fidelity:
        n += 1
    return n
