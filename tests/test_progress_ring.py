"""Native pie/doughnut and bounded progress-ring contract regressions."""
from __future__ import annotations

import copy
from io import BytesIO
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from xml.etree import ElementTree as ET
from zipfile import ZipFile

PROJECT = Path(__file__).resolve().parents[1]
SCRIPTS = PROJECT / "skill-src/how-to-report/scripts"
sys.path.insert(0, str(PROJECT / "skill-src/shared/scripts"))
sys.path.insert(0, str(SCRIPTS))
from presentation_composition import component_catalog, expand_page
from presentation_compiler import build_project
from presentation_document import evaluate_facts
from report_ppt import TemplateInputError


def ring(value=25, total=100):
    return {"id": "progress", "type": "component", "component": "progress-ring", "frame": [60, 150, 200, 135],
            "value": value, "total": total, "label": "Progress", "value_format": ",.0f",
            "style": {"font_size": 12, "value_size": 20}}


def document(elements):
    return {"schema_version": "0.1", "project_id": "pie-fixture", "revision": 1, "brief": {}, "sources": [],
            "facts": {"value": {"value": 25}, "total": {"value": 100}},
            "pages": [{"id": "overview", "kind": "scene", "job": "Synthetic composition", "elements": elements}]}


def chart(kind="pie"):
    item = {"id": "composition", "type": "chart", "chart_type": kind, "frame": [60, 150, 200, 200],
            "categories": ["Value", "Remaining"], "series": [{"name": "Parts", "values": [25, 75],
                                                                "point_colors": ["secondary", "border"]}],
            "data_labels": False, "show_legend": False}
    if kind == "doughnut":
        item["hole_size"] = 75
    return item


class ProgressRingTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="progress-ring-test-")
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)

    def test_boundaries_and_fact_changes_keep_two_exact_parts(self):
        for value, expected in ((0, "0%"), (25, "25.0%"), (100, "100%")):
            with self.subTest(value=value):
                expanded = expand_page({"id": "p1", "elements": [ring(value)]}, {}, (1280, 720))["elements"][0]
                children = {child["id"]: child for child in expanded["children"]}
                native = children["progress--ring"]
                self.assertEqual(native["series"][0]["values"], [value, 100 - value])
                self.assertEqual(native["frame"][2], native["frame"][3])
                self.assertEqual(children["progress--percentage"]["text"], expected)
                self.assertEqual(children["progress--denominator"]["text"], f"{value} / 100")
        item = ring({"ref": "value"}, {"ref": "total"})
        source = document([item])
        facts = evaluate_facts(source)
        before = expand_page(source["pages"][0], facts, (1280, 720))
        facts["value"] = 80
        after = expand_page(source["pages"][0], facts, (1280, 720))
        self.assertEqual([child["id"] for child in before["elements"][0]["children"]],
                         [child["id"] for child in after["elements"][0]["children"]])
        self.assertEqual(after["elements"][0]["children"][1]["series"][0]["values"], [80, 20])
        item["value_prefix"] = "约"
        approximate = expand_page({"id": "p1", "elements": [item]}, facts, (1280, 720))
        self.assertEqual(approximate["elements"][0]["children"][-1]["text"], "约80 / 100")
        self.assertEqual(approximate["elements"][0]["children"][1]["series"][0]["values"], [80, 20])

    def test_invalid_progress_domain_and_capacity_fail_without_publication(self):
        invalid = [ring(-1), ring(101), ring(1, 0), ring(True), ring(float("inf"))]
        for field, value in (("hole_size", 9), ("hole_size", 91), ("hole_size", 75.5),
                             ("percent_decimals", True), ("percent_decimals", -1), ("percent_decimals", 5),
                             ("value_prefix", {"text": "bad"})):
            item = ring()
            item[field] = value
            invalid.append(item)
        tiny = ring()
        tiny["frame"] = [60, 150, 200, 35]
        invalid.append(tiny)
        for index, item in enumerate(invalid):
            with self.subTest(index=index):
                target = self.base / f"invalid-{index}"
                with self.assertRaises(ValueError):
                    build_project(document([item]), target)
                self.assertFalse(target.exists())

    def test_pie_payload_and_svg_share_values_colors_and_full_plot(self):
        for kind in ("pie", "doughnut"):
            item = chart(kind)
            target = self.base / kind
            build_project(document([item]), target)
            xml = ET.parse(next((target / "svg_output").glob("*.svg"))).getroot()
            payload = json.loads(xml.find(".//{*}metadata").text)
            self.assertEqual(payload["series"][0]["values"], [25, 75])
            self.assertEqual(payload["plot_area"], {"x": 60.0, "y": 150.0, "width": 200.0, "height": 200.0})
            colors = payload["series"][0]["point_colors"]
            paths = xml.findall(".//{*}path")
            self.assertEqual([path.get("fill") for path in paths], colors)
            self.assertIn("160 150 A 100 100 0 0 1 260 250", paths[0].get("d"))
            if kind == "doughnut":
                self.assertEqual(payload["hole_size"], 75)
                self.assertIn("A 75 75 0 0 0 160 175", paths[0].get("d"))
                self.assertIsNone(xml.find(".//{*}circle"))

    def test_invalid_pie_data_and_options_are_rejected(self):
        cases = []
        for values in ([0, 0], [-1, 2], [None, 1]):
            item = chart()
            item["series"][0]["values"] = values
            cases.append(item)
        extra = chart()
        extra["series"].append(copy.deepcopy(extra["series"][0]))
        cases.append(extra)
        for field, value in (("axes", {"value": {"visible": False}}), ("data_labels", {"show_value": True}),
                             ("hole_size", 75), ("plot_padding", [100, 100, 100, 100])):
            item = chart()
            item[field] = value
            cases.append(item)
        for index, item in enumerate(cases):
            with self.subTest(index=index), self.assertRaises(TemplateInputError):
                build_project(document([item]), self.base / f"invalid-pie-{index}")

    def test_ring_background_is_transparent_and_full_sectors_preserve_hole(self):
        for value in (0, 25, 100):
            with self.subTest(value=value):
                source = document([ring(value)])
                source["pages"][0]["background"] = "surfaceMuted"
                target = self.base / f"transparent-{value}"
                build_project(source, target)
                xml = ET.parse(next((target / "svg_output").glob("*.svg"))).getroot()
                payload = json.loads(xml.find(".//{*}metadata").text)
                self.assertEqual(payload["style"]["chart_area_fill"], "none")
                self.assertEqual(payload["style"]["plot_area_fill"], "none")
                self.assertIsNone(xml.find(".//{*}circle"))
                for path in xml.findall(".//{*}path"):
                    inner_radius = payload["plot_area"]["width"] * .75 / 2
                    self.assertIn(f"A {inner_radius:g} {inner_radius:g}", path.get("d"))
        item = ring()
        item["chart_background"] = "surfaceMuted"
        target = self.base / "role-background"
        build_project(document([item]), target)
        xml = ET.parse(next((target / "svg_output").glob("*.svg"))).getroot()
        style = json.loads(xml.find(".//{*}metadata").text)["style"]
        self.assertRegex(style["chart_area_fill"], r"^#[0-9A-Fa-f]{6}$")
        self.assertEqual(style["plot_area_fill"], style["chart_area_fill"])

    def test_normal_cli_exports_native_charts_workbooks_and_editable_center(self):
        items = [ring({"ref": "value"}, {"ref": "total"})]
        for index, kind in enumerate(("pie", "doughnut")):
            item = chart(kind)
            item.update(id=kind, frame=[350 + index * 250, 150, 200, 200])
            items.append(item)
        author = self.base / "author.json"
        author.write_text(json.dumps(document(items)), encoding="utf-8")
        output = self.base / "native.pptx"
        project = self.base / "project"
        result = subprocess.run([sys.executable, "-B", str(SCRIPTS / "report_engine.py"), "build", "--geometry-policy", "legacy-replay",
                                 "--input", str(author), "--output", str(project), "--pptx", str(output)],
                                cwd=self.base, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["asset_usage"]["components"], {"progress-ring": 1})
        ns = {"p": "http://schemas.openxmlformats.org/presentationml/2006/main",
              "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
              "c": "http://schemas.openxmlformats.org/drawingml/2006/chart",
              "s": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
        with ZipFile(output) as package:
            charts = [name for name in package.namelist() if name.startswith("ppt/charts/chart") and name.endswith(".xml")]
            workbooks = [name for name in package.namelist() if name.startswith("ppt/embeddings/") and name.endswith(".xlsx")]
            self.assertEqual(len(charts), 3)
            self.assertEqual(len(workbooks), 3)
            for path in charts:
                xml = ET.fromstring(package.read(path))
                self.assertEqual([float(node.text) for node in xml.findall(".//c:val//c:numCache/c:pt/c:v", ns)], [25, 75])
                self.assertEqual(xml.find(".//c:firstSliceAng", ns).get("val"), "0")
                series_name = xml.find(".//c:doughnutChart/c:ser/c:tx//c:v", ns)
                if series_name is not None and series_name.text == "Progress":
                    self.assertIsNotNone(xml.find("./c:spPr/a:noFill", ns))
                    self.assertIsNotNone(xml.find(".//c:plotArea/c:spPr/a:noFill", ns))
            for path in workbooks:
                with ZipFile(BytesIO(package.read(path))) as workbook:
                    xml = ET.fromstring(workbook.read("xl/worksheets/sheet1.xml"))
                    self.assertEqual(float(xml.find('.//s:c[@r="B2"]/s:v', ns).text), 25)
                    self.assertEqual(float(xml.find('.//s:c[@r="B3"]/s:v', ns).text), 75)
            slide = ET.fromstring(package.read("ppt/slides/slide1.xml"))
            texts = ["".join(node.text or "" for node in shape.findall(".//a:t", ns))
                     for shape in slide.findall(".//p:sp/p:txBody", ns)]
            self.assertIn("25.0%", texts)
        self.assertIn("progress-ring", component_catalog()["definitions"])
        capability = subprocess.run([sys.executable, "-B", str(SCRIPTS / "report_engine.py"), "capabilities"],
                                    cwd=self.base, capture_output=True, text=True, encoding="utf-8")
        self.assertIn("progress-ring", json.loads(capability.stdout)["components"]["names"])


if __name__ == "__main__":
    unittest.main()
