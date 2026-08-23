from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from app.dashboard.manager_view import aggregate_manager_view, export_manager_csv
from app.io import export_weekly_csv, read_weekly_csv
from app.services.action_auditor import audit_action_change
from app.services.manager import process_weekly_report
from app.services.pipeline import analyze_pipeline, safe_rate
from app.services.validator import validate_report
from research.operational_metrics import translate_report


ROOT = Path(__file__).resolve().parents[1]


def sample(name: str = "sample_current.json") -> dict:
    return json.loads((ROOT / "data" / "weekly" / name).read_text(encoding="utf-8"))


class WeeklyAgencyTests(unittest.TestCase):
    def setUp(self):
        self.current = sample()
        self.previous = sample("sample_previous.json")
        self.now = datetime(2026, 8, 23, tzinfo=timezone.utc)

    def test_01_normal_report(self):
        self.assertTrue(validate_report(self.current)["valid"])

    def test_02_zero_sales_target_is_safe(self):
        self.current["results"]["monthly_sales_target"] = 0
        self.assertIsNone(analyze_pipeline(self.current)["metrics"]["sales_achievement_rate"])

    def test_03_zero_visits_is_safe(self):
        self.current["results"]["visits"] = 0
        self.assertIsNone(analyze_pipeline(self.current)["metrics"]["visit_to_proposal_rate"])

    def test_04_zero_proposals_is_safe(self):
        self.current["results"]["proposals"] = 0
        self.assertIsNone(analyze_pipeline(self.current)["metrics"]["proposal_to_estimate_rate"])

    def test_05_missing_deadline_rejected(self):
        self.current["next_action_change"]["deadline"] = ""
        self.assertFalse(validate_report(self.current)["valid"])

    def test_06_missing_owner_rejected(self):
        self.current["next_action_change"]["owner"] = ""
        self.assertFalse(validate_report(self.current)["valid"])

    def test_07_not_executed_verdict(self):
        self.current["previous_action_change"]["executed"] = False
        self.assertEqual(audit_action_change(self.current, self.previous)["verdict"], "not_executed")

    def test_08_executed_no_change_is_ineffective(self):
        self.current["results"]["new_approaches"] = self.previous["results"]["new_approaches"]
        self.assertEqual(audit_action_change(self.current, self.previous)["verdict"], "ineffective")

    def test_09_manager_decision_routed(self):
        result = process_weekly_report(self.current, self.previous, now=self.now)
        self.assertIn("上司判断待ち", result["routing"]["alerts"])

    def test_10_many_missing_values_are_data_gaps(self):
        broken = {"employee": {}}
        result = validate_report(broken)
        self.assertFalse(result["valid"])
        self.assertGreater(len(result["data_gaps"]), 5)

    def test_11_abnormally_large_value_warns(self):
        self.current["results"]["visits"] = 100001
        self.assertEqual(validate_report(self.current)["status"], "warning")

    def test_12_no_previous_report_is_explicit_gap(self):
        result = analyze_pipeline(self.current)
        self.assertIn("previous_week_report", result["data_gaps"])

    def test_13_effective_numeric_change(self):
        self.assertEqual(audit_action_change(self.current, self.previous)["verdict"], "effective")

    def test_14_free_text_does_not_invent_effect(self):
        self.current["previous_action_change"]["verification_metric"] = "顧客好感度"
        result = audit_action_change(self.current)
        self.assertEqual(result["verdict"], "unknown")
        self.assertIn("numeric_before_after", result["data_gaps"])

    def test_15_negative_count_rejected(self):
        self.current["results"]["orders"] = -1
        self.assertFalse(validate_report(self.current)["valid"])

    def test_16_non_integer_count_rejected(self):
        self.current["results"]["visits"] = 1.5
        self.assertFalse(validate_report(self.current)["valid"])

    def test_17_invalid_previous_does_not_block_current(self):
        previous = copy.deepcopy(self.previous)
        previous["next_action_change"]["owner"] = ""
        result = process_weekly_report(self.current, previous, now=self.now)
        self.assertNotEqual(result["status"], "error")
        self.assertIn("valid_previous_week_report", result["data_gaps"])

    def test_18_manager_dashboard_has_required_fields(self):
        processed = process_weekly_report(self.current, self.previous, now=self.now)
        row = aggregate_manager_view([processed])[0]
        self.assertIn("sales_achievement_rate", row)
        self.assertIn("previous_action_verdict", row)

    def test_19_research_data_is_labeled_operational(self):
        translated = translate_report(self.current)
        self.assertEqual(translated["data_source"], "operational")
        self.assertIn("pressure_event_density", translated["data_gaps"])

    def test_20_identical_input_is_deterministic(self):
        a = process_weekly_report(self.current, self.previous, now=self.now)
        b = process_weekly_report(self.current, self.previous, now=self.now)
        self.assertEqual(a, b)

    def test_21_csv_export(self):
        processed = process_weekly_report(self.current, self.previous, now=self.now)
        with tempfile.TemporaryDirectory() as directory:
            path = export_manager_csv(aggregate_manager_view([processed]), Path(directory) / "manager.csv")
            self.assertTrue(path.exists())

    def test_22_safe_rate(self):
        self.assertEqual(safe_rate(3, 4), 0.75)
        self.assertIsNone(safe_rate(3, 0))

    def test_23_weekly_csv_roundtrip(self):
        with tempfile.TemporaryDirectory() as directory:
            path = export_weekly_csv([self.current], Path(directory) / "weekly.csv")
            restored = read_weekly_csv(path)[0]
            self.assertEqual(restored["results"]["orders"], self.current["results"]["orders"])
            self.assertIs(restored["manager_decision"]["required"], True)


class ResearchRegressionTests(unittest.TestCase):
    def test_existing_protocols_and_p4_are_preserved(self):
        import run_experiment
        self.assertEqual(len(run_experiment.PROTOCOLS), 6)
        self.assertIn("P4_週報最適化", run_experiment.PROTOCOLS)

    def test_existing_simulation_is_deterministic(self):
        import run_experiment
        p = run_experiment.PROTOCOLS["P4_週報最適化"]
        self.assertEqual(run_experiment.simulate(42, p), run_experiment.simulate(42, p))


if __name__ == "__main__":
    unittest.main()
