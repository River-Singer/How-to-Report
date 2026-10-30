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

    def test_audience_moves_annotations_but_preserves_authored_condition_and_sources(self):
        self.plan['display_mode'] = 'audience'
        page = self.plan['pages'][0]
        page['limits'] = ['Author note <script>alert(1)</script> & provenance.']
        page['elements'][0]['limits'] = ['Keep this exact note in details.']
        self.write(); self.run_cli()
        html = (self.output/'index.html').read_text(encoding='utf-8')
        stage = html.split('<main id="deck"')[1].split('</main>')[0]
        for marker in ('page-footer', 'element-footer', 'source-marker', 'Author note', 'Keep this exact note'):
            self.assertNotIn(marker, stage)
        self.assertIn('Confirm the responsible owner before committing a date.', stage)
        self.assertIn('&lt;script&gt;alert(1)&lt;/script&gt; &amp; provenance.', html)
        self.assertIn('Keep this exact note in details.', html)
        self.assertIn('id="page-sources"', html)
        mapping = json.loads((self.output/'page-map.json').read_text(encoding='utf-8'))
        self.assertEqual(mapping['display_mode'], 'audience')
        entries = mapping['elements']
        for owner, original in (('decision', page), ('request', page['elements'][0])):
            entry = next(e for e in entries if e['selector'] == ('#page-' if owner == 'decision' else '#element-')+owner)
            self.assertNotIn('limits', entry['displayed'])
            self.assertEqual(entry['annotations']['limits'], original['limits'])
            self.assertEqual(entry['annotations']['selector'], f'#sources-decision [data-annotation-owner="{owner}"]')
            self.assertEqual(entry['refs'], [self.ref])
        self.assertEqual(next(e for e in entries if e['selector'] == '#page-decision')['source_details']['refs'], [self.ref])
        self.assertEqual(json.loads((self.output/'plan.json').read_text(encoding='utf-8')), self.plan)

    def test_audience_empty_sources_still_have_details_and_backup_actions(self):
        self.plan['display_mode'] = 'audience'
        page = self.plan['pages'][0]
        page['refs'] = []; page['elements'][0]['refs'] = []
        backup = deepcopy(page)
        backup['id'] = 'backup'; backup['elements'][0]['id'] = 'backup-copy'
        backup['tree'] = {'element': 'backup-copy'}
        self.plan['pages'].append(backup)
        self.plan['main_path'] = ['decision']
        page['backup_links'] = [{'target': 'backup', 'label': 'Read the details'}]
        self.write(); self.run_cli()
        html = (self.output/'index.html').read_text(encoding='utf-8')
        stage = html.split('<main id="deck"')[1].split('</main>')[0]
        self.assertIn('class="page-actions backup-links"', stage)
        self.assertIn('data-backup-target="backup"', stage)
        self.assertNotIn('page-footer', stage)
        self.assertIn('id="sources-decision"', html)
        self.assertIn('id="sources-backup"', html)
        self.assertIn('No approved date.', html)

    def test_audience_reference_collection_does_not_emit_markers(self):
        source = self.helper().PageSources(self.plan['pages'][0], 'en', audience=True)
        self.assertEqual(source([self.ref]), '')
        self.assertEqual(source([]), '')
        self.assertEqual(source.references, [self.ref])
        self.assertIn('original-record@2', source.render())

    def test_review_is_identical_to_omitted_mode_and_rejects_invalid_modes(self):
        helper = self.helper()
        original_html, original_mapping = helper.render_document(self.plan)
        review = deepcopy(self.plan); review['display_mode'] = 'review'
        helper.validate(review)
        self.assertEqual(helper.render_document(review), (original_html, original_mapping))
        for invalid in (None, False, 1, {}, [], '', 'hide', 'AUDIENCE'):
            bad = deepcopy(self.plan); bad['display_mode'] = invalid
            with self.subTest(value=invalid), self.assertRaises(ValueError): helper.validate(bad)
        for mode in ('audience', 'review'):
            bad = deepcopy(self.plan); bad['page_plan_version'] = '0.1'; bad['display_mode'] = mode
            with self.subTest(legacy=mode), self.assertRaises(ValueError): helper.validate(bad)

    def test_audience_sample_runs_without_checkout_dependencies(self):
        self.plan = json.loads((self.package/'assets/report-html/sample-audience.json').read_text(encoding='utf-8'))
        self.write(); self.run_cli(isolated=True)
        html = (self.output/'index.html').read_text(encoding='utf-8')
        stage = html.split('<main id="deck"')[1].split('</main>')[0]
        self.assertNotIn('class="page-footer"', stage)
        self.assertNotIn('制作记录', stage)
        self.assertIn('参与人员确认后，才能确定开始时间。', stage)

    def test_schedule_context_moves_to_details_without_hiding_conditions_or_results(self):
        from test_report_schedule import core
        spec = json.loads((self.package/'assets/report-html/sample-schedule.json').read_text(encoding='utf-8'))
        self.plan = core.to_plan(spec, ['gantt', 'outcomes', 'milestones'])
        self.assertTrue(all('body' not in p['elements'][0] for p in self.plan['pages']))
        self.write(); self.run_cli(isolated=True)
        html = (self.output/'index.html').read_text(encoding='utf-8')
        mapping = json.loads((self.output/'page-map.json').read_text(encoding='utf-8'))['elements']
        stage = html.split('<main id="deck"')[1].split('</main>')[0]
        for hidden in ('日终边界', 'B1@1', spec['limits'][0], 'source-marker'):
            self.assertNotIn(hidden, stage)
        self.assertIn('截至 2026-10-28', stage)
        self.assertIn('实际 2026-10-06', stage)
        self.assertIn('预计 2026-11-03', stage)
        self.assertIn('预计: 2026-11-13', stage)
        self.assertIn('完成日期 / 较原计划', stage)
        self.assertNotIn('class="schedule-date-text"', stage)
        legend = stage.split('<p class="schedule-legend">')[1].split('</p>')[0]
        self.assertEqual(legend, '<span class="legend-baseline">原计划</span><span class="legend-actual">实际</span><span class="legend-forecast">预计</span>')
        self.assertNotIn('经过区间不等于工作量', stage)
        business_row = stage.split('id="schedule-schedule-gantt-1-view-business"')[1].split('</tr>')[0]
        self.assertNotIn('<small>未知</small>', business_row.split('</th>')[0])
        for task in spec['tasks']:
            if task.get('condition'):
                self.assertIn(task['condition'], stage)
            if task.get('progress'):
                self.assertIn(task['progress']['basis'], stage)
            for field in ('result', 'criteria', 'scope'):
                if field in task.get('acceptance', {}):
                    self.assertIn(task['acceptance'][field], stage)
        appendix = html.split('id="source-appendices"')[1].split('<dialog')[0]
        self.assertIn('自然日，日终边界', appendix)
        self.assertIn('批准基线: B1@1', appendix)
        self.assertIn(spec['limits'][0], appendix)
        self.assertIn('经过区间不等于工作量；点仅表示已知日期。', appendix)
        for task in spec['tasks']:
            entry = next(e for e in mapping if e.get('datum_id') == 'schedule-gantt-1-view-'+task['id'])
            dates = ' · '.join(f'{label}: {task.get(key, {}).get("start", "未知")} → {task.get(key, {}).get("finish", "未知")}'
                               for key, label in (('baseline', '基线'), ('actual', '实际'), ('forecast', '预计')))
            self.assertEqual(entry['date_details']['text'], dates)
            self.assertEqual(entry['date_details']['selector'], f'#sources-schedule-gantt-1 [data-detail-element="schedule-gantt-1-view-dates-{task["id"]}"]')
            self.assertIn('aria-label="'+dates+'"', stage)
            self.assertIn('<p class="schedule-date-text">'+dates+'</p>', appendix)
            for field in ('baseline', 'actual', 'forecast'):
                self.assertEqual(entry['displayed'].get(field), task.get(field))
        for p in self.plan['pages']:
            eid = p['elements'][0]['id']
            entry = next(e for e in mapping if e['selector'] == '#element-'+eid)
            self.assertNotIn('schedule', entry['displayed'])
            self.assertEqual(entry['semantic']['schedule']['spec'], spec)
            self.assertEqual(entry['displayed']['as_of'], spec['as_of'])
            page = next(e for e in mapping if e['selector'] == '#page-'+p['id'])
            self.assertIn(eid+'-context', page['source_details']['detail_elements'])
        self.plan['display_mode'] = 'review'; self.output = self.root/'review'
        self.write(); self.run_cli(isolated=True)
        review_html = (self.output/'index.html').read_text(encoding='utf-8')
        review_stage = review_html.split('<main id="deck"')[1].split('</main>')[0]
        self.assertIn('自然日，日终边界', review_stage)
        self.assertIn('批准基线: B1@1', review_stage)
        self.assertIn(spec['limits'][0], review_stage)
        self.assertEqual(review_stage.count('class="schedule-date-text"'), len(spec['tasks']))
        self.assertIn('当前完成日 / 偏差', review_stage)
        self.assertIn('经过区间不等于工作量；点仅表示已知日期。', review_stage)
        business_row = review_stage.split('id="schedule-schedule-gantt-1-view-business"')[1].split('</tr>')[0]
        self.assertIn('<small>未知</small>', business_row.split('</th>')[0])
        self.plan.pop('display_mode'); self.output = self.root/'omitted'
        self.write(); self.run_cli(isolated=True)
        self.assertEqual((self.output/'index.html').read_text(encoding='utf-8'), review_html)


if __name__ == '__main__':
    unittest.main()
