"""Native source reconstruction: lossless trees, real edits and rejection gates."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
from xml.etree import ElementTree as ET
from zipfile import ZIP_DEFLATED, ZipFile

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "skill-src/how-to-report/scripts"))
from presentation_native import (A, CT, MC, P, R, REL, NativeRoundtripError,
                                 extract_native_project, inspect_native_project, rebuild_native_project)
import presentation_native as native


def rels(*rows):
    return (f'<Relationships xmlns="{REL}">' + ''.join(
        f'<Relationship Id="{rid}" Type="{R}/{kind}" Target="{target}"/>'
        for rid, kind, target in rows) + '</Relationships>').encode()


def native_fixture(path, extra_shape="", extra_entries=None):
    """Synthetic source, not a business example or quality claim."""
    slide = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sld xmlns:p="{P}" xmlns:a="{A}" xmlns:r="{R}" xmlns:mc="{MC}">
<p:cSld><p:spTree>
<p:nvGrpSpPr><p:cNvPr id="1" name="Root"/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr/>
<p:sp><p:nvSpPr><p:cNvPr id="2" name="Hidden" hidden="1"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
<p:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="100" cy="100"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr></p:sp>
<p:grpSp><p:nvGrpSpPr><p:cNvPr id="3" name="Group"/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>
<p:grpSpPr><a:xfrm rot="0"><a:off x="914400" y="914400"/><a:ext cx="1828800" cy="1828800"/><a:chOff x="0" y="0"/><a:chExt cx="1000" cy="1000"/></a:xfrm></p:grpSpPr>
<p:sp><p:nvSpPr><p:cNvPr id="4" name="Custom ring"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
<p:spPr><a:xfrm><a:off x="10" y="20"/><a:ext cx="400" cy="300"/></a:xfrm>
<a:custGeom><a:avLst><a:gd name="adj" fmla="val 50000"/></a:avLst><a:gdLst><a:gd name="half" fmla="*/ w 1 2"/></a:gdLst><a:ahLst/><a:cxnLst/><a:rect l="0" t="0" r="r" b="b"/>
<a:pathLst><a:path w="100" h="100"><a:moveTo><a:pt x="0" y="0"/></a:moveTo><a:lnTo><a:pt x="100" y="0"/></a:lnTo><a:lnTo><a:pt x="100" y="100"/></a:lnTo><a:lnTo><a:pt x="0" y="100"/></a:lnTo><a:close/>
<a:moveTo><a:pt x="25" y="25"/></a:moveTo><a:lnTo><a:pt x="25" y="75"/></a:lnTo><a:lnTo><a:pt x="75" y="75"/></a:lnTo><a:lnTo><a:pt x="75" y="25"/></a:lnTo><a:close/></a:path></a:pathLst></a:custGeom>
<a:gradFill><a:gsLst><a:gs pos="0"><a:srgbClr val="0000FF"/></a:gs><a:gs pos="100000"><a:srgbClr val="FFFFFF"><a:alpha val="50000"/></a:srgbClr></a:gs></a:gsLst><a:lin ang="5400000" scaled="1"/></a:gradFill>
<a:ln w="12700"><a:solidFill><a:schemeClr val="accent1"/></a:solidFill></a:ln><a:effectLst><a:outerShdw blurRad="100" dist="20" dir="0"><a:srgbClr val="000000"/></a:outerShdw></a:effectLst>
<a:extLst><a:ext uri="synthetic-extension"><x:opaque xmlns:x="urn:test-extension" xmlns="" instruction="not executable"><![CDATA[arbitrary preserved data]]></x:opaque></a:ext></a:extLst></p:spPr>
<p:txBody><a:bodyPr wrap="square"/><a:lstStyle/><a:p><a:pPr><a:lnSpc><a:spcPct val="120000"/></a:lnSpc></a:pPr><a:r><a:rPr sz="1400"/><a:t>Hello</a:t></a:r><a:r><a:rPr b="1"/><a:t> world</a:t></a:r><a:endParaRPr lang="en-US"/></a:p><a:p><a:r><a:t>第二段</a:t></a:r></a:p></p:txBody></p:sp>
<p:sp><p:nvSpPr><p:cNvPr id="5" name="Target"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr><p:spPr><a:xfrm><a:off x="600" y="20"/><a:ext cx="200" cy="300"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr></p:sp>
<p:cxnSp><p:nvCxnSpPr><p:cNvPr id="6" name="Connector"/><p:cNvCxnSpPr><a:stCxn id="4" idx="0"/><a:endCxn id="5" idx="2"/></p:cNvCxnSpPr><p:nvPr/></p:nvCxnSpPr><p:spPr><a:xfrm><a:off x="400" y="100"/><a:ext cx="200" cy="0"/></a:xfrm><a:prstGeom prst="line"><a:avLst/></a:prstGeom></p:spPr></p:cxnSp>
</p:grpSp>{extra_shape}</p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sld>'''.encode()
    entries = {
        "[Content_Types].xml": f'<Types xmlns="{CT}"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Default Extension="fntdata" ContentType="application/x-fontdata"/></Types>'.encode(),
        "_rels/.rels": rels(("rId1", "officeDocument", "ppt/presentation.xml")),
        "ppt/presentation.xml": f'<p:presentation xmlns:p="{P}" xmlns:r="{R}"><p:sldIdLst><p:sldId id="256" r:id="rId1"/></p:sldIdLst><p:sldSz cx="12192000" cy="6858000"/><p:embeddedFontLst><p:embeddedFont><p:font typeface="Synthetic"/><p:regular r:id="rId2"/></p:embeddedFont></p:embeddedFontLst></p:presentation>'.encode(),
        "ppt/_rels/presentation.xml.rels": rels(("rId1", "slide", "slides/slide1.xml"), ("rId2", "font", "fonts/font1.fntdata")),
        "ppt/slides/slide1.xml": slide,
        "ppt/slides/_rels/slide1.xml.rels": rels(("rId1", "slideLayout", "../slideLayouts/slideLayout1.xml")),
        "ppt/slideLayouts/slideLayout1.xml": f'<p:sldLayout xmlns:p="{P}"><p:cSld/></p:sldLayout>'.encode(),
        "ppt/slideLayouts/_rels/slideLayout1.xml.rels": rels(("rId1", "slideMaster", "../slideMasters/slideMaster1.xml")),
        "ppt/slideMasters/slideMaster1.xml": f'<p:sldMaster xmlns:p="{P}" xmlns:a="{A}"><p:cSld><p:bg><p:bgRef idx="1001"><a:schemeClr val="bg1"/></p:bgRef></p:bg></p:cSld></p:sldMaster>'.encode(),
        "ppt/slideMasters/_rels/slideMaster1.xml.rels": rels(("rId1", "theme", "../theme/theme1.xml")),
        "ppt/theme/theme1.xml": f'<a:theme xmlns:a="{A}" name="Synthetic"><a:themeElements/></a:theme>'.encode(),
        "ppt/fonts/font1.fntdata": b"synthetic opaque embedded font data\0\xff",
    }
    entries.update(extra_entries or {})
    with ZipFile(path, "w", compression=ZIP_DEFLATED) as archive:
        for name, data in entries.items():
            archive.writestr(name, data)
    return entries


def xml_semantics(payload):
    root = ET.fromstring(payload)
    def visit(node):
        return (node.tag, sorted(node.attrib.items()), node.text, node.tail, tuple(visit(child) for child in node))
    return visit(root)


class NativeReconstructionTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="htr-native-test-")
        self.root = Path(self.temporary.name)
        self.source = self.root / "source.pptx"
        self.entries = native_fixture(self.source)
        self.project = self.root / "project"

    def tearDown(self):
        self.temporary.cleanup()

    def imported(self):
        return extract_native_project(self.source, self.project, slides=[1])

    def slide_config(self):
        path = self.project / "slides/slide_0001.json"
        return path, json.loads(path.read_text(encoding="utf-8"))

    def save(self, path, data):
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def test_no_source_roundtrip_preserves_all_native_structure_and_assets(self):
        report = self.imported()
        self.source.unlink()
        target = self.root / "restored.pptx"
        result = rebuild_native_project(self.project, target)
        self.assertFalse(result["source_required"])
        self.assertEqual(result["edits"], [])
        self.assertEqual(report["source"]["sha256"], result["source"]["sha256"])
        self.assertEqual(result["coverage"]["render_verification"], "not_run")
        self.assertEqual(result["slides"][0]["object_count"], 5)
        self.assertEqual(result["slides"][0]["hidden_count"], 1)
        self.assertEqual([p["kind"] for p in result["slides"][0]["inheritance"]["chain"]], ["slideLayout", "slideMaster", "theme"])
        with ZipFile(target) as archive:
            self.assertEqual(set(archive.namelist()), set(self.entries))
            for name, expected in self.entries.items():
                if name.endswith((".xml", ".rels")):
                    self.assertEqual(xml_semantics(expected), xml_semantics(archive.read(name)), name)
                else:
                    self.assertEqual(expected, archive.read(name))
            xml = archive.read("ppt/slides/slide1.xml")
            root = ET.fromstring(xml)
            self.assertEqual(len(root.findall(f".//{{{A}}}path/{{{A}}}close")), 2)
            self.assertEqual(len(root.findall(f".//{{{A}}}gradFill")), 1)
            self.assertEqual(len(root.findall(f".//{{{P}}}grpSp")), 1)
            self.assertEqual(root.find(f".//{{{A}}}stCxn").get("id"), "4")
            self.assertIn(b'xmlns=""', xml)
            self.assertIn(b'<![CDATA[arbitrary preserved data]]>', xml)
            self.assertEqual(len(root.findall(f".//{{{P}}}pic")), 0)
        for path in self.project.rglob("*"):
            self.assertNotEqual(path.suffix.lower(), ".pptx")
            self.assertNotEqual(path.suffix.lower(), ".xml")

    def test_editable_transform_text_and_geometry_tree_drive_output(self):
        self.imported()
        path, slide = self.slide_config()
        shape = next(item for item in slide["objects"] if item["id"] == "4")
        shape["transform"]["coordinates"]["off"]["x"] += 12700
        shape["text_runs"][0]["text"] = "Changed title"
        self.save(path, slide)
        xml_path = self.project / "xml/ppt/slides/slide1.xml.json"
        tree = json.loads(xml_path.read_text(encoding="utf-8"))
        geom = native._node(tree, shape["properties"]["custGeom"][0])
        guide = geom["children"][0]["children"][0]
        guide["attrs"]["fmla"] = "val 25000"
        self.save(xml_path, tree)
        target = self.root / "edited.pptx"
        report = rebuild_native_project(self.project, target)
        self.assertEqual([e["kind"] for e in report["edits"]], ["transform", "text"])
        self.assertEqual([e["part"] for e in report["xml_tree_edits"]], ["ppt/slides/slide1.xml"])
        with ZipFile(target) as archive:
            root = ET.fromstring(archive.read("ppt/slides/slide1.xml"))
            shape = next(s for s in root.findall(f".//{{{P}}}sp") if s.find(f".//{{{P}}}cNvPr").get("id") == "4")
            self.assertEqual(shape.find(f".//{{{A}}}off").get("x"), "12710")
            self.assertEqual(shape.find(f".//{{{A}}}t").text, "Changed title")
            self.assertEqual(shape.find(f".//{{{A}}}gd").get("fmla"), "val 25000")

    def test_repeated_alternative_ids_and_ole_representation_are_preserved(self):
        # The v namespace is used only in Requires; serializers must not prune it.
        one = '<p:sp><p:nvSpPr><p:cNvPr id="7" name="Choice"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr><p:spPr/></p:sp>'
        extra = f'<mc:AlternateContent><mc:Choice xmlns:v="urn:schemas-microsoft-com:vml" Requires="v">{one}</mc:Choice><mc:Fallback>{one}</mc:Fallback></mc:AlternateContent>'
        extra += '<p:graphicFrame><p:nvGraphicFramePr><p:cNvPr id="8" name="OLE"/><p:cNvGraphicFramePr/><p:nvPr/></p:nvGraphicFramePr><p:xfrm><a:off x="0" y="0"/><a:ext cx="500" cy="600"/></p:xfrm><a:graphic><a:graphicData><mc:AlternateContent><mc:Choice xmlns:v="urn:schemas-microsoft-com:vml" Requires="v"/><mc:Fallback><p:oleObj><p:pic><p:nvPicPr><p:cNvPr id="8" name="OLE fallback"/><p:cNvPicPr/><p:nvPr/></p:nvPicPr><p:spPr/></p:pic></p:oleObj></mc:Fallback></mc:AlternateContent></a:graphicData></a:graphic></p:graphicFrame>'
        entries = native_fixture(self.source, extra_shape=extra)
        self.imported()
        output = self.root / "branches.pptx"
        rebuild_native_project(self.project, output)
        with ZipFile(output) as archive:
            actual = archive.read("ppt/slides/slide1.xml")
        self.assertIn(b'xmlns:v="urn:schemas-microsoft-com:vml" Requires="v"', actual)
        self.assertEqual(xml_semantics(entries["ppt/slides/slide1.xml"]), xml_semantics(actual))
        _, slide = self.slide_config()
        self.assertEqual(len([s for s in slide["objects"] if s["id"] == "7"]), 2)
        self.assertEqual(len([s for s in slide["objects"] if s["id"] == "8"]), 1)

    def test_existing_outputs_and_skill_boundary_are_preserved(self):
        self.imported()
        before = (self.project / "native-project.json").read_bytes()
        with self.assertRaisesRegex(NativeRoundtripError, "already exists"):
            self.imported()
        self.assertEqual(before, (self.project / "native-project.json").read_bytes())
        target = self.root / "old.pptx"
        target.write_bytes(b"previous output")
        with self.assertRaisesRegex(NativeRoundtripError, "already exists"):
            rebuild_native_project(self.project, target)
        self.assertEqual(target.read_bytes(), b"previous output")
        package = self.root / "installed"
        package.mkdir()
        (package / "SKILL.md").write_text("package")
        with self.assertRaisesRegex(NativeRoundtripError, "outside installed"):
            rebuild_native_project(self.project, package / "bad.pptx")

    def test_nonfinite_boolean_negative_and_duplicate_configuration_rejected(self):
        self.imported()
        path, original = self.slide_config()
        for value in (float("nan"), True, -1):
            with self.subTest(value=value):
                changed = copy.deepcopy(original)
                changed["objects"][0]["transform"]["coordinates"]["ext"]["cx"] = value
                self.save(path, changed)
                target = self.root / "bad.pptx"
                with self.assertRaises(NativeRoundtripError):
                    rebuild_native_project(self.project, target)
                self.assertFalse(target.exists())
        changed = copy.deepcopy(original)
        changed["objects"][1]["id"] = changed["objects"][0]["id"]
        self.save(path, changed)
        with self.assertRaisesRegex(NativeRoundtripError, "identity"):
            inspect_native_project(self.project)
        path.write_text('{"schema":"x", "schema":"y"}', encoding="utf-8")
        with self.assertRaisesRegex(NativeRoundtripError, "duplicate JSON"):
            inspect_native_project(self.project)

    def test_tampered_binary_and_escaping_config_path_rejected(self):
        self.imported()
        asset = next((self.project / "assets").glob("*"))
        asset.write_bytes(b"tampered")
        with self.assertRaisesRegex(NativeRoundtripError, "asset hash"):
            rebuild_native_project(self.project, self.root / "bad.pptx")
        manifest_path = self.project / "native-project.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["parts"][0]["config"] = "../outside.json"
        self.save(manifest_path, manifest)
        with self.assertRaisesRegex(NativeRoundtripError, "unsafe"):
            inspect_native_project(self.project)

    def test_bad_source_relationships_duplicates_entities_and_zip_traversal(self):
        bad_cases = [
            {"ppt/slides/_rels/slide1.xml.rels": rels(("rId1", "slideLayout", "../../../outside.xml"))},
            {"ppt/slides/_rels/slide1.xml.rels": rels(("rId1", "slideLayout", "../missing.xml"))},
            {"ppt/slides/slide1.xml": self.entries["ppt/slides/slide1.xml"].replace(b'id="5"', b'id="4"')},
            {"ppt/slides/slide1.xml": b'<!DOCTYPE x [<!ENTITY e "expansion">]><x>&e;</x>'},
            {"../outside.xml": b"<x/>"},
        ]
        for index, entries in enumerate(bad_cases):
            with self.subTest(index=index):
                source = self.root / f"bad-{index}.pptx"
                native_fixture(source, extra_entries=entries)
                target = self.root / f"bad-project-{index}"
                with self.assertRaises(NativeRoundtripError):
                    extract_native_project(source, target)
                self.assertFalse(target.exists())

    def test_external_relationship_is_preserved_without_following(self):
        raw = self.entries["ppt/slides/_rels/slide1.xml.rels"].replace(
            b"</Relationships>", f'<Relationship Id="external1" Type="{R}/hyperlink" Target="https://example.invalid/test" TargetMode="External"/></Relationships>'.encode())
        native_fixture(self.source, extra_entries={"ppt/slides/_rels/slide1.xml.rels": raw})
        self.imported()
        result = self.root / "external.pptx"
        rebuild_native_project(self.project, result)
        with ZipFile(result) as archive:
            self.assertEqual(xml_semantics(raw), xml_semantics(archive.read("ppt/slides/_rels/slide1.xml.rels")))

    def test_smartart_empty_image_placeholder_is_preserved(self):
        layout = (f'<dgm:layoutDef xmlns:dgm="{native.DGM}" xmlns:r="{R}">'
                  '<dgm:layoutNode name="node"><dgm:shape type="rect" r:blip="">'
                  '<dgm:adjLst/></dgm:shape></dgm:layoutNode></dgm:layoutDef>').encode()
        native_fixture(self.source, extra_entries={"ppt/diagrams/layout1.xml": layout})
        self.imported()
        output = self.root / "smartart.pptx"
        rebuild_native_project(self.project, output)
        with ZipFile(output) as archive:
            self.assertEqual(xml_semantics(layout), xml_semantics(archive.read("ppt/diagrams/layout1.xml")))

    def test_smartart_exception_does_not_allow_dangling_or_other_empty_references(self):
        cases = [
            f'<dgm:shape xmlns:dgm="{native.DGM}" xmlns:r="{R}" r:blip="missing"/>',
            f'<dgm:shape xmlns:dgm="{native.DGM}" xmlns:r="{R}" r:id=""/>',
            f'<a:blip xmlns:a="{A}" xmlns:r="{R}" r:embed=""/>',
            f'<x:shape xmlns:x="urn:synthetic:other" xmlns:r="{R}" r:blip=""/>',
        ]
        for index, xml in enumerate(cases):
            with self.subTest(index=index):
                native_fixture(self.source, extra_entries={"ppt/diagrams/layout1.xml": xml.encode()})
                target = self.root / f"invalid-smartart-{index}"
                with self.assertRaisesRegex(NativeRoundtripError, "unresolved relationship"):
                    extract_native_project(self.source, target)
                self.assertFalse(target.exists())

    def test_failure_during_zip_write_never_publishes_partial_output(self):
        self.imported()
        target = self.root / "failed.pptx"
        with patch.object(native.ZipFile, "writestr", side_effect=OSError("synthetic write failure")):
            with self.assertRaisesRegex(OSError, "synthetic"):
                rebuild_native_project(self.project, target)
        self.assertFalse(target.exists())
        self.assertEqual(list(self.root.glob(".htr-native-build-*")), [])

    def test_source_identity_project_fingerprint_and_generator_are_real(self):
        first = self.imported()
        second = inspect_native_project(self.project)
        self.assertEqual(first["configuration_sha256"], second["configuration_sha256"])
        self.assertEqual(first["source"]["sha256"], hashlib.sha256(self.source.read_bytes()).hexdigest())
        self.assertEqual(second["generator"]["sha256"], hashlib.sha256(Path(native.__file__).read_bytes()).hexdigest())
        _, slide = self.slide_config()
        self.assertEqual(next(o for o in slide["objects"] if o["id"] == "4")["parent_id"], "3")
        group = next(o for o in slide["objects"] if o["id"] == "3")
        self.assertEqual(group["transform"]["coordinates"]["chExt"], {"cx": 1000, "cy": 1000})

    def test_malformed_json_types_fail_with_domain_error(self):
        self.imported()
        path, original = self.slide_config()
        for value in (None, [], True, 12):
            with self.subTest(value=value):
                changed = copy.deepcopy(original)
                changed["objects"][0] = value
                self.save(path, changed)
                with self.assertRaises(NativeRoundtripError):
                    inspect_native_project(self.project)
        self.save(path, original)
        xml_path = self.project / "xml/ppt/slides/slide1.xml.json"
        before = xml_path.read_bytes()
        self.save(xml_path, [])
        with self.assertRaises(NativeRoundtripError):
            inspect_native_project(self.project)
        xml_path.write_bytes(before)
        manifest_path = self.project / "native-project.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["slides"][0] = None
        self.save(manifest_path, manifest)
        with self.assertRaises(NativeRoundtripError):
            inspect_native_project(self.project)

    def test_custom_suffix_xml_content_type_is_tree_not_opaque_binary(self):
        content = self.entries["[Content_Types].xml"].replace(b"</Types>", b'<Default Extension="custom" ContentType="application/vnd.synthetic+xml"/></Types>')
        native_fixture(self.source, extra_entries={"[Content_Types].xml": content,
                                                  "custom/metadata.custom": b'<x xmlns="urn:test"><y value="editable"/></x>'})
        self.imported()
        manifest_path = self.project / "native-project.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        custom = next(part for part in manifest["parts"] if part["name"] == "custom/metadata.custom")
        self.assertEqual(custom["kind"], "xml")
        raw_xml = b'<x xmlns="urn:test"><y value="opaque"/></x>'
        (self.project / "assets/custom.bin").write_bytes(raw_xml)
        custom.update({"kind": "asset", "asset": "assets/custom.bin", "sha256": hashlib.sha256(raw_xml).hexdigest()})
        custom.pop("config")
        self.save(manifest_path, manifest)
        with self.assertRaisesRegex(NativeRoundtripError, "not a binary asset"):
            rebuild_native_project(self.project, self.root / "bad.pptx")

    def test_damaged_zip_crc_is_domain_error_and_leaves_no_output(self):
        # Write stored members so one payload byte can be changed without editing headers.
        with ZipFile(self.source, "w") as archive:
            for name, data in self.entries.items():
                archive.writestr(name, data)
        payload = bytearray(self.source.read_bytes())
        position = payload.index(self.entries["ppt/fonts/font1.fntdata"])
        payload[position] ^= 1
        self.source.write_bytes(payload)
        with self.assertRaisesRegex(NativeRoundtripError, "package parts"):
            self.imported()
        self.assertFalse(self.project.exists())

    def test_readonly_identity_metadata_cannot_masquerade_as_applied_edit(self):
        self.imported()
        path, data = self.slide_config()
        data["objects"][0]["hidden"] = False
        self.save(path, data)
        with self.assertRaisesRegex(NativeRoundtripError, "identity"):
            rebuild_native_project(self.project, self.root / "misleading.pptx")


if __name__ == "__main__":
    unittest.main()
