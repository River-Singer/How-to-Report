"""Local deterministic contracts; no model scenario execution or external data."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

PROJECT = Path(__file__).resolve().parents[1]
SOURCE = PROJECT / "skill-src" / "how-to-report"


class CalculationProfileTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="calculation-profile-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.package = self.root / "relocated"
        scripts = self.package / "scripts"
        scripts.mkdir(parents=True)
        for name in ("report_calculate.py", "report_profile.py", "report_run.py", "report_versions.py"):
            shutil.copyfile(SOURCE / "scripts" / name, scripts / name)
        shutil.copyfile(PROJECT / "skill-src/shared/scripts/validate_run.py", scripts / "validate_run.py")
        self.cwd = self.root / "unrelated"
        self.cwd.mkdir()
        self.data = self.root / "材料 #50%.csv"
        self.data.write_text("key,p0,q0,p1,q1\nA,10,2,12,3\nB,5,4,4,2\n", encoding="utf-8")
        self.spec = {"calculation_version": "0.1", "id": "synthetic-calc", "operation": "price_quantity_decomposition",
                     "source": {"id": "synthetic-data", "revision": 1, "ref": self.data.name, "sha256": self.digest(self.data)},
                     "context": {"measure": "synthetic expense", "unit": "CNY", "grain": "key", "period": "base/current",
                                 "population": "two synthetic rows", "filters": "none; all rows", "limitations": "synthetic algebra, not causes"},
                     "columns": {"base_price": "p0", "base_quantity": "q0", "current_price": "p1", "current_quantity": "q1"},
                     "column_units": {"base_price": "CNY/unit", "base_quantity": "units", "current_price": "CNY/unit", "current_quantity": "units"},
                     "key_columns": ["key"], "decimal_places": 2, "rounding": "half_even", "missing_policy": "error",
                     "definition_ref": "synthetic-test-definition"}
        self.spec_path = self.root / "spec.json"
        self.out = self.root / "new output"

    @staticmethod
    def digest(path):
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def save(self, path, obj):
        path.write_text(json.dumps(obj, ensure_ascii=False), encoding="utf-8")

    def command(self, helper, *args, expected=0):
        result = subprocess.run([sys.executable, "-I", "-B", str(self.package / "scripts" / helper), *map(str, args)],
                                cwd=self.cwd, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        self.assertNotIn("SECRET_CONFIRMED_VALUE", result.stdout)
        return json.loads(result.stdout)

    def calc(self, expected=0):
        self.spec["column_units"] = {role: self.spec["column_units"].get(role, "declared synthetic unit") for role in self.spec["columns"]}
        self.save(self.spec_path, self.spec)
        return self.command("report_calculate.py", "run", self.spec_path, "--output", self.out, expected=expected)

    def refresh(self, contents):
        self.data.write_text(contents, encoding="utf-8")
        self.spec["source"]["sha256"] = self.digest(self.data)

    def test_decomposition_receipt_snapshot_and_independent_integer_oracle(self):
        before = self.data.read_bytes()
        response = self.calc()
        result = json.loads((self.out / "result.json").read_text(encoding="utf-8"))
        # Independent hand arithmetic: base=20+20=40; current=36+8=44;
        # price=4-4=0; quantity=10-10=0; interaction=2+2=4.
        expected = {"base_total": "40", "current_total": "44", "difference": "4", "price_effect": "0",
                    "quantity_effect": "0", "interaction": "4", "reconciliation_residual": "0"}
        self.assertEqual({k: v["unrounded"] for k, v in result["values"].items()}, expected)
        receipt = json.loads((self.out / "calculation-receipt.json").read_text())
        self.assertEqual(receipt["result_sha256"], self.digest(self.out / "result.json"))
        self.assertEqual(receipt["method"]["sha256"], self.digest(self.package / "scripts/report_calculate.py"))
        self.assertEqual(receipt["independent_review"], "not_run")
        self.assertEqual(response["execution_status"], "completed")
        self.assertEqual((self.out / "input.csv").read_bytes(), before)
        self.assertEqual(self.data.read_bytes(), before)
        self.assertEqual((self.out / "spec.json").read_bytes(), self.spec_path.read_bytes())
        replay_out = self.root / "replayed"
        self.command("report_calculate.py", "run", self.out / "replay-spec.json", "--output", replay_out)
        self.assertEqual((replay_out / "result.json").read_bytes(), (self.out / "result.json").read_bytes())

    def test_sum_and_product_sum_use_final_aggregate_rounding(self):
        self.refresh("key,p,q\nA,4.4,2\nB,4.4,3\n")
        self.spec.update(operation="sum", columns={"value": "p"}, decimal_places=0)
        self.calc()
        value = json.loads((self.out / "result.json").read_text())["values"]["total"]
        self.assertEqual(value, {"unrounded": "8.8", "rounded": "9"})
        self.spec.update(operation="product_sum", columns={"price": "p", "quantity": "q"})
        self.out = self.root / "product"
        self.calc()
        self.assertEqual(json.loads((self.out / "result.json").read_text())["values"]["total"]["unrounded"], "22.0")

    def test_half_tie_policy_and_negative_values(self):
        self.refresh("key,v\nA,-6.5\n")
        self.spec.update(operation="sum", columns={"value": "v"}, decimal_places=0)
        for policy, expected in (("half_even", "-6"), ("half_up", "-7")):
            self.spec["rounding"] = policy
            self.out = self.root / policy
            self.calc()
            self.assertEqual(json.loads((self.out / "result.json").read_text())["values"]["total"]["rounded"], expected)

    def test_ratio_aggregate_and_zero_denominator(self):
        self.refresh("key,n,d\nA,1,2\nB,2,4\n")
        self.spec.update(operation="ratio_of_sums", columns={"numerator": "n", "denominator": "d"})
        self.calc()
        self.assertEqual(json.loads((self.out / "result.json").read_text())["values"]["ratio"]["rounded"], "0.50")
        self.refresh("key,n,d\nA,1,0\n")
        self.out = self.root / "zero-denominator"
        self.calc(expected=2)
        self.assertFalse(self.out.exists())

    def test_missing_invalid_and_nonfinite_are_never_zero(self):
        self.spec.update(operation="sum", columns={"value": "v"})
        for value in ("", "NaN", "Infinity", "True", "1e10", "1000000000000", "1.0000000000001"):
            with self.subTest(value=value):
                self.refresh("key,v\nA," + value + "\n")
                self.calc(expected=2)
                self.assertFalse(self.out.exists())

    def test_duplicate_grain_headers_width_and_empty_rows_fail(self):
        self.spec.update(operation="sum", columns={"value": "v"})
        for contents in ("key,v\nA,1\n A ,2\n", "key,v,v\nA,1,2\n", "key,v\nA\n", "key,v\nA,1,2\n", "key,v\n"):
            self.refresh(contents)
            self.calc(expected=2)
            self.assertFalse(self.out.exists())

    def test_source_version_change_requires_explicit_hash_and_keeps_old_output(self):
        self.calc()
        old_result = (self.out / "result.json").read_bytes()
        self.data.write_text("key,p0,q0,p1,q1\nA,10,2,12,4\n", encoding="utf-8")
        self.out = self.root / "v2"
        self.calc(expected=2)
        self.assertFalse(self.out.exists())
        self.spec["source"].update(revision=2, sha256=self.digest(self.data))
        self.calc()
        new = json.loads((self.out / "result.json").read_text())
        self.assertEqual(new["source"]["revision"], 2)
        self.assertEqual(new["values"]["difference"]["unrounded"], "28")
        self.assertEqual((self.root / "new output/result.json").read_bytes(), old_result)

    def test_strict_spec_rejects_unapproved_shape_and_boolean_revisions(self):
        original = deepcopy(self.spec)
        for mutate in (lambda s: s.update(operation="eval"), lambda s: s.update(extra="ignore"),
                       lambda s: s["source"].update(revision=True), lambda s: s.update(decimal_places=True),
                       lambda s: s.update(definition_ref=""), lambda s: s.update(missing_policy="zero")):
            self.spec = deepcopy(original)
            mutate(self.spec)
            self.calc(expected=2)
            self.assertFalse(self.out.exists())

    def test_output_no_overwrite_or_package_mutation(self):
        self.calc()
        before = {p.name: p.read_bytes() for p in self.out.iterdir()}
        self.calc(expected=2)
        self.assertEqual(before, {p.name: p.read_bytes() for p in self.out.iterdir()})
        self.out = self.package / "forbidden"
        self.calc(expected=2)
        self.assertFalse(self.out.exists())

    def test_invalid_json_or_source_code_is_not_executed(self):
        self.spec_path.write_text('{"id":1,"id":2}', encoding="utf-8")
        self.command("report_calculate.py", "run", self.spec_path, "--output", self.out, expected=2)
        self.assertFalse(self.out.exists())
        marker = self.root / "must-not-exist"
        self.spec.update(operation="sum", columns={"value": "v"})
        self.refresh("key,v\nA,__import__('pathlib').Path('must-not-exist').touch()\n")
        self.calc(expected=2)
        self.assertFalse(marker.exists())
        self.assertFalse((self.cwd / marker.name).exists())
        self.assertFalse(list(self.package.rglob("__pycache__")))

    def test_partial_output_failure_preserves_source_and_partial_files(self):
        self.spec["column_units"] = {role: "synthetic unit" for role in self.spec["columns"]}
        self.save(self.spec_path, self.spec)
        original = self.data.read_bytes()
        script = '''import sys
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, sys.argv[1])
import report_calculate
real_open = Path.open
def injected(path, *args, **kwargs):
    if path.name == "result.json" and args and args[0] == "xb":
        raise OSError("synthetic write failure")
    return real_open(path, *args, **kwargs)
with patch.object(Path, "open", injected):
    sys.exit(report_calculate.main(["run", sys.argv[2], "--output", sys.argv[3]]))
'''
        result = subprocess.run([sys.executable, "-I", "-B", "-c", script, str(self.package / "scripts"), str(self.spec_path), str(self.out)],
                                cwd=self.cwd, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)["execution_status"], "failed")
        self.assertEqual((self.out / "input.csv").read_bytes(), original)
        self.assertFalse((self.out / "calculation-receipt.json").exists())
        self.assertEqual(self.data.read_bytes(), original)

    def test_write_paths_reject_simulated_windows_reparse_attribute(self):
        self.save(self.spec_path, self.spec)
        marked = self.root / "simulated-reparse"
        marked.mkdir()
        script = '''import sys, stat
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
sys.path.insert(0, sys.argv[1])
import report_calculate, report_profile
real_lstat = Path.lstat
def simulated(path, *args, **kwargs):
    if str(path) == sys.argv[2]:
        return SimpleNamespace(st_mode=stat.S_IFDIR, st_file_attributes=0x400)
    return real_lstat(path, *args, **kwargs)
module = report_calculate if sys.argv[3] == "calc" else report_profile
with patch.object(Path, "lstat", simulated):
    sys.exit(module.main(sys.argv[4:]))
'''
        targets = [("calc", marked / "result", ["run", str(self.spec_path), "--output", str(marked / "result")]),
                   ("profile", marked / "private.json", ["init", str(marked / "private.json"), "--profile-id", "synthetic"])]
        for mode, output, arguments in targets:
            process = subprocess.run([sys.executable, "-I", "-B", "-c", script, str(self.package / "scripts"), str(marked), mode, *arguments],
                                     cwd=self.cwd, capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(process.returncode, 2, process.stdout + process.stderr)
            self.assertIn("reparse", json.loads(process.stdout)["error"])
            self.assertFalse(output.exists())

    def init_profile(self):
        self.profile = self.root / "private v0.json"
        return self.command("report_profile.py", "init", self.profile, "--profile-id", "synthetic-only")

    def entry(self, value="SECRET_CONFIRMED_VALUE", **changes):
        obj = {"id": "style", "type": "preference", "value": value, "scope": "synthetic confirmed scope",
               "confirmation_ref": "synthetic-user-message-1"}
        obj.update(changes)
        path = self.root / "change.json"
        self.save(path, obj)
        return path

    def revise(self, output, entry=None, expected=0, fingerprint=None):
        return self.command("report_profile.py", "revise", self.profile, "--entry", entry or self.entry(),
                            "--expected-sha256", fingerprint or self.digest(self.profile), "--output", output, expected=expected)

    def test_private_profile_init_revise_inspect_preserves_history_and_hides_values(self):
        self.init_profile()
        original = self.profile.read_bytes()
        first = self.root / "private v1.json"
        response = self.revise(first)
        self.assertFalse(response["values_disclosed"])
        self.assertEqual(self.profile.read_bytes(), original)
        self.profile = first
        first_bytes = first.read_bytes()
        second = self.root / "private v2.json"
        self.revise(second, self.entry("corrected confirmed preference", confirmation_ref="synthetic-user-message-2"))
        current = json.loads(second.read_text())
        self.assertEqual([e["revision"] for e in current["entries"]], [1, 2])
        self.assertEqual(current["parent_snapshot_sha256"], self.digest(first))
        self.assertEqual(first.read_bytes(), first_bytes)
        checked = self.command("report_profile.py", "inspect", second)
        self.assertEqual(checked["current_entries"], [{"id": "style", "revision": 2, "type": "preference"}])
        visible = self.command("report_profile.py", "inspect", second, "--show-values")
        self.assertEqual(visible["current_entries"][0]["value"], "corrected confirmed preference")

    def test_profile_stale_hash_missing_confirmation_and_type_change_rejected(self):
        self.init_profile()
        output = self.root / "rejected.json"
        self.revise(output, fingerprint="0" * 64, expected=2)
        self.assertFalse(output.exists())
        self.revise(output, self.entry(confirmation_ref=""), expected=2)
        self.assertFalse(output.exists())
        self.revise(output)
        self.profile = output
        newer = self.root / "newer.json"
        self.revise(newer, self.entry(type="experience"), expected=2)
        self.assertFalse(newer.exists())

    def test_profiles_never_overwrite_or_enter_run_or_package(self):
        self.init_profile()
        before = self.profile.read_bytes()
        self.revise(self.profile, expected=2)
        self.assertEqual(self.profile.read_bytes(), before)
        run = self.root / "run"
        run.mkdir()
        (run / "run.json").write_text("{}")
        for target in (run / "private.json", self.package / "private.json"):
            self.command("report_profile.py", "init", target, "--profile-id", "synthetic", expected=2)
            self.assertFalse(target.exists())

    def test_profile_invalid_history_and_boolean_revision_rejected(self):
        self.init_profile()
        for revision in (True, 0, 2):
            record = {"contract_version": "0.1", "profile_id": "synthetic", "entries": [
                {"id": "p", "revision": revision, "type": "preference", "value": "x", "scope": "x", "confirmation_ref": "m"}]}
            self.save(self.profile, record)
            self.command("report_profile.py", "inspect", self.profile, expected=2)

    def test_existing_contract_profile_is_readable_and_readonly(self):
        self.profile = self.root / "old-example.json"
        shutil.copyfile(PROJECT / "skill-src/shared/assets/examples/profile.json", self.profile)
        before = self.profile.read_bytes()
        result = self.command("report_profile.py", "inspect", self.profile)
        self.assertEqual(len(result["current_entries"]), 1)
        self.assertEqual(self.profile.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
