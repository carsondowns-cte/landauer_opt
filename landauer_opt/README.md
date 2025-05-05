# Landauer-Opt 🧊⚡

Energy-aware **optimization** pass for Qiskit circuits.

```python
from qiskit import QuantumCircuit
from landauer_opt import optimize

qc = QuantumCircuit(5, 5)
# ... build circuit ...
opt_circ, report = optimize(qc, max_cluster=4, fidelity=0.95)
print(report)