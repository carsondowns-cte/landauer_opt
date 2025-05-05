"""
Top-level user API: :func:`optimize`.

   - runs greedy min-cut
   - decides shot budget via parity policy
   - inserts measure+reset
   - returns (new_circuit, report_dict)
"""

from __future__ import annotations
from typing import Dict, List, Tuple

from qiskit import QuantumCircuit, ClassicalRegister

from .metrics import landauer_cost
from .cut import mincut_measure
from .policy import greedy_parity_shots


def _insert_measure_reset(circ: QuantumCircuit, qubits: List[int]) -> QuantumCircuit:
    out = circ.copy()
    need = max(qubits) + 1
    if out.num_clbits < need:
        out.add_register(ClassicalRegister(need - out.num_clbits))

    for q in qubits:
        out.measure(q, q)
        out.reset(q)
    return out


def optimize(
    circ: QuantumCircuit,
    *,
    max_cluster: int = 4,
    fidelity: float = 0.95,
    T: float = 0.02,
    eta: float = 0.05,
    heat_cap: float | None = None,
) -> Tuple[QuantumCircuit, Dict]:
    """
    Adaptive Landauer-aware placement.

    Returns
    -------
    optimized_circuit
    report : dict
        Keys = "ok", "cuts", "base_bits", "extra_bits",
        "total_bits", "landauer_J".
    """
    cuts = list(mincut_measure(circ, max_cluster))
    extra_bits = greedy_parity_shots(fidelity) * len(cuts)
    base_bits = sum(
        1 for inst in circ.data if inst.operation.name in ("measure", "reset")
    )
    total_bits = base_bits + extra_bits
    J = landauer_cost(total_bits, T, eta)

    if heat_cap is not None and J > heat_cap:
        return circ, {"ok": False, "needed_J": J}

    return (
        _insert_measure_reset(circ, cuts),
        {
            "ok": True,
            "cuts": cuts,
            "base_bits": base_bits,
            "extra_bits": extra_bits,
            "total_bits": total_bits,
            "landauer_J": J,
        },
    )
