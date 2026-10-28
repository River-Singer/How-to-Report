"""Synthetic deterministic renderer checks; real-browser verification is separate."""
from copy import deepcopy
import hashlib
from html.parser import HTMLParser
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

PROJECT = Path(__file__).resolve().parents[1]
SOURCE = PROJECT / "skill-src" / "how-to-report"


class Nodes(HTMLParser):
    def __init__(self, value):
        super().__init__()
        self.tags = []
        self.feed(value)

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))


class ReportHTMLTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="report-html-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.package = self.root / "standalone"
        scripts = self.package / "scripts"
        scripts.mkdir(parents=True)
        for name in ("report_html.py", "report_run.py"):
            shutil.copyfile(SOURCE / "scripts" / name, scripts / name)
        shutil.copyfile(PROJECT / "skill-src/shared/scripts/validate_run.py", scripts / "validate_run.py")
        shutil.copytree(SOURCE / "assets/report-html", self.package / "assets/report-html")
        self.plan = json.loads((self.package / "assets/report-html/sample-plan.json").read_text(encoding="utf-8"))
        self.composed = deepcopy(self.plan)
        self.plan["pages"] = self.plan["pages"][:4]
        self.input = self.root / "输入 #1 50%.json"
        self.output = self.root / "演示 #1 50%"
        self.cwd = self.root / "unrelated"
        self.cwd.mkdir()
        self.write()

    def write(self):
        self.input.write_text(json.dumps(self.plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def run_cli(self, expected=0, isolated=False):
        result = subprocess.run([sys.executable, *(["-I"] if isolated else []), str(self.package / "scripts/report_html.py"), "render", str(self.input), "--output", str(self.output)], cwd=self.cwd, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        return json.loads(result.stdout)

    def helper(self):
        spec = importlib.util.spec_from_file_location("report_html_under_test", self.package / "scripts/report_html.py")
        helper = importlib.util.module_from_spec(spec)
        previous_path, previous_flag = sys.path[:], sys.dont_write_bytecode
        try:
            spec.loader.exec_module(helper)
        finally:
            sys.path[:] = previous_path
            sys.dont_write_bytecode = previous_flag
        return helper

    @staticmethod
    def snapshot(directory):
        return {p.relative_to(directory).as_posix(): (p.read_bytes(), p.stat().st_mtime_ns) for p in directory.rglob("*") if p.is_file()}

    def test_actual_outputs_capture_input_and_hashes_without_claiming_checks(self):
        original = self.input.read_bytes()
        result = self.run_cli()
        self.assertEqual(set(p.name for p in self.output.iterdir()), {"index.html", "plan.json", "page-map.json", "render-receipt.json"})
        self.assertEqual((self.output / "plan.json").read_bytes(), original)
        receipt = json.loads((self.output / "render-receipt.json").read_text(encoding="utf-8"))
        for name, digest in receipt["files"].items():
            self.assertEqual(hashlib.sha256((self.output/name).read_bytes()).hexdigest(), digest)
        self.assertEqual(result["browser_validation"], "not_run")
        self.assertEqual(result["semantic_validation"], "not_run")
        self.assertEqual(result["run_mutation"], "not_performed")

    def test_mapping_matches_actual_page_element_ids_and_declared_references(self):
        self.run_cli()
        mapping = json.loads((self.output / "page-map.json").read_text(encoding="utf-8"))
        nodes = Nodes((self.output / "index.html").read_text(encoding="utf-8"))
        actual = {attrs["id"]: attrs for _, attrs in nodes.tags if "id" in attrs}
        for entry in mapping["elements"]:
            node = actual[entry["selector"][1:]]
            if "element_id" in entry:
                self.assertEqual(json.loads(node["data-refs"]), entry["refs"])
            elif entry["page_id"] == "data":
                self.assertEqual(entry["displayed"]["unit"], self.plan["pages"][-1]["unit"])
                self.assertEqual(entry["displayed"]["layout"], "data")
        self.assertEqual({attrs["data-layout"] for _, attrs in nodes.tags if "data-layout" in attrs}, {"focus", "compare", "sequence", "data"})

    def test_markup_and_reference_strings_stay_inert_text(self):
        attack = '</script><script>window.HACKED=true</script><img src="https://bad.test/x" onerror="alert(1)">'
        for page in self.plan["pages"]:
            page["title"] = attack
            page["elements"][0]["body"] = attack
            page["refs"] = [{"id": attack, "revision": 1, "locator": attack}]
        self.write()
        self.run_cli()
        html = (self.output / "index.html").read_text(encoding="utf-8")
        tags = Nodes(html).tags
        self.assertEqual(sum(tag == "script" for tag, _ in tags), 1)
        self.assertFalse(any(tag in ("img", "iframe", "form", "link", "base") for tag, _ in tags))
        self.assertIn("&lt;/script&gt;", html)
        self.assertNotIn('<script>window.HACKED', html)

    def test_null_zero_negative_remain_distinct_with_finite_geometry(self):
        self.run_cli()
        nodes = Nodes((self.output / "index.html").read_text(encoding="utf-8"))
        rows = {attrs["data-element-id"]: attrs["data-value"] for _, attrs in nodes.tags if "data-value" in attrs}
        self.assertEqual(rows, {"positive": "12", "negative": "-4", "zero": "0", "missing": "null"})
        bars = [attrs for _, attrs in nodes.tags if "bar " in attrs.get("class", "")]
        self.assertEqual(len(bars), 3)
        self.assertTrue(any("width:0.00000000%" in b["style"] for b in bars))
        self.assertFalse(any("nan" in b["style"].lower() or "inf" in b["style"].lower() for b in bars))

    def test_all_zero_or_missing_data_does_not_divide_by_zero(self):
        helper = self.helper()
        for value in (0, None):
            plan = deepcopy(self.plan)
            for element in plan["pages"][-1]["elements"]:
                element["value"] = value
            html, _ = helper.render_document(helper.validate(plan))
            self.assertNotIn(b"width:nan", html.lower())
            self.assertNotIn(b"width:inf", html.lower())

    def test_no_overwrite_preserves_previous_output(self):
        self.run_cli()
        before = self.snapshot(self.output)
        self.run_cli(expected=2)
        self.assertEqual(before, self.snapshot(self.output))

    def test_file_destination_missing_parent_and_package_destination_refused(self):
        for kind in ("file", "parent", "package"):
            with self.subTest(kind=kind):
                if kind == "file":
                    self.output = self.root / "existing"
                    self.output.write_text("preserve", encoding="utf-8")
                elif kind == "parent":
                    self.output = self.root / "absent-parent" / "deck"
                else:
                    self.output = self.package / "deck"
                self.run_cli(expected=2)
                if kind != "file":
                    self.assertFalse(self.output.exists())
                else:
                    self.assertEqual(self.output.read_text(), "preserve")

    def test_invalid_root_and_page_shapes_fail_before_output(self):
        helper = self.helper()
        for invalid in (None, [], {}, {"page_plan_version": "0.1"}):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                helper.validate(invalid)
        for field, value in (("layout", []), ("id", {}), ("limits", []), ("elements", None), ("refs", "bad")):
            plan = deepcopy(self.plan)
            plan["pages"][0][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                helper.validate(plan)

    def test_duplicate_unsafe_ids_and_unknown_fields_are_rejected(self):
        helper = self.helper()
        for identifier in ("bad id", "../x", 'x" onload="x', self.plan["pages"][0]["id"]):
            plan = deepcopy(self.plan)
            plan["pages"][1]["elements"][0]["id"] = identifier
            with self.subTest(identifier=identifier), self.assertRaises(ValueError):
                helper.validate(plan)
        self.plan["pages"][0]["html"] = "<h1>unsafe</h1>"
        self.write()
        self.run_cli(expected=2)
        self.assertFalse(self.output.exists())

    def test_invalid_number_types_and_missing_values_rejected(self):
        helper = self.helper()
        for value in (True, "0", float("inf"), float("nan"), 1e13, -(10**1000), [], {}):
            plan = deepcopy(self.plan)
            plan["pages"][-1]["elements"][0]["value"] = value
            with self.subTest(value=repr(value)[:40]), self.assertRaises(ValueError):
                helper.validate(plan)
        del self.plan["pages"][-1]["elements"][0]["value"]
        self.write()
        self.run_cli(expected=2)
        self.assertFalse(self.output.exists())

    def test_duplicate_data_labels_and_layout_counts_rejected(self):
        helper = self.helper()
        self.plan["pages"][-1]["elements"][1]["title"] = " " + self.plan["pages"][-1]["elements"][0]["title"] + " "
        with self.assertRaises(ValueError):
            helper.validate(self.plan)
        self.plan["pages"] = [self.plan["pages"][1]]
        self.plan["pages"][0]["elements"].pop()
        with self.assertRaises(ValueError):
            helper.validate(self.plan)

    def test_exact_references_reject_bool_revision_and_duplicates(self):
        helper = self.helper()
        for values in ([{"id": "s", "revision": True}], [{"id": "s", "revision": 0}], [{"id": "s", "revision": 1}]*2, [{"id": "s", "revision": 1, "locator": []}]):
            plan = deepcopy(self.plan)
            plan["pages"][0]["refs"] = values
            with self.subTest(values=values), self.assertRaises(ValueError):
                helper.validate(plan)

    def test_empty_refs_are_visible_unresolved_not_fabricated(self):
        self.plan["pages"][0]["refs"] = []
        self.plan["pages"][0]["elements"][0]["refs"] = []
        self.write()
        self.run_cli()
        self.assertIn("未提供引用", (self.output/"index.html").read_text(encoding="utf-8"))

    def test_duplicate_json_key_and_nonfinite_json_fail_without_output(self):
        for raw in ('{"page_plan_version":"0.1","page_plan_version":"0.2"}', '{"title":NaN}', '\ud800'):
            with self.subTest(raw=repr(raw)):
                self.input.write_bytes(raw.encode("utf-8", errors="surrogatepass"))
                self.run_cli(expected=2)
                self.assertFalse(self.output.exists())

    def test_bom_plan_bytes_preserved(self):
        self.input.write_bytes(b"\xef\xbb\xbf" + self.input.read_bytes())
        self.run_cli()
        self.assertEqual((self.output/"plan.json").read_bytes(), self.input.read_bytes())

    def test_long_content_is_preserved_for_actual_browser_check(self):
        body = "CONTENT " * 1000
        self.plan["pages"][0]["elements"][0]["body"] = body
        self.write()
        result = self.run_cli()
        self.assertIn(body, (self.output/"index.html").read_text(encoding="utf-8"))
        self.assertEqual(result["browser_validation"], "not_run")

    def test_remote_output_rejected_before_filesystem_probe(self):
        helper = self.helper()
        with patch.object(helper.os.path, "lexists", side_effect=AssertionError("must not probe")), self.assertRaises(ValueError):
            helper.output_path(Path("//server/share/deck"))

    def test_reparse_write_component_is_refused(self):
        helper = self.helper()
        real = Path.lstat
        def reparse(path, *args, **kwargs):
            result = real(path, *args, **kwargs)
            if path == self.root:
                class Reparse:
                    st_mode = result.st_mode
                    st_file_attributes = 0x400
                return Reparse()
            return result
        with patch.object(Path, "lstat", reparse), self.assertRaises(ValueError):
            helper.output_path(self.output)
        self.assertFalse(self.output.exists())

    def test_partial_write_failure_preserves_files_and_refuses_retry(self):
        helper = self.helper()
        original = Path.open
        def fail(path, *args, **kwargs):
            if path.name == "page-map.json" and args and args[0] == "xb":
                raise OSError("synthetic disk failure")
            return original(path, *args, **kwargs)
        with patch.object(Path, "open", fail), self.assertRaises(OSError):
            helper.render(self.input, self.output)
        self.assertTrue((self.output/"index.html").is_file())
        before = self.snapshot(self.output)
        with self.assertRaises(ValueError):
            helper.render(self.input, self.output)
        self.assertEqual(self.snapshot(self.output), before)

    def test_missing_asset_preflights_before_output(self):
        (self.package/"assets/report-html/deck.js").unlink()
        self.run_cli(expected=2)
        self.assertFalse(self.output.exists())

    def test_independent_package_isolated_invocation_no_input_execution(self):
        before = self.snapshot(self.package)
        self.plan["pages"][0]["elements"][0]["body"] = '__import__("os").system("never executed")'
        self.write()
        self.run_cli(isolated=True)
        self.assertEqual(before, self.snapshot(self.package))
        self.assertFalse(list(self.package.rglob("__pycache__")))

    def test_composition_mapping_closes_over_actual_data_and_layout(self):
        self.plan = self.composed
        self.write()
        self.run_cli(isolated=True)
        nodes = Nodes((self.output/"index.html").read_text(encoding="utf-8"))
        actual = {a["id"]: a for _, a in nodes.tags if "id" in a}
        entries = json.loads((self.output/"page-map.json").read_text(encoding="utf-8"))["elements"]
        self.assertEqual(len(actual), len([a for _, a in nodes.tags if "id" in a]))
        data = [e for e in entries if "datum_id" in e]
        self.assertEqual({e["datum_id"] for e in data}, {a["data-datum-id"] for _, a in nodes.tags if "data-datum-id" in a})
        for entry in entries:
            attrs = actual[entry["selector"][1:]]
            if "element_id" in entry:
                self.assertEqual(json.loads(attrs["data-refs"]), entry["refs"])
            if "datum_id" in entry and "value" in entry["displayed"]:
                value = entry["displayed"]["value"]
                self.assertEqual(attrs["data-value"], "null" if value is None else str(value))
                self.assertIn("unit", entry["displayed"])
        for page in self.plan["pages"][4:]:
            mapped = next(e for e in entries if e["page_id"] == page["id"] and "element_id" not in e)
            self.assertEqual(mapped["displayed"]["tree"], page["tree"])

    def test_tree_rejects_unknown_duplicate_missing_reordered_leaves_and_css(self):
        helper = self.helper()
        original = self.composed["pages"][4]["tree"]
        cases = [
            {"element": "unknown"},
            {"type": "row", "weights": [1, 1], "children": [{"element": "structure"}]*2},
            {"type": "row", "weights": [1, 1], "children": [{"element": "ranking"}, {"element": "structure"}]},
            dict(original, style="display:none"),
            dict(original, weights=[True, 1]),
            dict(original, weights=[float("inf"), 1]),
            dict(original, weights=[0, 1]),
            dict(original, weights=[1]),
            dict(original, children=[]),
        ]
        for tree in cases:
            plan = deepcopy(self.composed)
            plan["pages"][4]["tree"] = tree
            with self.subTest(tree=tree), self.assertRaises(ValueError):
                helper.validate(plan)

    def test_tree_depth_and_node_budgets_are_checked_before_recursion(self):
        helper = self.helper()
        deep = {"element": "structure"}
        for _ in range(8):
            deep = {"type": "column", "weights": [1, 1], "children": [deep, {"element": "ranking"}]}
        wide = {"type": "row", "weights": [1]*6, "children": [{"type": "column", "weights": [1]*6, "children": [{"element": "structure"}]*6}]*6}
        for tree in (deep, wide):
            plan = deepcopy(self.composed)
            plan["pages"][4]["tree"] = tree
            with self.assertRaisesRegex(ValueError, "budget"):
                helper.validate(plan)

    def test_typed_shapes_reject_mismatched_axes_duplicate_labels_ids_and_invalid_values(self):
        helper = self.helper()
        mutations = [
            lambda p: p["pages"][4]["elements"][2]["chart"]["series"][0]["points"].pop(),
            lambda p: p["pages"][4]["elements"][2]["chart"]["x_labels"].__setitem__(1, "第1期"),
            lambda p: p["pages"][5]["elements"][0]["chart"]["cells"][0].pop(),
            lambda p: p["pages"][5]["elements"][0]["chart"]["cells"][0][0].__setitem__("value", True),
            lambda p: p["pages"][5]["elements"][0]["chart"]["cells"][0][0].__setitem__("id", "structure"),
            lambda p: p["pages"][4]["elements"][0]["levels"][0].__setitem__("label", "阶段结果与解释"),
            lambda p: p["pages"][4]["elements"][1]["chart"].__setitem__("kind", "raw-svg"),
            lambda p: p["pages"][4]["elements"][1].__setitem__("limits", []),
            lambda p: p["pages"][4]["elements"][1]["chart"]["items"][0].__setitem__("value", float("nan")),
            lambda p: p["pages"][5]["elements"][2].__setitem__("value", "15"),
        ]
        for mutate in mutations:
            plan = deepcopy(self.composed)
            mutate(plan)
            with self.subTest(mutation=mutate), self.assertRaises(ValueError):
                helper.validate(plan)

    def test_line_missing_values_break_paths_and_matrix_preserves_null_zero_negative(self):
        html, _ = self.helper().render_document(self.helper().validate(self.composed))
        nodes = Nodes(html.decode())
        paths = [a for t,a in nodes.tags if t == "path"]
        self.assertEqual([int(a["data-point-count"]) for a in paths if a["data-series-id"] == "trend-a"], [2])
        self.assertEqual([int(a["data-point-count"]) for a in paths if a["data-series-id"] == "trend-b"], [4])
        self.assertEqual(len([1 for t,a in nodes.tags if t == "circle"]), 7)
        cells = {a["data-datum-id"]: a for _,a in nodes.tags if "heat-cell" in a.get("class", "")}
        self.assertEqual(cells["matrix-0-2"]["data-value"], "null")
        self.assertIn("transparent", cells["matrix-0-2"]["style"])
        self.assertEqual(cells["matrix-1-1"]["data-value"], "0")
        self.assertEqual(cells["matrix-2-2"]["data-value"], "-20")
        self.assertNotIn("missing-cell", cells["matrix-1-1"]["class"])

    def test_all_missing_and_all_zero_new_charts_keep_finite_geometry(self):
        helper = self.helper()
        for value in (None, 0, -7):
            plan = deepcopy(self.composed)
            for series in plan["pages"][4]["elements"][2]["chart"]["series"]:
                for point in series["points"]:
                    point["value"] = value
            for row in plan["pages"][5]["elements"][0]["chart"]["cells"]:
                for cell in row:
                    cell["value"] = value
            html, _ = helper.render_document(helper.validate(plan))
            attrs = [a for _,a in Nodes(html.decode()).tags]
            geometry = " ".join(a.get("style", "") + a.get("d", "") + a.get("cx", "") + a.get("cy", "") for a in attrs)
            self.assertNotIn("nan", geometry.lower())
            self.assertNotIn("inf", geometry.lower())
            if value is None:
                self.assertFalse(any("line-segment" in a.get("class", "") for a in attrs))

    def test_adversarial_chart_labels_and_hierarchy_remain_text(self):
        plan = deepcopy(self.composed)
        attack = '</td><svg onload="window.PWN=1"><script>1</script>'
        plan["pages"][4]["elements"][2]["chart"]["x_labels"][0] = attack
        plan["pages"][5]["elements"][0]["chart"]["columns"][0] = attack
        plan["pages"][4]["elements"][0]["levels"][0]["body"] = attack
        html, _ = self.helper().render_document(self.helper().validate(plan))
        nodes = Nodes(html.decode()).tags
        self.assertEqual(sum(t == "script" for t,a in nodes), 1)
        self.assertFalse(any("onload" in a for t,a in nodes))
        self.assertIn("&lt;/td&gt;", html.decode())

    def test_text_element_and_single_leaf_composition_are_supported(self):
        plan = deepcopy(self.composed)
        page = plan["pages"][4]
        element = page["elements"][0]
        del element["levels"]
        element["type"] = "text"
        page["elements"] = [element]
        page["tree"] = {"element": element["id"]}
        html, _ = self.helper().render_document(self.helper().validate(plan))
        self.assertIn(b'type-text', html)

    def test_canvas_validates_dimensions_and_controls_print_and_runtime_css(self):
        helper = self.helper()
        plan = deepcopy(self.composed)
        plan["canvas"] = {"width": 1600, "height": 1000}
        html, _ = helper.render_document(helper.validate(plan))
        self.assertIn(b'--canvas-height:1000px', html)
        self.assertIn(b'@page{size:16.66666667in 10.41666667in', html)
        for canvas in ({"width": True, "height": 900}, {"width": 1600, "height": 10}, {"width": 2400, "height": 675}, {"width": 1600.5, "height": 900}, {"width": 1600, "height": 900, "css": "x"}):
            plan["canvas"] = canvas
            with self.subTest(canvas=canvas), self.assertRaises(ValueError):
                helper.validate(plan)


if __name__ == "__main__":
    unittest.main()
