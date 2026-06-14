import numpy as np

class TelemetryMonitor:
    def __init__(self, window_size=20):
        self.window_size = window_size

    def update_backend_stats(self, backend, latency_ms, success):
        # Update history
        backend.latency_history.append(latency_ms)
        backend.success_history.append(1.0 if success else 0.0)
        
        # Keep window size
        if len(backend.latency_history) > self.window_size:
            backend.latency_history.pop(0)
            backend.success_history.pop(0)
            
        # Calculate P95 Latency
        if backend.latency_history:
            backend.latency_obs_ms = float(np.percentile(backend.latency_history, 95))
        
        # Calculate Health Score (Success Rate)
        if backend.success_history:
            backend.health_score = float(np.mean(backend.success_history))

def update_telemetry(backend, latency_ms, success):
    """Global helper function used by simulation and tests"""
    monitor = TelemetryMonitor()
    monitor.update_backend_stats(backend, latency_ms, success)
