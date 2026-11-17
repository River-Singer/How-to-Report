"""Small regressions for mixed numeric precision in native KPI templates."""
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
import report_ppt as ppt


def metrics():
    return [{"label": "激活率", "value": 52.6, "unit": "%", "decimals": 1},
            {"label": "活跃人数", "value": 6947, "unit": "人", "decimals": 0},
            {"label": "约增幅", "value": 20, "unit": "%", "decimals": 0},
            {"label": "关联组织", "value": 3, "unit": "家", "decimals": 0}]


class KpiPrecisionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root, cls.catalog, cls.tokens = ppt.load_template()

    def document(self):
        return {"schema_version": 1, "template_id": self.catalog["template_id"], "pages": [
            {"id": "precision", "family": "kpi", "variant": "strip-4",
             "content": {"title": "混合指标", "metrics": metrics()}}]}

    def render(self, document):
        page = ppt.validate_document(document, self.catalog, self.root)["pages"][0]
        return ppt.render_page(page, self.catalog, self.tokens, self.root)

    def test_each_metric_controls_precision_and_preserves_units(self):
        _, bindings, _ = self.render(self.document())
        values = [item for item in bindings if item["field"].endswith(".value")]
        self.assertEqual([item["text"] for item in values], ["52.6", "6,947", "20", "3"])
        self.assertEqual([item["derived_from"] for item in values], [
            f"metrics.{index}.value + metrics.{index}.decimals" for index in range(4)])
        self.assertEqual([item["text"] for item in bindings if item["field"].endswith(".unit")],
                         ["%", "人", "%", "家"])

    def test_global_fallback_and_legacy_prototypes(self):
        document = self.document()
        page = document["pages"][0]
        page["variant"] = "cards-3"
        page["config"] = {"decimals": 2}
        page["content"]["metrics"] = [{"label": "A", "value": 1.256, "decimals": 1},
                                        {"label": "B", "value": 2.1}, {"label": "C", "value": 3}]
        _, bindings, _ = self.render(document)
        values = [item for item in bindings if item["field"].endswith(".value")]
        self.assertEqual([item["text"] for item in values], ["1.3", "2.10", "3.00"])
        self.assertEqual(values[1]["derived_from"], "metrics.1.value + config.decimals")
        family = self.catalog["families"]["kpi"]
        for name, variant in family["variants"].items():
            content = copy.deepcopy(family["prototype_content"])
            content["metrics"] = content["metrics"][:variant["capacity"]]
            original = {"schema_version": 1, "template_id": self.catalog["template_id"], "pages": [
                {"id": "structure", "family": "kpi", "variant": name, "content": content}]}
            svg, _, _ = self.render(original)
            self.assertEqual(svg, (self.root / "templates/prototypes" / variant["prototype"]).read_text(encoding="utf-8"))

    def test_invalid_metric_precision_is_rejected(self):
        for precision in (-1, 5, True, 0.5, "1", None):
            with self.subTest(precision=precision):
                document = self.document()
                document["pages"][0]["content"]["metrics"][0]["decimals"] = precision
                with self.assertRaisesRegex(ppt.TemplateInputError, r"metrics\.0\.decimals"):
                    ppt.validate_document(document, self.catalog, self.root)

    def test_normal_cli_preserves_numeric_refs_and_native_carriers(self):
        with tempfile.TemporaryDirectory(prefix="kpi-precision-") as temporary:
            folder = Path(temporary)
            items = metrics()
            facts = {f"metric_{index}": {"value": item["value"]} for index, item in enumerate(items)}
            for index, item in enumerate(items):
                item["value"] = {"ref": f"metric_{index}"}
            author = {"schema_version": "0.1", "project_id": "kpi-precision-fixture", "revision": 1,
                      "brief": {}, "sources": [], "facts": facts, "pages": [
                          {"id": "precision", "kind": "template", "template": {
                              "family": "kpi", "variant": "strip-4", "content": {
                                  "title": "混合指标", "metrics": items}}}]}
            source = folder / "author.json"
            source.write_text(json.dumps(author, ensure_ascii=False), encoding="utf-8")
            project = folder / "project"
            output = folder / "precision.pptx"
            result = subprocess.run([sys.executable, "-B", str(SCRIPTS / "report_engine.py"), "build",
                                     "--input", str(source), "--output", str(project), "--pptx", str(output)],
                                    cwd=folder, capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)["check_status"], "pass")
            ns = {"p": "http://schemas.openxmlformats.org/presentationml/2006/main",
                  "a": "http://schemas.openxmlformats.org/drawingml/2006/main"}
            with ZipFile(output) as package:
                slide = ET.fromstring(package.read("ppt/slides/slide1.xml"))
                shapes = {shape.find("p:nvSpPr/p:cNvPr", ns).get("name"): shape
                          for shape in slide.findall(".//p:sp", ns)}
                for index, expected in enumerate(("52.6", "6,947", "20", "3")):
                    shape = next(shape for name, shape in shapes.items() if f"metrics-{index}-value" in name)
                    self.assertEqual("".join(node.text or "" for node in shape.findall(".//a:t", ns)), expected)
                    extent = shape.find("p:spPr/a:xfrm/a:ext", ns)
                    self.assertIsNotNone(extent)
                    self.assertGreater(int(extent.get("cx")), 0)
                    self.assertGreater(int(extent.get("cy")), 0)


if __name__ == "__main__":
    unittest.main()
