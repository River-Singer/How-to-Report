"""Regression coverage for the author-document to native-PPT boundary."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
from xml.etree import ElementTree as ET
from zipfile import ZipFile

PROJECT = Path(__file__).resolve().parents[1]
OWN = PROJECT / "skill-src" / "how-to-report"
sys.path.insert(0, str(PROJECT / "skill-src" / "shared" / "scripts"))
sys.path.insert(0, str(OWN / "scripts"))

from presentation_compiler import build_project
from report_ppt import TemplateInputError
import ppt_runtime


def document():
    return {"schema_version":"0.1", "project_id":"compiler-fixture", "revision":1,
        "brief":{"audience":"Engineering fixture"}, "sources":[],
        "facts":{"a":{"value":12},"b":{"value":5},"gap":{"derived":{"op":"difference","args":["a","b"]}}},
        "pages":[{"id":"overview", "kind":"scene", "job":"Show derived values and native relations", "notes":"Fixture notes",
            "elements":[
                {"id":"node-a","type":"shape","shape":"rect","frame":[80,140,220,100],"fill":"#DFEAF5"},
                {"id":"node-b","type":"shape","shape":"rect","frame":[520,140,220,100],"fill":"#DFEAF5"},
                {"id":"connection","type":"connector","from":"node-a","to":"node-b","arrow":True},
                {"id":"heading","type":"text","frame":[50,30,1100,80],"text":["Gap ",{"ref":"gap","format":"integer"}],"style":{"font_size":32}},
                {"id":"paragraph","type":"text","frame":[80,300,300,150],"text":"First line\n第二行文字", "style":{"font_size":24}},
                {"id":"data","type":"chart","frame":[470,300,700,330],"chart_type":"bar","categories":["A","B"],
                    "series":[{"name":"Count","values":[{"ref":"a"},{"ref":"b"}]}],"axes":{"value":{"visible":False}}}
            ]}]}


class PresentationCompilerTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="presentation-engine-")
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)

    def test_scene_native_objects_and_editable_multiline_text(self):
        target = self.base / "project"
        receipt = build_project(document(), target)
        self.assertEqual(receipt["page_count"],1)
        self.assertTrue((target/"inputs"/"presentation.project.json").is_file())
        self.assertTrue((target/"object-map.json").is_file())
        ppt_runtime.check_project(target,target/"tokens.json")
        output = self.base/"scene.pptx"
        ppt_runtime.export_project(target,output,target/"tokens.json")
        with ZipFile(output) as package:
            ns=ppt_runtime.NS
            root=ET.fromstring(package.read("ppt/slides/slide1.xml"))
            texts=["".join(node.itertext()) for node in root.findall(".//p:sp/p:txBody",ns)]
            self.assertTrue(any("Gap 7" in text for text in texts))
            self.assertEqual(len([text for text in texts if "First line" in text or "第二行文字" in text]),1)
            connectors=root.findall(".//p:cxnSp",ns)
            self.assertEqual(len(connectors),1)
            self.assertIsNotNone(connectors[0].find(".//a:stCxn",ns))
            self.assertIsNotNone(connectors[0].find(".//a:endCxn",ns))
            self.assertEqual(len([n for n in package.namelist() if n.startswith("ppt/charts/chart") and n.endswith(".xml")]),1)

    def test_invalid_text_does_not_create_output(self):
        value=document()
        value["pages"][0]["elements"][4]["frame"]=[80,300,100,8]
        with self.assertRaisesRegex(TemplateInputError,"measured text"):
            build_project(value,self.base/"invalid")
        self.assertFalse((self.base/"invalid").exists())

    def test_existing_output_is_preserved(self):
        target=self.base/"existing"
        target.mkdir()
        marker=target/"keep.txt"
        marker.write_text("preserve",encoding="utf-8")
        with self.assertRaisesRegex(TemplateInputError,"already exists"):
            build_project(document(),target)
        self.assertEqual(marker.read_text(encoding="utf-8"),"preserve")

    def test_chart_domain_and_connector_scope_are_validated(self):
        bad=document()
        bad["pages"][0]["elements"][-1]["axes"]["value"]["maximum"]=4
        with self.assertRaisesRegex(TemplateInputError,"domain"):
            build_project(bad,self.base/"bad-domain")
        bad=document()
        bad["pages"][0]["elements"][2]["to"]="heading"
        with self.assertRaisesRegex(TemplateInputError,"must name a shape"):
            build_project(bad,self.base/"bad-endpoint")

    def test_template_adapter_preserves_existing_parameter_entry(self):
        value=document()
        value["pages"]=[{"id":"template-page","kind":"template","template":{"family":"ending","variant":"thanks",
            "content":{"title":"结束","message":"谢谢"}}}]
        # Use a catalog-defined example rather than coupling to a guessed variant.
        from report_ppt import load_template
        _,catalog,_=load_template()
        family=catalog["families"]["ending"]
        variant=next(iter(family["variants"]))
        value["pages"][0]["template"]["variant"]=variant
        value["pages"][0]["template"]["content"]=copy.deepcopy(family["prototype_content"])
        value["pages"][0]["template"]["content"]["actions"]=[]
        result=build_project(value,self.base/"parameter")
        self.assertEqual(result["page_count"],1)

    def test_whitespace_and_rich_runs_preserve_original_characters(self):
        value=document()
        original="来源  report materials.docx及11月12日　数据概览。"
        value["pages"][0]["elements"]=[{"id":"spaces","type":"text","frame":[60,120,1100,80],
            "runs":[{"text":"来源  ","weight":700},{"text":"report materials.docx及11月12日　数据概览。"}],
            "style":{"font_size":18}}]
        target=self.base/"spaces"
        build_project(value,target)
        svg=ET.parse(next((target/"svg_output").glob("*.svg"))).getroot()
        text=next(node for node in svg.iter() if node.get("id")=="spaces")
        self.assertEqual("".join(text.itertext()),original)
        ppt_runtime.check_project(target,target/"tokens.json")
        output=self.base/"spaces.pptx"
        ppt_runtime.export_project(target,output,target/"tokens.json")
        with ZipFile(output) as package:
            slide=ET.fromstring(package.read("ppt/slides/slide1.xml"))
            actual="".join(node.text or "" for node in slide.findall(".//a:t",ppt_runtime.NS))
            self.assertEqual(actual,original)

    def test_native_group_keeps_paragraph_and_correct_ellipse_site(self):
        value=document()
        value["pages"][0]["elements"]=[{"id":"cluster","type":"group","children":[
            {"id":"ellipse-a","type":"shape","shape":"ellipse","frame":[60,160,200,100],"fill":"#DFEAF5"},
            {"id":"rectangle-b","type":"shape","shape":"rect","frame":[480,160,200,100],"fill":"#DFEAF5"},
            {"id":"group-edge","type":"connector","from":"ellipse-a","to":"rectangle-b"},
            {"id":"group-copy","type":"text","text":"Two lines\n一个文字框", "frame":[70,300,400,120],"style":{"font_size":24}}
        ]}]
        target=self.base/"groups"
        build_project(value,target)
        ppt_runtime.check_project(target,target/"tokens.json")
        output=self.base/"groups.pptx"
        ppt_runtime.export_project(target,output,target/"tokens.json")
        with ZipFile(output) as package:
            slide=ET.fromstring(package.read("ppt/slides/slide1.xml"))
            group=slide.find(".//p:grpSp",ppt_runtime.NS)
            self.assertIsNotNone(group)
            connector=group.find("p:cxnSp",ppt_runtime.NS)
            self.assertIsNotNone(connector)
            start=connector.find(".//a:stCxn",ppt_runtime.NS)
            self.assertEqual(start.get("idx"),"6")
            ids={node.get("id") for node in group.findall("./p:sp/p:nvSpPr/p:cNvPr",ppt_runtime.NS)}
            self.assertIn(start.get("id"),ids)
            texts=["".join(node.itertext()) for node in group.findall("./p:sp/p:txBody",ppt_runtime.NS)]
            self.assertEqual(sum("Two lines" in text or "一个文字框" in text for text in texts),1)

    def test_image_is_copied_and_native_cover_crop_is_retained(self):
        from PIL import Image
        assets=self.base/"assets"
        assets.mkdir()
        Image.new("RGB",(200,50),"red").save(assets/"source.png")
        value=document()
        value["pages"][0]["elements"]=[{"id":"picture","type":"image","path":"source.png",
            "frame":[60,150,300,300],"fit":"cover","position":"xMidYMid","alt":"Fixture"}]
        target=self.base/"picture"
        build_project(value,target,asset_root=assets)
        self.assertEqual(len(list((target/"images").glob("*.png"))),1)
        ppt_runtime.check_project(target,target/"tokens.json")
        output=self.base/"picture.pptx"
        ppt_runtime.export_project(target,output,target/"tokens.json")
        with ZipFile(output) as package:
            slide=ET.fromstring(package.read("ppt/slides/slide1.xml"))
            self.assertIsNotNone(slide.find(".//p:pic/p:blipFill/a:srcRect",ppt_runtime.NS))

    def test_unknown_fields_and_unsafe_page_ids_fail_explicitly(self):
        value=document()
        value["pages"][0]["elements"][3]["style"]["fontsize"]=42
        with self.assertRaisesRegex(TemplateInputError,"unsupported text style"):
            build_project(value,self.base/"typo")
        value=document()
        value["pages"][0]["id"]="../escape"
        with self.assertRaisesRegex(TemplateInputError,"safe stable filename"):
            build_project(value,self.base/"bad-id")

    def test_dependency_changes_abort_before_publishing(self):
        with patch.object(ppt_runtime,"_runtime_fingerprint",side_effect=["before","after"]):
            with self.assertRaisesRegex(TemplateInputError,"dependencies changed"):
                build_project(document(),self.base/"changed")
        self.assertFalse((self.base/"changed").exists())
        self.assertFalse(list(self.base.glob(".presentation-build-*")))

    def test_chart_series_color_is_shared_by_payload_and_fallback(self):
        value=document()
        value["pages"][0]["elements"]=value["pages"][0]["elements"][-1:]
        value["pages"][0]["elements"][0]["series"][0]["color"]="#D65B20"
        target=self.base/"color"
        build_project(value,target)
        root=ET.parse(next((target/"svg_output").glob("*.svg"))).getroot()
        ns={"s":"http://www.w3.org/2000/svg"}
        payload=json.loads(root.find(".//s:metadata",ns).text)
        self.assertEqual(payload["style"]["colors"],["#D65B20"])
        bars=[node for node in root.findall(".//s:rect",ns) if node.get("fill")=="#D65B20"]
        self.assertEqual(len(bars),2)


if __name__ == "__main__":
    unittest.main()
