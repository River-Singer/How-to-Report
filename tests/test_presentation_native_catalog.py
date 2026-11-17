"""Native atom registry and actual editable fragment construction."""
import json
import re
from pathlib import Path
import sys
import tempfile
import unittest
from zipfile import ZipFile, ZIP_DEFLATED
from xml.etree import ElementTree as ET

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"skill-src/how-to-report/scripts"))
import presentation_native_catalog as catalog
import presentation_native as native
from test_presentation_native import native_fixture


class NativeCatalogTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        self.sources=[]
        for sid,color in (("blue","2244AA"),("red","CC4411")):
            path=self.root/(sid+".pptx");data=native_fixture(path)
            # A self-contained colored atom within a transformed source group.
            raw=data["ppt/slides/slide1.xml"].decode()
            marker='<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr></p:sp>'
            raw=raw.replace(marker,'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:solidFill><a:schemeClr val="accent1"/></a:solidFill></p:spPr></p:sp>')
            data["ppt/slides/slide1.xml"]=raw.encode()
            data["ppt/theme/theme1.xml"]=(f'<a:theme xmlns:a="{native.A}"><a:themeElements><a:clrScheme name="test"><a:accent1><a:srgbClr val="{color}"/></a:accent1></a:clrScheme></a:themeElements></a:theme>').encode()
            with ZipFile(path,"w",ZIP_DEFLATED) as z:
                for name,payload in data.items():z.writestr(name,payload)
            project=self.root/sid;native.extract_native_project(path,project)
            self.sources.append({"id":sid,"project":str(project)})
        self.library=self.root/"catalog"
        catalog.build_native_catalog(self.sources,self.library)

    def tearDown(self):self.temp.cleanup()

    def find(self,sid,object_id):
        return next(a for a in catalog.list_native_assets(self.library,source=sid,include_hidden=True,limit=100)["items"] if a["object_id"]==object_id)

    def test_all_objects_traced_hidden_excluded_default_and_group_hierarchy(self):
        result=catalog.list_native_assets(self.library,source="blue",include_hidden=True,limit=100)
        self.assertEqual(result["total"],6)
        self.assertEqual(catalog.list_native_assets(self.library,source="blue")["total"],5)
        group=self.find("blue","3");leaf=self.find("blue","5")
        self.assertEqual(leaf["parent_id"],group["id"])
        self.assertIn(leaf["id"],group["children"])
        self.assertAlmostEqual(leaf["bbox_emu"][0],914400+600*1828.8)
        self.assertFalse(self.find("blue","6")["executable"])

    def test_portable_leaf_extraction_preserves_ancestor_transform(self):
        atom=self.find("blue","5");out=self.root/"atom.pptx"
        (self.root/"blue").rename(self.root/"unavailable-original-project")
        receipt=catalog.instantiate_native_assets(self.library,[atom["id"]],out)
        self.assertEqual(receipt["text_replacement_validation"]["mode"],"not_applicable")
        with ZipFile(out) as z:
            root=ET.fromstring(z.read("ppt/slides/slide1.xml"))
            ids=[e.get("id") for e in root.iter('{'+native.P+'}cNvPr')]
            self.assertEqual(ids,["1","3","5"])
            self.assertIn("ppt/theme/theme1.xml",z.namelist())
            self.assertFalse(list(root.iter('{'+native.P+'}pic')))

    def test_cross_source_composition_resolves_each_theme_and_computes_grid(self):
        ids=[self.find(s,"5")["id"] for s in ("blue","red")]
        out=self.root/"grid.pptx";report=catalog.instantiate_native_assets(self.library,ids,out,columns=2)
        self.assertEqual(report["layout"]["columns"],2)
        frames=[r["frame_emu"] for r in report["layout"]["items"]]
        self.assertLess(frames[0][0]+frames[0][2],frames[1][0])
        with ZipFile(out) as z:
            slide=ET.fromstring(z.read("ppt/slides/slide1.xml"))
            colors={e.get("val") for e in slide.iter('{'+native.A+'}srgbClr')}
            self.assertTrue({"2244AA","CC4411"}<=colors)
            self.assertEqual(len(list(slide.iter('{'+native.A+'}schemeClr'))),0)
            ids=[e.get("id") for e in slide.iter('{'+native.P+'}cNvPr')]
            self.assertEqual(len(ids),len(set(ids)))

    def test_text_slots_real_native_edits_and_capacity_rejection(self):
        atom=self.find("blue","4");out=self.root/"text.pptx"
        receipt=catalog.instantiate_native_assets(self.library,[atom["id"]],out,texts={atom["id"]:{"t0":"Hi"}})
        self.assertEqual(receipt["text_replacement_validation"],{"mode":"source-character-count-only","changed_run_count":1,"glyph_fit":"not_measured","office_review_required":True})
        with ZipFile(out) as z:self.assertIn(b">Hi<",z.read("ppt/slides/slide1.xml"))
        with self.assertRaisesRegex(ValueError,"longer text"):
            catalog.instantiate_native_assets(self.library,[atom["id"]],self.root/"failed.pptx",texts={atom["id"]:{"t0":"Much longer than allowed"}})
        self.assertFalse((self.root/"failed.pptx").exists())

    def test_existing_output_tamper_and_invalid_request_rejected(self):
        atom=self.find("blue","5");out=self.root/"keep.pptx";out.write_bytes(b"keep")
        with self.assertRaises(ValueError):catalog.instantiate_native_assets(self.library,[atom["id"]],out)
        self.assertEqual(out.read_bytes(),b"keep")
        with self.assertRaises(ValueError):catalog.instantiate_native_assets(self.library,[atom["id"],atom["id"]],self.root/"bad.pptx",columns=True)
        pack=self.library/"sources/blue.zip"
        with pack.open("ab") as stream:stream.write(b"changed")
        with self.assertRaisesRegex(ValueError,"hash mismatch"):
            catalog.instantiate_native_assets(self.library,[atom["id"]],self.root/"bad.pptx")

    def test_grid_refuses_native_text_below_nine_points(self):
        shape=f'''<p:sp><p:nvSpPr><p:cNvPr id="7" name="Large text"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr><p:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="10000000" cy="5000000"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr><p:txBody><a:bodyPr/><a:lstStyle/><a:p><a:r><a:rPr sz="1400"><a:latin typeface="Arial"/></a:rPr><a:t>Fourteen point text</a:t></a:r></a:p></p:txBody></p:sp>'''
        source=self.root/"text-source.pptx";native_fixture(source,extra_shape=shape)
        project=self.root/"text-project";native.extract_native_project(source,project)
        library=self.root/"text-catalog";catalog.build_native_catalog([{"id":"text","project":str(project)}],library)
        asset=next(a for a in catalog.list_native_assets(library,include_hidden=True,limit=100)["items"] if a["object_id"]=="7")
        with self.assertRaisesRegex(ValueError,"below 9pt"):
            catalog.instantiate_native_assets(library,[asset["id"],asset["id"]],self.root/"tiny.pptx",columns=2)
        self.assertFalse((self.root/"tiny.pptx").exists())

    def test_refresh_keeps_pack_identity_and_adds_style_metadata(self):
        refreshed=self.root/"refreshed";catalog.refresh_native_catalog(self.library,refreshed)
        before=json.loads((self.library/"catalog.json").read_text())
        after=json.loads((refreshed/"catalog.json").read_text())
        self.assertEqual([s["pack_sha256"] for s in before["sources"]],[s["pack_sha256"] for s in after["sources"]])
        group=self.find("blue","3")
        record=catalog.describe_native_asset(refreshed,group["id"])
        self.assertIn("gradient",record["style_flags"])
        self.assertEqual(record["gradient_count"],1)
        self.assertTrue(record["structure_fingerprint"])

    def test_horizontal_line_is_indexed_but_grid_fit_is_explicitly_rejected(self):
        shape='<p:sp><p:nvSpPr><p:cNvPr id="7" name="Horizontal rule"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr><p:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="1000000" cy="0"/></a:xfrm><a:prstGeom prst="line"><a:avLst/></a:prstGeom></p:spPr></p:sp>'
        source=self.root/"line.pptx";native_fixture(source,extra_shape=shape)
        project=self.root/"line-project";native.extract_native_project(source,project)
        library=self.root/"line-catalog";catalog.build_native_catalog([{"id":"line","project":str(project)}],library)
        atom=next(a for a in catalog.list_native_assets(library,include_hidden=True,limit=100)["items"] if a["object_id"]=="7")
        self.assertEqual(atom["bbox_emu"][3],0)
        catalog.instantiate_native_assets(library,[atom["id"]],self.root/"line-only.pptx")
        with self.assertRaisesRegex(ValueError,"zero-area"):
            catalog.instantiate_native_assets(library,[atom["id"],atom["id"]],self.root/"line-grid.pptx")

    def test_composed_text_materializes_each_source_font_and_paragraph(self):
        shape='<p:sp><p:nvSpPr><p:cNvPr id="7" name="Theme text"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr><p:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="1000000" cy="500000"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr><p:txBody><a:bodyPr/><a:lstStyle/><a:p><a:r><a:t>Theme text</a:t></a:r></a:p></p:txBody></p:sp>'
        sources=[]
        for sid,font,color in (("one","Arial","223344"),("two","Georgia","554433")):
            source=self.root/(sid+".pptx");parts=native_fixture(source,extra_shape=shape)
            parts["ppt/presentation.xml"]=re.sub(rb'<p:embeddedFontLst>.*?</p:embeddedFontLst>',b'',parts["ppt/presentation.xml"])
            parts["ppt/slideMasters/slideMaster1.xml"]=parts["ppt/slideMasters/slideMaster1.xml"].replace(b'</p:sldMaster>',b'<p:txStyles><p:otherStyle><a:lvl1pPr algn="ctr"><a:lnSpc><a:spcPct val="115000"/></a:lnSpc><a:defRPr sz="1400"/></a:lvl1pPr></p:otherStyle></p:txStyles></p:sldMaster>')
            parts["ppt/theme/theme1.xml"]=(f'<a:theme xmlns:a="{native.A}"><a:themeElements><a:clrScheme name="test"><a:dk1><a:srgbClr val="{color}"/></a:dk1></a:clrScheme><a:fontScheme name="test"><a:minorFont><a:latin typeface="{font}"/></a:minorFont></a:fontScheme></a:themeElements></a:theme>').encode()
            with ZipFile(source,"w",ZIP_DEFLATED) as z:
                for name,payload in parts.items():z.writestr(name,payload)
            project=self.root/(sid+"-project");native.extract_native_project(source,project);sources.append({"id":sid,"project":str(project)})
        library=self.root/"font-catalog";catalog.build_native_catalog(sources,library)
        ids=[a["id"] for a in catalog.list_native_assets(library,include_hidden=True,limit=100)["items"] if a["object_id"]=="7"]
        out=self.root/"font-grid.pptx";catalog.instantiate_native_assets(library,ids,out)
        with ZipFile(out) as z:slide=ET.fromstring(z.read("ppt/slides/slide1.xml"))
        self.assertEqual({e.get("typeface") for e in slide.iter('{'+native.A+'}latin')},{"Arial","Georgia"})
        self.assertEqual({e.get("algn") for e in slide.iter('{'+native.A+'}pPr')},{"ctr"})
        self.assertEqual({e.get("val") for e in slide.iter('{'+native.A+'}spcPct')},{"115000"})
        self.assertTrue({"223344","554433"}<={e.get("val") for e in slide.iter('{'+native.A+'}srgbClr')})

    def test_selected_dependency_closure_omits_other_master_layouts(self):
        from test_presentation_native import rels
        source=self.root/"layouts.pptx";parts=native_fixture(source)
        parts["ppt/slideLayouts/slideLayout2.xml"]=parts["ppt/slideLayouts/slideLayout1.xml"]
        parts["ppt/slideLayouts/_rels/slideLayout2.xml.rels"]=rels(("rId1","image","../media/unused.bin"))
        parts["ppt/media/unused.bin"]=b"large-unneeded-source-payload"
        parts["[Content_Types].xml"]=parts["[Content_Types].xml"].replace(b'</Types>',b'<Default Extension="bin" ContentType="application/octet-stream"/></Types>')
        parts["ppt/slideMasters/_rels/slideMaster1.xml.rels"]=rels(("rId1","theme","../theme/theme1.xml"),("rId2","slideLayout","../slideLayouts/slideLayout1.xml"),("rId3","slideLayout","../slideLayouts/slideLayout2.xml"))
        parts["ppt/slideMasters/slideMaster1.xml"]=(f'<p:sldMaster xmlns:p="{native.P}" xmlns:a="{native.A}" xmlns:r="{native.R}"><p:cSld/><p:sldLayoutIdLst><p:sldLayoutId id="1" r:id="rId2"/><p:sldLayoutId id="2" r:id="rId3"/></p:sldLayoutIdLst></p:sldMaster>').encode()
        with ZipFile(source,"w",ZIP_DEFLATED) as z:
            for name,payload in parts.items():z.writestr(name,payload)
        project=self.root/"layouts-project";native.extract_native_project(source,project)
        library=self.root/"layouts-catalog";catalog.build_native_catalog([{"id":"layouts","project":str(project)}],library)
        atom=next(a for a in catalog.list_native_assets(library,include_hidden=True,limit=100)["items"] if a["object_id"]=="5")
        out=self.root/"small-atom.pptx";catalog.instantiate_native_assets(library,[atom["id"]],out)
        with ZipFile(out) as z:
            self.assertNotIn("ppt/slideLayouts/slideLayout2.xml",z.namelist())
            self.assertNotIn("ppt/media/unused.bin",z.namelist())
            self.assertIn("ppt/slideLayouts/slideLayout1.xml",z.namelist())

    def test_unused_empty_complex_font_is_allowed_but_used_script_is_not(self):
        fontshape='<p:sp><p:nvSpPr><p:cNvPr id="7" name="Font probe"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr><p:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="1000000" cy="500000"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr><p:txBody><a:bodyPr/><a:lstStyle/><a:p><a:r><a:rPr sz="1400"><a:cs typeface="+mn-cs"/></a:rPr><a:t>{text}</a:t></a:r><a:endParaRPr><a:cs typeface="+mn-cs"/></a:endParaRPr></a:p></p:txBody></p:sp>'
        for name,text in (("empty",""),("active","مرحبا")):
            with self.subTest(name=name):
                source=self.root/(name+".pptx");parts=native_fixture(source,extra_shape=fontshape.format(text=text))
                parts["ppt/theme/theme1.xml"]=(f'<a:theme xmlns:a="{native.A}"><a:themeElements><a:clrScheme name="test"><a:dk1><a:srgbClr val="000000"/></a:dk1></a:clrScheme><a:fontScheme name="test"><a:minorFont><a:latin typeface="Arial"/><a:cs typeface=""/></a:minorFont></a:fontScheme></a:themeElements></a:theme>').encode()
                with ZipFile(source,"w",ZIP_DEFLATED) as z:
                    for part,payload in parts.items():z.writestr(part,payload)
                project=self.root/(name+"-project");native.extract_native_project(source,project)
                library=self.root/(name+"-catalog");catalog.build_native_catalog([{"id":name,"project":str(project)}],library)
                atom=next(a for a in catalog.list_native_assets(library,include_hidden=True,limit=100)["items"] if a["object_id"]=="7")
                out=self.root/(name+"-grid.pptx")
                if text:
                    with self.assertRaisesRegex(ValueError,"unresolved source theme font"):
                        catalog.instantiate_native_assets(library,[atom["id"],atom["id"]],out)
                else:
                    catalog.instantiate_native_assets(library,[atom["id"],atom["id"]],out)
                    with ZipFile(out) as z:self.assertNotIn(b'+mn-cs',z.read("ppt/slides/slide1.xml"))

    def test_explicit_run_overrides_survive_cascade_in_schema_order_and_fonts_scale(self):
        shape='<p:sp><p:nvSpPr><p:cNvPr id="7" name="Title"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr><p:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="3744615" cy="543739"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr><p:txBody><a:bodyPr><a:spAutoFit/></a:bodyPr><a:lstStyle><a:lvl1pPr><a:defRPr sz="6400"><a:solidFill><a:srgbClr val="C63520"/></a:solidFill><a:latin typeface="Alimama ShuHeiTi Bold"/><a:ea typeface="Alimama ShuHeiTi Bold"/><a:cs typeface="Alimama ShuHeiTi Bold"/><a:sym typeface="Alimama ShuHeiTi Bold"/></a:defRPr></a:lvl1pPr></a:lstStyle><a:p><a:r><a:rPr sz="3200"><a:solidFill><a:srgbClr val="045CFA"/></a:solidFill><a:latin typeface="HarmonyOS Sans SC Black"/><a:ea typeface="HarmonyOS Sans SC Black"/></a:rPr><a:t>Title</a:t></a:r></a:p></p:txBody></p:sp>'
        source=self.root/"explicit.pptx";native_fixture(source,extra_shape=shape)
        project=self.root/"explicit-project";native.extract_native_project(source,project)
        library=self.root/"explicit-catalog";catalog.build_native_catalog([{"id":"explicit","project":str(project)}],library)
        atom=next(a for a in catalog.list_native_assets(library,include_hidden=True,limit=100)["items"] if a["object_id"]=="7")
        out=self.root/"explicit-grid.pptx";receipt=catalog.instantiate_native_assets(library,[atom["id"],atom["id"]],out,columns=2)
        with ZipFile(out) as z:slide=ET.fromstring(z.read("ppt/slides/slide1.xml"))
        for rp in slide.iter('{'+native.A+'}rPr'):
            self.assertEqual([e.tag.split('}')[-1] for e in rp],["solidFill","latin","ea","cs","sym"])
            self.assertEqual(rp.find('{'+native.A+'}solidFill/{'+native.A+'}srgbClr').get('val'),"045CFA")
            self.assertEqual(rp.find('{'+native.A+'}ea').get('typeface'),"HarmonyOS Sans SC Black")
            self.assertEqual(int(rp.get('sz')),round(3200*receipt['layout']['items'][0]['scale']))
        self.assertEqual(len(list(slide.iter('{'+native.A+'}spAutoFit'))),0)
        self.assertEqual(len(list(slide.iter('{'+native.A+'}noAutofit'))),2)

    def test_native_group_geometry_does_not_inflate_source_point_size(self):
        root,data=catalog._catalog(self.library)
        pack=catalog._Pack(root,next(s for s in data['sources'] if s['id']=='blue'))
        try:
            atom=self.find('blue','4');part,tree,_=catalog._selected(pack,atom,{})
            for _,node in native._walk(tree):
                if native._is(node,native.A,'r'):
                    rp=next(iter(catalog._elements(node,native.A,'rPr')),None)
                    if rp is None:
                        rp=catalog._element('a:rPr',native.A);node['children'].insert(0,rp)
                    rp['attrs']['sz']='1400'
            # The retained source group uses ext/chExt = 1828.8. Its text is
            # still 14pt, not 25,603pt; group coordinates are shape coordinates.
            self.assertEqual(catalog._source_text_sizes(pack,part,tree),[14,14,14])
        finally:pack.close()


if __name__=="__main__":unittest.main()
