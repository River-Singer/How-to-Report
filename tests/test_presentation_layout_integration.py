"""Persistent layout author trees through normal mutation, publication and native export."""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from xml.etree import ElementTree as ET
from zipfile import ZipFile

PROJECT = Path(__file__).resolve().parents[1]
SCRIPTS = PROJECT / "skill-src/how-to-report/scripts"
sys.path.insert(0, str(PROJECT / "skill-src/shared/scripts"))
sys.path.insert(0, str(SCRIPTS))
import presentation_compiler as compiler
from presentation_document import apply_patch_to_document, validate_document
from presentation_library import profile_identity
from report_ppt import TemplateInputError, fingerprint
import ppt_runtime


def author():
    return {"schema_version": "0.1", "project_id": "layout-integration", "revision": 1,
            "brief": {"design_profile": profile_identity()}, "sources": [],
            "facts": {"copy": {"value": "Short evidence"}},
            "pages": [{"id": "overview", "kind": "layout", "layout_version": "0.1",
                       "layout": {"id": "content", "type": "column", "padding": [50, 40, 50, 40], "gap": 12,
                                  "children": [{"id": "copy", "type": "leaf", "width": 360,
                                                "element": {"type": "text", "text": {"ref": "copy"}}},
                                               {"id": "following", "type": "leaf", "height": 45,
                                                "element": {"type": "shape", "shape": "rect", "fill": "#E7EEF4"}}]}}]}


class LayoutIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="layout-integration-")
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)

    def read(self, path):
        return json.loads(path.read_text(encoding="utf-8"))

    def run_cli(self, *args, script=None):
        return subprocess.run([sys.executable, "-B", str(script or SCRIPTS / "report_engine.py"), *args],
                              cwd=self.base, capture_output=True, encoding="utf-8")

    def solved(self, value, name):
        folder = self.base / name
        receipt = compiler.build_project(value, folder)
        page = receipt["pages"][0]
        return folder, receipt, self.read(folder / page["layout"]["scene_ref"])

    def test_layout_ids_references_relations_and_leaf_identity(self):
        value = author()
        # Fact and leaf IDs share the existing document ID space.
        value["facts"] = {"evidence": value["facts"].pop("copy")}
        value["pages"][0]["layout"]["children"][0]["element"]["text"]["ref"] = "evidence"
        value["relations"] = [{"id": "relation", "type": "supports", "from": "copy", "to": "following"}]
        validate_document(value)
        duplicate = copy.deepcopy(value)
        duplicate["pages"][0]["layout"]["children"][1]["id"] = "copy"
        with self.assertRaisesRegex(ValueError, "duplicate"):
            validate_document(duplicate)
        invalid = copy.deepcopy(value)
        invalid["pages"][0]["layout"]["children"][0]["element"]["text"] = {"ref": "unknown"}
        with self.assertRaisesRegex(ValueError, "unknown fact"):
            validate_document(invalid)

    def valid_author(self):
        value = author()
        value["facts"]["evidence"] = value["facts"].pop("copy")
        value["pages"][0]["layout"]["children"][0]["element"]["text"]["ref"] = "evidence"
        return value

    def test_fact_and_text_patches_reflow_without_changing_source(self):
        value = self.valid_author()
        original = copy.deepcopy(value)
        first, receipt, solved = self.solved(value, "first")
        first_y = solved["scene"]["elements"][1]["frame"][1]
        long_copy = "A longer piece of current evidence needs several lines at the same font size. " * 6
        changed = apply_patch_to_document(value, [{"op": "replace", "path": "/facts/evidence/value", "value": long_copy}], 1, "fact-change")
        second, second_receipt, second_solved = self.solved(changed, "second")
        self.assertGreater(second_solved["scene"]["elements"][1]["frame"][1], first_y)
        self.assertNotEqual(receipt["input_sha256"], second_receipt["input_sha256"])
        self.assertEqual(value, original)
        self.assertEqual(self.read(first / "inputs/presentation.project.json"), original)
        self.assertIn("layout", self.read(second / "inputs/presentation.project.json")["pages"][0])
        patched = apply_patch_to_document(value, [{"op": "replace", "path": "/pages/0/layout/children/0/element/text", "value": long_copy}], 1, "text-change")
        _, _, third = self.solved(patched, "third")
        self.assertEqual(third["scene"]["elements"][1]["frame"], second_solved["scene"]["elements"][1]["frame"])

    def test_reports_scenes_identity_determinism_and_native_text(self):
        value = self.valid_author()
        folder, receipt, solved = self.solved(value, "compiled")
        again, repeated, _ = self.solved(value, "repeated")
        self.assertEqual(receipt, repeated)
        self.assertEqual(receipt["asset_usage"]["layout_pages"], 1)
        self.assertEqual(solved["input_sha256"], fingerprint(value))
        for key in ("presentation_layout.py", "presentation_topology.py"):
            self.assertIn(key, receipt["compiler_files"])
        for item in ("scene", "report"):
            relative = receipt["pages"][0]["layout"][item + "_ref"]
            raw = (folder / relative).read_bytes()
            self.assertEqual(raw, (again / relative).read_bytes())
            self.assertEqual(hashlib.sha256(raw).hexdigest(), receipt["pages"][0]["layout"][item + "_sha256"])
        ppt_runtime.check_project(folder, folder / "tokens.json")
        output = self.base / "editable.pptx"
        ppt_runtime.export_project(folder, output, folder / "tokens.json")
        with ZipFile(output) as package:
            root = ET.fromstring(package.read("ppt/slides/slide1.xml"))
            self.assertIn("Short evidence", "".join(node.text or "" for node in root.findall(".//a:t", ppt_runtime.NS)))
            self.assertTrue(root.findall(".//p:sp", ppt_runtime.NS))
            self.assertFalse(root.findall(".//p:pic", ppt_runtime.NS))

    def test_bottom_anchor_passes_normal_check_and_native_inset_export(self):
        value = self.valid_author()
        value["pages"][0]["layout"]["children"][0]["element"]["style"] = {"vertical_anchor": "bottom"}
        original = copy.deepcopy(value)
        folder, receipt, solved = self.solved(value, "bottom-anchor")
        effective_bottom = solved["scene"]["elements"][0]["style"]["insets"][3]
        self.assertGreater(effective_bottom, 0)
        report = self.read(folder / receipt["pages"][0]["layout"]["report_ref"])["report"]
        copy_report = next(node for node in report["nodes"] if node["id"] == "copy")
        self.assertEqual(copy_report["computed_text_insets"]["effective"][3], effective_bottom)
        self.assertEqual(self.read(folder / "inputs/presentation.project.json"), original)
        ppt_runtime.check_project(folder, folder / "tokens.json")
        output = self.base / "bottom-anchor.pptx"
        ppt_runtime.export_project(folder, output, folder / "tokens.json")
        with ZipFile(output) as package:
            root = ET.fromstring(package.read("ppt/slides/slide1.xml"))
            body = root.find(".//p:sp/p:txBody/a:bodyPr", ppt_runtime.NS)
            self.assertEqual(body.get("anchor"), "b")
            self.assertAlmostEqual(int(body.get("bIns")) / 9525, effective_bottom, places=3)

    def test_topology_layout_leaf_exports_native_shapes_and_endpoints(self):
        value = self.valid_author()
        value["pages"][0]["layout"]["children"] = [{"id": "topology", "type": "leaf", "height": 500,
            "element": {"type": "component", "component": "topology", "layout": "tree",
                        "nodes": [{"id": "a", "label": "Parent"}, {"id": "b", "label": "Child"}],
                        "edges": [{"id": "ab", "from": "a", "to": "b"}]}}]
        folder, receipt, _ = self.solved(value, "topology")
        self.assertEqual(receipt["asset_usage"]["components"], {"topology": 1})
        ppt_runtime.check_project(folder, folder / "tokens.json")
        output = self.base / "topology.pptx"
        ppt_runtime.export_project(folder, output, folder / "tokens.json")
        with ZipFile(output) as package:
            root = ET.fromstring(package.read("ppt/slides/slide1.xml"))
            connector = root.find(".//p:cxnSp", ppt_runtime.NS)
            self.assertIsNotNone(connector)
            self.assertIsNotNone(connector.find(".//a:stCxn", ppt_runtime.NS))
            self.assertIsNotNone(connector.find(".//a:endCxn", ppt_runtime.NS))

    def test_dependency_change_and_layout_error_do_not_publish(self):
        value = self.valid_author()
        changed = dict(compiler._compiler_identity(), **{"presentation_layout.py": "changed"})
        with patch.object(compiler, "_compiler_identity", side_effect=[compiler._compiler_identity(), changed]):
            with self.assertRaisesRegex(TemplateInputError, "dependencies changed"):
                compiler.build_project(value, self.base / "dependency-changed")
        value["pages"][0]["layout"]["children"][0]["height"] = 1
        with self.assertRaises(TemplateInputError) as error:
            compiler.build_project(value, self.base / "overflow")
        self.assertIsInstance(error.exception.diagnostic, dict)
        self.assertFalse((self.base / "dependency-changed").exists())
        self.assertFalse((self.base / "overflow").exists())
        self.assertEqual(list(self.base.glob(".presentation-build-*")), [])

    def test_normal_cli_discovery_patch_rebuild_and_structured_diagnostic(self):
        value = self.valid_author()
        source = self.base / "author.json"
        source.write_text(json.dumps(value), encoding="utf-8")
        for command in (("layouts",), ("layouts", "grid"), ("components", "topology"), ("capabilities",),
                        ("validate", "--input", str(source)), ("facts", "--input", str(source))):
            result = self.run_cli(*command)
            self.assertEqual(result.returncode, 0, result.stderr)
            json.loads(result.stdout)
        operations = self.base / "patch.json"
        operations.write_text(json.dumps([{"op": "replace", "path": "/facts/evidence/value", "value": "Reflowed copy " * 35}]), encoding="utf-8")
        patched = self.base / "author-v2.json"
        result = self.run_cli("patch", "--input", str(source), "--patch", str(operations), "--expected-revision", "1",
                              "--operation-id", "normal-patch", "--output", str(patched))
        self.assertEqual(result.returncode, 0, result.stderr)
        result = self.run_cli("build", "--input", str(patched), "--output", str(self.base / "cli-build"))
        self.assertEqual(result.returncode, 0, result.stderr)
        value["pages"][0]["layout"]["children"][0]["height"] = 1
        source.write_text(json.dumps(value), encoding="utf-8")
        result = self.run_cli("build", "--input", str(source), "--output", str(self.base / "failed-cli"))
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("diagnostic", json.loads(result.stderr))
        self.assertFalse((self.base / "failed-cli").exists())

    def test_materialized_installation_has_no_checkout_dependency(self):
        spec = importlib.util.spec_from_file_location("layout_package_test", PROJECT / "tools/package_skills.py")
        packager = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(packager)
        payload = packager.expected_packages(PROJECT)["how-to-report"]
        package = self.base / "standalone"
        for relative, raw in payload.items():
            target = package / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
        value = self.valid_author()
        source = self.base / "standalone-author.json"
        source.write_text(json.dumps(value), encoding="utf-8")
        environment = dict(os.environ)
        environment.pop("PYTHONPATH", None)
        result = subprocess.run([sys.executable, "-B", str(package / "scripts/report_engine.py"), "build", "--input", str(source),
                                 "--output", str(self.base / "standalone-build"), "--pptx", str(self.base / "standalone.pptx")],
                                cwd=self.base, env=environment, capture_output=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["inspection"]["counts"]["slides"], 1)

    def test_normal_cli_rejects_manual_scene_even_with_computed_metadata(self):
        value = self.valid_author()
        value["pages"] = [{"id": "manual", "kind": "scene", "metadata": {"computed": True},
                           "elements": [{"id": "manual-copy", "type": "text", "frame": [50, 40, 300, 60], "text": "Legacy"}]}]
        source = self.base / "manual.json"
        source.write_text(json.dumps(value), encoding="utf-8")
        result = self.run_cli("build", "--input", str(source), "--output", str(self.base / "manual-failed"))
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertEqual(json.loads(result.stderr)["diagnostic"]["code"], "computed_geometry_required")
        self.assertFalse((self.base / "manual-failed").exists())
        result = self.run_cli("build", "--geometry-policy", "legacy-replay", "--input", str(source),
                              "--output", str(self.base / "manual-replay"))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["geometry_policy"], "legacy-replay")

    def test_saved_recipe_replays_current_facts_and_ignores_cached_geometry(self):
        from presentation_recipes import compose_document
        request = self.read(SCRIPTS.parent / "assets/design-system/examples/three-recipes.json")
        request["pages"] = request["pages"][:1]
        value = compose_document(request)
        first = self.base / "recipe-first"
        first_receipt = compiler.build_project(value, first, geometry_policy="computed")
        self.assertIn("assets/design-system/recipe-request.schema.json", first_receipt["data_dependencies"])
        changed = apply_patch_to_document(value, [{"op": "replace", "path": "/facts/a/value", "value": 12345}], 1, "recipe-fact")
        changed["pages"][0]["elements"][0]["frame"] = [0, 0, 1, 1]
        # The saved constrained request is actually replayed. A manually edited
        # cache cannot control the current computed scene.
        source = self.base / "recipe.json"
        source.write_text(json.dumps(changed), encoding="utf-8")
        second = self.base / "recipe-second"
        result = self.run_cli("build", "--input", str(source), "--output", str(second))
        self.assertEqual(result.returncode, 0, result.stderr)
        second_receipt = self.read(second / "engine-receipt.json")
        def units(folder, receipt):
            scene = self.read(folder / receipt["pages"][0]["layout"]["scene_ref"])["scene"]
            return next(item["frame"] for item in scene["elements"] if item["id"] == "metric-a--unit")
        self.assertGreater(units(second, second_receipt)[0], units(first, first_receipt)[0])
        self.assertEqual(second_receipt["geometry_policy"], "computed")
        changed["pages"][0]["recipe_source"]["slots"]["main"]["frame"] = [1, 2, 3, 4]
        with self.assertRaises(TemplateInputError):
            compiler.build_project(changed, self.base / "recipe-forged", geometry_policy="computed")
        self.assertFalse((self.base / "recipe-forged").exists())

    def test_arch_interior_recursively_expands_and_counts_ordinary_components(self):
        value = self.valid_author()
        value["pages"][0]["layout"]["children"] = [{"id": "arch", "type": "leaf", "height": 500,
            "element": {"type": "component", "component": "topology", "layout": "arch",
                        "nodes": [{"id": "a", "label": "A"}, {"id": "b", "label": "B"}, {"id": "c", "label": "C"}],
                        "interior": {"id": "inside", "type": "column", "children": [
                            {"id": "inside-copy", "type": "leaf", "height": 100,
                             "element": {"type": "component", "component": "paragraph-flow",
                                         "paragraphs": [{"id": "first", "text": "Evidence"}, {"id": "next", "text": "Meaning"}]}}]}}}]
        _, receipt, solved = self.solved(value, "arch-interior")
        self.assertEqual(receipt["asset_usage"]["components"], {"paragraph-flow": 1, "topology": 1})
        def descendants(items):
            for item in items:
                yield item
                yield from descendants(item.get("children", []))
        self.assertNotIn("component", [item["type"] for item in descendants(solved["scene"]["elements"])])
        self.assertIn("interior_report", solved["scene"]["elements"][0]["metadata"]["topology_report"])

    def test_individual_icon_discovery_and_image_asset_normal_build(self):
        from presentation_icons import icon_catalog
        from presentation_library import library
        catalog = icon_catalog(query="ppt-icons-", limit=1)
        self.assertTrue(catalog["items"])
        key = catalog["items"][0]["key"]
        detail = library(identifier="icon." + key)
        self.assertTrue((SCRIPTS.parent / detail["asset_ref"]).is_file())
        self.assertEqual(detail["icon_key"], key)
        for command in (("icons", key), ("library", "icon." + key), ("library", "--kind", "icon", "--limit", "1")):
            result = self.run_cli(*command)
            self.assertEqual(result.returncode, 0, result.stderr)
        value = self.valid_author()
        value["pages"][0]["layout"] = detail["usage"]["layout_leaf"]
        source = self.base / "icon-author.json"
        source.write_text(json.dumps(value), encoding="utf-8")
        output = self.base / "icon.pptx"
        result = self.run_cli("build", "--input", str(source), "--assets", str(SCRIPTS.parent),
                              "--output", str(self.base / "icon-project"), "--pptx", str(output))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(output.is_file())


if __name__ == "__main__":
    unittest.main()
