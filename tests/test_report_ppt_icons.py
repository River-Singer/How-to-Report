"""Exercise every declared user-icon input through the real template renderer."""
from __future__ import annotations

import copy
from pathlib import Path
import sys
import tempfile
import unittest
from xml.etree import ElementTree as ET
from zipfile import ZipFile

PROJECT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(PROJECT / "skill-src/how-to-report/scripts"), str(PROJECT / "skill-src/shared/scripts")]
import report_ppt as ppt
import ppt_runtime as runtime


class UserIconTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root, cls.catalog, cls.tokens = ppt.load_template()

    def declared_variants(self):
        for name, family in self.catalog["families"].items():
            array = family.get("array_key")
            if array and "icon_key" in family["content_schema"]["properties"][array].get("items", {}).get("properties", {}):
                for variant in family["variants"]:
                    yield name, variant, array

    def page(self, family, variant, identifier="icons", show=True):
        spec = self.catalog["families"][family]
        content = copy.deepcopy(spec["prototype_content"])
        content.update(copy.deepcopy(spec["variants"][variant].get("prototype_content", {})))
        content[spec["array_key"]] = content[spec["array_key"]][:spec["variants"][variant]["capacity"]]
        for item in content[spec["array_key"]]:
            item["icon_key"] = "team"
        if family == "hierarchy":
            content["root"]["icon_key"] = "team"
            for branch in content["branches"]:
                for child in branch.get("children", []):
                    child["icon_key"] = "team"
        return {"id": identifier, "family": family, "variant": variant, "content": content, "config": {"show_icons": show}}

    def render(self, page):
        document = {"schema_version": 1, "template_id": "business-blue-v1", "pages": [page]}
        normalized = ppt.validate_document(document, self.catalog, self.root)["pages"][0]
        svg, bindings, _ = ppt.render_page(normalized, self.catalog, self.tokens, self.root)
        return ET.fromstring(svg), bindings

    def test_all_declared_variants_render_icons_in_reserved_regions_with_stable_layout(self):
        variants = list(self.declared_variants())
        self.assertEqual(len(variants), 21)
        self.assertTrue({("hub", "radial", "nodes"), ("process", "cycle", "steps"),
                         ("hierarchy", "tree", "branches")}.issubset(variants))
        for family, variant, array in variants:
            with self.subTest(family=family, variant=variant):
                page = self.page(family, variant)
                visible, bindings = self.render(page)
                icons = visible.findall(".//*[@data-htr-icon-key]")
                expected_icons = len(page["content"][array])
                if family == "hierarchy":
                    expected_icons += 1 + sum(len(branch.get("children", []))
                                              for branch in page["content"][array])
                self.assertEqual(len(icons), expected_icons)
                bx, by, bw, bh = self.tokens["body"]["frame"]
                for icon in icons:
                    self.assertEqual(icon.get("data-htr-icon-key"), "team")
                    self.assertTrue(icon.findall(".//{*}path"))
                    self.assertRegex(icon.get("transform"), r"scale\([^ )]+\)")
                    x, y, w, h = map(float, icon.get("data-htr-icon-frame").split())
                    self.assertGreater(min(w, h), 0)
                    self.assertGreaterEqual(x, bx)
                    self.assertGreaterEqual(y, by)
                    self.assertLessEqual(x + w, bx + bw)
                    self.assertLessEqual(y + h, by + bh)
                    for binding in bindings:
                        tx, ty, tw, th = binding["frame"]
                        self.assertFalse(min(x + w, tx + tw) - max(x, tx) > .01 and min(y + h, ty + th) - max(y, ty) > .01, (family, variant, binding["field"]))
                page["config"]["show_icons"] = False
                hidden, hidden_bindings = self.render(page)
                self.assertFalse(hidden.findall(".//*[@data-htr-icon-key]"))
                self.assertEqual(bindings, hidden_bindings)
                fixed = lambda xml: [ET.tostring(node) for node in xml if node.get("data-pptx-layer")]
                self.assertEqual(fixed(visible), fixed(hidden))

    def test_unknown_icon_is_rejected_even_when_hidden_for_every_declared_variant(self):
        for family, variant, array in self.declared_variants():
            page = self.page(family, variant, show=False)
            page["content"][array][0]["icon_key"] = "missing-user-icon"
            with self.subTest(family=family, variant=variant):
                with self.assertRaisesRegex(ppt.TemplateInputError, "icon_key.*unknown user icon_key"):
                    self.render(page)

    def test_visible_and_hidden_icons_export_through_same_native_layout(self):
        representatives = [("parallel", "columns-3"), ("process", "cycle-4"), ("image", "gallery-3"), ("strategy", "house-6"), ("architecture", "layers-4"), ("hub", "ring-5")]
        pages = []
        for family, variant in representatives:
            pages.extend([self.page(family, variant, family + "-on"), self.page(family, variant, family + "-off", False)])
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary) / "project"
            ppt.build_project({"schema_version": 1, "template_id": "business-blue-v1", "pages": pages}, project)
            runtime.check_project(project, self.tokens)
            output = Path(temporary) / "icons.pptx"
            inspected = runtime.export_project(project, output, self.tokens)
            self.assertEqual(inspected["counts"], {"slides": 12, "masters": 1, "layouts": 6})
            with ZipFile(output) as package:
                for index in range(1, 13, 2):
                    visible = ET.fromstring(package.read(f"ppt/slides/slide{index}.xml"))
                    hidden = ET.fromstring(package.read(f"ppt/slides/slide{index + 1}.xml"))
                    # Native icon paths become editable DrawingML freeform shapes.
                    self.assertGreater(len(visible.findall(".//a:custGeom", runtime.NS)), len(hidden.findall(".//a:custGeom", runtime.NS)))


if __name__ == "__main__":
    unittest.main()
