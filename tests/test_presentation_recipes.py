"""Finite recipes lower through the normal compiler and reject invalid slots."""
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from xml.etree import ElementTree as ET
from zipfile import ZipFile
from unittest import mock


PROJECT = Path(__file__).resolve().parents[1]
SOURCE = PROJECT / "skill-src/how-to-report"
sys.path.insert(0, str(SOURCE / "scripts"))
from presentation_recipes import compose_document
from presentation_library import profile_path, resolve_profile_tokens
from presentation_document import evaluate_facts
from report_ppt import read_json


class RecipeTests(unittest.TestCase):
    def setUp(self):
        self.request = read_json(SOURCE / "assets/design-system/examples/three-recipes.json")

    def test_three_recipes_lower_to_scene_and_pin_profile(self):
        document = compose_document(self.request)
        self.assertEqual([page["kind"] for page in document["pages"]], ["scene"] * 3)
        self.assertEqual(sum(document["brief"]["recipe_usage"]["recipes"].values()), 3)
        self.assertEqual(resolve_profile_tokens(document), profile_path())
        self.assertEqual(document["facts"], self.request["facts"])
        value = next(item for item in document["pages"][0]["elements"] if item["id"] == "metric-a--value")
        unit = next(item for item in document["pages"][0]["elements"] if item["id"] == "metric-a--unit")
        self.assertAlmostEqual(unit["frame"][0] - value["frame"][0] - value["frame"][2], 8)

    def test_fact_update_changes_bound_values_without_copying_literals(self):
        self.request["facts"]["a"]["value"] = 47
        document = compose_document(self.request)
        self.assertEqual(evaluate_facts(document)["a"], 47)
        value = next(item for item in document["pages"][0]["elements"] if item["id"] == "metric-a--value")
        self.assertEqual(value["text"], {"ref": "a"})

    def test_scope_period_differences_visible_but_unit_scale_must_match(self):
        self.request["pages"] = [self.request["pages"][1]]
        panels = self.request["pages"][0]["slots"]["charts"]
        panels[1]["semantics"].update(scope="second population", period="second period")
        document = compose_document(self.request)
        texts = [item.get("text", "") for item in document["pages"][0]["elements"] if item["type"] == "text"]
        self.assertTrue(any("second population" in text for text in texts if isinstance(text, str)))
        panels[1]["semantics"]["unit"] = "different unit"
        with self.assertRaisesRegex(ValueError, "identical declared unit"):
            compose_document(self.request)

    def test_missing_facts_duplicate_ids_and_caller_frames_rejected(self):
        for change in ("missing", "duplicate", "frame", "type"):
            request = deepcopy(self.request)
            if change == "missing":
                request.pop("facts")
            elif change == "duplicate":
                request["pages"][1]["id"] = request["pages"][0]["id"]
            elif change == "frame":
                request["pages"][0]["slots"]["main"]["frame"] = [0, 0, 9000, 9000]
            else:
                request["pages"][0]["slots"]["main"]["use"] = "chart-vocabulary.scatterplot"
            with self.subTest(change=change), self.assertRaises(ValueError):
                compose_document(request)

    def test_long_labels_and_domain_errors_are_rejected(self):
        request = deepcopy(self.request)
        request["pages"][0]["slots"]["metrics"][0]["label"] = "非常长的标签" * 40
        with self.assertRaises(ValueError):
            compose_document(request)
        request = deepcopy(self.request)
        request["facts"]["a"]["value"] = -1
        with self.assertRaisesRegex(ValueError, "within declared shared scale"):
            compose_document(request)
        request = deepcopy(self.request)
        request["pages"][1]["slots"]["charts"][0]["chart"]["axes"] = {"value": {"minimum": 0, "maximum": 70}}
        with self.assertRaisesRegex(ValueError, "axes conflict"):
            compose_document(request)

    def test_child_typography_cannot_bypass_recipe_profile(self):
        for style in ({"font_family": "Arial"}, {"line_height": .5}, {"insets": [0, 0, 0, 0]},
                      {"fontFamily": "Arial"}, {"fontSize": 2}, {"fontFace": "Arial"}, {"bold": True}):
            request = deepcopy(self.request)
            request["pages"][0]["slots"]["main"]["style"] = style
            with self.subTest(style=style), self.assertRaisesRegex(ValueError, "typography"):
                compose_document(request)

    def test_profile_bytes_cannot_change_between_verification_and_consumption(self):
        import presentation_compiler as compiler
        import presentation_library as registry
        author = compose_document(self.request)
        with tempfile.TemporaryDirectory() as directory:
            tokens = Path(directory) / "tokens.json"
            original_bytes = profile_path().read_bytes()
            tokens.write_bytes(original_bytes)
            original_resolver = registry.resolve_profile_tokens
            changed = read_json(tokens)
            changed["theme"]["slots"]["dk1"] = "#123456"
            changed_bytes = json.dumps(changed).encode("utf-8")
            def mutate_after_resolve(document, supplied):
                result = original_resolver(document, supplied)
                tokens.write_bytes(changed_bytes)
                return result
            with mock.patch.object(registry, "resolve_profile_tokens", side_effect=mutate_after_resolve):
                with self.assertRaisesRegex(ValueError, "changed after verification"):
                    compiler.build_project(author, Path(directory) / "failed-one", tokens=tokens)
            tokens.write_bytes(original_bytes)
            original_loader = compiler.load_template
            def transient_different_load(*args):
                tokens.write_bytes(changed_bytes)
                try:
                    return original_loader(*args)
                finally:
                    tokens.write_bytes(original_bytes)
            with mock.patch.object(compiler, "load_template", side_effect=transient_different_load):
                with self.assertRaisesRegex(ValueError, "differ from declared profile"):
                    compiler.build_project(author, Path(directory) / "failed-two", tokens=tokens)
            self.assertFalse((Path(directory) / "failed-one").exists())
            self.assertFalse((Path(directory) / "failed-two").exists())

    def test_profile_conflict_and_legacy_behavior(self):
        document = compose_document(self.request)
        with tempfile.TemporaryDirectory() as directory:
            changed = Path(directory) / "different.json"
            changed.write_text("{}", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "conflict"):
                resolve_profile_tokens(document, changed)
            self.assertEqual(resolve_profile_tokens({"brief": {}}, changed), changed)

    def test_qualitative_recipe_allows_empty_facts_and_rejects_unknown_references(self):
        request = deepcopy(self.request)
        request["facts"] = {}
        request["pages"] = [request["pages"][2]]
        for index, row in enumerate(request["pages"][0]["slots"]["rows"]):
            row["evidence"]["paragraphs"][0]["text"] = f"Synthetic observation {index + 1}"
        document = compose_document(request)
        self.assertEqual(document["facts"], {})
        request["pages"][0]["slots"]["rows"][0]["evidence"]["paragraphs"][0]["text"] = {"ref": "missing"}
        with self.assertRaisesRegex(ValueError, "unknown fact"):
            compose_document(request)

    def test_quantitative_recipe_readouts_are_native_main_color_and_scene_defaults_stay_muted(self):
        request = deepcopy(self.request)
        page = request["pages"][0]
        request["pages"] = []
        children = [
            {"id": "ring-readout", "use": "component.progress-ring", "value": 25, "total": 100,
             "label": "Share", "text_roles": {"value": "metricCompact"}},
            {"id": "partition-readout", "use": "component.partition", "total": 100,
             "segments": [{"id": "part-a", "label": "Part A", "value": 25},
                          {"id": "part-b", "label": "Part B", "value": 75}]}]
        for index, child in enumerate(children):
            candidate = deepcopy(page)
            candidate["id"] = f"readout-{index}"
            for metric in candidate["slots"]["metrics"]:
                metric["id"] += f"-{index}"
            candidate["slots"]["main"] = child
            request["pages"].append(candidate)
            important = "detail" if index == 0 else "percent"
            for override in ({"text_roles": {important: "caption"}},
                             {"style": {"muted": "#A6A6A6"}}, {"style": {"color": "#A6A6A6"}}):
                invalid = deepcopy(request)
                invalid["pages"][-1]["slots"]["main"].update(override)
                with self.subTest(child=child["use"], override=override), self.assertRaisesRegex(ValueError, "dataCaption"):
                    compose_document(invalid)
        document = compose_document(request)
        legacy = []
        for index, child in enumerate(children):
            item = deepcopy(child)
            item["component"] = item.pop("use").split(".", 1)[1]
            item.update(id="legacy-" + item["id"], type="component", frame=[48 + index * 560, 140, 520, 400])
            legacy.append(item)
        document["pages"].append({"id": "legacy-scene", "kind": "scene", "elements": legacy})
        from presentation_compiler import build_project
        import ppt_runtime
        ns = {"p": "http://schemas.openxmlformats.org/presentationml/2006/main",
              "a": "http://schemas.openxmlformats.org/drawingml/2006/main"}
        with tempfile.TemporaryDirectory(prefix="recipe-readout-colors-") as directory:
            project, pptx = Path(directory) / "project", Path(directory) / "readouts.pptx"
            build_project(document, project)
            self.assertEqual(ppt_runtime.check_project(project)["status"], "pass")
            self.assertEqual(ppt_runtime.export_project(project, pptx, project / "tokens.json")["status"], "pass")
            with ZipFile(pptx) as package:
                theme = ET.fromstring(package.read("ppt/theme/theme1.xml"))
                scheme = {node.tag.rsplit("}", 1)[-1]: node[0].get("val", node[0].get("lastClr"))
                          for node in theme.find(".//a:clrScheme", ns)}
                for number, expected, count in ((1, "333333", 1), (2, "333333", 2), (3, "A6A6A6", 3)):
                    slide = ET.fromstring(package.read(f"ppt/slides/slide{number}.xml"))
                    readouts = [shape for shape in slide.findall(".//p:sp", ns)
                                if shape.find("p:nvSpPr/p:cNvPr", ns).get("name", "").endswith(("--denominator", "--share"))]
                    self.assertEqual(len(readouts), count)
                    for shape in readouts:
                        for props in shape.findall(".//a:rPr", ns):
                            color = props.find("a:solidFill", ns)[0]
                            actual = scheme[color.get("val")] if color.tag.endswith("}schemeClr") else color.get("val")
                            self.assertEqual(actual.upper(), expected)

    def test_chart_readout_color_overrides_are_rejected_and_series_colors_remain_available(self):
        overrides = [
            {"style": {"text_color": "#A6A6A6"}},
            {"data_labels": {"show_value": True, "color": "#A6A6A6"}},
            {"data_labels": {"show_value": True, "labelColors": ["#A6A6A6"]}},
            {"series": [{"name": "Items", "values": [25, 75],
                         "data_labels": {"show_value": True, "color": "#A6A6A6"}}]},
            {"series": [{"name": "Items", "values": [25, 75],
                         "data_labels": {"show_value": True, "points": [{"idx": 0, "color": "#A6A6A6"}]}}]}]
        for override in overrides:
            request = deepcopy(self.request)
            request["pages"][0]["slots"]["main"].update(override)
            with self.subTest(override=override), self.assertRaisesRegex(ValueError, "dataCaption"):
                compose_document(request)
        request = deepcopy(self.request)
        request["pages"][0]["slots"]["main"]["style"] = {"colors": ["#123456"]}
        request["pages"][0]["slots"]["main"]["series"][0]["point_colors"] = ["#123456", "#654321", "#ABCDEF"]
        document = compose_document(request)
        chart = next(item for item in document["pages"][0]["elements"] if item.get("id") == "main-chart")
        self.assertEqual(chart["style"]["colors"], ["#123456"])

    def test_cli_failed_compose_does_not_publish_author(self):
        with tempfile.TemporaryDirectory() as directory:
            source, output = Path(directory) / "request.json", Path(directory) / "author.json"
            request = deepcopy(self.request)
            request["pages"][0]["slots"]["main"]["use"] = "chart-vocabulary.spine"
            source.write_text(json.dumps(request), encoding="utf-8")
            result = subprocess.run([sys.executable, "-B", str(SOURCE / "scripts/report_engine.py"),
                                     "compose", "--input", str(source), "--output", str(output)],
                                    capture_output=True, text=True, encoding="utf-8")
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(output.exists())

    def test_single_paragraph_flow_passes_real_export_and_invalid_group_frame_fails(self):
        from presentation_compiler import build_project
        from presentation_document import resolve_text, resolve_value
        from presentation_svg import SceneRenderer
        import ppt_runtime
        request = deepcopy(self.request)
        request["pages"] = [request["pages"][2]]
        author = compose_document(request)
        with tempfile.TemporaryDirectory() as directory:
            project, pptx = Path(directory) / "project", Path(directory) / "flow.pptx"
            build_project(author, project)
            self.assertEqual(ppt_runtime.check_project(project)["status"], "pass")
            self.assertEqual(ppt_runtime.export_project(project, pptx, project / "tokens.json")["status"], "pass")
        page = {"id": "bad-frame", "elements": [{"id": "bad-group", "type": "group",
                "metadata": {"component_contract": "0.1", "component_frame": [48, 120, 100, 60]},
                "children": [{"id": "outside", "type": "shape", "shape": "rect",
                              "frame": [160, 120, 100, 50], "fill": "surfaceMuted"}]}]}
        tokens = read_json(profile_path())
        with self.assertRaisesRegex(ValueError, "does not contain"):
            SceneRenderer(page, tokens, None, resolve_text, resolve_value, {}).render()

    def test_nested_declared_groups_contribute_their_full_bounds(self):
        from presentation_document import resolve_text, resolve_value
        from presentation_svg import SceneRenderer
        from xml.etree import ElementTree as ET
        nested = {"id": "nested", "type": "group",
                  "metadata": {"component_contract": "0.1", "component_frame": [48, 120, 200, 200]},
                  "children": [{"id": "leaf", "type": "shape", "shape": "rect",
                                "frame": [60, 132, 30, 30], "fill": "surfaceMuted"}]}
        outer = {"id": "outer", "type": "group", "children": [nested],
                 "metadata": {"component_contract": "0.1", "component_frame": [48, 120, 100, 100]}}
        page = {"id": "nested-probe", "elements": [outer]}
        tokens = read_json(profile_path())
        with self.assertRaisesRegex(ValueError, "does not contain"):
            SceneRenderer(page, tokens, None, resolve_text, resolve_value, {}).render()
        outer.pop("metadata")
        svg, _, _ = SceneRenderer(page, tokens, None, resolve_text, resolve_value, {}).render()
        root = ET.fromstring(svg)
        group = next(node for node in root if node.get("id") == "outer")
        self.assertEqual(group.get("data-pptx-bounds"), "48 120 200 200")


if __name__ == "__main__":
    unittest.main()
