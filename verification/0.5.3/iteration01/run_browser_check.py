"""Reproduce the bounded 0.5.3 engineering check; no model execution.

From project/: python verification/0.5.3/run_browser_check.py --output NEW_DIRECTORY
Requires existing Playwright Chromium and pypdf. Never edits an installed package.
"""
from copy import deepcopy
from datetime import datetime, timezone
import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'tools'))
from check_presentation_browser import inspect_deck, settle, active, more_action
from check_report_html_browser import digest, render, write_json, MEASURE


def require(value, message):
    if not value:
        raise AssertionError(message)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    package = ROOT/'skills/how-to-report'
    require(not output.exists() and output.parent.is_dir() and not output.is_relative_to(package), 'new output outside package required')
    output.mkdir()
    receipt = {'scope':'0.5.3 audience/review projection and schedule browser checks',
               'captured_at_utc':datetime.now(timezone.utc).isoformat(), 'model_execution':False,
               'semantic_quality':'not_assessed', 'decks':[], 'errors':[],
               'package_manifest_sha256':digest(package/'bundle-manifest.json')}
    payload = [*sorted((package/'scripts').glob('*.py')), *sorted((package/'assets/report-html').glob('*.js')), *sorted((package/'assets/report-html').glob('*.css'))]
    receipt['implementation_before'] = {p.relative_to(package).as_posix():digest(p) for p in payload}
    try:
        renderer = package/'scripts/report_html.py'
        audience = json.loads((package/'assets/report-html/sample-audience.json').read_text(encoding='utf-8'))
        audience['pages'][0]['limits'].append('INTERNAL_NOTE_ONLY_053')
        for name, plan in [('audience', audience), ('review', {**deepcopy(audience), 'display_mode':'review'})]:
            write_json(output/(name+'-input.json'), plan)
            receipt[name+'_render'] = render(renderer, output/(name+'-input.json'), output/name)
        command = [sys.executable,'-B','-I',str(package/'scripts/report_schedule.py'),'render',
                   str(package/'assets/report-html/sample-schedule.json'),'--views','gantt,outcomes','--output',str(output/'schedule')]
        result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8')
        receipt['schedule_render'] = {'argv':command,'exit_code':result.returncode,'stdout':result.stdout,'stderr':result.stderr}
        require(result.returncode == 0, 'schedule render failed')
        dense = deepcopy(audience)
        dense['pages'] = dense['pages'][:1]
        dense['pages'][0].pop('backup_links')
        dense_text = 'Important authored condition must remain complete. '*450
        dense['pages'][0]['elements'][0]['body'] = dense_text
        write_json(output/'overflow-input.json', dense)
        receipt['overflow_render'] = render(renderer, output/'overflow-input.json', output/'overflow')
        from playwright.sync_api import sync_playwright
        from pypdf import PdfReader
        with sync_playwright() as p:
            browser = p.chromium.launch()
            receipt['browser'] = {'name':'Chromium','version':browser.version}
            try:
                for name in ('audience','review','schedule'):
                    inspect_deck(browser, name, output/name, receipt, False, False)
                page = browser.new_page(viewport={'width':1600,'height':1000}, offline=True)
                errors = []
                page.on('pageerror', lambda e: errors.append(str(e)))
                page.goto((output/'audience/index.html').as_uri()); settle(page)
                require(page.locator('.page-footer,.element-footer,.source-marker').count() == 0, 'automatic audience notes remain')
                origin = active(page)
                page.locator('.slide.active [data-backup-target]').click(); settle(page)
                require(active(page) != origin and page.locator('#next').is_disabled(), 'Backup missing without footer')
                page.locator('#backup-return').click(); settle(page)
                require(active(page) == origin, 'Backup return lost origin')
                page.locator('#contents-toggle').click(); page.keyboard.press('Escape'); settle(page)
                require(page.evaluate('document.activeElement.id') == 'contents-toggle', 'directory focus')
                page.locator('#notes-toggle').click(); settle(page)
                require(page.locator('#notes-panel').is_visible() and '参与人员' in page.locator('#notes-text').inner_text(), 'speaker notes unavailable')
                page.locator('#notes-close').click(); settle(page)
                page.locator('#fullscreen').click(); settle(page)
                fullscreen = page.evaluate('!!document.fullscreenElement')
                require(fullscreen, 'fullscreen control failed')
                page.evaluate('document.exitFullscreen()'); settle(page)
                receipt['audience_controls'] = {'backup_return':True,'directory_focus':True,'speaker_notes':True,'fullscreen':fullscreen}
                pdf_text = lambda file: '\n'.join(p.extract_text() or '' for p in PdfReader(file).pages)
                require('INTERNAL_NOTE_ONLY_053' not in pdf_text(output/'audience/deck.pdf'), 'ordinary audience PDF leaked author note')
                require('INTERNAL_NOTE_ONLY_053' in pdf_text(output/'audience/deck-with-sources.pdf'), 'appendix PDF lost author note')
                require('INTERNAL_NOTE_ONLY_053' in pdf_text(output/'review/deck.pdf'), 'review PDF no longer preserves notes')
                receipt['pdf_projection'] = {'audience_excludes_note':True,'audience_appendix_retains_note':True,'review_retains_note':True}
                page.goto((output/'schedule/index.html').as_uri()); settle(page)
                spec = json.loads((package/'assets/report-html/sample-schedule.json').read_text(encoding='utf-8'))
                texts = page.locator('.slide').all_text_contents()
                require(all('截至' in value and '状态日:' not in value for value in texts), 'audience schedule context not projected')
                for task in spec['tasks']:
                    if task.get('condition'): require(task['condition'] in texts[0], 'gantt lost business condition')
                    for field in ('result','criteria','scope'):
                        if task.get('acceptance',{}).get(field): require(task['acceptance'][field] in texts[1], 'outcomes lost acceptance '+field)
                receipt['schedule_business_fields'] = {'conditions_preserved':True,'acceptance_result_criteria_scope_preserved':True}
                page.goto((output/'overflow/index.html').as_uri()); settle(page)
                issues = page.evaluate('reportDeck.inspectLayout().issues')
                measured = page.evaluate(MEASURE)
                require(issues and any(e['outsideSlide'] or e['textOutsideSlide'] or e['scrollHeight'] > e['clientHeight']+2 for s in measured for e in s['elements']), 'footless overfull content falsely passed')
                page.screenshot(path=str(output/'overflow/detected.png'))
                more_action(page, '#read-all')
                require(page.locator('#element-trial-request .element-header p').text_content() == dense_text, 'read-all lost overfull authored text')
                receipt['overflow_negative'] = {'issues':issues,'dom':measured,'full_text_preserved':True}
                require(not errors, 'runtime script errors')
                receipt['control_probe_script_errors'] = errors
                page.close()
            finally:
                browser.close()
        receipt['implementation_after'] = {p.relative_to(package).as_posix():digest(p) for p in payload}
        require(receipt['implementation_before'] == receipt['implementation_after'], 'package changed while checking')
    except Exception as error:
        receipt['errors'].append(type(error).__name__+': '+str(error))
    receipt['passed'] = not receipt['errors']
    receipt['evidence_files'] = {p.relative_to(output).as_posix():digest(p) for p in output.rglob('*') if p.is_file()}
    write_json(output/'browser-receipt.json', receipt)
    print(json.dumps({'passed':receipt['passed'],'errors':receipt['errors'],'receipt':str(output/'browser-receipt.json')}))
    return 0 if receipt['passed'] else 1


if __name__ == '__main__':
    sys.exit(main())
