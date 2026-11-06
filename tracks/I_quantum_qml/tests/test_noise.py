from optlab.quantum.algorithms import noisy_grover_success


def test_gate_local_noise_reduces_grover_success():
    noiseless = noisy_grover_success(single_qubit_error=0.0, two_qubit_error=0.0)
    noisy = noisy_grover_success(single_qubit_error=0.005, two_qubit_error=0.05)
    assert noiseless > 1.0 - 1e-9
    assert 0.25 < noisy < noiseless
