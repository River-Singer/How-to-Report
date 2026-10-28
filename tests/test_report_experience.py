"""Explicit private snapshot lifecycle, bounded retrieval and boundary regressions."""
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


class ExperienceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.package = self.root / "relocated-skill"
        scripts = self.package / "scripts"
        scripts.mkdir(parents=True)
        (self.package / "SKILL.md").write_text("synthetic", encoding="utf-8")
        for src in (PROJECT / "skill-src/shared/scripts").glob("*.py"):
            shutil.copyfile(src, scripts / src.name)
        self.script = scripts / "report_experience.py"
        sys.path.insert(0, str(scripts))
        self.addCleanup(lambda: sys.path.remove(str(scripts)))
        spec = importlib.util.spec_from_file_location("experience_test", self.script)
        self.mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.mod)
        self.path = self.root / "v1.json"
        self.entry = json.loads((PROJECT / "skill-src/shared/assets/examples/experience-entry.json").read_text(encoding="utf-8"))
        self.change = self.root / "request.json"

    def write_request(self, entry=None):
        self.change.write_text(json.dumps(entry or self.entry, ensure_ascii=False), encoding="utf-8")

    def create_case(self):
        self.mod.initialize(self.path, "cases")
        self.write_request()
        out = self.root / "v2.json"
        self.mod.revise(self.path, self.change, hashlib.sha256(self.path.read_bytes()).hexdigest(), out)
        return out

    def test_append_correct_and_withdraw_preserve_old_bytes_and_history(self):
        path = self.create_case()
        before = path.read_bytes()
        self.entry["action"] = "Corrected explicit action"
        self.entry["status"] = "withdrawn"
        self.write_request()
        out = self.root / "v3.json"
        self.mod.revise(path, self.change, hashlib.sha256(before).hexdigest(), out)
        self.assertEqual(path.read_bytes(), before)
        data = json.loads(out.read_text(encoding="utf-8"))
        self.assertEqual([e["revision"] for e in data["entries"]], [1, 2])
        self.assertEqual(data["parent_snapshot_sha256"], hashlib.sha256(before).hexdigest())
        self.assertEqual(self.mod.inspect(out)["entries"], [])
        self.assertEqual(len(self.mod.inspect(out, include_withdrawn=True)["entries"]), 1)
        self.assertEqual(self.mod.inspect(out, tags=["delay"])["entries"], [])
        self.assertEqual(len(self.mod.inspect(out, tags=["delay"], include_withdrawn=True)["entries"]), 1)
        # A caller-selected old snapshot is still old history, never silently rewritten.
        self.assertEqual(self.mod.inspect(path)["entries"][0]["status"], "active")

    def test_default_metadata_redacts_private_values(self):
        path = self.create_case()
        self.assertNotIn(self.entry["context"], json.dumps(self.mod.inspect(path), ensure_ascii=False))
        self.assertEqual(self.mod.inspect(path, show=True)["entries"][0]["context"], self.entry["context"])

    def test_literal_search_and_tag_filters_do_not_claim_semantic_applicability(self):
        path = self.create_case()
        self.assertEqual(len(self.mod.inspect(path, query="资源协调", tags=["delay"])["entries"]), 1)
        self.assertEqual(self.mod.inspect(path, query="unrelated")["entries"], [])
        self.assertEqual(self.mod.inspect(path, tags=["absent"])["entries"], [])
        self.assertEqual(self.mod.inspect(path, kind="method_candidate")["entries"], [])
        self.assertEqual(self.mod.inspect(path)["semantic_applicability"], "not_assessed")

    def test_stale_snapshot_and_overwrite_fail_without_change(self):
        path = self.create_case()
        before = path.read_bytes()
        with self.assertRaises(ValueError):
            self.mod.revise(path, self.change, "0" * 64, self.root / "new.json")
        with self.assertRaises(ValueError):
            self.mod.revise(path, self.change, hashlib.sha256(before).hexdigest(), path)
        self.assertEqual(path.read_bytes(), before)
        self.assertFalse((self.root / "new.json").exists())

    def test_observation_requires_declared_exact_source_and_state(self):
        entry = {**self.entry, "revision": 1}
        for refs in ([], [{"id":"not-declared","revision":1,"locator":"x"}], [{"id":"synthetic-input","revision":True,"locator":"x"}]):
            bad = deepcopy(entry)
            bad["observations"] = [{"status":"observed","text":"Measured result", "source_refs":refs}]
            with self.subTest(refs=refs), self.assertRaises(ValueError):
                self.mod.validate_entry(bad)
        entry["observations"] = [{"status":"observed","text":"Synthetic measurement declaration only","source_refs":deepcopy(entry["source_refs"])}]
        self.mod.validate_entry(entry)

    def test_kind_cannot_change_or_become_preference(self):
        path = self.create_case()
        for kind in ("preference", "method_candidate"):
            self.entry["kind"] = kind
            self.write_request()
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                self.mod.revise(path, self.change, hashlib.sha256(path.read_bytes()).hexdigest(), self.root / "new.json")
        self.assertFalse((self.root / "new.json").exists())

    def test_history_duplicate_keys_and_unknown_fields_rejected(self):
        path = self.create_case()
        data = json.loads(path.read_text(encoding="utf-8"))
        data["entries"][0]["revision"] = 2
        with self.assertRaises(ValueError):
            self.mod.validate(data)
        data["entries"][0]["revision"] = True
        with self.assertRaises(ValueError):
            self.mod.validate(data)
        self.change.write_text('{"experience_version":"0.1","experience_version":"0.1"}', encoding="utf-8")
        with self.assertRaises(ValueError):
            self.mod.read(self.change)
        data["extra"] = "unknown"
        with self.assertRaises(ValueError):
            self.mod.validate(data)

    def test_cross_package_and_run_write_protection(self):
        other = self.root / "other-skill"; other.mkdir()
        (other / "bundle-manifest.json").write_text("{}", encoding="utf-8")
        run = self.root / "run"; run.mkdir()
        (run / "run.json").write_text("{}", encoding="utf-8")
        for parent in (self.package, other, run):
            with self.subTest(parent=parent), self.assertRaises(ValueError):
                self.mod.initialize(parent / "private.json", "cases")
            self.assertFalse((parent / "private.json").exists())

    def test_revision_and_withdrawal_reject_nested_package_without_side_effects(self):
        source = self.create_case()
        nested = self.root / "private-store" / "history" / "installed-skill"
        nested.mkdir(parents=True)
        marker = nested / "SKILL.md"
        marker.write_bytes(b"unrelated installed Skill")
        for status in ("active", "withdrawn"):
            self.entry["status"] = status
            self.write_request()
            before = {p.relative_to(self.root): (p.read_bytes(), p.stat().st_mtime_ns)
                      for p in self.root.rglob("*") if p.is_file()}
            with self.subTest(status=status), self.assertRaisesRegex(ValueError, "installed Skill"):
                self.mod.revise(source, self.change, hashlib.sha256(source.read_bytes()).hexdigest(), nested / "new.json")
            self.assertEqual(before, {p.relative_to(self.root): (p.read_bytes(), p.stat().st_mtime_ns)
                                      for p in self.root.rglob("*") if p.is_file()})

    def test_partial_new_snapshot_failure_preserves_old_snapshot_and_partial_file(self):
        source = self.create_case()
        before = source.read_bytes()
        request_before = self.change.read_bytes()
        output = self.root / "failed-snapshot.json"
        original_open = Path.open

        class FailingWrite:
            def __enter__(inner):
                inner.stream = original_open(output, "xb")
                return inner

            def write(inner, data):
                inner.stream.write(data[:32])
                raise OSError("simulated partial snapshot write")

            def __exit__(inner, *args):
                inner.stream.close()

        def fail_output(path, *args, **kwargs):
            return FailingWrite() if path.resolve() == output.resolve() and args == ("xb",) else original_open(path, *args, **kwargs)

        with patch.object(Path, "open", fail_output), self.assertRaisesRegex(OSError, "partial snapshot write"):
            self.mod.revise(source, self.change, hashlib.sha256(before).hexdigest(), output)
        self.assertEqual(source.read_bytes(), before)
        self.assertEqual(self.change.read_bytes(), request_before)
        self.assertEqual(len(output.read_bytes()), 32)
        with self.assertRaises(ValueError):
            self.mod.revise(source, self.change, hashlib.sha256(before).hexdigest(), output)
        self.assertEqual(len(output.read_bytes()), 32)

    def test_missing_confirmed_scope_and_oversize_store_rejected(self):
        for key in ("confirmation_ref", "applicability", "exclusions"):
            entry = {**self.entry, "revision": 1, key: ""}
            with self.subTest(key=key), self.assertRaises(ValueError):
                self.mod.validate_entry(entry)
        self.change.write_bytes(b" " * (self.mod.MAX_BYTES + 1))
        with self.assertRaises(ValueError):
            self.mod.read(self.change)

    def test_invalid_json_field_types_fail_with_value_error(self):
        for key in ("kind", "status", "source_refs", "observations", "tags"):
            for invalid in (None, {}, True):
                entry = {**self.entry, "revision": 1, key: invalid}
                with self.subTest(key=key, invalid=invalid), self.assertRaises(ValueError):
                    self.mod.validate_entry(entry)
        entry = {**self.entry, "revision": 1, "observations": [{"status": [], "text": "unknown", "source_refs": []}]}
        with self.assertRaises(ValueError):
            self.mod.validate_entry(entry)

    def test_isolated_cli_relocation_and_read_only_inspection(self):
        result = subprocess.run([sys.executable, "-B", "-I", str(self.script), "init", str(self.path), "--store-id", "cases"], cwd=self.root, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        before = self.path.read_bytes()
        result = subprocess.run([sys.executable, "-B", "-I", str(self.script), "inspect", str(self.path)], cwd=self.root, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertEqual(self.path.read_bytes(), before)
        self.assertEqual(json.loads(result.stdout)["automatic_learning"], False)
        self.assertFalse(list(self.package.rglob("__pycache__")))


if __name__ == "__main__":
    unittest.main()
