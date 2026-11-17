"""Regressions for token-based adaptive structures and quantitative pie templates."""
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
import presentation_assets
import report_ppt as ppt

NS = {"p": "http://schemas.openxmlformats.org/presentationml/2006/main",
      "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
      "c": "http://schemas.openxmlformats.org/drawingml/2006/chart"}


class SmartArtTopologyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root, cls.catalog, cls.tokens = ppt.load_template()

    def page(self, family, variant, count=None):
        definition = self.catalog["families"][family]
        content = copy.deepcopy(definition["prototype_content"])
        content.update(copy.deepcopy(definition["variants"][variant].get("prototype_content", {})))
        if count is not None:
            content[definition["array_key"]] = content[definition["array_key"]][:count]
        return {"id": family + variant + str(count or ""), "family": family, "variant": variant, "content": content}

    def document(self, pages):
        return {"schema_version": 1, "template_id": "business-blue-v1", "pages": pages}

    def render(self, page, tokens=None):
        page = ppt.validate_document(self.document([page]), self.catalog, self.root)["pages"][0]
        svg, bindings, _ = ppt.render_page(page, self.catalog, tokens or self.tokens, self.root)
        return ET.fromstring(svg), bindings

    def test_actual_node_count_connections_and_layout_identity(self):
        for family, variant, field in (("hub", "radial", "nodes"), ("process", "cycle", "steps")):
            layouts = set()
            for count in range(3, 7):
                with self.subTest(family=family, count=count):
                    root, bindings = self.render(self.page(family, variant, count))
                    layouts.add(root.get("data-pptx-layout"))
                    nodes = root.findall(".//*[@data-pptx-object='shape']")
                    edges = root.findall(".//*[@data-pptx-object='connector']")
                    self.assertEqual(len(nodes), count + 1)
                    self.assertEqual(len(edges), count)
                    self.assertEqual(sum(b["field"].startswith(field + ".") for b in bindings), 2 * count)
                    graph = [(e.get("data-pptx-start-shape-id"), e.get("data-pptx-end-shape-id")) for e in edges]
                    if family == "hub":
                        self.assertEqual(graph, [("100", str(101 + index)) for index in range(count)])
                        self.assertTrue(all(e.get("marker-end") is None for e in edges))
                    else:
                        self.assertEqual(graph, [(str(101 + index), str(101 + (index + 1) % count)) for index in range(count)])
                        self.assertTrue(all(e.get("marker-end") for e in edges))
            self.assertEqual(len(layouts), 4)

    def test_capacity_text_and_nested_icons_are_validated(self):
        for family, variant, field in (("hub", "radial", "nodes"), ("process", "cycle", "steps")):
            for count in (2, 7):
                page = self.page(family, variant)
                page["content"][field] = [{"title": "节点", "body": "说明"} for _ in range(count)]
                with self.assertRaises(ppt.TemplateInputError):
                    self.render(page)
            page = self.page(family, variant, 3)
            page["content"][field][0]["title"] = "文" * 13
            with self.assertRaisesRegex(ppt.TemplateInputError, r"\.title"):
                self.render(page)
        page = self.page("hierarchy", "tree")
        page["content"]["branches"][0]["children"][0]["icon_key"] = "unknown-icon"
        with self.assertRaisesRegex(ppt.TemplateInputError, r"children\.0\.icon_key"):
            self.render(page)

    def test_tree_children_follow_their_actual_parent(self):
        page = self.page("hierarchy", "tree")
        for index, branch in enumerate(page["content"]["branches"]):
            branch["children"] = branch["children"][:index]
        root, _ = self.render(page)
        edges = root.findall(".//*[@data-pptx-object='connector']")
        self.assertEqual(len(root.findall(".//*[@data-pptx-object='shape']")), 7)
        self.assertEqual([(e.get("data-pptx-start-shape-id"), e.get("data-pptx-end-shape-id")) for e in edges],
                         [("100", "101"), ("100", "102"), ("102", "202"),
                          ("100", "103"), ("103", "204"), ("103", "205")])
        self.assertTrue(all(e.get("marker-end") is None for e in edges))

    def test_optional_cycle_center_has_a_distinct_layout_contract(self):
        page = self.page("process", "cycle", 3)
        with_center, _ = self.render(page)
        del page["content"]["center"]
        without_center, bindings = self.render(page)
        self.assertNotEqual(with_center.get("data-pptx-layout"), without_center.get("data-pptx-layout"))
        self.assertEqual(len(without_center.findall(".//*[@data-pptx-object='shape']")), 3)
        self.assertEqual(len(without_center.findall(".//*[@data-pptx-object='connector']")), 3)
        self.assertFalse(any(binding["field"].startswith("center.") for binding in bindings))

    def test_colors_fonts_and_connectors_consume_actual_tokens(self):
        page = self.page("hub", "radial", 3)
        old_root, old_bindings = self.render(page)
        tokens = copy.deepcopy(self.tokens)
        tokens["theme"]["slots"]["accent1"] = "#7A2450"
        tokens["theme"]["slots"]["lt2"] = "#F8EBDD"
        tokens["font"]["sizes"]["heading"] = 26
        tokens["line"]["connector"] = 3
        new_root, new_bindings = self.render(page, tokens)
        self.assertEqual([b["text"] for b in old_bindings], [b["text"] for b in new_bindings])
        self.assertEqual([b["frame"] for b in old_bindings], [b["frame"] for b in new_bindings])
        self.assertEqual(old_root.get("data-pptx-layout"), new_root.get("data-pptx-layout"))
        self.assertTrue(all(n.get("fill") == "#F8EBDD" for n in new_root.findall(".//*[@data-pptx-object='shape']")))
        self.assertTrue(all(n.get("stroke") == "#7A2450" and n.get("stroke-width") == "3"
                            for n in new_root.findall(".//*[@data-pptx-object='connector']")))
        heading = new_root.find(".//*[@id='text-nodes-0-title']")
        self.assertEqual(heading.get("font-size"), "26")

    def test_svg_serialization_is_independent_of_ooxml_import_order(self):
        page = self.page("hub", "radial", 3)
        before, _ = self.render(page)
        ET.register_namespace("", "http://schemas.openxmlformats.org/package/2006/relationships")
        after, _ = self.render(page)
        self.assertEqual(ET.tostring(before), ET.tostring(after))
        self.assertTrue(ET.tostring(after, encoding="unicode").startswith("<svg xmlns="))

    def test_discovery_exposes_adaptation_and_quantitative_templates(self):
        for task, expected in (("可变中心辐射", "hub/radial"), ("可变闭环流程", "process/cycle"),
                               ("可变二至三层树", "hierarchy/tree"), ("饼图与构成说明", "chart/pie"),
                               ("环形图与构成说明", "chart/doughnut")):
            result = presentation_assets.query_assets(self.root, task, variants=True, limit=20)
            self.assertEqual(result["candidates"][0]["id"], expected)
        radial = presentation_assets.inventory_assets(self.root, family="hub", variants=True)["items"]
        radial = next(item for item in radial if item["variant"] == "radial")
        self.assertEqual(radial["content_limits"]["array_min_items"], 3)
        self.assertEqual(radial["capacity"], 6)
        self.assertTrue(radial["adaptation"]["dynamic_count"])
        self.assertFalse(radial["adaptation"]["fixed_source_topology"])
        self.assertTrue(radial["adaptation"]["supported_changes"])

    def test_pie_templates_share_scene_geometry_and_validate_parts(self):
        for kind in ("pie", "doughnut"):
            root, bindings = self.render(self.page("chart", kind))
            native = root.find(".//*[@data-pptx-replace-with='chart']")
            payload = json.loads(native.find("{*}metadata").text)
            self.assertEqual(payload["type"], kind)
            self.assertEqual(payload["series"][0]["values"], [50, 30, 20])
            self.assertEqual(payload["series"][0]["point_colors"],
                             [self.tokens["theme"]["slots"][f"accent{index}"] for index in range(1, 4)])
            self.assertIn("50 · 50.0%", [b["text"] for b in bindings])
            for values in ([0, 0, 0], [-1, 2, 3], [1, None, 3]):
                page = self.page("chart", kind)
                page["content"]["series"][0]["values"] = values
                with self.assertRaisesRegex(ppt.TemplateInputError, "nonnegative"):
                    self.render(page)

    def test_pie_value_labels_require_the_external_legend_region(self):
        for kind in ("pie", "doughnut"):
            page = self.page("chart", kind)
            page["config"] = {"show_legend": False, "show_data_labels": True}
            with self.subTest(kind=kind), self.assertRaisesRegex(
                    ppt.TemplateInputError, r"pages\.0\.config\.show_data_labels"):
                self.render(page)
            page["config"]["show_data_labels"] = False
            root, bindings = self.render(page)
            payload = json.loads(root.find(".//*[@data-pptx-replace-with='chart']/{*}metadata").text)
            self.assertFalse(payload["show_legend"])
            self.assertFalse(payload["data_labels"])
            self.assertFalse(any(binding["field"].startswith("value_labels.") for binding in bindings))

    def test_normal_cli_exports_real_connections_charts_and_workbooks(self):
        pages = [self.page("hub", "radial", 3), self.page("hub", "radial", 6),
                 self.page("process", "cycle", 6), self.page("hierarchy", "tree"),
                 self.page("chart", "pie"), self.page("chart", "doughnut")]
        pages[-1]["config"] = {"show_legend": False, "show_data_labels": False}
        author = {"schema_version": "0.1", "project_id": "topology-fixture", "revision": 1,
                  "brief": {}, "sources": [], "facts": {}, "pages": [
                      {"id": page.pop("id"), "kind": "template", "template": page} for page in pages]}
        with tempfile.TemporaryDirectory(prefix="smartart-templates-") as temporary:
            folder = Path(temporary)
            source, output = folder / "author.json", folder / "output.pptx"
            source.write_text(json.dumps(author, ensure_ascii=False), encoding="utf-8")
            result = subprocess.run([sys.executable, "-B", str(SCRIPTS / "report_engine.py"), "build",
                                     "--input", str(source), "--output", str(folder / "project"), "--pptx", str(output)],
                                    cwd=folder, capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)["check_status"], "pass")
            with ZipFile(output) as package:
                for number, expected in enumerate((3, 6, 6, 9), 1):
                    slide = ET.fromstring(package.read(f"ppt/slides/slide{number}.xml"))
                    ids = {node.get("id") for node in slide.findall(".//p:cNvPr", NS)}
                    edges = slide.findall(".//p:cxnSp", NS)
                    self.assertEqual(len(edges), expected)
                    for edge in edges:
                        self.assertIn(edge.find(".//a:stCxn", NS).get("id"), ids)
                        self.assertIn(edge.find(".//a:endCxn", NS).get("id"), ids)
                charts = [name for name in package.namelist() if name.startswith("ppt/charts/chart") and name.endswith(".xml")]
                self.assertEqual(len(charts), 2)
                roots = [ET.fromstring(package.read(name)) for name in charts]
                self.assertEqual(sum(root.find(".//c:pieChart", NS) is not None for root in roots), 1)
                self.assertEqual(sum(root.find(".//c:doughnutChart", NS) is not None for root in roots), 1)
                self.assertEqual(sum(name.startswith("ppt/embeddings/") and name.endswith(".xlsx") for name in package.namelist()), 2)


if __name__ == "__main__":
    unittest.main()
