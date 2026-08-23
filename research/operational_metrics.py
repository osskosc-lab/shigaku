"""Translate weekly operational records to P4 research variables."""
from __future__ import annotations

from typing import Any


def _present(value: Any) -> int:
    return int(value is not None and (not isinstance(value, str) or bool(value.strip())))


def translate_report(report: dict[str, Any], *, input_minutes: float | None = None,
                     manager_review_minutes: float | None = None,
                     authority_confirmed: bool | None = None,
                     submitted_on_time: bool | None = None) -> dict[str, Any]:
    n = report["next_action_change"]
    clarity_fields = [n.get("deadline"), n.get("owner"), n.get("completion_condition"),
                      n.get("verification_metric"), report["employee"].get("manager")]
    previous = report["previous_action_change"]
    return {
        "data_source": "operational",
        "clarity": sum(map(_present, clarity_fields)) / len(clarity_fields),
        "authority": None if authority_confirmed is None else float(authority_confirmed),
        "cadence": None if submitted_on_time is None else float(submitted_on_time),
        "change": {"executed": float(previous["executed"]),
                   "effect_verified": float(bool(previous.get("observed_result")))},
        "pressure": None,
        "admin": {"employee_input_minutes": input_minutes,
                  "manager_review_minutes": manager_review_minutes},
        "data_gaps": [name for name, value in {
            "authority_confirmed": authority_confirmed, "submitted_on_time": submitted_on_time,
            "input_minutes": input_minutes, "manager_review_minutes": manager_review_minutes,
            "pressure_event_density": None,
        }.items() if value is None],
    }

