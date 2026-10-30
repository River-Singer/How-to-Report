"""Audience projection preserves evidence without forcing it onto the canvas."""
from copy import deepcopy
import json
from html.parser import HTMLParser
import unittest

import test_report_html as legacy


class DisplayProjectionTests(unittest.TestCase):
    helper = legacy.ReportHTMLTests.helper
    write = legacy.ReportHTMLTests.write
    run_cli = legacy.ReportHTMLTests.run_cli

    def setUp(self):
        legacy.ReportHTMLTests.setUp(self)
        self.ref = {'id': 'original-record', 'revision': 2, 'locator': 'full locator <not markup>'}
        self.plan = {'page_plan_version': '0.2', 'title': 'Synthetic projection', 'language': 'en',
                     'pages': [{'id': 'decision', 'layout': 'composed', 'title': 'Approve a conditional trial',
                                'question': 'What is required?', 'takeaway': 'Approval is pending.',
                                'limits': ['Synthetic exercise; resource approval remains pending.'],
                                'refs': [self.ref], 'elements': [
                                    {'id': 'request', 'type': 'text', 'role': 'primary',
                                     'body': 'Confirm the responsible owner before committing a date.',
                                     'refs': [self.ref], 'limits': ['No approved date.']}],
                                'tree': {'element': 'request'}}]}

    def test_optional_heading_and_body_do_not_generate_filler(self):
        self.write(); self.run_cli()
        html = (self.output/'index.html').read_text(encoding='utf-8')
        stage = html.split('<main id="deck"')[1].split('</main>')[0]
        self.assertNotIn('<h2>', stage)
        self.assertIn('Confirm the responsible owner', stage)
        self.assertIn('No approved date.', stage)
        self.assertIn('resource approval remains pending.', stage)
        class VisibleText(HTMLParser):
            def __init__(self): super().__init__(); self.parts = []
            def handle_data(self, data): self.parts.append(data)
        visible = VisibleText(); visible.feed(stage)
        self.assertNotIn('full locator', ''.join(visible.parts))
        appendix = html.split('id="source-appendices"')[1].split('<dialog')[0]
        self.assertEqual(appendix.count('full locator &lt;not markup&gt;'), 1)
        self.assertIn('original-record@2', appendix)
        mapping = json.loads((self.output/'page-map.json').read_text(encoding='utf-8'))['elements']
        page = next(item for item in mapping if item['selector'] == '#page-decision')
        self.assertEqual(page['source_details']['refs'], [self.ref])
        self.assertEqual(page['source_details']['selector'], '#sources-decision')

    def test_supplied_descriptions_preserved_and_empty_text_rejected(self):
        element = self.plan['pages'][0]['elements'][0]
        element['title'] = 'Distinct information'; element['body'] = 'Do not silently remove this qualification.'
        self.write(); self.run_cli()
        html = (self.output/'index.html').read_text(encoding='utf-8')
        self.assertIn(element['title'], html); self.assertIn(element['body'], html)
        helper = self.helper()
        for value in ('', '  ', None, 0):
            bad = deepcopy(self.plan); bad['pages'][0]['elements'][0]['body'] = value
            with self.subTest(value=value), self.assertRaises(ValueError): helper.validate(bad)
        element.pop('title'); element.pop('body')
        with self.assertRaises(ValueError): helper.validate(self.plan)

    def test_metric_must_identify_number_even_when_body_omitted(self):
        element = self.plan['pages'][0]['elements'][0]
        element.update(type='metric', title='Natural days', value=13, unit='days')
        element.pop('body')
        self.helper().validate(self.plan)
        element.pop('title')
        with self.assertRaises(ValueError): self.helper().validate(self.plan)

    def test_legacy_still_requires_both_fields(self):
        self.plan['page_plan_version'] = '0.1'
        with self.assertRaises(ValueError): self.helper().validate(self.plan)

    def test_ref_numbers_shared_across_page_and_element_exact_versions(self):
        source = self.helper().PageSources(self.plan['pages'][0], 'en')
        a = source([self.ref])
        other = {**self.ref, 'revision': 3}
        b = source([other, self.ref])
        self.assertIn('[1]', a); self.assertIn('[2,1]', b)
        self.assertEqual(source.references, [self.ref, other])
        self.assertIn('data-source-page="decision"', a)

    def test_surface_is_bounded_and_does_not_allow_style_code(self):
        element = self.plan['pages'][0]['elements'][0]
        for surface in ('plain', 'panel'):
            element['surface'] = surface
            self.helper().validate(self.plan)
        for surface in ('none', 'plain;display:none', {}, None):
            element['surface'] = surface
            with self.subTest(surface=surface), self.assertRaises(ValueError):
                self.helper().validate(self.plan)


if __name__ == '__main__':
    unittest.main()
