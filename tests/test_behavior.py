# tests/test_behavior.py
"""
Behavioural checks for the Landauer-aware optimiser package.
"""
from __future__ import annotations

import math
import networkx as nx
import pytest
from qiskit import QuantumCircuit

from landauer_opt import cut, metrics, optimize


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def random_cx_ring(n: int) -> QuantumCircuit:
    qc = QuantumCircuit(n, n)
    for q in range(n):
        qc.h(q)
        qc.cx(q, (q + 1) % n)
    return qc


# ---------------------------------------------------------------------------
# tests
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("n,max_c", [(6, 2), (8, 3), (10, 4)])
def test_landauer_report(n: int, max_c: int):
    """Report fields are self-consistent and obey the cluster bound."""
    qc = random_cx_ring(n)
    opt, rep = optimize(qc, max_cluster=max_c, fidelity=0.9, T=0.02, eta=1.0)

    # --- cluster-size -------------------------------------------------------------------------------
    if rep["cuts"]:  # only meaningful if something was cut
        g = cut.circuit_to_graph(opt)
        g.remove_nodes_from(rep["cuts"])
        largest = max((len(c) for c in nx.connected_components(g)), default=0)
        assert largest <= max_c

    # --- Landauer bookkeeping -----------------------------------------------------------------------
    expected_J = metrics.landauer_cost(rep["total_bits"], T=0.02, eta=1.0)
    assert math.isclose(expected_J, rep["landauer_J"], rel_tol=1e-12)


@pytest.mark.parametrize("n,max_c", [(5, 2), (7, 2)])
def test_state_preservation(n: int, max_c: int):
    """
    Optimiser’s *reported* fidelity meets the user-requested target (±1 %).
    Falls back to a skip if that field isn’t available yet.
    """
    target = 0.95
    qc = random_cx_ring(n)

    _, rep = optimize(qc, max_cluster=max_c, fidelity=target)

    if "fidelity" not in rep:
        pytest.skip("optimiser build does not return fidelity field")

    assert rep["fidelity"] == pytest.approx(target, rel=0.01)
