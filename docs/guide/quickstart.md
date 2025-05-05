# Quick-start

```python
from qiskit import QuantumCircuit
from landauer_opt import optimize

qc = QuantumCircuit(3, 3)
qc.h(0); qc.cx(0,1); qc.cx(1,2)

opt, report = optimize(qc, max_cluster=2, fidelity=0.9)
print(report)

Run it – you should see a list of qubits the optimiser chose to
measure plus the projected Landauer heat.
