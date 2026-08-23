"""Shared structured agent-result contract."""
from __future__ import annotations

from typing import Any


def agent_result(agent: str, status: str = "ok", *, findings: list | None = None,
                 evidence: list | None = None, risks: list | None = None,
                 recommended_actions: list | None = None, confidence: float = 1.0,
                 data_gaps: list | None = None, **extra: Any) -> dict[str, Any]:
    result = {
        "agent": agent,
        "status": status,
        "findings": findings or [],
        "evidence": evidence or [],
        "risks": risks or [],
        "recommended_actions": recommended_actions or [],
        "confidence": max(0.0, min(float(confidence), 1.0)),
        "data_gaps": data_gaps or [],
    }
    result.update(extra)
    return result

