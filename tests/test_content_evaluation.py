"""Current content inputs remain portable, staged and separate from historical designs."""
from pathlib import Path
import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
EVAL = ROOT / "evaluation"
CURRENT = EVAL / "content-0.8.2"
spec = importlib.util.spec_from_file_location("content_case_check", EVAL / "tools/validate_cases.py")
CHECK = importlib.util.module_from_spec(spec)
spec.loader.exec_module(CHECK)


class ContentEvaluationTests(unittest.TestCase):
    def test_current_dataset_is_portable_and_readonly(self):
        with tempfile.TemporaryDirectory() as temporary:
            moved = Path(temporary) / "content"
            shutil.copytree(CURRENT, moved)
            before = {p.relative_to(moved): p.read_bytes() for p in moved.rglob("*") if p.is_file()}
            cases, errors = CHECK.validate(moved)
            self.assertFalse(errors)
            self.assertEqual(len(cases), 13)
            self.assertEqual([len(c["turns"]) for c in cases], [2, 1, 2, 1, 2, 2, 3, 1, 3, 2, 1, 2, 3])
            after = {p.relative_to(moved): p.read_bytes() for p in moved.rglob("*") if p.is_file()}
            self.assertEqual(before, after)

    def test_depth_pair_and_joint_peer_share_complete_sources(self):
        cases, errors = CHECK.validate(CURRENT)
        self.assertFalse(errors)
        selected = [c for c in cases if c["family"] in
                    ("03-business-direct", "04-business-department", "08-external-peer")]
        self.assertEqual(len(selected), 3)
        expected = ["fixtures/cost-pilot-" + part + ".md"
                    for part in ("records", "rules", "checks", "arrangements")]
        for case in selected:
            self.assertEqual(case["fixtures"], expected)
            for turn in case["turn_fixtures"]:
                self.assertEqual(turn, expected)

    def test_unchanged_scenarios_keep_original_prompts_and_exposure(self):
        prior = [json.loads(line) for line in
                 (EVAL / "content-0.8.1/cases.jsonl").read_text(encoding="utf-8").splitlines()]
        current, errors = CHECK.validate(CURRENT)
        self.assertFalse(errors)
        for n in set(range(13)) - {2, 3, 7}:
            for field in ("turns", "fixtures", "turn_fixtures"):
                self.assertEqual(current[n][field], prior[n][field])

    def test_rich_cost_rows_reconcile_without_treating_pending_as_zero(self):
        body = (CURRENT / "fixtures/cost-pilot-records.md").read_text(encoding="utf-8")
        rows = [[cell.strip() for cell in line.strip().strip("|").split("|")]
                for line in body.splitlines() if line.startswith("| R")]
        self.assertEqual(len(rows), 6)
        amounts = {}
        for row in rows:
            amounts[row[0]] = (int(row[4]) * (int(row[5]) + int(row[6]))
                               if row[7] == "已确认" else None)
        self.assertEqual(amounts, {"R1": 200, "R2": 50, "R3": 224,
                                  "R4": 45, "R5": 216, "R6": None})
        self.assertEqual(amounts["R1"] + amounts["R2"], 250)
        self.assertEqual(amounts["R3"] + amounts["R4"], 269)
        self.assertEqual((amounts["R3"] - amounts["R1"]) +
                         (amounts["R4"] - amounts["R2"]), 19)

    def test_new_evidence_is_not_visible_in_first_turn(self):
        cases, errors = CHECK.validate(CURRENT)
        self.assertFalse(errors)
        case = next(c for c in cases if c["id"] == "C082-MATERIAL")
        first = CHECK.visible_turn(case, 1)
        second = CHECK.visible_turn(case, 2)
        third = CHECK.visible_turn(case, 3)
        self.assertNotIn("fixtures/coordination-update.md", first["fixtures"])
        self.assertNotIn("fixtures/coordination-update.md", second["fixtures"])
        self.assertIn("fixtures/coordination-update.md", third["fixtures"])
        self.assertEqual(len(case["turns"]), 3)
        self.assertNotIn("fixtures/request-deadline-update.md", case["fixtures"])
        self.assertFalse({"must", "must_not", "turns", "scored_dimensions"} & first.keys())

    def test_cli_default_current_and_explicit_historical_scope(self):
        for arguments, expected in [([], 13), (["--root", str(EVAL / "content-0.8.0")], 13), (["--root", str(EVAL / "content-0.7.5")], 13), (["--root", str(EVAL / "content-0.7.4")], 4), (["--root", str(EVAL / "content-0.7.3")], 4), (["--root", str(EVAL / "content-0.7.2")], 4), (["--root", str(EVAL / "content-0.7.1")], 4), (["--root", str(EVAL / "content-0.7.0")], 4), (["--root", str(EVAL / "content-0.6.1")], 6), (["--root", str(EVAL / "content-0.6.0")], 4), (["--root", str(EVAL)], 67)]:
            with self.subTest(arguments=arguments):
                result = subprocess.run([sys.executable, "-B", "-I", str(EVAL / "tools/validate_content_cases.py"), *arguments], cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                receipt = json.loads(result.stdout)
                self.assertEqual(receipt["cases"], expected)
                self.assertFalse(receipt["model_execution"])
                self.assertEqual(receipt["writes"], "none")

    def test_changed_current_input_is_not_repaired(self):
        with tempfile.TemporaryDirectory() as temporary:
            moved = Path(temporary) / "content"
            shutil.copytree(CURRENT, moved)
            fixture = moved / "fixtures/coordination.md"
            fixture.write_bytes(fixture.read_bytes() + b"changed")
            before = fixture.read_bytes()
            _, errors = CHECK.validate(moved)
            self.assertTrue(any("changed input" in error for error in errors))
            self.assertEqual(fixture.read_bytes(), before)

    def test_audit_exposes_body_before_sources_and_author_notes(self):
        cases, errors = CHECK.validate(CURRENT)
        self.assertFalse(errors)
        case = next(c for c in cases if c["id"] == "C082-AUDIT")
        first, second, third = [CHECK.visible_turn(case, n) for n in (1, 2, 3)]
        self.assertEqual(first["fixtures"], ["fixtures/audit-draft.md"])
        self.assertIn("fixtures/audit-source.md", second["fixtures"])
        for path in ("fixtures/audit-author-notes.md", "fixtures/audit-prior.md"):
            self.assertNotIn(path, first["fixtures"])
            self.assertNotIn(path, second["fixtures"])
            self.assertIn(path, third["fixtures"])

    def test_every_visible_turn_omits_rubric_and_future_turns(self):
        cases, errors = CHECK.validate(CURRENT)
        self.assertFalse(errors)
        allowed = {"case_id", "entry", "environment", "turn", "prompt", "fixtures", "instructions"}
        for case in cases:
            for number, prompt in enumerate(case["turns"], 1):
                with self.subTest(case=case["id"], turn=number):
                    visible = CHECK.visible_turn(case, number)
                    self.assertEqual(set(visible), allowed)
                    self.assertEqual(visible["prompt"], prompt)
                    self.assertEqual(visible["fixtures"], case.get("turn_fixtures", [case["fixtures"]] * len(case["turns"]))[number - 1])

    def test_current_inventory_covers_all_input_files(self):
        metadata = json.loads((CURRENT / "dataset.json").read_text(encoding="utf-8"))
        actual = {p.relative_to(CURRENT).as_posix() for p in CURRENT.rglob("*") if p.is_file() and p.name != "dataset.json"}
        self.assertEqual(set(metadata["files"]), actual)
        for path, expected in metadata["files"].items():
            self.assertEqual(hashlib.sha256((CURRENT / path).read_bytes()).hexdigest(), expected)

    def test_periodic_correction_and_close_are_released_in_their_stages(self):
        cases, errors = CHECK.validate(CURRENT)
        self.assertFalse(errors)
        weekly = next(c for c in cases if c["id"] == "C082-WEEKLY")
        monthly = next(c for c in cases if c["id"] == "C082-MONTHLY")
        first = CHECK.visible_turn(weekly, 1)["fixtures"]
        corrected = CHECK.visible_turn(weekly, 2)["fixtures"]
        close = CHECK.visible_turn(monthly, 1)["fixtures"]
        self.assertNotIn("fixtures/periodic-week-correction.md", first)
        self.assertIn("fixtures/periodic-week-correction.md", corrected)
        for stage in (first, corrected):
            self.assertNotIn("fixtures/periodic-month-close.md", stage)
        self.assertTrue(set(corrected).issubset(close))
        self.assertIn("fixtures/periodic-month-close.md", close)

    def test_current_case_ids_cover_distinct_scenarios(self):
        cases, errors = CHECK.validate(CURRENT)
        self.assertFalse(errors)
        self.assertEqual({c["id"] for c in cases}, {
            "C082-INTERNAL", "C082-EXTERNAL", "C082-BUSINESS-DIRECT",
            "C082-BUSINESS-DEPARTMENT", "C082-TECHNICAL-DIRECT",
            "C082-TECHNICAL-DEPARTMENT", "C082-GENERAL-MANAGER",
            "C082-EXTERNAL-PEER", "C082-MATERIAL", "C082-WEEKLY",
            "C082-MONTHLY", "C082-TRANSFER", "C082-AUDIT",
        })
        self.assertEqual(sum(len(c["turns"]) for c in cases), 25)

    def test_new_choice_conditions_are_not_exposed_early(self):
        cases, errors = CHECK.validate(CURRENT)
        self.assertFalse(errors)
        for identity, filename, final_turn in [
            ("C082-TECHNICAL-DEPARTMENT", "fixtures/next-task-options.md", 2),
            ("C082-GENERAL-MANAGER", "fixtures/pilot-participation.md", 3),
        ]:
            case = next(c for c in cases if c["id"] == identity)
            for turn in range(1, final_turn):
                self.assertNotIn(filename, CHECK.visible_turn(case, turn)["fixtures"])
            self.assertIn(filename, CHECK.visible_turn(case, final_turn)["fixtures"])

    def test_invalid_stage_cannot_use_undeclared_fixture(self):
        with tempfile.TemporaryDirectory() as temporary:
            moved = Path(temporary) / "content"
            shutil.copytree(CURRENT, moved)
            catalog = moved / "cases.jsonl"
            rows = [json.loads(line) for line in catalog.read_text(encoding="utf-8").splitlines()]
            rows[0]["turn_fixtures"][0].append("fixtures/audit-prior.md")
            catalog.write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n", encoding="utf-8")
            metadata = json.loads((moved / "dataset.json").read_text(encoding="utf-8"))
            metadata["files"]["cases.jsonl"] = hashlib.sha256(catalog.read_bytes()).hexdigest()
            (moved / "dataset.json").write_text(json.dumps(metadata), encoding="utf-8")
            _, errors = CHECK.validate(moved)
            self.assertTrue(any("stage fixture is outside declared inputs" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
