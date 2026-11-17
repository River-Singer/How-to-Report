"""Role inheritance, shared measurement, paragraph flow and native text properties."""
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
SCRIPTS = PROJECT / "skill-src/how-to-report/scripts"
sys.path.insert(0, str(PROJECT / "skill-src/shared/scripts"))
sys.path.insert(0, str(SCRIPTS))
from presentation_composition import expand_page
from presentation_compiler import build_project
from presentation_typography import measure_text_block, resolve_text_style
from presentation_svg import SceneRenderer, runtime_helpers
from presentation_document import resolve_text, resolve_value
from report_ppt import load_template


def document(elements):
    return {"schema_version": "0.1", "project_id": "typography-fixture", "revision": 1, "brief": {}, "sources": [],
            "facts": {}, "pages": [{"id": "overview", "kind": "scene", "job": "Synthetic typography", "elements": elements}]}


class TypographyTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="typography-test-")
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        _, _, self.tokens = load_template()
        self.tokens["font"]["textStyles"] = {"bodyStrong": {"base_role": "compactBody", "weight": 700},
                                             "metricCompact": {"base_role": "heading", "weight": 700}}

    def test_role_inheritance_explicit_precedence_and_validation(self):
        style = resolve_text_style(self.tokens, "bodyStrong", {"font_size": 19, "weight": 500})
        self.assertEqual(style["font_size"], 19)
        self.assertEqual(style["weight"], 400)
        self.assertEqual(style["font_family"], self.tokens["font"]["families"]["body"])
        self.assertEqual(resolve_text_style(self.tokens, "metricCompact")["font_size"], self.tokens["font"]["sizes"]["heading"])
        for invalid in ({"insets": [0, -1, 0, 0]}, {"insets": [0, 0]}, {"paragraph_gap": True},
                        {"line_height": .5}, {"weight": 550}, {"font_family": ""}, {"vertical_anchor": "invalid"}):
            with self.subTest(style=invalid), self.assertRaises(ValueError):
                resolve_text_style(self.tokens, style=invalid)
        self.tokens["font"]["textStyles"]["a"] = {"base_role": "b"}
        self.tokens["font"]["textStyles"]["b"] = {"base_role": "a"}
        with self.assertRaises(ValueError):
            resolve_text_style(self.tokens, "a")
        with self.assertRaises(ValueError):
            resolve_text_style(self.tokens, "unknown")
        profile = self.base / "invalid-role.json"
        profile.write_text(json.dumps(self.tokens), encoding="utf-8")
        with self.assertRaises(ValueError):
            load_template(tokens=profile)

    def test_scene_defaults_use_role_and_explicit_newline_gap_is_measured(self):
        item = {"id": "copy", "type": "text", "role": "compactBody", "frame": [40, 140, 300, 170], "text": "First line\n第二段"}
        page = document([item])["pages"][0]
        renderer = SceneRenderer(page, self.tokens, None, resolve_text, resolve_value, {})
        first = ET.fromstring(renderer.render()[0]).find('.//{*}text[@id="copy"]')
        self.assertEqual(first.get("font-size"), str(self.tokens["font"]["sizes"]["compactBody"]))
        self.assertEqual(first.get("font-family"), "Microsoft YaHei")
        base = resolve_text_style(self.tokens, "compactBody")
        before = measure_text_block(item["text"], 300, base, runtime_helpers())
        after = measure_text_block(item["text"], 300, {**base, "paragraph_gap": 12}, runtime_helpers())
        self.assertAlmostEqual(after["height"] - before["height"], 12)
        self.assertEqual(before["paragraph_starts"], [0, 1])
        item["role"] = "evidence"
        compatible = ET.fromstring(SceneRenderer(page, self.tokens, None, resolve_text, resolve_value, {}).render()[0]).find('.//{*}text[@id="copy"]')
        self.assertEqual(compatible.get("data-htr-text-role"), "body")
        self.assertEqual(compatible.get("data-htr-semantic-role"), "evidence")

    def test_flow_places_mixed_role_paragraphs_and_rejects_overflow(self):
        item = {"id": "flow", "type": "component", "component": "paragraph-flow", "frame": [40, 140, 300, 250],
                "role": "compactBody", "style": {"paragraph_gap": 12, "insets": [16, 16, 16, 16]},
                "paragraphs": [{"id": "main", "text": "当前观察"},
                               {"id": "next", "role": "bodyStrong", "runs": [{"text": "后续判断"}]}]}
        expanded = expand_page(document([item])["pages"][0], {}, (1280, 720), self.tokens)["elements"][0]
        first, second = expanded["children"]
        self.assertEqual(first["frame"][:1], [56.0])
        self.assertAlmostEqual(second["frame"][1] - first["frame"][1] - first["frame"][3], 12)
        self.assertEqual(second["style"]["weight"], 700)
        self.assertEqual(second["role"], "bodyStrong")
        tiny = copy.deepcopy(item)
        tiny["frame"][3] = 40
        profile = self.base / "tokens.json"
        profile.write_text(json.dumps(self.tokens), encoding="utf-8")
        with self.assertRaises(ValueError):
            build_project(document([tiny]), self.base / "invalid", tokens=profile)
        self.assertFalse((self.base / "invalid").exists())
        unknown = copy.deepcopy(item)
        unknown["paragraphs"][0]["style"] = {"insets": [0, 0, 0, 0]}
        with self.assertRaises(ValueError):
            expand_page(document([unknown])["pages"][0], {}, (1280, 720), self.tokens)

    def test_component_purpose_roles_and_legacy_explicit_sizes(self):
        item = {"id": "ring", "type": "component", "component": "progress-ring", "frame": [40, 140, 250, 200],
                "value": 25, "total": 100, "label": "当前比例", "detail": "统计范围",
                "text_roles": {"label": "diagramCompact", "value": "metricCompact", "detail": "caption"}}
        result = expand_page(document([item])["pages"][0], {}, (1280, 720), self.tokens)["elements"][0]
        children = {child["id"]: child for child in result["children"]}
        self.assertEqual(children["ring--label"]["style"]["font_size"], 14)
        self.assertEqual(children["ring--percentage"]["style"]["font_size"], 28)
        self.assertEqual(children["ring--denominator"]["style"]["font_size"], 16)
        item["style"] = {"font_size": 12, "value_size": 20}
        result = expand_page(document([item])["pages"][0], {}, (1280, 720), self.tokens)["elements"][0]
        children = {child["id"]: child for child in result["children"]}
        self.assertEqual(children["ring--label"]["style"]["font_size"], 12)
        self.assertEqual(children["ring--percentage"]["style"]["font_size"], 20)

    def test_flow_gap_separates_items_and_preserves_internal_line_spacing(self):
        self.tokens["font"]["sizes"]["compactBody"] = 20
        self.tokens["font"]["lineHeight"]["compactBody"] = 1.3
        self.tokens["font"]["textStyles"]["compactBody"] = {"paragraph_gap": 5}
        item = {"id": "flow", "type": "component", "component": "paragraph-flow", "frame": [40, 140, 300, 250],
                "role": "compactBody", "style": {"paragraph_gap": 12, "insets": [16, 16, 16, 16]},
                "paragraphs": [{"id": "main", "text": "A\nB"}, {"id": "next", "text": "C"}]}
        first, second = expand_page(document([item])["pages"][0], {}, (1280, 720), self.tokens)["elements"][0]["children"]
        self.assertEqual(first["style"]["paragraph_gap"], 0)
        expected = measure_text_block("A\nB", first["frame"][2], first["style"], runtime_helpers())
        self.assertAlmostEqual(expected["baselines"][1] - expected["baselines"][0], 26)
        self.assertAlmostEqual(first["frame"][3], expected["height"])
        self.assertAlmostEqual(first["frame"][3] - expected["baselines"][0] - 20 * .25, 26)
        self.assertAlmostEqual(second["frame"][1] - first["frame"][1] - first["frame"][3], 12)
        author, profile = self.base / "flow-author.json", self.base / "flow-tokens.json"
        author.write_text(json.dumps(document([item])), encoding="utf-8")
        profile.write_text(json.dumps(self.tokens), encoding="utf-8")
        output = self.base / "flow-native.pptx"
        result = subprocess.run([sys.executable, "-B", str(SCRIPTS / "report_engine.py"), "build", "--geometry-policy", "legacy-replay", "--input", str(author),
                                 "--tokens", str(profile), "--output", str(self.base / "flow-project"), "--pptx", str(output)],
                                capture_output=True, text=True, encoding="utf-8", cwd=self.base)
        self.assertEqual(result.returncode, 0, result.stderr)
        ns = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main", "p": "http://schemas.openxmlformats.org/presentationml/2006/main"}
        with ZipFile(output) as archive:
            slide = ET.fromstring(archive.read("ppt/slides/slide1.xml"))
            shape = next(node for node in slide.findall('.//p:grpSp/p:sp', ns)
                         if ''.join(text.text or '' for text in node.findall('.//a:t', ns)) == 'AB')
            paragraphs = shape.findall('./p:txBody/a:p', ns)
            self.assertEqual(len(paragraphs), 2)
            for paragraph in paragraphs:
                self.assertEqual(paragraph.find('./a:pPr/a:lnSpc/a:spcPts', ns).get('val'), '1950')
                before = paragraph.find('./a:pPr/a:spcBef/a:spcPts', ns)
                self.assertTrue(before is None or before.get('val') == '0')

    def test_normal_cli_native_insets_line_spacing_alignment_and_font_scripts(self):
        item = {"id": "copy", "type": "text", "role": "bodyStrong", "frame": [40, 140, 400, 180],
                "text": "First line\n第二段", "style": {"line_height": 1.4, "paragraph_gap": 12,
                "insets": [11, 13, 17, 19], "align": "center", "vertical_anchor": "middle"}}
        author, profile = self.base / "author.json", self.base / "tokens.json"
        flow = {"id": "flow", "type": "component", "component": "paragraph-flow", "frame": [500, 140, 350, 300],
                "role": "compactBody", "style": {"paragraph_gap": 12},
                "paragraphs": [{"id": "lines", "text": "A\n\nB"}, {"id": "empty", "text": ""}, {"id": "tail", "text": "Tail"}]}
        author.write_text(json.dumps(document([item, flow])), encoding="utf-8")
        profile.write_text(json.dumps(self.tokens), encoding="utf-8")
        output = self.base / "native.pptx"
        result = subprocess.run([sys.executable, "-B", str(SCRIPTS / "report_engine.py"), "build", "--geometry-policy", "legacy-replay", "--input", str(author),
                                 "--tokens", str(profile), "--output", str(self.base / "project"), "--pptx", str(output)],
                                capture_output=True, text=True, encoding="utf-8", cwd=self.base)
        self.assertEqual(result.returncode, 0, result.stderr)
        ns = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main", "p": "http://schemas.openxmlformats.org/presentationml/2006/main"}
        with ZipFile(output) as archive:
            slide = ET.fromstring(archive.read("ppt/slides/slide1.xml"))
            theme = ET.fromstring(archive.read("ppt/theme/theme1.xml"))
            shape = next(node for node in slide.findall('.//p:sp', ns) if 'First line' in ''.join(text.text or '' for text in node.findall('.//a:t', ns)))
            body = shape.find('./p:txBody/a:bodyPr', ns)
            for key, px in (("lIns", 11), ("tIns", 13), ("rIns", 17), ("bIns", 19)):
                self.assertEqual(int(body.get(key)), px * 9525)
            self.assertEqual(body.get("anchor"), "ctr")
            self.assertTrue(all(node.get('algn') == 'ctr' for node in shape.findall('.//a:pPr', ns)))
            def font_face(raw):
                if raw.startswith('+mn-') or raw.startswith('+mj-'):
                    collection = 'minorFont' if raw.startswith('+mn-') else 'majorFont'
                    tag = {'lt': 'latin', 'ea': 'ea', 'cs': 'cs'}[raw.rsplit('-', 1)[-1]]
                    return theme.find(f'.//a:{collection}/a:{tag}', ns).get('typeface')
                return raw
            for run in shape.findall('.//a:rPr', ns):
                self.assertEqual(font_face(run.find('a:latin', ns).get('typeface')), font_face(run.find('a:ea', ns).get('typeface')))
                self.assertEqual(run.get('b'), '1')
            self.assertEqual(shape.find('.//a:lnSpc/a:spcPts', ns).get('val'), str(round(20 * 1.4 * 75)))
            self.assertEqual(shape.find('.//a:spcBef/a:spcPts', ns).get('val'), '900')
            grouped = slide.findall('.//p:grpSp/p:sp', ns)
            self.assertEqual(len(grouped), 3)
            lines = next(node for node in grouped if ''.join(text.text or '' for text in node.findall('.//a:t', ns)) == 'AB')
            self.assertEqual([''.join(node.text or '' for node in paragraph.findall('.//a:t', ns))
                              for paragraph in lines.findall('./p:txBody/a:p', ns)], ['A', '', 'B'])
            self.assertTrue(any(not ''.join(node.text or '' for node in shape.findall('.//a:t', ns)) for shape in grouped))
        discovery = subprocess.run([sys.executable, "-B", str(SCRIPTS / "report_engine.py"), "typography", "--tokens", str(profile)],
                                   capture_output=True, text=True, encoding="utf-8", cwd=self.base)
        self.assertEqual(discovery.returncode, 0, discovery.stderr)
        self.assertIn("bodyStrong", json.loads(discovery.stdout)["roles"])

    def test_compact_percent_custom_font_weight_and_insets_share_exact_measurement(self):
        self.tokens["font"]["textStyles"]["shareStrong"] = {"base_role": "caption", "font_family": "Arial",
                                                           "weight": 700, "insets": [5, 3, 7, 3]}
        item = {"id": "parts", "type": "component", "component": "partition", "frame": [40, 140, 800, 250],
                "density": "compact", "total": 100, "total_label": "Overall", "text_roles": {"percent": "shareStrong"},
                "segments": [{"id": "a", "label": "Part A", "value": 25}, {"id": "b", "label": "Part B", "value": 75}]}
        profile = self.base / "percent-profile.json"
        profile.write_text(json.dumps(self.tokens), encoding="utf-8")
        build_project(document([item]), self.base / "compact-percent", tokens=profile)
        expanded = expand_page(document([item])["pages"][0], {}, (1280, 720), self.tokens)["elements"][0]
        child = next(child for child in expanded["children"] if child["id"] == "parts--a--share")
        self.assertEqual(child["style"]["font_family"], "Arial")
        self.assertEqual(child["style"]["weight"], 700)
        self.assertEqual(child["style"]["insets"], [5, 3, 7, 3])

    def test_partition_percent_role_color_preserves_explicit_muted_and_legacy_default(self):
        self.tokens["font"]["textStyles"]["dataCaption"] = {"base_role": "caption", "color": "text"}
        default_muted = self.tokens["theme"]["slots"][self.tokens["color"]["roles"]["textMuted"]]
        for density in ("comfortable", "compact"):
            for roles, style, expected in (({}, {}, default_muted),
                                            ({"percent": "dataCaption"}, {}, "text"),
                                            ({"percent": "dataCaption"}, {"muted": "#AABBCC"}, "#AABBCC")):
                with self.subTest(density=density, roles=roles, style=style):
                    item = {"id": "parts", "type": "component", "component": "partition", "frame": [40, 140, 800, 300],
                            "density": density, "total": 100, "text_roles": roles, "style": style,
                            "segments": [{"id": "a", "label": "Part A", "value": 25},
                                         {"id": "b", "label": "Part B", "value": 75}]}
                    group = expand_page(document([item])["pages"][0], {}, (1280, 720), self.tokens)["elements"][0]
                    shares = [child for child in group["children"] if child["id"].endswith("--share")]
                    self.assertEqual([child["style"]["color"] for child in shares], [expected, expected])


if __name__ == "__main__":
    unittest.main()
