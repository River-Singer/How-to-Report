"""Independent review of content observation scope and non-mutating intent."""
import copy
from pathlib import Path
import sys
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parents[1] / "skill-src/how-to-report"
sys.path[:0] = [str(SOURCE / "scripts"), str(SOURCE.parent / "shared/scripts")]

from presentation_compiler import build_project
from presentation_content_diagnostics import analyze_page
from presentation_library import profile_identity, profile_path
from report_ppt import load_template


class ContentDiagnosticReviewTests(unittest.TestCase):
    def test_overlapping_text_rectangles_and_hidden_groups_do_not_inflate_area(self):
        _, _, tokens = load_template(tokens=profile_path())
        item = {"id": "a", "type": "text", "role": "body", "text": "同一位置的文本", "frame": [30, 40, 500, 120]}
        page = {"id": "observation", "intent": "summary", "job": "检验矩形面积"}
        one = analyze_page(page, {"elements": [item]}, tokens)
        scene = {"elements": [item, {**item, "id": "b"},
            {"id": "background", "type": "shape", "shape": "rect", "fill": "surfaceMuted", "frame": [0, 0, 1280, 720]},
            {"id": "hidden", "type": "group", "opacity": 0, "children": [{**item, "id": "hidden-copy"}]},
            {"id": "decorative", "type": "text", "text": "decorative", "frame": [500, 400, 400, 100], "metadata": {"decorative": True}}]}
        before = copy.deepcopy(scene)
        result = analyze_page(page, scene, tokens)
        self.assertEqual(scene, before)
        self.assertEqual(result["observations"]["text_block_count"], 2)
        self.assertEqual(result["observations"]["text_rectangle_union_area"], one["observations"]["text_rectangle_union_area"])
        self.assertEqual(set(result["observations"]["excluded_invisible_or_declared_decorative"]), {"hidden", "decorative"})
        self.assertLess(result["observations"]["text_rectangle_union_canvas_fraction"], .05)
        self.assertEqual(result["semantic_quality"], "not_assessed")

    def test_intent_changes_observations_without_changing_svg_and_templates_are_not_guessed(self):
        document = {"schema_version": "0.1", "project_id": "review-intent", "revision": 1,
            "brief": {"design_profile": profile_identity()}, "sources": [], "facts": {},
            "pages": [{"id": "one", "kind": "layout", "layout_version": "0.1", "job": "观察诊断边界",
                       "intent": "analysis", "layout": {"id": "root", "type": "column", "padding": 40,
                         "children": [{"id": "copy", "type": "leaf", "element": {"type": "text", "role": "body", "text": "一项已知判断。"}}]}}]}
        with tempfile.TemporaryDirectory(prefix="content-review-") as temporary:
            root = Path(temporary)
            before = copy.deepcopy(document)
            analytical = build_project(document, root / "analysis", geometry_policy="computed")
            self.assertEqual(document, before)
            document["pages"][0]["intent"] = "cover"
            cover = build_project(document, root / "cover", geometry_policy="computed")
            self.assertTrue(analytical["content_diagnostics"]["review_required"])
            self.assertFalse(cover["content_diagnostics"]["review_required"])
            left = next((root / "analysis/svg_output").glob("*.svg")).read_bytes()
            right = next((root / "cover/svg_output").glob("*.svg")).read_bytes()
            self.assertEqual(left, right)
        _, _, tokens = load_template(tokens=profile_path())
        source = analyze_page({"id": "source", "intent": "architecture", "job": "source template"}, None, tokens)
        self.assertEqual(source["status"], "not_assessable")
        self.assertEqual(source["semantic_quality"], "not_assessed")
        self.assertNotIn("text_rectangle_union_canvas_fraction", source["observations"])


if __name__ == "__main__":
    unittest.main()
