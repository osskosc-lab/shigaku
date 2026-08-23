"""KPI calculation and factual week-over-week comparisons."""
from __future__ import annotations

from typing import Any

from .contracts import agent_result


METRIC_FIELDS = ("monthly_sales_actual", "orders", "new_approaches", "dormant_approaches",
                 "appointments_or_meetings", "visits", "proposals", "estimates")


def safe_rate(numerator: float, denominator: float) -> float | None:
    return numerator / denominator if denominator else None


def analyze_pipeline(current: dict[str, Any], previous: dict[str, Any] | None = None) -> dict[str, Any]:
    r = current["results"]
    action = current["previous_action_change"]
    total = r["new_approaches"] + r["dormant_approaches"]
    completed_at = action.get("completed_at")
    deadline_completion = None
    if completed_at:
        from datetime import datetime
        deadline_completion = float(datetime.fromisoformat(completed_at) <= datetime.fromisoformat(action["deadline"]))
    metrics = {
        "sales_achievement_rate": safe_rate(r["monthly_sales_actual"], r["monthly_sales_target"]),
        "total_approaches": total,
        "approach_to_visit_rate": safe_rate(r["visits"], total),
        "visit_to_proposal_rate": safe_rate(r["proposals"], r["visits"]),
        "proposal_to_estimate_rate": safe_rate(r["estimates"], r["proposals"]),
        "action_execution_rate": float(action["executed"]),
        "deadline_completion_rate": deadline_completion,
    }
    gaps = [name for name, value in metrics.items() if value is None]
    deltas: dict[str, float] = {}
    if previous:
        pr = previous["results"]
        deltas = {field: r[field] - pr[field] for field in METRIC_FIELDS}
        deltas["total_approaches"] = total - (pr["new_approaches"] + pr["dormant_approaches"])
    else:
        gaps.append("previous_week_report")
    findings = [{"metric": k, "value": v} for k, v in metrics.items() if v is not None]
    status = "insufficient_data" if not previous else ("warning" if gaps else "ok")
    return agent_result("Pipeline Analyst", status, findings=findings,
                        evidence=[{"current": r}, {"week_over_week_deltas": deltas}] if previous else [{"current": r}],
                        confidence=1.0 if previous else 0.75, data_gaps=gaps,
                        metrics=metrics, deltas=deltas)
