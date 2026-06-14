from dataclasses import dataclass, field
from typing import List

@dataclass
class BackendState:
    """
    Represents a single backend (pool member / region / cluster) in the DTDE lab.
    This includes both static characteristics (base latency, failure rate) and
    dynamic telemetry-derived fields (health_score, latency_obs_ms, etc.).
    """
    id: str
    base_latency_ms: float
    failure_rate: float  # probability that a request to this backend fails

    # Policy and security flags
    security_ok: bool = True
    policy_ok: bool = True

    # Telemetry-derived scores (0-1 where applicable)
    health_score: float = 1.0
    latency_obs_ms: float = 0.0
    security_score: float = 1.0
    policy_score: float = 1.0

    # Sliding window histories for telemetry
    latency_history: List[float] = field(default_factory=list)
    success_history: List[bool] = field(default_factory=list)

@dataclass
class RequestResult:
    """
    Captures the outcome of routing a single synthetic request in the simulation.
    """
    backend_id: str
    latency_ms: float
    success: bool
    ts: int  # simulation timestamp / step index
