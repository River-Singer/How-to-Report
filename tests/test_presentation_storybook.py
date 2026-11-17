"""Portable Storybook contracts, safe publication and actual engine CLI requests."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import subprocess
import shutil
import sys
import tempfile
import unittest
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skill-src/how-to-report/scripts"
sys.path.insert(0, str(SCRIPTS))

from presentation_storybook import build_storybook


def js_data(path):
    text = path.read_text(encoding="utf-8")
    return json.loads(text.split("=", 1)[1].rstrip(";\n"))


class StorybookTests(unittest.TestCase):
    def fixture(self, root):
        image = root / "source.svg"
        image.write_text('<svg xmlns="http://www.w3.org/2000/svg" width="2000" height="1000"><rect width="2000" height="1000" fill="blue"/></svg>', encoding="utf-8")
        catalog = root / "catalog"
        (catalog / "assets/demo").mkdir(parents=True)
        manifest = {"schema": "how-to-report.native-catalog.v1", "sources": [{"id": "demo",
            "source": {"name": "原始模板.pptx", "sha256": "test"},
            "pages": [{"number": 1, "index": "assets/demo/p0001.json"}]}]}
        page_id, atom_id = "native:demo:p0001:page", "native:demo:p0001:o123"
        def asset(identifier, kind, box):
            return {"id": identifier, "name": "<script>untrusted label</script>", "kind": kind,
                    "source_id": "demo", "slide_number": 1, "executable": True, "bbox_emu": box,
                    "parent_id": page_id if kind == "atom" else None, "children": [atom_id] if kind == "page" else [],
                    "preview": {"image": str(image), "crop_emu": list(box), "slide_emu": [2000, 1000]},
                    "capabilities": {"text_slots": []}}
        entries = [asset(page_id, "page", [0, 0, 2000, 1000]), asset(atom_id, "atom", [100, 100, 0, 100])]
        payload = json.dumps({"assets": entries}).encode("utf-8")
        (catalog / "assets/demo/p0001.json").write_bytes(payload)
        manifest["sources"][0]["pages"][0]["sha256"] = hashlib.sha256(payload).hexdigest()
        (catalog / "catalog.json").write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")
        return catalog, entries, image

    def test_native_hierarchy_and_zero_thickness_preview_are_portable(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            catalog, originals, image = self.fixture(root)
            output = root / "site"
            receipt = build_storybook(catalog, output, include_builtin=False)
            self.assertEqual(receipt["asset_count"], 2)
            self.assertEqual(receipt["preview_files"], 1)
            index = js_data(output / "data/index.js")
            self.assertEqual(index["page_size"], 24)
            self.assertEqual(index["items"][0]["source_name"], "原始模板.pptx")
            detail = js_data(output / "data/chunk-0000.js")
            self.assertEqual(detail[1]["parent_id"], detail[0]["id"])
            self.assertEqual(detail[1]["bbox_emu"], originals[1]["bbox_emu"])
            self.assertGreater(detail[1]["preview"]["crop_emu"][2], 0)
            self.assertEqual(detail[1]["preview"]["slide_emu"], [2000, 1000])
            self.assertIn("Zero-thickness", detail[1]["preview"]["viewport_adjustment"])
            image.unlink()
            self.assertTrue((output / detail[1]["preview"]["image"]).is_file())
            self.assertNotIn("<script>untrusted", (output / "index.html").read_text(encoding="utf-8"))
            js = (output / "storybook.js").read_text(encoding="utf-8")
            self.assertNotIn("innerHTML", js)
            self.assertNotIn("fetch(", js)

    def test_details_are_bounded_chunks_and_default_filters_are_honest(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "site"
            records = [{"id": f"planned.{n}", "kind": "chart", "label": str(n), "executable": False, "mode": "planned"} for n in range(257)]
            receipt = build_storybook(None, output, include_builtin=False, extra_records=records)
            self.assertEqual(receipt["detail_chunks"], 2)
            self.assertEqual(len(js_data(output / "data/chunk-0000.js")), 256)
            self.assertEqual(len(js_data(output / "data/chunk-0001.js")), 1)
            self.assertEqual(receipt["executable_count"], 0)
            self.assertIn('id="executable" checked', (output / "index.html").read_text(encoding="utf-8"))

    def test_invalid_catalog_path_and_invalid_crop_publish_nothing(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            catalog, entries, _ = self.fixture(root)
            entries[1]["preview"]["crop_emu"][2] = -1
            payload = json.dumps({"assets": entries}).encode("utf-8")
            (catalog / "assets/demo/p0001.json").write_bytes(payload)
            manifest = json.loads((catalog / "catalog.json").read_text(encoding="utf-8"))
            manifest["sources"][0]["pages"][0]["sha256"] = hashlib.sha256(payload).hexdigest()
            (catalog / "catalog.json").write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "nonnegative"):
                build_storybook(catalog, root / "bad-crop", include_builtin=False)
            self.assertFalse((root / "bad-crop").exists())
            manifest = json.loads((catalog / "catalog.json").read_text(encoding="utf-8"))
            manifest["sources"][0]["pages"][0]["index"] = "../secret.json"
            (catalog / "catalog.json").write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "escapes"):
                build_storybook(catalog, root / "bad-path", include_builtin=False)
            self.assertFalse((root / "bad-path").exists())

    def test_changed_native_index_is_rejected_before_publication(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            catalog, entries, _ = self.fixture(root)
            entries[0]["name"] = "Changed source identity"
            (catalog / "assets/demo/p0001.json").write_text(json.dumps({"assets": entries}), encoding="utf-8")
            output = root / "site"
            with self.assertRaisesRegex(ValueError, "hash mismatch"):
                build_storybook(catalog, output, include_builtin=False)
            self.assertFalse(output.exists())

    def test_duplicate_and_existing_output_are_rejected_without_modifying_inputs(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            output = root / "site"
            record = {"id": "a", "kind": "chart", "executable": False}
            with self.assertRaisesRegex(ValueError, "unique"):
                build_storybook(None, output, include_builtin=False, extra_records=[record, copy.deepcopy(record)])
            self.assertFalse(output.exists())
            output.mkdir()
            marker = output / "keep.txt"
            marker.write_text("keep", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "already exists"):
                build_storybook(None, output, include_builtin=False)
            self.assertEqual(marker.read_text(encoding="utf-8"), "keep")


class StorybookCliTests(unittest.TestCase):
    def command(self, directory, *arguments):
        return subprocess.run([sys.executable, "-B", str(SCRIPTS / "report_engine.py"), *arguments], cwd=directory,
                              capture_output=True, text=True, encoding="utf-8")

    def test_registered_chart_request_compiles_from_unrelated_directory(self):
        from presentation_chart_assets import describe_chart_asset
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            request = root / "request.json"
            example = describe_chart_asset("chart.column")["example"]
            request.write_text(json.dumps(example), encoding="utf-8")
            result = self.command(root, "chart-build", "--request", str(request), "--output", str(root / "project"))
            self.assertEqual(result.returncode, 0, result.stderr)
            receipt = json.loads(result.stdout)
            self.assertEqual(receipt["geometry_policy"], "computed")
            self.assertEqual(receipt["page_count"], 1)
            layout = list((root / "project/layout").glob("*.report.json"))
            self.assertTrue(layout)

    def test_discovery_and_arbitrary_geometry_rejection(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            discovered = self.command(root, "chart-assets", "--limit", "100")
            self.assertEqual(discovered.returncode, 0, discovered.stderr)
            self.assertEqual(json.loads(discovered.stdout)["total"], 68)
            request = root / "request.json"
            request.write_text(json.dumps({"asset_ids": ["a"], "frame": [1, 2, 3, 4]}), encoding="utf-8")
            output = root / "bad.pptx"
            result = self.command(root, "catalog-build", "--catalog", str(root / "missing"), "--request", str(request), "--pptx", str(output))
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("arbitrary geometry", result.stderr)
            self.assertFalse(output.exists())


class BuiltinRequestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from presentation_storybook import _builtin_records
        from report_ppt import DEFAULT_TEMPLATE
        cls.records = list(_builtin_records(DEFAULT_TEMPLATE))

    def test_every_template_request_respects_its_variant_schema_and_capacity(self):
        from report_ppt import load_template, validate_document
        root, catalog, _ = load_template()
        templates = [r for r in self.records if r["kind"] == "template"]
        self.assertEqual(len(templates), 170)
        for record in templates:
            with self.subTest(asset=record["id"]):
                page = copy.deepcopy(record["invocation"]["request"]["pages"][0]["template"])
                page["id"] = "test"
                validate_document({"schema_version": 1, "template_id": catalog["template_id"], "pages": [page]}, catalog, root)
                if record["contract"]["variant"].get("renderer") == "source-diagram":
                    self.assertEqual(record["mode"], "source-parameter")

    def test_icons_and_components_have_computed_requests_without_literal_frames(self):
        records = [r for r in self.records if r["kind"] in {"icon", "component"}]
        self.assertEqual(sum(r["kind"] == "icon" for r in records), 871)
        def visit(value):
            if isinstance(value, dict):
                self.assertNotIn("frame", value)
                for child in value.values():
                    visit(child)
            elif isinstance(value, list):
                for child in value:
                    visit(child)
        for record in records:
            self.assertEqual(record["invocation"]["mode"], "author")
            visit(record["invocation"]["request"])
        self.assertEqual(sum("invocation" in r for r in self.records if r["kind"] == "recipe"), 3)

    def test_individual_icon_request_builds_with_declared_asset_root(self):
        from presentation_compiler import build_project
        record = next(r for r in self.records if r["kind"] == "icon")
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "icon-project"
            receipt = build_project(record["invocation"]["request"], output,
                                    asset_root=record["invocation"]["asset_root"], geometry_policy="computed")
            self.assertEqual(receipt["page_count"], 1)
            self.assertEqual(receipt["geometry_policy"], "computed")

    def test_palette_previews_and_portable_selection_metadata(self):
        from presentation_storybook import _component_previews
        from report_ppt import DEFAULT_TEMPLATE
        palettes = [copy.deepcopy(r) for r in self.records if r["kind"] == "palette"]
        self.assertEqual(len(palettes), 5)
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            _component_previews(palettes, root / "previews", DEFAULT_TEMPLATE)
            colors = []
            for record in palettes:
                request = record["invocation"]["request"]
                self.assertEqual(request["brief"]["palette_id"], record["palette_id"])
                self.assertNotIn('"frame"', json.dumps(request))
                output = root / "previews" / record["id"]
                tokens = json.loads((output / "tokens.json").read_text(encoding="utf-8"))
                receipt = json.loads((output / "engine-receipt.json").read_text(encoding="utf-8"))
                self.assertEqual(receipt["palette_id"], record["palette_id"])
                if record["palette_id"] != "report-default":
                    self.assertEqual(tokens["color"]["palette"]["id"], record["palette_id"])
                svg = Path(record["preview"]["image"]).read_text(encoding="utf-8")
                self.assertIn(record["roles"]["primary"].lower(), svg.lower())
                colors.append(record["roles"]["primary"])
                self.assertTrue(record["contrast"])
                self.assertIsInstance(record["provenance"]["sources"], list)
            self.assertGreater(len(set(colors)), 1)
            build_storybook(None, root / "site", include_builtin=False, extra_records=palettes)
            data = js_data(root / "site/data/index.js")
            self.assertEqual(len(data["palettes"]), 5)
            self.assertEqual({r["palette_id"] for r in data["palettes"]}, {r["palette_id"] for r in palettes})
            self.assertTrue((root / "site/storybook-requests.js").is_file())

    @unittest.skipUnless(shutil.which("node"), "Node is needed to exercise browser request binding")
    def test_browser_request_binding_preserves_data_and_native_colors(self):
        result = subprocess.run(["node", str(ROOT / "tests/storybook_palette_requests.cjs")],
                                capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_text_profile_is_callable_with_real_multi_page_previews(self):
        from presentation_storybook import _component_previews
        from report_ppt import DEFAULT_TEMPLATE
        record = copy.deepcopy(next(r for r in self.records if r["id"] == "profile.report-14pt"))
        self.assertTrue(record["executable"])
        self.assertEqual(record["roles"]["body"]["font_size_pt"], 14)
        self.assertEqual(min(r["font_size_pt"] for r in record["roles"].values()), 9)
        self.assertEqual(record["invocation"]["request"]["brief"]["design_profile"], record["identity"])
        self.assertNotIn('"frame"', json.dumps(record["invocation"]["request"]))
        self.assertEqual(record["rich_text"]["run_fields"], ["text", "weight", "color"])
        self.assertTrue(record["rich_text"]["unsupported"])
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            _component_previews([record], root / "compiled", DEFAULT_TEMPLATE)
            self.assertEqual(len(record["preview_pages"]), 3)
            self.assertEqual([p["title"] for p in record["preview_pages"]], ["文字角色", "段落与富文本", "对齐与内边距"])
            self.assertEqual([p["page_id"] for p in record["preview_pages"]], ["type-roles", "type-paragraphs", "type-alignment"])
            build_storybook(None, root / "site", include_builtin=False, extra_records=[record])
            data = js_data(root / "site/data/index.js")
            self.assertEqual(data["text_profile"]["body_pt"], 14)
            self.assertEqual(data["text_profile"]["minimum_pt"], 9)
            result = js_data(root / "site/data/chunk-0000.js")[0]
            for preview in result["preview_pages"]:
                self.assertFalse(Path(preview["image"]).is_absolute())
                self.assertTrue((root / "site" / preview["image"]).is_file())
                self.assertTrue(preview["title"])

    def test_parameter_and_source_anchor_requests_bind_actual_role_font_sizes(self):
        from presentation_compiler import build_project
        from presentation_text_profile import describe_text_profile
        standard = describe_text_profile()
        with tempfile.TemporaryDirectory() as temp:
            for identifier in ("template.parallel/columns-2", "template.source-circular/page-01"):
                with self.subTest(asset=identifier):
                    record = next(r for r in self.records if r["id"] == identifier)
                    author = record["invocation"]["request"]
                    self.assertEqual(author["brief"]["design_profile"], standard["identity"])
                    output = Path(temp) / record["family"]
                    receipt = build_project(author, output, geometry_policy="computed")
                    svg = ET.parse(output / receipt["pages"][0]["svg"]).getroot()
                    texts = [node for node in svg.iter() if node.get("data-htr-text-role")]
                    self.assertTrue(texts)
                    for node in texts:
                        expected = standard["roles"][node.get("data-htr-text-role")]["font_size_px"]
                        self.assertAlmostEqual(float(node.get("font-size")), expected)
                    if record["mode"] == "source-parameter":
                        fields = record["contract"]["variant"]["fields"]
                        for field in fields.values():
                            node = next(n for n in texts if n.get("data-htr-source-ref") == field["source_ref"])
                            for actual, expected in zip([float(v) for v in node.get("data-pptx-frame").split()], field["frame"]):
                                self.assertAlmostEqual(actual, expected, delta=.001)


if __name__ == "__main__":
    unittest.main()
