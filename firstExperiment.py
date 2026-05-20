# Core qiskit imports
from qiskit import QuantumCircuit
from qiskit.visualization import plot_histogram
from qiskit_aer import AerSimulator
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager

# IBM runtime specific imports
from qiskit_ibm_runtime import SamplerV2 as Sampler, QiskitRuntimeService

import matplotlib.pyplot as plt

##### ##### ##### ##### 
# 2 GOALS FOR EXPERIMENT --> States spins are in (qubits [up is 0, down is 1]), energy of configuration
##### ##### ##### #####

'''
Qiskit patterns workflow
The Qiskit patterns workflow is a general framework we use to solve quantum problems with Qiskit. It breaks a quantum computing task into four steps:
    1. Map the problem to a model that can be represented by quantum circuits
    2. Optimize the circuit to be run on a specific backend
    3. Execute the optimized circuit on the selected backend
    4. Post-process the raw measurement data

# Note --> No error mitigation for now

Before we run our circuit on a quantum computer (or a simulator if you have exhausted your free time on real quantum computers for the month), we need to prepare it for execution (through optimization)
During optimization:
    1. We choose the backend — either a real quantum computer or a simulator.
    2. We assign our circuit's qubits to physical qubits on the device.
    3. rewrite the circuit using only the gates that the quantum computer can actually perform.
    4. Optionally implement error mitigation and suppression techniques to reduce the effects of noise.

Transpiler takes care of this automatically in most cases (pass_manager)

2 Experiments below
    - Measuring counts of states (00, 01, 10, 11)
    - Measuring energy configuration of state (uses Estimator)
'''

# Experiment 1

"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Step 1 Quantum Circuit ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"

import numpy as np

# Make state
qc = QuantumCircuit(2)
qc.h(0)
qc.cx(0,1)
qc.x(1)
qc.z(0)

# Measure state
qc.measure_all()

# Draw circuit
qc.draw('mpl')

"~~~~~~~~~~~~~~~~~~~~~~~~~~~ Connecting to IBM Quantum ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
# Using .env
from dotenv import load_dotenv
import os
load_dotenv()
IBM_API_TOKEN = os.getenv("IBM_API_TOKEN")

#save account to use in the future
QiskitRuntimeService.save_account(channel="ibm_quantum_platform", 
                                  token=IBM_API_TOKEN, 
                                  overwrite=True, 
                                  set_as_default=True)
# use saved account 
service = QiskitRuntimeService(channel="ibm_quantum_platform")

# load saved credentials 
service = QiskitRuntimeService()

# Use the least busy backend, or uncomment the loading of a specific backend like "ibm_fez"
backend = service.least_busy(operational=True, simulator=False, min_num_qubits=127)
# backend = service.get_backend("ibm_fez")
print(backend.name)
"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Step 2 Transpile (optimize) ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
# Transpile circuit and optimize it for running on selected quantum computer

target = backend.target
pm = generate_preset_pass_manager(target=target, optimization_level=3) # Will handle all optimization steps
qc_isa = pm.run(qc)

qc_isa.draw('mpl')
plt.savefig("Optimized Experimental Circuit")

"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Step 3 Job-->Backend ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
sampler = Sampler(mode=backend)
job = sampler.run([qc_isa], shots=100)

result = job.result()
counts = result[0].data.meas.get_counts()
"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Step 4 Post-Process ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
print("counts = ", counts)
plot_histogram(counts)
plt.savefig("ExprimentCounts.png")

print("-----------------------------------------------------------------------------------------")
print("-----------------------------------------------------------------------------------------")
print("-----------------------------------------------------------------------------------------")

# Experiment 2

'''
Observable --> Hermitian matrix that represents something you can measure (energy, spin, magnetization)
SparsePauliOp --> Translate pauli terms (X,Y,Z) into observables
Estimator --> compute average value of each observable on state and combine according to coefficients in Hamiltonian to get total energy
'''

from qiskit.quantum_info import SparsePauliOp

# Parameters
J = 1.0 # Antiferromagnetic coupling (J<0)
hx = -0.5  # transverse field strength

"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Define Hamiltonian ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
# Hamiltonian --> H = J Z1 Z2 + hx (X1 + X2)  --> H=J*Z0*Z0+hx(X0+X1)
obs = SparsePauliOp.from_list([
    ("ZZ", J),
    ("XI", hx),
    ("IX", hx)
])

# Make State
qc = QuantumCircuit(2)
qc.h(0)
qc.cx(0,1)
qc.x(1)
qc.z(0)

# Dont need qc.measure_all() since we are not measuring circuit's states, but observables themselves, and Estimator will do those calculations for us behind the scenes anyways

# Also already connected to IBM before so don't need to redo that step

"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Step 2 Transpile (optimize) ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
# Transpile circuit and optimize it for running on selected quantum computer

target = backend.target
pm = generate_preset_pass_manager(target=target, optimization_level=3) # Will handle all optimization steps
qc_isa = pm.run(qc)
obs_isa = obs.apply_layout(layout=qc_isa.layout)

qc_isa.draw('mpl')
plt.savefig("Optimized Experimental Circuit(2)")

"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Step 3 Execute Estimator ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
from qiskit_ibm_runtime import EstimatorV2 as Estimator 

estimator = Estimator(mode=backend)

from qiskit.primitives import BackendEstimatorV2

pubs = [(qc_isa, obs_isa)]
job = estimator.run(pubs)
res = job.result()

energyConfig = res[0].data.evs

print("Energy of our state = ", energyConfig)