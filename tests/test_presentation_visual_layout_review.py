"""Independent behavior probes for visual layout, not model quality scores."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "skill-src/shared/scripts"))
sys.path.insert(0, str(PROJECT / "skill-src/how-to-report/scripts"))

from presentation_compiler import build_project
from presentation_layout import lower_layout_page
from presentation_library import profile_identity
from report_ppt import load_template


def text(identifier, value, **extra):
    return {"id": identifier, "type": "leaf", "element": {
        "type": "text", "role": "body", "text": value}, **extra}


class VisualLayoutReviewTests(unittest.TestCase):
    def test_decorations_and_sequence_do_not_inflate_real_content_diagnostics(self):
        author = {"schema_version": "0.1", "project_id": "visual-review", "revision": 1,
                  "brief": {"design_profile": profile_identity()}, "sources": [], "facts": {},
                  "pages": [{"id": "sample", "kind": "layout", "layout_version": "0.1", "intent": "demo",
                             "layout": {"id": "row", "type": "row", "padding": 32, "gap": 40, "children": [
                                 {"id": name, "type": "column", "grow": 1, "basis": 0, "padding": 20,
                                  "surface": {"fill": "surfaceMuted"}, "children": [text(name + "-text", value)]}
                                 for name, value in (("a", "Collect input"), ("b", "Validate input"))]}}]}
        decorated = copy.deepcopy(author)
        decorated["pages"][0]["layout"]["connect"] = "sequence"
        for node in decorated["pages"][0]["layout"]["children"]:
            node["surface"]["accent"] = {"kind": "bracket"}
        with tempfile.TemporaryDirectory(prefix="visual-review-") as directory:
            records = []
            for name, source in (("plain", author), ("decorated", decorated)):
                output = Path(directory) / name
                build_project(source, output, geometry_policy="computed")
                records.append(json.loads((output / "content-diagnostics.json").read_text(encoding="utf-8"))["pages"][0])
            self.assertEqual(records[0]["occupancy"], records[1]["occupancy"])
            self.assertEqual(records[0]["observations"]["supplied_data_record_count"], 0)

    def test_width_and_text_changes_remeasure_spanned_rows_without_font_shrink(self):
        _, _, tokens = load_template()
        original = {"id": "sample", "kind": "layout", "layout_version": "0.1", "layout": {
            "id": "grid", "type": "grid", "gap": 12, "columns": [{"fr": 1}] * 3, "children": [
                text("shared", "Shared foundation supports all three services. " * 3, column_span=3),
                text("a", "First"), text("b", "Second"), text("c", "Third")]}}
        scene_wide, wide = lower_layout_page(original, {}, [900, 700], tokens)
        scene_narrow, narrow = lower_layout_page(original, {}, [450, 700], tokens)
        wide_nodes = {node["id"]: node for node in wide["nodes"]}
        narrow_nodes = {node["id"]: node for node in narrow["nodes"]}
        self.assertGreater(narrow_nodes["shared"]["line_count"], wide_nodes["shared"]["line_count"])
        self.assertGreater(narrow_nodes["a"]["frame"][1], wide_nodes["a"]["frame"][1])
        self.assertEqual([item["text"] for item in scene_wide["elements"]],
                         [item["text"] for item in scene_narrow["elements"]])
        self.assertEqual([item.get("style") for item in scene_wide["elements"]],
                         [item.get("style") for item in scene_narrow["elements"]])
        longer = copy.deepcopy(original)
        longer["layout"]["children"][0]["element"]["text"] *= 2
        _, grown = lower_layout_page(longer, {}, [900, 700], tokens)
        grown_nodes = {node["id"]: node for node in grown["nodes"]}
        self.assertGreater(grown_nodes["a"]["frame"][1], wide_nodes["a"]["frame"][1])


if __name__ == "__main__":
    unittest.main()
