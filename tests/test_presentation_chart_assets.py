"""Data contracts, quantitative geometry and computed/native chart asset integration."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from xml.etree import ElementTree as ET
from zipfile import ZipFile

PROJECT=Path(__file__).resolve().parents[1]
SCRIPTS=PROJECT/'skill-src/how-to-report/scripts'
sys.path[:0]=[str(SCRIPTS),str(PROJECT/'skill-src/shared/scripts')]
import presentation_chart_assets as charts
from presentation_document import resolve_text,resolve_value
from presentation_layout import lower_layout_page
from presentation_library import resolve_profile_tokens
from presentation_svg import SceneRenderer
from report_ppt import DEFAULT_TEMPLATE,TemplateInputError,load_template
from ppt_runtime import _engine_modules

SVG='{http://www.w3.org/2000/svg}'


class ChartAssetsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _,_,cls.tokens=load_template(DEFAULT_TEMPLATE,resolve_profile_tokens(charts.chart_story('bar'),None))

    def render(self,key,data=None,options=None):
        author=charts.chart_story(key,data,options)
        scene,report=lower_layout_page(author['pages'][0],{},(1280,720),self.tokens)
        svg,mapping,assets=SceneRenderer(scene,self.tokens,None,resolve_text,resolve_value,{}).render()
        return ET.fromstring(svg),scene,report

    def test_every_vocabulary_entry_has_valid_schema_example_and_real_vector_story(self):
        import jsonschema
        records=charts.chart_assets()
        checker=_engine_modules()[0]();checker.scan_banner=False
        self.assertEqual(len(records),68)
        self.assertEqual(len({r['id'] for r in records}),68)
        self.assertEqual(len({c for r in records for c in r['categories']}),9)
        for row in records:
            with self.subTest(chart=row['id']):
                detail=charts.describe_chart_asset(row['id'])
                jsonschema.Draft202012Validator.check_schema(detail['data_schema'])
                jsonschema.Draft202012Validator(detail['data_schema']).validate(detail['example']['data'])
                self.assertTrue(detail['executable'])
                self.assertTrue(detail['use_cases']);self.assertTrue(detail['avoid']);self.assertTrue(detail['limitations'])
                xml,scene,report=self.render(row['id'])
                with tempfile.TemporaryDirectory(prefix='chart-svg-contract-') as folder:
                    path=Path(folder)/'chart.svg';ET.ElementTree(xml).write(path,encoding='utf-8',xml_declaration=True)
                    checked=checker.check_file(str(path),expected_viewbox='0 0 1280 720')
                    self.assertEqual(checked['errors'],[])
                self.assertFalse(list(xml.iter(SVG+'image')))
                self.assertFalse(list(xml.iter(SVG+'linearGradient')))
                self.assertFalse(list(xml.iter(SVG+'radialGradient')))
                geometry=[node for node in xml.iter() if node.tag in {SVG+'path',SVG+'rect',SVG+'circle',SVG+'line'}]
                self.assertGreater(len(geometry),2)
                self.assertTrue(all(float(node.get('font-size'))>=12 for node in xml.iter(SVG+'text')))
                self.assertNotIn('frame',charts.instantiate_chart_asset(row['id'],detail['example']['data']))

    def test_structural_and_semantic_errors_are_not_silently_repaired(self):
        with self.assertRaisesRegex(TemplateInputError,'unknown'):charts.describe_chart_asset('imaginary')
        example=charts.describe_chart_asset('bar')['example']['data']
        for option in ({'frame':[0,0,600,400]},{'font_size':7},{'orientation':'vertical'},{'bins':8}):
            with self.subTest(option=option),self.assertRaises(TemplateInputError):charts.instantiate_chart_asset('bar',example,option)
        for values in ([1,2],[True,2,3,4],[float('nan'),2,3,4]):
            bad=copy.deepcopy(example);bad['series'][0]['values']=values
            with self.subTest(values=values),self.assertRaises(TemplateInputError):charts.instantiate_chart_asset('bar',bad)
        negative={'categories':['A','B'],'series':[{'name':'Value','values':[3,-1]}]}
        for key in ('pie','doughnut','area'):
            with self.subTest(key=key),self.assertRaises(TemplateInputError):charts.instantiate_chart_asset(key,negative)
        too_many=copy.deepcopy(example);too_many['series'].append(copy.deepcopy(too_many['series'][0]))
        with self.assertRaises(TemplateInputError):charts.instantiate_chart_asset('line',too_many)

    def test_data_changes_recompute_bar_length_without_model_coordinates(self):
        data={'categories':['A','B','C'],'series':[{'name':'Count','values':[10,20,30]}]}
        before,_,_=self.render('bar',data)
        data['series'][0]['values'][0]=20
        after,_,_=self.render('bar',data)
        def bars(xml):return [float(n.get('width')) for n in xml.iter(SVG+'rect') if n.get('fill')==self.tokens['theme']['slots']['accent1']]
        original,changed=bars(before),bars(after)
        self.assertEqual(len(original),3)
        self.assertAlmostEqual(changed[0],original[0]*2)
        self.assertEqual(changed[1:],original[1:])

    def test_bubble_uses_area_not_radius_and_remains_inside_container(self):
        data={'series':[{'name':'Value','points':[[0,0,1],[10,10,4]]}]}
        xml,scene,_=self.render('bubble',data)
        circles=list(xml.iter(SVG+'circle'))
        self.assertEqual(len(circles),2)
        self.assertAlmostEqual(float(circles[1].get('r'))/float(circles[0].get('r')),2)
        frame=next(n['frame'] for n in scene['elements'] if n['type']=='chart')
        for node in circles:
            x,y,r=[float(node.get(k)) for k in ('cx','cy','r')]
            self.assertGreaterEqual(x-r,frame[0]);self.assertLessEqual(x+r,frame[0]+frame[2])
            self.assertGreaterEqual(y-r,frame[1]);self.assertLessEqual(y+r,frame[1]+frame[3])

    def test_xy_markers_and_axis_labels_share_the_same_numeric_scale(self):
        data={'series':[{'name':'Value','points':[[0,0,1],[10,20,4]]}]}
        xml,_,_=self.render('bubble',data)
        y_ticks=[];x_ticks=[]
        for node in xml.iter(SVG+'text'):
            try:value=float(node.text)
            except (ValueError,TypeError):continue
            if node.get('text-anchor')=='end':y_ticks.append((float(node.get('y'))-float(node.get('font-size'))*.3,value))
            elif node.get('text-anchor')=='middle':x_ticks.append((float(node.get('x')),value))
        def interpolate(ticks,coordinate):
            a,b=min(ticks),max(ticks)
            return a[1]+(b[1]-a[1])*(coordinate-a[0])/(b[0]-a[0])
        for node,(x,y,_) in zip(xml.iter(SVG+'circle'),data['series'][0]['points']):
            self.assertAlmostEqual(interpolate(x_ticks,float(node.get('cx'))),x,delta=.03)
            self.assertAlmostEqual(interpolate(y_ticks,float(node.get('cy'))),y,delta=.06)

    def test_bump_rank_ticks_match_top_rank_one_and_use_integer_ticks(self):
        data={'categories':['Before','After'],'series':[{'name':'A','values':[90,10]},{'name':'B','values':[10,90]}]}
        xml,_,_=self.render('bump',data)
        ticks=[]
        for node in xml.iter(SVG+'text'):
            if node.get('text-anchor')=='end':
                ticks.append((float(node.get('y'))-float(node.get('font-size'))*.3,float(node.text)))
        self.assertEqual([v for _,v in sorted(ticks)],[1,2])
        marker_y=[float(n.get('cy')) for n in xml.iter(SVG+'circle')]
        self.assertEqual(marker_y,[min(ticks)[0],max(ticks)[0],max(ticks)[0],min(ticks)[0]])

    def test_histogram_uses_observed_samples_and_touching_equal_width_bins(self):
        xml,_,_=self.render('histogram',{'series':[{'name':'Sample','values':[0,0,1,2,4,6]}]}, {'bins':3})
        bars=[n for n in xml.iter(SVG+'rect') if n.get('fill')==self.tokens['theme']['slots']['accent1']]
        self.assertEqual(len(bars),3)
        heights=[float(n.get('height')) for n in bars]
        self.assertAlmostEqual(heights[1]/heights[0],1/3)
        self.assertAlmostEqual(heights[2]/heights[0],2/3)
        self.assertAlmostEqual(float(bars[0].get('x'))+float(bars[0].get('width')),float(bars[1].get('x')))

    def test_voronoi_covers_bounds_and_sites_are_nearest_inside_each_cell(self):
        data=charts.describe_chart_asset('voronoi')['example']['data']
        cells=charts._voronoi_cells(data)
        self.assertAlmostEqual(sum(abs(charts._polygon_area(c)) for c in cells),60)
        for site,cell in zip(data['sites'],cells):
            for x,y in cell:
                own=(x-site['point'][0])**2+(y-site['point'][1])**2
                self.assertTrue(all(own<=(x-s['point'][0])**2+(y-s['point'][1])**2+1e-8 for s in data['sites']))

    def test_four_hundred_hemicycle_seats_do_not_overlap(self):
        xml,_,_=self.render('arc',{'categories':['A','B'],'series':[{'name':'Seats','values':[240,160]}]})
        circles=[tuple(float(n.get(k)) for k in ('cx','cy','r')) for n in xml.iter(SVG+'circle')]
        self.assertEqual(len(circles),400)
        for i,(x,y,r) in enumerate(circles):
            self.assertTrue(all((x-a)**2+(y-b)**2>=(r+s)**2-.01 for a,b,s in circles[i+1:]))

    def test_sankey_refuses_cycles_unbalanced_flows_and_has_value_labels(self):
        data=charts.describe_chart_asset('sankey')['example']['data']
        xml,_,_=self.render('sankey',data)
        labels=[n.text for n in xml.iter(SVG+'text')]
        self.assertIn('30',labels);self.assertIn('20',labels);self.assertIn('A (50)',labels)
        bad=copy.deepcopy(data);bad['links'][2]['value']=40
        with self.assertRaisesRegex(TemplateInputError,'conserve'):self.render('sankey',bad)
        bad=copy.deepcopy(data);bad['links'].append({'source':'D','target':'A','value':50})
        with self.assertRaisesRegex(TemplateInputError,'acyclic'):self.render('sankey',bad)

    def test_geography_requires_real_input_semantics_and_no_random_dot_generation(self):
        choropleth=charts.describe_chart_asset('choropleth')['example']['data']
        choropleth['metric_type']='count'
        with self.assertRaisesRegex(TemplateInputError,'metric_type'):charts.instantiate_chart_asset('choropleth',choropleth)
        dots=charts.describe_chart_asset('dot-density')['example']['data']
        xml,_,_=self.render('dot-density',dots)
        self.assertEqual(len(list(xml.iter(SVG+'circle'))),len(dots['points']))
        del dots['points']
        with self.assertRaisesRegex(TemplateInputError,'event points'):charts.instantiate_chart_asset('dot-density',dots)

    def test_degenerate_flow_geometry_and_overcrowded_sankey_are_explicit_errors(self):
        data=charts.describe_chart_asset('flow-map')['example']['data']
        data['regions'][3]['boundary']=copy.deepcopy(data['regions'][0]['boundary'])
        with self.assertRaisesRegex(TemplateInputError,'coincident centroids'):self.render('flow-map',data)
        data={'nodes':[{'id':str(i),'label':str(i)} for i in range(20)],
              'links':[{'source':'0','target':str(i),'value':1} for i in range(1,20)]}
        story=charts.chart_story('sankey',data)
        story['pages'][0]['layout']['children'][1]['height']=100
        scene,report=lower_layout_page(story['pages'][0],{},(1280,720),self.tokens)
        with self.assertRaisesRegex(TemplateInputError,'too many nodes'):
            SceneRenderer(scene,self.tokens,None,resolve_text,resolve_value,{}).render()

    def test_source_request_is_immutable_and_capacity_errors_are_explicit(self):
        detail=charts.describe_chart_asset('bar');data=detail['example']['data'];snapshot=copy.deepcopy(data)
        leaf=charts.instantiate_chart_asset('bar',data);leaf['data']['series'][0]['values'][0]=999
        self.assertEqual(data,snapshot)
        bad=copy.deepcopy(data);bad['categories'][0]='一个无法放入默认类别列的非常非常长的分类名称'*2
        with self.assertRaisesRegex(TemplateInputError,'label.*exceeds'):self.render('bar',bad)


if __name__=='__main__':unittest.main()
