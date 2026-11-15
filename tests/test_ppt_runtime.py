"""Regression checks for the self-contained PPT technology component."""
from __future__ import annotations

import importlib.util
import hashlib
import html
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

PROJECT = Path(__file__).resolve().parents[1]
OWN = PROJECT / "skill-src" / "how-to-report"
SHARED = PROJECT / "skill-src" / "shared"
sys.path.insert(0, str(SHARED / "scripts"))
SPEC = importlib.util.spec_from_file_location("htr_ppt_runtime_tests", OWN / "scripts" / "ppt_runtime.py")
runtime = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runtime)

SVG = '''<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="720"
viewBox="0 0 1280 720" data-pptx-master="user-white"
data-pptx-master-name="User White" data-pptx-layout="technical"
data-pptx-layout-name="Technical"><rect id="canvas" data-pptx-layer="master"
width="1280" height="720" fill="#FFFFFF"/><text id="title" x="48" y="60"
font-size="36" font-family="Arial" fill="#000000">Technical geometry check</text></svg>'''


def tokens():
    colors = ["000000", "FFFFFF", "383535", "EFEFEF", "003591", "5385C5",
              "80AACD", "BBCDE5", "003591", "5385C5", "003591", "5385C5"]
    return {"theme": {"slots": dict(zip(runtime.THEME_SLOTS, colors))},
            "font": {"families": {"title": "Arial", "body": "Arial", "latin": "Arial"},
                     "sizes": {"title": 36, "body": 24}},
            "canvas": {"width": 1280, "height": 720}}


@unittest.skipUnless(importlib.util.find_spec("pptx"), "PPT runtime dependency python-pptx unavailable")
class PptRuntimeTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="htr-ppt-test-")
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.project = self.base / "report"
        (self.project / "svg_output").mkdir(parents=True)
        self.slide = self.project / "svg_output" / "01.svg"
        self.slide.write_text(SVG, encoding="utf-8")
        self.tokens = tokens()

    def test_check_and_native_export_roundtrip(self):
        report = runtime.check_project(self.project, self.tokens)
        self.assertEqual(report["status"], "pass")
        output = self.project / "exports" / "result.pptx"
        inspection = runtime.export_project(self.project, output, self.tokens)
        self.assertEqual(inspection["status"], "pass")
        self.assertEqual(inspection["counts"], {"slides": 1, "masters": 1, "layouts": 1})
        self.assertEqual(len(inspection["themes"]), 1)
        shape = next(s for s in inspection["slides"][0]["shapes"] if s["text"])
        self.assertIn("Technical geometry check", shape["text"])
        self.assertIsNotNone(shape["geometry_px"])
        self.assertEqual(shape["font_sizes_pt"], [27.0])

    def test_changed_sources_invalidate_passed_check(self):
        runtime.check_project(self.project, self.tokens)
        self.slide.write_text(SVG.replace("geometry", "measurement"), encoding="utf-8")
        with self.assertRaisesRegex(runtime.PptRuntimeError, "differ"):
            runtime.export_project(self.project, self.base / "out.pptx", self.tokens)
        self.assertFalse((self.base / "out.pptx").exists())

    def test_runtime_identity_invalidates_passed_check(self):
        runtime.check_project(self.project, self.tokens)
        with patch.object(runtime, "_runtime_fingerprint", return_value="changed-runtime"):
            with self.assertRaisesRegex(runtime.PptRuntimeError, "runtime differ"):
                runtime.export_project(self.project, self.base / "out.pptx", self.tokens)

    def test_export_uses_checked_snapshot_when_live_source_changes_and_returns(self):
        from PIL import Image
        image = self.project / "images" / "input.png"
        image.parent.mkdir()
        Image.new("RGB", (10, 10), "white").save(image)
        original_image = image.read_bytes()
        original_svg = SVG.replace("</svg>", '<image x="48" y="150" width="100" height="100" href="../images/input.png"/></svg>')
        self.slide.write_text(original_svg, encoding="utf-8")
        runtime.check_project(self.project, self.tokens)
        original_modules = runtime._engine_modules()
        actual_builder = original_modules[1]

        def transient_change(*args, **kwargs):
            self.slide.write_text(original_svg.replace("geometry", "different"), encoding="utf-8")
            Image.new("RGB", (10, 10), "black").save(image)
            try:
                return actual_builder(*args, **kwargs)
            finally:
                self.slide.write_text(original_svg, encoding="utf-8")
                image.write_bytes(original_image)

        modules = (original_modules[0], transient_change, *original_modules[2:])
        with patch.object(runtime, "_engine_modules", return_value=modules):
            result = runtime.export_project(self.project, self.base / "snapshot.pptx", self.tokens)
        text = "".join(text for slide in result["slides"] for shape in slide["shapes"] for text in shape["text"])
        self.assertIn("Technical geometry check", text)
        self.assertNotIn("different", text)
        self.assertIn(hashlib.sha256(original_image).hexdigest(), [item["sha256"] for item in result["media"]])
        self.assertEqual(result["checked_inputs"]["sources"]["images/input.png"], hashlib.sha256(original_image).hexdigest())

    def test_changed_token_values_invalidate_passed_check(self):
        runtime.check_project(self.project, self.tokens)
        self.tokens["theme"]["slots"]["accent1"] = "5385C5"
        with self.assertRaisesRegex(runtime.PptRuntimeError, "differ"):
            runtime.export_project(self.project, self.base / "out.pptx", self.tokens)

    def test_explicit_notes_are_bound_to_the_check(self):
        runtime.check_project(self.project, self.tokens)
        with self.assertRaisesRegex(runtime.PptRuntimeError, "differ"):
            runtime.export_project(self.project, self.base / "out.pptx", self.tokens,
                                   notes={"01": "Changed narration"})
        notes = {"01": "Checked narration"}
        runtime.check_project(self.project, self.tokens, notes=notes)
        result = runtime.export_project(self.project, self.base / "notes.pptx", self.tokens,
                                        notes=notes)
        self.assertEqual(result["status"], "pass")

    def test_referenced_resource_in_an_output_directory_is_fingerprinted(self):
        from PIL import Image
        resources = self.project / "exports"
        resources.mkdir()
        asset = resources / "source.png"
        Image.new("RGB", (100, 100), "white").save(asset)
        image = '<image x="48" y="150" width="100" height="100" href="../exports/source.png"/>'
        self.slide.write_text(SVG.replace("</svg>", image + "</svg>"), encoding="utf-8")
        report = runtime.check_project(self.project, self.tokens)
        self.assertIn("exports/source.png", report["sources"])
        Image.new("RGB", (100, 100), "black").save(asset)
        with self.assertRaisesRegex(runtime.PptRuntimeError, "differ"):
            runtime.export_project(self.project, self.base / "changed-asset.pptx", self.tokens)

    def test_export_inside_project_ignores_its_own_staging_files(self):
        runtime.check_project(self.project, self.tokens)
        output = self.project / "result.pptx"
        result = runtime.export_project(self.project, output, self.tokens)
        self.assertEqual(result["status"], "pass")
        self.assertTrue(output.is_file())

    def test_receipt_failure_preserves_prior_receipt_and_rolls_back_output(self):
        runtime.check_project(self.project, self.tokens)
        receipt = self.project / "validation" / "ppt-export.json"
        receipt.write_text('{"prior":"valid"}', encoding="utf-8")
        output = self.base / "out.pptx"
        original = os.replace

        def fail_receipt(source, target):
            if Path(target).name == receipt.name:
                raise OSError("receipt publication failed")
            return original(source, target)

        with patch.object(runtime.os, "replace", side_effect=fail_receipt):
            with self.assertRaisesRegex(OSError, "receipt publication failed"):
                runtime.export_project(self.project, output, self.tokens)
        self.assertFalse(output.exists())
        self.assertEqual(json.loads(receipt.read_text(encoding="utf-8")), {"prior": "valid"})

    def test_concurrent_publication_preserves_the_existing_output(self):
        runtime.check_project(self.project, self.tokens)
        output = self.base / "out.pptx"
        publish = runtime._publish_candidate

        def competing_publication(candidate, target):
            target.write_bytes(b"existing export")
            return publish(candidate, target)

        with patch.object(runtime, "_publish_candidate", side_effect=competing_publication):
            with self.assertRaises(FileExistsError):
                runtime.export_project(self.project, output, self.tokens)
        self.assertEqual(output.read_bytes(), b"existing export")

    def test_empty_optional_placeholder_is_a_genuine_empty_native_text_frame(self):
        from xml.etree import ElementTree as ET
        carrier = ('<g id="optional" data-pptx-placeholder="body" data-pptx-idx="7" '
                   'data-pptx-bounds="48 672 500 24"><text id="optional-text" '
                   'data-pptx-carrier="true" x="48" y="692" font-size="16" '
                   'font-family="Arial"><tspan x="48" y="692"/></text></g>')
        ordinary_empty = '<text id="ordinary-empty" x="48" y="200" font-size="24"/>'
        tree = ET.fromstring(SVG.replace("</svg>", carrier + ordinary_empty + "</svg>"))
        ET.indent(tree)
        self.slide.write_text(ET.tostring(tree, encoding="unicode"), encoding="utf-8")
        runtime.check_project(self.project, self.tokens)
        output = self.base / "empty.pptx"
        result = runtime.export_project(self.project, output, self.tokens)
        from zipfile import ZipFile
        with ZipFile(output) as package:
            slide = ET.fromstring(package.read("ppt/slides/slide1.xml"))
        placeholder = next(shape for shape in slide.findall("p:cSld/p:spTree/p:sp", runtime.NS)
                           if shape.find("p:nvSpPr/p:nvPr/p:ph", runtime.NS) is not None)
        self.assertEqual("".join(placeholder.itertext()).strip(), "")
        frame = placeholder.find("p:spPr/a:xfrm", runtime.NS)
        self.assertEqual(frame.find("a:off", runtime.NS).attrib, {"x": str(48 * 9525), "y": str(672 * 9525)})
        self.assertEqual(frame.find("a:ext", runtime.NS).attrib, {"cx": str(500 * 9525), "cy": str(24 * 9525)})
        self.assertFalse(any(shape["name"] == "ordinary-empty" for shape in result["slides"][0]["shapes"]))

    def test_wrapped_placeholder_rows_remain_one_native_text_frame(self):
        from xml.etree import ElementTree as ET
        from zipfile import ZipFile
        carrier = ('<g id="wrapped" data-pptx-placeholder="body" data-pptx-idx="7" '
                   'data-pptx-bounds="450.56 144 757.44 112"><text id="wrapped-text" '
                   'data-pptx-carrier="true" x="450.56" y="165.12" font-size="24" '
                   'font-family="Arial" font-weight="400">'
                   '<tspan x="450.56" y="165.12">First wrapped row</tspan>'
                   '<tspan x="450.56" y="197.52">Second wrapped row</tspan></text></g>')
        ordinary = ('<text id="ordinary-rows" x="48" y="350" font-size="24">'
                    '<tspan x="48" y="350">First ordinary row</tspan>'
                    '<tspan x="48" y="382.4">Second ordinary row</tspan></text>')
        self.slide.write_text(SVG.replace("</svg>", carrier + ordinary + "</svg>"), encoding="utf-8")
        runtime.check_project(self.project, self.tokens)
        output = self.base / "wrapped.pptx"
        result = runtime.export_project(self.project, output, self.tokens)
        with ZipFile(output) as package:
            slide = ET.fromstring(package.read("ppt/slides/slide1.xml"))
        placeholders = [shape for shape in slide.findall("p:cSld/p:spTree/p:sp", runtime.NS)
                        if shape.find("p:nvSpPr/p:nvPr/p:ph", runtime.NS) is not None]
        self.assertEqual(len(placeholders), 1)
        shape = placeholders[0]
        self.assertEqual(shape.find("p:nvSpPr/p:nvPr/p:ph", runtime.NS).get("idx"), "7")
        self.assertEqual([node.text for node in shape.findall(".//a:t", runtime.NS)],
                         ["First wrapped row", "Second wrapped row"])
        self.assertEqual(len(shape.findall(".//a:br", runtime.NS)), 1)
        self.assertEqual(shape.find(".//a:lnSpc/a:spcPts", runtime.NS).get("val"), "2430")
        self.assertEqual({node.get("sz") for node in shape.findall(".//a:r/a:rPr", runtime.NS)}, {"1800"})
        frame = shape.find("p:spPr/a:xfrm", runtime.NS)
        self.assertEqual(frame.find("a:off", runtime.NS).attrib,
                         {"x": str(round(450.56 * 9525)), "y": str(144 * 9525)})
        self.assertEqual(frame.find("a:ext", runtime.NS).attrib,
                         {"cx": str(round(757.44 * 9525)), "cy": str(112 * 9525)})
        self.assertEqual(shape.find("p:txBody/a:bodyPr", runtime.NS).get("wrap"), "none")
        self.assertEqual(len([item for item in result["slides"][0]["shapes"]
                              if (item["name"] or "").startswith("ordinary-rows")]), 2)

    def test_placeholder_explicit_breaks_preserve_blank_rows_and_run_styling(self):
        from xml.etree import ElementTree as ET
        from zipfile import ZipFile
        carrier = ('<g id="explicit" data-pptx-placeholder="body" data-pptx-idx="7" '
                   'data-pptx-bounds="48 144 800 160"><text id="explicit-text" '
                   'data-pptx-carrier="true" x="48" y="165.12" font-size="24" '
                   'font-family="Arial" font-weight="400">'
                   '<tspan x="48" y="165.12">First <tspan font-weight="700">line</tspan></tspan>'
                   '<tspan x="48" y="197.52"/>'
                   '<tspan x="48" y="229.92">Third line</tspan></text></g>')
        self.slide.write_text(SVG.replace("</svg>", carrier + "</svg>"), encoding="utf-8")
        runtime.check_project(self.project, self.tokens)
        output = self.base / "explicit.pptx"
        runtime.export_project(self.project, output, self.tokens)
        with ZipFile(output) as package:
            slide = ET.fromstring(package.read("ppt/slides/slide1.xml"))
        shape = next(shape for shape in slide.findall("p:cSld/p:spTree/p:sp", runtime.NS)
                     if shape.find("p:nvSpPr/p:nvPr/p:ph", runtime.NS) is not None)
        self.assertEqual([node.text for node in shape.findall(".//a:t", runtime.NS)],
                         ["First ", "line", "Third line"])
        self.assertEqual(len(shape.findall(".//a:br", runtime.NS)), 2)
        bold = next(run for run in shape.findall(".//a:r", runtime.NS)
                    if run.find("a:t", runtime.NS).text == "line")
        self.assertEqual(bold.find("a:rPr", runtime.NS).get("b"), "1")
        self.assertEqual(shape.find(".//a:lnSpc/a:spcPts", runtime.NS).get("val"), "2430")

    def test_rotated_placeholder_uses_local_bounds_and_preserves_native_frame(self):
        from xml.etree import ElementTree as ET
        from zipfile import ZipFile
        carriers = []
        for index, angle in enumerate((0, 45, -45, 90)):
            x = 120 + index * 260
            carriers.append(
                f'<g id="rotated-{index}" data-pptx-placeholder="body" data-pptx-idx="{index}" '
                f'data-pptx-bounds="{x} 260 180 80"><text id="rotation-{index}" data-pptx-carrier="true" '
                f'x="{x}" y="277.6" font-size="20" font-family="Arial" '
                f'transform="rotate({angle} {x + 90} 300)">'
                f'<tspan x="{x}" y="277.6">First row</tspan>'
                f'<tspan x="{x}" y="303.6">Second row</tspan></text></g>'
            )
        self.slide.write_text(SVG.replace("</svg>", "".join(carriers) + "</svg>"), encoding="utf-8")
        runtime.check_project(self.project, self.tokens)
        output = self.base / "rotated.pptx"
        runtime.export_project(self.project, output, self.tokens)
        with ZipFile(output) as package:
            root = ET.fromstring(package.read("ppt/slides/slide1.xml"))
            layout_shapes = []
            for name in package.namelist():
                if name.startswith("ppt/slideLayouts/slideLayout") and name.endswith(".xml"):
                    layout = ET.fromstring(package.read(name))
                    layout_shapes.extend(shape for shape in layout.findall("p:cSld/p:spTree/p:sp", runtime.NS)
                                         if shape.find("p:nvSpPr/p:nvPr/p:ph", runtime.NS) is not None)
        placeholders = [shape for shape in root.findall("p:cSld/p:spTree/p:sp", runtime.NS)
                        if shape.find("p:nvSpPr/p:nvPr/p:ph", runtime.NS) is not None]
        self.assertEqual(len(placeholders), 4)
        self.assertEqual(len(layout_shapes), 4)
        for index, shape in enumerate(placeholders):
            transform = shape.find("p:spPr/a:xfrm", runtime.NS)
            angle = (0, 45, -45, 90)[index]
            self.assertEqual(int(transform.get("rot", "0")) % 21600000, angle * 60000 % 21600000)
            self.assertEqual(transform.find("a:off", runtime.NS).attrib,
                             {"x": str((120 + index * 260) * 9525), "y": str(260 * 9525)})
            self.assertEqual(transform.find("a:ext", runtime.NS).attrib,
                             {"cx": str(180 * 9525), "cy": str(80 * 9525)})
            self.assertEqual(len(shape.findall(".//a:br", runtime.NS)), 1)
            layout_shape = next(item for item in layout_shapes if item.find("p:nvSpPr/p:nvPr/p:ph", runtime.NS).get("idx") == str(index))
            layout_transform = layout_shape.find("p:spPr/a:xfrm", runtime.NS)
            self.assertEqual(int(layout_transform.get("rot", "0")) % 21600000, angle * 60000 % 21600000)
            self.assertEqual(layout_transform.find("a:off", runtime.NS).attrib, transform.find("a:off", runtime.NS).attrib)
            self.assertEqual(layout_transform.find("a:ext", runtime.NS).attrib, transform.find("a:ext", runtime.NS).attrib)
        for index in (1, 2):
            with self.subTest(angle=(0, 45, -45, 90)[index]):
                invalid = carriers[index].replace("First row", "W" * 16)
                self.slide.write_text(SVG.replace("</svg>", invalid + "</svg>"), encoding="utf-8")
                with self.assertRaisesRegex(runtime.PptRuntimeError, "data-pptx-bounds"):
                    runtime.check_project(self.project, self.tokens)

    def test_placeholder_relative_line_spacing_keeps_paragraph_gap(self):
        from xml.etree import ElementTree as ET
        from zipfile import ZipFile
        carrier = ('<g id="relative" data-pptx-placeholder="body" data-pptx-idx="7" '
                   'data-pptx-bounds="48 144 800 180"><text id="relative-text" '
                   'data-pptx-carrier="true" x="48" y="165.12" font-size="24" '
                   'font-family="Arial">'
                   '<tspan x="48" dy="0">First row</tspan>'
                   '<tspan x="48" dy="32.4">Second row</tspan>'
                   '<tspan x="48" dy="48.6">New paragraph</tspan></text></g>')
        self.slide.write_text(SVG.replace("</svg>", carrier + "</svg>"), encoding="utf-8")
        runtime.check_project(self.project, self.tokens)
        output = self.base / "relative.pptx"
        runtime.export_project(self.project, output, self.tokens)
        with ZipFile(output) as package:
            slide = ET.fromstring(package.read("ppt/slides/slide1.xml"))
        shape = next(shape for shape in slide.findall("p:cSld/p:spTree/p:sp", runtime.NS)
                     if shape.find("p:nvSpPr/p:nvPr/p:ph", runtime.NS) is not None)
        self.assertEqual(len(shape.findall("p:txBody/a:p", runtime.NS)), 2)
        self.assertEqual(shape.find(".//a:spcBef/a:spcPts", runtime.NS).get("val"), "1215")

    def test_near_horizontal_gradient_wraps_full_turn_and_inspection_rejects_invalid_angle(self):
        from xml.etree import ElementTree as ET
        from zipfile import ZipFile
        from svg_to_pptx.drawingml.styles import _shadow_dir_angle
        self.assertEqual(_shadow_dir_angle(1, -1e-16), 0)
        gradient = ('<defs><linearGradient id="near-horizontal" x1="0" y1="0.5000000000000001" x2="1" y2="0.5">'
                    '<stop offset="0" stop-color="#003591"/><stop offset="1" stop-color="#5385C5"/></linearGradient></defs>'
                    '<rect id="gradient-probe" data-pptx-layer="layout" x="96" y="200" width="240" height="80" fill="url(#near-horizontal)"/>')
        self.slide.write_text(SVG.replace('<text id="title"', gradient + '<text id="title"'), encoding="utf-8")
        runtime.check_project(self.project, self.tokens)
        output = self.base / "gradient.pptx"
        runtime.export_project(self.project, output, self.tokens)
        malformed = self.base / "invalid-gradient.pptx"
        changed = False
        with ZipFile(output) as source, ZipFile(malformed, "w") as target:
            for item in source.infolist():
                data = source.read(item.filename)
                if item.filename.endswith(".xml") and b'<a:lin ang="0"' in data:
                    data = data.replace(b'<a:lin ang="0"', b'<a:lin ang="21600000"')
                    changed = True
                target.writestr(item, data)
        self.assertTrue(changed)
        inspection = runtime.inspect_pptx(malformed, self.tokens)
        self.assertEqual(inspection["status"], "fail")
        self.assertTrue(any("ST_PositiveFixedAngle" in error for error in inspection["errors"]))

    def test_native_geometry_and_text_units_match_svg_pixels(self):
        geometry = '<rect id="unit-probe" x="96" y="144" width="192" height="96" fill="#5385C5"/>'
        self.slide.write_text(SVG.replace("</svg>", geometry + "</svg>"), encoding="utf-8")
        runtime.check_project(self.project, self.tokens)
        result = runtime.export_project(self.project, self.base / "units.pptx", self.tokens)
        probe = next(shape for shape in result["slides"][0]["shapes"] if shape["name"] == "unit-probe")
        self.assertEqual(probe["geometry_px"], {"x": 96, "y": 144, "width": 192, "height": 96})
        title = next(shape for shape in result["slides"][0]["shapes"] if shape["text"])
        self.assertEqual(title["font_sizes_pt"], [27])
        self.assertEqual(result["masters"][0]["level1_font_sizes_hpt"], {"title": 2700, "body": 1800})

    def test_inspection_follows_presentation_order(self):
        from zipfile import ZipFile
        from xml.etree import ElementTree as ET
        for index in (2, 3):
            (self.project / "svg_output" / f"0{index}.svg").write_text(SVG, encoding="utf-8")
        runtime.check_project(self.project, self.tokens)
        output = self.base / "ordered.pptx"
        runtime.export_project(self.project, output, self.tokens)
        modified = self.base / "reordered.pptx"
        with ZipFile(output) as source, ZipFile(modified, "w") as target:
            for item in source.infolist():
                content = source.read(item.filename)
                if item.filename == "ppt/presentation.xml":
                    root = ET.fromstring(content)
                    order = root.find("p:sldIdLst", runtime.NS)
                    order[:] = list(reversed(list(order)))
                    content = ET.tostring(root, encoding="utf-8", xml_declaration=True)
                target.writestr(item, content)
        result = runtime.inspect_pptx(modified, self.tokens)
        self.assertEqual([slide["part"] for slide in result["slides"]],
                         ["ppt/slides/slide3.xml", "ppt/slides/slide2.xml", "ppt/slides/slide1.xml"])

    def test_partial_theme_and_nonwhite_canvas_are_rejected(self):
        del self.tokens["theme"]["slots"]["accent6"]
        with self.assertRaisesRegex(runtime.PptRuntimeError, "twelve"):
            runtime.check_project(self.project, self.tokens)
        self.slide.write_text(SVG.replace('fill="#FFFFFF"', 'fill="#003591"'), encoding="utf-8")
        with self.assertRaisesRegex(runtime.PptRuntimeError, "white"):
            runtime.check_project(self.project, tokens())

    def test_measurement_helpers_are_present_and_execute(self):
        runtime._engine_modules()
        from svg_quality import checker
        self.assertIsNotNone(checker._unsafe_exported_font_faces)
        self.assertIsNotNone(checker._estimate_single_line_text_frame_width)
        from text_measure import measure_text
        measured = measure_text("MMMM", size=24, family="Arial")
        self.assertGreater(measured, 0)

    def test_missing_measurement_helper_fails_closed(self):
        runtime._engine_modules()
        from svg_quality import checker
        with patch.object(checker, "_estimate_single_line_text_frame_width", None):
            with self.assertRaisesRegex(runtime.PptRuntimeError, "measurement helpers"):
                runtime.check_project(self.project, self.tokens)

    def test_conflicting_external_engine_module_is_rejected(self):
        runtime._engine_modules()
        import resource_paths
        with patch.object(resource_paths, "__file__", str(self.base / "external-engine.py")):
            with self.assertRaisesRegex(runtime.PptRuntimeError, "conflicting PPT module"):
                runtime.check_project(self.project, self.tokens)

    def test_external_tokens_and_notes_changed_during_export_are_rejected(self):
        original_modules = runtime._engine_modules()
        actual_builder = original_modules[1]
        notes = {"01": "Checked narration"}
        for changed in ("tokens", "notes"):
            with self.subTest(changed=changed):
                token_values = tokens()
                runtime.check_project(self.project, token_values, notes=notes)

                def changing_builder(*args, **kwargs):
                    result = actual_builder(*args, **kwargs)
                    if changed == "tokens":
                        token_values["spacing"] = {"changed": 24}
                    else:
                        notes["01"] = "Changed during export"
                    return result

                modules = (original_modules[0], changing_builder, *original_modules[2:])
                output = self.base / f"changed-{changed}.pptx"
                with patch.object(runtime, "_engine_modules", return_value=modules):
                    with self.assertRaisesRegex(runtime.PptRuntimeError, "changed during export"):
                        runtime.export_project(self.project, output, token_values, notes=notes)
                self.assertFalse(output.exists())

    def test_component_allowlist_has_actual_hashes_and_technical_origins(self):
        root = OWN / "runtime" / "ppt-engine"
        manifest = json.loads((root / "provenance.json").read_text(encoding="utf-8"))
        actual = {p.relative_to(root).as_posix() for p in root.rglob("*")
                  if p.is_file() and p.name != "provenance.json" and "__pycache__" not in p.parts}
        self.assertEqual(actual, {entry["path"] for entry in manifest["files"]})
        for entry in manifest["files"]:
            self.assertEqual(hashlib.sha256((root / entry["path"]).read_bytes()).hexdigest(), entry["sha256"])
            source = entry.get("source_path", "")
            self.assertTrue(not source or source == "LICENSE" or source.startswith(("scripts/", "templates/schemas/")))
        self.assertFalse(any(root.rglob("*.svg")))
        self.assertFalse((root / "templates").exists())

    def test_explicit_chart_and_table_payloads_compile_to_native_objects(self):
        chart = {"name": "technical-chart", "type": "column", "x": 48, "y": 150,
                 "width": 600, "height": 400, "categories": ["A", "B"],
                 "series": [{"name": "Value", "values": [1, 2]}],
                 "style": {"colors": ["#003591"], "font_family": "Arial",
                           "text_color": "#000000", "chart_area_fill": "#FFFFFF",
                           "plot_area_fill": "#FFFFFF", "axis_color": "#383535",
                           "grid_color": "#EFEFEF"}}
        table = {"schema": "ppt-master.semantic-table.v2", "name": "technical-table",
                 "x": 48, "y": 150, "width": 600, "height": 200,
                 "columns": ["A", "B"], "rows": [["1", "2"]],
                 "style": {"font_family": "Arial", "font_size": 24,
                           "header_fill": "#003591", "header_text": "#FFFFFF",
                           "body_fill": "#FFFFFF", "body_text": "#000000"}}
        for index, (kind, payload) in enumerate((("chart", chart), ("table", table)), 1):
            group = (f'<g id="technical-{kind}" data-pptx-replace-with="{kind}" '
                     'data-pptx-native-authority="json" data-pptx-bounds="48 150 600 400">'
                     f'<metadata type="application/json">{html.escape(json.dumps(payload))}</metadata>'
                     '<rect x="48" y="150" width="600" height="400" fill="#FFFFFF"/>'
                     '<rect x="148" y="350" width="80" height="150" fill="#003591"/>'
                     '<rect x="348" y="200" width="80" height="300" fill="#003591"/>'
                     '<text x="148" y="530" font-size="24" font-family="Arial">A</text>'
                     '<text x="348" y="530" font-size="24" font-family="Arial">B</text></g>')
            slide = SVG.replace('data-pptx-layout="technical"', f'data-pptx-layout="{kind}"')
            (self.project / "svg_output" / f"0{index}.svg").write_text(slide.replace("</svg>", group + "</svg>"), encoding="utf-8")
        runtime.check_project(self.project, self.tokens)
        output = self.base / "native-data.pptx"
        result = runtime.export_project(self.project, output, self.tokens)
        self.assertEqual(result["native_objects"], {"charts": 1, "tables": 1})
        from zipfile import ZipFile
        from xml.etree import ElementTree as ET
        chart_ns = {"c": "http://schemas.openxmlformats.org/drawingml/2006/chart"}
        with ZipFile(output) as package:
            chart_part = next(name for name in package.namelist() if name.startswith("ppt/charts/chart") and name.endswith(".xml"))
            actual_chart = ET.fromstring(package.read(chart_part))
            self.assertEqual([node.text for node in actual_chart.findall(".//c:cat/c:strRef/c:strCache/c:pt/c:v", chart_ns)], chart["categories"])
            self.assertEqual([float(node.text) for node in actual_chart.findall(".//c:val/c:numRef/c:numCache/c:pt/c:v", chart_ns)], chart["series"][0]["values"])
            actual_slide = ET.fromstring(package.read("ppt/slides/slide2.xml"))
            table_text = ["".join(cell.itertext()) for cell in actual_slide.findall(".//a:tbl/a:tr/a:tc", runtime.NS)]
            self.assertEqual(table_text, ["A", "B", "1", "2"])

    def test_relocated_component_runs_without_the_upstream_skill(self):
        package = self.base / "relocated-skill"
        shutil.copytree(OWN / "runtime", package / "runtime")
        (package / "scripts").mkdir()
        shutil.copyfile(OWN / "scripts" / "ppt_runtime.py", package / "scripts" / "ppt_runtime.py")
        shutil.copyfile(SHARED / "scripts" / "write_boundary.py", package / "scripts" / "write_boundary.py")
        self.assertFalse((package / "runtime" / "ppt-engine" / "templates").exists())
        self.assertFalse(any((package / "runtime").rglob("*.svg")))
        token_file = self.project / "tokens.json"
        token_file.write_text(json.dumps(self.tokens), encoding="utf-8")
        script = package / "scripts" / "ppt_runtime.py"
        checked = subprocess.run([sys.executable, "-B", str(script), "check", str(self.project),
                                  "--tokens", str(token_file)], cwd=self.base,
                                 capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(checked.returncode, 0, checked.stdout + checked.stderr)
        exported = subprocess.run([sys.executable, "-B", str(script), "export", str(self.project),
                                   "--tokens", str(token_file), "--output", str(self.base / "out.pptx")],
                                  cwd=self.base, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(exported.returncode, 0, exported.stdout + exported.stderr)


if __name__ == "__main__":
    unittest.main()
