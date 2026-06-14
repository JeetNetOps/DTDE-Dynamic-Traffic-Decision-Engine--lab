import time
import numpy as np
from dtde.models import BackendState, RequestResult
from dtde.telemetry import TelemetryMonitor
from dtde.decision import DecisionEngine

def run_controlled_experiment():
    print("=== DTDE ACADEMIC REPRODUCIBILITY SUITE ===")
    backends = [
        BackendState(id="Primary-Node", base_latency_ms=40.0, failure_rate=0.01),
        BackendState(id="Secondary-Node", base_latency_ms=120.0, failure_rate=0.01),
    ]
    monitor = TelemetryMonitor(window_size=10)
    engine = DecisionEngine()
    
    # Metrics tracking
    detections = []
    
    for t in range(1, 61):
        if t == 30:
            print(f"[T={t}] SIMULATING FAULT: Injecting 90% failure rate into Primary-Node")
            backends[0].failure_rate = 0.9
        
        selected = engine.select_best_backend(backends)
        
        # Simulate result
        success = np.random.random() > selected.failure_rate
        latency = selected.base_latency_ms if success else 1000.0
        res = RequestResult(backend_id=selected.id, latency_ms=latency, success=success, ts=t)
        
        monitor.update_backend(selected, res)
        
        if t >= 30 and selected.id == "Secondary-Node" and not detections:
            detections.append(t)
            print(f"[T={t}] DETECTION: Engine successfully pivoted to Secondary-Node")

    print("\n=== EXPERIMENT SUMMARY ===")
    print(f"Fault Injected at: T=30")
    print(f"First Pivot at:    T={detections[0] if detections else 'N/A'}")
    print(f"Detection Latency: {detections[0]-30 if detections else 'Fail'} requests")
    print("==========================")

if __name__ == "__main__":
    run_controlled_experiment()
