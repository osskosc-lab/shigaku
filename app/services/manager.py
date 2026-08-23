"""Weekly Report Manager orchestration and compressed meeting output."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from .action_auditor import audit_action_change
from .contracts import agent_result
from .pipeline import analyze_pipeline
from .router import route_decisions
from .specialists import deal_strategy, outbound_strategy
from .validator import validate_report


def build_meeting_summary(report: dict[str, Any], pipeline: dict[str, Any],
                          action: dict[str, Any], router: dict[str, Any]) -> dict[str, Any]:
    r, n, d = report["results"], report["next_action_change"], report["manager_decision"]
    return {
        "meeting_timing": "毎週月曜日 朝礼終了後 8:45",
        "employee_id": report["employee"]["employee_id"],
        "name": report["employee"]["name"],
        "period": {"start": report["employee"]["period_start"], "end": report["employee"]["period_end"]},
        "期限時の結果": {"monthly_sales_actual": r["monthly_sales_actual"], "orders": r["orders"]},
        "目標との差": (r["monthly_sales_actual"] - r["monthly_sales_target"]),
        "前週に約束した行動変化": report["previous_action_change"]["promise"],
        "行動変化の実行有無": report["previous_action_change"]["executed"],
        "数字または外部反応の変化": {
            "verdict": action["verdict"], "evidence": action["evidence"],
        },
        "今週変える行動": n["action"],
        "結果責任者": n["owner"],
        "期限": n["deadline"],
        "完了状態": n["completion_condition"],
        "検証指標": n["verification_metric"],
        "上司判断事項": d if d["required"] else None,
        "alerts": router["alerts"],
        "kpi": pipeline["metrics"],
        "operational_metadata": report.get("operational_metadata", {}),
    }


def process_weekly_report(report: dict[str, Any], previous_report: dict[str, Any] | None = None,
                          now: datetime | None = None) -> dict[str, Any]:
    validation = validate_report(report)
    if not validation["valid"]:
        return agent_result("Weekly Report Manager", "error",
                            findings=[{"processing": "stopped_before_analysis"}],
                            evidence=[validation], risks=validation["risks"],
                            confidence=1.0, data_gaps=validation["data_gaps"],
                            validation=validation, agent_results=[validation])
    previous_valid = None
    previous_gap: list[str] = []
    if previous_report is not None:
        prior_validation = validate_report(previous_report)
        if prior_validation["valid"]:
            previous_valid = previous_report
        else:
            previous_gap = ["valid_previous_week_report"]
    pipeline = analyze_pipeline(report, previous_valid)
    action = audit_action_change(report, previous_valid)
    router = route_decisions(report, pipeline, action, now=now)
    specialists: list[dict[str, Any]] = []
    for route in router["routes"]:
        if route["agent"] == "Outbound Strategist":
            specialists.append(outbound_strategy(report, route["reason"]))
        elif route["agent"] == "Deal Strategist":
            specialists.append(deal_strategy(report, route["reason"]))
    summary = build_meeting_summary(report, pipeline, action, router)
    all_results = [validation, pipeline, action, router, *specialists]
    gaps = sorted(set(previous_gap + [g for result in all_results for g in result["data_gaps"]]))
    return agent_result("Weekly Report Manager", "warning" if router["alerts"] or gaps else "ok",
                        findings=[{"meeting_summary_ready": True}], evidence=[summary],
                        risks=router["alerts"], confidence=min(x["confidence"] for x in all_results),
                        data_gaps=gaps, validation=validation, pipeline=pipeline,
                        action_change=action, routing=router, specialists=specialists,
                        meeting_summary=summary, agent_results=all_results)
