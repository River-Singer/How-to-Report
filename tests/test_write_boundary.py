"""Read-only destination preflight independent of native link privileges."""
import importlib.util
import os
from pathlib import Path
import stat
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

HELPER = Path(__file__).resolve().parents[1] / "skill-src/shared/scripts/write_boundary.py"
SPEC = importlib.util.spec_from_file_location("write_boundary_under_test", HELPER)
BOUNDARY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BOUNDARY)


class WriteBoundaryTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="write-boundary-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()

    def test_external_missing_destination_remains_absent_and_existing_file_is_not_written(self):
        target = self.root / "not-created" / "output.json"
        self.assertEqual(BOUNDARY.require_external_write(target), target)
        self.assertFalse(target.parent.exists())
        existing = self.root / "existing.json"
        existing.write_bytes(b"unchanged")
        self.assertEqual(BOUNDARY.require_external_write(existing), existing)
        self.assertEqual(existing.read_bytes(), b"unchanged")

    def test_both_recognized_markers_and_explicit_unmarked_package_root(self):
        for marker in ("SKILL.md", "bundle-manifest.json"):
            package = self.root / marker.replace(".", "-")
            package.mkdir()
            (package / marker).write_text("synthetic", encoding="utf-8")
            with self.subTest(marker=marker), self.assertRaisesRegex(ValueError, "installed Skill"):
                BOUNDARY.require_external_write(package / "missing" / "out")
            self.assertFalse((package / "missing").exists())
        package = self.root / "unmarked"
        with self.assertRaisesRegex(ValueError, "installed Skill"):
            BOUNDARY.require_external_write(package / "out", (package,))

    def test_reparse_and_symlink_components_are_rejected_without_creating_descendants(self):
        parent = self.root / "linked"
        parent.mkdir()
        original = Path.lstat
        for mode, attributes in ((stat.S_IFLNK, 0), (stat.S_IFDIR, 0x400)):
            def synthetic_lstat(path, *args, **kwargs):
                return SimpleNamespace(st_mode=mode, st_file_attributes=attributes) if path == parent else original(path, *args, **kwargs)
            with self.subTest(mode=mode, attributes=attributes), patch.object(Path, "lstat", synthetic_lstat):
                with self.assertRaisesRegex(ValueError, "link/reparse"):
                    BOUNDARY.require_external_write(parent / "missing" / "out")
            self.assertEqual(list(parent.iterdir()), [])

    def test_unc_devices_and_traversal_fail_before_filesystem_probe(self):
        values = ("//host/share/out", r"\\host\share\out", r"\\?\C:\out",
                  self.root / "x" / ".." / "out", self.root / "NUL.txt", self.root / "out:stream")
        with patch.object(os.path, "lexists", side_effect=AssertionError("must not probe rejected path")):
            for path in values:
                with self.subTest(path=str(path)), self.assertRaises(ValueError):
                    BOUNDARY.require_external_write(path)


if __name__ == "__main__":
    unittest.main()
