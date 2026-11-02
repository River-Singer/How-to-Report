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
CURRENT = EVAL / "content-0.7.4"
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
            self.assertEqual(len(cases), 4)
            self.assertEqual(sorted(len(c["turns"]) for c in cases), [2, 2, 2, 3])
            after = {p.relative_to(moved): p.read_bytes() for p in moved.rglob("*") if p.is_file()}
            self.assertEqual(before, after)

    def test_new_evidence_is_not_visible_in_first_turn(self):
        cases, errors = CHECK.validate(CURRENT)
        self.assertFalse(errors)
        case = next(c for c in cases if c["id"] == "C074-MATERIAL")
        first = CHECK.visible_turn(case, 1)
        second = CHECK.visible_turn(case, 2)
        self.assertNotIn("fixtures/coordination-update.md", first["fixtures"])
        self.assertIn("fixtures/coordination-update.md", second["fixtures"])
        self.assertEqual(len(case["turns"]), 2)
        self.assertNotIn("fixtures/request-deadline-update.md", case["fixtures"])
        self.assertFalse({"must", "must_not", "turns", "scored_dimensions"} & first.keys())

    def test_cli_default_current_and_explicit_historical_scope(self):
        for arguments, expected in [([], 4), (["--root", str(EVAL / "content-0.7.3")], 4), (["--root", str(EVAL / "content-0.7.2")], 4), (["--root", str(EVAL / "content-0.7.1")], 4), (["--root", str(EVAL / "content-0.7.0")], 4), (["--root", str(EVAL / "content-0.6.1")], 6), (["--root", str(EVAL / "content-0.6.0")], 4), (["--root", str(EVAL)], 67)]:
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
        case = next(c for c in cases if c["id"] == "C074-AUDIT")
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
