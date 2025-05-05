"""
Utility: convert a Qiskit circuit into an undirected
interaction graph (vertices = qubits, edges = CX pairs).
"""

from __future__ import annotations
import networkx as nx
from qiskit import QuantumCircuit


def circuit_to_graph(circ: QuantumCircuit) -> nx.Graph:
    """Return NetworkX graph of two-qubit interactions."""
    g = nx.Graph()
    g.add_nodes_from(range(circ.num_qubits))

    for inst in circ.data:
        if inst.operation.num_qubits == 2:
            a = circ.qubits.index(inst.qubits[0])
            b = circ.qubits.index(inst.qubits[1])
            g.add_edge(a, b)

    return g
