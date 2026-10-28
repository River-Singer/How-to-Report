"""Reporting Run lifecycle tests with synthetic files, no model or case execution."""

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
from unittest.mock import patch


PROJECT = Path(__file__).resolve().parents[1]
SOURCE = PROJECT / "skill-src" / "how-to-report"
VALIDATOR = PROJECT / "skill-src" / "shared" / "scripts" / "validate_run.py"


class ReportRunTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="report-run-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.package = self.root / "standalone-report"
        (self.package / "scripts").mkdir(parents=True)
        shutil.copyfile(SOURCE / "scripts" / "report_run.py", self.package / "scripts" / "report_run.py")
        shutil.copyfile(VALIDATOR, self.package / "scripts" / "validate_run.py")
        shutil.copytree(SOURCE / "assets" / "report-run", self.package / "assets" / "report-run")
        self.cwd = self.root / "unrelated"
        self.cwd.mkdir()
        self.target = self.root / "report #1 100% 项目.md"
        self.target.write_text("Synthetic old report: pilot planned, not completed.\n", encoding="utf-8")
        self.source = self.root / "材料 #2 50%.csv"
        self.source.write_bytes(b"PRIVATE_INPUT_BODY\x00\xff\n")
        self.run = self.root / "Run #3 20% 汇报"

    def command(self, *arguments, expected=0, python_flags=()):
        process = subprocess.run(
            [sys.executable, *python_flags, str(self.package / "scripts" / "report_run.py"), *map(str, arguments)],
            cwd=self.cwd, capture_output=True, text=True, encoding="utf-8",
        )
        self.assertEqual(process.returncode, expected, process.stdout + process.stderr)
        self.assertNotIn("PRIVATE_INPUT_BODY", process.stdout + process.stderr)
        return json.loads(process.stdout)

    def initialize(self, *arguments, mode="create", expected=0):
        return self.command("init", self.run, "--run-id", "synthetic-report", "--mode", mode, *arguments, expected=expected)

    def read(self):
        return json.loads((self.run / "run.json").read_text(encoding="utf-8"))

    def write(self, record):
        (self.run / "run.json").write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    @staticmethod
    def snapshot(directory):
        return {path.relative_to(directory).as_posix(): (path.read_bytes(), path.stat().st_mtime_ns)
                for path in directory.rglob("*") if path.is_file()}

    def load_helper(self):
        specification = importlib.util.spec_from_file_location("report_run_under_test", self.package / "scripts" / "report_run.py")
        module = importlib.util.module_from_spec(specification)
        original_path, original_bytecode = sys.path[:], sys.dont_write_bytecode
        try:
            specification.loader.exec_module(module)
        finally:
            sys.path[:] = original_path
            sys.dont_write_bytecode = original_bytecode
        return module

    def test_each_mode_starts_with_only_real_sources_and_no_result_claims(self):
        for mode in ("create", "revise", "analyze-first"):
            with self.subTest(mode=mode):
                self.run = self.root / mode
                arguments = ("--target", self.target) if mode == "revise" else ()
                result = self.initialize(*arguments, mode=mode)
                record = self.read()
                self.assertTrue(result["valid"])
                self.assertEqual(record["mode"], mode)
                self.assertEqual(record["work_status"], "in_progress")
                self.assertEqual(record["artifacts"], [])
                self.assertEqual(record["checks"], [])
                self.assertEqual(set(record), {"contract_version", "run_id", "mode", "work_status", "notes_ref", "sources", "artifacts", "checks"})
                self.assertEqual(result["scope"], "structure_and_declared_references_only")
                self.assertEqual(result["content_work"], "not_performed_by_this_command")
                self.assertEqual(result["origin_currentness"], "not_assessed")
                self.assertEqual((self.run / "run.md").read_bytes(), (self.package / "assets" / "report-run" / "run.md").read_bytes())
                if mode == "revise":
                    self.assertEqual(record["sources"][0]["role"], "revision_target")
                    self.assertEqual(record["sources"][0]["id"], "revision-target")
                else:
                    self.assertEqual(record["sources"], [])
                    self.assertEqual(set(path.name for path in self.run.iterdir()), {"run.json", "run.md"})

    def test_required_target_and_forbidden_other_mode_targets_preflight(self):
        self.initialize(mode="revise", expected=2)
        self.assertFalse(self.run.exists())
        for mode in ("create", "analyze-first"):
            self.initialize("--target", self.target, mode=mode, expected=2)
            self.assertFalse(self.run.exists())

    def test_explicit_binary_sources_are_exact_copies_with_separate_origin_metadata(self):
        before = {path: path.read_bytes() for path in (self.source, self.target)}
        self.initialize("--target", self.target, "--source", self.source, mode="revise")
        sources = self.read()["sources"]
        self.assertEqual([source["id"] for source in sources], ["revision-target", "source-001"])
        self.assertEqual([source["role"] for source in sources], ["revision_target", "supporting_material"])
        for source, origin in zip(sources, (self.target, self.source)):
            with self.subTest(source=source["id"]):
                self.assertEqual(source["revision"], 1)
                self.assertEqual(source["origin"], {"path": str(origin.resolve()), "filename": origin.name})
                self.assertEqual((self.run / source["ref"]).read_bytes(), before[origin])
                self.assertEqual(source["content_hash"], hashlib.sha256(before[origin]).hexdigest())
                self.assertEqual(origin.read_bytes(), before[origin])
                self.assertFalse(Path(source["ref"]).is_absolute())
                self.assertTrue((self.run / source["ref"]).resolve().is_relative_to(self.run))

    def test_safe_snapshot_names_preserve_only_short_ascii_extensions(self):
        inputs = [self.root / name for name in ("same.md", "a# %.知识", "noextension", "many.abcdefghijklmnopq", "last.MD")]
        for index, path in enumerate(inputs):
            path.write_bytes(bytes([index]))
        self.initialize(*[value for path in inputs for value in ("--source", path)])
        self.assertEqual([source["ref"] for source in self.read()["sources"]],
                         ["inputs/source-001.md", "inputs/source-002.bin", "inputs/source-003.bin", "inputs/source-004.bin", "inputs/source-005.MD"])

    def test_duplicate_resolved_inputs_are_rejected_before_any_write(self):
        for arguments, mode in ((("--source", self.source, "--source", self.source.parent / "." / self.source.name), "create"),
                                (("--target", self.target, "--source", self.target), "revise")):
            with self.subTest(mode=mode):
                result = self.initialize(*arguments, mode=mode, expected=2)
                self.assertIn("duplicate", result["errors"][0])
                self.assertFalse(self.run.exists())

    def test_changed_or_removed_origins_do_not_change_or_invalidate_captured_bytes(self):
        self.initialize("--target", self.target, "--source", self.source, mode="revise")
        before = self.snapshot(self.run)
        self.source.write_bytes(b"changed original")
        self.target.unlink()
        result = self.command("inspect", self.run)
        self.assertTrue(result["valid"])
        self.assertEqual(result["origin_currentness"], "not_assessed")
        self.assertEqual(self.snapshot(self.run), before)

    def test_snapshot_tampering_or_missing_snapshot_fails_without_refresh(self):
        self.initialize("--source", self.source)
        source = self.read()["sources"][0]
        snapshot = self.run / source["ref"]
        snapshot.write_bytes(b"changed snapshot")
        result = self.command("inspect", self.run, expected=1)
        self.assertTrue(any("hash" in error for error in result["errors"]))
        self.assertEqual(self.read()["sources"][0]["content_hash"], source["content_hash"])
        snapshot.unlink()
        result = self.command("inspect", self.run, expected=1)
        self.assertTrue(any("does not exist" in error for error in result["errors"]))

    def test_inspection_preserves_exact_declared_status_versions_pointers_and_all_files(self):
        self.initialize("--source", self.source)
        record = self.read()
        record["work_status"] = "completed"
        (self.run / "draft.md").write_text("Synthetic draft\n", encoding="utf-8")
        (self.run / "check.md").write_text("Unresolved synthetic check\n", encoding="utf-8")
        record["artifacts"] = [{"id": "draft", "revision": 2, "ref": "draft.md"}, {"id": "draft", "revision": 1, "ref": "draft.md"}]
        record["checks"] = [{"id": "quality", "target": {"id": "draft", "revision": 1}, "status": "fail", "detail_ref": "check.md"}]
        for field, filename, body in (("semantic_ref", "semantic.json", {"nodes": []}), ("tasks_ref", "tasks.json", {"tasks": []})):
            record[field] = filename
            (self.run / filename).write_text(json.dumps({"contract_version": "0.1", "run_id": record["run_id"], **body}), encoding="utf-8")
        record["events_ref"] = "events.jsonl"
        (self.run / "events.jsonl").write_text("", encoding="utf-8")
        self.write(record)
        before = self.snapshot(self.root)
        result = self.command("inspect", self.run)
        self.assertEqual(result["run_id"], record["run_id"])
        self.assertEqual(result["mode"], "create")
        self.assertEqual(result["work_status"], "completed")
        self.assertEqual([item["revision"] for item in result["artifacts"]], [2, 1])
        self.assertEqual(result["checks"], record["checks"])
        self.assertEqual(result["record_refs"], {field: record[field] for field in ("notes_ref", "semantic_ref", "tasks_ref", "events_ref")})
        self.assertEqual(result["run_record_sha256"], hashlib.sha256((self.run / "run.json").read_bytes()).hexdigest())
        self.assertEqual(self.snapshot(self.root), before)
        self.assertFalse((self.package / "scripts" / "__pycache__").exists())

    def test_all_check_statuses_are_reported_without_executing_detail_files(self):
        self.initialize("--source", self.source)
        record = self.read()
        detail = self.run / "danger.py"
        detail.write_text("raise RuntimeError('must never run')\n", encoding="utf-8")
        record["checks"] = [{"id": status, "target": {"id": "source-001", "revision": 1}, "status": status,
                             "detail_ref": "danger.py", "method": "declared test method", "scope": "synthetic fixture only"}
                            for status in ("not_run", "pass", "fail", "not_assessable")]
        self.write(record)
        result = self.command("inspect", self.run)
        self.assertEqual([check["status"] for check in result["checks"]], ["not_run", "pass", "fail", "not_assessable"])
        self.assertEqual(self.read(), record)

    def test_existing_destinations_never_change(self):
        for kind in ("file", "empty-directory", "run"):
            with self.subTest(kind=kind):
                self.run = self.root / kind
                if kind == "file":
                    self.run.write_text("keep", encoding="utf-8")
                elif kind == "empty-directory":
                    self.run.mkdir()
                else:
                    self.initialize()
                before = self.snapshot(self.root)
                self.initialize(expected=2)
                self.assertEqual(self.snapshot(self.root), before)

    def test_dangling_destination_link_is_rejected_when_links_are_available(self):
        try:
            self.run.symlink_to(self.root / "missing-link-target", target_is_directory=True)
        except OSError as exc:
            self.skipTest(f"symbolic links unavailable: {exc}")
        self.initialize(expected=2)
        self.assertTrue(self.run.is_symlink())
        self.assertFalse((self.root / "missing-link-target").exists())

    def test_invalid_destinations_and_package_subdirectory_are_rejected(self):
        for destination in (self.package / "new-run", self.root / "missing-parent" / "run", self.source / "run", "//unavailable-server/share/run"):
            with self.subTest(destination=destination):
                before = self.snapshot(self.root)
                self.command("init", destination, "--run-id", "fixture", "--mode", "create", expected=2)
                self.assertEqual(self.snapshot(self.root), before)

    def test_missing_nonfile_and_unc_inputs_are_rejected_before_output(self):
        for source in (self.root / "missing", self.cwd, "//unavailable-server/share/file.md"):
            with self.subTest(source=source):
                self.initialize("--source", self.source, "--source", source, expected=2)
                self.assertFalse(self.run.exists())
        self.initialize("--target", self.cwd, mode="revise", expected=2)
        self.assertFalse(self.run.exists())

    def test_invalid_cli_arguments_exit_two_without_output_directory(self):
        for arguments in (("init", self.run, "--run-id", " ", "--mode", "create"),
                          ("init", self.run, "--run-id", "fixture", "--mode", "audit"),
                          ("init", self.run, "--run-id", "fixture"),
                          ("inspect", self.run, "--changed", "source-001@1")):
            with self.subTest(arguments=arguments):
                result = subprocess.run([sys.executable, str(self.package / "scripts" / "report_run.py"), *map(str, arguments)],
                                        cwd=self.cwd, capture_output=True)
                self.assertEqual(result.returncode, 2)
                self.assertFalse(self.run.exists())

    def test_missing_or_invalid_template_fails_preflight(self):
        template = self.package / "assets" / "report-run" / "run.json"
        for content in ("[]", "{", '{"contract_version":"future"}'):
            template.write_text(content, encoding="utf-8")
            self.initialize(expected=2)
            self.assertFalse(self.run.exists())
        template.unlink()
        self.initialize(expected=2)
        self.assertFalse(self.run.exists())

    def test_inspection_rejects_audit_and_preserves_saved_work_state(self):
        self.initialize()
        record = self.read()
        record.update(mode="audit", work_status="blocked")
        self.write(record)
        before = self.snapshot(self.run)
        result = self.command("inspect", self.run, expected=1)
        self.assertEqual(result["mode"], "audit")
        self.assertEqual(result["work_status"], "blocked")
        self.assertEqual(self.snapshot(self.run), before)

    def test_malformed_records_and_list_shapes_return_invalid_without_crash(self):
        self.initialize()
        base = self.read()
        invalid_records = [[], None, {**base, "mode": []}, {**base, "sources": {}}, {**base, "checks": [None, []]},
                           {**base, "artifacts": [{"id": [], "revision": [], "ref": []}]},
                           {**base, "checks": [{"id": {}, "target": [], "status": [], "detail_ref": []}]}]
        for record in invalid_records:
            with self.subTest(record=record):
                self.write(deepcopy(record))
                before = self.snapshot(self.run)
                result = self.command("inspect", self.run, expected=1)
                self.assertFalse(result["valid"])
                self.assertEqual(self.snapshot(self.run), before)
        for content in (b"{", b'\xff', b'{"run_id":"a","run_id":"b"}'):
            (self.run / "run.json").write_bytes(content)
            self.command("inspect", self.run, expected=1)

    def test_missing_run_or_record_is_an_io_failure(self):
        self.command("inspect", self.run, expected=2)
        self.run.mkdir()
        self.command("inspect", self.run, expected=2)
        (self.run / "run.json").mkdir()
        self.command("inspect", self.run, expected=2)

    def test_record_change_during_inspection_is_detected_and_hash_stays_bound_to_summary(self):
        self.initialize()
        helper = self.load_helper()
        original = (self.run / "run.json").read_bytes()
        actual_validate = helper.validate_run

        def concurrent_validation(directory, changed):
            record = self.read()
            record["work_status"] = "completed"
            self.write(record)
            return actual_validate(directory, changed)

        with patch.object(helper, "validate_run", side_effect=concurrent_validation):
            result = helper.inspect_run(self.run)
        self.assertFalse(result["valid"])
        self.assertEqual(result["work_status"], "in_progress")
        self.assertEqual(result["run_record_sha256"], hashlib.sha256(original).hexdigest())
        self.assertTrue(any("changed during" in error for error in result["errors"]))

    def test_hash_binds_captured_bytes_when_origin_changes_before_snapshot_write(self):
        helper = self.load_helper()
        original = self.source.read_bytes()
        actual_read = Path.read_bytes

        def changing_read(path):
            captured = actual_read(path)
            if path == self.source:
                path.write_bytes(b"later original bytes")
            return captured

        with patch.object(Path, "read_bytes", changing_read):
            result = helper.initialize(self.run, "fixture", "create", [self.source])
        source = self.read()["sources"][0]
        self.assertTrue(result["valid"])
        self.assertEqual((self.run / source["ref"]).read_bytes(), original)
        self.assertEqual(source["content_hash"], hashlib.sha256(original).hexdigest())
        self.assertNotEqual(self.source.read_bytes(), original)

    def test_partial_io_failure_keeps_written_snapshot_and_returns_non_success(self):
        helper = self.load_helper()
        actual_open = Path.open

        def fail_record(path, *args, **kwargs):
            if path == self.run / "run.json" and args and args[0] == "xb":
                raise OSError("synthetic write failure")
            return actual_open(path, *args, **kwargs)

        with patch.object(Path, "open", fail_record), patch("builtins.print") as output:
            exit_code = helper.main(["init", str(self.run), "--run-id", "fixture", "--mode", "create", "--source", str(self.source)])
        self.assertEqual(exit_code, 2)
        self.assertFalse(json.loads(output.call_args.args[0])["valid"])
        self.assertEqual((self.run / "inputs" / "source-001.csv").read_bytes(), self.source.read_bytes())
        self.assertTrue((self.run / "run.md").is_file())
        self.assertFalse((self.run / "run.json").exists())
        self.initialize(expected=2)

    def test_relocated_isolated_python_uses_same_package_validator_and_no_cache(self):
        relocated = self.root / "relocated # 30% 独立"
        self.package.rename(relocated)
        self.package = relocated
        (self.cwd / "validate_run.py").write_text("raise RuntimeError('wrong cwd module')\n", encoding="utf-8")
        result = self.command("init", self.run, "--run-id", "fixture", "--mode", "revise", "--target", self.target,
                              "--source", self.source, python_flags=("-I",))
        self.assertTrue(result["valid"])
        before = self.snapshot(self.root)
        self.command("inspect", self.run, python_flags=("-I",))
        self.assertEqual(self.snapshot(self.root), before)
        self.assertFalse((self.package / "scripts" / "__pycache__").exists())


if __name__ == "__main__":
    unittest.main()
