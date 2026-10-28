"""Deterministic presentation contract checks; actual browser evidence is separate."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import unittest

import test_report_html as legacy


class PresentationTests(unittest.TestCase):
    helper = legacy.ReportHTMLTests.helper
    write = legacy.ReportHTMLTests.write
    run_cli = legacy.ReportHTMLTests.run_cli

    def setUp(self):
        legacy.ReportHTMLTests.setUp(self)
        self.plan['page_plan_version'] = '0.2'
        self.plan['pages'] = self.plan['pages'][:2]
        self.plan['pages'][0]['limits'] = []
        self.plan['pages'][0]['notes'] = '提醒：关键条件必须讲清楚。'
        self.plan['main_path'] = [self.plan['pages'][0]['id']]
        self.plan['pages'][0]['backup_links'] = [{'label':'核对依据', 'target':self.plan['pages'][1]['id']}]

    def component(self, kind, value):
        self.plan['pages'] = [self.plan['pages'][0]]
        page = self.plan['pages'][0]
        page.pop('backup_links', None)
        page['layout'] = 'composed'
        page['elements'] = [{'id':'custom', 'type':kind, 'role':'primary', 'title':'工程输入', 'body':'合成数据，仅检查表达机制。', 'refs':[{'id':'synthetic','revision':1}], 'limits':[], kind:value}]
        page['tree'] = {'element':'custom'}

    def test_single_title_retains_semantics_without_claiming_them_visible(self):
        self.write(); self.run_cli(isolated=True)
        html = (self.output/'index.html').read_text(encoding='utf-8')
        self.assertNotIn('<p class="question">', html)
        self.assertNotIn('<p class="takeaway">', html)
        entries = json.loads((self.output/'page-map.json').read_text(encoding='utf-8'))['elements']
        page = next(x for x in entries if x['selector'] == '#page-'+self.plan['pages'][0]['id'])
        self.assertEqual(page['semantic']['question'], self.plan['pages'][0]['question'])
        self.assertNotIn('question', page['displayed'])
        self.assertEqual(page['speaker_notes'], self.plan['pages'][0]['notes'])
        self.assertIn('data-backup-target=', html)
        self.assertIn('id="contents-dialog"', html)

    def test_route_and_backup_targets_are_exact_and_checked(self):
        helper=self.helper()
        for route in ([], ['missing'], ['focus','focus'], None):
            plan=deepcopy(self.plan); plan['main_path']=route
            with self.subTest(route=route), self.assertRaises(ValueError): helper.validate(plan)
        self.plan['pages'][0]['backup_links'][0]['target']='missing'
        with self.assertRaises(ValueError): helper.validate(self.plan)

    def test_legacy_plan_keeps_visible_question_and_takeaway(self):
        self.plan['page_plan_version']='0.1'; self.plan.pop('main_path')
        for page in self.plan['pages']:
            page.pop('notes',None); page.pop('backup_links',None); page['limits']=['保留旧限定']
        self.write(); self.run_cli()
        html=(self.output/'index.html').read_text(encoding='utf-8')
        self.assertIn('<p class="question">',html); self.assertIn('<p class="takeaway">',html)

    def test_theme_is_values_not_css_injection(self):
        self.plan['theme']={'accent':'#156a98'}; self.helper().validate(self.plan)
        for bad in ('red', '#123;display:none', {}, '#12345678'):
            self.plan['theme']['accent']=bad
            with self.subTest(bad=bad), self.assertRaises(ValueError): self.helper().validate(self.plan)

    def test_structured_table_retains_null_and_reference_mapping(self):
        self.component('table',{'columns':['事项','状态'], 'rows':[{'id':'row1','cells':['联调',None],'refs':[{'id':'record','revision':3,'locator':'行2'}]}]})
        self.write(); self.run_cli()
        html=(self.output/'index.html').read_text(encoding='utf-8')
        self.assertIn('未提供',html); self.assertIn('record@3',html)
        entries=json.loads((self.output/'page-map.json').read_text(encoding='utf-8'))['elements']
        row=next(x for x in entries if x.get('datum_id')=='row1')
        self.assertIsNone(row['displayed']['cells'][1])

    def test_media_is_hashed_before_writes_and_snapshotted(self):
        # A real minimal PNG; this test verifies byte closure, not perceptual image quality.
        import base64
        raw=base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9Y9ZlS8AAAAASUVORK5CYII=')
        (self.root/'pixel.png').write_bytes(raw)
        media={'kind':'image','file':{'path':'pixel.png','sha256':hashlib.sha256(raw).hexdigest()},'alt':'合成像素', 'annotations':[{'id':'ann1','label':'定位示意','x':10,'y':10,'width':20,'height':30,'refs':[]}]}
        self.component('media',media);self.write();self.run_cli()
        receipt=json.loads((self.output/'render-receipt.json').read_text(encoding='utf-8'))
        media_names=[n for n in receipt['files'] if n.startswith('media/')]
        self.assertEqual(len(media_names),1);self.assertEqual((self.output/media_names[0]).read_bytes(),raw)
        html=(self.output/'index.html').read_text(encoding='utf-8');self.assertIn('src="data:image/png;base64,',html)
        self.assertNotIn('src="pixel.png"',html)

    def test_invalid_or_missing_media_leaves_no_output(self):
        self.component('media',{'kind':'image','file':{'path':'missing.png','sha256':'0'*64},'alt':'缺失文件'})
        self.write(); self.run_cli(expected=2);self.assertFalse(self.output.exists())
        (self.root/'missing.png').write_bytes(b'not an image')
        self.write(); self.run_cli(expected=2);self.assertFalse(self.output.exists())
        self.plan['pages'][0]['elements'][0]['media']['file']['path']='../outside.png'
        with self.assertRaises(ValueError): self.helper().validate(self.plan)

    def test_media_rejects_unsupported_annotation_and_missing_video_poster(self):
        self.component('media',{'kind':'video','file':{'path':'clip.mp4','sha256':'0'*64},'alt':'片段'})
        with self.assertRaises(ValueError): self.helper().validate(self.plan)
        media=self.plan['pages'][0]['elements'][0]['media']; media['poster']={'path':'poster.png','sha256':'0'*64}
        media['annotations']=[{'id':'a','label':'x','x':0,'y':0,'width':1,'height':1,'refs':[]}]
        with self.assertRaises(ValueError): self.helper().validate(self.plan)

    def test_media_rejects_raw_svg_even_with_correct_hash(self):
        raw=b'<svg xmlns="http://www.w3.org/2000/svg"><script>alert(1)</script></svg>'
        (self.root/'unsafe.svg').write_bytes(raw)
        self.component('media',{'kind':'image','file':{'path':'unsafe.svg','sha256':hashlib.sha256(raw).hexdigest()},'alt':'Unsupported SVG'})
        self.write();self.run_cli(expected=2);self.assertFalse(self.output.exists())

    def test_media_rejects_wrong_signature_even_with_correct_hash(self):
        raw=b'not a decoded image or a PNG signature'
        (self.root/'wrong.png').write_bytes(raw)
        self.component('media',{'kind':'image','file':{'path':'wrong.png','sha256':hashlib.sha256(raw).hexdigest()},'alt':'Wrong signature'})
        self.write();self.run_cli(expected=2);self.assertFalse(self.output.exists())

    def test_explicit_relationships_have_traceable_nodes_edges_and_text(self):
        self.component('diagram', {'kind':'swimlane','lanes':[{'id':'team','label':'集成组'}], 'nodes':[{'id':'a','label':'接口准备','lane':'team','refs':[]},{'id':'b','label':'执行联调','lane':'team','refs':[]}], 'edges':[{'id':'ab','from':'a','to':'b','relation':'dependency','label':'联调以前置接口就绪为条件','refs':[{'id':'plan','revision':2}]}]})
        self.write();self.run_cli()
        entries=json.loads((self.output/'page-map.json').read_text(encoding='utf-8'))['elements']
        self.assertTrue({'a','b','ab'} <= {x.get('datum_id') for x in entries})
        html=(self.output/'index.html').read_text(encoding='utf-8');self.assertIn('dependency',html);self.assertIn('plan@2',html)
        ids=[a['id'] for _,a in legacy.Nodes(html).tags if 'id' in a];self.assertEqual(len(ids),len(set(ids)))
        self.plan['pages'][0]['elements'][0]['diagram']['edges'][0]['to']='missing'
        with self.assertRaises(ValueError): self.helper().validate(self.plan)
        self.plan['pages'][0]['elements'][0]['diagram']['edges'][0]['to']=[]
        with self.assertRaises(ValueError): self.helper().validate(self.plan)


if __name__=='__main__':
    unittest.main()
