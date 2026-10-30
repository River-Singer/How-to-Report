"""Meaningful small-graph regressions: topology, clearance and exact labels."""
from copy import deepcopy
import importlib.util
from pathlib import Path
import unittest
import json
import xml.etree.ElementTree as ET

import test_report_html as legacy
import test_presentation as presentation

SCRIPT = Path(__file__).resolve().parents[1]/'skill-src/how-to-report/scripts/diagram_layout.py'
SPEC = importlib.util.spec_from_file_location('diagram_layout_under_test', SCRIPT)
graph = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(graph)


def diagram(ids, links):
    return {'kind':'relation', 'nodes':[{'id':i,'label':i,'refs':[]} for i in ids],
            'edges':[{'id':'edge'+str(n),'from':a,'to':b,'relation':r,'label':'条件成立后推进','refs':[]} for n,(a,b,r) in enumerate(links)]}


class DiagramLayoutTests(unittest.TestCase):
    def clear(self, data, layout):
        self.assertEqual(set(layout['edges']), {e['id'] for e in data['edges']})
        for edge in data['edges']:
            path = layout['edges'][edge['id']]
            for a,b in zip(path,path[1:]):
                self.assertTrue(a[0]==b[0] or a[1]==b[1])
                for nid,rect in layout['nodes'].items():
                    self.assertFalse(graph.intersects(a,b,rect), (edge['id'],nid,a,b,rect))
            for x,y in path:
                self.assertTrue(0<=x<=layout['width'] and 0<=y<=layout['height'])
        for rect in [*layout['nodes'].values(),*(l['rect'] for l in layout['labels'].values())]:
            x,y,w,h=rect
            self.assertGreaterEqual(x,0); self.assertGreaterEqual(y,0)
            self.assertLessEqual(x+w,layout['width']);self.assertLessEqual(y+h,layout['height'])

    def test_parallel_branch_stays_parallel_and_clear(self):
        data=diagram(['base','horizontal','vertical'], [('base','horizontal','dependency'),('base','vertical','dependency')])
        layout=graph.layout_diagram(data)
        boxes=layout['nodes']
        self.assertEqual(boxes['horizontal'][0], boxes['vertical'][0])
        self.assertNotEqual(boxes['horizontal'][1], boxes['vertical'][1])
        self.assertLess(boxes['base'][0], boxes['horizontal'][0])
        self.clear(data,layout)

    def test_feedback_goes_around_middle_node(self):
        data=diagram(['ce','ci','system'], [('ce','ci','data-flow'),('ci','system','data-flow'),('system','ce','feedback')])
        layout=graph.layout_diagram(data)
        self.clear(data,layout)
        middle=layout['nodes']['ci']
        self.assertTrue(any(y>middle[1]+middle[3] for x,y in layout['edges']['edge2']))
        self.assertEqual(layout,graph.layout_diagram(dict(data,nodes=list(reversed(data['nodes'])),edges=list(reversed(data['edges'])))))

    def test_join_and_skip_edge_dont_run_through_intermediate_node(self):
        data=diagram(['a','b','c','d'], [('a','b','sequence'),('a','c','sequence'),('b','d','dependency'),('c','d','dependency'),('a','d','association')])
        self.clear(data,graph.layout_diagram(data))

    def test_cycle_is_routed_without_dropping_or_reclassifying_edges(self):
        data=diagram(['a','b','c'], [('a','b','dependency'),('b','c','dependency'),('c','a','dependency')])
        original=deepcopy(data)
        self.clear(data,graph.layout_diagram(data));self.assertEqual(data,original)

    def test_long_axis_and_association_are_distinct(self):
        data=diagram(['part','assembly','module','system','vehicle','compare'], [('part','assembly','sequence'),('assembly','module','sequence'),('module','system','sequence'),('system','vehicle','sequence'),('vehicle','compare','association')])
        layout=graph.layout_diagram(data)
        self.assertEqual(layout['direction'],'vertical')
        self.assertEqual(layout['nodes']['vehicle'][1],layout['nodes']['compare'][1])
        self.assertNotEqual(layout['nodes']['vehicle'][0],layout['nodes']['compare'][0])
        self.clear(data,layout)

    def test_swimlane_rank_is_not_input_position(self):
        data=diagram(['c','a','b','d'], [('a','b','dependency'),('b','c','data-flow'),('c','d','dependency'),('d','a','feedback')])
        data['kind']='swimlane';data['lanes']=[{'id':'business','label':'业务'},{'id':'delivery','label':'实施'}]
        for n in data['nodes']: n['lane']='business' if n['id'] in ('a','d') else 'delivery'
        layout=graph.layout_diagram(data)
        self.assertLess(layout['nodes']['a'][0],layout['nodes']['b'][0])
        self.assertLess(layout['nodes']['b'][0],layout['nodes']['c'][0])
        self.assertEqual(layout['nodes']['a'][1],layout['nodes']['d'][1])
        self.clear(data,layout)

    def test_explicit_direction_and_short_label_preserve_input(self):
        data=diagram(['a','b'], [('a','b','dependency')]);data['direction']='vertical'
        full='资源尚未批准，因此日期仅为附条件预测，不能作为确定承诺'
        data['edges'][0]['label']=full;data['edges'][0]['short_label']='资源待批 · 附条件预测'
        original=deepcopy(data);layout=graph.layout_diagram(data)
        self.assertEqual(layout['direction'],'vertical')
        self.assertEqual(''.join(layout['labels']['edge0']['lines']),data['edges'][0]['short_label'])
        self.assertEqual(data,original)

    def test_eight_nodes_and_edges_with_mixed_relations(self):
        data=diagram(list('abcdefgh'), [('a','b','sequence'),('b','c','sequence'),('a','d','dependency'),('d','e','dependency'),('e','f','dependency'),('f','g','data-flow'),('g','h','data-flow'),('h','a','feedback')])
        self.clear(data,graph.layout_diagram(data))

    def test_unicode_wrap_preserves_every_character(self):
        text='系统 MAStér / 未批准资源不能成为确定承诺'
        self.assertEqual(''.join(graph.wrap_label(text)),text)

    def test_lane_surfaces_and_labels_fit_declared_viewbox(self):
        data=diagram(['a','b','c'], [('a','b','dependency'),('b','c','feedback')])
        data['kind']='swimlane';data['lanes']=[{'id':'one','label':'Long lane'},{'id':'two','label':'Other lane'}]
        for node in data['nodes']: node['lane']='one' if node['id']=='a' else 'two'
        layout=graph.layout_diagram(data)
        for lane in layout['lanes']:
            self.assertLessEqual(lane['y']+lane['height'],layout['height'])
        self.clear(data,layout)


class DiagramContractTests(unittest.TestCase):
    helper = legacy.ReportHTMLTests.helper
    write = legacy.ReportHTMLTests.write
    run_cli = legacy.ReportHTMLTests.run_cli
    component = presentation.PresentationTests.component

    def setUp(self):
        presentation.PresentationTests.setUp(self)

    def test_full_label_refs_and_exact_edges_survive_short_display(self):
        data=diagram(['a','b'], [('a','b','dependency')])
        data['edges'][0].update(label='资源尚未批准，日期仅为附条件预测，不能作为确定承诺',short_label='资源待批 · 附条件预测',refs=[{'id':'record','revision':3,'locator':'原始条件'}])
        self.component('diagram',data);self.write();self.run_cli(isolated=True)
        html=(self.output/'index.html').read_text(encoding='utf-8')
        svg=html.split('<svg',1)[1].split('</svg>',1)[0]
        rendered=ET.fromstring('<svg'+svg+'</svg>').find('.//text[@class="edge-label"]')
        self.assertEqual(''.join(rendered.itertext()),'资源待批 · 附条件预测')
        self.assertIn(data['edges'][0]['label'],html)
        self.assertIn('record@3',html)
        self.assertNotIn('record@3',svg)
        self.assertNotIn('class="relation-key"',svg)
        mapping=json.loads((self.output/'page-map.json').read_text(encoding='utf-8'))['elements']
        edge=next(m for m in mapping if m.get('datum_id')=='edge0')
        self.assertEqual(edge['displayed'],data['edges'][0])
        self.assertEqual(edge['refs'],data['edges'][0]['refs'])

    def test_association_has_no_arrow_and_generated_ids_remain_unique(self):
        data=diagram(['a','b','c'], [('a','b','dependency'),('b','c','association'),('c','a','feedback')])
        self.component('diagram',data);self.write();self.run_cli()
        html=(self.output/'index.html').read_text(encoding='utf-8')
        group=html.split('id="datum-edge1"',1)[1].split('</g>',1)[0]
        self.assertNotIn('marker-end=',group);self.assertIn('stroke-dasharray=',group)
        ids=[a['id'] for _,a in legacy.Nodes(html).tags if 'id' in a]
        self.assertEqual(len(ids),len(set(ids)))

    def test_explicit_short_label_and_direction_are_validated(self):
        self.component('diagram',diagram(['a','b'], [('a','b','dependency')]))
        data=self.plan['pages'][0]['elements'][0]['diagram']
        for invalid in ('diagonal',None,[]):
            data['direction']=invalid
            with self.subTest(direction=invalid),self.assertRaises(ValueError): self.helper().validate(self.plan)
        data['direction']='vertical'
        for invalid in ('', '文'*25,False):
            data['edges'][0]['short_label']=invalid
            with self.subTest(short_label=invalid),self.assertRaises(ValueError): self.helper().validate(self.plan)
        data['edges'][0]['short_label']='待批准'
        self.helper().validate(self.plan)


if __name__=='__main__': unittest.main()
