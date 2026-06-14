from typing import List
import numpy as np

from .models import RequestResult


def compute_metrics(results: List[RequestResult]) -> dict:
    """
    Compute basic performance metrics from a list of RequestResult:
    - mean response time (successful requests)
    - P95 latency (successful requests)
    - availability (success ratio)
    - MTTR-like metric: mean length of consecutive failure streaks
    """
    if not results:
        return {
            "mean_response_time_ms": float("inf"),
            "p95_latency_ms": float("inf"),
            "availability": 0.0,
            "mttr_steps": 0.0,
        }

    latencies = [r.latency_ms for r in results if r.success]
    successes = [r for r in results if r.success]

    if latencies:
        mean_rt = float(np.mean(latencies))
        p95 = float(np.percentile(latencies, 95))
    else:
        mean_rt = float("inf")
        p95 = float("inf")

    availability = len(successes) / len(results)

    # Simple MTTR proxy: mean length of consecutive failure streaks
    down_streaks = []
    current = 0
    for r in results:
        if not r.success:
            current += 1
        elif current > 0:
            down_streaks.append(current)
            current = 0
    if current > 0:
        down_streaks.append(current)

    mttr_steps = float(np.mean(down_streaks)) if down_streaks else 0.0

    return {
        "mean_response_time_ms": mean_rt,
        "p95_latency_ms": p95,
        "availability": availability,
        "mttr_steps": mttr_steps,
    }
