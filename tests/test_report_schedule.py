"""Deterministic schedule behavior, isolated-package integration; no model calls."""
from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "skill-src/how-to-report"
module = importlib.util.spec_from_file_location("schedule_test_core", SOURCE / "scripts/schedule_core.py")
core = importlib.util.module_from_spec(module)
module.loader.exec_module(core)


class ScheduleTests(unittest.TestCase):
    def setUp(self):
        self.spec = json.loads((SOURCE / "assets/schedule/sample-schedule.json").read_text(encoding="utf-8"))

    def test_sample_calculations(self):
        before = deepcopy(self.spec)
        core.validate(self.spec)
        self.assertEqual(core.delta(self.spec["tasks"][1]), 15)
        self.assertEqual(core.delta(self.spec["milestones"][0], True), 5)
        self.assertEqual(self.spec, before)

    def test_no_baseline_preserves_unknown(self):
        del self.spec["baseline"]; self.spec.pop("snapshots")
        for t in self.spec["tasks"]: t.pop("baseline")
        self.spec["milestones"][0].pop("baseline_date")
        core.validate(self.spec)
        self.assertIsNone(core.delta(self.spec["tasks"][0]))

    def test_unknown_forecast_is_not_copied(self):
        self.spec["tasks"][1].pop("forecast")
        core.validate(self.spec)
        self.assertIsNone(core.finish(self.spec["tasks"][1]))
        self.assertIsNone(core.delta(self.spec["tasks"][1]))

    def test_future_actual_rejected(self):
        self.spec["tasks"][1]["actual"]["start"]="2026-10-29"
        with self.assertRaisesRegex(ValueError,"future actual"): core.validate(self.spec)

    def test_done_requires_actual(self):
        self.spec["tasks"][1]["state"]="done"
        with self.assertRaisesRegex(ValueError,"actual finish"): core.validate(self.spec)

    def test_percentage_cannot_be_boolean_or_undefined_basis(self):
        for value in (True, float("inf"), -1, 101, 10**400):
            s=deepcopy(self.spec);s["tasks"][1]["progress"]["value"]=value
            with self.assertRaises(ValueError): core.validate(s)
        self.spec["tasks"][1]["progress"]["basis"]=""
        with self.assertRaises(ValueError): core.validate(self.spec)

    def test_acceptance_is_independent_and_evidence_bound(self):
        acc=self.spec["tasks"][1]["acceptance"];acc.update(status="rejected",result="接口用例未通过")
        core.validate(self.spec)
        del acc["refs"]
        with self.assertRaisesRegex(ValueError,"evidence"): core.validate(self.spec)

    def test_partial_acceptance_does_not_require_project_done(self):
        self.spec["tasks"][1]["acceptance"].update(status="accepted",scope="仅首批12项已验收")
        core.validate(self.spec)

    def test_missing_acceptance_is_unknown(self):
        self.spec["tasks"][0].pop("acceptance")
        core.validate(self.spec)

    def test_fs_current_actual_forecast_conflict(self):
        self.spec["tasks"][2]["forecast"]["start"]="2026-11-02"
        with self.assertRaisesRegex(ValueError,"FS"): core.validate(self.spec)

    def test_same_day_fs_preserves_uncertainty(self):
        self.spec["tasks"][2]["forecast"]["start"]="2026-11-03"
        core.validate(self.spec)
        self.assertTrue(any(w["code"]=="same_day_fs_order_unknown" for w in core.warnings(self.spec)))

    def test_cycle_rejected_without_rescheduling(self):
        self.spec["dependencies"]=[{"from":"integration","to":"integration","type":"FS","lag":0,"refs":self.spec["refs"]}]
        for t in self.spec["tasks"]: t.pop("baseline",None);t.pop("forecast",None)
        with self.assertRaisesRegex(ValueError,"cyclic"): core.validate(self.spec)

    def test_unsupported_dependency_and_calendar(self):
        self.spec["dependencies"][0]["type"]="SS"
        with self.assertRaisesRegex(ValueError,"FS"): core.validate(self.spec)
        self.spec["dependencies"]=[];self.spec["calendar"]="workdays"
        with self.assertRaisesRegex(ValueError,"natural days"): core.validate(self.spec)

    def test_summary_selection_does_not_prescribe_the_report(self):
        self.spec["summary"]["task_ids"] = ["requirements", "business"]
        before = deepcopy(self.spec)
        core.validate(self.spec)
        self.assertEqual(self.spec, before)
        self.spec["summary"]["milestone_ids"] = ["absent"]
        with self.assertRaisesRegex(ValueError, "unknown object"):
            core.validate(self.spec)

    def test_long_content_is_not_constrained_by_a_slide(self):
        self.spec["title"] = "标题" * 1000
        self.spec["tasks"][0]["label"] = "长名称" * 1000
        self.spec["tasks"][1]["condition"] = "条件" * 1000
        core.validate(self.spec)

    def test_history_cannot_reuse_new_baseline(self):
        self.spec["snapshots"][0]["baseline_ref"]["revision"]=2
        with self.assertRaisesRegex(ValueError,"baseline"): core.validate(self.spec)

    def test_same_status_day_forecasts_must_agree_without_filling_unknown(self):
        self.spec["snapshots"][-1]["forecasts"][0]["date"] = "2026-12-01"
        with self.assertRaisesRegex(ValueError, "same-day current/historical forecast conflict"):
            core.validate(self.spec)
        # Earlier reports can legitimately differ from the current forecast.
        self.spec["snapshots"][-1]["reported_on"] = "2026-10-27"
        core.validate(self.spec)
        self.spec["snapshots"][-1]["reported_on"] = self.spec["as_of"]
        self.spec["milestones"][0].pop("forecast_date")
        before = deepcopy(self.spec)
        core.validate(self.spec)
        self.assertIsNone(core.delta(self.spec["milestones"][0], True))
        self.assertEqual(self.spec, before)

    def test_historical_forecasts_after_actual_are_preserved_with_evidence_warning(self):
        mark = self.spec["milestones"][0]
        mark.pop("forecast_date")
        mark["actual_date"] = "2026-10-20"
        mark["refs"] = [{"id": "actual-record", "revision": 2, "locator": "launch event"}]
        before = deepcopy(self.spec)
        core.validate(self.spec)
        warnings = [w for w in core.warnings(self.spec) if w["code"] == "historical_forecast_after_actual"]
        self.assertEqual([w["reported_on"] for w in warnings], ["2026-10-21", "2026-10-28"])
        self.assertEqual(warnings[-1]["actual_date"], "2026-10-20")
        self.assertEqual(warnings[-1]["forecast_date"], "2026-11-13")
        self.assertEqual(warnings[-1]["refs"], mark["refs"] + self.spec["snapshots"][-1]["forecasts"][0]["refs"])
        self.assertEqual(self.spec, before)

    def test_snapshot_boolean_revision_is_not_integer_one(self):
        self.spec["snapshots"][0]["baseline_ref"]["revision"]=True
        with self.assertRaisesRegex(ValueError,"revision"):core.validate(self.spec)

    def test_history_beyond_visual_window_preserved(self):
        snapshot = deepcopy(self.spec["snapshots"][0])
        self.spec["snapshots"] = []
        for n in range(15):
            item = deepcopy(snapshot)
            item["reported_on"] = f"2026-10-{10+n:02d}"
            self.spec["snapshots"].append(item)
        before = deepcopy(self.spec)
        core.validate(self.spec)
        self.assertEqual(self.spec, before)

    def test_single_and_missing_historical_points_remain_valid_facts(self):
        self.spec["snapshots"] = self.spec["snapshots"][:1]
        self.spec["snapshots"][0]["forecasts"] = []
        before = deepcopy(self.spec)
        core.validate(self.spec)
        self.assertEqual(self.spec, before)

    def test_revision_bool_and_unknown_fields_rejected(self):
        self.spec["refs"][0]["revision"]=True
        with self.assertRaises(ValueError): core.validate(self.spec)
        self.spec["refs"][0]["revision"]=1;self.spec["workday_calendar"]={}
        with self.assertRaisesRegex(ValueError,"unknown fields"): core.validate(self.spec)

    def test_milestone_baseline_needs_approval(self):
        self.spec.pop("baseline");self.spec.pop("snapshots")
        for task in self.spec["tasks"]:task.pop("baseline")
        with self.assertRaisesRegex(ValueError,"approved identity"):core.validate(self.spec)

    def test_real_leap_day_and_year_boundaries(self):
        self.assertEqual((core.day("2028-03-01")-core.day("2028-02-28")).days,2)
        self.assertEqual((core.day("2027-01-01")-core.day("2026-12-31")).days,1)
        with self.assertRaises(ValueError):core.day("2026-02-29")


class ScheduleIntegrationTests(unittest.TestCase):
    def test_isolated_read_only_date_checks_and_failure_paths(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            pkg = root / "skill"
            scripts = pkg / "scripts"
            scripts.mkdir(parents=True)
            (pkg / "SKILL.md").write_text("test installation", encoding="utf-8")
            for folder in (SOURCE / "scripts", ROOT / "skill-src/shared/scripts"):
                for path in folder.glob("*.py"):
                    shutil.copyfile(path, scripts / path.name)
            baseline = json.loads((SOURCE / "assets/schedule/sample-schedule.json").read_text(encoding="utf-8"))
            before_package = {p.relative_to(pkg): p.read_bytes() for p in pkg.rglob("*") if p.is_file()}
            source = root / "input.json"

            def execute(spec):
                source.write_text(json.dumps(spec), encoding="utf-8")
                before = source.read_bytes()
                process = subprocess.run([sys.executable, "-I", "-B", str(scripts / "report_schedule.py"),
                                          "validate", str(source)], cwd=root, capture_output=True,
                                         text=True, encoding="utf-8")
                self.assertEqual(source.read_bytes(), before)
                self.assertEqual(process.stderr, "")
                return process, json.loads(process.stdout)

            process, result = execute(baseline)
            self.assertEqual(process.returncode, 0)
            self.assertEqual(result["input_sha256"], hashlib.sha256(source.read_bytes()).hexdigest())
            for name, digest in result["method_sha256"].items():
                self.assertEqual(digest, hashlib.sha256((scripts / name).read_bytes()).hexdigest())
            rows = {row["id"]: row for row in result["date_comparisons"]}
            self.assertEqual(rows["integration"]["deviation_calendar_days"], 15)
            self.assertEqual(rows["integration"]["current_finish_type"], "forecast")
            self.assertEqual(rows["requirements"]["current_finish_type"], "actual")
            self.assertEqual(rows["launch"]["deviation_calendar_days"], 5)
            self.assertEqual(result["semantic_validation"], "not_run")
            self.assertEqual(result["run_mutation"], "not_performed")

            unknown = deepcopy(baseline)
            unknown["tasks"][1].pop("forecast")
            process, result = execute(unknown)
            row = next(row for row in result["date_comparisons"] if row["id"] == "integration")
            self.assertEqual(process.returncode, 0)
            self.assertIsNone(row["current_finish"])
            self.assertIsNone(row["deviation_calendar_days"])
            self.assertEqual(row["current_finish_type"], "unknown")

            for kind in ("same-day-conflict", "huge-percentage"):
                spec = deepcopy(baseline)
                if kind == "same-day-conflict":
                    spec["snapshots"][-1]["forecasts"][0]["date"] = "2026-12-01"
                else:
                    spec["tasks"][1]["progress"]["value"] = 10**400
                process, result = execute(spec)
                with self.subTest(kind=kind):
                    self.assertEqual(process.returncode, 2)
                    self.assertFalse(result["valid"])
                    self.assertIn("same-day" if kind == "same-day-conflict" else "progress", result["error"])

            history = deepcopy(baseline)
            history["milestones"][0].pop("forecast_date")
            history["milestones"][0]["actual_date"] = "2026-10-20"
            history["milestones"][0]["refs"] = [{"id": "actual-record", "revision": 2}]
            process, result = execute(history)
            self.assertEqual(process.returncode, 0)
            self.assertEqual(len(result["warnings"]), 2)
            self.assertTrue(all(row["code"] == "historical_forecast_after_actual" for row in result["warnings"]))
            self.assertEqual(result["warnings"][-1]["actual_date"], "2026-10-20")
            self.assertEqual(result["warnings"][-1]["forecast_date"], "2026-11-13")
            self.assertEqual(result["warnings"][-1]["refs"][0]["id"], "actual-record")

            obsolete = subprocess.run([sys.executable, "-I", "-B", str(scripts / "report_schedule.py"),
                                       "render", str(source), "--output", str(root / "rendered")],
                                      cwd=root, capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(obsolete.returncode, 2)
            self.assertFalse((root / "rendered").exists())
            self.assertFalse((scripts / "report_html.py").exists())
            self.assertEqual(before_package, {p.relative_to(pkg): p.read_bytes() for p in pkg.rglob("*") if p.is_file()})


if __name__ == "__main__":
    unittest.main()
