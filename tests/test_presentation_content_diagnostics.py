"""Content observations are traceable warnings, never quality scores or edits."""
import copy
import hashlib
import json
import math
from pathlib import Path
import sys
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parents[1] / 'skill-src/how-to-report'
sys.path.insert(0, str(SOURCE / 'scripts'))
from presentation_chart_assets import chart_story
from presentation_compiler import build_project
from presentation_content_diagnostics import rectangle_union_area, analyze_page, _occupancy, _ring_rectangles, validate_page_intent
from presentation_library import profile_identity
from presentation_recipes import compose_document


def text_page(intent='analysis'):
    page = {'id': 'sample', 'kind': 'layout', 'layout_version': '0.1', 'job': '展示当前业务判断',
            'layout': {'id': 'root', 'type': 'column', 'padding': 32, 'gap': 16, 'children': [
                {'id': 'title', 'type': 'leaf', 'element': {'type': 'text', 'role': 'title', 'text': '当前判断'}},
                {'id': 'body', 'type': 'leaf', 'height': 300, 'element': {'type': 'text', 'role': 'body', 'text': '只有一项说明。'}}]}}
    if intent is not None:
        page['intent'] = intent
    return {'schema_version': '0.1', 'project_id': 'content-diagnostic-test', 'revision': 1,
            'brief': {'design_profile': profile_identity()}, 'sources': [], 'facts': {}, 'pages': [page]}


class ContentDiagnosticsTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='content-diagnostics-')
        self.root = Path(self.temporary.name)

    def tearDown(self):
        self.temporary.cleanup()

    def build(self, author, name):
        path = self.root / name
        before = copy.deepcopy(author)
        receipt = build_project(author, path, geometry_policy='computed')
        self.assertEqual(author, before)
        raw = (path / 'content-diagnostics.json').read_bytes()
        self.assertEqual(receipt['content_diagnostics']['sha256'], hashlib.sha256(raw).hexdigest())
        report = json.loads(raw)
        self.assertEqual(report['semantic_quality'], 'not_assessed')
        self.assertIn('presentation_content_diagnostics.py', receipt['compiler_files'])
        return report['pages'][0], path

    def test_union_is_not_sum_or_full_container_area(self):
        self.assertEqual(rectangle_union_area([[0, 0, 10, 10], [5, 0, 10, 10]]), 150)
        report, path = self.build(text_page(), 'sparse')
        codes = {w['code'] for w in report['warnings']}
        self.assertIn('limited_analysis_support', codes)
        self.assertLess(report['observations']['text_rectangle_union_canvas_fraction'], .1)
        svg = next((path/'svg_output').glob('*.svg')).read_text(encoding='utf-8')
        self.assertNotIn('limited_analysis_support', svg)
        self.assertNotIn('review_question', svg)

    def test_cover_and_section_whitespace_are_valid_not_sparse_errors(self):
        for intent in ('cover', 'section', 'demo'):
            report, _ = self.build(text_page(intent), intent)
            self.assertEqual(report['warnings'], [])
            self.assertEqual(report['status'], 'observed')
            self.assertEqual(report['semantic_quality'], 'not_assessed')

    def test_few_words_with_real_data_are_not_treated_as_empty_analysis(self):
        author = chart_story('bar', {'categories': ['A', 'B'], 'series': [{'name': 'n', 'values': [10, 20]}]})
        author['pages'][0]['intent'] = 'analysis'
        report, _ = self.build(author, 'data')
        self.assertEqual(report['observations']['supplied_data_record_count'], 2)
        self.assertNotIn('limited_analysis_support', {w['code'] for w in report['warnings']})

    def test_large_arch_with_two_repeated_nodes_is_flagged_without_modification(self):
        author = text_page('architecture')
        author['pages'][0]['layout']['children'][1] = {'id': 'arch', 'type': 'leaf', 'height': 450,
            'element': {'type': 'component', 'component': 'topology', 'layout': 'arch',
                        'nodes': [{'id': 'a', 'label': '平台'}, {'id': 'b', 'label': '平台'}]}}
        report, _ = self.build(author, 'arch')
        self.assertTrue({'large_frame_few_graph_items', 'repeated_topology_labels'} <= {w['code'] for w in report['warnings']})
        item = report['observations']['topologies'][0]
        self.assertEqual((item['node_count'], item['edge_count']), (2, 0))
        self.assertLess(item['node_rectangle_union_canvas_fraction'], item['allocated_canvas_fraction'])

    def test_missing_intent_is_compatible_and_bad_intent_fails_before_publish(self):
        report, _ = self.build(text_page(None), 'legacy')
        self.assertIn('intent_not_declared', {w['code'] for w in report['warnings']})
        with self.assertRaisesRegex(ValueError, 'intent'):
            build_project(text_page('guaranteed-80'), self.root/'invalid', geometry_policy='computed')
        self.assertFalse((self.root/'invalid').exists())

    def test_recipe_intent_survives_compose_and_normal_rebuild(self):
        request = json.loads((SOURCE/'assets/design-system/examples/three-recipes.json').read_text(encoding='utf-8'))
        request['pages'] = [request['pages'][1]]
        request['pages'][0]['intent'] = 'comparison'
        author = compose_document(request)
        self.assertEqual(author['pages'][0]['intent'], 'comparison')
        report, _ = self.build(author, 'recipe')
        self.assertEqual(report['intent'], 'comparison')

    def test_body_region_uses_solved_node_and_excludes_title(self):
        author = text_page()
        author['pages'][0]['content_diagnostics'] = {'region_node_id': 'body'}
        report, path = self.build(author, 'body-region')
        occupancy = report['occupancy']
        self.assertEqual(occupancy['region_source'], 'layout_node:body')
        self.assertEqual(occupancy['allocated_fraction'], 1)
        self.assertLess(occupancy['estimated_content_fraction'], .02)
        self.assertAlmostEqual(occupancy['estimated_content_fraction'] + occupancy['estimated_blank_fraction'], 1)
        author['pages'][0]['content_diagnostics']['region_node_id'] = 'missing'
        with self.assertRaisesRegex(ValueError, 'no unique solved node'):
            build_project(author, self.root/'missing-node', geometry_policy='computed')
        self.assertFalse((self.root/'missing-node').exists())

    def test_occupancy_union_clips_and_deduplicates_and_ignores_surfaces(self):
        texts = [{'id': 'a', 'line_rectangles': [[-10, 20, 30, 10]]},
                 {'id': 'b', 'line_rectangles': [[10, 20, 20, 10]]}]
        elements = [{'id': t['id'], 'type': 'text', 'frame': t['line_rectangles'][0]} for t in texts]
        elements += [{'id': 'background', 'type': 'shape', 'frame': [0, 0, 100, 100]},
                     {'id': 'decor', 'type': 'text', 'frame': [0, 0, 100, 100], 'metadata': {'decorative': True}},
                     {'id': 'hidden', 'type': 'text', 'frame': [0, 0, 100, 100], 'opacity': 0}]
        report = _occupancy({'id': 'p'}, {'elements': elements}, texts, (100, 100), None, None)
        self.assertEqual(report['allocated_fraction'], .03)
        self.assertEqual(report['estimated_content_fraction'], .03)
        self.assertEqual(report['estimated_blank_fraction'], .97)

    def test_empty_text_and_paragraph_gaps_are_not_filled_content(self):
        author = text_page()
        author['pages'][0]['layout']['children'][1]['element']['text'] = 'A\n\nB'
        report, _ = self.build(author, 'lines')
        body = next(t for t in report['observations']['text_regions'] if t['id'] == 'body')
        self.assertEqual(len(body['line_rectangles']), 2)
        self.assertLess(rectangle_union_area(body['line_rectangles']), math.prod(body['rectangle'][2:]))
        author['pages'][0]['layout']['children'][1]['element']['text'] = '   '
        report, _ = self.build(author, 'blank')
        self.assertEqual(report['observations']['body_text_block_count'], 0)

    def test_ring_footprint_preserves_hole_and_is_resolution_bounded(self):
        plot = {'x': 0, 'y': 0, 'width': 200, 'height': 200}
        actual = rectangle_union_area(_ring_rectangles(plot, 75))
        expected = math.pi*100**2*(1-.75**2)
        self.assertLess(abs(actual-expected)/expected, .003)
        self.assertLess(actual/(200*200), .35)

    def test_large_few_value_chart_warns_even_with_real_data(self):
        author = chart_story('bar', {'categories': ['A', 'B'], 'series': [{'name': 'n', 'values': [10, 20]}]})
        author['pages'][0]['intent'] = 'analysis'
        report, _ = self.build(author, 'big-chart')
        self.assertIn('large_chart_few_records', {w['code'] for w in report['warnings']})
        occupancy = report['occupancy']
        self.assertEqual(occupancy['status'], 'complete_estimate')
        self.assertLess(occupancy['estimated_content_fraction'], occupancy['allocated_fraction'])
        author['pages'][0]['intent'] = 'cover'
        report, _ = self.build(author, 'big-chart-cover')
        self.assertEqual(report['warnings'], [])

    def test_real_ring_uses_marks_but_reviews_its_larger_component(self):
        author = text_page()
        page = author['pages'][0]
        page['content_diagnostics'] = {'region_node_id': 'body'}
        page['layout']['children'][1]['element'] = {
            'type': 'component', 'component': 'progress-ring',
            'value': 50, 'total': 100, 'label': '参与比例'}
        report, _ = self.build(author, 'ring-component')
        occupancy = report['occupancy']
        self.assertEqual(occupancy['status'], 'complete_estimate')
        self.assertLess(occupancy['known_chart_footprint_fraction'], .15)
        self.assertEqual(occupancy['allocated_fraction'], 1)
        chart = occupancy['charts'][0]
        self.assertEqual(chart['allocation_source'], 'component_frame')
        self.assertEqual(chart['allocation_region_fraction'], 1)
        self.assertIn('large_chart_few_records', {w['code'] for w in report['warnings']})
        self.assertEqual(next(r for r in occupancy['allocation_regions'] if r['kind'] == 'component')['id'], 'body')

    def test_unknown_graphic_is_partial_and_not_counted_as_blank(self):
        scene = {'elements': [{'id': 'photo', 'type': 'image', 'frame': [0, 0, 100, 100]}]}
        report = _occupancy({'id': 'p'}, scene, [], (100, 100), None, None)
        self.assertEqual(report['status'], 'partial')
        self.assertIsNone(report['estimated_content_fraction'])
        self.assertIsNone(report['estimated_blank_fraction'])
        self.assertEqual(report['content_fraction_bounds'], [0., 1.])
        page_report = analyze_page({'id': 'p', 'intent': 'analysis'}, scene,
                                   {'canvas': {'width': 100, 'height': 100}})
        self.assertTrue(page_report['review_required'])
        self.assertIn('measurement_incomplete', {w['code'] for w in page_report['warnings']})
        self.assertNotIn('low_content_occupancy', {w['code'] for w in page_report['warnings']})
        report = _occupancy({'id': 'p'}, None, [], (100, 100), None, None)
        self.assertEqual(report['status'], 'not_assessable')
        self.assertIsNone(report['allocated_fraction'])

    def test_thresholds_are_validated_and_can_control_review(self):
        for config in ({'thresholds': {'low_content_fraction': -1}},
                       {'thresholds': {'few_chart_records': True}}, {'region_node_id': ''},
                       {'thresholds': {'guaranteed_quality': .8}}):
            with self.assertRaises(ValueError):
                validate_page_intent({'id': 'bad', 'content_diagnostics': config})
        author = text_page()
        author['pages'][0]['content_diagnostics'] = {'thresholds': {'low_content_fraction': 0}}
        report, _ = self.build(author, 'no-low-area')
        self.assertNotIn('low_content_occupancy', {w['code'] for w in report['warnings']})
        self.assertIn('limited_analysis_support', {w['code'] for w in report['warnings']})

    def test_rotated_unknown_image_uses_visible_bounds_for_body_region(self):
        # The unrotated image misses the body. Its visible rotated bounds enter it.
        scene = {'elements': [{'id': 'photo', 'type': 'image',
                              'frame': [35, 0, 10, 80], 'rotation': 90}]}
        page = {'id': 'p', 'content_diagnostics': {'region_node_id': 'body'}}
        layout = {'nodes': [{'id': 'body', 'frame': [0, 0, 30, 100]}]}
        report = _occupancy(page, scene, [], (100, 100), layout, None)
        self.assertEqual(report['status'], 'partial')
        self.assertEqual(report['unknown_visual_ids'], ['photo'])
        self.assertIsNone(report['estimated_blank_fraction'])
        self.assertEqual(report['content_fraction_bounds'], [0., .1])
        self.assertEqual(report['unknown_visuals'][0]['frame'], [0., 35., 80., 10.])

    def test_shape_based_data_components_do_not_certify_text_only_coverage(self):
        for component in ('partition', 'comparison'):
            with self.subTest(component=component):
                author = text_page()
                page = author['pages'][0]
                page['content_diagnostics'] = {'region_node_id': 'body'}
                element = {'type': 'component', 'component': component}
                records = [{'id': 'a', 'label': 'A', 'value': 40},
                           {'id': 'b', 'label': 'B', 'value': 60}]
                element.update({'total': 100, 'segments': records} if component == 'partition'
                               else {'rows': records})
                page['layout']['children'][1]['element'] = element
                report, _ = self.build(author, 'shape-data-' + component)
                occupancy = report['occupancy']
                self.assertEqual(occupancy['status'], 'partial')
                self.assertIsNone(occupancy['estimated_content_fraction'])
                self.assertIsNone(occupancy['estimated_blank_fraction'])
                self.assertEqual(occupancy['unknown_visual_ids'], ['body'])
                self.assertGreater(occupancy['known_content_fraction'], 0)
                self.assertEqual(occupancy['content_fraction_bounds'][1], 1)
                self.assertIn('measurement_incomplete', {w['code'] for w in report['warnings']})


if __name__ == '__main__':
    unittest.main()
