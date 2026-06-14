from typing import List
import random

from .models import BackendState, RequestResult
from .telemetry import update_telemetry


def simulate_step(backends: List[BackendState], policy, ts: int) -> RequestResult:
    """
    Simulate routing a single request at time step ts using the given policy.
    """
    backend = policy.choose_backend(backends)
    if backend is None:
        # No eligible backend: simulate outage
        return RequestResult(
            backend_id="none",
            latency_ms=1000.0,
            success=False,
            ts=ts,
        )

    # Draw success/failure and latency
    success = random.random() > backend.failure_rate

    # Base latency with some jitter
    jitter = random.uniform(-0.1, 0.3) * backend.base_latency_ms
    latency = max(1.0, backend.base_latency_ms + jitter)

    # If failure, simulate timeout/retry amplification
    if not success:
        latency *= 3

    # Update telemetry for this backend
    update_telemetry(backend, latency, success)

    return RequestResult(
        backend_id=backend.id,
        latency_ms=latency,
        success=success,
        ts=ts,
    )


def run_simulation(backends: List[BackendState], policy, steps: int) -> List[RequestResult]:
    """
    Run a full simulation for `steps` requests, including a brownout scenario.

    - Normal operation initially
    - Inject brownout on the first backend at ~30% of steps
    - Recover it at ~60% of steps
    """
    results: List[RequestResult] = []

    brownout_start = int(steps * 0.3)
    brownout_end = int(steps * 0.6)

    for ts in range(steps):
        # Inject brownout on backend[0]
        if ts == brownout_start:
            backends[0].failure_rate = 0.90
            backends[0].base_latency_ms *= 3

        # Recover backend[0]
        if ts == brownout_end:
            backends[0].failure_rate = 0.01
            backends[0].base_latency_ms /= 3

        res = simulate_step(backends, policy, ts)
        results.append(res)

    return results
