import matplotlib.pyplot as plt
import random
from dtde.models import BackendState, RequestResult
from dtde.telemetry import TelemetryMonitor
from dtde.decision import DecisionEngine

def simulate_request(backend: BackendState) -> RequestResult:
    success = random.random() > backend.failure_rate
    latency = backend.base_latency_ms + random.uniform(10, 50) if success else 1000.0
    return RequestResult(backend_id=backend.id, latency_ms=latency, success=success, ts=0)

def run_visual_sim():
    backends = [
        BackendState(id="Region-A", base_latency_ms=50.0, failure_rate=0.02),
        BackendState(id="Region-B", base_latency_ms=150.0, failure_rate=0.01),
    ]
    monitor = TelemetryMonitor(window_size=15)
    engine = DecisionEngine()
    
    history = {"Region-A": [], "Region-B": []}
    steps = list(range(100))

    for i in steps:
        if i == 50: # Trigger failure at midpoint
            backends[0].failure_rate = 0.9
            
        best = engine.select_best_backend(backends)
        res = simulate_request(best)
        monitor.update_backend_stats(best, res.latency_ms, res.success)
        
        # Log scores for graphing
        history["Region-A"].append(engine.calculate_score(backends[0]))
        history["Region-B"].append(engine.calculate_score(backends[1]))

    # Plotting
    plt.figure(figsize=(10, 6))
    plt.plot(steps, history["Region-A"], label="Region-A Score (Fast but Fails)")
    plt.plot(steps, history["Region-B"], label="Region-B Score (Stable)")
    plt.axvline(x=50, color='r', linestyle='--', label="Failure Injected")
    plt.title("DTDE Dynamic Traffic Shifting")
    plt.xlabel("Request Step")
    plt.ylabel("Composite Score (Si)")
    plt.legend()
    plt.grid(True)
    plt.savefig("simulation_results.png")
    print("Graph saved as simulation_results.png")

if __name__ == "__main__":
    run_visual_sim()
