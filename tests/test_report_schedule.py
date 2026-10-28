"""Deterministic schedule behavior, isolated-package integration; no model calls."""
from copy import deepcopy
import hashlib
from html.parser import HTMLParser
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
        self.spec = json.loads((SOURCE / "assets/report-html/sample-schedule.json").read_text(encoding="utf-8"))

    def test_sample_calculations_and_five_views(self):
        core.validate(self.spec)
        self.assertEqual(core.delta(self.spec["tasks"][1]), 15)
        self.assertEqual(core.delta(self.spec["milestones"][0], True), 5)
        plan = core.to_plan(self.spec, list(core.VIEWS))
        self.assertEqual(len(plan["pages"]), 6)
        self.assertEqual({p["elements"][0]["schedule"]["view"] for p in plan["pages"]}, set(core.VIEWS))

    def test_no_baseline_preserves_unknown(self):
        del self.spec["baseline"]; self.spec.pop("snapshots")
        for t in self.spec["tasks"]: t.pop("baseline")
        self.spec["milestones"][0].pop("baseline_date")
        core.validate(self.spec)
        self.assertIsNone(core.delta(self.spec["tasks"][0]))
        core.to_plan(self.spec, ["gantt", "milestones"])
        with self.assertRaisesRegex(ValueError, "baseline"):
            core.to_plan(self.spec, ["drift"])

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
        core.to_plan(self.spec,["outcomes"])

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

    def test_summary_cannot_hide_tail_blocker(self):
        self.spec["summary"]["task_ids"]=["requirements","business"]
        with self.assertRaisesRegex(ValueError,"omits blocked"): core.validate(self.spec)

    def test_summary_milestones_are_explicit_and_preserved(self):
        plan=core.to_plan(self.spec,["summary"])
        self.assertEqual([m for p in plan["pages"] for m in p["elements"][0]["schedule"].get("milestone_ids",[])],["launch"])
        self.spec["summary"]["milestone_ids"]=["absent"]
        with self.assertRaises(ValueError):core.validate(self.spec)

    def test_all_actions_survive_pagination(self):
        self.spec["actions"]=[{"id":f"act{i}","text":f"Action {i}","refs":self.spec["refs"]} for i in range(10)]
        plan=core.to_plan(self.spec,["summary"])
        emitted=[a for p in plan["pages"] for a in p["elements"][0]["schedule"].get("action_ids",[])]
        self.assertEqual(emitted,[f"act{i}" for i in range(10)])

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
        core.to_plan(self.spec, ["milestones", "drift"])
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
        core.to_plan(self.spec, ["milestones", "drift"])
        self.assertEqual(self.spec, before)

    def test_snapshot_boolean_revision_is_not_integer_one(self):
        self.spec["snapshots"][0]["baseline_ref"]["revision"]=True
        with self.assertRaisesRegex(ValueError,"revision"):core.validate(self.spec)

    def test_drift_history_paginated_without_losing_records(self):
        snapshot=deepcopy(self.spec["snapshots"][0])
        self.spec["snapshots"]=[]
        for n in range(8):
            item=deepcopy(snapshot);item["reported_on"]=f"2026-10-{10+n:02d}"
            self.spec["snapshots"].append(item)
        plan=core.to_plan(self.spec,["drift"])
        self.assertEqual([n for p in plan["pages"] for n in p["elements"][0]["schedule"]["snapshot_indices"]],list(range(8)))

    def test_one_snapshot_cannot_be_drift(self):
        self.spec["snapshots"]=self.spec["snapshots"][:1]
        core.validate(self.spec)
        with self.assertRaisesRegex(ValueError,"two recorded"): core.to_plan(self.spec,["drift"])

    def test_missing_historical_point_is_not_interpolated(self):
        self.spec["snapshots"][1]["forecasts"]=[]
        with self.assertRaisesRegex(ValueError,"missing historical"): core.to_plan(self.spec,["drift"])

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
    def test_cli_conflict_and_huge_percentage_fail_cleanly_before_output(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); pkg = root / "skill"; scripts = pkg / "scripts"
            scripts.mkdir(parents=True)
            (pkg / "SKILL.md").write_text("test installation", encoding="utf-8")
            for folder in (SOURCE / "scripts", ROOT / "skill-src/shared/scripts"):
                for path in folder.glob("*.py"):
                    shutil.copyfile(path, scripts / path.name)
            shutil.copytree(SOURCE / "assets/report-html", pkg / "assets/report-html")
            baseline = json.loads((SOURCE / "assets/report-html/sample-schedule.json").read_text(encoding="utf-8"))
            package_before = {p.relative_to(pkg): p.read_bytes() for p in pkg.rglob("*") if p.is_file()}
            for kind in ("same-day-conflict", "huge-percentage"):
                spec = deepcopy(baseline)
                if kind == "same-day-conflict":
                    spec["snapshots"][-1]["forecasts"][0]["date"] = "2026-12-01"
                else:
                    spec["tasks"][1]["progress"]["value"] = 10**400
                source = root / (kind + ".json")
                source.write_text(json.dumps(spec), encoding="utf-8")
                before = source.read_bytes()
                output = root / (kind + "-output")
                for command in ("validate", "render"):
                    args = [sys.executable, "-I", "-B", str(scripts / "report_schedule.py"), command, str(source)]
                    if command == "render":
                        args += ["--views", "milestones,drift", "--output", str(output)]
                    process = subprocess.run(args, cwd=root, capture_output=True, text=True, encoding="utf-8")
                    with self.subTest(kind=kind, command=command):
                        self.assertEqual(process.returncode, 2, process.stdout + process.stderr)
                        error = json.loads(process.stdout)
                        self.assertFalse(error["valid"])
                        self.assertEqual(error["semantic_validation"], "not_run")
                        self.assertIn("same-day" if kind == "same-day-conflict" else "progress", error["error"])
                        self.assertEqual(process.stderr, "")
                        self.assertFalse(output.exists())
                        self.assertEqual(source.read_bytes(), before)
            # A preserved historical error is a warning, not an invented FS issue.
            history = deepcopy(baseline)
            history["milestones"][0].pop("forecast_date")
            history["milestones"][0]["actual_date"] = "2026-10-20"
            history["milestones"][0]["refs"] = [{"id": "actual-record", "revision": 2, "locator": "launch event"}]
            source = root / "history.json"; source.write_text(json.dumps(history), encoding="utf-8")
            before = source.read_bytes(); output = root / "history-output"
            process = subprocess.run([sys.executable, "-I", "-B", str(scripts / "report_schedule.py"),
                                      "render", str(source), "--views", "milestones,drift", "--output", str(output)],
                                     cwd=root, capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
            receipt = json.loads(process.stdout)
            self.assertEqual(len(receipt["warnings"]), 2)
            self.assertTrue(all(w["code"] == "historical_forecast_after_actual" for w in receipt["warnings"]))
            html = (output / "index.html").read_text(encoding="utf-8")
            self.assertIn('data-warning-code="historical_forecast_after_actual"', html)
            self.assertNotIn('data-warning-code="same_day_fs_order_unknown"', html)
            self.assertIn("actual-record@2", html)
            self.assertIn("snapshot.1028", html)
            self.assertIn("2026-10-20", html)
            self.assertIn("2026-10-28", html)
            self.assertEqual((output / "schedule-input.json").read_bytes(), before)
            self.assertEqual(source.read_bytes(), before)
            self.assertEqual(package_before, {p.relative_to(pkg): p.read_bytes() for p in pkg.rglob("*") if p.is_file()})

    def test_isolated_cli_hashes_namespace_and_refusal(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);pkg=root/"skill";scripts=pkg/"scripts";scripts.mkdir(parents=True)
            (pkg/"SKILL.md").write_text("test installation",encoding="utf-8")
            for folder in (SOURCE/"scripts",ROOT/"skill-src/shared/scripts"):
                for p in folder.glob("*.py"):shutil.copyfile(p,scripts/p.name)
            shutil.copytree(SOURCE/"assets/report-html",pkg/"assets/report-html")
            sample=root/"input.json";raw=(SOURCE/"assets/report-html/sample-schedule.json").read_bytes();sample.write_bytes(raw)
            out=root/"rendered"
            args=[sys.executable,"-I",str(scripts/"report_schedule.py"),"render",str(sample),"--views",",".join(core.VIEWS),"--output",str(out)]
            run=subprocess.run(args,cwd=root,capture_output=True,text=True,encoding="utf-8")
            self.assertEqual(run.returncode,0,run.stdout+run.stderr)
            receipt=json.loads((out/"schedule-receipt.json").read_text(encoding="utf-8"))
            self.assertEqual(receipt["input_sha256"],hashlib.sha256(raw).hexdigest())
            self.assertEqual(receipt["semantic_validation"],"not_run")
            for name,digest in receipt["files"].items():self.assertEqual(hashlib.sha256((out/name).read_bytes()).hexdigest(),digest)
            page_map=json.loads((out/"page-map.json").read_text(encoding="utf-8"))
            datums=[x for x in page_map["elements"] if x.get("datum_id")]
            self.assertEqual(len({x["datum_id"] for x in datums}),len(datums))
            self.assertTrue(any(x["displayed"].get("deviation_days")==15 for x in datums))
            self.assertNotIn('<header class="element-header">',(out/"index.html").read_text(encoding="utf-8"))
            shared=[x for x in page_map["elements"] if x.get("shared_display")]
            self.assertEqual(len(shared),6)
            self.assertTrue(all("title" not in x["displayed"] and "body" not in x["displayed"] for x in shared))
            self.assertEqual((out/"schedule-input.json").read_bytes(),raw)
            before={p.name:p.read_bytes() for p in out.iterdir() if p.is_file()}
            self.assertEqual(subprocess.run(args,capture_output=True).returncode,2)
            self.assertEqual(before,{p.name:p.read_bytes() for p in out.iterdir() if p.is_file()})
            other=root/"another-skill";other.mkdir();(other/"SKILL.md").write_text("other",encoding="utf-8")
            args[-1]=str(other/"pollution")
            self.assertEqual(subprocess.run(args,capture_output=True).returncode,2)
            self.assertFalse((other/"pollution").exists())


if __name__ == "__main__":unittest.main()
