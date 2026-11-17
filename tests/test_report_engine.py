"""Normal entry-point and controlled state persistence regressions."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skill-src" / "how-to-report" / "scripts"
sys.path.insert(0, str(SCRIPTS))
import report_engine


class ReportEngineTests(unittest.TestCase):
    def document(self):
        return {
            "schema_version": "0.1", "project_id": "test-engine", "revision": 1,
            "brief": {"audience": "项目团队"}, "sources": [],
            "facts": {"total": {"value": 100}, "active": {"value": 40},
                      "rate": {"derived": {"op": "ratio", "args": ["active", "total"]}}},
            "pages": [{"id": "p1", "kind": "scene", "job": "解释比例", "notes": "说明",
                       "elements": [{"id": "p1-title", "type": "text", "frame": [50, 50, 1000, 80],
                                     "text": ["使用比例 ", {"ref": "rate", "format": "percent"}]}]}],
        }

    def command(self, directory, *arguments):
        return subprocess.run([sys.executable, str(SCRIPTS / "report_engine.py"), *arguments],
                              cwd=directory, capture_output=True, text=True, encoding="utf-8")

    def test_validate_facts_and_patch_from_unrelated_cwd(self):
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            source = folder / "author.json"
            raw = report_engine.encoded(self.document())
            source.write_bytes(raw)
            checked = self.command(folder, "validate", "--input", str(source))
            self.assertEqual(checked.returncode, 0, checked.stderr)
            calculated = self.command(folder, "facts", "--input", str(source))
            self.assertEqual(calculated.returncode, 0, calculated.stderr)
            self.assertEqual(json.loads(calculated.stdout)["facts"]["rate"], 0.4)
            operations = folder / "patch.json"
            operations.write_text(json.dumps([{"op": "replace", "path": "/facts/active/value", "value": 60}]),
                                  encoding="utf-8")
            target = folder / "author-v2.json"
            patched = self.command(folder, "patch", "--input", str(source), "--patch", str(operations),
                                   "--expected-revision", "1", "--operation-id", "update-active",
                                   "--output", str(target))
            self.assertEqual(patched.returncode, 0, patched.stderr)
            self.assertEqual(json.loads(target.read_text(encoding="utf-8"))["revision"], 2)
            self.assertEqual(source.read_bytes(), raw)
            changed = self.command(folder, "facts", "--input", str(target))
            self.assertEqual(json.loads(changed.stdout)["facts"]["rate"], 0.6)

    def test_new_output_preserves_existing_bytes(self):
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary) / "existing.json"
            destination.write_bytes(b"existing")
            with self.assertRaises(FileExistsError):
                report_engine.write_new_json(destination, {"changed": True})
            self.assertEqual(destination.read_bytes(), b"existing")

    def test_build_and_native_export_from_unrelated_cwd(self):
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            source = folder / "author.json"
            source.write_bytes(report_engine.encoded(self.document()))
            project = folder / "compiled"
            output = folder / "example.pptx"
            result = self.command(folder, "build", "--geometry-policy", "legacy-replay", "--input", str(source),
                                  "--output", str(project), "--pptx", str(output))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(output.is_file())
            receipt = json.loads(result.stdout)
            self.assertEqual(receipt["check_status"], "pass")
            self.assertEqual(receipt["inspection"]["counts"]["slides"], 1)
            self.assertLess(len(result.stdout), 8000)
            self.assertNotIn("pages", receipt)
            self.assertNotIn("slides", receipt["inspection"])
            inspection_path = Path(receipt["inspection"]["detail_ref"])
            self.assertTrue(inspection_path.is_file())
            details = json.loads(inspection_path.read_text(encoding="utf-8"))
            self.assertEqual(details["counts"], receipt["inspection"]["counts"])
            self.assertEqual(len(details["slides"]), 1)
            self.assertIn("checked_inputs", details)
            self.assertTrue(Path(receipt["receipt_ref"]).is_file())
            self.assertTrue(Path(receipt["object_map_ref"]).is_file())
            second = self.command(folder, "build", "--geometry-policy", "legacy-replay", "--input", str(source),
                                  "--output", str(folder / "unused"), "--pptx", str(output))
            self.assertNotEqual(second.returncode, 0)
            self.assertFalse((folder / "unused").exists())

    def test_control_commit_keeps_history_and_rejects_stale_write(self):
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "control.json"
            raw = report_engine.encoded({"revision": 1})
            target.write_bytes(raw)
            before = hashlib.sha256(raw).hexdigest()
            report_engine.mutate_control(target, before, lambda state: {"revision": state["revision"] + 1})
            self.assertEqual(json.loads(target.read_text(encoding="utf-8")), {"revision": 2})
            self.assertEqual((target.parent / "control-history" / (before + ".json")).read_bytes(), raw)
            with self.assertRaisesRegex(ValueError, "stale"):
                report_engine.mutate_control(target, before, lambda state: {"revision": 3})
            self.assertEqual(json.loads(target.read_text(encoding="utf-8")), {"revision": 2})
            self.assertFalse(target.with_name("control.json.lock").exists())

    def test_control_preserves_another_writer_lock(self):
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "control.json"
            target.write_bytes(report_engine.encoded({"revision": 1}))
            lock = target.with_name("control.json.lock")
            lock.write_bytes(b"other writer")
            expected = hashlib.sha256(target.read_bytes()).hexdigest()
            with self.assertRaises(FileExistsError):
                report_engine.mutate_control(target, expected, lambda state: {"revision": 2})
            self.assertEqual(lock.read_bytes(), b"other writer")

    def test_query_json_remains_utf8_with_legacy_console_encoding(self):
        with tempfile.TemporaryDirectory() as temporary:
            environment = dict(os.environ, PYTHONIOENCODING="cp936")
            result = subprocess.run(
                [sys.executable, str(SCRIPTS / "report_engine.py"), "query", "--task", "strategy"],
                cwd=temporary, env=environment, capture_output=True, encoding="utf-8")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)["candidates"][0]["label"], "战略屋")

    def test_materialized_package_builds_without_checkout_or_sibling(self):
        specification = importlib.util.spec_from_file_location("engine_test_packager", ROOT / "tools/package_skills.py")
        packager = importlib.util.module_from_spec(specification)
        specification.loader.exec_module(packager)
        payload = packager.expected_packages(ROOT)["how-to-report"]
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            package = folder / "standalone"
            for relative, data in payload.items():
                target = package / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
            unrelated = folder / "user-work"
            unrelated.mkdir()
            source = unrelated / "author.json"
            source.write_bytes(report_engine.encoded(self.document()))
            output = unrelated / "result.pptx"
            environment = dict(os.environ)
            environment.pop("PYTHONPATH", None)
            result = subprocess.run(
                [sys.executable, str(package / "scripts/report_engine.py"), "build", "--geometry-policy", "legacy-replay", "--input", str(source),
                 "--output", str(unrelated / "compiled"), "--pptx", str(output)],
                cwd=unrelated, env=environment, capture_output=True, encoding="utf-8")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(output.is_file())
            self.assertEqual(json.loads(result.stdout)["inspection"]["counts"]["slides"], 1)


if __name__ == "__main__":
    unittest.main()
