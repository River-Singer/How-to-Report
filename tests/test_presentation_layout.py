"""Regression tests for the measured, deterministic layout subset."""
import copy
import math
from pathlib import Path
import sys
import unittest

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "skill-src/shared/scripts"))
sys.path.insert(0, str(PROJECT / "skill-src/how-to-report/scripts"))

from presentation_layout import LayoutError, layout_catalog, lower_layout_page, validate_layout_page
from presentation_typography import measure_text_block, resolve_text_style
from presentation_svg import SceneRenderer, runtime_helpers
from presentation_document import resolve_text, resolve_value
from presentation_composition import expand_page
from report_ppt import load_template


def leaf(identifier, **properties):
    return {"id": identifier, "type": "leaf", "element": {"type": "shape", "fill": "#CCCCCC"}, **properties}


def text(identifier, value="短文", **properties):
    return {"id": identifier, "type": "leaf", "element": {"type": "text", "text": value}, **properties}


def page(root):
    return {"id": "test-page", "kind": "layout", "layout_version": "0.1", "job": "Synthetic engineering fixture", "layout": root}


class PresentationLayoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _, _, cls.tokens = load_template()
        cls.helpers = runtime_helpers()

    def solve(self, root, width=600, height=500, facts=None, bounds=None):
        scene, report = lower_layout_page(page(root), facts or {}, [width, height], self.tokens, bounds=bounds)
        return scene, {node["id"]: node for node in report["nodes"]}

    def test_text_replacement_reflows_following_elements_and_preserves_input(self):
        root = {"id": "body", "type": "column", "padding": [20, 10, 20, 15], "gap": 12,
                "children": [text("copy", {"ref": "copy"}), leaf("chart", height=50)]}
        snapshot = copy.deepcopy(root)
        short, short_nodes = self.solve(root, facts={"copy": "当前观察"})
        long, long_nodes = self.solve(root, facts={"copy": "当前观察需要保留完整口径和所有文字。" * 8})
        self.assertEqual(root, snapshot)
        self.assertGreater(long_nodes["copy"]["frame"][3], short_nodes["copy"]["frame"][3])
        self.assertAlmostEqual(long_nodes["chart"]["frame"][1] - short_nodes["chart"]["frame"][1],
                               long_nodes["copy"]["frame"][3] - short_nodes["copy"]["frame"][3])
        self.assertEqual(long["elements"][0]["element"] if "element" in long["elements"][0] else long["elements"][0]["text"], {"ref": "copy"})
        self.assertEqual(short["elements"][0].get("style"), long["elements"][0].get("style"))
        self.assertGreater(long_nodes["copy"]["line_count"], short_nodes["copy"]["line_count"])

    def test_bottom_anchor_reserves_visible_descent_in_effective_insets(self):
        copy_node = text("copy", "Bottom anchored text")
        copy_node["element"]["style"] = {"vertical_anchor": "bottom"}
        root = {"id": "flow", "type": "column", "children": [copy_node]}
        original = copy.deepcopy(root)
        scene, nodes = self.solve(root)
        record = nodes["copy"]
        safe_descent = record["envelope_height"] - record["measured_height"]
        self.assertGreater(safe_descent, 0)
        self.assertEqual(record["computed_text_insets"]["requested"], [0, 0, 0, 0])
        self.assertAlmostEqual(scene["elements"][0]["style"]["insets"][3], safe_descent)
        self.assertEqual(root, original)
        copy_node["element"]["style"]["insets"] = [3, 4, 5, 12]
        scene, nodes = self.solve(root)
        self.assertEqual(scene["elements"][0]["style"]["insets"], [3, 4, 5, 12])
        self.assertNotIn("computed_text_insets", nodes["copy"])

    def test_row_grow_weighted_with_padding_and_gap(self):
        root = {"id": "row", "type": "row", "padding": [10, 8, 20, 7], "gap": 30,
                "children": [leaf("a", basis=100, grow=1, height=20), leaf("b", basis=100, grow=2, height=20)]}
        _, nodes = self.solve(root, width=560, height=100)
        self.assertEqual(nodes["a"]["frame"], [10, 8, 200, 20])
        self.assertEqual(nodes["b"]["frame"], [240, 8, 300, 20])

    def test_row_max_freeze_redistributes_growth(self):
        root = {"id": "row", "type": "row", "children": [leaf("a", basis=100, grow=1, max_width=150, height=20),
                                                                  leaf("b", basis=100, grow=1, height=20)]}
        _, nodes = self.solve(root, width=500, height=100)
        self.assertEqual(nodes["a"]["frame"][2], 150)
        self.assertEqual(nodes["b"]["frame"][2], 350)
        root["children"][1]["max_width"] = 180
        _, nodes = self.solve(root, width=500, height=100)
        self.assertEqual(nodes["b"]["frame"][2], 180)

    def test_row_shrink_freezes_minimum_and_uses_scaled_basis(self):
        root = {"id": "row", "type": "row", "children": [leaf("a", basis=200, shrink=1, min_width=180, height=20),
                                                                  leaf("b", basis=200, shrink=1, height=20)]}
        _, nodes = self.solve(root, width=300, height=100)
        self.assertEqual(nodes["a"]["frame"][2], 180)
        self.assertEqual(nodes["b"]["frame"][2], 120)
        root["children"][0].pop("min_width")
        root["children"][1]["basis"] = 100
        _, nodes = self.solve(root, width=150, height=100)
        self.assertEqual(nodes["a"]["frame"][2], 100)
        self.assertEqual(nodes["b"]["frame"][2], 50)

    def test_shrunk_row_text_remeasures_at_final_width(self):
        root = {"id": "body", "type": "column", "gap": 10,
                "children": [{"id": "row", "type": "row", "align": "start", "gap": 10,
                              "children": [text("a", "正文保持全部文字并根据实际宽度换行。" * 4, basis=500, shrink=1),
                                           text("b", "另一列", basis=200, shrink=1)]}, leaf("tail", height=10)]}
        _, narrow = self.solve(root, width=400)
        _, wide = self.solve(root, width=800)
        self.assertGreater(narrow["a"]["line_count"], wide["a"]["line_count"])
        self.assertGreater(narrow["tail"]["frame"][1], wide["tail"]["frame"][1])
        style = resolve_text_style(self.tokens)
        expected = measure_text_block(root["children"][0]["children"][0]["element"]["text"], narrow["a"]["frame"][2], style, self.helpers)
        self.assertAlmostEqual(expected["height"], narrow["a"]["measured_height"], places=5)
        self.assertGreaterEqual(narrow["a"]["frame"][3], expected["height"])

    def test_unshrinkable_width_overflow_is_structured(self):
        root = {"id": "row", "type": "row", "children": [leaf("a", width=200, height=20), leaf("b", width=200, height=20)]}
        with self.assertRaises(LayoutError) as caught:
            self.solve(root, width=300)
        diagnostic = caught.exception.diagnostic
        self.assertEqual(diagnostic["node_id"], "row")
        self.assertEqual(diagnostic["axis"], "x")
        self.assertEqual(diagnostic["required"], 400)
        self.assertEqual(diagnostic["available"], 300)
        self.assertEqual(diagnostic["overflow_px"], 100)
        self.assertTrue(diagnostic["suggestions"])

    def test_column_shrink_respects_nontext_minimum_and_preserves_text(self):
        root = {"id": "body", "type": "column", "children": [text("copy", "正文\n两行"), leaf("visual", height=200, min_height=40, shrink=1)]}
        _, nodes = self.solve(root, height=140)
        self.assertAlmostEqual(nodes["visual"]["frame"][3], 140 - nodes["copy"]["frame"][3], places=5)
        self.assertGreaterEqual(nodes["visual"]["frame"][3], 40)
        root["children"][0]["shrink"] = 1
        with self.assertRaises(LayoutError) as caught:
            self.solve(root, height=50)
        self.assertEqual(caught.exception.diagnostic["axis"], "y")
        self.assertGreater(caught.exception.diagnostic["required"], 50)

    def test_column_zero_basis_text_keeps_true_minimum(self):
        root = {"id": "body", "type": "column", "children": [text("copy", "文字", basis=0, grow=1), leaf("visual", height=30)]}
        _, nodes = self.solve(root, height=150)
        self.assertEqual(nodes["copy"]["frame"][3], 120)
        self.assertEqual(nodes["visual"]["frame"][1], 120)

    def test_column_grow_respects_maximum_and_definite_nontext_allocation(self):
        root = {"id": "body", "type": "column", "children": [leaf("a", basis=0, grow=1, max_height=80), leaf("b", basis=0, grow=1)]}
        _, nodes = self.solve(root, height=300)
        self.assertEqual(nodes["a"]["frame"][3], 80)
        self.assertEqual(nodes["b"]["frame"][3], 220)

    def test_grid_uses_final_column_width_then_auto_row_maximum(self):
        root = {"id": "grid", "type": "grid", "columns": [100, {"fr": 1}], "gap": 10,
                "children": [text("a", "较长文字" * 8), text("b", "短文"), leaf("c", height=30), leaf("d", height=50)]}
        _, nodes = self.solve(root, width=400)
        self.assertEqual(nodes["a"]["frame"][2], 100)
        self.assertEqual(nodes["b"]["frame"][2], 290)
        self.assertAlmostEqual(nodes["c"]["frame"][1], nodes["a"]["frame"][3] + 10, places=5)
        self.assertEqual(nodes["c"]["frame"][1], nodes["d"]["frame"][1])
        root["children"][0]["element"]["text"] = "短"
        _, shorter = self.solve(root, width=400)
        self.assertLess(shorter["c"]["frame"][1], nodes["c"]["frame"][1])

    def test_grid_mixed_fixed_auto_fraction_tracks(self):
        root = {"id": "grid", "type": "grid", "columns": [80, "auto", {"fr": 1}, {"fr": 2}], "gap": 10,
                "children": [leaf("a", height=20), text("b", "自动列"), leaf("c", height=20), leaf("d", height=20)]}
        _, nodes = self.solve(root, width=700)
        style = resolve_text_style(self.tokens)
        from text_measure import measure_text
        auto = measure_text("自动列", size=style["font_size"], family=style["font_family"], weight=str(style["weight"]))
        self.assertAlmostEqual(nodes["b"]["frame"][2], auto, places=5)
        self.assertAlmostEqual(nodes["d"]["frame"][2], nodes["c"]["frame"][2] * 2, places=5)

    def test_grid_fraction_tracks_share_total_after_minimum_freeze(self):
        root = {"id": "grid", "type": "grid", "columns": [{"fr": 1}, {"fr": 1}],
                "children": [leaf("a", height=20, min_width=100), leaf("b", height=20)]}
        _, nodes = self.solve(root, width=400)
        self.assertEqual(nodes["a"]["frame"][2], 200)
        self.assertEqual(nodes["b"]["frame"][2], 200)
        root["children"][0]["min_width"] = 300
        _, nodes = self.solve(root, width=400)
        self.assertEqual(nodes["a"]["frame"][2], 300)
        self.assertEqual(nodes["b"]["frame"][2], 100)

    def test_grid_fixed_and_fraction_rows_and_explicit_stretch(self):
        root = {"id": "grid", "type": "grid", "columns": [{"fr": 1}], "rows": [50, {"fr": 1}, {"fr": 2}], "gap": 10,
                "children": [leaf("a"), leaf("b"), leaf("c")]}
        _, nodes = self.solve(root, height=370)
        self.assertEqual(nodes["a"]["frame"][3], 50)
        self.assertEqual(nodes["b"]["frame"][3], 100)
        self.assertEqual(nodes["c"]["frame"][3], 200)
        self.assertEqual(nodes["c"]["frame"][1], 170)

    def test_grid_fixed_row_cannot_hide_text(self):
        root = {"id": "grid", "type": "grid", "columns": [100], "rows": [20], "children": [text("a", "文字" * 10)]}
        with self.assertRaises(LayoutError) as caught:
            self.solve(root)
        self.assertEqual(caught.exception.diagnostic["axis"], "y")

    def test_auto_grid_row_stretches_nontext_using_measured_cell(self):
        root = {"id": "grid", "type": "grid", "columns": [{"fr": 1}, {"fr": 1}],
                "children": [text("copy", "正文决定本行自然高度。" * 4), leaf("visual")]}
        _, nodes = self.solve(root, width=400)
        self.assertEqual(nodes["visual"]["frame"][3], nodes["copy"]["frame"][3])
        root["children"][0] = leaf("copy")
        with self.assertRaisesRegex(LayoutError, "auto grid row"):
            self.solve(root)

    def test_fr_rows_without_definite_parent_height_are_rejected(self):
        root = {"id": "body", "type": "column", "children": [{"id": "grid", "type": "grid", "columns": [100], "rows": [{"fr": 1}], "children": [text("a")]}]}
        with self.assertRaisesRegex(LayoutError, "definite"):
            self.solve(root)

    def test_nested_padding_alignment_justify_surface_and_bounds(self):
        root = {"id": "body", "type": "column", "padding": [10, 20, 30, 40], "align": "center", "justify": "space-between",
                "surface": {"fill": "#F0F0F0"}, "children": [leaf("a", width=100, height=20),
                {"id": "row", "type": "row", "width": 200, "height": 100, "padding": 10, "align": "end", "justify": "end",
                 "children": [leaf("b", width=50, height=30)]}]}
        scene, nodes = self.solve(root, width=800, height=600, bounds=[50, 60, 500, 400])
        self.assertEqual(scene["elements"][0]["id"], "body--surface")
        self.assertEqual(nodes["body"]["frame"], [50, 60, 500, 400])
        self.assertEqual(nodes["a"]["frame"], [240, 80, 100, 20])
        self.assertEqual(nodes["row"]["frame"], [190, 320, 200, 100])
        self.assertEqual(nodes["b"]["frame"], [330, 380, 50, 30])
        self.assertTrue(all(item["type"] != "group" for item in scene["elements"]))

    def test_component_image_chart_shape_leaf_frames_are_injected(self):
        component = {"type": "component", "component": "comparison", "rows": [{"id": "first", "label": "参考", "value": 10}, {"id": "second", "label": "当前", "value": 12}]}
        root = {"id": "body", "type": "column", "gap": 5, "children": [leaf("comparison", height=220, element=component),
                leaf("image", aspect_ratio=4, element={"type": "image", "path": "example.png"}),
                leaf("chart", height=40, element={"type": "chart", "chart_type": "column", "categories": ["A"], "series": [{"name": "Value", "values": [1]}]})]}
        scene, nodes = self.solve(root, width=400)
        self.assertEqual(nodes["image"]["frame"], [0, 225, 400, 100])
        self.assertEqual([item["id"] for item in scene["elements"]], ["comparison", "image", "chart"])
        expanded = expand_page(scene, {}, [400, 500], self.tokens)
        self.assertEqual(expanded["elements"][0]["type"], "group")
        self.assertTrue(all(child["id"].startswith("comparison--") for child in expanded["elements"][0]["children"]))

    def test_row_definite_stretch_can_allocate_nontext_height(self):
        root = {"id": "row", "type": "row", "children": [leaf("a", basis=0, grow=1)]}
        _, nodes = self.solve(root, width=300, height=80)
        self.assertEqual(nodes["a"]["frame"], [0, 0, 300, 80])

    def test_auto_row_stretch_uses_measured_sibling_height(self):
        root = {"id": "body", "type": "column", "children": [{"id": "row", "type": "row", "gap": 10,
                "children": [text("copy", "需要自动测量的正文。" * 5, basis=0, grow=1), leaf("bar", width=20)]}]}
        _, nodes = self.solve(root, width=400)
        self.assertEqual(nodes["bar"]["frame"][3], nodes["copy"]["frame"][3])
        root["children"][0]["children"] = [leaf("bar", width=20)]
        with self.assertRaisesRegex(LayoutError, "definite stretched height"):
            self.solve(root)

    def test_unknown_nontext_height_and_undetermined_auto_width_fail(self):
        with self.assertRaisesRegex(LayoutError, "non-text leaf needs"):
            self.solve({"id": "body", "type": "column", "children": [leaf("a")]})
        with self.assertRaisesRegex(LayoutError, "auto width"):
            self.solve({"id": "row", "type": "row", "children": [leaf("a", height=20)]})

    def test_text_insets_runs_and_newlines_use_shared_measurement(self):
        item = text("copy", element={"type": "text", "role": "body", "runs": [{"text": "First ", "weight": 700}, {"text": "line\n第二段"}],
                                     "style": {"insets": [11, 13, 17, 19], "paragraph_gap": 12}})
        scene, nodes = self.solve({"id": "body", "type": "column", "children": [item]}, width=300)
        style = resolve_text_style(self.tokens, "body", {**item["element"]["style"], "weight": 700})
        expected = measure_text_block("First line\n第二段", 272, style, self.helpers)
        self.assertAlmostEqual(nodes["copy"]["frame"][3], expected["height"] + style["font_size"] * .1 + 32, places=5)
        rendered = SceneRenderer(scene, self.tokens, None, resolve_text, resolve_value, {}).render()[0]
        self.assertIn('id="copy"', rendered)
        self.assertEqual(nodes["copy"]["line_count"], len(expected["lines"]))

    def test_max_height_rejects_true_text_minimum(self):
        root = {"id": "body", "type": "column", "children": [text("copy", "多行正文" * 20, max_height=20)]}
        with self.assertRaises(LayoutError) as caught:
            self.solve(root, width=150)
        self.assertEqual(caught.exception.diagnostic["node_id"], "copy")
        self.assertGreater(caught.exception.diagnostic["required"], 20)

    def test_nested_definite_stretch_and_fr_containers_can_shrink(self):
        for child in (
            {"id": "inner", "type": "row", "height": 300, "shrink": 1,
             "children": [leaf("a", basis=0, grow=1, min_height=30)]},
            {"id": "inner", "type": "grid", "height": 300, "shrink": 1,
             "columns": [{"fr": 1}], "rows": [{"fr": 1}], "children": [leaf("a", min_height=30)]},
        ):
            with self.subTest(kind=child["type"]):
                root = {"id": "body", "type": "column", "children": [child, leaf("tail", height=20)]}
                _, nodes = self.solve(root, height=100)
                self.assertEqual(nodes["inner"]["frame"][3], 80)
                self.assertEqual(nodes["a"]["frame"][3], 80)
                self.assertEqual(nodes["tail"]["frame"][1], 80)

    def test_column_basis_is_main_size_before_overflow_check(self):
        root = {"id": "body", "type": "column", "children": [leaf("a", height=200, basis=30)]}
        _, nodes = self.solve(root, height=50)
        self.assertEqual(nodes["a"]["frame"][3], 30)

    def test_unbreakable_word_overflow_reports_runtime_required_width(self):
        root = {"id": "body", "type": "column", "children": [text("copy", "UnbreakableBusinessIdentifierWithoutSpaces")]}
        with self.assertRaises(LayoutError) as caught:
            self.solve(root, width=50)
        diagnostic = caught.exception.diagnostic
        self.assertEqual(diagnostic["code"], "layout_overflow")
        self.assertEqual(diagnostic["node_id"], "copy")
        self.assertEqual(diagnostic["axis"], "x")
        self.assertGreater(diagnostic["required"], 50)
        self.assertEqual(diagnostic["causes"], ["copy"])

    def test_gap_overflow_diagnostic_includes_padding_and_gaps(self):
        root = {"id": "body", "type": "row", "padding": 10, "gap": 40,
                "children": [leaf("a", basis=0, height=20), leaf("b", basis=0, height=20)]}
        with self.assertRaises(LayoutError) as caught:
            self.solve(root, width=50)
        self.assertEqual(caught.exception.diagnostic["available"], 50)
        self.assertEqual(caught.exception.diagnostic["required"], 60)

    def test_source_references_propagate_and_handwritten_paths_are_rejected(self):
        root = {"id": "body", "type": "column", "source_ref": "source", "children": [text("copy", source_ref="source", content_ref="claim")]}
        scene, nodes = self.solve(root)
        self.assertEqual(scene["elements"][0]["source_ref"], "source")
        self.assertEqual(nodes["body"]["source_ref"], "source")
        for element in ({"type": "shape", "shape": "path", "d": "M0 0 L10 10"}, {"type": "shape", "d": "M0 0"}):
            with self.subTest(element=element), self.assertRaisesRegex(LayoutError, "handwritten path"):
                validate_layout_page(page(leaf("a", height=20, element=element)))

    def test_nonfinite_payload_and_cyclic_tree_are_rejected_without_recursion(self):
        with self.assertRaises(LayoutError):
            validate_layout_page(page(text("copy", metadata={"bad": math.inf})))
        root = {"id": "cycle", "type": "column"}
        root["children"] = [root]
        with self.assertRaises(LayoutError):
            validate_layout_page(page(root))
        element = {"type": "text", "text": "text"}
        element["metadata"] = element
        with self.assertRaisesRegex(LayoutError, "acyclic"):
            validate_layout_page(page(text("copy", element=element)))

    def test_finite_extreme_weights_and_unsafe_size_arithmetic(self):
        root = {"id": "row", "type": "row", "children": [leaf("a", basis=0, grow=1e308, height=20), leaf("b", basis=0, grow=1e308, height=20)]}
        _, nodes = self.solve(root, width=200)
        self.assertEqual(nodes["a"]["frame"][2], 100)
        with self.assertRaises(LayoutError):
            self.solve({"id": "row", "type": "row", "gap": 1e308, "children": [leaf(f"a{i}", basis=0, height=20) for i in range(4)]})

    def test_catalog_determinism_and_input_immutability(self):
        original = layout_catalog()["example"]
        snapshot = copy.deepcopy(original)
        first = lower_layout_page(original, {}, [1280, 720], self.tokens)
        second = lower_layout_page(original, {}, [1280, 720], self.tokens)
        self.assertEqual(first, second)
        self.assertEqual(original, snapshot)
        self.assertEqual(first[1]["precision_decimals"], 6)
        catalog = layout_catalog("row")
        catalog["definitions"]["row"]["purpose"] = "mutated"
        self.assertNotEqual(catalog, layout_catalog("row"))
        with self.assertRaises(ValueError):
            layout_catalog("wrap")

    def test_fractional_geometry_remains_contained(self):
        root = {"id": "row", "type": "row", "gap": .07, "padding": [.13, 0, .17, 0], "children": [leaf(f"item{i}", basis=0, grow=1, height=10) for i in range(64)]}
        scene, _ = self.solve(root, width=1000.001, height=50)
        last = scene["elements"][-1]["frame"]
        self.assertLessEqual(last[0] + last[2], 1000.001 - .17 + .000002)

    def test_invalid_numeric_fields_are_rejected(self):
        for value in (True, False, -1, math.nan, math.inf, -math.inf, "50%", {}, []):
            for field in ("width", "height", "min_width", "max_width", "min_height", "grow", "shrink", "basis", "aspect_ratio"):
                with self.subTest(value=value, field=field), self.assertRaises(LayoutError):
                    validate_layout_page(page(leaf("bad", **{"height": 20, field: value})))

    def test_invalid_tree_shape_duplicate_ids_surface_collision_and_fields(self):
        roots = [
            {"id": "body", "type": "column", "children": [text("a"), text("a")]},
            {"id": "body", "type": "column", "surface": {"fill": "#FFFFFF"}, "children": [text("body--surface")]},
            {"id": "body", "type": "grid", "columns": [{"fr": -1}], "children": [text("a")]},
            {"id": "body", "type": "column", "padding": [1, 2], "children": [text("a")]},
            text("a", span=2), text("a", min_width=50, max_width=20),
            text("a", element={"type": "text", "text": "a", "frame": [0, 0, 1, 1]}),
            text("a", element={"type": "text", "text": "a", "id": "other"}),
            text("a", element={"type": "text", "text": "a", "unknown": 2}),
            {"id": "bad", "type": {}},
            {"id": "bad", "type": "column", "align": [], "children": [text("a")]},
        ]
        for root in roots:
            with self.subTest(root=root), self.assertRaises(LayoutError):
                validate_layout_page(page(root))

    def test_tree_depth_node_count_and_child_limits(self):
        root = text("tail")
        for index in range(12):
            root = {"id": f"layer{index}", "type": "column", "children": [root]}
        with self.assertRaisesRegex(LayoutError, "depth"):
            validate_layout_page(page(root))
        with self.assertRaisesRegex(LayoutError, "1..64"):
            validate_layout_page(page({"id": "body", "type": "column", "children": [text(f"a{i}") for i in range(65)]}))
        root = {"id": "body", "type": "column", "children": [{"id": f"row{i}", "type": "row", "children": [text(f"a{i}_{j}") for j in range(64)]} for i in range(4)]}
        with self.assertRaisesRegex(LayoutError, "count"):
            validate_layout_page(page(root))


if __name__ == "__main__":
    unittest.main()
