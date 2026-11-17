"""Full-catalog discovery and explainable variant-level lexical retrieval."""
from __future__ import annotations

import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skill-src" / "how-to-report" / "scripts"
sys.path.insert(0, str(SCRIPTS))
import presentation_assets
import report_engine
from report_ppt import DEFAULT_TEMPLATE, load_template


class PresentationAssetTests(unittest.TestCase):
    def test_inventory_pages_cover_every_variant_once(self):
        identifiers = []
        offset = 0
        identities = set()
        while offset is not None:
            page = presentation_assets.inventory_assets(DEFAULT_TEMPLATE, variants=True,
                                                        offset=offset, limit=17)
            identities.add((page["catalog_revision"], page["catalog_sha256"]))
            identifiers.extend(item["id"] for item in page["items"])
            self.assertEqual(page["total"], 170)
            self.assertEqual(page["counts"], {"families": 21, "variants": 170})
            offset = page["next_offset"]
        self.assertEqual(len(identifiers), 170)
        self.assertEqual(len(set(identifiers)), 170)
        self.assertEqual(len(identities), 1)

    def test_inventory_families_and_filtered_variants_are_bounded(self):
        families = presentation_assets.inventory_assets(DEFAULT_TEMPLATE, limit=100)
        self.assertEqual(families["total"], 21)
        self.assertIsNone(families["next_offset"])
        self.assertEqual(sum(item["variant_count"] for item in families["items"]), 170)
        self.assertTrue(all("variants" not in item for item in families["items"]))
        variants = presentation_assets.inventory_assets(DEFAULT_TEMPLATE, family="source-house",
                                                        variants=True, offset=25, limit=20)
        self.assertEqual(variants["total"], 30)
        self.assertEqual(len(variants["items"]), 5)
        self.assertTrue(all(item["family"] == "source-house" for item in variants["items"]))
        self.assertIsNone(variants["next_offset"])
        beyond = presentation_assets.inventory_assets(DEFAULT_TEMPLATE, variants=True, offset=1000)
        self.assertEqual(beyond["items"], [])
        self.assertIsNone(beyond["next_offset"])

    def test_chinese_variant_labels_and_scenarios_are_discoverable(self):
        examples = {"目标与能力支撑": "source-house/page-02",
                    "运营方法体系": "source-house/page-01",
                    "平台全景架构": "source-architecture/page-01",
                    "需要讲清楚平台全景架构和各层关系": "source-architecture/page-01"}
        for task, expected in examples.items():
            with self.subTest(task=task):
                result = presentation_assets.query_assets(DEFAULT_TEMPLATE, task, variants=True)
                candidate = result["candidates"][0]
                self.assertEqual(candidate["id"], expected)
                self.assertIn("Chinese-bigram", result["match_method"])
                self.assertTrue(candidate["match_evidence"])
                for evidence in candidate["match_evidence"]:
                    self.assertTrue(evidence["terms"])
                    self.assertIn("excerpt_truncated", evidence)

    def test_variant_summary_exposes_capacity_and_adaptation_without_geometry(self):
        result = presentation_assets.query_assets(DEFAULT_TEMPLATE, "目标与能力支撑", variants=True)
        candidate = result["candidates"][0]
        self.assertTrue(candidate["adaptation"]["fixed_source_topology"])
        self.assertEqual(candidate["adaptation"]["geometry_use"], "qualitative-fixed")
        self.assertGreater(candidate["content_limits"]["fixed_text_fields"], 0)
        self.assertTrue(Path(candidate["preview"]).is_file())
        self.assertIn("describe source-house --variant page-02", candidate["detail_command"])
        self.assertNotIn("fields", candidate)
        self.assertNotIn("geometry", candidate)
        strategy = presentation_assets.query_assets(DEFAULT_TEMPLATE, "strategy", variants=True)
        self.assertEqual(strategy["candidates"][0]["adaptation"]["auto_variant_by_items"]["2"], "house-2")

    def test_match_evidence_excerpt_contains_late_hits_and_preserves_source_offsets(self):
        for source, task in (("前文" * 120 + "目标与能力支撑" + "后文" * 120, "目标与能力支撑"),
                             ("ß" * 120 + "Target relationship" + " detail" * 40, "target")):
            with self.subTest(task=task):
                score, count, evidence = presentation_assets._match(
                    {"variant.description": source}, presentation_assets._query_terms(task))
                self.assertGreater(score, 0)
                self.assertGreater(count, 0)
                detail = evidence[0]
                self.assertIn(task.casefold(), detail["text_excerpt"].casefold())
                self.assertLessEqual(len(detail["text_excerpt"]), 180)
                self.assertTrue(detail["excerpt_truncated"])
                start = detail["excerpt_start"]
                self.assertGreater(start, 0)
                self.assertEqual(detail["text_excerpt"], source[start:start + len(detail["text_excerpt"])])

    def test_legacy_family_query_and_empty_queries_remain_available(self):
        result = report_engine.query_assets(DEFAULT_TEMPLATE, "strategy", 3)
        family = result["candidates"][0]
        self.assertEqual(family["id"], "strategy")
        self.assertEqual(family["label"], "战略屋")
        self.assertIn("variants", family)
        self.assertIn("capacity", family["variants"][0])
        self.assertEqual(result["result_level"], "families")
        empty = report_engine.query_assets(DEFAULT_TEMPLATE, "", 3)
        self.assertEqual(empty["total_matches"], 21)
        self.assertEqual(len(empty["candidates"]), 3)
        self.assertEqual(presentation_assets.query_assets(DEFAULT_TEMPLATE, "unlikely_lexical_token_zzzzz")["candidates"], [])

    def test_catalog_changes_are_visible_without_a_second_index(self):
        root, catalog, tokens = load_template()
        original = presentation_assets.inventory_assets(DEFAULT_TEMPLATE, variants=True)
        changed = copy.deepcopy(catalog)
        changed["families"]["strategy"]["variants"]["new-shape"] = {
            "label": "新增协同编组", "description": "dynamic catalog metadata", "capacity": 7}
        with patch.object(presentation_assets, "load_template", return_value=(root, changed, tokens)):
            result = presentation_assets.query_assets(DEFAULT_TEMPLATE, "新增协同编组", variants=True)
            self.assertEqual(result["candidates"][0]["id"], "strategy/new-shape")
            self.assertEqual(result["candidates"][0]["capacity"], 7)
            self.assertEqual(result["counts"]["variants"], 171)
            self.assertNotEqual(result["catalog_sha256"], original["catalog_sha256"])
            page = presentation_assets.inventory_assets(DEFAULT_TEMPLATE, family="strategy", variants=True)
            self.assertIn("strategy/new-shape", [item["id"] for item in page["items"]])

    def test_invalid_family_and_pagination_fail_explicitly(self):
        with self.assertRaisesRegex(ValueError, "unknown template family"):
            presentation_assets.inventory_assets(DEFAULT_TEMPLATE, family="unknown")
        for values in ({"offset": -1}, {"offset": True}, {"limit": 0}, {"limit": 101}, {"limit": False}):
            with self.subTest(values=values), self.assertRaises(ValueError):
                presentation_assets.inventory_assets(DEFAULT_TEMPLATE, **values)
        for limit in (0, 51, -1, False):
            with self.subTest(limit=limit), self.assertRaises(ValueError):
                presentation_assets.query_assets(DEFAULT_TEMPLATE, limit=limit)

    def test_normal_cli_discovery_from_unrelated_cwd(self):
        cli = str(SCRIPTS / "report_engine.py")
        with tempfile.TemporaryDirectory() as folder:
            environment = dict(os.environ, PYTHONIOENCODING="cp936", PYTHONDONTWRITEBYTECODE="1")
            for arguments in (("inventory", "--variants", "--family", "source-house", "--limit", "3"),
                              ("query", "--variants", "--task", "运营方法体系", "--limit", "2"),
                              ("capabilities",)):
                result = subprocess.run([sys.executable, "-B", cli, *arguments], cwd=folder,
                                        env=environment, capture_output=True, text=True, encoding="utf-8")
                self.assertEqual(result.returncode, 0, result.stderr)
                data = json.loads(result.stdout)
                if arguments[0] == "inventory":
                    self.assertEqual(data["total"], 30)
                    self.assertEqual(data["next_offset"], 3)
                elif arguments[0] == "query":
                    self.assertEqual(data["candidates"][0]["id"], "source-house/page-01")
                else:
                    self.assertIn("asset_discovery", data)
                    self.assertIn("--tokens", data["components"]["command"])
            invalid = subprocess.run([sys.executable, "-B", cli, "inventory", "--offset", "-1"],
                                     cwd=folder, capture_output=True, text=True, encoding="utf-8")
            self.assertNotEqual(invalid.returncode, 0)
            self.assertIn("offset", invalid.stderr)

    def test_explicit_template_root_is_used_by_cli(self):
        _, catalog, _ = load_template()
        custom = copy.deepcopy(catalog)
        custom["template_id"] = "synthetic-discovery"
        custom["revision"] = 71
        custom["families"] = {
            "demo": {"label": "测试原型集", "purpose": "合成工程输入", "variants": {
                "custom": {"label": "跨团队责任协同", "description": "内容来自本次传入catalog", "capacity": 7}}}}
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            template = folder / "custom-template"
            (template / "templates").mkdir(parents=True)
            for name in ("tokens.json", "tokens.schema.json"):
                (template / "templates" / name).write_bytes((DEFAULT_TEMPLATE / "templates" / name).read_bytes())
            (template / "templates/page-catalog.json").write_text(
                json.dumps(custom, ensure_ascii=False), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, "-B", str(SCRIPTS / "report_engine.py"), "--template", str(template),
                 "query", "--variants", "--task", "跨团队责任协同"],
                cwd=folder, capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(result.returncode, 0, result.stderr)
            data = json.loads(result.stdout)
            self.assertEqual(data["template_id"], "synthetic-discovery")
            self.assertEqual(data["catalog_revision"], 71)
            self.assertEqual(data["counts"], {"families": 1, "variants": 1})
            self.assertEqual(data["candidates"][0]["id"], "demo/custom")


if __name__ == "__main__":
    unittest.main()
