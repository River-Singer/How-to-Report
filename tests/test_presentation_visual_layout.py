"""Span negotiation and semantic native visual composition, without model calls."""
import copy
import json
import os
from pathlib import Path
import sys
import subprocess
import tempfile
import unittest
import zipfile
from xml.etree import ElementTree as ET

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "skill-src/shared/scripts"))
sys.path.insert(0, str(PROJECT / "skill-src/how-to-report/scripts"))

from presentation_layout import LayoutError, lower_layout_page, validate_layout_page
from presentation_document import resolve_text, resolve_value
from presentation_svg import SceneRenderer
from report_ppt import load_template


def text(identifier, content="Short text", **kwargs):
    return {"id": identifier, "type": "leaf", "element": {"type": "text", "role": "body", "text": content}, **kwargs}


def page(root):
    return {"id": "visual-layout", "kind": "layout", "layout_version": "0.1", "layout": root}


def section(identifier, kind="rail", **kwargs):
    return {"id": identifier, "type": "column", "surface": {"fill": "surfaceMuted", "accent": {"kind": kind}},
            "children": [text(identifier + "-copy")], **kwargs}


class VisualLayoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _, _, cls.tokens = load_template()

    def solve(self, root, width=600, height=500):
        scene, report = lower_layout_page(page(root), {}, [width, height], self.tokens)
        return scene, {item["id"]: item for item in report["nodes"]}

    def test_spanning_text_measured_at_combined_width_and_stable_input(self):
        root = {"id": "grid", "type": "grid", "columns": [{"fr": 1}] * 3, "gap": 12,
                "children": [text("wide", "Complete content wraps at the allocated width. " * 2, column_span=2),
                             text("right"), text("next", column_span=3)]}
        original = copy.deepcopy(root)
        scene, nodes = self.solve(root)
        self.assertEqual(root, original)
        self.assertAlmostEqual(nodes["wide"]["frame"][2], 396)
        self.assertEqual(nodes["wide"]["measurement_width"], 396)
        self.assertEqual(nodes["wide"]["grid_cell"], {"row": 0, "column": 0, "column_span": 2, "allocated_width": 396})
        self.assertAlmostEqual(nodes["right"]["frame"][0], 408)
        self.assertEqual(nodes["next"]["frame"][2], 600)
        self.assertEqual(nodes["next"]["grid_cell"]["row"], 1)
        narrow = copy.deepcopy(root)
        narrow["children"][0]["column_span"] = 1
        _, narrow_nodes = self.solve(narrow)
        self.assertGreater(narrow_nodes["wide"]["line_count"], nodes["wide"]["line_count"])
        self.assertEqual(scene, self.solve(root)[0])

    def test_spans_preserve_order_without_backfilling_holes(self):
        root = {"id": "g", "type": "grid", "columns": [100, 200, 100], "gap": 10,
                "children": [text("a", column_span=2), text("b", column_span=2), text("c")]}
        _, nodes = self.solve(root)
        self.assertEqual([nodes[key]["grid_cell"]["row"] for key in ("a", "b", "c")], [0, 1, 1])
        self.assertEqual(nodes["a"]["frame"][2], 310)
        self.assertEqual(nodes["c"]["frame"][0], 320)

    def test_fixed_spanned_minimum_uses_sum_instead_of_equal_track_minimum(self):
        root = {"id": "g", "type": "grid", "columns": [100, 200], "gap": 10,
                "children": [text("a", column_span=2, min_width=310)]}
        self.assertEqual(self.solve(root)[1]["a"]["frame"][2], 310)
        root["children"][0]["min_width"] = 311
        with self.assertRaisesRegex(LayoutError, "fixed spanned tracks"):
            self.solve(root)

    def test_fractional_span_minimum_and_overlapping_constraints(self):
        root = {"id": "g", "type": "grid", "columns": [{"fr": 1}, {"fr": 2}, {"fr": 1}], "gap": 10,
                "children": [text("a", column_span=2, min_width=360), text("b", min_width=80),
                             text("c", min_width=100), text("d", column_span=2, min_width=300)]}
        _, nodes = self.solve(root)
        self.assertGreaterEqual(nodes["a"]["frame"][2], 360)
        self.assertGreaterEqual(nodes["d"]["frame"][2], 300)

    def test_span_input_failures_are_author_addressable(self):
        root = {"id": "g", "type": "grid", "columns": [{"fr": 1}] * 2, "children": [text("a", column_span=2)]}
        for span in (0, -1, 1.5, True, "2", 3, None, []):
            with self.subTest(span=span):
                invalid = copy.deepcopy(root)
                invalid["children"][0]["column_span"] = span
                with self.assertRaisesRegex(LayoutError, "column_span"):
                    validate_layout_page(page(invalid))
        root["columns"] = {"auto_fit": 100}
        with self.assertRaisesRegex(LayoutError, "auto_fit"):
            validate_layout_page(page(root))
        with self.assertRaisesRegex(LayoutError, "direct grid"):
            validate_layout_page(page(text("root", column_span=1)))

    def test_rows_validate_after_actual_span_placement(self):
        root = {"id": "g", "type": "grid", "columns": [100] * 3, "rows": [100],
                "children": [text("a", column_span=2), text("b", column_span=2)]}
        with self.assertRaisesRegex(LayoutError, "occupied row count"):
            self.solve(root)
        root["rows"] = [100, 100]
        self.assertEqual(self.solve(root)[1]["b"]["frame"][1], 100)

    def test_span_growth_fails_instead_of_shrinking_or_losing_text(self):
        root = {"id": "g", "type": "grid", "columns": [100, 100], "children": [text("a", "Content must remain. " * 30, column_span=2)]}
        with self.assertRaises(LayoutError) as error:
            self.solve(root, height=100)
        self.assertEqual(error.exception.diagnostic["code"], "layout_overflow")

    def test_accent_reserves_insets_without_mutating_author(self):
        for kind, expected in (("rail", [16, 0, 0, 0]), ("rule", [0, 16, 0, 0]), ("bracket", [16, 16, 0, 16])):
            with self.subTest(kind=kind):
                root = section("s", kind)
                snapshot = copy.deepcopy(root)
                scene, nodes = self.solve(root)
                self.assertEqual(root, snapshot)
                self.assertEqual(nodes["s"]["effective_padding"], expected)
                self.assertEqual(nodes["s-copy"]["frame"][:2], expected[:2])
                accents = [item for item in scene["elements"] if "--accent-" in item["id"]]
                self.assertTrue(all(item["role"] == "decoration" and item["fill"] == "primary" for item in accents))
                self.assertEqual(len(accents), 3 if kind == "bracket" else 1)
                self.assertLess(scene["elements"].index(accents[-1]), next(i for i, item in enumerate(scene["elements"]) if item["id"] == "s-copy"))

    def test_accent_tracks_changed_parent_geometry(self):
        root = section("s", "bracket", padding=24)
        small, _ = self.solve(root, width=300, height=200)
        large, _ = self.solve(root, width=600, height=400)
        self.assertEqual([item["id"] for item in small["elements"]], [item["id"] for item in large["elements"]])
        bottom = lambda scene: next(item for item in scene["elements"] if item["id"] == "s--accent-bottom")["frame"]
        self.assertEqual(bottom(large)[1] - bottom(small)[1], 200)

    def test_accent_rejects_bad_parameters_and_reserved_id_collision(self):
        for accent in ({"kind": []}, {"kind": "rail", "thickness": 0}, {"kind": "rail", "gap": -1},
                       {"kind": "rail", "color": "none"}, {"kind": "rule", "gradient": True}):
            root = section("s")
            root["surface"]["accent"] = accent
            with self.subTest(accent=accent), self.assertRaises(LayoutError):
                self.solve(root)
        root = section("s")
        root["children"][0]["id"] = "s--accent-rail"
        with self.assertRaisesRegex(LayoutError, "collides"):
            self.solve(root)

    def test_sequence_has_explicit_relation_stable_endpoints_and_behind_child_layer(self):
        root = {"id": "flow", "type": "row", "connect": "sequence", "relation_ref": "ordered-handoff", "gap": 40,
                "children": [section("a", grow=1, basis=0), section("b", grow=1, basis=0)]}
        scene, nodes = self.solve(root)
        link = next(item for item in scene["elements"] if item["type"] == "connector")
        self.assertEqual((link["from"], link["to"]), ("a--surface", "b--surface"))
        self.assertEqual(link["relation_ref"], "ordered-handoff")
        self.assertEqual(scene["elements"][0], link)
        self.assertEqual(nodes["flow"]["connector_ids"], [link["id"]])
        svg = SceneRenderer(scene, self.tokens, None, resolve_text, resolve_value, {}).render()[0]
        ids = [item.get("id") for item in ET.fromstring(svg)]
        self.assertLess(ids.index(link["id"]), ids.index("a--surface"))
        parsed_link = next(item for item in ET.fromstring(svg) if item.get("id") == link["id"])
        self.assertEqual(parsed_link.get("data-pptx-object"), "connector")
        self.assertIsNotNone(parsed_link.get("data-pptx-start-shape-id"))
        self.assertEqual(scene, self.solve(root)[0])
        del root["connect"]
        self.assertFalse(any(item["type"] == "connector" for item in self.solve(root)[0]["elements"]))

    def test_column_sequence_ports_and_generated_id_collision(self):
        root = {"id": "flow", "type": "column", "connect": "sequence", "gap": 30,
                "children": [section("a"), section("b")]}
        scene, _ = self.solve(root)
        link = next(item for item in scene["elements"] if item["type"] == "connector")
        self.assertEqual((link["from_port"], link["to_port"]), ("bottom", "top"))
        root["children"][0]["children"][0]["id"] = link["id"]
        with self.assertRaisesRegex(LayoutError, "collides"):
            self.solve(root)

    def test_sequence_invalid_targets_and_gap(self):
        for children, gap in (([text("a"), text("b")], 20), ([section("a"), section("b")], 0), ([section("a")], 20)):
            root = {"id": "flow", "type": "row", "connect": "sequence", "gap": gap, "children": children}
            with self.subTest(gap=gap, count=len(children)), self.assertRaises(LayoutError):
                self.solve(root)

    def test_solid_registered_preset_surface_serializes_with_native_identity(self):
        root = section("stage", padding=30)
        root["surface"] = {"shape": "chevron", "fill": "primary"}
        scene, _ = self.solve(root)
        svg = SceneRenderer(scene, self.tokens, None, resolve_text, resolve_value, {}).render()[0]
        preset = next(node for node in ET.fromstring(svg) if node.get("id") == "stage--surface")
        self.assertEqual(preset.get("stroke"), "none")
        self.assertIsNone(preset.get("stroke-width"))
        self.assertEqual(preset.get("data-pptx-shape-id"), "100")

    def test_preset_sequence_normal_computed_cli_exports_native_attached_connectors(self):
        root = {"id": "sequence", "type": "row", "padding": 40, "gap": 36, "connect": "sequence", "children": []}
        for key in ("a", "b"):
            child = section(key, padding=[40, 30, 40, 30], basis=0, grow=1)
            child["surface"] = {"shape": "chevron", "fill": "primary"}
            root["children"].append(child)
        author = {"schema_version": "0.1", "project_id": "native-preset-regression", "revision": 1,
                  "brief": {}, "sources": [], "facts": {}, "pages": [page(root)]}
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            source, target = folder / "author.json", folder / "result.pptx"
            source.write_text(json.dumps(author), encoding="utf-8")
            result = subprocess.run([sys.executable, str(PROJECT / "skill-src/how-to-report/scripts/report_engine.py"),
                                     "build", "--input", str(source), "--output", str(folder / "build"),
                                     "--pptx", str(target), "--geometry-policy", "computed"],
                                    capture_output=True, text=True, encoding="utf-8", timeout=90,
                                    env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "PYTHONIOENCODING": "utf-8"})
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            ns = {"p": "http://schemas.openxmlformats.org/presentationml/2006/main",
                  "a": "http://schemas.openxmlformats.org/drawingml/2006/main"}
            with zipfile.ZipFile(target) as package:
                slide = ET.fromstring(package.read("ppt/slides/slide1.xml"))
            tree = list(slide.find("p:cSld/p:spTree", ns))
            presets = [item for item in tree if item.find('.//a:prstGeom[@prst="chevron"]', ns) is not None]
            connector = next(item for item in tree if item.tag.endswith("}cxnSp"))
            self.assertEqual(len(presets), 2)
            identities = [item.find(".//p:cNvPr", ns).get("id") for item in presets]
            self.assertEqual(connector.find(".//a:stCxn", ns).get("id"), identities[0])
            self.assertEqual(connector.find(".//a:endCxn", ns).get("id"), identities[1])
            self.assertLess(tree.index(connector), min(tree.index(item) for item in presets))
            all_ids = [item.get("id") for item in slide.findall(".//p:cNvPr", ns)]
            self.assertEqual(len(all_ids), len(set(all_ids)))


if __name__ == "__main__":
    unittest.main()
