"""Flat CSV interchange for weekly reports.

Nested JSON keys are represented with dots, for example
``results.monthly_sales_actual`` and ``next_action_change.deadline``.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


NUMBER_FIELDS = {"monthly_sales_target", "monthly_sales_actual", "input_minutes", "manager_review_minutes"}
INTEGER_FIELDS = {"orders", "new_approaches", "dormant_approaches", "appointments_or_meetings",
                  "visits", "proposals", "estimates"}
BOOLEAN_FIELDS = {"executed", "required", "authority_confirmed"}
NULLABLE_FIELDS = {"decision_deadline", "completed_at", "reviewed_at", "submitted_at",
                   "input_minutes", "manager_review_minutes", "authority_confirmed"}


def flatten(data: dict[str, Any], prefix: str = "") -> dict[str, Any]:
    output: dict[str, Any] = {}
    for key, value in data.items():
        path = f"{prefix}.{key}" if prefix else key
        if isinstance(value, dict):
            output.update(flatten(value, path))
        else:
            output[path] = value
    return output


def _coerce(path: str, value: str) -> Any:
    field = path.rsplit(".", 1)[-1]
    if value == "" and field in NULLABLE_FIELDS:
        return None
    if field in BOOLEAN_FIELDS:
        lowered = value.lower()
        if lowered in {"true", "1", "yes"}:
            return True
        if lowered in {"false", "0", "no"}:
            return False
        return value
    if field in INTEGER_FIELDS:
        try:
            return int(value)
        except ValueError:
            return value
    if field in NUMBER_FIELDS:
        try:
            return float(value)
        except ValueError:
            return value
    return value


def unflatten(row: dict[str, str]) -> dict[str, Any]:
    output: dict[str, Any] = {}
    for path, raw in row.items():
        target = output
        parts = path.split(".")
        for part in parts[:-1]:
            target = target.setdefault(part, {})
        target[parts[-1]] = _coerce(path, raw)
    return output


def read_weekly_csv(path: str | Path) -> list[dict[str, Any]]:
    with Path(path).open(newline="", encoding="utf-8-sig") as handle:
        return [unflatten(dict(row)) for row in csv.DictReader(handle)]


def export_weekly_csv(reports: list[dict[str, Any]], path: str | Path) -> Path:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    rows = [flatten(report) for report in reports]
    fields = list(dict.fromkeys(key for row in rows for key in row))
    with destination.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    return destination


def load_report_file(path: str | Path) -> list[dict[str, Any]]:
    source = Path(path)
    if source.suffix.lower() == ".csv":
        return read_weekly_csv(source)
    data = json.loads(source.read_text(encoding="utf-8"))
    return data if isinstance(data, list) else [data]

