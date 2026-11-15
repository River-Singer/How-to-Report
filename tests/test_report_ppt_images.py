"""Image focus parameters through the public template and native export path."""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import io
from pathlib import Path
import sys
import tempfile
import unittest
from xml.etree import ElementTree as ET
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skill-src" / "how-to-report" / "scripts"))
sys.path.insert(0, str(ROOT / "skill-src" / "shared" / "scripts"))
import report_ppt as ppt

POSITIONS = [f"x{x}Y{y}" for y in ("Min", "Mid", "Max") for x in ("Min", "Mid", "Max")]


class ReportPptImageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root, cls.catalog, cls.tokens = ppt.load_template()

    def page(self, position="xMidYMid", fit="contain"):
        content = copy.deepcopy(self.catalog["families"]["image"]["prototype_content"])
        content["sections"] = content["sections"][:1]
        content["images"] = [{"path": "wide.png", "alt": "焦点检查"}]
        return {"id": "picture", "family": "image", "variant": "hero-right", "content": content,
                "config": {"image_position": position, "image_fit": fit}}

    def document(self, pages):
        return {"schema_version": 1, "template_id": "business-blue-v1", "pages": pages}

    def test_image_defaults_and_invalid_anchor_and_capacity(self):
        page = self.page()
        page.pop("config")
        result = ppt.validate_document(self.document([page]), self.catalog, self.root)
        self.assertEqual(result["pages"][0]["config"]["image_position"], "xMidYMid")
        with self.assertRaisesRegex(ppt.TemplateInputError, "image_position"):
            ppt.validate_document(self.document([self.page("top-right")]), self.catalog, self.root)
        page = self.page()
        page["content"]["images"] *= 2
        with self.assertRaisesRegex(ppt.TemplateInputError, r"content.images: capacity 1"):
            ppt.validate_document(self.document([page]), self.catalog, self.root)

    @unittest.skipUnless(importlib.util.find_spec("PIL"), "Pillow unavailable")
    def test_all_nine_anchors_reach_svg_and_preserve_local_resource(self):
        from PIL import Image
        with tempfile.TemporaryDirectory() as temporary:
            asset_root = Path(temporary)
            source = asset_root / "wide.png"
            Image.new("RGB", (400, 100), "#003591").save(source)
            expected = source.read_bytes()
            for position in POSITIONS:
                for fit, mode in (("contain", "meet"), ("cover", "slice")):
                    page = ppt.validate_document(self.document([self.page(position, fit)]), self.catalog, self.root)["pages"][0]
                    svg, _, assets = ppt.render_page(page, self.catalog, self.tokens, self.root, asset_root=asset_root)
                    picture = ET.fromstring(svg).find(".//{*}image")
                    self.assertEqual(picture.get("preserveAspectRatio"), f"{position} {mode}")
                    self.assertEqual(list(assets.values()), [expected])
                    self.assertEqual(picture.find("{*}desc").text, "焦点检查")

    @unittest.skipUnless(importlib.util.find_spec("PIL") and importlib.util.find_spec("pptx"), "Native image dependencies unavailable")
    def test_native_crop_anchors_roundtrip_and_keep_full_source_dimensions(self):
        from PIL import Image
        import ppt_runtime as runtime
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            for name, dimensions in (("wide", (400, 100)), ("tall", (100, 400))):
                Image.new("RGB", dimensions, "#5385C5").save(base / f"{name}.png")
            pages, expected = [], []
            for name in ("wide", "tall"):
                for position in POSITIONS:
                    page = self.page(position, "cover")
                    page["id"] = f"{name}-{position}"
                    page["content"]["images"][0]["path"] = f"{name}.png"
                    pages.append(page)
                    expected.append((name, position))
            page = self.page("xMaxYMin", "contain")
            page["id"] = "complete-image"
            pages.append(page)
            project = base / "project"
            ppt.build_project(self.document(pages), project, asset_root=base)
            for source in (base / "wide.png", base / "tall.png"):
                digest = hashlib.sha256(source.read_bytes()).hexdigest()
                self.assertEqual((project / "images" / f"{digest[:16]}.png").read_bytes(), source.read_bytes())
            self.assertEqual(runtime.check_project(project, self.tokens)["status"], "pass")
            output = base / "result.pptx"
            self.assertEqual(runtime.export_project(project, output, self.tokens)["status"], "pass")
            with ZipFile(output) as package:
                # The hero-right image frame is determined by the unchanged template tokens.
                box_ratio = (1184 * .52) / (528 - 66)
                for index, (name, position) in enumerate(expected, 1):
                    slide = ET.fromstring(package.read(f"ppt/slides/slide{index}.xml"))
                    picture = slide.find(".//{*}pic")
                    crop = picture.find(".//{*}srcRect")
                    self.assertIsNotNone(crop)
                    values = {key: int(crop.get(key, "0")) for key in ("l", "t", "r", "b")}
                    horizontal = {"Min": 0, "Mid": .5, "Max": 1}[position[1:4]]
                    vertical = {"Min": 0, "Mid": .5, "Max": 1}[position[5:8]]
                    total = round((1 - box_ratio / 4) * 100000) if name == "wide" else round((1 - .25 / box_ratio) * 100000)
                    first, second, anchor = ("l", "r", horizontal) if name == "wide" else ("t", "b", vertical)
                    self.assertEqual(values[first] + values[second], total)
                    self.assertEqual(values[first], round(total * anchor))
                    other = ("t", "b") if name == "wide" else ("l", "r")
                    self.assertEqual(sum(values[key] for key in other), 0)
                complete = ET.fromstring(package.read("ppt/slides/slide19.xml"))
                picture = complete.find(".//{*}pic")
                self.assertIsNone(picture.find(".//{*}srcRect"))
                extent = picture.find(".//{*}xfrm/{*}ext")
                self.assertAlmostEqual(int(extent.get("cx")) / int(extent.get("cy")), 4, places=4)
                dimensions = set()
                for name in package.namelist():
                    if name.startswith("ppt/media/") and name.endswith(".png"):
                        with Image.open(io.BytesIO(package.read(name))) as embedded:
                            dimensions.add(embedded.size)
                self.assertTrue({(400, 100), (100, 400)}.issubset(dimensions))


if __name__ == "__main__":
    unittest.main()
