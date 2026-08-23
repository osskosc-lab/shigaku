"""Report validation without silent imputation."""
from __future__ import annotations

from datetime import date, datetime
from typing import Any

from .contracts import agent_result


REQUIRED = {
    "employee": ("employee_id", "name", "manager", "period_start", "period_end"),
    "results": ("monthly_sales_target", "monthly_sales_actual", "orders", "new_approaches",
                "dormant_approaches", "appointments_or_meetings", "visits", "proposals", "estimates"),
    "previous_action_change": ("promise", "deadline", "completion_condition", "verification_metric",
                               "executed", "observed_result"),
    "next_action_change": ("action", "owner", "deadline", "completion_condition", "verification_metric"),
    "manager_decision": ("required", "subject", "decision_deadline"),
}
COUNT_FIELDS = ("orders", "new_approaches", "dormant_approaches", "appointments_or_meetings",
                "visits", "proposals", "estimates")


def _parse_iso(value: Any, parser: type[date] | type[datetime]) -> bool:
    try:
        parser.fromisoformat(value)
        return True
    except (TypeError, ValueError):
        return False


def validate_report(data: Any) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []
    gaps: list[str] = []
    if not isinstance(data, dict):
        return agent_result("Report Validator", "error", findings=[],
                            risks=["週報を処理できません"], data_gaps=["report"],
                            confidence=1.0, valid=False,
                            errors=[{"path": "$", "message": "object型が必要です"}], warnings=[])

    for section, fields in REQUIRED.items():
        block = data.get(section)
        if not isinstance(block, dict):
            errors.append({"path": section, "message": "object型の必須セクションです"})
            gaps.append(section)
            continue
        for field in fields:
            nullable_optional_value = section == "manager_decision" and field == "decision_deadline"
            if field not in block or (block[field] is None and not nullable_optional_value):
                errors.append({"path": f"{section}.{field}", "message": "必須項目です"})
                gaps.append(f"{section}.{field}")

    results = data.get("results", {}) if isinstance(data.get("results"), dict) else {}
    for field in ("monthly_sales_target", "monthly_sales_actual", *COUNT_FIELDS):
        value = results.get(field)
        if value is None:
            continue
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            errors.append({"path": f"results.{field}", "message": "数値が必要です"})
        elif value < 0:
            errors.append({"path": f"results.{field}", "message": "0以上が必要です"})
        elif field in COUNT_FIELDS and not isinstance(value, int):
            errors.append({"path": f"results.{field}", "message": "整数が必要です"})
        elif field in COUNT_FIELDS and value > 100000:
            warnings.append({"path": f"results.{field}", "message": "通常範囲を超えるため確認してください"})

    employee = data.get("employee", {}) if isinstance(data.get("employee"), dict) else {}
    if employee.get("period_start") is not None and not _parse_iso(employee["period_start"], date):
        errors.append({"path": "employee.period_start", "message": "ISO日付が必要です"})
    if employee.get("period_end") is not None and not _parse_iso(employee["period_end"], date):
        errors.append({"path": "employee.period_end", "message": "ISO日付が必要です"})
    if _parse_iso(employee.get("period_start"), date) and _parse_iso(employee.get("period_end"), date):
        if date.fromisoformat(employee["period_start"]) > date.fromisoformat(employee["period_end"]):
            errors.append({"path": "employee.period_end", "message": "開始日以後である必要があります"})

    previous = data.get("previous_action_change", {}) if isinstance(data.get("previous_action_change"), dict) else {}
    next_action = data.get("next_action_change", {}) if isinstance(data.get("next_action_change"), dict) else {}
    decision = data.get("manager_decision", {}) if isinstance(data.get("manager_decision"), dict) else {}
    for path, value in (("previous_action_change.deadline", previous.get("deadline")),
                        ("next_action_change.deadline", next_action.get("deadline"))):
        if value is not None and not _parse_iso(value, datetime):
            errors.append({"path": path, "message": "ISO日時が必要です"})
    if previous.get("completed_at") is not None and not _parse_iso(previous["completed_at"], datetime):
        errors.append({"path": "previous_action_change.completed_at", "message": "ISO日時またはnullが必要です"})
    if not isinstance(previous.get("executed"), bool) and "executed" in previous:
        errors.append({"path": "previous_action_change.executed", "message": "boolean型が必要です"})
    if not isinstance(decision.get("required"), bool) and "required" in decision:
        errors.append({"path": "manager_decision.required", "message": "boolean型が必要です"})
    if decision.get("required"):
        for field in ("subject", "decision_deadline"):
            if not decision.get(field):
                errors.append({"path": f"manager_decision.{field}", "message": "判断依頼時は必須です"})
                gaps.append(f"manager_decision.{field}")
        if decision.get("decision_deadline") and not _parse_iso(decision["decision_deadline"], datetime):
            errors.append({"path": "manager_decision.decision_deadline", "message": "ISO日時が必要です"})
    for field in ("action", "owner", "deadline", "completion_condition", "verification_metric"):
        if not next_action.get(field):
            errors.append({"path": f"next_action_change.{field}", "message": "次行動では空欄にできません"})
            gaps.append(f"next_action_change.{field}")
    for section, block in (("employee", employee), ("previous_action_change", previous),
                           ("next_action_change", next_action)):
        for field, value in block.items():
            if isinstance(value, str) and not value.strip() and f"{section}.{field}" not in gaps:
                warnings.append({"path": f"{section}.{field}", "message": "空文字です"})

    valid = not errors
    status = "ok" if valid and not warnings else ("warning" if valid else "error")
    return agent_result("Report Validator", status,
                        findings=["入力検証に合格"] if valid else [f"入力エラー{len(errors)}件"],
                        evidence=[{"error_count": len(errors), "warning_count": len(warnings)}],
                        risks=[x["message"] for x in errors], confidence=1.0,
                        data_gaps=sorted(set(gaps)), valid=valid, errors=errors, warnings=warnings)
