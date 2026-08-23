"""Compact employee/manager views and CSV export."""
from __future__ import annotations

import csv
import html
from pathlib import Path
from typing import Any


def aggregate_manager_view(processed: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in processed:
        if item["status"] == "error":
            rows.append({"employee_id": None, "status": "error", "data_gaps": ";".join(item["data_gaps"])})
            continue
        s, p, a = item["meeting_summary"], item["pipeline"], item["action_change"]
        r = p["evidence"][0]["current"]
        rows.append({
            "employee_id": s["employee_id"], "name": s["name"],
            "sales_achievement_rate": p["metrics"]["sales_achievement_rate"],
            "new_approaches": r["new_approaches"], "dormant_approaches": r["dormant_approaches"],
            "visits": r["visits"], "proposals": r["proposals"], "estimates": r["estimates"],
            "approach_to_visit_rate": p["metrics"]["approach_to_visit_rate"],
            "visit_to_proposal_rate": p["metrics"]["visit_to_proposal_rate"],
            "proposal_to_estimate_rate": p["metrics"]["proposal_to_estimate_rate"],
            "previous_action_verdict": a["verdict"], "next_action_deadline": s["期限"],
            "manager_decision_required": s["上司判断事項"] is not None,
            "input_minutes": s["operational_metadata"].get("input_minutes"),
            "manager_review_minutes": s["operational_metadata"].get("manager_review_minutes"),
            "alerts": ";".join(s["alerts"]), "data_gaps": ";".join(item["data_gaps"]),
        })
    return rows


def export_manager_csv(rows: list[dict[str, Any]], output: str | Path) -> Path:
    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0]) if rows else ["employee_id", "status"]
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    return path


def export_manager_html(rows: list[dict[str, Any]], output: str | Path) -> Path:
    """Create a dependency-free manager dashboard for local weekly use."""
    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0]) if rows else ["employee_id", "status"]
    header = "".join(f"<th>{html.escape(str(field))}</th>" for field in fields)
    body = "".join("<tr>" + "".join(
        f"<td>{html.escape('' if row.get(field) is None else str(row.get(field)))}</td>" for field in fields
    ) + "</tr>" for row in rows)
    document = f"""<!doctype html><html lang=\"ja\"><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width\">
<title>Marukane Sales Weekly Dashboard</title><style>
body{{font-family:system-ui,sans-serif;margin:24px;color:#172033;background:#f4f7fb}}h1{{font-size:1.4rem}}p{{color:#536078}}
.table{{overflow:auto;background:white;border:1px solid #dbe3ef;border-radius:10px}}table{{border-collapse:collapse;min-width:1200px;width:100%}}
th,td{{padding:10px;border-bottom:1px solid #e5eaf1;text-align:left;white-space:nowrap}}th{{background:#173f68;color:white;position:sticky;top:0}}
</style><h1>マルカネ営業部 週報ダッシュボード</h1><p>会議: 毎週月曜日 朝礼終了後 8:45／事実・差分・期限を表示</p>
<div class=\"table\"><table><thead><tr>{header}</tr></thead><tbody>{body}</tbody></table></div></html>"""
    path.write_text(document, encoding="utf-8")
    return path
