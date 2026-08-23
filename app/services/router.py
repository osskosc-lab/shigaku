"""Route only observable risks to conditional specialists."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .contracts import agent_result


def route_decisions(report: dict[str, Any], pipeline: dict[str, Any], action: dict[str, Any],
                    now: datetime | None = None) -> dict[str, Any]:
    now = now or datetime.now(timezone.utc)
    metrics, results = pipeline["metrics"], report["results"]
    routes: list[dict[str, str]] = []
    alerts: list[str] = []
    achievement = metrics["sales_achievement_rate"]
    if achievement is not None and achievement < 0.8:
        alerts.append("売上進捗危険")
    if metrics["total_approaches"] == 0:
        alerts.append("アプローチ不足")
        routes.append({"agent": "Outbound Strategist", "reason": "新規・休眠アプローチが0件"})
    if metrics["approach_to_visit_rate"] is not None and metrics["approach_to_visit_rate"] < 0.2:
        alerts.append("訪問化率低下")
        routes.append({"agent": "Outbound Strategist", "reason": "訪問化率20%未満"})
    if metrics["visit_to_proposal_rate"] is not None and metrics["visit_to_proposal_rate"] < 0.3:
        alerts.append("提案化率低下")
        routes.append({"agent": "Deal Strategist", "reason": "提案化率30%未満"})
    if metrics["proposal_to_estimate_rate"] is not None and metrics["proposal_to_estimate_rate"] < 0.4:
        alerts.append("見積化率低下")
        routes.append({"agent": "Deal Strategist", "reason": "見積化率40%未満"})
    if action["verdict"] == "ineffective":
        alerts.append("行動変更を実施したが効果なし")
    if report["manager_decision"]["required"]:
        alerts.append("上司判断待ち")
        routes.append({"agent": "Manager", "reason": report["manager_decision"]["subject"]})
    deadline = datetime.fromisoformat(report["next_action_change"]["deadline"])
    comparison_now = now if deadline.tzinfo else now.replace(tzinfo=None)
    if deadline < comparison_now:
        alerts.append("期限超過")
    if results["proposals"] > 0 and results["estimates"] == 0:
        routes.append({"agent": "Deal Strategist", "reason": "提案あり・見積0件"})
    # Stable de-duplication keeps identical inputs reproducible.
    routes = list({(x["agent"], x["reason"]): x for x in routes}.values())
    alerts = list(dict.fromkeys(alerts))
    return agent_result("Decision Router", "warning" if alerts else "ok",
                        findings=routes, evidence=[{"alerts": alerts}], risks=alerts,
                        confidence=1.0, routes=routes, alerts=alerts)

