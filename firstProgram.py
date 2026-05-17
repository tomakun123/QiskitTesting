# pip install qiskit[visualization] qiskit-ibm-runtime qiskit-aer

# Core qiskit imports
from qiskit import QuantumCircuit
from qiskit.visualization import plot_histogram
from qiskit_aer import AerSimulator
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager

# IBM runtime specific imports
from qiskit_ibm_runtime import SamplerV2 as Sampler, QiskitRuntimeService

# Checking dependencies / environment checker
import sys
import matplotlib.pyplot as plt

import qiskit
import qiskit_aer
import qiskit_ibm_runtime

print("Python:", sys.version.split()[0])
print("qiskit:", qiskit.__version__)
print("qiskit-aer:", qiskit_aer.__version__)
print("qiskit-ibm-runtime:", qiskit_ibm_runtime.__version__) 

"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"

# Creating a bell state
bell = QuantumCircuit(2) # 2 qubit circuit
bell.h(0) # hadamard gate on qubit 0
bell.cx(0, 1) # cnot gate with control qubit 0 and target qubit 1

bell.measure_all() # measure all qubits

bell.draw("mpl") # draw the circuit
plt.savefig("bell_circuit.png") # save the figure

"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"

# Helper function to run a circuit on a backend and get the counts
def run_circuit_and_get_counts(circuit, backend, shots=1000):
    """
    Runs a quantum circuit on a specified backend and returns the measurement counts

    Args:
        circuit (QuantumCircuit): The quantum circuit to be executed/run
        backend: Qiskit backend (real device/simulator) to run the circuit on
        shots (int): The number of times/shots to execute the circuit (default: 1000)

    Returns:
        dict: A dictionary containing the measurement counts (bitstring -> count)p
    """
    # Transpile the circuit for the given backend
    pass_manager = generate_preset_pass_manager(backend=backend, optimization_level=1) #create pass_manager which hardware can actually understand
    isa_circuit = pass_manager.run(circuit)

    # Run the circuit on the backend
    sampler = Sampler(mode=backend)
    job = sampler.run([isa_circuit], shots=shots)

    # Get the results and return the counts
    result = job.result()
    
    return result[0].data.meas.get_counts() #meas is register made from measure_all() method

"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"

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
# Backend will be used with helper function above
'''
Can also run backend on simulator (using AerSimulator) which is an ideal simulation of qubits, but does not capture noise and errors of real devices.

backend = AerSimulator() # use simulator instead of real device
counts = run_circuit_and_get_counts(bell, backend) # default shots=1000
print(counts)
'''

"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"

counts = run_circuit_and_get_counts(bell, backend) # default shots=1000
plot_histogram(counts)
plt.savefig("bell_counts.png")
