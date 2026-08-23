"""Command-line entrypoint for JSON weekly reports."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from app.dashboard.manager_view import aggregate_manager_view, export_manager_csv, export_manager_html
from app.io import load_report_file
from app.services.manager import process_weekly_report


def main() -> int:
    parser = argparse.ArgumentParser(description="Marukane Sales Weekly Agency")
    parser.add_argument("reports", nargs="+", help="週報JSON（複数可）")
    parser.add_argument("--previous", help="前週週報JSON（1名処理時のみ）")
    parser.add_argument("--output", default="data/archive/weekly_meeting_output.json")
    parser.add_argument("--manager-csv", default="data/archive/manager_view.csv")
    parser.add_argument("--manager-html", default="data/archive/manager_dashboard.html")
    args = parser.parse_args()
    previous = load_report_file(args.previous)[0] if args.previous else None
    reports = [report for path in args.reports for report in load_report_file(path)]
    processed = [process_weekly_report(report, previous if len(reports) == 1 else None)
                 for report in reports]
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(processed, ensure_ascii=False, indent=2), encoding="utf-8")
    rows = aggregate_manager_view(processed)
    export_manager_csv(rows, args.manager_csv)
    export_manager_html(rows, args.manager_html)
    print(f"processed={len(processed)} output={output} manager_csv={args.manager_csv} manager_html={args.manager_html}")
    return 0 if all(x["status"] != "error" for x in processed) else 1


if __name__ == "__main__":
    raise SystemExit(main())
