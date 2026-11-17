"""Global colour choice travels through real computed builds without re-layout."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from xml.etree import ElementTree as ET

PROJECT = Path(__file__).resolve().parents[1]
SCRIPTS = PROJECT / "skill-src/how-to-report/scripts"
sys.path[:0] = [str(SCRIPTS), str(PROJECT / "skill-src/shared/scripts")]
from presentation_palette import (apply_palette, contrast_ratio, describe_palette,
                                  interpolate_scale, label_ink, palette_catalog, palette_color)
from presentation_chart_assets import chart_story
from presentation_compiler import build_project
from presentation_library import profile_path
from presentation_typography import resolve_text_style
from report_ppt import TemplateInputError


class PaletteTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="ppt-palette-")
        self.root = Path(self.temp.name)
        self.tokens = json.loads(profile_path().read_text(encoding="utf-8"))

    def tearDown(self):
        self.temp.cleanup()

    def author(self, identifier=None):
        author = chart_story("bar", {"categories": ["甲", "乙", "丙"],
            "series": [{"name": "示例", "values": [10, 20, 30]}]}, {"title": "配色传播验证"})
        if identifier is not None:
            author["brief"]["palette_id"] = identifier
        children = author["pages"][0]["layout"]["children"]
        children[1]["height"] = 350
        children.insert(1, {"id": "body", "type": "leaf", "element": {"type": "text", "role": "body", "text": "正文保持80%黑"}})
        children.insert(2, {"id": "state", "type": "leaf", "height": 30,
            "element": {"type": "shape", "shape": "rect", "fill": "success"}})
        return author

    def test_catalog_sources_contrast_and_fixed_text_semantics(self):
        records = palette_catalog()
        self.assertEqual(len(records), 6)
        self.assertAlmostEqual(contrast_ratio("#000000", "#FFFFFF"), 21)
        for item in records:
            self.assertEqual(item["roles"]["body"], "#333333")
            self.assertEqual(item["roles"]["muted"], "#A6A6A6")
            if item["id"] == "consulting-spectrum":
                self.assertEqual(item["roles"]["danger"], "#C7473D")
                self.assertEqual(item["roles"]["success"], "#4F7F1C")
                self.assertIn("user-provided", item["provenance"]["relationship"])
            else:
                self.assertEqual(item["roles"]["danger"], "#C21E2B")
                self.assertEqual(item["roles"]["success"], "#198038")
            self.assertEqual(len(item["categorical"]), 6)
            self.assertGreater(item["contrast"]["body"]["on_white"], 12)
            self.assertLess(item["contrast"]["muted"]["on_white"], 3)
            if item["id"] not in {"report-default", "consulting-spectrum"}:
                self.assertTrue(item["provenance"]["sources"])

    def test_default_is_exact_and_new_themes_do_not_mutate_typography(self):
        self.assertEqual(apply_palette(self.tokens, None), self.tokens)
        self.assertEqual(apply_palette(self.tokens, "report-default"), self.tokens)
        original = copy.deepcopy(self.tokens)
        changed = apply_palette(self.tokens, "ant-business")
        self.assertEqual(self.tokens, original)
        self.assertEqual(changed["font"], self.tokens["font"])
        self.assertAlmostEqual(resolve_text_style(changed, "body")["font_size"] * .75, 14)
        self.assertEqual(palette_color(changed, "danger"), "#C21E2B")
        self.assertEqual(palette_color(changed, "body"), "#333333")

    def test_real_builds_change_only_colour_and_lock_registry(self):
        svgs = []
        for key in (None, "report-default", "ant-business", "carbon-teal"):
            out = self.root / (key or "omitted")
            build_project(self.author(key), out, geometry_policy="computed")
            svgs.append(next((out / "svg_output").glob("*.svg")).read_text(encoding="utf-8"))
            receipt = json.loads((out / "engine-receipt.json").read_text(encoding="utf-8"))
            self.assertIn("assets/design-system/palettes.json", receipt["data_dependencies"])
            self.assertEqual(receipt["palette_id"], key)
            self.assertIn('#333333', svgs[-1])
            self.assertIn('#198038', svgs[-1])
        self.assertEqual(svgs[0], svgs[1])
        self.assertNotEqual(svgs[2], svgs[3])
        self.assertIn('#0050B3', svgs[2])
        self.assertIn('#005D5D', svgs[3])
        def geometry(xml):
            tree = ET.fromstring(xml)
            for node in tree.iter():
                node.attrib.pop("fill", None)
                node.attrib.pop("stroke", None)
            return ET.tostring(tree)
        self.assertEqual(geometry(svgs[2]), geometry(svgs[3]))

    def test_invalid_id_cannot_publish(self):
        for key in ("unknown", 123, {}, "../../custom"):
            with self.subTest(key=key):
                with self.assertRaises(ValueError):
                    build_project(self.author(key), self.root / "invalid", geometry_policy="computed")
                self.assertFalse((self.root / "invalid").exists())

    def test_scale_endpoints_and_neutral_are_not_reversed(self):
        selected = describe_palette("carbon-indigo")
        self.assertEqual(interpolate_scale(selected["sequential"], 0, 0, 10), selected["sequential"][0])
        self.assertEqual(interpolate_scale(selected["sequential"], 10, 0, 10), selected["sequential"][-1])
        self.assertEqual(interpolate_scale(selected["diverging"], 0, -10, 10), '#F0F0F0')

    def test_small_labels_use_actual_luminance_contrast(self):
        for palette in palette_catalog()[1:]:
            for color in palette["categorical"]:
                self.assertGreaterEqual(contrast_ratio(label_ink(color), color), 4.5)
        self.assertEqual(label_ink("#FFFFFF"), "#333333")

    def test_chart_cli_carries_top_level_palette_id(self):
        req = {"asset": "chart.bar", "data": {"categories": ["A", "B"],
            "series": [{"name": "observed", "values": [10, 20]}]}, "palette_id": "carbon-indigo"}
        path = self.root / "request.json"
        path.write_text(json.dumps(req), encoding="utf-8")
        result = subprocess.run([sys.executable, "-B", str(SCRIPTS / "report_engine.py"), "chart-build",
            "--request", str(path), "--output", str(self.root / "cli")], cwd=self.root, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        author = json.loads((self.root / "cli/inputs/presentation.project.json").read_text(encoding="utf-8"))
        self.assertEqual(author["brief"]["palette_id"], "carbon-indigo")


if __name__ == "__main__":
    unittest.main()
