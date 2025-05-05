"""
Landauer-aware circuit optimiser
================================

Public entry-point
------------------
    >>> new_circ, report = optimize(circ, max_cluster=4, fidelity=0.95)

Pipeline
~~~~~~~~
1.  *Min-cut*     – choose qubits to measure so every entangled cluster
   has size ≤ ``max_cluster``.
2.  *Shot budget* – greedy parity schedule to hit the requested fidelity.
3.  *Rewrite*     – insert measure + reset on the chosen qubits.
4.  *Report*      – Landauer heat estimate and bookkeeping numbers.

Returned dictionary keys
~~~~~~~~~~~~~~~~~~~~~~~~
``ok``           optimisation succeeded (False only if a heat_cap was
                supplied and the design would exceed it)

``cuts``         list[int]  indices of qubits measured mid-circuit

``base_bits``    # erase/measure operations already present in the input

``extra_bits``   additional bits erased by the optimiser (parity shots)

``total_bits``   base_bits + extra_bits

``landauer_J``   heat dissipation ( J )  =  *k*₍ᴮ₎ *T* ln2 · η · total_bits

``fidelity``     (optional) global |〈ψ_orig | ψ_opt〉|² after stripping
                terminal measurements
"""

from __future__ import annotations

from typing import Dict, List, Tuple

from qiskit import QuantumCircuit, ClassicalRegister
from qiskit.quantum_info import Statevector, state_fidelity
from qiskit.exceptions import QiskitError

from .metrics import landauer_cost
from .cut import mincut_measure
from .policy import greedy_parity_shots

import logging

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def _insert_measure_reset(circ: QuantumCircuit, qubits: List[int]) -> QuantumCircuit:
    """Return *new* circuit with measure+reset applied to ``qubits`` (in-place safe)."""
    out = circ.copy()
    need = max(qubits) + 1
    if out.num_clbits < need:
        out.add_register(ClassicalRegister(need - out.num_clbits))

    for q in qubits:
        out.measure(q, q)
        out.reset(q)
    return out


def _global_fidelity(orig: QuantumCircuit, opt: QuantumCircuit) -> float:
    """
    Overlap fidelity between original and optimised **unitary** circuits.

    We strip *final* measurement operations first, because
    ``Statevector.from_instruction`` cannot evolve through ``measure``.
    """
    base = orig.remove_final_measurements(inplace=False)
    cand = opt.remove_final_measurements(inplace=False)

    sv0 = Statevector.from_instruction(base)
    sv1 = Statevector.from_instruction(cand)
    return float(state_fidelity(sv0, sv1))


# ---------------------------------------------------------------------------
# public API
# ---------------------------------------------------------------------------


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
    Landauer-aware placement of mid-circuit measurements.

    Parameters
    ----------
    circ
        Input **logical** circuit (no hardware constraints assumed).

    max_cluster
        Largest entangled cluster permitted *after* inserting cuts.

    fidelity
        Target global state-fidelity that the optimiser should maintain.
        (Higher ⇒ more parity shots ⇒ more heat.)

    T
        Effective temperature ( K ) where erasures occur.

    eta
        Device / implementation overhead factor ≥ 1.
        ``eta = 1`` = Landauer limit; real hardware likely ×100 – ×1000.

    heat_cap
        Optional upper bound ( J ).  If the Landauer estimate exceeds this
        budget the optimiser returns ``ok=False`` and leaves the circuit
        unchanged.

    Returns
    -------
    (optimized_circuit, report_dict)
    """
    # ---------- 1 · choose qubits to measure --------------------------------
    cuts = list(mincut_measure(circ, max_cluster))

    # ---------- 2 · shot budget ---------------------------------------------
    extra_bits = greedy_parity_shots(fidelity) * len(cuts)

    # ---------- 3 · baseline bits already present ---------------------------
    base_bits = sum(
        1 for inst in circ.data if inst.operation.name in ("measure", "reset")
    )

    total_bits = base_bits + extra_bits
    J = landauer_cost(total_bits, T, eta)

    # ---------- 4 · heat-cap early exit -------------------------------------
    if heat_cap is not None and J > heat_cap:
        return circ, {"ok": False, "needed_J": J}

    # ---------- 5 · rewrite & bookkeeping -----------------------------------
    opt_circ = _insert_measure_reset(circ, cuts)

    report: Dict = {
        "ok": True,
        "cuts": cuts,
        "base_bits": base_bits,
        "extra_bits": extra_bits,
        "total_bits": total_bits,
        "landauer_J": J,
    }

    # optional fidelity field
    try:
        report["fidelity"] = _global_fidelity(circ, opt_circ)
    except (ImportError, QiskitError):
        # Simulator unavailable or failed – optimisation still OK
        pass

    return opt_circ, report
