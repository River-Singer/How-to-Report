"""Unified discovery preserves source ownership and truthful capability states."""
import hashlib
import json
from pathlib import Path
import sys
import shutil
import tempfile
import unittest


PROJECT = Path(__file__).resolve().parents[1]
SOURCE = PROJECT / "skill-src/how-to-report"
sys.path.insert(0, str(SOURCE / "scripts"))
from presentation_library import library, profile_identity, profile_path
from report_ppt import DEFAULT_TEMPLATE, read_json


class LibraryTests(unittest.TestCase):
    def test_template_adapter_has_all_current_variants_once(self):
        found, offset = [], 0
        while True:
            result = library(kind="template", offset=offset, limit=37)
            found.extend(record["id"] for record in result["items"])
            if result["next_offset"] is None:
                break
            offset = result["next_offset"]
        self.assertEqual(len(found), 170)
        self.assertEqual(len(found), len(set(found)))

    def test_ft_versions_counts_license_and_nonexecutable_mapping(self):
        result = library(kind="chart-vocabulary", limit=100)
        self.assertEqual(result["total"], 68)
        self.assertTrue(all(not record["executable"] for record in result["items"]))
        self.assertEqual(library(kind="chart-vocabulary", status="high_level", limit=100)["total"], 10)
        description = library(identifier="chart-vocabulary.sunburst")
        self.assertEqual(description["status"], "backend_only")
        self.assertEqual(description["version_summary"]["poster_unique"], 66)
        self.assertEqual(description["provenance"]["license"]["id"], "CC-BY-SA-4.0")

    def test_component_contract_and_profile_are_real(self):
        component = library(identifier="component.progress-ring")
        self.assertIn("progress-ring", component["contract"]["definitions"])
        self.assertTrue(component["executable"])
        profile = library(identifier="profile.report-14pt")
        self.assertFalse(profile["executable"])
        self.assertAlmostEqual(profile["tokens"]["font"]["sizes"]["body"] * .75, 14)
        self.assertEqual(profile["tokens"]["theme"]["slots"]["dk1"], "#333333")
        self.assertEqual(profile["tokens"]["theme"]["slots"]["dk2"], "#A6A6A6")
        self.assertEqual(profile_identity()["sha256"], hashlib.sha256(profile_path().read_bytes()).hexdigest())

    def test_filters_and_limits_are_bounded(self):
        self.assertEqual(library(kind="recipe", query="证据")["total"], 1)
        self.assertTrue(library(kind="component", relationship="part-to-whole")["items"])
        self.assertEqual(library(kind="chart-vocabulary", executable=True)["total"], 0)
        for kwargs in ({"limit": 0}, {"limit": 101}, {"offset": -1}, {"offset": True},
                       {"kind": "unknown"}, {"status": "ready"}, {"query": "x" * 257}):
            with self.assertRaises(ValueError):
                library(**kwargs)

    def test_package_refs_exist_and_no_research_absolute_paths(self):
        for record in library(kind="recipe", limit=10)["items"]:
            for key in ("schema_ref", "compiler_ref", "example_ref"):
                self.assertTrue((SOURCE / record[key]).is_file(), record[key])
            for preview in record["preview_refs"]:
                self.assertTrue((SOURCE / preview["ref"]).is_file(), preview["ref"])
            self.assertNotIn("D:\\", json.dumps(record))
        vocabulary = read_json(SOURCE / "assets/design-system/visual-vocabulary.json")
        self.assertIn("Root verified", vocabulary["screenshot_status"])

    def test_custom_template_component_defaults_use_custom_tokens(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "custom-template"
            (root / "templates").mkdir(parents=True)
            shutil.copyfile(DEFAULT_TEMPLATE / "templates/page-catalog.json", root / "templates/page-catalog.json")
            shutil.copyfile(DEFAULT_TEMPLATE / "templates/tokens.schema.json", root / "templates/tokens.schema.json")
            tokens = read_json(DEFAULT_TEMPLATE / "templates/tokens.json")
            tokens["theme"]["slots"]["dk1"] = "#123456"
            (root / "templates/tokens.json").write_text(json.dumps(tokens), encoding="utf-8")
            result = library(root, identifier="component.comparison")
            self.assertEqual(result["contract"]["style_defaults"]["color"], "#123456")


if __name__ == "__main__":
    unittest.main()
