"""Behavioral tests for measured component boxes and automatic small multiples."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from xml.etree import ElementTree as ET
from zipfile import ZipFile

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "skill-src/shared/scripts"))
sys.path.insert(0, str(PROJECT / "skill-src/how-to-report/scripts"))
from presentation_layout import LayoutError, layout_catalog, lower_layout_page
from presentation_composition import component_catalog, expand_page
from report_ppt import load_template


def ring(identifier, detail="一行说明", **payload):
    return {"id": identifier, "type": "leaf", "sizing": "intrinsic", "element": {
        "type": "component", "component": "progress-ring", "value": 25, "total": 100,
        "label": "当前比例", "detail": detail, "style": {"font_size": 18, "value_size": 28}, **payload}}


def grid(children, **options):
    return {"id": "grid", "type": "grid", "columns": {"auto_fit": "content", "max_columns": 5},
            "uniform_components": True, "column_gap": 16, "row_gap": 12, "children": children, **options}


class IntrinsicLayoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _, _, cls.tokens = load_template()

    def solve(self, root, width=900, height=1400, facts=None):
        page = {"id": "page", "kind": "layout", "layout_version": "0.1", "layout": root}
        scene, report = lower_layout_page(page, facts or {}, [width, height], self.tokens)
        groups = expand_page(scene, facts or {}, [width, height], self.tokens)["elements"]
        children = {c["id"]: c for group in groups if group["type"] == "group" for c in group["children"]}
        return scene, {n["id"]: n for n in report["nodes"]}, children

    def test_intrinsic_hug_long_detail_pushes_flow_without_shrinking_circle(self):
        root = {"id": "body", "type": "column", "gap": 13, "children": [ring("ratio"),
            {"id": "tail", "type": "leaf", "height": 25, "element": {"type": "shape", "shape": "rect"}}]}
        original = copy.deepcopy(root)
        _, short, short_children = self.solve(root, width=240)
        root["children"][0]["element"]["detail"] = "第一行说明\n第二行说明\n第三行说明"
        changed = copy.deepcopy(root)
        _, long, long_children = self.solve(root, width=240)
        self.assertEqual(root, changed)
        self.assertEqual(long_children["ratio--ring"]["frame"][2:], short_children["ratio--ring"]["frame"][2:])
        self.assertGreater(long["ratio"]["frame"][3], short["ratio"]["frame"][3])
        self.assertAlmostEqual(long["tail"]["frame"][1]-short["tail"]["frame"][1], long["ratio"]["frame"][3]-short["ratio"]["frame"][3])
        self.assertEqual(original["children"][0]["element"]["style"], root["children"][0]["element"]["style"])

    def test_uniform_slots_align_actual_geometry_with_different_text_lengths(self):
        root = grid([ring("a"), ring("b", "第一行说明\n第二行说明\n第三行说明", label="这是一条需要自动换行的较长中文标题")], columns=[{"fr": 1}, {"fr": 1}])
        _, nodes, shapes = self.solve(root, width=480)
        for suffix in ("ring", "label", "denominator", "detail"):
            self.assertEqual(shapes[f"a--{suffix}"]["frame"][1], shapes[f"b--{suffix}"]["frame"][1])
            self.assertEqual(shapes[f"a--{suffix}"]["frame"][3], shapes[f"b--{suffix}"]["frame"][3])
        self.assertEqual(shapes["a--ring"]["frame"][2:], shapes["b--ring"]["frame"][2:])
        self.assertEqual(nodes["a"]["component_intrinsic"]["metrics"], nodes["b"]["component_intrinsic"]["metrics"])

    def test_count_and_width_reflow_preserve_ids_and_last_row_circle_size(self):
        choices = []
        for count in (5, 6, 10):
            root = grid([ring(f"r{i}", style={"font_size": 18, "value_size": 52}) for i in range(count)])
            for width in (1200, 900):
                scene, nodes, shapes = self.solve(root, width=width, height=2400)
                choices.append((count, width, nodes["grid"]["grid_selection"]["columns"]))
                self.assertEqual([e["id"] for e in scene["elements"]], [f"r{i}" for i in range(count)])
                self.assertEqual(len({tuple(shapes[f"r{i}--ring"]["frame"][2:]) for i in range(count)}), 1)
        self.assertGreater(choices[-2][2], choices[-1][2])
        first = self.solve(grid([ring(f"r{i}") for i in range(6)]))[0]
        again = self.solve(grid([ring(f"r{i}") for i in range(6)]))[0]
        self.assertEqual(first, again)

    def test_wrappable_chinese_does_not_force_single_column(self):
        children = [ring(f"r{i}", label="这是较长但是可以自动换行的中文分类标题") for i in range(10)]
        _, nodes, _ = self.solve(grid(children), width=1200, height=2400)
        self.assertGreater(nodes["grid"]["grid_selection"]["columns"], 1)
        bad = grid([ring("long", label="UnbreakableIdentifier"*12)])
        with self.assertRaises(LayoutError):
            self.solve(bad, width=300)

    def test_fixed_height_and_hole_conflicts_fail_instead_of_shrinking(self):
        with self.assertRaises(LayoutError):
            self.solve({"id": "body", "type": "column", "children": [{**ring("a"), "height": 45}]})
        with self.assertRaisesRegex(LayoutError, "same hole_size"):
            self.solve(grid([ring("a", hole_size=75), ring("b", hole_size=65)]))
        with self.assertRaises(LayoutError):
            self.solve(grid([ring(f"r{i}") for i in range(10)]), height=60)

    def test_intrinsic_missing_detail_slot_keeps_group_geometry(self):
        a, b = ring("a"), ring("b")
        del b["element"]["detail"]
        _, _, shapes = self.solve(grid([a, b]), width=480)
        self.assertIn("a--detail", shapes)
        self.assertNotIn("b--detail", shapes)
        self.assertEqual(shapes["a--ring"]["frame"][2:], shapes["b--ring"]["frame"][2:])

    def test_intrinsic_bounds_contain_terminal_visible_text_envelope(self):
        from presentation_svg import runtime_helpers
        from presentation_typography import measure_text_block
        from text_measure import text_box
        for anchor in ("top", "middle", "bottom"):
            for has_detail in (True, False):
                item = ring("a", style={"font_size": 18, "value_size": 28, "vertical_anchor": anchor})
                if not has_detail:
                    del item["element"]["detail"]
                _, nodes, shapes = self.solve(grid([item]), width=300)
                terminal = shapes["a--detail" if has_detail else "a--denominator"]
                x, y, width, height = terminal["frame"]
                style = terminal["style"]
                left, top, right, bottom = style["insets"]
                measured = measure_text_block(terminal["text"], width-left-right, style, runtime_helpers())
                available = height-top-bottom
                offset = {"top": 0, "middle": (available-measured["height"])/2,
                          "bottom": available-measured["height"]}[anchor]
                bounds = text_box(x=x, baseline_y=y+top+offset+measured["baselines"][-1],
                                  size=style["font_size"], lines=1, dy=0,
                                  width=max(measured["widths"]), anchor="start")
                frame = nodes["a"]["frame"]
                self.assertLessEqual(bounds["bottom"], frame[1]+frame[3]+.00001)
                self.assertGreater(nodes["a"]["component_intrinsic"]["metrics"]["bottom_padding"], 0)

    def test_catalog_and_unsupported_intrinsic_are_explicit(self):
        self.assertIn("sizing", layout_catalog("leaf")["definitions"]["leaf"]["fields"])
        self.assertEqual(component_catalog("progress-ring")["intrinsic_layout"]["supported"], ["progress-ring"])
        wrong = ring("a")
        wrong["element"]["component"] = "comparison"
        with self.assertRaisesRegex(LayoutError, "progress-ring"):
            self.solve({"id": "body", "type": "column", "children": [wrong]})
        wrong = ring("a")
        wrong["element"]["computed_layout_metrics"] = {}
        with self.assertRaisesRegex(LayoutError, "assigned by the engine"):
            self.solve({"id": "body", "type": "column", "children": [wrong]})
        for invalid in (None, 1, "leaf"):
            with self.subTest(child=invalid), self.assertRaises(LayoutError):
                self.solve(grid([invalid]))

    def test_normal_cli_fact_patch_rebuild_and_native_values_are_deterministic(self):
        scripts = PROJECT / "skill-src/how-to-report/scripts"
        example = scripts.parent / "assets/design-system/examples/intrinsic-small-multiples.json"
        with tempfile.TemporaryDirectory(prefix="intrinsic-cli-") as folder:
            base = Path(folder)
            def cli(*args):
                result = subprocess.run([sys.executable, "-B", str(scripts / "report_engine.py"), *map(str, args)], cwd=base, capture_output=True, encoding="utf-8")
                self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
                return json.loads(result.stdout)
            cli("build", "--input", example, "--output", base / "first", "--geometry-policy", "computed")
            operations = [{"op": "replace", "path": "/facts/portion/value", "value": 100},
                          {"op": "replace", "path": "/facts/description/value", "value": "第一行说明\n第二行说明\n第三行说明"}]
            patch = base / "patch.json"
            patch.write_text(json.dumps(operations, ensure_ascii=False), encoding="utf-8")
            cli("patch", "--input", example, "--patch", patch, "--expected-revision", 1, "--operation-id", "change-number-and-copy", "--output", base / "changed.json")
            cli("build", "--input", base / "changed.json", "--output", base / "second", "--geometry-policy", "computed", "--pptx", base / "native.pptx")
            cli("build", "--input", base / "changed.json", "--output", base / "again", "--geometry-policy", "computed")
            def receipt(folder):
                return json.loads((base / folder / "engine-receipt.json").read_text(encoding="utf-8"))
            before, after, again = receipt("first"), receipt("second"), receipt("again")
            exported_check = json.loads((base / "second/validation/ppt-check.json").read_text(encoding="utf-8"))
            for checked in exported_check["files"]:
                self.assertFalse(any('--detail' in warning and 'data-pptx-bounds' in warning
                                     for warning in checked["warnings"]))
            self.assertNotEqual(before["input_sha256"], after["input_sha256"])
            self.assertEqual(json.loads((base / "changed.json").read_text(encoding="utf-8"))["revision"], 2)
            for item in ("scene", "report"):
                relative = after["pages"][0]["layout"][item + "_ref"]
                raw = (base / "second" / relative).read_bytes()
                self.assertEqual(raw, (base / "again" / relative).read_bytes())
                self.assertEqual(hashlib.sha256(raw).hexdigest(), after["pages"][0]["layout"][item + "_sha256"])
            def tail(folder, build):
                report = json.loads((base / folder / build["pages"][0]["layout"]["report_ref"]).read_text(encoding="utf-8"))["report"]
                return next(n["frame"][1] for n in report["nodes"] if n["id"] == "after")
            self.assertGreater(tail("second", after), tail("first", before))
            with ZipFile(base / "native.pptx") as package:
                namespace = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main", "c": "http://schemas.openxmlformats.org/drawingml/2006/chart"}
                slide = ET.fromstring(package.read("ppt/slides/slide1.xml"))
                self.assertIn("100%", [n.text for n in slide.findall(".//a:t", namespace)])
                charts = [ET.fromstring(package.read(name)) for name in package.namelist() if name.startswith("ppt/charts/chart") and name.endswith(".xml")]
                series = [[n.text for n in chart.findall(".//c:ser/c:val/c:numRef/c:numCache/c:pt/c:v", namespace)] for chart in charts]
                self.assertIn(["100", "0"], series)


if __name__ == "__main__":
    unittest.main()
