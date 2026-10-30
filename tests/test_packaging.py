"""Behavior tests with isolated sources; never edit real generated packages."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / "tools" / "package_skills.py"
SPEC = importlib.util.spec_from_file_location("package_skills", SCRIPT)
assert SPEC and SPEC.loader
packager = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(packager)


class PackagingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="report-package-tests-")
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.project = self.base / "checkout"
        self.project.mkdir()
        (self.project / "tools").mkdir()
        shutil.copyfile(SCRIPT, self.project / "tools" / "package_skills.py")
        self.cwd = self.base / "unrelated"
        self.cwd.mkdir()
        self.source = self.project / "skill-src"
        self.shared = self.source / "shared"
        for relative in packager.CORE_REFERENCES:
            self.write(self.shared / relative, "# Shared contract\n")
        self.write(self.shared / "assets" / "value.json", '{"answer": 42}\n')
        self.write(
            self.shared / "scripts" / "validate_run.py",
            "import json\nfrom pathlib import Path\nimport sys\n"
            "payload = Path(__file__).resolve().parents[1] / 'assets' / 'value.json'\n"
            "run = json.loads((Path(sys.argv[1]) / 'run.json').read_text())\n"
            "print(json.dumps({'answer': json.loads(payload.read_text())['answer'], 'run': run['id']}))\n",
        )
        for skill in packager.SKILLS:
            self.write(
                self.source / skill / "SKILL.md",
                f"---\nname: {skill}\ndescription: Fixture package for relocation tests\n---\n"
                + "\n".join(f"Read [contract]({path}) when needed." for path in packager.CORE_REFERENCES)
                + "\nRun [validator](scripts/validate_run.py).\n"
                + "Read [local method](references/method.md).\n",
            )
            self.write(self.source / skill / "references" / "method.md", "[Shared data](../assets/value.json)\n")

    @staticmethod
    def write(path: Path, data: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(data, encoding="utf-8")

    def command(self, command: str, success: bool = True) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(
            [sys.executable, str(self.project / "tools" / "package_skills.py"), command],
            cwd=self.cwd, capture_output=True, text=True,
        )
        if success:
            self.assertEqual(result.returncode, 0, result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0, result.stdout)
        return result

    def snapshot(self) -> dict[str, bytes]:
        output = self.project / "skills"
        return {path.relative_to(output).as_posix(): path.read_bytes() for path in output.rglob("*") if path.is_file()}

    def test_relocation_executes_helper_without_checkout_or_sibling(self) -> None:
        self.command("build")
        run = self.base / "user-run"
        self.write(run / "run.json", '{"id": "relocated"}')
        for skill in packager.SKILLS:
            destination = self.base / ("standalone-" + skill)
            shutil.copytree(self.project / "skills" / skill, destination)
        self.assertEqual(self.project.resolve().parent, self.base.resolve())
        shutil.rmtree(self.project)
        for skill in packager.SKILLS:
            result = subprocess.run(
                [sys.executable, str(self.base / ("standalone-" + skill) / "scripts" / "validate_run.py"), str(run)],
                cwd=self.cwd, capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout), {"answer": 42, "run": "relocated"})

    def test_manifest_and_shared_bytes_are_complete(self) -> None:
        self.command("build")
        for skill in packager.SKILLS:
            package = self.project / "skills" / skill
            manifest = json.loads((package / packager.MANIFEST).read_text())
            self.assertEqual(manifest["skill_name"], skill)
            self.assertEqual(manifest["package_version"], "0.6.0")
            self.assertEqual(manifest["supported_contract_version"], "0.1")
            self.assertNotIn(packager.MANIFEST, manifest["files"])
            for relative, digest in manifest["files"].items():
                self.assertEqual(hashlib.sha256((package / relative).read_bytes()).hexdigest(), digest)
            for path in self.shared.rglob("*"):
                if path.is_file():
                    self.assertEqual((package / path.relative_to(self.shared)).read_bytes(), path.read_bytes())

    def test_relocated_package_executes_real_audit_init_and_check(self) -> None:
        actual_source = SCRIPT.parents[1] / "skill-src"
        # Exercise the real shared runtime closure, including new helpers.
        shutil.copytree(actual_source / "shared" / "scripts", self.shared / "scripts",
                        dirs_exist_ok=True, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        audit_source = self.source / "report-audit"
        (audit_source / "scripts").mkdir()
        shutil.copyfile(actual_source / "report-audit" / "scripts" / "audit_run.py",
                        audit_source / "scripts" / "audit_run.py")
        shutil.copytree(actual_source / "report-audit" / "assets" / "audit-run",
                        audit_source / "assets" / "audit-run")
        self.command("build")
        self.command("check")
        destination = self.base / "standalone-report-audit"
        shutil.copytree(self.project / "skills" / "report-audit", destination)
        package_before = {path.relative_to(destination): path.read_bytes()
                          for path in destination.rglob("*") if path.is_file()}
        # Remove the temporary checkout and its generator package entirely.
        self.assertEqual(self.project.resolve().parent, self.base.resolve())
        shutil.rmtree(self.project)
        target = self.base / "external-report.md"
        target.write_text("Synthetic report fixture.\n", encoding="utf-8")
        target_before = target.read_bytes()
        run = self.base / "user-audit"
        helper = destination / "scripts" / "audit_run.py"
        for arguments in (("init", str(run), "--target", str(target), "--run-id", "relocated-audit"),
                          ("check", str(run))):
            result = subprocess.run([sys.executable, str(helper), *arguments], cwd=self.cwd,
                                    capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            checked = json.loads(result.stdout)
            self.assertTrue(checked["valid"], checked)
            self.assertEqual(checked["audit_directory"], str(run.resolve()))
            self.assertEqual(checked["scope"], "structure_and_declared_references_only")
        record = json.loads((run / "run.json").read_text(encoding="utf-8"))
        self.assertEqual(record["checks"][0]["status"], "not_run")
        self.assertEqual(target.read_bytes(), target_before)
        self.assertEqual(package_before, {path.relative_to(destination): path.read_bytes()
                                         for path in destination.rglob("*") if path.is_file()})

    def test_relocated_package_executes_real_report_init_and_inspect(self) -> None:
        actual_source = SCRIPT.parents[1] / "skill-src"
        # Exercise the real shared runtime closure, including new helpers.
        shutil.copytree(actual_source / "shared" / "scripts", self.shared / "scripts",
                        dirs_exist_ok=True, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        report_source = self.source / "how-to-report"
        (report_source / "scripts").mkdir()
        shutil.copyfile(actual_source / "how-to-report" / "scripts" / "report_run.py",
                        report_source / "scripts" / "report_run.py")
        shutil.copytree(actual_source / "how-to-report" / "assets" / "report-run",
                        report_source / "assets" / "report-run")
        self.command("build")
        self.command("check")
        destination = self.base / "standalone-how-to-report"
        shutil.copytree(self.project / "skills" / "how-to-report", destination)
        package_before = {path.relative_to(destination): path.read_bytes()
                          for path in destination.rglob("*") if path.is_file()}
        # This removes only the isolated fixture checkout, including its sibling skill.
        self.assertEqual(self.project.resolve().parent, self.base.resolve())
        shutil.rmtree(self.project)
        source = self.base / "原始 材料%# .txt"
        source.write_text("Synthetic source fixture.\n", encoding="utf-8")
        source_before = source.read_bytes()
        target = self.base / "待修订 报告.md"
        target.write_text("Synthetic revision target.\n", encoding="utf-8")
        target_before = target.read_bytes()
        helper = destination / "scripts" / "report_run.py"

        def execute(*arguments: str) -> dict:
            result = subprocess.run(
                [sys.executable, "-X", "utf8", "-I", "-B", str(helper), *arguments],
                cwd=self.cwd, capture_output=True, text=True, encoding="utf-8",
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            payload = json.loads(result.stdout)
            self.assertTrue(payload["valid"], payload)
            self.assertEqual(payload["scope"], "structure_and_declared_references_only")
            return payload

        runs = []
        for mode in ("create", "revise", "analyze-first"):
            with self.subTest(mode=mode):
                run = self.base / ("user-" + mode)
                arguments = ["init", str(run), "--run-id", "relocated-" + mode,
                             "--mode", mode, "--source", str(source)]
                if mode == "revise":
                    arguments.extend(("--target", str(target)))
                execute(*arguments)
                record = json.loads((run / "run.json").read_text(encoding="utf-8"))
                self.assertEqual(record["mode"], mode)
                self.assertEqual(record["work_status"], "in_progress")
                self.assertEqual(record["artifacts"], [])
                self.assertEqual(record["checks"], [])
                snapshots = sorted(path.read_bytes() for path in (run / "inputs").iterdir())
                expected = [source_before, target_before] if mode == "revise" else [source_before]
                self.assertEqual(snapshots, sorted(expected))
                self.assertEqual({item["revision"] for item in record["sources"]}, {1})
                runs.append((run, mode))
        self.assertEqual(source.read_bytes(), source_before)
        self.assertEqual(target.read_bytes(), target_before)
        # Continuation inspects frozen local inputs, even when original paths disappear.
        source.unlink()
        target.unlink()
        for run, mode in runs:
            before = {path.relative_to(run): (path.read_bytes(), path.stat().st_mtime_ns)
                      for path in run.rglob("*") if path.is_file()}
            payload = execute("inspect", str(run))
            self.assertEqual(payload["run_directory"], str(run.resolve()))
            self.assertEqual(payload["run_id"], "relocated-" + mode)
            self.assertEqual(payload["mode"], mode)
            self.assertEqual(payload["work_status"], "in_progress")
            self.assertEqual(payload["origin_currentness"], "not_assessed")
            self.assertEqual(payload["run_record_sha256"],
                             hashlib.sha256((run / "run.json").read_bytes()).hexdigest())
            self.assertEqual(before, {path.relative_to(run): (path.read_bytes(), path.stat().st_mtime_ns)
                                      for path in run.rglob("*") if path.is_file()})
        self.assertEqual(package_before, {path.relative_to(destination): path.read_bytes()
                                         for path in destination.rglob("*") if path.is_file()})

    def test_relocated_package_executes_real_version_change_and_acceptance(self) -> None:
        actual_source = SCRIPT.parents[1] / "skill-src"
        # Exercise the real shared runtime closure, including new helpers.
        shutil.copytree(actual_source / "shared" / "scripts", self.shared / "scripts",
                        dirs_exist_ok=True, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        report_source = self.source / "how-to-report"
        shutil.copytree(actual_source / "how-to-report" / "scripts", report_source / "scripts",
                        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        shutil.copytree(actual_source / "how-to-report" / "assets" / "report-run",
                        report_source / "assets" / "report-run")
        self.command("build")
        self.command("check")
        destination = self.base / "standalone-version-report"
        shutil.copytree(self.project / "skills" / "how-to-report", destination)
        package_before = {path.relative_to(destination): path.read_bytes()
                          for path in destination.rglob("*") if path.is_file()}
        self.assertEqual(self.project.resolve().parent, self.base.resolve())
        shutil.rmtree(self.project)
        run = self.base / "version-run"
        source = self.base / "material v1.txt"
        source.write_text("2\n3\n", encoding="utf-8")
        source2 = self.base / "material v2.txt"
        source2.write_text("2\n4\n", encoding="utf-8")
        report = self.base / "total.txt"
        report.write_text("5\n", encoding="utf-8")

        def execute(script, *arguments):
            result = subprocess.run(
                [sys.executable, "-X", "utf8", "-I", "-B", str(destination / "scripts" / script),
                 *map(str, arguments)], cwd=self.cwd, capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            payload = json.loads(result.stdout)
            self.assertTrue(payload["valid"], payload)
            return payload

        def mutate(command, *arguments):
            digest = hashlib.sha256((run / "run.json").read_bytes()).hexdigest()
            return execute("report_versions.py", command, run, *arguments,
                           "--reason", "Synthetic deterministic integer-sum fixture",
                           "--expect-run-sha256", digest)

        def checked_sum(revision, check_id):
            record = json.loads((run / "run.json").read_text(encoding="utf-8"))
            item = next(a for a in record["artifacts"] if a["id"] == "total" and a["revision"] == revision)
            dependency = next(a for a in record["sources"]
                              if a["id"] == "source-001" and a["revision"] == revision)
            actual = sum(int(line) for line in (run / dependency["ref"]).read_text().splitlines())
            self.assertEqual(int((run / item["ref"]).read_text()), actual)
            detail = f"checks/{check_id}.md"
            self.write(run / detail, f"Synthetic test actually summed registered integer inputs: {actual}.\n")
            record["checks"].append({"id": check_id, "target": {"id": "total", "revision": revision},
                                     "status": "pass", "method": "Python integer sum in this test",
                                     "scope": "Synthetic fixture only; no model/content-quality claim",
                                     "detail_ref": detail})
            self.write(run / "run.json", json.dumps(record, ensure_ascii=False, indent=2) + "\n")

        def artifact(payload, revision):
            return next(a for a in payload["artifacts"]
                        if a["target"] == {"id": "total", "revision": revision})

        execute("report_run.py", "init", run, "--run-id", "relocated-versions",
                "--mode", "create", "--source", source)
        mutate("select", "--target", "source-001@1")
        mutate("register", "--kind", "artifact", "--id", "total", "--revision", "1",
               "--file", report, "--uses", "source-001@1")
        mutate("select", "--target", "total@1")
        checked_sum(1, "sum-1")
        accepted = mutate("accept", "--target", "total@1", "--acceptance-id", "accepted-1", "--check", "sum-1")
        self.assertEqual(artifact(accepted, 1)["acceptance_status"], "current")
        preserved = json.loads((run / "run.json").read_text(encoding="utf-8"))
        old_files = {a["ref"]: (run / a["ref"]).read_bytes()
                     for a in preserved["sources"] + preserved["artifacts"]}
        mutate("register", "--kind", "source", "--id", "source-001", "--revision", "2", "--file", source2)
        pending = mutate("select", "--target", "source-001@2")
        self.assertEqual(artifact(pending, 1)["acceptance_status"], "stale")
        self.assertEqual(artifact(pending, 1)["currentness"]["state"], "pending")
        report.write_text("6\n", encoding="utf-8")
        mutate("register", "--kind", "artifact", "--id", "total", "--revision", "2",
               "--file", report, "--uses", "source-001@2")
        mutate("select", "--target", "total@2")
        checked_sum(2, "sum-2")
        accepted = mutate("accept", "--target", "total@2", "--acceptance-id", "accepted-2", "--check", "sum-2")
        self.assertEqual(artifact(accepted, 2)["acceptance_status"], "current")
        self.assertEqual(artifact(accepted, 1)["acceptance_status"], "stale")
        final = json.loads((run / "run.json").read_text(encoding="utf-8"))
        self.assertEqual(final["checks"][0], preserved["checks"][0])
        self.assertEqual(old_files, {relative: (run / relative).read_bytes() for relative in old_files})
        self.assertEqual(len(final["version_state"]["acceptances"]), 2)
        for origin in (source, source2, report):
            origin.unlink()
        before = {path.relative_to(run): (path.read_bytes(), path.stat().st_mtime_ns)
                  for path in run.rglob("*") if path.is_file()}
        inspected = execute("report_versions.py", "inspect", run)
        self.assertEqual(artifact(inspected, 2)["acceptance_status"], "current")
        execute("report_run.py", "inspect", run)
        self.assertEqual(before, {path.relative_to(run): (path.read_bytes(), path.stat().st_mtime_ns)
                                  for path in run.rglob("*") if path.is_file()})
        self.assertEqual(package_before, {path.relative_to(destination): path.read_bytes()
                                         for path in destination.rglob("*") if path.is_file()})

    def test_relocated_package_validates_schedule_without_visual_dependencies(self) -> None:
        actual_source = SCRIPT.parents[1] / "skill-src"
        shutil.copytree(actual_source / "shared" / "scripts", self.shared / "scripts",
                        dirs_exist_ok=True, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        report_source = self.source / "how-to-report"
        shutil.copytree(actual_source / "how-to-report" / "scripts", report_source / "scripts",
                        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        shutil.copytree(actual_source / "how-to-report" / "assets" / "schedule",
                        report_source / "assets" / "schedule")
        self.command("build")
        self.command("check")
        destination = self.base / "standalone-content-report"
        shutil.copytree(self.project / "skills" / "how-to-report", destination)
        package_before = {path.relative_to(destination): path.read_bytes()
                          for path in destination.rglob("*") if path.is_file()}
        self.assertEqual(self.project.resolve().parent, self.base.resolve())
        shutil.rmtree(self.project)
        original = self.base / "日期 #1 50%.json"
        shutil.copyfile(destination / "assets" / "schedule" / "sample-schedule.json", original)
        captured = original.read_bytes()
        result = subprocess.run([sys.executable, "-I", "-B", "-X", "utf8",
                                 str(destination / "scripts" / "report_schedule.py"), "validate", str(original)],
                                cwd=self.cwd, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        receipt = json.loads(result.stdout)
        self.assertTrue(receipt["valid"])
        self.assertEqual(receipt["semantic_validation"], "not_run")
        self.assertEqual(receipt["input_sha256"], hashlib.sha256(captured).hexdigest())
        self.assertEqual(receipt["run_mutation"], "not_performed")
        row = next(row for row in receipt["date_comparisons"] if row["id"] == "integration")
        self.assertEqual(row["deviation_calendar_days"], 15)
        self.assertEqual(original.read_bytes(), captured)
        for name in ("report_html.py", "presentation_components.py", "diagram_layout.py", "schedule_render.py"):
            self.assertFalse((destination / "scripts" / name).exists())
        self.assertFalse((destination / "assets" / "report-html").exists())
        self.assertEqual(package_before, {path.relative_to(destination): path.read_bytes()
                                         for path in destination.rglob("*") if path.is_file()})

    def test_check_is_read_only_and_detects_modified_extra_and_missing_files(self) -> None:
        self.command("build")
        original = self.snapshot()
        output = self.project / "skills" / "how-to-report"
        stamp = (output / "SKILL.md").stat().st_mtime_ns
        self.command("check")
        self.assertEqual((output / "SKILL.md").stat().st_mtime_ns, stamp)
        self.assertEqual(self.snapshot(), original)
        for change in ("modified", "extra", "empty-directory", "missing"):
            with self.subTest(change=change):
                if change == "modified":
                    self.write(output / "references" / "graph-model.md", "drift")
                elif change == "extra":
                    self.write(output / "leftover.txt", "old resource")
                elif change == "empty-directory":
                    (output / "leftover").mkdir()
                else:
                    (output / "references" / "graph-model.md").unlink()
                before = self.snapshot()
                self.command("check", success=False)
                self.assertEqual(self.snapshot(), before)
                self.command("build")
                self.assertEqual(self.snapshot(), original)

    def test_clean_rebuild_removes_deleted_source_payload(self) -> None:
        old = self.shared / "assets" / "obsolete.txt"
        self.write(old, "obsolete")
        self.command("build")
        old.unlink()
        self.command("build")
        self.command("check")
        for skill in packager.SKILLS:
            self.assertFalse((self.project / "skills" / skill / "assets" / "obsolete.txt").exists())

    def test_interpreter_caches_do_not_become_source_payload(self) -> None:
        self.write(self.shared / "scripts" / "__pycache__" / "validator.pyc", "machine cache")
        self.write(self.shared / "scripts" / "legacy.pyc", "machine cache")
        self.command("build")
        self.command("check")
        for skill in packager.SKILLS:
            manifest = json.loads((self.project / "skills" / skill / packager.MANIFEST).read_text())
            self.assertFalse(any("__pycache__" in path or path.endswith(".pyc") for path in manifest["files"]))

    def test_shared_collision_preserves_both_previous_packages(self) -> None:
        self.command("build")
        before = self.snapshot()
        self.write(self.source / "report-audit" / "references" / "graph-model.md", "shadow")
        failure = self.command("build", success=False)
        self.assertIn("collision", failure.stderr)
        self.assertEqual(self.snapshot(), before)

    def test_cross_source_case_collision_is_rejected(self) -> None:
        self.write(self.source / "how-to-report" / "Assets" / "other.md", "case mismatch")
        failure = self.command("build", success=False)
        self.assertIn("collision", failure.stderr)

    def test_file_directory_collision_is_rejected(self) -> None:
        self.write(self.source / "how-to-report" / "assets", "not a directory")
        self.command("build", success=False)

    def test_bad_static_resource_links_preserve_previous_packages(self) -> None:
        self.command("build")
        before = self.snapshot()
        reference = self.source / "how-to-report" / "references" / "method.md"
        for target in ("../../outside.txt", "%2e%2e/%2e%2e/outside.txt", "C:/private/file.txt", "file:///private/file.txt", "/private/file.txt", "missing.md", "../References/graph-model.md"):
            with self.subTest(target=target):
                self.write(reference, f"[Dependency]({target})\n")
                self.command("build", success=False)
                self.assertEqual(self.snapshot(), before)

    def test_external_links_code_examples_and_reference_definition(self) -> None:
        reference = self.source / "how-to-report" / "references" / "method.md"
        self.write(reference, "[Source](https://example.com/material?q=1#part)\n"
                   "```md\n[Example only](../../outside.txt)\n```\n"
                   "[Contract][core]\n\n[core]: graph-model.md\n")
        self.command("build")
        self.write(reference, "[Contract][core]\n\n[core]: absent.md\n")
        self.command("build", success=False)

    def test_missing_core_reference_and_mismatched_name_rejected(self) -> None:
        entry = self.source / "how-to-report" / "SKILL.md"
        original = entry.read_text()
        self.write(entry, original.replace("[contract](references/graph-model.md)", "graph-model"))
        self.command("build", success=False)
        self.write(entry, original.replace("name: how-to-report", "name: other-name"))
        self.command("build", success=False)

    def test_unknown_output_directory_never_overwritten(self) -> None:
        user_file = self.project / "skills" / "report-audit" / "notes.txt"
        self.write(user_file, "user content")
        self.command("build", success=False)
        self.assertEqual(user_file.read_text(), "user content")
        self.assertFalse((self.project / "skills" / "how-to-report").exists())

    def test_unrelated_output_directory_is_untouched(self) -> None:
        user_file = self.project / "skills" / "another-skill" / "notes.txt"
        self.write(user_file, "user content")
        self.command("build")
        self.command("check")
        self.assertEqual(user_file.read_text(), "user content")

    def test_failed_second_replacement_rolls_back_both_packages(self) -> None:
        self.command("build")
        before = self.snapshot()
        self.write(self.shared / "assets" / "value.json", '{"answer": 43}')
        packages = packager.expected_packages(self.project)
        original_rename = Path.rename

        def failing_rename(path: Path, destination: Path) -> Path:
            if path.name == "report-audit" and path.parent.name.startswith(".package-build-"):
                raise OSError("simulated second replacement failure")
            return original_rename(path, destination)

        with patch.object(Path, "rename", failing_rename), self.assertRaises(OSError):
            packager.build(self.project, packages)
        self.assertEqual(self.snapshot(), before)

    def test_failed_rollback_retains_previous_package_for_recovery(self) -> None:
        self.command("build")
        output = self.project / "skills"
        old_payload = (output / "how-to-report" / "assets" / "value.json").read_bytes()
        self.write(self.shared / "assets" / "value.json", '{"answer": 43}')
        packages = packager.expected_packages(self.project)
        original_rename = Path.rename
        original_remove = packager.remove_tree

        def failing_rename(path: Path, destination: Path) -> Path:
            if path == output / "report-audit":
                raise OSError("simulated failure before second backup")
            return original_rename(path, destination)

        def failing_remove(path: Path, root: Path) -> None:
            if path == output / "how-to-report":
                raise OSError("simulated locked new package during rollback")
            original_remove(path, root)

        with patch.object(Path, "rename", failing_rename), patch.object(
            packager, "remove_tree", failing_remove
        ), self.assertRaisesRegex(OSError, "locked new package"):
            packager.build(self.project, packages)
        retained = list(output.glob(".package-build-*"))
        self.assertEqual(len(retained), 1)
        backup = retained[0] / "how-to-report.previous" / "assets" / "value.json"
        self.assertEqual(backup.read_bytes(), old_payload)
        self.assertNotEqual((output / "how-to-report" / "assets" / "value.json").read_bytes(), old_payload)
        self.assertEqual((output / "report-audit" / "assets" / "value.json").read_bytes(), old_payload)

    @staticmethod
    def windows_rename_error(code: int = 5) -> OSError:
        error = PermissionError("simulated Windows directory rename failure")
        error.winerror = code
        return error

    def test_first_windows_backup_rename_preserves_roots_and_exact_payload(self) -> None:
        self.write(self.shared / "assets" / "obsolete.txt", "old")
        self.write(self.shared / "assets" / "becomes-directory", "old file")
        self.write(self.shared / "assets" / "becomes-file" / "child.txt", "old child")
        self.command("build")
        output = self.project / "skills"
        identities = {skill: (output / skill).stat().st_ino for skill in packager.SKILLS}
        for skill in packager.SKILLS:
            (output / skill / "empty-old-directory").mkdir()
            manifest_path = output / skill / packager.MANIFEST
            manifest = json.loads(manifest_path.read_text())
            manifest["package_version"] = "0.2.0"
            self.write(manifest_path, json.dumps(manifest))
        (self.shared / "assets" / "obsolete.txt").unlink()
        (self.shared / "assets" / "becomes-directory").unlink()
        self.write(self.shared / "assets" / "becomes-directory" / "child.txt", "new child")
        (self.shared / "assets" / "becomes-file" / "child.txt").unlink()
        (self.shared / "assets" / "becomes-file").rmdir()
        self.write(self.shared / "assets" / "becomes-file", "new file")
        self.write(self.shared / "assets" / "value.json", '{"answer": 43}')
        unrelated = output / "unrelated" / "keep.txt"
        self.write(unrelated, "leave alone")
        packages = packager.expected_packages(self.project)
        original_rename = Path.rename

        for code in (5, 32):
            with self.subTest(winerror=code):
                attempts = []

                def locked_first_backup(path: Path, destination: Path) -> Path:
                    attempts.append((path, destination))
                    if path == output / "how-to-report":
                        raise self.windows_rename_error(code)
                    return original_rename(path, destination)

                with patch.object(Path, "rename", locked_first_backup):
                    packager.build(self.project, packages)
                self.assertEqual(len(attempts), 1)
                packager.check(self.project, packages)
                for skill in packager.SKILLS:
                    self.assertEqual((output / skill).stat().st_ino, identities[skill])
                    self.assertEqual(packager.tree(output / skill)[0], packages[skill])
                    manifest = json.loads((output / skill / packager.MANIFEST).read_bytes())
                    self.assertEqual(manifest["package_version"], "0.6.0")
                    self.assertEqual(manifest["supported_contract_version"], "0.1")
                self.assertFalse(list(output.glob(".package-build-*")))
                self.assertEqual(unrelated.read_text(), "leave alone")

    def test_directory_fallback_finishes_all_backups_before_any_mutation(self) -> None:
        self.command("build")
        before = self.snapshot()
        output = self.project / "skills"
        self.write(self.shared / "assets" / "value.json", '{"answer": 43}')
        packages = packager.expected_packages(self.project)
        original_rename, original_write = Path.rename, Path.write_bytes

        def locked_first_backup(path: Path, destination: Path) -> Path:
            if path == output / "how-to-report":
                raise self.windows_rename_error()
            return original_rename(path, destination)

        def failed_second_backup(path: Path, data: bytes) -> int:
            if "report-audit.previous" in path.parts and path.name == "value.json":
                raise OSError("simulated second backup copy failure")
            return original_write(path, data)

        with patch.object(Path, "rename", locked_first_backup), patch.object(
            Path, "write_bytes", failed_second_backup
        ), self.assertRaisesRegex(OSError, "second backup copy"):
            packager.build(self.project, packages)
        self.assertEqual(self.snapshot(), before)
        self.assertFalse(list(output.glob(".package-build-*")))

    def test_directory_fallback_partial_install_restores_both_exact_trees(self) -> None:
        self.command("build")
        output = self.project / "skills"
        for skill in packager.SKILLS:
            (output / skill / "empty-preserved").mkdir()
        previous = {skill: packager.tree(output / skill) for skill in packager.SKILLS}
        identities = {skill: (output / skill).stat().st_ino for skill in packager.SKILLS}
        before = self.snapshot()
        self.write(self.shared / "assets" / "value.json", '{"answer": 43}')
        packages = packager.expected_packages(self.project)
        original_rename, original_write = Path.rename, Path.write_bytes
        failed = False

        def locked_first_backup(path: Path, destination: Path) -> Path:
            if path == output / "how-to-report":
                raise self.windows_rename_error()
            return original_rename(path, destination)

        def partial_second_install(path: Path, data: bytes) -> int:
            nonlocal failed
            if path == output / "report-audit" / "assets" / "value.json" and not failed:
                failed = True
                original_write(path, b"partial")
                raise OSError("simulated partial second install")
            return original_write(path, data)

        with patch.object(Path, "rename", locked_first_backup), patch.object(
            Path, "write_bytes", partial_second_install
        ), self.assertRaisesRegex(OSError, "partial second install"):
            packager.build(self.project, packages)
        self.assertTrue(failed)
        self.assertEqual(self.snapshot(), before)
        for skill in packager.SKILLS:
            self.assertEqual(packager.tree(output / skill), previous[skill])
            self.assertEqual((output / skill).stat().st_ino, identities[skill])
        self.assertFalse(list(output.glob(".package-build-*")))

    def test_directory_fallback_failed_rollback_retains_both_backups(self) -> None:
        self.command("build")
        output = self.project / "skills"
        previous = {skill: packager.tree(output / skill) for skill in packager.SKILLS}
        old_value = previous["how-to-report"][0]["assets/value.json"]
        self.write(self.shared / "assets" / "value.json", '{"answer": 43}')
        packages = packager.expected_packages(self.project)
        original_rename, original_write = Path.rename, Path.write_bytes
        failed = False

        def locked_first_backup(path: Path, destination: Path) -> Path:
            if path == output / "how-to-report":
                raise self.windows_rename_error()
            return original_rename(path, destination)

        def fail_install_and_first_restore(path: Path, data: bytes) -> int:
            nonlocal failed
            if path == output / "report-audit" / "assets" / "value.json" and not failed:
                failed = True
                original_write(path, b"partial")
                raise OSError("simulated partial second install")
            if path == output / "how-to-report" / "assets" / "value.json" and data == old_value:
                raise OSError("simulated first rollback failure")
            return original_write(path, data)

        with patch.object(Path, "rename", locked_first_backup), patch.object(
            Path, "write_bytes", fail_install_and_first_restore
        ), self.assertRaisesRegex(packager.DirectoryRecoveryError, "recovery backups retained"):
            packager.build(self.project, packages)
        retained = list(output.glob(".package-build-*"))
        self.assertEqual(len(retained), 1)
        for skill in packager.SKILLS:
            self.assertEqual(packager.tree(retained[0] / (skill + ".previous")), previous[skill])
        self.assertEqual(packager.tree(output / "report-audit"), previous["report-audit"])

    def test_directory_fallback_rollback_removes_only_new_empty_package_root(self) -> None:
        self.command("build")
        output = self.project / "skills"
        packager.remove_tree(output / "report-audit", output)
        before = self.snapshot()
        identity = (output / "how-to-report").stat().st_ino
        self.write(self.shared / "assets" / "value.json", '{"answer": 43}')
        packages = packager.expected_packages(self.project)
        original_rename, original_write = Path.rename, Path.write_bytes

        def locked_first_backup(path: Path, destination: Path) -> Path:
            if path == output / "how-to-report":
                raise self.windows_rename_error()
            return original_rename(path, destination)

        def failed_new_package(path: Path, data: bytes) -> int:
            if path == output / "report-audit" / "assets" / "value.json":
                original_write(path, b"partial new package")
                raise OSError("simulated new package failure")
            return original_write(path, data)

        with patch.object(Path, "rename", locked_first_backup), patch.object(
            Path, "write_bytes", failed_new_package
        ), self.assertRaisesRegex(OSError, "new package failure"):
            packager.build(self.project, packages)
        self.assertEqual(self.snapshot(), before)
        self.assertEqual((output / "how-to-report").stat().st_ino, identity)
        self.assertFalse((output / "report-audit").exists())

    def test_other_first_backup_errors_do_not_use_directory_fallback(self) -> None:
        self.command("build")
        before = self.snapshot()
        packages = packager.expected_packages(self.project)
        for error in (PermissionError(13, "ordinary permission failure"), self.windows_rename_error(87)):
            with self.subTest(error=repr(error)), patch.object(
                Path, "rename", side_effect=error
            ), patch.object(packager, "build_preserving_directories") as fallback, self.assertRaises(OSError):
                packager.build(self.project, packages)
            fallback.assert_not_called()
            self.assertEqual(self.snapshot(), before)

    def test_later_windows_backup_error_uses_normal_rollback(self) -> None:
        self.command("build")
        before = self.snapshot()
        output = self.project / "skills"
        self.write(self.shared / "assets" / "value.json", '{"answer": 43}')
        packages = packager.expected_packages(self.project)
        original_rename = Path.rename

        def locked_second_backup(path: Path, destination: Path) -> Path:
            if path == output / "report-audit":
                raise self.windows_rename_error()
            return original_rename(path, destination)

        with patch.object(Path, "rename", locked_second_backup), patch.object(
            packager, "build_preserving_directories"
        ) as fallback, self.assertRaises(OSError):
            packager.build(self.project, packages)
        fallback.assert_not_called()
        self.assertEqual(self.snapshot(), before)

    def test_first_windows_stage_install_error_does_not_use_fallback(self) -> None:
        packages = packager.expected_packages(self.project)
        with patch.object(Path, "rename", side_effect=self.windows_rename_error()), patch.object(
            packager, "build_preserving_directories"
        ) as fallback, self.assertRaises(OSError):
            packager.build(self.project, packages)
        fallback.assert_not_called()
        self.assertEqual(self.snapshot(), {})

    def test_directory_fallback_rechecks_links_before_backup_or_mutation(self) -> None:
        self.command("build")
        output = self.project / "skills"
        external = self.base / "external-fallback"
        self.write(external / "keep.txt", "outside")
        entry = output / "how-to-report" / "SKILL.md"
        before = entry.read_bytes()
        packages = packager.expected_packages(self.project)
        original_rename = Path.rename

        def link_then_lock(path: Path, destination: Path) -> Path:
            if path == output / "how-to-report":
                self.make_directory_link(path / "late-link", external)
                raise self.windows_rename_error()
            return original_rename(path, destination)

        with patch.object(Path, "rename", link_then_lock), self.assertRaisesRegex(
            packager.PackageError, "symlinks/junctions"
        ):
            packager.build(self.project, packages)
        self.assertEqual(entry.read_bytes(), before)
        self.assertEqual((external / "keep.txt").read_text(), "outside")
        self.assertFalse(list(output.glob(".package-build-*")))

    def make_directory_link(self, link: Path, target: Path) -> None:
        if os.name == "nt":
            # Junction creation needs no developer-mode/symlink privilege.
            result = subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(target)], capture_output=True, text=True)
            if result.returncode:
                self.skipTest("Cannot create junction in this environment: " + result.stderr)
            self.addCleanup(lambda: os.rmdir(link) if os.path.lexists(link) else None)
        else:
            link.symlink_to(target, target_is_directory=True)
            self.addCleanup(lambda: link.unlink() if link.is_symlink() else None)

    def test_source_directory_link_is_rejected(self) -> None:
        external = self.base / "external"
        self.write(external / "secret.txt", "outside")
        self.make_directory_link(self.shared / "linked", external)
        failure = self.command("build", success=False)
        self.assertIn("symlinks/junctions", failure.stderr)

    def test_linked_output_is_never_replaced_or_traversed(self) -> None:
        external = self.base / "external"
        self.write(external / "keep.txt", "outside")
        (self.project / "skills").mkdir()
        self.make_directory_link(self.project / "skills" / "how-to-report", external)
        self.command("build", success=False)
        self.assertEqual((external / "keep.txt").read_text(), "outside")


if __name__ == "__main__":
    unittest.main()
