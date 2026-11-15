"""Source-diagram inputs through the same public build and native export path."""
from __future__ import annotations

import copy
from pathlib import Path
import sys
import tempfile
import unittest
from xml.etree import ElementTree as ET
from zipfile import ZipFile

PROJECT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(PROJECT / "skill-src/how-to-report/scripts"), str(PROJECT / "skill-src/shared/scripts")]
import report_ppt as ppt
import ppt_runtime as runtime


class SourceDiagramTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root, cls.catalog, cls.tokens = ppt.load_template()

    def page(self, identifier="source", variant="page-03"):
        item = self.catalog["families"]["source-house"]["variants"][variant]
        return {"id": identifier, "family": "source-house", "variant": variant,
                "content": copy.deepcopy(item["prototype_content"])}

    def document(self, pages):
        return {"schema_version": 1, "template_id": "business-blue-v1", "pages": pages}

    def test_chart_slots_reject_unused_unknown_misaligned_and_all_null_input(self):
        cases = []
        unused = self.page(variant="page-02")
        unused["content"]["charts"] = {"chart_130": {}}
        cases.append((unused, "chart_130"))
        unknown = self.page()
        unknown["content"]["charts"]["unknown"] = {}
        cases.append((unknown, "unknown"))
        for values in ([1], [None, None, None]):
            invalid = self.page()
            invalid["content"]["charts"]["chart_130"]["series"][0]["values"] = values
            cases.append((invalid, "series"))
        for page, message in cases:
            with self.subTest(message=message):
                with self.assertRaisesRegex(ppt.TemplateInputError, message):
                    ppt.validate_document(self.document([page]), self.catalog, self.root)

    def test_mixed_empty_picture_and_real_crop_share_layout_and_replace_chart_data(self):
        from PIL import Image
        pages = [self.page("empty"), self.page("populated")]
        chart = pages[1]["content"]["charts"]["chart_130"]
        chart.update(categories=["甲", "乙", "丙", "丁"], series=[{"name": "值", "values": [-4, 5, 9, 3]}], chart_type="column", show_data_labels=True)
        pages[1]["content"]["visuals"] = {"picture_90": {"path": "wide.png", "alt": "工程图片"}}
        pages[1]["config"] = {"image_fit": "cover", "image_position": "xMaxYMid"}
        with tempfile.TemporaryDirectory() as temporary:
            assets = Path(temporary) / "assets"
            assets.mkdir()
            Image.new("RGB", (400, 100), "#5385C5").save(assets / "wide.png")
            project = Path(temporary) / "mixed"
            ppt.build_project(self.document(pages), project, asset_root=assets)
            runtime.check_project(project, self.tokens)
            output = Path(temporary) / "mixed.pptx"
            inspection = runtime.export_project(project, output, self.tokens)
            self.assertEqual(inspection["counts"], {"slides": 2, "masters": 1, "layouts": 1})
            self.assertEqual(inspection["native_objects"]["charts"], 2)
            with ZipFile(output) as package:
                slide = ET.fromstring(package.read("ppt/slides/slide2.xml"))
                crop = slide.find(".//a:srcRect", runtime.NS)
                self.assertIsNotNone(crop)
                self.assertEqual(crop.get("l"), "75000")
                charts = [ET.fromstring(package.read(name)) for name in package.namelist()
                          if name.startswith("ppt/charts/chart") and name.endswith(".xml")]
                chart_ns = {"c": "http://schemas.openxmlformats.org/drawingml/2006/chart"}
                values = [[node.text for node in item.findall(".//c:val/c:numRef/c:numCache/c:pt/c:v", chart_ns)] for item in charts]
                self.assertIn(["-4", "5", "9", "3"], values)

    def test_actual_width_multiline_and_vertical_anchor_contract(self):
        page = self.page(variant="page-02")
        variant = self.catalog["families"]["source-house"]["variants"]["page-02"]
        field = next(key for key, value in variant["fields"].items() if value["frame"][2] > 100 and value["frame"][3] < 40)
        for value in ("W" * 25, "汉" * 25, "汉\n字\n换\n行"):
            candidate = copy.deepcopy(page)
            candidate["content"]["nodes"][field] = value
            with self.subTest(value=value):
                with self.assertRaises(ppt.TemplateInputError):
                    normalized = ppt.validate_document(self.document([candidate]), self.catalog, self.root)
                    ppt.render_page(normalized["pages"][0], self.catalog, self.tokens, self.root)
        normalized = ppt.validate_document(self.document([page]), self.catalog, self.root)
        svg, bindings, _ = ppt.render_page(normalized["pages"][0], self.catalog, self.tokens, self.root)
        centered = [binding for binding in bindings if binding.get("vertical_anchor") == "ctr"]
        self.assertTrue(centered)
        xml = ET.fromstring(svg)
        for binding in centered:
            self.assertEqual(xml.find(f".//*[@id='{binding['selector']}']").get("data-htr-vertical-anchor"), "ctr")

    def test_source_white_font_reference_keeps_duplicate_label_invisible(self):
        variant = self.catalog["families"]["source-circular"]["variants"]["page-13"]
        page = {"id": "font-reference", "family": "source-circular", "variant": "page-13", "content": copy.deepcopy(variant["prototype_content"])}
        normalized = ppt.validate_document(self.document([page]), self.catalog, self.root)
        svg, bindings, _ = ppt.render_page(normalized["pages"][0], self.catalog, self.tokens, self.root)
        xml = ET.fromstring(svg)
        duplicate = xml.find(".//*[@id='text-nodes-shape_8']")
        visible = xml.find(".//*[@id='text-nodes-shape_22']")
        self.assertEqual(duplicate.get("fill"), self.tokens["theme"]["slots"]["lt1"])
        self.assertNotEqual(visible.get("fill"), duplicate.get("fill"))
        self.assertEqual(next(item for item in bindings if item["field"] == "nodes.shape_8")["source_ref"], "slide:8")
        self.assertIn("fontRef", variant["fields"]["shape_8"]["source_color_resolution"])

    def test_numbered_service_nodes_and_metric_pairs_use_single_line_contracts(self):
        cases = [("source-circular", "page-35"), ("source-spatial", "page-07")]
        for family, identifier in cases:
            variant = self.catalog["families"][family]["variants"][identifier]
            page = {"id": "single-line", "family": family, "variant": identifier, "content": copy.deepcopy(variant["prototype_content"])}
            normalized = ppt.validate_document(self.document([page]), self.catalog, self.root)
            _, bindings, _ = ppt.render_page(normalized["pages"][0], self.catalog, self.tokens, self.root)
            self.assertTrue(any(binding.get("max_lines") == 1 for binding in bindings))
            for field, value in (("shape_9", "节点"),) if family == "source-circular" else (("shape_138", "99"), ("shape_139", "单位单位"), ("shape_120", "1\n2")):
                invalid = copy.deepcopy(page)
                invalid["content"]["nodes"][field] = value
                with self.subTest(family=family, field=field, value=value):
                    with self.assertRaises(ppt.TemplateInputError):
                        document = ppt.validate_document(self.document([invalid]), self.catalog, self.root)
                        ppt.render_page(document["pages"][0], self.catalog, self.tokens, self.root)
        variant = self.catalog["families"]["source-spatial"]["variants"]["page-07"]
        for value_ref, unit_ref in ((120, 122), (124, 125), (127, 129), (131, 132), (134, 136), (138, 139)):
            value = variant["fields"][f"shape_{value_ref}"]["frame"]
            unit = variant["fields"][f"shape_{unit_ref}"]["frame"]
            self.assertLessEqual(value[0] + value[2] + 5.99, unit[0])
        candidate = {"id": "metric-width", "family": "source-spatial", "variant": "page-07", "content": copy.deepcopy(variant["prototype_content"])}
        candidate["content"]["nodes"]["shape_120"] = "999999"
        normalized = ppt.validate_document(self.document([candidate]), self.catalog, self.root)
        with self.assertRaisesRegex(ppt.TemplateInputError, r"nodes.shape_120: measured .* exceeds"):
            ppt.render_page(normalized["pages"][0], self.catalog, self.tokens, self.root)
        candidate["content"]["nodes"]["shape_120"] = "0"
        candidate["content"]["nodes"]["shape_122"] = "单位单位"
        normalized = ppt.validate_document(self.document([candidate]), self.catalog, self.root)
        with self.assertRaisesRegex(ppt.TemplateInputError, r"nodes.shape_122: measured \d+ lines, allowed 1"):
            ppt.render_page(normalized["pages"][0], self.catalog, self.tokens, self.root)


if __name__ == "__main__":
    unittest.main()
