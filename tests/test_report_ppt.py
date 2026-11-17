"""Parameter/template regressions using structural values, without model calls."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skill-src" / "how-to-report" / "scripts"
sys.path.insert(0, str(SCRIPTS))
import report_ppt as ppt


class ReportPptTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root, cls.catalog, cls.tokens = ppt.load_template()

    def document(self, family="kpi", variant="strip-4"):
        content = copy.deepcopy(self.catalog["families"][family]["prototype_content"])
        content.update(self.catalog["families"][family]["variants"][variant].get("prototype_content", {}))
        return {"schema_version": 1, "template_id": "business-blue-v1", "pages": [{"id": "structure", "family": family, "variant": variant, "content": content}]}

    def test_all_variants_bind_every_text_and_use_common_frames(self):
        total = 0
        for family_id, family in self.catalog["families"].items():
            for variant_id, variant in family["variants"].items():
                content = copy.deepcopy(family["prototype_content"])
                content.update(variant.get("prototype_content", {}))
                if family.get("array_key"):
                    key = family["array_key"]
                    content[key] = content[key][:variant["capacity"]]
                page = {"id": "structure", "family": family_id, "variant": variant_id, "content": content, "config": {**{key: self.catalog["config_defaults"][key] for key in family["config_fields"]}, **variant.get("config_defaults", {})}}
                svg, bindings, _ = ppt.render_page(page, self.catalog, self.tokens, self.root)
                self.assertEqual(svg, (self.root / "templates" / "prototypes" / variant["prototype"]).read_text(encoding="utf-8"))
                xml = ET.fromstring(svg)
                self.assertEqual(xml.get("viewBox"), "0 0 1280 720")
                self.assertEqual(xml.find(".//*[@id='canvas-background']").get("fill"), "#FFFFFF")
                self.assertEqual(bindings[0]["frame"], self.tokens["header"]["titleFrame"])
                self.assertEqual({text.get("id") for text in xml.findall(".//{*}text")}, {binding["selector"] for binding in bindings})
                for binding in bindings:
                    self.assertLessEqual(binding["min_length"], binding["max_length"])
                total += 1
        self.assertEqual(total, 170)

    def test_source_collections_cover_each_original_page_and_text_field(self):
        collections = ppt.read_json(self.root / "templates" / "source-collections.json")
        self.assertEqual(collections["source_pages"], 128)
        self.assertEqual([len(group["pages"]) for group in collections["collections"]], [30, 24, 34, 40])
        for group in collections["collections"]:
            family = self.catalog["families"][group["family"]]
            for page in group["pages"]:
                variant = family["variants"][page["variant"]]
                geometry = ET.parse(self.root / variant["geometry"]).getroot()
                self.assertFalse(geometry.findall(".//{*}text"))
                self.assertTrue(all(node.get("d", "").strip() for node in geometry.findall(".//{*}path")))
                self.assertEqual(set(variant["fields"]), set(variant["prototype_content"]["nodes"]))
                self.assertTrue((self.root / page["manual"]).is_file())
                self.assertTrue((self.root / page["preview"]).is_file())
                for field in variant["fields"].values():
                    self.assertTrue(field["source_ref"].startswith("slide:"))
                    self.assertTrue(field["role"])
                    self.assertEqual(field["min_length"], 1)
                    self.assertGreaterEqual(field["max_length"], 1)

    def test_source_diagram_nodes_reject_unknown_missing_and_oversized_values(self):
        document = self.document("source-circular", "page-12")
        nodes = document["pages"][0]["content"]["nodes"]
        key = next(iter(nodes))
        nodes["unexpected"] = "节点"
        with self.assertRaisesRegex(ppt.TemplateInputError, "unexpected"):
            ppt.validate_document(document, self.catalog, self.root)
        del nodes["unexpected"]
        value = nodes.pop(key)
        with self.assertRaisesRegex(ppt.TemplateInputError, key):
            ppt.validate_document(document, self.catalog, self.root)
        nodes[key] = "文" * (self.catalog["families"]["source-circular"]["variants"]["page-12"]["fields"][key]["max_length"] + 1)
        with self.assertRaisesRegex(ppt.TemplateInputError, key):
            ppt.validate_document(document, self.catalog, self.root)
        nodes[key] = value
        ppt.validate_document(document, self.catalog, self.root)

    def test_101_pages_keep_parameter_order_in_native_slides_and_notes(self):
        from zipfile import ZipFile
        import posixpath
        sys.path.insert(0, str(ROOT / "skill-src" / "shared" / "scripts"))
        import ppt_runtime as runtime
        document = self.document()
        example = document["pages"][0]
        document["pages"] = []
        for index in range(1, 102):
            page = copy.deepcopy(example)
            page["id"] = f"page-{index}"
            page["content"]["title"] = f"顺序第{index}页"
            page["notes"] = f"notes-{index}"
            document["pages"].append(page)
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "ordered"
            receipt = ppt.build_project(document, target)
            self.assertEqual(receipt["pages"][0]["svg"], "svg_output/001_page-1.svg")
            self.assertEqual(receipt["pages"][-1]["svg"], "svg_output/101_page-101.svg")
            runtime.check_project(target, self.tokens)
            output = Path(temporary) / "ordered.pptx"
            inspection = runtime.export_project(target, output, self.tokens)
            self.assertEqual(inspection["counts"]["slides"], 101)
            with ZipFile(output) as package:
                for index, slide in enumerate(inspection["slides"], 1):
                    page_number = next(shape for shape in slide["shapes"] if "page_number" in (shape["name"] or ""))
                    self.assertEqual(page_number["text"], [str(index)])
                    title = next(shape for shape in slide["shapes"] if "slot-text-title" in (shape["name"] or ""))
                    self.assertEqual(title["text"], [f"顺序第{index}页"])
                    slide_path = slide["part"]
                    relationship_path = posixpath.join(posixpath.dirname(slide_path), "_rels", posixpath.basename(slide_path) + ".rels")
                    relationships = ET.fromstring(package.read(relationship_path))
                    relation = next(item for item in relationships if item.get("Type", "").endswith("/notesSlide"))
                    self.assertNotEqual(relation.get("TargetMode"), "External")
                    note_path = posixpath.normpath(posixpath.join(posixpath.dirname(slide_path), relation.get("Target")))
                    note = ET.fromstring(package.read(note_path))
                    self.assertIn(f"notes-{index}", [node.text for node in note.findall(".//a:t", runtime.NS)])

    def test_unknown_variant_and_unknown_field_fail(self):
        doc = self.document()
        doc["pages"][0]["variant"] = "unknown"
        with self.assertRaisesRegex(ppt.TemplateInputError, "variant"):
            ppt.validate_document(doc, self.catalog, self.root)
        doc = self.document()
        doc["pages"][0]["content"]["unexpected"] = "text"
        with self.assertRaisesRegex(ppt.TemplateInputError, "unexpected"):
            ppt.validate_document(doc, self.catalog, self.root)

    def test_variant_capacity_is_enforced(self):
        with self.assertRaisesRegex(ppt.TemplateInputError, "capacity 3"):
            ppt.validate_document(self.document(variant="cards-3"), self.catalog, self.root)

    def test_chart_count_ticks_and_optional_exact_value_labels(self):
        doc = self.document("chart", "wide")
        doc["pages"][0]["content"].update({
            "categories": ["A", "B", "C", "D"],
            "series": [{"name": "Users", "values": [5644, 2926, 1800, 272]}],
        })
        doc["pages"][0]["config"] = {"show_data_labels": True}
        page = ppt.validate_document(doc, self.catalog, self.root)["pages"][0]
        svg, bindings, _ = ppt.render_page(page, self.catalog, self.tokens, self.root)
        ticks = [binding["text"] for binding in bindings if binding["field"].startswith("chart_ticks.")]
        self.assertEqual(ticks, ["0", "2000", "4000", "6000"])
        labels = [binding["text"] for binding in bindings if binding["field"].startswith("value_labels.")]
        self.assertEqual(labels, ["5644", "2926", "1800", "272"])
        native = json.loads(ET.fromstring(svg).find(".//{*}metadata").text)
        self.assertEqual(native["axes"]["value"], {"minimum": 0, "maximum": 6000, "major_unit": 2000})
        self.assertTrue(native["data_labels"]["show_value"])
        doc["pages"][0]["config"]["show_data_labels"] = False
        page = ppt.validate_document(doc, self.catalog, self.root)["pages"][0]
        svg, bindings, _ = ppt.render_page(page, self.catalog, self.tokens, self.root)
        self.assertFalse(any(binding["field"].startswith("value_labels.") for binding in bindings))
        self.assertNotIn("data_labels", json.loads(ET.fromstring(svg).find(".//{*}metadata").text))

    def test_chart_scale_keeps_zero_negative_decimal_and_multiseries_values(self):
        for chart_type in ("column", "line"):
            for values in ([0, 0, 0], [-2.25, 0, 1.23456789], [-2.25, None, -0.5]):
                with self.subTest(chart_type=chart_type, values=values):
                    doc = self.document("chart", "wide")
                    doc["pages"][0]["content"].update({
                        "categories": ["A", "B", "C"],
                        "series": [{"name": "First", "values": values}, {"name": "Second", "values": [0, 0.5, -1]}],
                    })
                    doc["pages"][0]["config"] = {"chart_type": chart_type, "show_data_labels": True}
                    page = ppt.validate_document(doc, self.catalog, self.root)["pages"][0]
                    svg, bindings, _ = ppt.render_page(page, self.catalog, self.tokens, self.root)
                    native = json.loads(ET.fromstring(svg).find(".//{*}metadata").text)
                    self.assertEqual(native["series"][0]["values"], values)
                    axis = native["axes"]["value"]
                    self.assertLessEqual(axis["minimum"], min(value for value in [*values, 0, 0.5, -1] if value is not None))
                    self.assertGreaterEqual(axis["maximum"], max(value for value in [*values, 0, 0.5, -1] if value is not None))
                    self.assertGreater(axis["major_unit"], 0)
                    labels = [binding["text"] for binding in bindings if binding["field"].startswith("value_labels.0.")]
                    self.assertEqual(labels, [str(value) for value in values if value is not None])
        doc = self.document("chart", "wide")
        doc["pages"][0]["content"]["series"] = [{"name": "Zero", "values": [0]}]
        page = ppt.validate_document(doc, self.catalog, self.root)["pages"][0]
        svg, _, _ = ppt.render_page(page, self.catalog, self.tokens, self.root)
        self.assertEqual(json.loads(ET.fromstring(svg).find(".//{*}metadata").text)["axes"]["value"]["minimum"], 0)

    def test_chart_label_option_reaches_native_values_and_axis(self):
        from zipfile import ZipFile
        doc = self.document("chart", "wide")
        doc["pages"][0]["content"].update({
            "categories": ["A", "B", "C", "D"],
            "series": [{"name": "Count", "values": [13, 8, 5, 2]}],
        })
        doc["pages"][0]["config"] = {"show_data_labels": True}
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary) / "chart"
            ppt.build_project(doc, project)
            import ppt_runtime
            ppt_runtime.check_project(project, project / "tokens.json")
            output = project / "result.pptx"
            ppt_runtime.export_project(project, output, project / "tokens.json")
            with ZipFile(output) as archive:
                part = next(name for name in archive.namelist()
                            if name.startswith("ppt/charts/chart") and name.endswith(".xml"))
                chart = ET.fromstring(archive.read(part))
            ns = {"c": "http://schemas.openxmlformats.org/drawingml/2006/chart"}
            self.assertEqual(chart.find(".//c:dLbls/c:showVal", ns).get("val"), "1")
            self.assertEqual([float(node.text) for node in chart.findall(".//c:ser/c:val/c:numRef/c:numCache/c:pt/c:v", ns)], [13, 8, 5, 2])
            axis = chart.find(".//c:valAx", ns)
            self.assertEqual(float(axis.find("c:scaling/c:min", ns).get("val")), 0)
            self.assertEqual(float(axis.find("c:scaling/c:max", ns).get("val")), 15)
            self.assertEqual(float(axis.find("c:majorUnit", ns).get("val")), 5)

    def test_title_character_range_and_whitespace(self):
        for value in [" ", "x" * 33, "\ud800", "bad\x01value"]:
            doc = self.document()
            doc["pages"][0]["content"]["title"] = value
            with self.assertRaises(ppt.TemplateInputError):
                ppt.validate_document(doc, self.catalog, self.root)

    def test_measured_overflow_fails_without_truncation(self):
        doc = self.document("cover", "split")
        doc["pages"][0]["content"]["subtitle"] = "说明" * 20
        page = ppt.validate_document(doc, self.catalog, self.root)["pages"][0]
        with self.assertRaisesRegex(ppt.TemplateInputError, "measured"):
            ppt.render_page(page, self.catalog, self.tokens, self.root)

    def test_nonfinite_and_misaligned_chart_data_fail(self):
        doc = self.document("chart", "side")
        doc["pages"][0]["content"]["series"][0]["values"] = [float("nan")]
        with self.assertRaisesRegex(ppt.TemplateInputError, "finite"):
            ppt.validate_document(doc, self.catalog, self.root)
        doc = self.document("chart", "side")
        doc["pages"][0]["content"]["series"][0]["values"] = [0, 1]
        with self.assertRaisesRegex(ppt.TemplateInputError, "align"):
            ppt.validate_document(doc, self.catalog, self.root)

    def test_token_changes_change_the_actual_svg(self):
        page = ppt.validate_document(self.document(), self.catalog, self.root)["pages"][0]
        first, _, _ = ppt.render_page(page, self.catalog, self.tokens, self.root)
        tokens = copy.deepcopy(self.tokens)
        tokens["theme"]["slots"]["accent1"] = "#5385C5"
        tokens["spacing"]["lg"] = 32
        second, _, _ = ppt.render_page(page, self.catalog, tokens, self.root)
        self.assertNotEqual(first, second)
        self.assertIn("#5385C5", second)

    def test_config_rejects_fields_for_other_families(self):
        doc = self.document()
        doc["pages"][0]["config"] = {"chart_type": "line"}
        with self.assertRaisesRegex(ppt.TemplateInputError, "do not apply"):
            ppt.validate_document(doc, self.catalog, self.root)

    def test_icon_and_page_number_configuration_reaches_svg(self):
        doc = self.document("parallel", "columns-3")
        doc["pages"][0]["content"]["items"][0]["icon_key"] = "team"
        page = ppt.validate_document(doc, self.catalog, self.root)["pages"][0]
        svg, bindings, _ = ppt.render_page(page, self.catalog, self.tokens, self.root)
        self.assertTrue(ET.fromstring(svg).findall(".//{*}path"))
        page["config"]["show_icons"] = False
        page["config"]["show_page_number"] = False
        svg, bindings, _ = ppt.render_page(page, self.catalog, self.tokens, self.root)
        self.assertFalse(ET.fromstring(svg).findall(".//{*}path"))
        self.assertEqual(next(item for item in bindings if item["field"] == "page_number")["text"], "")

    def test_private_copy_is_exact_and_rejects_existing_target(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "template"
            receipt = ppt.copy_template(self.root, output)
            self.assertGreater(receipt["files"], 70)
            self.assertEqual((output / "templates" / "tokens.json").read_bytes(), (self.root / "templates" / "tokens.json").read_bytes())
            with self.assertRaisesRegex(ppt.TemplateInputError, "exists"):
                ppt.copy_template(self.root, output)

    def test_build_is_external_and_does_not_overwrite(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "report"
            receipt = ppt.build_project(self.document(), output)
            self.assertEqual(len(receipt["pages"]), 1)
            self.assertTrue((output / "parameter-receipt.json").is_file())
            with self.assertRaisesRegex(ppt.TemplateInputError, "exists"):
                ppt.build_project(self.document(), output)

    def test_docs_and_binding_receipts_are_current(self):
        receipt = ppt.read_json(self.root / "templates" / "text-bindings.json")
        self.assertEqual(receipt["tokens_sha256"], ppt.fingerprint(self.tokens))
        self.assertEqual(receipt["catalog_sha256"], ppt.fingerprint(self.catalog))
        self.assertEqual(receipt["pages_schema_sha256"], ppt.fingerprint(ppt.read_json(self.root / "templates" / "pages.schema.json")))
        self.assertEqual(len(receipt["variants"]), 170)
        for family_id in self.catalog["families"]:
            doc = (self.root / "docs" / "families" / f"{family_id}.md").read_text(encoding="utf-8")
            self.assertIn(ppt.fingerprint(self.catalog), doc)

    def test_gantt_date_ticks_describe_equal_time_periods(self):
        from datetime import date
        for variant, periods in (("annual-12", 12), ("halfyear-6", 6)):
            doc = self.document("gantt", variant)
            self.assertEqual(doc["pages"][0]["content"]["end"], "2000-12-31")
            doc["pages"][0]["content"]["tasks"] = [{"name": "任务", "start": "2000-01-01", "end": "2000-12-31"}]
            page = ppt.validate_document(doc, self.catalog, self.root)["pages"][0]
            _, bindings, _ = ppt.render_page(page, self.catalog, self.tokens, self.root)
            labels = [b["text"] for b in bindings if b["field"].startswith("period_labels.")]
            expected = [date.fromordinal(date(2000, 1, 1).toordinal() + 366 * index // periods).strftime("%m/%d") for index in range(periods)]
            self.assertEqual(labels, expected)
            self.assertEqual(next(b["text"] for b in bindings if b["field"] == "period_range"), "2000-01-01\n2000-12-31")

    def test_gantt_cross_year_and_partial_months_keep_calendar_dates(self):
        doc = self.document("gantt", "halfyear-6")
        doc["pages"][0]["content"].update({"start": "2025-10-15", "end": "2026-03-20",
            "tasks": [{"name": "任务", "start": "2025-10-15", "end": "2025-10-15"}]})
        page = ppt.validate_document(doc, self.catalog, self.root)["pages"][0]
        _, bindings, _ = ppt.render_page(page, self.catalog, self.tokens, self.root)
        self.assertEqual(next(b["text"] for b in bindings if b["field"] == "period_range"), "2025-10-15\n2026-03-20")
        self.assertEqual(next(b["text"] for b in bindings if b["field"] == "period_labels.0"), "10/15")
        doc["pages"][0]["content"]["end"] = "2026-04-20"
        ppt.validate_document(doc, self.catalog, self.root)

    def test_gantt_short_range_suppresses_duplicate_ticks_and_keeps_one_day_bar(self):
        doc = self.document("gantt", "halfyear-6")
        doc["pages"][0]["content"].update({"start": "2025-10-15", "end": "2025-10-16",
            "tasks": [{"name": "任务", "start": "2025-10-15", "end": "2025-10-15"}]})
        page = ppt.validate_document(doc, self.catalog, self.root)["pages"][0]
        svg, bindings, _ = ppt.render_page(page, self.catalog, self.tokens, self.root)
        labels = [b["text"] for b in bindings if b["field"].startswith("period_labels.")]
        self.assertEqual(labels, ["10/15", "", "", "10/16", "", ""])
        bar = next(node for node in ET.fromstring(svg).findall(".//{*}rect") if node.get("id", "").startswith("data-"))
        self.assertAlmostEqual(float(bar.get("width")), (1184 - 250 - 160) / 2)

    def test_font_weights_and_strategy_mission_use_measured_safe_frame(self):
        page = ppt.validate_document(self.document("strategy", "house-3"), self.catalog, self.root)["pages"][0]
        svg, bindings, _ = ppt.render_page(page, self.catalog, self.tokens, self.root)
        xml = ET.fromstring(svg)
        title = next(node for node in xml.findall(".//{*}text") if node.get("id") == "text-title")
        mission = next(node for node in xml.findall(".//{*}text") if node.get("id") == "text-mission")
        self.assertEqual(title.get("font-weight"), "700")
        self.assertEqual(title.get("font-family"), self.tokens["font"]["families"]["title"])
        self.assertEqual(mission.get("fill"), "#FFFFFF")
        frame = next(b["frame"] for b in bindings if b["field"] == "mission")
        bx, by, bw, _ = self.tokens["body"]["frame"]
        half_width_at_top = bw / 2 * (frame[1] - by) / 100
        self.assertGreater(frame[0], bx + bw / 2 - half_width_at_top)
        self.assertLess(frame[0] + frame[2], bx + bw / 2 + half_width_at_top)
        self.assertLessEqual(frame[1] + frame[3], by + 100)

    def test_cover_uses_complete_source_arrow_with_uniform_scale(self):
        page = ppt.validate_document(self.document("cover", "arrow"), self.catalog, self.root)["pages"][0]
        svg, _, _ = ppt.render_page(page, self.catalog, self.tokens, self.root)
        arrow = next(node for node in ET.fromstring(svg).findall(".//{*}polygon") if node.get("id") == "cover-rising-arrow")
        points = [tuple(map(float, point.split(","))) for point in arrow.get("points").split()]
        self.assertEqual(len(points), 14)
        xs, ys = zip(*points)
        self.assertAlmostEqual((max(xs) - min(xs)) / (max(ys) - min(ys)), 11727179 / 6393179, places=4)
        self.assertGreater(min(xs), 48 + 1184 * .78)
        self.assertLessEqual(max(xs), 1232)
        self.assertEqual(points[0][1], points[-1][1])

    def test_strategy_selects_two_to_six_cards_and_recalculates_frames(self):
        family = self.catalog["families"]["strategy"]
        for count in range(2, 7):
            with self.subTest(count=count):
                doc = self.document("strategy", f"house-{count}")
                doc["pages"][0].pop("variant")
                doc["pages"][0]["content"]["pillars"] = [{"title": "支柱", "body": "支撑说明"} for _ in range(count)]
                page = ppt.validate_document(doc, self.catalog, self.root)["pages"][0]
                self.assertEqual(page["variant"], f"house-{count}")
                svg, bindings, _ = ppt.render_page(page, self.catalog, self.tokens, self.root)
                cards = [node for node in ET.fromstring(svg).findall(".//{*}rect") if node.get("y") == "316" and node.get("height") == "224"]
                self.assertEqual(len(cards), count)
                expected_width = (1184 - 24 * (count - 1)) / count
                self.assertAlmostEqual(float(cards[-1].get("x")) + float(cards[-1].get("width")), 1232)
                for index, card in enumerate(cards):
                    self.assertAlmostEqual(float(card.get("width")), expected_width)
                    self.assertLess(float(card.get("y")) + float(card.get("height")), 120 + 430)
                    for field in ("title", "body"):
                        binding = next(item for item in bindings if item["field"] == f"pillars.{index}.{field}")
                        self.assertEqual(binding["text"], page["content"]["pillars"][index][field])
                        self.assertEqual(binding["max_length"], family["variants"][f"house-{count}"]["item_text_limits"][field])

    def test_strategy_keeps_legacy_three_slot_inputs(self):
        for explicit in (True, False):
            doc = self.document("strategy", "house-3")
            doc["pages"][0]["content"]["pillars"] = [{"title": "支柱", "body": "说明"}]
            if not explicit:
                doc["pages"][0].pop("variant")
            page = ppt.validate_document(doc, self.catalog, self.root)["pages"][0]
            self.assertEqual(page["variant"], "house-3")
            _, bindings, _ = ppt.render_page(page, self.catalog, self.tokens, self.root)
            self.assertEqual(len([item for item in bindings if item["field"].startswith("pillars.")]), 6)

    def test_parallel_two_and_four_cards_choose_matching_layouts(self):
        for count, variant in ((2, "columns-2"), (4, "grid-4")):
            doc = self.document("parallel", variant)
            doc["pages"][0].pop("variant")
            limits = self.catalog["families"]["parallel"]["variants"][variant]["item_text_limits"]
            doc["pages"][0]["content"]["items"] = [{"title": "中" * limits["title"], "body": "中" * limits["body"]} for _ in range(count)]
            page = ppt.validate_document(doc, self.catalog, self.root)["pages"][0]
            self.assertEqual(page["variant"], variant)
            svg, bindings, _ = ppt.render_page(page, self.catalog, self.tokens, self.root)
            cards = ET.fromstring(svg).findall(".//{*}rect")[1:]
            self.assertEqual(len(cards), count)
            self.assertTrue(all(binding["measured_height"] <= binding["frame"][3] for binding in bindings))
        doc = self.document("parallel", "columns-3")
        doc["pages"][0].pop("variant")
        self.assertEqual(ppt.validate_document(doc, self.catalog, self.root)["pages"][0]["variant"], "columns-3")

    def test_strategy_reports_variant_count_and_text_limit_errors(self):
        doc = self.document("strategy", "house-4")
        doc["pages"][0]["content"]["pillars"] = doc["pages"][0]["content"]["pillars"][:3]
        with self.assertRaisesRegex(ppt.TemplateInputError, "provide 4 items"):
            ppt.validate_document(doc, self.catalog, self.root)
        doc = self.document("strategy", "house-6")
        doc["pages"][0]["content"]["pillars"][0]["title"] = "标题过长字段"
        with self.assertRaisesRegex(ppt.TemplateInputError, r"pillars.0.title.*exceeds 4"):
            ppt.validate_document(doc, self.catalog, self.root)

    def test_new_strategy_variants_fit_chinese_limits_and_reject_measured_overflow(self):
        for count in (2, 4, 5, 6):
            doc = self.document("strategy", f"house-{count}")
            limits = self.catalog["families"]["strategy"]["variants"][f"house-{count}"]["item_text_limits"]
            doc["pages"][0]["content"]["pillars"] = [{"title": "中" * limits["title"], "body": "中" * limits["body"]} for _ in range(count)]
            page = ppt.validate_document(doc, self.catalog, self.root)["pages"][0]
            _, bindings, _ = ppt.render_page(page, self.catalog, self.tokens, self.root)
            self.assertTrue(all(item["measured_height"] <= item["frame"][3] for item in bindings))
        doc = self.document("strategy", "house-6")
        doc["pages"][0]["content"]["pillars"][0]["title"] = "标题字段"
        page = ppt.validate_document(doc, self.catalog, self.root)["pages"][0]
        tokens = copy.deepcopy(self.tokens)
        tokens["font"]["sizes"]["heading"] = 48
        with self.assertRaisesRegex(ppt.TemplateInputError, "measured"):
            ppt.render_page(page, self.catalog, tokens, self.root)


if __name__ == "__main__":
    unittest.main()
