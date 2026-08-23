"""Evaluate last week's promised change using only explicit evidence."""
from __future__ import annotations

from typing import Any

from .contracts import agent_result
from .pipeline import METRIC_FIELDS


METRIC_ALIASES = {
    "売上": "monthly_sales_actual", "受注": "orders", "新規アプローチ": "new_approaches",
    "休眠アプローチ": "dormant_approaches", "商談": "appointments_or_meetings",
    "訪問": "visits", "提案": "proposals", "見積": "estimates",
}


def _resolve_metric(text: str) -> str | None:
    if text in METRIC_FIELDS:
        return text
    for label, field in METRIC_ALIASES.items():
        if label in text:
            return field
    return None


def audit_action_change(current: dict[str, Any], previous_report: dict[str, Any] | None = None) -> dict[str, Any]:
    action = current["previous_action_change"]
    if not action["executed"]:
        verdict, evidence, gaps, confidence = "not_executed", [{"executed": False}], [], 1.0
    else:
        metric = _resolve_metric(action.get("verification_metric", ""))
        observed = action.get("observed_result", "").strip()
        if previous_report and metric:
            before = previous_report["results"][metric]
            after = current["results"][metric]
            verdict = "effective" if after > before else "ineffective"
            evidence = [{"metric": metric, "before": before, "after": after, "delta": after - before}]
            gaps, confidence = [], 1.0
        elif observed and any(token in observed for token in ("変化なし", "増減なし", "0件", "効果なし")):
            verdict, evidence, gaps, confidence = "ineffective", [{"observed_result": observed}], [], 0.9
        elif observed:
            verdict, evidence, gaps, confidence = "unknown", [{"observed_result": observed}], ["numeric_before_after"], 0.6
        else:
            verdict, evidence, gaps, confidence = "unknown", [{"executed": True}], ["observed_result"], 1.0
    status = "ok" if verdict == "effective" else ("insufficient_data" if verdict == "unknown" else "warning")
    return agent_result("Action Change Auditor", status,
                        findings=[{"verdict": verdict, "promise": action.get("promise", "")}],
                        evidence=evidence, risks=[] if verdict == "effective" else [f"前週行動判定: {verdict}"],
                        confidence=confidence, data_gaps=gaps, verdict=verdict)

