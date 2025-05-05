from qiskit import QuantumCircuit
from landauer_opt import landauer_cost, optimize


def test_landauer():
    assert abs(landauer_cost(1, T=300, eta=1) - 2.87e-21) < 1e-23


def test_optimize_smoke():
    qc = QuantumCircuit(3, 3)
    qc.cx(0, 1)
    qc.cx(1, 2)
    qc.measure(0, 0)
    opt, rep = optimize(qc, max_cluster=1, fidelity=0.9)
    assert rep["ok"] and rep["total_bits"] > 1
