"""
Step 2: Performance & Stability Verification
- Measures mean and P95 latency
- Measures availability and failure streaks (MTTR-like)
- Compares behavior under DTDE with an injected brownout
"""

from dtde.models import BackendState
from dtde.decision import DTDEPolicy
from dtde.simulation import run_simulation
from dtde.metrics import compute_metrics


def main():
    print("\nDTDE PERFORMANCE & STABILITY VERIFICATION - STEP 2")

    # Define backends (same baseline as functional tests)
    backends = [
        BackendState(id="b1", base_latency_ms=200.0, failure_rate=0.01),
        BackendState(id="b2", base_latency_ms=220.0, failure_rate=0.01),
        BackendState(id="b3", base_latency_ms=250.0, failure_rate=0.01),
    ]

    policy = DTDEPolicy()

    # Total number of simulated requests
    steps = 1000

    print(f"\nRunning DTDE simulation for {steps} requests with injected brownout...")
    results = run_simulation(backends, policy, steps)

    metrics = compute_metrics(results)

    print("\nMETRICS (DTDE with brownout scenario):")
    print(f"  Mean response time: {metrics['mean_response_time_ms']:.1f} ms")
    print(f"  P95 latency:        {metrics['p95_latency_ms']:.1f} ms")
    print(f"  Availability:       {metrics['availability']*100:.2f} %")
    print(f"  MTTR (steps):       {metrics['mttr_steps']:.2f}")

    print("\nInterpretation:")
    print("  - Mean and P95 should remain reasonable despite the injected failure.")
    print("  - Availability should stay high (close to 100%).")
    print("  - MTTR (failure streak length) should be relatively small,")
    print("    showing DTDE reacts quickly to degradation.")

    print("\nIf these numbers look healthy compared to your expectations/baseline,")
    print("you can treat Step 2 (performance & stability) as validated.")


if __name__ == "__main__":
    main()
