"""Cross-template, scene and native chart typography regressions."""
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
sys.path.insert(0, str(PROJECT / "skill-src/shared/scripts"))
import report_ppt as ppt
from presentation_svg import SceneRenderer, runtime_helpers
from presentation_typography import resolve_text_style

NS = {"p": "http://schemas.openxmlformats.org/presentationml/2006/main",
      "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
      "c": "http://schemas.openxmlformats.org/drawingml/2006/chart"}


class TemplateTypographyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root, cls.catalog, cls.tokens = ppt.load_template()

    def profile(self):
        tokens = copy.deepcopy(self.tokens)
        tokens["font"]["textStyles"] = {"body": {
            "font_family": "Microsoft YaHei", "font_size": 20, "weight": 400,
            "line_height": 1.4, "paragraph_gap": 6, "insets": [8, 6, 10, 4],
            "align": "right", "vertical_anchor": "middle"}}
        tokens["chart"]["axis_role"] = "body"
        return tokens

    def test_template_and_scene_consume_the_same_resolved_role_and_measurement(self):
        tokens = self.profile()
        family = self.catalog["families"]["parallel"]
        page = {"id": "template", "family": "parallel", "variant": "columns-3",
                "content": copy.deepcopy(family["prototype_content"]),
                "config": {key: self.catalog["config_defaults"][key] for key in family["config_fields"]}}
        canvas = ppt.Canvas(page, family, family["variants"]["columns-3"], tokens, self.root, 1)
        value = "第一段 123\n第二段 456"
        frame = [80, 140, 430, 160]
        template = canvas.text("items.0.body", value, frame, "body")[0]
        item = {"id": "body-text", "type": "text", "role": "body", "frame": frame, "text": value}
        renderer = SceneRenderer({"id": "scene", "elements": [item]}, tokens, None,
                                 lambda text, facts: text, lambda text, facts: text, {})
        scene = renderer.text(item).find(".//{*}text")
        for attribute in ("font-family", "font-size", "font-weight", "text-anchor",
                          "data-paragraph-line-height", "data-htr-text-insets", "data-htr-vertical-anchor"):
            self.assertEqual(template.get(attribute), scene.get(attribute), attribute)
        self.assertEqual([float(span.get("y")) for span in template],
                         [float(span.get("y")) for span in scene])
        self.assertEqual(template[1].get("data-paragraph-space-before"), "6")
        self.assertEqual(canvas.bindings[-1]["resolved_style"], resolve_text_style(tokens, "body"))

    def test_unused_invalid_role_is_rejected_globally(self):
        tokens = self.profile()
        tokens["font"]["textStyles"]["unused"] = {"base_role": "missing"}
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "tokens.json"
            source.write_text(json.dumps(tokens), encoding="utf-8")
            with self.assertRaisesRegex(ppt.TemplateInputError, "missing"):
                ppt.load_template(tokens=source)
            del tokens["font"]["textStyles"]["unused"]
            tokens["chart"]["axis_role"] = "missing-axis-role"
            source.write_text(json.dumps(tokens), encoding="utf-8")
            with self.assertRaisesRegex(ppt.TemplateInputError, "missing-axis-role"):
                ppt.load_template(tokens=source)

    def test_native_chart_resolved_styles_preserve_local_overrides(self):
        runtime_helpers()
        from svg_to_pptx.native_objects.chart_data import validate_chart_payload
        from svg_to_pptx.native_objects.chart_style import _chart_text_style_override, _chart_tx_pr_xml
        from svg_to_pptx.native_objects.chart_xml import _data_labels_xml
        style = resolve_text_style(self.profile(), "body")
        style["color"] = "#123456"
        merged = _chart_text_style_override(style, {"font_size": 24, "font_family": "Arial",
                                                   "color": "#654321", "bold": True})
        fragment = _chart_tx_pr_xml(900, font_face="Old Font", text_style=merged)
        node = ET.fromstring('<root xmlns:a="' + NS["a"] + '" xmlns:c="' + NS["c"] + '">' + fragment + '</root>')
        props = node.find(".//a:defRPr", NS)
        self.assertEqual(props.get("sz"), "1800")
        self.assertEqual(props.get("b"), "1")
        self.assertEqual(props.find("a:latin", NS).get("typeface"), "Arial")
        self.assertEqual(props.find("a:solidFill/a:srgbClr", NS).get("val"), "654321")
        self.assertEqual(node.find(".//a:pPr/a:lnSpc/a:spcPts", NS).get("val"), "2520")
        self.assertEqual(node.find(".//a:pPr/a:spcBef/a:spcPts", NS).get("val"), "450")
        body = node.find(".//a:bodyPr", NS)
        self.assertEqual([body.get(key) for key in ("lIns", "tIns", "rIns", "bIns")], ["76200", "57150", "95250", "38100"])
        self.assertEqual(body.get("anchor"), "ctr")
        self.assertEqual(node.find(".//a:pPr", NS).get("algn"), "r")
        fractional_style = {**style, "font_size": 18, "line_height": 1.3}
        fragment = _chart_tx_pr_xml(900, text_style=fractional_style)
        fractional = ET.fromstring('<root xmlns:a="' + NS["a"] + '" xmlns:c="' + NS["c"] + '">' + fragment + '</root>')
        self.assertEqual(fractional.find(".//a:lnSpc/a:spcPts", NS).get("val"), "1755")
        rich_style = {**style, "font_size": 23, "font_family": "Courier New", "weight": 700}
        config = {"show_value": True, "points": [
            {"idx": 0, "text": "Role default"},
            {"idx": 1, "text": "Point override", "font_size": 16,
             "font_family": "Arial", "color": "#ABCDEF", "bold": False}]}
        fragment = _data_labels_xml(config, chart_type="column", grouping=None, point_count=2,
                                    font_size=900, default_color="#654321", default_font_face="Old Font",
                                    text_style=rich_style)
        rich = ET.fromstring('<root xmlns:a="' + NS["a"] + '" xmlns:c="' + NS["c"] + '">' + fragment + '</root>')
        for point, expected in zip(rich.findall(".//c:dLbl", NS),
                                   (("1720", "Courier New", "123456", "1"),
                                    ("1200", "Arial", "ABCDEF", "0"))):
            for path in ("c:tx/c:rich/a:p/a:r/a:rPr", "c:txPr/a:p/a:pPr/a:defRPr"):
                props = point.find(path, NS)
                self.assertEqual(props.get("sz"), expected[0])
                self.assertEqual(props.find("a:latin", NS).get("typeface"), expected[1])
                self.assertEqual(props.find("a:solidFill/a:srgbClr", NS).get("val"), expected[2])
                self.assertEqual(props.get("b", "0"), expected[3])
        legacy_fragment = _data_labels_xml(config, chart_type="column", grouping=None, point_count=2,
                                           font_size=900, default_color="#654321", default_font_face="Old Font")
        legacy = ET.fromstring('<root xmlns:a="' + NS["a"] + '" xmlns:c="' + NS["c"] + '">' + legacy_fragment + '</root>')
        legacy_props = legacy.find(".//c:dLbl/c:tx/c:rich/a:p/a:r/a:rPr", NS)
        self.assertEqual(legacy_props.get("sz"), "900")
        self.assertEqual(legacy_props.find("a:latin", NS).get("typeface"), "Old Font")
        self.assertEqual(legacy_props.get("b", "0"), "0")
        payload = {"type": "column", "categories": ["A"], "series": [{"name": "X", "values": [1]}],
                   "text_styles": {"axis": style}}
        validate_chart_payload(payload)
        invalid = copy.deepcopy(payload)
        invalid["text_styles"]["axis"]["insets"][0] = -1
        with self.assertRaisesRegex(RuntimeError, "insets"):
            validate_chart_payload(invalid)

    def test_template_chart_readouts_use_data_caption_with_legacy_fallback(self):
        for mode, readout_color in (("legacy", None), ("14pt", "#333333"), ("custom", "#7A2450")):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory(prefix="chart-readout-color-") as temporary:
                folder = Path(temporary)
                tokens = copy.deepcopy(self.tokens)
                tokens["font"]["sizes"].update(body=56 / 3, caption=12)
                tokens["theme"]["slots"][tokens["color"]["roles"]["text"]] = "#333333"
                tokens["theme"]["slots"][tokens["color"]["roles"]["textMuted"]] = "#A6A6A6"
                tokens["font"]["textStyles"] = {"caption": {"color": "textMuted"}}
                if readout_color is not None:
                    tokens["font"]["textStyles"]["dataCaption"] = {"base_role": "caption", "color": readout_color}
                pages = []
                for variant in ("wide", "pie"):
                    pages.append({"id": variant, "kind": "template", "template": {
                        "family": "chart", "variant": variant, "content": {
                            "title": "Chart colors", "categories": ["Part A", "Part B"],
                            "series": [{"name": "Series", "values": [25, 75]}],
                            "conclusions": "Short conclusion"},
                        "config": {"show_legend": True, "show_data_labels": True}}})
                author = {"schema_version": "0.1", "project_id": "chart-readout-color", "revision": 1,
                          "brief": {}, "facts": {}, "sources": [], "pages": pages}
                source, profile = folder / "author.json", folder / "tokens.json"
                source.write_text(json.dumps(author), encoding="utf-8")
                profile.write_text(json.dumps(tokens), encoding="utf-8")
                output, project = folder / "output.pptx", folder / "project"
                result = subprocess.run([sys.executable, "-B", str(SCRIPTS / "report_engine.py"), "build",
                                         "--input", str(source), "--tokens", str(profile),
                                         "--output", str(project), "--pptx", str(output)],
                                        cwd=folder, capture_output=True, text=True, encoding="utf-8")
                self.assertEqual(result.returncode, 0, result.stderr)
                expected_role = "dataCaption" if readout_color is not None else "caption"
                expected_legend = readout_color or "#A6A6A6"
                expected_value = readout_color or "#333333"
                for number in (1, 2):
                    svg = ET.parse(next((project / "svg_output").glob(f"{number:02}_*.svg")))
                    for node in svg.findall(".//{*}text"):
                        identifier = node.get("id", "")
                        if (identifier.startswith(("text-series-", "text-value_labels-"))
                                or number == 2 and identifier.startswith("text-categories-")):
                            self.assertEqual(node.get("data-htr-text-role"), expected_role)
                            self.assertEqual(node.get("fill"), expected_legend)
                with ZipFile(output) as package:
                    theme = ET.fromstring(package.read("ppt/theme/theme1.xml"))
                    scheme = {node.tag.rsplit("}", 1)[-1]: node[0].get("val", node[0].get("lastClr"))
                              for node in theme.find(".//a:clrScheme", NS)}

                    def native_color(properties):
                        fill = properties.find("a:solidFill", NS)
                        color = fill[0]
                        value = color.get("val")
                        if color.tag.endswith("}schemeClr"):
                            value = scheme[value]
                        return "#" + value.upper()

                    charts = [ET.fromstring(package.read(name)) for name in package.namelist()
                              if name.startswith("ppt/charts/chart") and name.endswith(".xml")]
                    column = next(chart for chart in charts if chart.find(".//c:barChart", NS) is not None)
                    legend = column.find(".//c:legend/c:txPr/a:p/a:pPr/a:defRPr", NS)
                    self.assertEqual(native_color(legend), expected_legend)
                    labels = column.findall(".//c:dLbls/c:txPr/a:p/a:pPr/a:defRPr", NS)
                    self.assertTrue(labels)
                    self.assertEqual({native_color(label) for label in labels}, {expected_value})
                    slide = ET.fromstring(package.read("ppt/slides/slide2.xml"))
                    readouts = [shape for shape in slide.findall(".//p:sp", NS)
                                if "".join(node.text or "" for node in shape.findall(".//a:t", NS))
                                in {"Part A", "25 · 25.0%"}]
                    self.assertEqual(len(readouts), 2)
                    for shape in readouts:
                        self.assertEqual({native_color(props) for props in shape.findall(".//a:rPr", NS)},
                                         {expected_legend})

    def test_normal_cli_exports_template_scene_and_chart_at_the_same_native_size(self):
        tokens = self.profile()
        tokens["font"]["textStyles"]["chart_label"] = {
            "base_role": "body", "insets": [0, 0, 0, 0], "paragraph_gap": 0,
            "vertical_anchor": "top"}
        tokens["chart"]["axis_role"] = "chart_label"
        template = {"family": "parallel", "variant": "columns-3", "content": {
            "title": "模板文字", "items": [{"title": "工作一", "body": "第一段 123\n第二段 456"}]}}
        chart = {"family": "chart", "variant": "wide", "content": {
            "title": "统一图表", "categories": ["A", "B"], "series": [{"name": "数列", "values": [3, 5]}],
            "conclusions": "同一文字角色使用相同字号。"}, "config": {"show_data_labels": True}}
        scene = {"id": "body-text", "type": "text", "role": "body", "frame": [80, 140, 430, 160],
                 "text": "第一段 123\n第二段 456"}
        chart_item = {"id": "local-chart", "type": "chart", "frame": [80, 150, 1050, 450],
                      "chart_type": "column", "categories": ["A", "B"], "series": [{"name": "数列", "values": [3, 5]}],
                      "axes": {"value": {"font_size": 24, "font_family": "Arial", "color": "#654321"}},
                      "show_legend": True, "data_labels": {"show_value": True, "font_size": 18, "font_family": "Arial", "bold": True,
                          "points": [{"idx": 0, "text": "Inherited label"},
                                     {"idx": 1, "text": "Explicit label", "font_size": 16,
                                      "font_family": "Courier New", "color": "#ABCDEF", "bold": False}]},
                      "text_roles": {key: "body" for key in ("base", "axis", "legend", "data_label")}}
        author = {"schema_version": "0.1", "project_id": "typography-fixture", "revision": 1, "brief": {}, "facts": {}, "sources": [],
                  "pages": [{"id": "template", "kind": "template", "template": template},
                            {"id": "scene", "kind": "scene", "elements": [scene]},
                            {"id": "chart-template", "kind": "template", "template": chart},
                            {"id": "chart-scene", "kind": "scene", "elements": [chart_item]}]}
        with tempfile.TemporaryDirectory(prefix="template-typography-") as temporary:
            folder = Path(temporary)
            source, profile, output = folder / "author.json", folder / "tokens.json", folder / "output.pptx"
            source.write_text(json.dumps(author, ensure_ascii=False), encoding="utf-8")
            profile.write_text(json.dumps(tokens, ensure_ascii=False), encoding="utf-8")
            result = subprocess.run([sys.executable, "-B", str(SCRIPTS / "report_engine.py"), "build", "--geometry-policy", "legacy-replay", "--input", str(source),
                                     "--tokens", str(profile), "--output", str(folder / "project"), "--pptx", str(output)],
                                    cwd=folder, capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(result.returncode, 0, result.stderr)
            with ZipFile(output) as package:
                for slide_number, identity in ((1, "items-0-body"), (2, "body-text")):
                    slide = ET.fromstring(package.read(f"ppt/slides/slide{slide_number}.xml"))
                    shape = next(shape for shape in slide.findall(".//p:sp", NS)
                                 if identity in shape.find("p:nvSpPr/p:cNvPr", NS).get("name", ""))
                    sizes = {props.get("sz") for props in shape.findall(".//a:rPr", NS)}
                    self.assertEqual(sizes, {"1500"})
                    self.assertEqual(shape.find(".//a:bodyPr", NS).get("lIns"), "76200")
                charts = [ET.fromstring(package.read(name)) for name in package.namelist()
                          if name.startswith("ppt/charts/chart") and name.endswith(".xml")]
                self.assertEqual(len(charts), 2)
                first, second = charts
                self.assertEqual(first.find(".//c:catAx/c:txPr/a:p/a:pPr/a:defRPr", NS).get("sz"), "1500")
                self.assertEqual(first.find(".//c:catAx/c:txPr/a:p/a:pPr/a:lnSpc/a:spcPts", NS).get("val"), "2100")
                self.assertEqual(second.find(".//c:valAx/c:txPr/a:p/a:pPr/a:defRPr", NS).get("sz"), "1800")
                self.assertEqual(second.find(".//c:legend/c:txPr/a:p/a:pPr/a:defRPr", NS).get("sz"), "1500")
                labels = second.find(".//c:dLbls/c:txPr/a:p/a:pPr/a:defRPr", NS)
                self.assertEqual(labels.get("sz"), "1350")
                self.assertEqual(labels.get("b"), "1")
                self.assertEqual(labels.find("a:latin", NS).get("typeface"), "Arial")
                rich_labels = second.findall(".//c:dLbls/c:dLbl/c:tx/c:rich/a:p/a:r/a:rPr", NS)
                self.assertEqual([props.get("sz") for props in rich_labels], ["1350", "1200"])
                self.assertEqual([props.find("a:latin", NS).get("typeface") for props in rich_labels], ["Arial", "Courier New"])
                self.assertEqual([props.get("b", "0") for props in rich_labels], ["1", "0"])
                self.assertEqual(rich_labels[1].find("a:solidFill/a:srgbClr", NS).get("val"), "ABCDEF")
                for chart_root in charts:
                    for props in chart_root.findall(".//a:defRPr", NS):
                        self.assertIsNotNone(props.find("a:latin", NS))
                        self.assertIsNotNone(props.find("a:ea", NS))


if __name__ == "__main__":
    unittest.main()
