"""Thick cycle geometry, actual safe text containment and native export."""
from __future__ import annotations

import copy
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from xml.etree import ElementTree as ET
from zipfile import ZipFile

PROJECT = Path(__file__).resolve().parents[1]
SCRIPTS = PROJECT / "skill-src/how-to-report/scripts"
sys.path[:0] = [str(SCRIPTS), str(PROJECT / "skill-src/shared/scripts")]

from presentation_cycle_arrows import rect_in_sector
from presentation_palette import apply_palette
from presentation_topology import TopologyError, lower_topology, topology_catalog
from report_ppt import TemplateInputError


def ring(count=4, size=500):
    return {"id": "ring", "type": "component", "component": "topology", "layout": "cycle", "variant": "arrow-ring",
            "frame": [100, 100, 700, size], "nodes": [{"id": "n"+str(i), "label": "阶段"+str(i+1)} for i in range(count)]}


class CycleArrowsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tokens = json.loads((PROJECT / "skill-src/how-to-report/assets/design-profiles/report-14pt.json").read_text(encoding="utf-8"))

    def lower(self, item, tokens=None):
        return lower_topology(item, {}, [1280, 720], tokens or self.tokens)

    def test_count_recalculates_disjoint_arrows_and_proven_text_safe_boxes(self):
        for count in range(3, 7):
            with self.subTest(count=count):
                result = self.lower(ring(count))
                report = result["metadata"]["topology_report"]
                paths = [child for child in result["children"] if child["type"] == "shape"]
                self.assertEqual(len(paths), count)
                self.assertTrue(all(path["shape"] == "path" and path["d"].count(" A ") == 2 for path in paths))
                self.assertFalse(any(child["type"] == "connector" for child in result["children"]))
                self.assertAlmostEqual(sum(abs(s["sweep_radians"])+report["gap_radians"] for s in report["segments"]), math.tau)
                for segment in report["segments"]:
                    self.assertTrue(rect_in_sector(segment["label_safe_frame"], report["center"],
                        report["body_radii"][0]+report["label_clearance"], report["body_radii"][1]-report["label_clearance"],
                        segment["start_radians"], segment["body_sweep_radians"]))
                    self.assertEqual(report["measurements"][segment["node_id"]]["font_size"], self.tokens["font"]["sizes"]["body"])
                self.assertIn("qualitative", report["encoding"])

    def test_safe_box_checks_inner_disk_intersection_even_when_corners_clear(self):
        # Four corners can be outside a hole while the middle of the rectangle
        # crosses it; merely checking corners would produce unsafe labels.
        self.assertFalse(rect_in_sector([-9, 2, 18, 2], [0, 0], 5, 20, 0, math.pi))

    def test_reverse_cycle_changes_geometry_direction_not_stage_identities(self):
        item = ring()
        forward = self.lower(item)
        item["edges"] = [{"id": "e"+str(i), "from": "n"+str(i), "to": "n"+str((i-1)%4)} for i in range(4)]
        reverse = self.lower(item)
        self.assertEqual(reverse["metadata"]["topology_report"]["direction"], "counterclockwise")
        self.assertEqual([c["id"] for c in forward["children"]], [c["id"] for c in reverse["children"]])
        self.assertNotEqual(forward["children"][0]["d"], reverse["children"][0]["d"])
        for s in reverse["metadata"]["topology_report"]["segments"]:
            self.assertLess(s["sweep_radians"], 0)

    def test_radius_recalculates_and_long_text_cannot_be_hidden_by_shrinking(self):
        item = ring()
        before = self.lower(item)
        item["frame"][3] = 550
        after = self.lower(item)
        self.assertGreater(after["metadata"]["topology_report"]["radius"], before["metadata"]["topology_report"]["radius"])
        item["nodes"][0]["label"] = "必须保留的长标签" * 30
        with self.assertRaises(TopologyError) as raised:
            self.lower(item)
        self.assertEqual(raised.exception.diagnostic["reason"], "text_overflow")
        self.assertEqual(raised.exception.diagnostic["font_size"], self.tokens["font"]["sizes"]["body"])
        with self.assertRaises(TopologyError):
            self.lower(ring(size=100))

    def test_palette_and_label_ink_are_resolved_and_ids_are_deterministic(self):
        item = ring(6)
        original = copy.deepcopy(item)
        tokens = apply_palette(self.tokens, "consulting-spectrum")
        result = self.lower(item, tokens)
        segments = result["metadata"]["topology_report"]["segments"]
        self.assertEqual([s["fill"] for s in segments], tokens["color"]["palette"]["categorical"][:6])
        self.assertTrue(all(s["label_contrast_ratio"] >= 4.5 for s in segments))
        self.assertEqual(item, original)
        self.assertEqual(result, self.lower(item, tokens))

    def test_unsupported_options_counts_and_undirected_arrows_reject(self):
        changes = [{"variant": "pie"}, {"layout": "radial"}, {"node_width": 120}, {"node_height": 50},
                   {"style": {"fill": "primary"}}, {"arrow": False}]
        for update in changes:
            item = ring()
            item.update(update)
            with self.subTest(update=update), self.assertRaises(TemplateInputError):
                self.lower(item)
        for count in (2, 7):
            with self.assertRaises(TopologyError):
                self.lower(ring(count))
        for key, value in (("shape", "ellipse"), ("width", 50), ("stroke", "primary"), ("fill", {})):
            item = ring()
            item["nodes"][0][key] = value
            with self.subTest(key=key), self.assertRaises(TemplateInputError):
                self.lower(item)
        item = ring()
        item["edges"] = [{"id": "e"+str(i), "from": "n"+str(i), "to": "n"+str((i+1)%4), "arrow": False} for i in range(4)]
        with self.assertRaises(TopologyError):
            self.lower(item)

    def test_catalog_exposes_reusable_variant_and_old_default_survives(self):
        catalog = topology_catalog("cycle", self.tokens)
        example = catalog["variant"]["arrow-ring"]["example"]
        self.assertEqual(self.lower(example)["metadata"]["topology_report"]["variant"], "arrow-ring")
        item = ring()
        del item["variant"]
        self.assertEqual(sum(c["type"] == "connector" for c in self.lower(item)["children"]), 4)

    def test_normal_computed_cli_exports_native_curves_editable_labels_and_no_images(self):
        item = ring()
        del item["frame"]
        del item["id"]
        author = {"schema_version": "0.1", "project_id": "cycle-arrows-native", "revision": 1,
            "brief": {}, "sources": [], "facts": {}, "pages": [{"id": "cycle-page", "kind": "layout", "layout_version": "0.1",
            "layout": {"id": "root", "type": "column", "padding": 60, "children": [{"id": "ring", "type": "leaf", "height": 550, "element": item}]}}]}
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            source, output = directory / "author.json", directory / "cycle.pptx"
            source.write_text(json.dumps(author), encoding="utf-8")
            run = subprocess.run([sys.executable, str(SCRIPTS / "report_engine.py"), "build", "--input", str(source),
                "--output", str(directory / "build"), "--pptx", str(output), "--geometry-policy", "computed"],
                capture_output=True, text=True, encoding="utf-8", timeout=90,
                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "PYTHONIOENCODING": "utf-8"})
            self.assertEqual(run.returncode, 0, run.stdout+run.stderr)
            ns = {"p": "http://schemas.openxmlformats.org/presentationml/2006/main", "a": "http://schemas.openxmlformats.org/drawingml/2006/main"}
            with ZipFile(output) as archive:
                slide = ET.fromstring(archive.read("ppt/slides/slide1.xml"))
            self.assertEqual(len(slide.findall(".//a:custGeom", ns)), 4)
            self.assertGreaterEqual(len(slide.findall(".//a:cubicBezTo", ns)), 8)
            self.assertEqual(len(slide.findall(".//p:pic", ns)), 0)
            self.assertEqual(len(slide.findall(".//p:cxnSp", ns)), 0)
            self.assertEqual(len(slide.findall(".//p:sp/p:txBody", ns)), 4)
            self.assertEqual([t.text for t in slide.findall(".//a:t", ns)], ["阶段"+str(i) for i in range(1,5)])
            ids = [n.get("id") for n in slide.findall(".//p:cNvPr", ns)]
            self.assertEqual(len(ids), len(set(ids)))


if __name__ == "__main__":
    unittest.main()
