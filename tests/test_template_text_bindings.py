"""Synthetic regressions for bound text at the author/template boundary."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from xml.etree import ElementTree as ET
from zipfile import ZipFile

PROJECT = Path(__file__).resolve().parents[1]
SCRIPTS = PROJECT / "skill-src" / "how-to-report" / "scripts"
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(PROJECT / "skill-src" / "shared" / "scripts"))

from presentation_compiler import _resolve_template_text, _template_parameters, build_project
from presentation_document import apply_patch_to_document, evaluate_facts
from report_ppt import TemplateInputError, load_template
import ppt_runtime


def author_document():
    return {
        "schema_version": "0.1", "project_id": "template-text-fixture", "revision": 1,
        "brief": {"metadata": {"parts": ["keep", "as", "data"]}}, "sources": [],
        "facts": {"a": {"value": 12}, "b": {"value": 5},
                  "gap": {"derived": {"op": "difference", "args": ["a", "b"]}}},
        "pages": [{"id": "overview", "kind": "template", "notes": "Synthetic fixture",
                   "template": {"family": "parallel", "variant": "columns-2",
                                "content": {"title": {"parts": ["Values ", {"ref": "a"}]},
                                            "items": [{"title": "Total", "body": {"parts": [
                                                "Value ", {"ref": "a"}, " and ", {"ref": "b"}]}},
                                                      {"title": "Difference", "body": {"parts": [
                                                          "Gap ", {"ref": "gap"}]}}]}}}],
    }


def svg_texts(project):
    return ["".join(ET.parse(path).getroot().itertext())
            for path in sorted((project / "svg_output").glob("*.svg"))]


class TemplateTextBindingTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="template-text-binding-")
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        _, self.catalog, _ = load_template()

    def test_nested_parts_resolve_and_original_author_is_preserved(self):
        document = author_document()
        document["pages"][0]["template"]["content"]["items"][0]["body"] = {
            "parts": ["Total ", {"parts": [{"ref": "a", "format": ",.0f"}, " units"]}, "."]}
        original = copy.deepcopy(document)
        target = self.base / "nested"
        build_project(document, target)
        self.assertIn("Total 12 units.", svg_texts(target)[0])
        self.assertEqual(document, original)
        self.assertEqual(json.loads((target / "inputs/presentation.project.json").read_text(encoding="utf-8")), original)

    def test_fact_patch_updates_template_text_and_native_chart_values(self):
        document = author_document()
        document["pages"].append({"id": "chart", "kind": "template", "template": {
            "family": "chart", "content": {
                "title": "Fixture quantities", "categories": [{"parts": ["Group ", {"ref": "a"}]}, "B"],
                "series": [{"name": {"parts": ["Series ", {"ref": "b"}]},
                            "values": [{"ref": "a"}, {"ref": "b"}]}],
                "conclusions": {"parts": ["Difference ", {"ref": "gap"}]}}}})
        before = self.base / "before"
        build_project(document, before)
        changed = apply_patch_to_document(document, [{"op": "replace", "path": "/facts/a/value", "value": 14}],
                                          expected_revision=1, operation_id="update-quantity")
        after = self.base / "after"
        build_project(changed, after)
        self.assertIn("Value 12 and 5", svg_texts(before)[0])
        self.assertIn("Value 14 and 5", svg_texts(after)[0])
        self.assertIn("Gap 9", svg_texts(after)[0])
        self.assertIn("Group 14", svg_texts(after)[1])
        self.assertIn("Difference 9", svg_texts(after)[1])
        ppt_runtime.check_project(after, after / "tokens.json")
        output = self.base / "bound.pptx"
        ppt_runtime.export_project(after, output, after / "tokens.json")
        with ZipFile(output) as package:
            slide = ET.fromstring(package.read("ppt/slides/slide1.xml"))
            text = "".join(node.text or "" for node in slide.findall(".//a:t", ppt_runtime.NS))
            self.assertIn("Value 14 and 5", text)
            chart_name = next(name for name in package.namelist()
                              if name.startswith("ppt/charts/chart") and name.endswith(".xml"))
            chart = ET.fromstring(package.read(chart_name))
            ns = {"c": "http://schemas.openxmlformats.org/drawingml/2006/chart"}
            values = [node.text for node in chart.findall(".//c:val//c:numCache/c:pt/c:v", ns)]
            self.assertEqual(values, ["14", "5"])

    def test_source_text_nodes_use_additional_property_string_types(self):
        family = self.catalog["families"]["source-house"]
        variant = min(family["variants"].values(), key=lambda item: len(item["fields"]))
        field = next(key for key, definition in variant["fields"].items() if definition["max_length"] >= 8)
        content = copy.deepcopy(variant["prototype_content"])
        content["nodes"][field] = {"parts": ["值", {"ref": "a"}]}
        document = author_document()
        document["pages"][0]["template"] = {"family": "source-house", "variant": variant["id"], "content": content}
        target = self.base / "source-node"
        receipt = build_project(document, target)
        self.assertIn("值12", svg_texts(target)[0])
        mapping = receipt["pages"][0]["objects"]
        binding = next(item for item in mapping if item.get("field") == "nodes." + field)
        self.assertEqual(binding["source_ref"], variant["fields"][field]["source_ref"])

    def test_source_chart_slots_keep_numeric_arrays(self):
        family_id, variant = next((family_id, variant)
                                  for family_id, family in self.catalog["families"].items()
                                  for variant in family["variants"].values() if variant.get("chart_slots"))
        content = copy.deepcopy(variant["prototype_content"])
        chart = next(iter(content["charts"].values()))
        chart["title"] = {"parts": ["Trend ", {"ref": "a"}]}
        chart["categories"] = [{"parts": ["A", {"ref": "b"}]}, "B"]
        chart["series"] = [{"name": {"parts": ["Count ", {"ref": "a"}]},
                            "values": [{"ref": "a"}, {"ref": "b"}]}]
        document = author_document()
        document["pages"][0]["template"] = {"family": family_id, "variant": variant["id"], "content": content}
        target = self.base / "source-chart"
        build_project(document, target)
        svg = next((target / "svg_output").glob("*.svg")).read_text(encoding="utf-8")
        self.assertIn("Trend 12", svg)
        self.assertIn("A5", svg)
        parameters = _template_parameters(document["pages"][0]["template"], self.catalog,
                                          evaluate_facts(document), "fixture")
        self.assertEqual(next(iter(parameters["content"]["charts"].values()))["series"][0]["values"], [12, 5])

    def test_nontext_metadata_and_structural_arrays_are_preserved(self):
        catalog = copy.deepcopy(self.catalog)
        properties = catalog["families"]["parallel"]["content_schema"]["properties"]
        properties["metadata"] = {"type": "object", "additionalProperties": True}
        properties["charts"] = {"type": "object", "additionalProperties": True}
        template = copy.deepcopy(author_document()["pages"][0]["template"])
        metadata = {"parts": ["keep", "structure"], "enabled": True}
        chart_metadata = {"slot": {"title": {"parts": ["retain", "object"]}, "values": [1, 2]}}
        template["content"].update(metadata=metadata, charts=chart_metadata)
        result = _template_parameters(template, catalog, {"a": 12, "b": 5, "gap": 7}, "fixture")
        self.assertEqual(result["content"]["metadata"], metadata)
        self.assertEqual(result["content"]["charts"], chart_metadata)
        self.assertIsInstance(result["content"]["items"], list)
        self.assertEqual(_resolve_template_text(["x"], {"type": "array", "items": False}, {}, "fixture"), ["x"])

    def test_invalid_wrappers_and_unknown_references_do_not_publish(self):
        bad_wrappers = [{"parts": "not-an-array"}, {"parts": [True]}, {"parts": [None]},
                        {"parts": ["text"], "unknown": 1},
                        {"parts": [{"ref": "a", "extra": True}]},
                        {"parts": [{"parts": ["nested"], "extra": True}]}]
        for index, wrapper in enumerate(bad_wrappers):
            with self.subTest(wrapper=wrapper):
                document = author_document()
                document["pages"][0]["template"]["content"]["items"][0]["body"] = wrapper
                target = self.base / f"bad-{index}"
                with self.assertRaisesRegex(TemplateInputError, r"pages\.0\.template\.content\.items\.0\.body"):
                    build_project(document, target)
                self.assertFalse(target.exists())
        document = author_document()
        document["pages"][0]["template"]["content"]["title"] = {"parts": [{"ref": "missing"}]}
        with self.assertRaisesRegex(ValueError, "unknown fact reference"):
            build_project(document, self.base / "missing")
        self.assertFalse((self.base / "missing").exists())

    def test_bound_text_keeps_length_and_measured_capacity_checks(self):
        for index, text in enumerate(("x" * 121, "W" * 120)):
            with self.subTest(text_length=len(text)):
                document = author_document()
                document["pages"][0]["template"]["content"]["items"][0]["body"] = {"parts": [text]}
                target = self.base / f"overflow-{index}"
                with self.assertRaises(TemplateInputError):
                    build_project(document, target)
                self.assertFalse(target.exists())

    def test_normal_cli_build_from_unrelated_cwd(self):
        source = self.base / "author.json"
        source.write_text(json.dumps(author_document(), ensure_ascii=False), encoding="utf-8")
        target = self.base / "cli-project"
        pptx = self.base / "cli.pptx"
        result = subprocess.run([sys.executable, "-B", str(SCRIPTS / "report_engine.py"), "build",
                                 "--input", str(source), "--output", str(target), "--pptx", str(pptx)],
                                cwd=self.base, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stderr)
        receipt = json.loads(result.stdout)
        self.assertEqual(receipt["check_status"], "pass")
        self.assertEqual(receipt["asset_usage"]["template_pages"], 1)
        self.assertTrue(pptx.is_file())
        self.assertIn("Value 12 and 5", svg_texts(target)[0])


if __name__ == "__main__":
    unittest.main()
