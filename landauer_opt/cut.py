"""
Greedy vertex-cut heuristic.

Repeatedly removes the highest-degree vertex until
no connected component exceeds a size threshold.
"""

from __future__ import annotations
from typing import Generator
import networkx as nx

from qiskit import QuantumCircuit
from .graph_utils import circuit_to_graph


def mincut_measure(
    circ: QuantumCircuit,
    max_cluster: int = 4,
) -> Generator[int, None, None]:
    """
    Yield qubit indices to measure/reset.

    Guarantees: after removing those vertices, every
    entanglement cluster ≤ `max_cluster` qubits.
    """
    if max_cluster < 1:
        raise ValueError("max_cluster must be ≥ 1")

    g = circuit_to_graph(circ)
    while max(map(len, nx.connected_components(g))) > max_cluster:
        # pick highest-degree vertex
        v = max(g.degree, key=lambda x: x[1])[0]
        g.remove_node(v)
        yield v
