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
CURRENT = EVAL / "content-0.6.0"
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
            self.assertTrue(all(len(c["turns"]) == 2 for c in cases))
            after = {p.relative_to(moved): p.read_bytes() for p in moved.rglob("*") if p.is_file()}
            self.assertEqual(before, after)

    def test_new_evidence_is_not_visible_in_first_turn(self):
        cases, errors = CHECK.validate(CURRENT)
        self.assertFalse(errors)
        case = next(c for c in cases if c["id"] == "C06-VALUE")
        first = CHECK.visible_turn(case, 1)
        second = CHECK.visible_turn(case, 2)
        self.assertNotIn("fixtures/value-update.md", first["fixtures"])
        self.assertIn("fixtures/value-update.md", second["fixtures"])
        self.assertFalse({"must", "must_not", "turns", "scored_dimensions"} & first.keys())

    def test_cli_default_current_and_explicit_historical_scope(self):
        for arguments, expected in [([], 4), (["--root", str(EVAL)], 67)]:
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
            fixture = moved / "fixtures/goal.md"
            fixture.write_bytes(fixture.read_bytes() + b"changed")
            before = fixture.read_bytes()
            _, errors = CHECK.validate(moved)
            self.assertTrue(any("changed input" in error for error in errors))
            self.assertEqual(fixture.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
