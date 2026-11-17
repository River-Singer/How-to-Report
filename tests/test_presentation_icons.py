"""User icon inventory and normal author consumption contracts."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import sys
import unittest
from xml.etree import ElementTree as ET

PROJECT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(PROJECT / "skill-src/how-to-report/scripts"), str(PROJECT / "skill-src/shared/scripts")]
from presentation_icons import ICON_ROOT, icon_catalog
import report_ppt as ppt


class IndependentIconTests(unittest.TestCase):
    def test_all_native_source_icons_are_unique_and_aliases_remain_separate(self):
        found, offset = [], 0
        while True:
            result = icon_catalog(offset=offset, limit=100)
            self.assertEqual((result["source_asset_count"], result["legacy_alias_count"]), (847, 24))
            found.extend(result["items"])
            offset += len(result["items"])
            if offset == result["total"]:
                break
        self.assertEqual(len({item["key"] for item in found}), 871)
        source = [item for item in found if item["key"].startswith("ppt-icons-")]
        self.assertEqual(len({(item["source"]["slide"], item["source"]["shape_id"]) for item in source}), 847)
        for item in source:
            root = ET.parse(ICON_ROOT / item["file"]).getroot()
            self.assertTrue(root.findall(".//{*}path"))
            self.assertFalse(root.findall(".//{*}image"))
            self.assertGreater(min(map(float, root.get("viewBox").split()[2:])), 0)
        for item in found:
            if not item["key"].startswith("ppt-icons-"):
                self.assertIn(item["alias_of"], {row["key"] for row in source})

    def test_bounded_query_and_single_description(self):
        result = icon_catalog(query="team", limit=3)
        self.assertTrue(result["items"])
        self.assertTrue(any(item["key"] == "team" for item in result["items"]))
        item = icon_catalog("ppt-icons-p01-shape-76")
        self.assertEqual(item["source"]["shape_id"], "76")
        self.assertTrue(item["asset"].startswith("assets/"))
        self.assertEqual(icon_catalog(name="team")["key"], "team")
        for values in ({"offset": -1}, {"limit": 0}, {"limit": 101}, {"offset": True}, {"query": "x" * 201}):
            with self.assertRaises(ppt.TemplateInputError):
                icon_catalog(**values)
        with self.assertRaises(ppt.TemplateInputError):
            icon_catalog("missing")

    def test_new_source_key_is_accepted_and_colored_by_normal_template(self):
        root, catalog, tokens = ppt.load_template()
        family = catalog["families"]["parallel"]
        content = copy.deepcopy(family["prototype_content"])
        content.update(copy.deepcopy(family["variants"]["columns-3"].get("prototype_content", {})))
        content["items"] = content["items"][:3]
        for item in content["items"]:
            item["icon_key"] = "ppt-icons-p01-shape-76"
        document = {"schema_version": 1, "template_id": "business-blue-v1", "pages": [{"id": "source-icons", "family": "parallel", "variant": "columns-3", "content": content}]}
        normalized = ppt.validate_document(document, catalog, root)["pages"][0]
        svg, _, _ = ppt.render_page(normalized, catalog, tokens, root)
        parsed = ET.fromstring(svg)
        icons = parsed.findall(".//*[@data-htr-icon-key]")
        self.assertEqual(len(icons), 3)
        for icon in icons:
            for path in icon.findall(".//{*}path"):
                self.assertEqual(path.get("fill"), tokens["theme"]["slots"][tokens["color"]["roles"]["primary"]])


if __name__ == "__main__":
    unittest.main()
