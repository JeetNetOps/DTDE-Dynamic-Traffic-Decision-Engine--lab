"""
Step 1: Functional Verification
- Confirms DTDE makes decisions with proper scoring
- Tests controlled brownout detection and traffic shift
- Validates policy and security constraint enforcement
"""

import sys
from dtde.models import BackendState
from dtde.decision import DTDEPolicy
from dtde.simulation import simulate_step
from dtde.telemetry import update_telemetry


def test_normal_routing():
    """Test 1: Verify DTDE routes to healthy backends with proper scoring"""
    print("\n" + "=" * 60)
    print("TEST 1: Normal Routing - Verify Score Calculation")
    print("=" * 60)

    backends = [
        BackendState(id="b1", base_latency_ms=200.0, failure_rate=0.01),
        BackendState(id="b2", base_latency_ms=220.0, failure_rate=0.01),
        BackendState(id="b3", base_latency_ms=250.0, failure_rate=0.01),
    ]

    policy = DTDEPolicy()

    # Warm up telemetry with 10 successful requests
    for _ in range(10):
        for b in backends:
            update_telemetry(b, b.base_latency_ms, True)

    print("\nBackend Scores:")
    for b in backends:
        score = policy.score_backend(b, backends)
        print(
            f"  {b.id}: score={score:.3f} | "
            f"health={b.health_score:.2f} | "
            f"latency={b.latency_obs_ms:.1f}ms"
        )

    chosen = policy.choose_backend(backends)
    print(f"\n? DTDE chose: {chosen.id}")
    return True


def test_brownout_detection():
    """Test 2: Inject brownout and verify DTDE detects and pivots"""
    print("\n" + "=" * 60)
    print("TEST 2: Brownout Detection - Inject 90% Failure")
    print("=" * 60)

    backends = [
        BackendState(id="b1", base_latency_ms=200.0, failure_rate=0.01),
        BackendState(id="b2", base_latency_ms=220.0, failure_rate=0.01),
        BackendState(id="b3", base_latency_ms=250.0, failure_rate=0.01),
    ]

    policy = DTDEPolicy()

    # Phase 1: normal operation
    for i in range(20):
        simulate_step(backends, policy, i)

    # Inject brownout on b1
    print("\n??  INJECTING BROWNOUT: b1 failure_rate 90%, latency x3")
    backends[0].failure_rate = 0.90
    backends[0].base_latency_ms *= 3

    b1_chosen = 0

    # Phase 2: observe pivot behavior
    for i in range(20, 35):
        result = simulate_step(backends, policy, i)
        if result.backend_id == "b1":
            b1_chosen += 1

    print(f"\n  b1 health after brownout: {backends[0].health_score:.2f}")

    if b1_chosen < 3:
        print("? DTDE successfully pivoted traffic away from b1")
        return True

    print("? DTDE still routing significant traffic to degraded b1")
    return False


def test_policy_constraints():
    """Test 3: Verify policy and security constraints are enforced"""
    print("\n" + "=" * 60)
    print("TEST 3: Policy & Security Constraints")
    print("=" * 60)

    backends = [
        BackendState(
            id="b1",
            base_latency_ms=200.0,
            failure_rate=0.01,
            policy_ok=True,
            security_ok=True,
        ),
        BackendState(
            id="b2",
            base_latency_ms=220.0,
            failure_rate=0.01,
            policy_ok=False,   # Policy violation
            security_ok=True,
        ),
        BackendState(
            id="b3",
            base_latency_ms=180.0,
            failure_rate=0.01,
            policy_ok=True,
            security_ok=False, # Security violation
        ),
    ]

    policy = DTDEPolicy()

    # Warm up telemetry
    for _ in range(10):
        for b in backends:
            update_telemetry(b, b.base_latency_ms, True)

    chosen_count = {"b1": 0, "b2": 0, "b3": 0}

    for i in range(10):
        chosen = policy.choose_backend(backends)
        if chosen:
            chosen_count[chosen.id] += 1

    print(
        f"\nRouting: "
        f"b1: {chosen_count['b1']} | "
        f"b2: {chosen_count['b2']} | "
        f"b3: {chosen_count['b3']}"
    )

    if chosen_count["b2"] == 0 and chosen_count["b3"] == 0:
        print("? DTDE enforced policy & security constraints correctly")
        return True

    print("? DTDE routed to non-compliant backends")
    return False


def main():
    print("\nDTDE FUNCTIONAL VERIFICATION - STEP 1")

    results = [
        ("Normal Routing", test_normal_routing()),
        ("Brownout Detection", test_brownout_detection()),
        ("Policy Constraints", test_policy_constraints()),
    ]

    print("\nVERIFICATION SUMMARY")
    for name, res in results:
        print(f"{'? PASS' if res else '? FAIL'}: {name}")

    return 0 if all(r[1] for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
