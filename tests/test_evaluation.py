"""Portable evaluation input checks, without agent/model execution."""
from __future__ import annotations

from decimal import Decimal
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

EVALUATION = Path(__file__).resolve().parents[1] / "evaluation"


def module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


CHECK = module("evaluation_input_check", EVALUATION / "tools/validate_cases.py")
ORACLE = module("evaluation_numeric_oracle", EVALUATION / "tools/numeric_oracle.py")


class EvaluationTests(unittest.TestCase):
    def test_current_inputs_and_commands_are_read_only(self):
        before = {p.relative_to(EVALUATION): (p.read_bytes(), p.stat().st_mtime_ns)
                  for p in EVALUATION.rglob("*") if p.is_file()}
        cases, issues = CHECK.validate(EVALUATION)
        self.assertEqual(issues, [])
        self.assertEqual(len(cases), 39)
        for tool in ("validate_cases.py", "numeric_oracle.py"):
            result = subprocess.run([sys.executable, "-B", "-I", str(EVALUATION / "tools" / tool)],
                                    cwd=EVALUATION.parent, capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            receipt = json.loads(result.stdout)
            self.assertFalse(receipt["model_execution"])
            self.assertEqual(receipt["writes"], "none")
        after = {p.relative_to(EVALUATION): (p.read_bytes(), p.stat().st_mtime_ns)
                 for p in EVALUATION.rglob("*") if p.is_file()}
        self.assertEqual(before, after)

    def test_stage_display_does_not_leak_oracle_or_future_input(self):
        cases, issues = CHECK.validate(EVALUATION)
        self.assertFalse(issues)
        case = next(item for item in cases if item["id"] == "B-A02")
        first = CHECK.visible_turn(case, 1)
        second = CHECK.visible_turn(case, 2)
        self.assertEqual(first["prompt"], case["turns"][0])
        self.assertEqual(first["fixtures"], case["turn_fixtures"][0])
        self.assertNotEqual(first["fixtures"], second["fixtures"])
        self.assertFalse({"must", "must_not", "tags", "turns"} & first.keys())
        for invalid in (0, 3):
            with self.assertRaises(ValueError):
                CHECK.visible_turn(case, invalid)

    def test_corrupt_input_types_duplicates_and_escape_fail_cleanly(self):
        for mode in ("type", "duplicate", "escape"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as temporary:
                target = Path(temporary) / "evaluation"
                shutil.copytree(EVALUATION, target, ignore=shutil.ignore_patterns("__pycache__"))
                path = target / "eval-cases.jsonl"
                rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
                if mode == "type":
                    rows[0]["id"] = ["invalid"]
                elif mode == "duplicate":
                    rows[1]["id"] = rows[0]["id"]
                else:
                    rows[0]["fixtures"] = ["../private.md"]
                path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
                metadata = json.loads((target / "dataset.json").read_text(encoding="utf-8"))
                metadata["files"]["eval-cases.jsonl"] = hashlib.sha256(path.read_bytes()).hexdigest()
                (target / "dataset.json").write_text(json.dumps(metadata), encoding="utf-8")
                _, issues = CHECK.validate(target)
                self.assertTrue(issues)

    def test_hash_drift_is_not_silently_repaired(self):
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "evaluation"
            shutil.copytree(EVALUATION, target, ignore=shutil.ignore_patterns("__pycache__"))
            fixture = target / "fixtures/data-cost.csv"
            fixture.write_bytes(fixture.read_bytes() + b"\n")
            changed = fixture.read_bytes()
            _, issues = CHECK.validate(target)
            self.assertTrue(any("changed input" in item for item in issues))
            self.assertEqual(fixture.read_bytes(), changed)

    def test_independent_cost_oracle_accepts_declared_decompositions(self):
        result = ORACLE.cost_decomposition(EVALUATION / "fixtures/data-cost.csv")
        self.assertEqual((result["base"], result["current"], result["delta"]),
                         (Decimal(350), Decimal(440), Decimal(90)))
        self.assertEqual(result["base_weighted"], {"price": Decimal(35), "quantity": Decimal(50), "interaction": Decimal(5)})
        self.assertEqual(result["symmetric"], {"price": Decimal("37.5"), "quantity": Decimal("52.5")})
        for key in ("base_weighted", "price_then_quantity", "quantity_then_price", "symmetric"):
            self.assertEqual(sum(result[key].values()), result["delta"])
        with self.assertRaises(ValueError):
            ORACLE.cost_decomposition(EVALUATION / "fixtures/data-conflicted.csv")


if __name__ == "__main__":
    unittest.main()
