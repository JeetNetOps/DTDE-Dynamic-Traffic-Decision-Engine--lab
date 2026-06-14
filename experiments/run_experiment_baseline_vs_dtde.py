import random
from dtde.models import BackendState, RequestResult
from dtde.telemetry import TelemetryMonitor
from dtde.decision import DecisionEngine

def simulate_request(backend: BackendState) -> RequestResult:
    """Simulates a network request with random latency and failure chance."""
    success = random.random() > backend.failure_rate
    # If it fails, latency is usually high (timeout)
    latency = backend.base_latency_ms + random.uniform(10, 50) if success else 1000.0
    return RequestResult(backend_id=backend.id, latency_ms=latency, success=success, ts=0)

def main():
    # 1. Setup our "World"
    backends = [
        BackendState(id="Region-A", base_latency_ms=50.0, failure_rate=0.02),
        BackendState(id="Region-B", base_latency_ms=150.0, failure_rate=0.01),
        BackendState(id="Region-C", base_latency_ms=300.0, failure_rate=0.01),
    ]
    
    monitor = TelemetryMonitor(window_size=20)
    engine = DecisionEngine()
    
    stats = {"Region-A": 0, "Region-B": 0, "Region-C": 0}
    total_success = 0

    print(f"{'Step':<5} | {'Winner':<10} | {'Score':<6} | {'Status'}")
    print("-" * 40)

    # 2. Run Simulation for 100 steps
    for i in range(100):
        # SIMULATE DISASTER: At step 40, Region-A (the fastest) starts failing 80% of the time
        if i == 40:
            print("\n!!! ALERT: Region-A is experiencing a Brownout !!!\n")
            backends[0].failure_rate = 0.80

        # Engine picks the best backend based on CURRENT telemetry
        best_backend = engine.select_best_backend(backends)
        
        # Execute request
        result = simulate_request(best_backend)
        
        # Update Telemetry (The Engine "Learns")
        monitor.update_backend_stats(best_backend, result.latency_ms, result.success)
        
        # Record stats
        stats[best_backend.id] += 1
        if result.success: total_success += 1

        if i % 10 == 0 or i > 38 and i < 45: # Show detail around the failure
            score = engine.calculate_score(best_backend)
            status = "PASS" if result.success else "FAIL"
            print(f"{i:<5} | {best_backend.id:<10} | {score:.2f} | {status}")

    print("-" * 40)
    print(f"Simulation Complete. Total Success Rate: {total_success}%")
    print(f"Traffic Distribution: {stats}")

if __name__ == "__main__":
    main()
