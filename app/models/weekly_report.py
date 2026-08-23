"""Typed, immutable view of one weekly report.

Validation is deliberately performed before construction.  This model never
fills missing business data; callers must preserve gaps as explicit findings.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Any


@dataclass(frozen=True)
class Employee:
    employee_id: str
    name: str
    manager: str
    period_start: date
    period_end: date


@dataclass(frozen=True)
class Results:
    monthly_sales_target: float
    monthly_sales_actual: float
    orders: int
    new_approaches: int
    dormant_approaches: int
    appointments_or_meetings: int
    visits: int
    proposals: int
    estimates: int


@dataclass(frozen=True)
class PreviousActionChange:
    promise: str
    deadline: datetime
    completion_condition: str
    verification_metric: str
    executed: bool
    observed_result: str


@dataclass(frozen=True)
class NextActionChange:
    action: str
    owner: str
    deadline: datetime
    completion_condition: str
    verification_metric: str


@dataclass(frozen=True)
class ManagerDecision:
    required: bool
    subject: str
    decision_deadline: datetime | None


@dataclass(frozen=True)
class WeeklyReport:
    employee: Employee
    results: Results
    previous_action_change: PreviousActionChange
    next_action_change: NextActionChange
    manager_decision: ManagerDecision
    shared_information: str
    other_notes: str
    operational_metadata: dict[str, Any] | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "WeeklyReport":
        e, r = data["employee"], data["results"]
        p, n, m = data["previous_action_change"], data["next_action_change"], data["manager_decision"]
        return cls(
            employee=Employee(
                employee_id=e["employee_id"], name=e["name"], manager=e["manager"],
                period_start=date.fromisoformat(e["period_start"]),
                period_end=date.fromisoformat(e["period_end"]),
            ),
            results=Results(**r),
            previous_action_change=PreviousActionChange(
                **{**p, "deadline": datetime.fromisoformat(p["deadline"])}
            ),
            next_action_change=NextActionChange(
                **{**n, "deadline": datetime.fromisoformat(n["deadline"])}
            ),
            manager_decision=ManagerDecision(
                required=m["required"], subject=m["subject"],
                decision_deadline=(datetime.fromisoformat(m["decision_deadline"])
                                   if m.get("decision_deadline") else None),
            ),
            shared_information=data.get("shared_information", ""),
            other_notes=data.get("other_notes", ""),
            operational_metadata=data.get("operational_metadata"),
        )
