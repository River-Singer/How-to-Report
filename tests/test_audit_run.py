"""Actual audit helper lifecycle using only synthetic temporary local files."""

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from urllib.parse import unquote


PROJECT = Path(__file__).resolve().parents[1]
SOURCE = PROJECT / "skill-src" / "report-audit"
VALIDATOR = PROJECT / "skill-src" / "shared" / "scripts" / "validate_run.py"


class AuditRunTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="report-audit-run-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.package = self.root / "standalone-audit"
        (self.package / "scripts").mkdir(parents=True)
        shutil.copyfile(SOURCE / "scripts" / "audit_run.py", self.package / "scripts" / "audit_run.py")
        shutil.copyfile(VALIDATOR, self.package / "scripts" / "validate_run.py")
        shutil.copyfile(VALIDATOR.with_name("write_boundary.py"), self.package / "scripts" / "write_boundary.py")
        shutil.copytree(SOURCE / "assets" / "audit-run", self.package / "assets" / "audit-run")
        self.cwd = self.root / "unrelated"
        self.cwd.mkdir()
        self.target = self.root / "report #1 100% 项目.md"
        self.target.write_text("Synthetic fixture: a pilot is planned, not yet complete.\n", encoding="utf-8")
        self.original_target = self.target.read_bytes()
        self.run = self.root / "audit"

    def command(self, *arguments, expected=0, python_flags=()):
        result = subprocess.run(
            [sys.executable, *python_flags, str(self.package / "scripts" / "audit_run.py"), *map(str, arguments)],
            cwd=self.cwd, capture_output=True, text=True, encoding="utf-8",
        )
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return json.loads(result.stdout)

    def initialize(self, *arguments):
        return self.command("init", self.run, "--target", self.target, "--run-id", "synthetic-audit", *arguments)

    def read(self):
        return json.loads((self.run / "run.json").read_text(encoding="utf-8"))

    def test_other_installed_skill_marker_refuses_before_creating_run(self):
        other = self.root / "other-installed-skill"
        other.mkdir()
        (other / "bundle-manifest.json").write_text("{}", encoding="utf-8")
        output = other / "new-parent" / "audit"
        before = self.snapshot(other)
        self.command("init", output, "--target", self.target, "--run-id", "synthetic", expected=2)
        self.assertEqual(before, self.snapshot(other))
        self.assertFalse(output.parent.exists())

    def write(self, record):
        (self.run / "run.json").write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    @staticmethod
    def snapshot(directory):
        return {path.relative_to(directory).as_posix(): (path.read_bytes(), path.stat().st_mtime_ns)
                for path in directory.rglob("*") if path.is_file()}

    def test_initial_state_is_honest_and_uses_actual_templates_and_exact_revision(self):
        result = self.initialize("--target-id", "report-draft", "--target-revision", "4")
        record = self.read()
        self.assertTrue(result["valid"], result)
        self.assertEqual(result["scope"], "structure_and_declared_references_only")
        self.assertEqual(result["content_audit"], "not_performed_by_this_command")
        self.assertEqual(record["mode"], "audit")
        self.assertEqual(record["work_status"], "in_progress")
        target = {"id": "report-draft", "revision": 4}
        self.assertEqual(record["checks"][0]["target"], target)
        self.assertEqual(record["checks"][0]["status"], "not_run")
        self.assertEqual(record["artifacts"][0]["uses"], [target])
        self.assertEqual(record["artifacts"][0]["ref"], "audit.md")
        self.assertEqual(record["notes_ref"], "run.md")
        self.assertEqual(Path(unquote(record["sources"][0]["ref"])), self.target.resolve())
        self.assertEqual(record["sources"][0]["content_hash"], hashlib.sha256(self.original_target).hexdigest())
        for filename in ("run.md", "audit.md"):
            self.assertEqual((self.run / filename).read_bytes(),
                             (self.package / "assets" / "audit-run" / filename).read_bytes())
        self.assertTrue((self.run / record["checks"][0]["detail_ref"]).is_file())
        self.assertFalse({"conclusion", "independence", "events_ref", "semantic_ref", "tasks_ref"} & record.keys())
        self.assertEqual(self.target.read_bytes(), self.original_target)

    def test_check_identifies_the_record_and_leaves_run_target_and_package_unchanged(self):
        self.initialize()
        before = self.snapshot(self.root)
        result = self.command("check", self.run)
        self.assertTrue(result["valid"], result)
        self.assertEqual(result["audit_directory"], str(self.run.resolve()))
        self.assertEqual(result["run_id"], "synthetic-audit")
        self.assertEqual(result["run_record_sha256"], hashlib.sha256((self.run / "run.json").read_bytes()).hexdigest())
        self.assertEqual(self.read()["work_status"], "in_progress")
        self.assertEqual(self.read()["checks"][0]["status"], "not_run")
        self.assertEqual(self.snapshot(self.root), before)
        self.assertFalse((self.package / "scripts" / "__pycache__").exists())

    def test_isolated_python_init_and_check_after_package_relocation(self):
        relocated = self.root / "relocated audit"
        self.package.rename(relocated)
        self.package = relocated
        # A cwd module must not substitute for the validator inside the package.
        (self.cwd / "validate_run.py").write_text("raise RuntimeError('wrong validator from cwd')\n", encoding="utf-8")
        package_before = self.snapshot(self.package)
        flags = ("-I", "-X", "utf8")  # No -B: the helper itself must prevent cache writes.
        initialized = self.command("init", self.run, "--target", self.target,
                                   "--run-id", "isolated-audit", python_flags=flags)
        self.assertTrue(initialized["valid"], initialized)
        run_before = self.snapshot(self.run)
        checked = self.command("check", self.run, python_flags=flags)
        self.assertTrue(checked["valid"], checked)
        self.assertEqual(checked["run_id"], "isolated-audit")
        self.assertEqual(checked["audit_directory"], str(self.run.resolve()))
        self.assertEqual(checked["scope"], "structure_and_declared_references_only")
        self.assertEqual(self.read()["checks"][0]["status"], "not_run")
        self.assertEqual(self.target.read_bytes(), self.original_target)
        self.assertEqual(self.snapshot(self.run), run_before)
        self.assertEqual(self.snapshot(self.package), package_before)
        self.assertFalse((self.package / "scripts" / "__pycache__").exists())

    def test_completed_recorded_review_retains_failed_content_check(self):
        self.initialize()
        # This is a synthetic declaration fixture, not a model content audit.
        (self.run / "audit.md").write_text("Synthetic recorded finding: the fixture's claimed completion lacks evidence.\n", encoding="utf-8")
        record = self.read()
        record["work_status"] = "completed"
        record["checks"][0].update({"status": "fail", "method": "synthetic fixture review", "scope": "fixture claim only"})
        self.write(record)
        before = self.snapshot(self.root)
        result = self.command("check", self.run)
        self.assertTrue(result["valid"], result)
        self.assertEqual(self.read()["checks"][0]["status"], "fail")
        self.assertEqual(self.snapshot(self.root), before)

    def test_init_refuses_existing_run_directory_empty_directory_and_file(self):
        self.initialize()
        empty = self.root / "empty-workspace"
        empty.mkdir()
        existing_file = self.root / "previous.txt"
        existing_file.write_text("prior work", encoding="utf-8")
        before = self.snapshot(self.root)
        for destination in (self.run, empty, existing_file):
            with self.subTest(destination=destination):
                result = self.command("init", destination, "--target", self.target, "--run-id", "later", expected=2)
                self.assertFalse(result["valid"])
                self.assertIn("refusing to overwrite", result["errors"][0])
        self.assertEqual(self.snapshot(self.root), before)
        self.assertEqual(list(empty.iterdir()), [])

    def test_missing_or_nonfile_target_fails_without_creating_workspace(self):
        for target in (self.root / "absent.md", self.cwd):
            with self.subTest(target=target):
                self.command("init", self.run, "--target", target, "--run-id", "bad", expected=2)
                self.assertFalse(self.run.exists())
        self.assertEqual(self.target.read_bytes(), self.original_target)

    def test_invalid_cli_identity_or_revision_fails_before_writing(self):
        for flags in (("--run-id", " "), ("--target-id", " "), ("--target-revision", "0"),
                      ("--target-revision", "-1"), ("--target-revision", "True")):
            with self.subTest(flags=flags):
                result = subprocess.run(
                    [sys.executable, str(self.package / "scripts" / "audit_run.py"), "init", str(self.run),
                     "--target", str(self.target), "--run-id", "fixture", *flags],
                    cwd=self.cwd, capture_output=True, text=True,
                )
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                self.assertFalse(self.run.exists())

    def test_init_refuses_installed_package_as_output_location(self):
        before = self.snapshot(self.package)
        destination = self.package / "assets" / "new-run"
        result = self.command("init", destination, "--target", self.target, "--run-id", "bad-location", expected=2)
        self.assertIn("outside the installed Skill", result["errors"][0])
        self.assertFalse(destination.exists())
        self.assertEqual(self.snapshot(self.package), before)

    def test_missing_template_fails_before_creating_workspace(self):
        (self.package / "assets" / "audit-run" / "audit.md").unlink()
        self.command("init", self.run, "--target", self.target, "--run-id", "missing-template", expected=2)
        self.assertFalse(self.run.exists())

    def test_target_identity_collision_does_not_change_the_requested_identity(self):
        self.initialize("--target-id", "audit-report")
        record = self.read()
        self.assertEqual(record["sources"][0]["id"], "audit-report")
        self.assertEqual(record["checks"][0]["target"]["id"], "audit-report")
        self.assertEqual(record["artifacts"][0]["id"], "audit-report-output")

    def test_valid_generation_run_cannot_substitute_for_audit_self_check(self):
        self.initialize()
        record = self.read()
        record["mode"] = "create"
        self.write(record)
        before = self.snapshot(self.root)
        result = self.command("check", self.run, expected=1)
        self.assertFalse(result["valid"])
        self.assertIn("audit self-check requires mode audit", "\n".join(result["errors"]))
        self.assertEqual(self.snapshot(self.root), before)

    def test_observed_malformed_records_fail_without_silent_repairs(self):
        self.initialize()
        original = self.read()
        variants = []
        sentinel = deepcopy(original)
        sentinel["sources"][0]["content_hash"] = "not-recorded-this-run"
        variants.append((sentinel, "expected a SHA-256 hex digest"))
        section_path = deepcopy(original)
        section_path["checks"][0]["detail_ref"] = "audit.md §2–§4、§6"
        variants.append((section_path, "local file does not exist"))
        missing_arrays = deepcopy(original)
        del missing_arrays["sources"]
        del missing_arrays["artifacts"]
        del missing_arrays["checks"]
        variants.append((missing_arrays, "expected an array"))
        nonstandard = deepcopy(original)
        nonstandard["checks"] = [{"id": "wrong-check", "result": "pass", "note": "claimed checked"}]
        variants.append((nonstandard, "run.json.checks[0].target"))
        wrong_revision = deepcopy(original)
        wrong_revision["checks"][0]["target"]["revision"] = 2
        variants.append((wrong_revision, "unknown exact object version audit-target@2"))
        for record, error in variants:
            with self.subTest(error=error):
                self.write(record)
                before = self.snapshot(self.root)
                result = self.command("check", self.run, expected=1)
                self.assertFalse(result["valid"])
                self.assertIn(error, "\n".join(result["errors"]))
                if record is nonstandard:
                    for field in ("status", "detail_ref"):
                        self.assertIn("run.json.checks[0]." + field, "\n".join(result["errors"]))
                if record is missing_arrays:
                    for field in ("sources", "artifacts", "checks"):
                        self.assertIn("run.json." + field, "\n".join(result["errors"]))
                self.assertEqual(self.snapshot(self.root), before)

    def test_declared_pass_needs_method_and_scope_even_with_existing_detail(self):
        self.initialize()
        record = self.read()
        record["checks"][0]["status"] = "pass"
        self.write(record)
        result = self.command("check", self.run, expected=1)
        errors = "\n".join(result["errors"])
        self.assertIn("run.json.checks[0].method", errors)
        self.assertIn("run.json.checks[0].scope", errors)

    def test_changed_target_fails_hash_check_without_refreshing_record(self):
        self.initialize()
        before = self.snapshot(self.run)
        self.target.write_text("Synthetic revised target\n", encoding="utf-8")
        result = self.command("check", self.run, expected=1)
        self.assertIn("local file bytes differ from declared hash", "\n".join(result["errors"]))
        self.assertEqual(self.snapshot(self.run), before)

    def test_malformed_json_is_invalid_and_missing_record_is_io_failure(self):
        self.initialize()
        (self.run / "run.json").write_text('{"run_id": "broken",', encoding="utf-8")
        result = self.command("check", self.run, expected=1)
        self.assertIn("invalid JSON", "\n".join(result["errors"]))
        result = self.command("check", self.root / "absent-run", expected=2)
        self.assertFalse(result["valid"])


if __name__ == "__main__":
    unittest.main()
