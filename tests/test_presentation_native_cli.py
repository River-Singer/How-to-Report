"""Native PPTX reconstruction through the public CLI, from an unrelated cwd."""
from __future__ import annotations

import base64
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from xml.etree import ElementTree as ET
from zipfile import ZipFile


PROJECT = Path(__file__).resolve().parents[1]
CLI = PROJECT / "skill-src/how-to-report/scripts/report_engine.py"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
P = "http://schemas.openxmlformats.org/presentationml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
REL = "http://schemas.openxmlformats.org/package/2006/relationships"
PNG = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+aBZkAAAAASUVORK5CYII=")


def fixture(destination):
    """Small synthetic OPC package; no source templates or Office dependency."""
    parts = {
        "[Content_Types].xml": '''<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
          <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
          <Default Extension="png" ContentType="image/png"/>
          <Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>
          <Override PartName="/ppt/slides/slide1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>
          <Override PartName="/ppt/slides/slide2.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>
        </Types>''',
        "_rels/.rels": f'<Relationships xmlns="{REL}"><Relationship Id="rId1" Type="{R}/officeDocument" Target="ppt/presentation.xml"/></Relationships>',
        "ppt/presentation.xml": f'''<p:presentation xmlns:p="{P}" xmlns:r="{R}">
          <p:sldIdLst><p:sldId id="256" r:id="rId1"/><p:sldId id="257" r:id="rId2"/></p:sldIdLst>
          <p:sldSz cx="12192000" cy="6858000"/><p:notesSz cx="6858000" cy="9144000"/>
        </p:presentation>''',
        "ppt/_rels/presentation.xml.rels": f'''<Relationships xmlns="{REL}">
          <Relationship Id="rId1" Type="{R}/slide" Target="slides/slide1.xml"/>
          <Relationship Id="rId2" Type="{R}/slide" Target="slides/slide2.xml"/>
        </Relationships>''',
        "ppt/slides/_rels/slide2.xml.rels": f'<Relationships xmlns="{REL}"><Relationship Id="rId1" Type="{R}/image" Target="../media/pixel.png"/></Relationships>',
        "ppt/media/pixel.png": PNG,
    }
    for page in (1, 2):
        parts[f"ppt/slides/slide{page}.xml"] = f'''<p:sld xmlns:p="{P}" xmlns:a="{A}" xmlns:r="{R}"><p:cSld><p:spTree>
          <p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr/>
          <p:sp><p:nvSpPr><p:cNvPr id="2" name="Evidence {page}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
            <p:spPr><a:xfrm><a:off x="914400" y="914400"/><a:ext cx="3657600" cy="914400"/></a:xfrm>
              <a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:solidFill><a:srgbClr val="153654"/></a:solidFill>
            </p:spPr><p:txBody><a:bodyPr/><a:lstStyle/><a:p><a:r><a:rPr lang="zh-CN" sz="1400"/>
              <a:t>原生配置 {page}</a:t></a:r></a:p></p:txBody>
          </p:sp></p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sld>'''
    with ZipFile(destination, "w") as package:
        for name, data in parts.items():
            package.writestr(name, data)
    return {name: data.encode("utf-8") if isinstance(data, str) else data for name, data in parts.items()}


def xml_identity(raw):
    def node_identity(node):
        return (node.tag, sorted(node.attrib.items()), node.text or "", node.tail or "",
                tuple(node_identity(child) for child in node))
    return node_identity(ET.fromstring(raw))


class NativeCliTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="native-cli-")
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name)
        self.source = self.base / "source.pptx"
        self.parts = fixture(self.source)
        self.project = self.base / "native-project"

    def run_cli(self, *args):
        return subprocess.run([sys.executable, "-B", str(CLI), *(str(arg) for arg in args)],
                              cwd=self.base, capture_output=True, encoding="utf-8", timeout=45)

    def success(self, *args):
        result = self.run_cli(*args)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def failure(self, *args):
        result = self.run_cli(*args)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        error = json.loads(result.stderr)
        self.assertFalse(error["valid"])
        self.assertTrue(error["error"])
        self.assertNotIn("Traceback", result.stderr)
        return error

    def imported(self):
        return self.success("native-import", "--input", self.source, "--output", self.project, "--slides", "2")

    def test_capabilities_distinguish_source_replay_from_computed_layout(self):
        capabilities = self.success("capabilities")
        native = capabilities["native_roundtrip"]
        self.assertFalse(native["source_required_for_rebuild"])
        self.assertIn("no automatic reflow", native["scope"])
        self.assertEqual(capabilities["geometry_policy"]["default"], "computed")

    def test_focus_keeps_full_package_and_build_needs_no_source(self):
        source_hash = hashlib.sha256(self.source.read_bytes()).hexdigest()
        self.imported()
        manifest_path = self.project / "native-project.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(len(manifest["slides"]), 2)
        self.assertEqual([slide["number"] for slide in manifest["slides"] if slide["focus"]], [2])
        self.assertEqual(manifest["source"]["sha256"], source_hash)
        before = {path.relative_to(self.project): path.read_bytes() for path in self.project.rglob("*") if path.is_file()}
        self.success("native-inspect", "--project", self.project)
        after = {path.relative_to(self.project): path.read_bytes() for path in self.project.rglob("*") if path.is_file()}
        self.assertEqual(before, after)
        self.assertEqual(hashlib.sha256(self.source.read_bytes()).hexdigest(), source_hash)
        self.source.rename(self.base / "source-unavailable.bin")
        output = self.base / "rebuilt.pptx"
        self.success("native-build", "--project", self.project, "--pptx", output)
        with ZipFile(output) as package:
            self.assertEqual(set(package.namelist()), set(self.parts))
            for name, raw in self.parts.items():
                rebuilt = package.read(name)
                if name.endswith((".xml", ".rels")):
                    self.assertEqual(xml_identity(rebuilt), xml_identity(raw), name)
                else:
                    self.assertEqual(rebuilt, raw, name)

    def test_invalid_focus_rejects_before_publishing(self):
        for pages in (("0",), ("3",), ("1", "1")):
            with self.subTest(pages=pages):
                self.failure("native-import", "--input", self.source, "--output", self.project, "--slides", *pages)
                self.assertFalse(self.project.exists())

    def test_semantic_text_and_geometry_changes_reach_native_output(self):
        self.imported()
        manifest = json.loads((self.project / "native-project.json").read_text(encoding="utf-8"))
        slide_path = self.project / manifest["slides"][0]["config"]
        config = json.loads(slide_path.read_text(encoding="utf-8"))
        shape = next(item for item in config["objects"] if item["id"] == "2")
        shape["transform"]["coordinates"]["off"]["x"] += 12700
        shape["text_runs"][0]["text"] = "配置修改已生效"
        slide_path.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
        self.source.rename(self.base / "source-unavailable.bin")
        self.success("native-inspect", "--project", self.project)
        output = self.base / "edited.pptx"
        self.success("native-build", "--project", self.project, "--pptx", output)
        with ZipFile(output) as package:
            root = ET.fromstring(package.read("ppt/slides/slide1.xml"))
            self.assertEqual(root.find(f".//{{{A}}}xfrm/{{{A}}}off").get("x"), "927100")
            self.assertEqual(root.find(f".//{{{A}}}t").text, "配置修改已生效")
            self.assertFalse(root.findall(f".//{{{P}}}pic"))
            self.assertEqual(xml_identity(package.read("ppt/slides/slide2.xml")),
                             xml_identity(self.parts["ppt/slides/slide2.xml"]))

    def test_existing_outputs_remain_unchanged(self):
        self.imported()
        manifest = self.project / "native-project.json"
        original = manifest.read_bytes()
        self.failure("native-import", "--input", self.source, "--output", self.project)
        self.assertEqual(manifest.read_bytes(), original)
        output = self.base / "already.pptx"
        output.write_bytes(b"keep existing result")
        self.failure("native-build", "--project", self.project, "--pptx", output)
        self.assertEqual(output.read_bytes(), b"keep existing result")

    def test_bad_inputs_are_json_failures_without_output(self):
        output = self.base / "invalid.pptx"
        self.failure("native-import", "--input", self.base / "absent.pptx", "--output", self.project)
        self.failure("native-inspect", "--project", self.project)
        self.source.write_bytes(b"not a ZIP package")
        self.failure("native-import", "--input", self.source, "--output", self.project)
        self.assertFalse(self.project.exists())
        self.project.mkdir()
        (self.project / "native-project.json").write_text("{}", encoding="utf-8")
        self.failure("native-build", "--project", self.project, "--pptx", output)
        self.assertFalse(output.exists())

    def test_protected_package_output_is_refused(self):
        self.imported()
        protected = self.base / "installed-skill"
        protected.mkdir()
        (protected / "SKILL.md").write_text("Synthetic installed skill boundary", encoding="utf-8")
        output = protected / "forbidden.pptx"
        self.failure("native-build", "--project", self.project, "--pptx", output)
        self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
