"""Rule-based conditional specialists; never used as final evaluators."""
from __future__ import annotations

from typing import Any

from .contracts import agent_result


def outbound_strategy(report: dict[str, Any], reason: str) -> dict[str, Any]:
    action = report["next_action_change"]
    recommendation = {
        "action": action["action"],
        "owner": action["owner"],
        "deadline": action["deadline"],
        "completion_condition": action["completion_condition"],
        "verification_metric": action["verification_metric"],
        "focus": "新規・休眠先を分け、対象件数と接触完了を記録する",
    }
    return agent_result("Outbound Strategist", "warning", findings=[{"trigger": reason}],
                        evidence=[{"new_approaches": report["results"]["new_approaches"],
                                   "dormant_approaches": report["results"]["dormant_approaches"]}],
                        recommended_actions=[recommendation], confidence=1.0)


def deal_strategy(report: dict[str, Any], reason: str) -> dict[str, Any]:
    action = report["next_action_change"]
    recommendation = {
        "action": action["action"],
        "owner": action["owner"],
        "deadline": action["deadline"],
        "completion_condition": action["completion_condition"],
        "verification_metric": action["verification_metric"],
        "focus": "停滞案件ごとに相手の次回答日と自社の次接触日を確定する",
    }
    return agent_result("Deal Strategist", "warning", findings=[{"trigger": reason}],
                        evidence=[{"proposals": report["results"]["proposals"],
                                   "estimates": report["results"]["estimates"],
                                   "orders": report["results"]["orders"]}],
                        recommended_actions=[recommendation], confidence=1.0)


def sales_coaching(report: dict[str, Any]) -> dict[str, Any]:
    action = report["next_action_change"]
    return agent_result("Sales Coach", "ok",
                        findings=[{"support_scope": "決定済み行動の実行支援のみ"}],
                        evidence=[{"decided_action": action}],
                        recommended_actions=[{
                            "action": f"『{action['completion_condition']}』を満たす作業手順を実行前に3段階へ分解する",
                            "owner": action["owner"], "deadline": action["deadline"],
                            "completion_condition": "3段階の手順が記録され、実行開始できる",
                            "verification_metric": action["verification_metric"],
                        }], confidence=0.9)

