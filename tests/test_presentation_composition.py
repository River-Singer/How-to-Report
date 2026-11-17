"""Semantic component geometry, fact propagation and native compilation regressions."""
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
sys.path.insert(0, str(PROJECT / "skill-src" / "shared" / "scripts"))
sys.path.insert(0, str(SCRIPTS))

from presentation_composition import component_catalog, expand_page
from presentation_compiler import build_project
from presentation_document import evaluate_facts, validate_document
from report_ppt import TemplateInputError, load_template
import ppt_runtime


def partition():
    return {"id": "adoption", "type": "component", "component": "partition", "frame": [60, 160, 1100, 360],
            "total": {"ref": "total"}, "total_label": "分配总人数", "unit": "人",
            "segments": [{"id": "enabled", "label": "已启用", "value": {"ref": "enabled"},
                           "detail": "Current enabled employees"},
                          {"id": "remaining", "label": "尚未启用", "value": {"ref": "remaining"},
                           "detail": "仍需观察后续使用情况"}]}


def comparison():
    return {"id": "usage", "type": "component", "component": "comparison", "frame": [60, 160, 1100, 350],
            "baseline_id": "planned", "delta_label": "差额", "unit": "万点", "value_format": ".1f",
            "rows": [{"id": "planned", "label": "月度基准", "value": 166, "detail": "Purchased annual quota spread over twelve months"},
                     {"id": "actual", "label": "实际月用量", "value": 200, "detail": "约数，不含赠送额度"}]}


def evidence_map():
    return {"id": "decisions", "type": "component", "component": "evidence-map", "frame": [60, 160, 1100, 450],
            "columns": ["观察证据", "业务判断", "建议动作"],
            "rows": [{"id": "activation", "evidence": "分配席位仍有未激活人群，具体使用障碍待确认。", "meaning": "应先了解未启用员工的实际工作场景。", "action": "选择一组员工，观察从激活到完成首个工作任务。"},
                     {"id": "cost", "evidence": "Two source panels report different quota usage.", "meaning": "Budget decisions require a common reporting scope.", "action": "Reconcile the reporting period and purchase scope."}]}


def author(item):
    return {"schema_version": "0.1", "project_id": "composition-fixture", "revision": 1, "brief": {}, "sources": [],
            "facts": {"total": {"value": 100}, "enabled": {"value": 40},
                      "remaining": {"derived": {"op": "difference", "args": ["total", "enabled"]}}},
            "pages": [{"id": "overview", "kind": "scene", "job": "Show semantic relations", "elements": [item]}]}


def expanded(item, facts=None, tokens=None):
    return expand_page({"id": "p1", "elements": [item]}, facts or evaluate_facts(author(item)),
                       (1280, 720), tokens)["elements"][0]


class PresentationCompositionTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="semantic-component-")
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)

    def test_catalog_contract_and_normal_cli_discovery(self):
        catalog = component_catalog("partition")
        self.assertEqual(catalog["definitions"]["partition"]["capacity"]["segments"], [2, 4])
        catalog["style_defaults"]["font_size"] = 999
        _, _, tokens = load_template()
        self.assertEqual(component_catalog()["style_defaults"]["font_size"], tokens["font"]["sizes"]["body"])
        result = subprocess.run([sys.executable, "-B", str(SCRIPTS / "report_engine.py"), "components", "comparison"],
                                cwd=self.base, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["examples"]["comparison"]["baseline_id"], "planned")
        with self.assertRaisesRegex(TemplateInputError, "unknown component"):
            component_catalog("unknown")

    def test_defaults_follow_theme_roles_font_sizes_and_accent_palette(self):
        _, _, tokens = load_template()
        alternate = copy.deepcopy(tokens)
        alternate["theme"]["slots"].update(dk1="#183329", dk2="#57736B", lt2="#EFF7F0",
            accent1="#176642", accent2="#6B3A87", accent3="#347F89", accent4="#A7C8BC",
            accent5="#AD6633", accent6="#B39C5A")
        alternate["color"]["roles"]["secondary"] = "accent3"
        alternate["font"]["families"]["body"] = "Arial"
        alternate["font"]["sizes"].update(body=18, metric=30)
        first = component_catalog(tokens=tokens)
        second = component_catalog(tokens=alternate)
        self.assertNotEqual(first["style_defaults"], second["style_defaults"])
        self.assertEqual(second["style_defaults"], {
            "font_family": "Arial", "font_size": 18, "value_size": 30,
            "color": "#183329", "muted": "#57736B", "accent": "#347F89",
            "background": "#EFF7F0", "line": "#A7C8BC", "difference": "#AD6633"})
        self.assertEqual(second["palette"], [alternate["theme"]["slots"][f"accent{index}"] for index in range(1, 7)])
        children = {child["id"]: child for child in expanded(partition(), tokens=alternate)["children"]}
        self.assertEqual(children["adoption--enabled--bar"]["fill"], second["palette"][0])
        self.assertEqual(children["adoption--remaining--bar"]["fill"], second["palette"][1])
        self.assertEqual(children["adoption--enabled--label"]["style"]["font_family"], "Arial")
        self.assertEqual(children["adoption--enabled--label"]["style"]["font_size"], 18)
        self.assertEqual(children["adoption--enabled--value"]["style"]["font_size"], 30)

    def test_colour_change_preserves_fact_content_and_geometry(self):
        _, _, tokens = load_template()
        alternate = copy.deepcopy(tokens)
        for index, slot in enumerate(alternate["theme"]["slots"]):
            alternate["theme"]["slots"][slot] = f"#{index + 32:02X}6655"
        for item in (partition(), comparison(), evidence_map()):
            first = expanded(item, tokens=tokens)
            second = expanded(item, tokens=alternate)
            signature = lambda group: [(child["id"], child["type"], child.get("frame"), child.get("text"),
                                        child.get("from"), child.get("to")) for child in group["children"]]
            self.assertEqual(signature(first), signature(second))
            self.assertNotEqual(first["children"], second["children"])

    def test_explicit_component_and_item_style_overrides_theme(self):
        _, _, tokens = load_template()
        item = partition()
        item["style"] = {"font_family": "Arial", "font_size": 18, "value_size": 26,
                         "color": "#A12233", "muted": "#556677"}
        item["segments"][0]["color"] = "#112233"
        children = {child["id"]: child for child in expanded(item, tokens=tokens)["children"]}
        self.assertEqual(children["adoption--enabled--bar"]["fill"], "#112233")
        self.assertEqual(children["adoption--enabled--label"]["style"]["color"], "#A12233")
        self.assertEqual(children["adoption--enabled--label"]["style"]["font_family"], "Arial")
        self.assertEqual(children["adoption--enabled--value"]["style"]["font_size"], 26)
        self.assertEqual(children["adoption--enabled--share"]["style"]["color"], "#556677")
        self.assertEqual(children["adoption--remaining--bar"]["fill"], tokens["theme"]["slots"]["accent2"])

    def test_theme_defaults_reach_normal_build_svg_and_native_objects(self):
        _, _, tokens = load_template()
        tokens["font"]["families"]["body"] = "Arial"
        tokens["font"]["sizes"].update(body=18, metric=30)
        tokens["theme"]["slots"].update(dk1="#184433", accent1="#226644", accent2="#773388")
        token_path = self.base / "alternate-tokens.json"
        token_path.write_text(json.dumps(tokens), encoding="utf-8")
        discovery = subprocess.run([sys.executable, "-B", str(SCRIPTS / "report_engine.py"), "components", "partition",
                                    "--tokens", str(token_path)], cwd=self.base, capture_output=True,
                                   text=True, encoding="utf-8")
        self.assertEqual(discovery.returncode, 0, discovery.stderr)
        actual_defaults = json.loads(discovery.stdout)["style_defaults"]
        self.assertEqual(actual_defaults["font_family"], "Arial")
        self.assertEqual(actual_defaults["color"], "#184433")
        target = self.base / "themed-project"
        build_project(author(partition()), target, tokens=token_path)
        svg = (target / "svg_output" / "01_overview.svg").read_text(encoding="utf-8")
        self.assertIn('font-family="Arial"', svg)
        self.assertIn("#226644", svg)
        self.assertIn("#184433", svg)
        ppt_runtime.check_project(target)
        output = self.base / "themed-native.pptx"
        ppt_runtime.export_project(target, output, target / "tokens.json")
        with ZipFile(output) as package:
            xml = ET.fromstring(package.read("ppt/slides/slide1.xml"))
            fills = {node.get("val") for node in xml.findall(".//a:srgbClr", ppt_runtime.NS)}
            theme = ET.fromstring(package.read("ppt/theme/theme1.xml"))
            scheme = theme.find(".//a:clrScheme", ppt_runtime.NS)
            slots = {node.tag.rsplit("}", 1)[-1]: list(node)[0].get("val") for node in scheme}
            aliases = {"tx1": "dk1", "bg1": "lt1", "tx2": "dk2", "bg2": "lt2"}
            fills.update(slots.get(aliases.get(node.get("val"), node.get("val")))
                         for node in xml.findall(".//a:schemeClr", ppt_runtime.NS))
            self.assertTrue({"226644", "773388", "184433"}.issubset(fills))
            font_scheme = theme.find(".//a:fontScheme", ppt_runtime.NS)
            font_aliases = {f"+{prefix}-{script}": font_scheme.find(f"a:{kind}/a:{tag}", ppt_runtime.NS).get("typeface")
                            for prefix, kind in (("mj", "majorFont"), ("mn", "minorFont"))
                            for script, tag in (("lt", "latin"), ("ea", "ea"), ("cs", "cs"))}
            typefaces = {font_aliases.get(node.get("typeface"), node.get("typeface"))
                         for node in xml.findall(".//a:latin", ppt_runtime.NS)}
            self.assertIn("Arial", typefaces)
            sizes = {node.get("sz") for node in xml.findall(".//a:rPr", ppt_runtime.NS)}
            self.assertTrue({"1350", "2250"}.issubset(sizes))

    def test_receipts_record_actual_template_and_nested_component_branches(self):
        value = author({"id": "outer", "type": "group", "metadata": {"component": "comparison"},
                        "children": [partition()]})
        _, catalog, _ = load_template()
        family = catalog["families"]["ending"]
        content = copy.deepcopy(family["prototype_content"])
        content["actions"] = []
        value["pages"].append({"id": "ending", "kind": "template", "template": {"family": "ending", "content": content}})
        target = self.base / "usage-receipt"
        receipt = build_project(value, target)
        variant = family["default_variant"]
        expected = {"scene_pages": 1, "template_pages": 1, "families": {"ending": 1},
                    "variants": {f"ending/{variant}": 1}, "components": {"partition": 1}}
        self.assertEqual(receipt["asset_usage"], expected)
        self.assertEqual(receipt["pages"][0]["kind"], "scene")
        self.assertEqual(receipt["pages"][0]["components"], {"partition": 1})
        self.assertEqual(receipt["pages"][1]["template"], {"family": "ending", "variant": variant})
        mapping = json.loads((target / "object-map.json").read_text(encoding="utf-8"))
        self.assertEqual(mapping["asset_usage"], expected)

    def test_fact_change_updates_width_text_and_retains_semantic_ids(self):
        item = partition()
        original = copy.deepcopy(item)
        first = expanded(item)
        second = expanded(item, {"total": 100, "enabled": 60, "remaining": 40})
        self.assertEqual(item, original)
        by_id = lambda group: {child["id"]: child for child in group["children"]}
        first, second = by_id(first), by_id(second)
        self.assertEqual(first.keys(), second.keys())
        self.assertEqual(first["adoption--enabled--bar"]["frame"][2], 440)
        self.assertEqual(second["adoption--enabled--bar"]["frame"][2], 660)
        self.assertEqual(second["adoption--enabled--value"]["text"], "60人")
        self.assertEqual(second["adoption--enabled--share"]["text"], "60.0%")

    def test_partition_zero_segment_and_exact_sum_domain(self):
        group = expanded(partition(), {"total": 100, "enabled": 0, "remaining": 100})
        ids = {child["id"] for child in group["children"]}
        self.assertNotIn("adoption--enabled--bar", ids)
        self.assertIn("adoption--enabled--label", ids)
        for facts in ({"total": 100, "enabled": 50, "remaining": 60},
                      {"total": 100, "enabled": -1, "remaining": 101},
                      {"total": 0, "enabled": 0, "remaining": 0},
                      {"total": 100, "enabled": float("nan"), "remaining": 100}):
            with self.subTest(facts=facts), self.assertRaises(TemplateInputError):
                expanded(partition(), facts)

    def test_comparison_common_scale_and_negative_delta(self):
        item = comparison()
        item["rows"][1]["value"] = 100
        group = expanded(item)
        children = {child["id"]: child for child in group["children"]}
        baseline_width = children["usage--planned--bar"]["frame"][2]
        actual_width = children["usage--actual--bar"]["frame"][2]
        self.assertAlmostEqual(actual_width / baseline_width, 100 / 166)
        self.assertEqual(children["usage--actual--delta"]["text"], "差额 -66.0万点")
        item["rows"][1]["value"] = 200
        children = {child["id"]: child for child in expanded(item)["children"]}
        self.assertEqual(children["usage--actual--delta"]["text"], "差额 +34.0万点")

    def test_comparison_zero_baseline_and_invalid_domains(self):
        item = comparison()
        item["rows"][0]["value"] = 0
        group = expanded(item)
        delta = next(child for child in group["children"] if child["id"] == "usage--actual--delta")
        self.assertEqual(delta["text"], "差额 +200.0万点")
        for values in ([0, 0], [-1, 10], [float("nan"), 10]):
            bad = comparison()
            for row, value in zip(bad["rows"], values):
                row["value"] = value
            with self.subTest(values=values), self.assertRaises(TemplateInputError):
                expanded(bad)
        item["baseline_id"] = "missing"
        with self.assertRaisesRegex(TemplateInputError, "baseline_id"):
            expanded(item)

    def test_multiline_difference_reserves_space_above_detail(self):
        for density in ("comfortable", "compact"):
            item = comparison()
            item["density"] = density
            item["delta_label"] = "相对采购基准形成的实际用量差额"
            item["frame"][3] = 400
            group = expanded(item)
            children = {child["id"]: child for child in group["children"]}
            delta = children["usage--actual--delta"]["frame"]
            detail = children["usage--actual--detail"]["frame"]
            self.assertLessEqual(delta[1] + delta[3], detail[1])

    def test_compact_partition_retains_explicit_font_sizes_and_values(self):
        item = partition()
        item["density"] = "compact"
        item["frame"] = [60, 160, 552, 164]
        item["style"] = {"font_size": 18, "value_size": 26}
        item["segments"][0].pop("detail")
        item["segments"][1].pop("detail")
        children = {child["id"]: child for child in expanded(item)["children"]}
        metric = children["adoption--enabled--value"]
        share = children["adoption--enabled--share"]
        self.assertEqual(metric["style"]["font_size"], 26)
        self.assertEqual(metric["text"], "40人")
        self.assertEqual(share["text"], "40.0%")
        self.assertLess(metric["frame"][0] + metric["frame"][2], share["frame"][0])
        with self.assertRaisesRegex(TemplateInputError, "density"):
            expanded({**item, "density": "tiny"})

    def test_partial_component_metadata_in_existing_scene_remains_compatible(self):
        value = author({"id": "old-group", "type": "group", "metadata": {"component_contract": "application-specific"},
                        "children": [{"id": "old-shape", "type": "shape", "frame": [60, 160, 200, 100]}]})
        receipt = build_project(value, self.base / "old-metadata")
        group = next(obj for obj in receipt["pages"][0]["objects"] if obj["author_id"] == "old-group")
        self.assertNotIn("component", group)

    def test_compact_partition_key_does_not_overlap_small_text(self):
        for size in (2, 10, 12, 18):
            item = partition()
            item.update(density="compact", style={"font_size": size, "value_size": 18})
            children = {child["id"]: child for child in expanded(item)["children"]}
            key = children["adoption--enabled--key"]["frame"]
            label = children["adoption--enabled--label"]["frame"]
            self.assertLess(key[0] + key[2], label[0])
            self.assertGreaterEqual(key[1], label[1])
            self.assertLessEqual(key[1] + key[3], label[1] + label[3])
            build_project(author(item), self.base / f"small-key-{size}")

    def test_compact_business_density_four_segments_two_panels_and_four_rows(self):
        membership = partition()
        membership.update(frame=[52, 182, 1176, 154], density="compact", total=17300,
                          total_label="采购席位", unit="", style={"font_size": 18, "value_size": 26})
        membership["segments"] = [
            {"id": "active", "label": "当日活跃", "value": 6947},
            {"id": "not-active", "label": "已激活·当日未活跃", "value": 2025},
            {"id": "not-activated", "label": "已分配·未激活", "value": 8076},
            {"id": "not-allocated", "label": "未分配", "value": 252},
        ]
        panels = []
        for identifier, left, total, participating in (("message", 52, 5644, 3437), ("docs", 676, 2926, 1141)):
            panel = partition()
            panel.update(id=identifier, frame=[left, 223, 552, 164], density="compact", total=total,
                         total_label="本模块活跃人数", unit="", style={"font_size": 18, "value_size": 26})
            panel["segments"] = [{"id": "participating", "label": "当日发送或创建", "value": participating},
                                 {"id": "remaining", "label": "其余模块活跃", "value": total - participating}]
            panels.append(panel)
        decisions = evidence_map()
        decisions.update(frame=[52, 208, 1176, 412], density="compact", style={"font_size": 18, "value_size": 26})
        decisions["rows"] = [{"id": f"row-{index}", "evidence": "当前观察\n分配与使用尚有落差\n具体原因仍待核实",
                              "meaning": "核对名单与适用权限\n选择一个已有高频事务\n辅导完成首次使用",
                              "action": "新增使用与后续活跃\n具体卡点及仍未使用原因"} for index in range(4)]
        value = author(membership)
        value["pages"].extend([{"id": "participation", "kind": "scene", "job": "Show two panels", "elements": panels},
                               {"id": "next-steps", "kind": "scene", "job": "Connect observations", "elements": [decisions]}])
        receipt = build_project(value, self.base / "compact-business")
        self.assertEqual(receipt["page_count"], 3)

    def test_textual_quantities_and_invalid_formats_rejected(self):
        item = partition()
        item["segments"][0]["value"]["format"] = "integer"
        with self.assertRaisesRegex(TemplateInputError, "finite number"):
            expanded(item)
        item = comparison()
        item["value_format"] = "unknown"
        with self.assertRaisesRegex(ValueError, "unsupported fact format"):
            expanded(item)

    def test_capacity_unknown_fields_and_stable_item_identity(self):
        for item in (partition(), comparison(), evidence_map()):
            collection = "segments" if item["component"] == "partition" else "rows"
            bad = copy.deepcopy(item)
            bad[collection] = bad[collection][:1]
            with self.assertRaisesRegex(TemplateInputError, "capacity"):
                expanded(bad)
            bad = copy.deepcopy(item)
            bad[collection][1]["id"] = bad[collection][0]["id"]
            with self.assertRaisesRegex(TemplateInputError, "unique stable"):
                expanded(bad)
            bad = copy.deepcopy(item)
            bad["paddingg"] = 10
            with self.assertRaisesRegex(TemplateInputError, "unsupported component fields"):
                expanded(bad)
            bad = copy.deepcopy(item)
            bad["style"] = {"fontsizze": 22}
            with self.assertRaisesRegex(TemplateInputError, "unsupported component style"):
                expanded(bad)

    def test_evidence_map_measured_rows_and_order_preserve_ids(self):
        item = evidence_map()
        before = expanded(item)
        row_shapes = [child for child in before["children"] if child.get("type") == "shape"]
        self.assertEqual(len(row_shapes), 6)
        self.assertEqual(len([child for child in before["children"] if child["type"] == "connector"]), 4)
        original_ids = {child["id"] for child in before["children"]}
        item["rows"].reverse()
        after = expanded(item)
        self.assertEqual({child["id"] for child in after["children"]}, original_ids)
        for group in (before, after):
            for child in group["children"]:
                if "frame" in child:
                    x, y, width, height = child["frame"]
                    self.assertGreaterEqual(x, item["frame"][0])
                    self.assertGreaterEqual(y, item["frame"][1])
                    self.assertLessEqual(x + width, item["frame"][0] + item["frame"][2] + .01)
                    self.assertLessEqual(y + height, item["frame"][1] + item["frame"][3] + .01)

    def test_long_content_fails_before_output_publication(self):
        for item in (partition(), comparison(), evidence_map()):
            item["frame"][3] = 25
            with self.subTest(kind=item["component"]), self.assertRaisesRegex(TemplateInputError, "height|content area|component frame"):
                build_project(author(item), self.base / item["component"])
            self.assertFalse((self.base / item["component"]).exists())
        bad = evidence_map()
        bad["rows"][0]["evidence"] = "这是一段必须完整保存的很长中文。" * 80
        with self.assertRaisesRegex(TemplateInputError, "height"):
            build_project(author(bad), self.base / "long")
        self.assertFalse((self.base / "long").exists())

    def test_component_inside_group_and_duplicate_generated_id_rejected(self):
        value = author({"id": "outer", "type": "group", "children": [partition()]})
        target = self.base / "nested"
        receipt = build_project(value, target)
        group = next(item for item in receipt["pages"][0]["objects"] if item["author_id"] == "adoption")
        self.assertEqual(group["component"]["component"], "partition")
        value["pages"][0]["elements"].append({"id": "adoption--enabled--bar", "type": "shape", "frame": [10, 10, 20, 20]})
        with self.assertRaisesRegex(TemplateInputError, "duplicate scene id"):
            build_project(value, self.base / "duplicate")

    def test_normal_cli_build_native_groups_text_and_attached_connectors(self):
        value = author(partition())
        value["pages"].extend([{"id": "comparison", "kind": "scene", "job": "Compare", "elements": [comparison()]},
                               {"id": "decision", "kind": "scene", "job": "Relate evidence", "elements": [evidence_map()]}])
        validate_document(value)
        source = self.base / "author.json"
        source.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")
        target = self.base / "compiled"
        output = self.base / "editable.pptx"
        result = subprocess.run([sys.executable, "-B", str(SCRIPTS / "report_engine.py"), "build", "--geometry-policy", "legacy-replay", "--input", str(source),
                                 "--output", str(target), "--pptx", str(output)],
                                cwd=self.base, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["page_count"], 3)
        receipt = json.loads((target / "engine-receipt.json").read_text(encoding="utf-8"))
        self.assertIn("presentation_composition.py", receipt["compiler_files"])
        ns = ppt_runtime.NS
        with ZipFile(output) as package:
            first = ET.fromstring(package.read("ppt/slides/slide1.xml"))
            self.assertIsNotNone(first.find(".//p:grpSp", ns))
            texts = [node.text or "" for node in first.findall(".//a:t", ns)]
            self.assertIn("40人", texts)
            self.assertIn("Current enabled employees", "".join(texts))
            third = ET.fromstring(package.read("ppt/slides/slide3.xml"))
            connectors = third.findall(".//p:cxnSp", ns)
            self.assertEqual(len(connectors), 4)
            group = third.find(".//p:grpSp", ns)
            shape_ids = {node.get("id") for node in group.findall("./p:sp/p:nvSpPr/p:cNvPr", ns)}
            for connector in connectors:
                self.assertIn(connector.find(".//a:stCxn", ns).get("id"), shape_ids)
                self.assertIn(connector.find(".//a:endCxn", ns).get("id"), shape_ids)


if __name__ == "__main__":
    unittest.main()
