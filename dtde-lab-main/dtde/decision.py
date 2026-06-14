from .models import BackendState, RequestResult
from typing import List

class DecisionEngine:
    def __init__(self, w_health=0.4, w_latency=0.4, w_security=0.2):
        self.w_h = w_health
        self.w_l = w_latency
        self.w_s = w_security

    def calculate_score(self, backend: BackendState) -> float:
        if not backend.security_ok or not backend.policy_ok:
            return 0.0
        
        # S = (w_h * H) + (w_l * 1/L)
        # Using 1000ms as a baseline for latency normalization
        latency_factor = 1.0 / (backend.latency_obs_ms / 100.0 + 1.0)
        score = (self.w_h * backend.health_score) + (self.w_l * latency_factor)
        return round(score, 3)

    def select_best_backend(self, backends: List[BackendState]) -> BackendState:
        return max(backends, key=self.calculate_score)

# Alias for Academic Verification Scripts
class DTDEPolicy(DecisionEngine):
    def score_backend(self, backend, all_backends):
        return self.calculate_score(backend)
    
    def choose_backend(self, backends):
        return self.select_best_backend(backends)
