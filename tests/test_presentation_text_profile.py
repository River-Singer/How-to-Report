"""Published text contracts are backed by normal computed builds and native text."""
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
sys.path[:0] = [str(SCRIPTS), str(PROJECT / "skill-src/shared/scripts")]

from presentation_compiler import build_project
from presentation_library import profile_identity, profile_path
from presentation_text_profile import describe_text_profile, text_profile_story, validate_profile_text_floor
from presentation_typography import resolve_text_style
from report_ppt import load_template


class TextProfileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory(prefix="text-profile-test-")
        cls.base = Path(cls.temporary.name)
        cls.author = text_profile_story()
        cls.input = cls.base / "author.json"
        cls.input.write_text(json.dumps(cls.author, ensure_ascii=False), encoding="utf-8")
        cls.output = cls.base / "text-standard.pptx"
        cls.project = cls.base / "project"
        cls.command = subprocess.run([sys.executable, "-B", str(SCRIPTS / "report_engine.py"), "build",
            "--input", str(cls.input), "--output", str(cls.project), "--geometry-policy", "computed", "--pptx", str(cls.output)],
            capture_output=True, text=True, encoding="utf-8", cwd=cls.base)

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def test_describe_uses_existing_global_profile_and_actual_resolved_roles(self):
        result = describe_text_profile("profile.report-14pt")
        _, _, tokens = load_template(tokens=profile_path())
        self.assertEqual(result["tokens"], tokens)
        self.assertEqual(result["global_binding"]["value"], profile_identity())
        self.assertEqual(result["global_binding"]["field"], "brief.design_profile")
        self.assertEqual(result["standards"]["body_pt"], 14)
        self.assertEqual(result["standards"]["minimum_role_pt"], 9)
        for role, published in result["roles"].items():
            actual = resolve_text_style(tokens, role)
            self.assertEqual(published["font_size_px"], actual["font_size"])
            self.assertEqual(published["font_size_pt"], actual["font_size"] * .75)
            self.assertEqual(published["line_height_pt"], actual["font_size"] * actual["line_height"] * .75)
            self.assertEqual(published["paragraph_gap_px"], actual["paragraph_gap"])
            self.assertEqual(published["font_family"], actual["font_family"])
        self.assertEqual(result["rich_text"]["run_fields"], ["text", "weight", "color"])
        self.assertIn("未实现", result["font_policy"]["fallback"])
        self.assertTrue(result["rich_text"]["unsupported"])
        for invalid in (None, "not-registered", "../report-14pt"):
            with self.subTest(identifier=invalid), self.assertRaises(ValueError):
                describe_text_profile(invalid)

    def test_three_pages_build_with_persistent_layout_and_native_typography(self):
        self.assertEqual(self.command.returncode, 0, self.command.stderr)
        self.assertTrue(all(page["kind"] == "layout" for page in self.author["pages"]))
        self.assertEqual(self.author["brief"]["design_profile"], profile_identity())
        self.assertNotIn('"frame"', json.dumps(self.author))
        ns = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main", "p": "http://schemas.openxmlformats.org/presentationml/2006/main"}
        with ZipFile(self.output) as archive:
            slides = [ET.fromstring(archive.read(f"ppt/slides/slide{index}.xml")) for index in (1, 2, 3)]
            sizes = [int(node.get("sz")) for slide in slides for node in slide.findall(".//a:rPr", ns) if node.get("sz")]
            self.assertGreater(len(sizes), 16)
            self.assertGreaterEqual(min(sizes), 900)
            shape = next(shape for shape in slides[1].findall(".//p:sp", ns)
                         if "本周完成率" in "".join(node.text or "" for node in shape.findall(".//a:t", ns)))
            runs = shape.findall(".//a:r", ns)
            bold = next(run for run in runs if run.find("a:t", ns).text == "本周完成率")
            self.assertEqual(bold.find("a:rPr", ns).get("b"), "1")
            self.assertEqual(bold.find("a:rPr", ns).get("sz"), "1400")
            colored = next(run for run in runs if run.find("a:t", ns).text == "82%")
            self.assertEqual(colored.find("a:rPr/a:solidFill/a:srgbClr", ns).get("val"), "0756B8")
            self.assertEqual(shape.find(".//a:pPr/a:lnSpc/a:spcPts", ns).get("val"), "1820")
            paragraph_shapes = [shape for shape in slides[1].findall(".//p:sp", ns)
                                if "第一段：" in "".join(node.text or "" for node in shape.findall(".//a:t", ns))]
            self.assertEqual(len(paragraph_shapes), 2)
            before_values = [[int(n.get("val")) for n in shape.findall(".//a:spcBef/a:spcPts", ns)] for shape in paragraph_shapes]
            self.assertTrue(any(900 in values for values in before_values), before_values)
            self.assertTrue(any(900 not in values for values in before_values), before_values)
            alignment_shapes = [shape for shape in slides[2].findall(".//p:sp", ns)
                                if "正文14pt" in "".join(node.text or "" for node in shape.findall(".//a:t", ns))]
            self.assertEqual(len(alignment_shapes), 3)
            self.assertEqual({shape.find("p:txBody/a:bodyPr", ns).get("anchor") for shape in alignment_shapes}, {"t", "ctr", "b"})
            for shape in alignment_shapes:
                body = shape.find("p:txBody/a:bodyPr", ns)
                self.assertTrue(all(int(body.get(key)) == 16 * 9525 for key in ("lIns", "tIns", "rIns", "bIns")))

    def test_unsupported_run_and_paragraph_fields_fail_without_publishing(self):
        for index, element in enumerate([
            {"runs": [{"text": "Unsupported", "italic": True}]},
            {"runs": [{"text": "Unsupported", "font_size": 18}]},
            {"text": "Unsupported", "style": {"paragraph_before": 12}},
            {"text": "Unsupported", "style": {"align": "justify"}},
        ]):
            author = copy.deepcopy(self.author)
            author["pages"] = [{"id": "invalid", "kind": "layout", "layout_version": "0.1", "job": "reject unsupported text",
                "layout": {"id": "invalid-text", "type": "leaf", "element": {"type": "text", "role": "body", **element}}}]
            output = self.base / f"invalid-{index}"
            with self.subTest(element=element), self.assertRaises(ValueError):
                build_project(author, output, geometry_policy="computed")
            self.assertFalse(output.exists())

    def test_named_profile_cli_discovery_and_example_preserve_legacy_query(self):
        cli = [sys.executable, "-B", str(SCRIPTS / "report_engine.py"), "typography"]
        for args in (["--profile", "report-14pt"], ["--profile", "report-14pt", "--example"], []):
            result = subprocess.run(cli + args, capture_output=True, text=True, encoding="utf-8", cwd=self.base)
            self.assertEqual(result.returncode, 0, result.stderr)
            value = json.loads(result.stdout)
            if "--example" in args:
                self.assertEqual(value, self.author)
            elif args:
                self.assertEqual(value["roles"]["body"]["font_size_pt"], 14)
            else:
                self.assertIn("font_size", value["roles"]["body"])
        for args in (["--example"], ["--profile", "unknown"], ["--profile", "report-14pt", "--tokens", str(profile_path())]):
            result = subprocess.run(cli + args, capture_output=True, text=True, encoding="utf-8", cwd=self.base)
            self.assertNotEqual(result.returncode, 0)

    def test_computed_profile_rejects_six_pt_override_and_accepts_nine_pt(self):
        for size, accepted in ((8, False), (12, True)):
            author = copy.deepcopy(self.author)
            author["pages"] = [{"id": "floor", "kind": "layout", "layout_version": "0.1", "job": "font floor",
                "layout": {"id": "floor-text", "type": "leaf", "element": {
                    "type": "text", "role": "body", "text": "字号边界", "style": {"font_size": size}}}}]
            output = self.base / f"floor-{size}"
            if accepted:
                build_project(author, output, geometry_policy="computed")
                self.assertTrue(output.exists())
            else:
                with self.assertRaisesRegex(ValueError, "minimum is 9pt") as failure:
                    build_project(author, output, geometry_policy="computed")
                self.assertEqual(failure.exception.diagnostic["effective_pt"], 6)
                self.assertFalse(output.exists())

    def test_computed_floor_covers_expanded_components_and_native_chart_styles(self):
        elements = [
            {"type": "component", "component": "paragraph-flow", "style": {"font_size": 8},
             "paragraphs": [{"id": "small", "text": "小字号"}]},
            {"type": "chart", "chart_type": "column", "categories": ["A", "B"],
             "series": [{"name": "示例", "values": [2, 3]}], "style": {"axis_font_size": 8}},
        ]
        for index, element in enumerate(elements):
            author = copy.deepcopy(self.author)
            author["pages"] = [{"id": "floor", "kind": "layout", "layout_version": "0.1", "job": "font floor",
                "layout": {"id": "floor-element", "type": "leaf", "height": 400, "element": element}}]
            output = self.base / f"floor-component-{index}"
            with self.subTest(element=element), self.assertRaisesRegex(ValueError, "minimum is 9pt"):
                build_project(author, output, geometry_policy="computed")
            self.assertFalse(output.exists())

    def test_floor_leaves_unbound_legacy_and_preserved_template_source_unchanged(self):
        author = copy.deepcopy(self.author)
        author["pages"] = [{"id": "small", "kind": "layout", "layout_version": "0.1", "job": "compatibility",
            "layout": {"id": "small-text", "type": "leaf", "element": {
                "type": "text", "role": "body", "text": "compatibility", "style": {"font_size": 8}}}}]
        legacy = self.base / "floor-legacy"
        build_project(author, legacy, geometry_policy="legacy-replay")
        author["brief"].pop("design_profile")
        build_project(author, self.base / "floor-unbound", geometry_policy="computed")
        template = {"id": "source-page", "kind": "template"}
        mixed = '<svg><text font-size="8">保留源字</text><text data-htr-text-role="body" font-size="12">新文字</text></svg>'
        validate_profile_text_floor(self.author, template, mixed, "computed")
        with self.assertRaisesRegex(ValueError, "minimum is 9pt"):
            validate_profile_text_floor(self.author, template, mixed.replace('font-size="12"', 'font-size="8"'), "computed")


if __name__ == "__main__":
    unittest.main()
