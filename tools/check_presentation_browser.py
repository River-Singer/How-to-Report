#!/usr/bin/env python3
"""Actual offline Chromium checks for presentation 0.2 and ScheduleSpec 0.1.

Development only; requires existing playwright/Chromium and pypdf. Creates a new
evidence directory, never mutates an input/package and never runs a model case.
Use --package for release bytes or --source-root for a detached source snapshot.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from datetime import date, datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

from check_report_html_browser import MEASURE, digest, render, write_json


SVG_BOUNDS = r"""() => [...document.querySelectorAll('.slide.active svg')].map(svg=>{
 const view=svg.viewBox.baseVal, box=svg.getBBox();
 const outside=b=>b.x<view.x-1||b.y<view.y-1||b.x+b.width>view.x+view.width+1||b.y+b.height>view.y+view.height+1;
 return {element:svg.closest('[data-element-id]').dataset.elementId,
 view:{x:view.x,y:view.y,width:view.width,height:view.height},
 box:{x:box.x,y:box.y,width:box.width,height:box.height},outside:outside(box),
 text:[...svg.querySelectorAll('text')].map(t=>({text:t.textContent,outside:outside(t.getBBox())}))};
})"""


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def settle(page):
    page.evaluate("() => document.fonts.ready")
    page.evaluate("() => Promise.all([...document.images].map(i=>i.decode().catch(()=>null)))")
    page.evaluate("() => new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))")


def active(page):
    return page.locator('.slide.active').get_attribute('data-page-id')


def more_action(page, action):
    page.locator('#more-toggle').click()
    page.locator(action).click()
    settle(page)


def source_snapshot(source, destination):
    from package_skills import merge_payloads, source_tree
    payload = merge_payloads('how-to-report', source_tree(source/'how-to-report'), source_tree(source/'shared'))
    for relative, raw in payload.items():
        path = destination/relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
    return {name: hashlib.sha256(raw).hexdigest() for name, raw in payload.items()}


def copy_plan(plan_path, directory):
    """Only copy explicitly declared, bounded child media beside the probe plan."""
    plan = json.loads(plan_path.read_text(encoding='utf-8-sig'))
    directory.mkdir()
    for page in plan['pages']:
        for element in page['elements']:
            if element.get('type') != 'media':
                continue
            for field in ('file', 'poster'):
                item = element['media'].get(field)
                if not item:
                    continue
                relative = Path(item['path'])
                require(not relative.is_absolute() and '..' not in relative.parts and ':' not in str(relative), 'unsafe probe media path')
                source = (plan_path.parent/relative).resolve(strict=True)
                require(source.is_relative_to(plan_path.parent.resolve()), 'probe media escapes input')
                target = directory/relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, target)
    write_json(directory/'plan.json', plan)
    return plan


def check_navigation(page, plan, folder):
    route = plan.get('main_path', [p['id'] for p in plan['pages']])
    page.keyboard.press('Home'); settle(page)
    require(active(page) == route[0] and page.locator('#previous').is_disabled(), 'Home/first boundary')
    page.locator('#next').click(); settle(page)
    require(active(page) == route[1], 'next did not follow main path')
    page.keyboard.press('ArrowLeft'); settle(page)
    require(active(page) == route[0], 'ArrowLeft')
    page.keyboard.press('End'); settle(page)
    require(active(page) == route[-1] and page.locator('#next').is_disabled(), 'End/main-path boundary')
    page.locator('.page-dots button').nth(1).click(); settle(page)
    second = plan['pages'][1]['id']
    require(active(page) == second, 'page dots')
    page.locator('#contents-toggle').click()
    require(page.locator('#contents-dialog').evaluate('(d)=>d.open'), 'directory opens')
    page.keyboard.press('Escape'); settle(page)
    require(page.evaluate('document.activeElement.id') == 'contents-toggle', 'directory focus after Escape')
    page.locator('#contents-toggle').click()
    page.locator('#contents-dialog [data-jump]').first.click(); settle(page)
    require(active(page) == plan['pages'][0]['id'], 'directory selection')
    page.evaluate('(id)=>{location.hash=id}', second); settle(page)
    page.wait_for_function('(id)=>document.querySelector(".slide.active").dataset.pageId===id', arg=second)
    page.reload(); settle(page)
    require(active(page) == second, 'hash reload')
    backup = next((p['id'] for p in plan['pages'] if p['id'] not in route), None)
    if backup:
        page.locator(f'.slide.active [data-backup-target="{backup}"]').click(); settle(page)
        require(active(page) == backup and page.locator('#next').is_disabled(), 'Backup landing')
        page.locator('#backup-return').click(); settle(page)
        require(active(page) == second, 'Backup return lost non-first origin')
        page.goto(page.url.split('#')[0]+'#'+backup); settle(page)
        page.locator('#backup-return').click(); settle(page)
        require(active(page) == route[0], 'direct Backup hash fallback')
    page.keyboard.press('Home'); settle(page)
    if page.locator('#notes-toggle').count():
        page.locator('#notes-toggle').click(); settle(page)
        note = page.locator('#notes-panel').bounding_box()
        slide = page.locator('.slide.active').bounding_box()
        require(slide['x']+slide['width'] <= note['x'], 'notes cover main content on desktop')
        require(plan['pages'][0]['notes'] == page.locator('#notes-text').inner_text(), 'notes content changed')
        page.screenshot(path=str(folder/'notes.png'))
        page.keyboard.press('Escape'); settle(page)
        require(not page.locator('#notes-panel').is_visible(), 'notes Escape')
    page.locator('#fullscreen').click(); settle(page)
    fullscreen = page.evaluate('Boolean(document.fullscreenElement)')
    if fullscreen:
        page.locator('#fullscreen').click(); settle(page)
        require(not page.evaluate('Boolean(document.fullscreenElement)'), 'fullscreen exit')
    else:
        require(bool(page.locator('#control-status').inner_text()), 'fullscreen unavailable without status')
    return {'fullscreen_entered': fullscreen, 'unavailable_status': page.locator('#control-status').inner_text(), 'backup_origin':second}


def inspect_deck(browser, name, folder, receipt, navigation=False, video=False):
    plan = json.loads((folder/'plan.json').read_text(encoding='utf-8-sig'))
    ctx = browser.new_context(viewport={'width':1600,'height':1000}, device_scale_factor=1, offline=True)
    page = ctx.new_page()
    errors, requests = [], []
    page.on('pageerror', lambda e: errors.append(str(e)))
    page.on('request', lambda r: requests.append(r.url) if r.url.startswith(('http:', 'https:')) else None)
    record = {'name':name, 'html_sha256':digest(folder/'index.html'), 'checks':[], 'script_errors':errors, 'network_requests':requests}
    receipt['decks'].append(record)
    try:
        page.goto((folder/'index.html').as_uri(), wait_until='load'); settle(page)
        record['initial_state']=page.evaluate('({page:document.querySelector(".slide.active").dataset.pageId,hash:location.hash,mode:document.body.className,counter:document.querySelector("#page-number").value})')
        initial_page=plan.get('main_path',[p['id'] for p in plan['pages']])[0]
        require(record['initial_state']['hash']=='' and record['initial_state']['page']==initial_page, 'fresh no-hash navigation did not start at the first main-path page')
        require('deck-mode' in record['initial_state']['mode'] and 'reading-mode' not in record['initial_state']['mode'], 'fresh load restored an unexpected reading state')
        for viewport in ({'width':1600,'height':1000}, {'width':1280,'height':800}, {'width':390,'height':844}):
            page.set_viewport_size(viewport); settle(page)
            current = {'viewport':page.evaluate('({width:innerWidth,height:innerHeight})'), 'pages':[]}
            for i, definition in enumerate(plan['pages']):
                page.evaluate('(i)=>reportDeck.goTo(i)', i); settle(page)
                dom = page.evaluate(MEASURE)
                geometry = page.evaluate('reportDeck.inspectLayout()')
                svg = page.evaluate(SVG_BOUNDS)
                own_issues = [e for s in dom for e in s['elements'] if e['outsideSlide'] or e['textOutsideSlide']]
                current['pages'].append({'id':definition['id'], 'dom':dom, 'svg':svg, 'geometry_issues':geometry['issues'], 'independent_issues':own_issues})
                if geometry['issues'] or own_issues or any(s['outside'] or any(t['outside'] for t in s['text']) for s in svg):
                    receipt['errors'].append(f'{name}/{viewport["width"]}/{definition["id"]}: geometry or SVG overflow (see measurements)')
                require(active(page) == definition['id'], 'page activation')
                box = dom[0]['rect']
                require(box['x'] >= -2 and box['y'] >= -2 and box['right'] <= viewport['width']+2 and box['bottom'] <= viewport['height']+2, 'stage outside viewport')
                require(page.locator('.slide.active h1').count() == 1, 'single title')
                if viewport['width'] == 1600:
                    page.screenshot(path=str(folder/f'page-{i+1:02}.png'))
            record['checks'].append(current)
        page.set_viewport_size({'width':1600,'height':1000}); settle(page)
        ids = page.locator('[id]').evaluate_all('(els)=>els.map(e=>e.id)')
        require(len(ids) == len(set(ids)), 'duplicate DOM/SVG id')
        images = page.locator('img:not(.video-print-poster)').evaluate_all('(els)=>els.map(i=>({loaded:i.complete&&i.naturalWidth>0,width:i.naturalWidth,height:i.naturalHeight}))')
        require(all(i['loaded'] for i in images), 'image decoder failed')
        annotations = []
        for i, definition in enumerate(plan['pages']):
            page.evaluate('(i)=>reportDeck.goTo(i)', i); settle(page)
            for e in definition['elements']:
                if e.get('type') == 'media' and e['media']['kind'] == 'image':
                    bounds = page.locator(f'#element-{e["id"]} .image-frame').evaluate('(e)=>{const a=e.getBoundingClientRect(),b=e.querySelector("img").getBoundingClientRect();return {dx:a.x-b.x,dy:a.y-b.y,dw:a.width-b.width,dh:a.height-b.height,annotations:[...e.querySelectorAll(".image-annotation")].map(x=>{const r=x.getBoundingClientRect();return {x:100*(r.x-b.x)/b.width,y:100*(r.y-b.y)/b.height,width:100*r.width/b.width,height:100*r.height/b.height}})}}')
                    require(all(abs(bounds[k]) < 1 for k in ('dx','dy','dw','dh')), 'annotation frame differs from actual image pixels')
                    for expected, actual in zip(e['media'].get('annotations', []), bounds['annotations']):
                        require(all(abs(expected[k]-actual[k]) < .1 for k in ('x','y','width','height')), 'annotation changed source-relative position')
                    annotations.append(bounds)
        record['images'], record['annotations'] = images, annotations
        if navigation:
            record['navigation'] = check_navigation(page, plan, folder)
        if video:
            page.evaluate('reportDeck.goTo(0)'); settle(page)
            playback = page.locator('video').evaluate('async v=>{v.muted=true;await v.play();await new Promise(r=>setTimeout(r,250));return {time:v.currentTime,paused:v.paused,ready:v.readyState,width:v.videoWidth,height:v.videoHeight,error:v.error}}')
            require(playback['time'] > 0 and not playback['paused'] and playback['error'] is None, 'video playback failed')
            page.locator('#next').click(); settle(page)
            require(page.locator('video').evaluate('(v)=>v.paused'), 'video not paused on leaving page')
            record['video'] = playback
        # True narrow viewport; full text and wide relation/table containers remain reachable.
        page.set_viewport_size({'width':390,'height':844}); settle(page)
        more_action(page, '#read-all')
        require(page.locator('.slide:visible').count() == len(plan['pages']), 'read-all missing pages')
        require(page.evaluate('document.documentElement.scrollWidth <= innerWidth+1'), 'read-all causes document-wide horizontal overflow')
        scrolling = page.locator('.chart-content,.structured-table,.diagram-content,.schedule-content').evaluate_all('''els=>els.map(e=>{const previous=e.scrollLeft;e.scrollLeft=e.scrollWidth;const r={kind:e.className,width:e.clientWidth,scrollWidth:e.scrollWidth,maximum:e.scrollLeft};e.scrollLeft=previous;return r})''')
        require(all(e['scrollWidth'] <= e['width']+1 or e['maximum'] > 0 for e in scrolling), 'wide contents cannot be horizontally reached')
        # The SVG line and HTML point values must share one horizontal coordinate system.
        line_alignment = page.locator('.chart-line').evaluate_all('''els=>els.map(e=>{e.scrollLeft=e.scrollWidth;const svg=e.querySelector('svg'),t=e.querySelector('table');return {svgWidth:svg.getBoundingClientRect().width,tableWidth:t.getBoundingClientRect().width,deltas:[...svg.querySelectorAll('[data-point-id]')].map(p=>{const a=p.getBoundingClientRect(),b=t.querySelector('#datum-'+p.dataset.pointId).getBoundingClientRect();return Math.abs(a.x+a.width/2-b.x-b.width/2)})}})''')
        require(all(abs(e['svgWidth']-e['tableWidth'])<1 and all(d<2 for d in e['deltas']) for e in line_alignment), 'line/value correspondence lost in mobile read-all')
        for definition in plan['pages']:
            page.locator('#page-'+definition['id']).scroll_into_view_if_needed()
            page.screenshot(path=str(folder/'mobile-{}.png'.format(definition['id'])))
        record['reading'] = {'actual_viewport':page.evaluate('({width:innerWidth,height:innerHeight})'), 'scrolling':scrolling, 'line_alignment':line_alignment, 'scaled_deck_readability':'not_asserted'}
        page.evaluate('reportDeck.inspectLayout()'); settle(page)
        require(page.locator('.slide:visible').count() == len(plan['pages']), 'inspectLayout fails to restore reading mode')
        # PDF runs real beforeprint/afterprint handlers, not CSS emulation alone.
        page.set_viewport_size({'width':1600,'height':1000}); settle(page)
        page.pdf(path=str(folder/'deck.pdf'), print_background=True, prefer_css_page_size=True)
        from pypdf import PdfReader
        pdf = PdfReader(folder/'deck.pdf')
        require(len(pdf.pages) == len(plan['pages']), 'PDF physical page count differs')
        canvas = plan.get('canvas', {'width':1600,'height':900})
        require(all(abs(float(p.mediabox.width)-canvas['width']*.75)<1 and abs(float(p.mediabox.height)-canvas['height']*.75)<1 for p in pdf.pages), 'PDF canvas dimensions')
        require(page.locator('#read-all').get_attribute('aria-pressed') == 'true', 'print did not restore read-all')
        page.emulate_media(media='print'); settle(page)
        require(not page.locator('.toolbar').is_visible(), 'print includes toolbar')
        if video:
            require(not page.locator('video').is_visible() and page.locator('.video-print-poster').is_visible(), 'print video poster absent')
            require(bool(pdf.pages[0].images), 'PDF contains no embedded poster image')
        record['pdf'] = {'pages':len(pdf.pages), 'sha256':digest(folder/'deck.pdf'), 'media_box_points':[float(pdf.pages[0].mediabox.width),float(pdf.pages[0].mediabox.height)], 'poster_verified':video}
        require(not errors and not requests, 'script errors or network requests')
    except Exception as exc:
        receipt['errors'].append(f'{name}: {type(exc).__name__}: {exc}')
        page.screenshot(path=str(folder/'failure.png'), full_page=False)
    finally:
        ctx.close()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--package', type=Path)
    group.add_argument('--source-root', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--video-plan', type=Path)
    parser.add_argument('--skip-schedule', action='store_true', help='presentation iteration only; receipt records schedule was skipped')
    args = parser.parse_args(argv)
    output = args.output.resolve()
    require(not output.exists() and output.parent.is_dir(), 'output must be a new directory with an existing parent')
    source = (args.package or args.source_root).resolve(strict=True)
    require(not output.is_relative_to(source), 'evidence must be outside input package/source')
    output.mkdir()
    receipt = {'scope':'deterministic_synthetic_engineering_browser_checks_only', 'captured_at_utc':datetime.now(timezone.utc).isoformat(), 'model_execution':False, 'semantic_quality':'not_assessed', 'schedule_skipped':args.skip_schedule, 'decks':[], 'errors':[]}
    try:
        package = args.package.resolve() if args.package else output/'source-snapshot'
        if args.source_root:
            receipt['source_snapshot_sha256'] = source_snapshot(source, package)
        manifest=package/'bundle-manifest.json'
        receipt['package_manifest_sha256']=digest(manifest) if manifest.is_file() else None
        renderer = package/'scripts/report_html.py'
        assets = package/'assets/report-html'
        implementation=[*sorted((package/'scripts').glob('*.py')), *sorted(assets.glob('*.js')), *sorted(assets.glob('*.css'))]
        receipt['implementation_before']={p.relative_to(package).as_posix():digest(p) for p in implementation}
        advanced = copy_plan(assets/'sample-advanced.json', output/'advanced-input')
        advanced['pages'][1]['backup_links'] = deepcopy(advanced['pages'][0]['backup_links'])
        write_json(output/'advanced-input/plan.json', advanced)
        receipt['advanced_render'] = render(renderer, output/'advanced-input/plan.json', output/'advanced')
        plans = [('advanced', True, False)]
        sample = json.loads((assets/'sample-plan.json').read_text(encoding='utf-8-sig'))
        chart = next(deepcopy(e) for p in sample['pages'] for e in p['elements'] if e.get('type')=='chart' and e['chart']['kind']=='line')
        chart_plan = deepcopy(advanced); chart_plan.pop('main_path')
        chart_plan['pages'] = [deepcopy(advanced['pages'][0])]
        chart_page = chart_plan['pages'][0]; chart_page.pop('backup_links'); chart_page.pop('notes')
        chart_page['title'] = '合成图表：缺失保留与窄屏对应'; chart_page['elements']=[chart]; chart_page['tree']={'element':chart['id']}
        write_json(output/'line-plan.json', chart_plan)
        receipt['line_render'] = render(renderer, output/'line-plan.json', output/'line')
        plans.append(('line', False, False))
        if args.video_plan:
            copy_plan(args.video_plan.resolve(strict=True), output/'video-input')
            receipt['video_render'] = render(renderer, output/'video-input/plan.json', output/'video')
            plans.append(('video', False, True))
        if not args.skip_schedule:
            command=[sys.executable,'-B','-I',str(package/'scripts/report_schedule.py'),'render',str(assets/'sample-schedule.json'),'--views','summary,gantt,milestones,outcomes,drift','--output',str(output/'schedule')]
            result=subprocess.run(command,capture_output=True,text=True,encoding='utf-8')
            receipt['schedule_render']={'argv':command,'exit_code':result.returncode,'stdout':result.stdout,'stderr':result.stderr}
            require(result.returncode == 0, 'schedule render failed')
            plans.append(('schedule', False, False))
        from playwright.sync_api import sync_playwright
        with sync_playwright() as engine:
            browser=engine.chromium.launch(headless=True)
            receipt['browser']={'name':'Chromium','version':browser.version}
            try:
                for name, navigation, video in plans:
                    inspect_deck(browser, name, output/name, receipt, navigation, video)
                if not args.skip_schedule:
                    schedule_boundaries(browser, package, output, receipt)
                negative_checks(browser, renderer, output, advanced, chart_plan, receipt)
                media_boundaries(browser, renderer, output, advanced, receipt)
            finally:
                browser.close()
        receipt['implementation_after']={p.relative_to(package).as_posix():digest(p) for p in implementation}
        require(receipt['implementation_before']==receipt['implementation_after'], 'implementation changed during browser probe; rerun stable bytes')
    except Exception as exc:
        receipt['errors'].append(f'{type(exc).__name__}: {exc}')
    receipt['passed']=not receipt['errors']
    receipt['evidence_files']={p.relative_to(output).as_posix():digest(p) for p in output.rglob('*') if p.is_file() and 'source-snapshot' not in p.parts}
    write_json(output/'browser-receipt.json',receipt)
    print(json.dumps({'passed':receipt['passed'],'errors':receipt['errors'],'receipt':str(output/'browser-receipt.json')},ensure_ascii=True))
    return 0 if receipt['passed'] else 1


def negative_checks(browser, renderer, output, advanced, chart_plan, receipt):
    base=deepcopy(advanced); base.pop('main_path'); base['pages']=base['pages'][:1]; base['pages'][0].pop('backup_links')
    dense=deepcopy(base); dense['pages'][0]['elements'][0]['body']='重要条件必须完整保留，不能裁剪掩盖。'*200
    label=deepcopy(chart_plan)
    label['pages'][0]['elements'][0]['chart']['x_labels'][0]='不可截掉的真实长中文分类标签'*30
    hostile=deepcopy(base); hostile['pages'][0]['elements'][0]['body']='<img src="https://example.invalid/unsafe" onerror="window.__ATTACKED__=1"><script>window.__ATTACKED__=1</script>'
    ctx=browser.new_context(viewport={'width':1280,'height':800},offline=True)
    page=ctx.new_page()
    try:
        for name, plan in (('dense',dense),('long-label',label),('hostile',hostile)):
            path=output/(name+'-plan.json');write_json(path,plan)
            render(renderer,path,output/name)
            page.goto((output/name/'index.html').as_uri());settle(page)
            issues=page.evaluate('reportDeck.inspectLayout().issues')
            if name == 'hostile':
                require(page.evaluate('window.__ATTACKED__===undefined') and page.locator('img').count()==0, 'markup injection')
                require('<img src=' in page.locator('.slide.active').inner_text(), 'hostile text not preserved literally')
            else:
                require(bool(issues) and page.locator('#layout-warning').is_visible(), name+' negative fixture escaped layout detection')
                page.screenshot(path=str(output/name/'overflow.png'))
                more_action(page,'#read-all')
                text=page.locator('.slide').inner_text()
                original=plan['pages'][0]['elements'][0]['body'] if name=='dense' else plan['pages'][0]['elements'][0]['chart']['x_labels'][0]
                require(original in text, name+' read-all lost content')
            receipt.setdefault('negative_checks',[]).append({'name':name,'issues':issues,'passed':True})
    finally:
        ctx.close()


def media_boundaries(browser, renderer, output, advanced, receipt):
    """Preflight is a byte/signature check; real decoder rejection remains separate."""
    plan=deepcopy(advanced); plan.pop('main_path')
    plan['pages']=[next(p for p in plan['pages'] if any(e.get('type')=='media' for e in p['elements']))]
    directory=output/'media-boundaries'; directory.mkdir()
    shutil.copyfile(output/'advanced-input/sample-media.png', directory/'sample-media.png')
    evidence=[]
    for name, transform in (
        ('wrong-hash', lambda m:m['file'].update(sha256='0'*64)),
        ('remote-media', lambda m:m['file'].update(path='https://example.invalid/picture.png')),
        ('raw-svg', lambda m:m.update(svg='<svg onload="alert(1)"></svg>')),
    ):
        bad=deepcopy(plan); transform(bad['pages'][0]['elements'][0]['media'])
        path=directory/(name+'.json'); write_json(path,bad)
        command=[sys.executable,'-B','-I',str(renderer),'render',str(path),'--output',str(directory/name)]
        result=subprocess.run(command,capture_output=True,text=True,encoding='utf-8')
        require(result.returncode==2 and not (directory/name).exists(), name+' was not rejected before output')
        evidence.append({'name':name,'exit_code':result.returncode,'stdout':result.stdout,'output_created':False})
    raw=b'\x89PNG\r\n\x1a\nnot a complete encoded image'
    (directory/'header-only.png').write_bytes(raw)
    plan['pages'][0]['elements'][0]['media']['file']={'path':'header-only.png','sha256':hashlib.sha256(raw).hexdigest()}
    write_json(directory/'header-only.json',plan)
    render(renderer,directory/'header-only.json',directory/'header-only')
    render_receipt=json.loads((directory/'header-only/render-receipt.json').read_text(encoding='utf-8'))
    require(render_receipt['browser_validation']=='not_run', 'signature check claimed browser pass')
    page=browser.new_page(viewport={'width':1280,'height':800})
    try:
        page.goto((directory/'header-only/index.html').as_uri()); settle(page)
        result=page.locator('.media-content img').evaluate('async i=>{try{await i.decode();return {decoded:true,width:i.naturalWidth}}catch(e){return {decoded:false,width:i.naturalWidth,error:e.name}}}')
        require(not result['decoded'] and result['width']==0, 'corrupt image unexpectedly decoded')
        evidence.append({'name':'signature_is_not_decode','renderer_browser_validation':'not_run','actual_decoder':result,'expected_decode_failure':True})
    finally:
        page.close()
    receipt['media_boundaries']=evidence


def schedule_boundaries(browser, package, output, receipt):
    """Independent date/identity oracles and bounded capacity counterexamples."""
    canonical=json.loads((package/'assets/report-html/sample-schedule.json').read_text(encoding='utf-8-sig'))
    directory=output/'schedule-boundaries';directory.mkdir()
    def shift(value):
        if isinstance(value,dict):return {k:shift(v) for k,v in value.items()}
        if isinstance(value,list):return [shift(v) for v in value]
        if isinstance(value,str) and re.fullmatch(r'\d{4}-\d{2}-\d{2}',value):return (date.fromisoformat(value)+timedelta(days=70)).isoformat()
        return value
    crossyear=shift(canonical)
    crossyear['snapshots'][1]['reported_on']=(date.fromisoformat(crossyear['snapshots'][1]['reported_on'])-timedelta(days=1)).isoformat()
    actions=deepcopy(canonical)
    actions['actions']=[{'id':f'probe-action-{i}','text':f'合成协调事项 {i}：核实所需资源','refs':canonical['refs']} for i in range(10)]
    dense=deepcopy(canonical)
    dense['snapshots']=[{**deepcopy(canonical['snapshots'][0]),'reported_on':(date.fromisoformat(canonical['baseline']['approved_on'])+timedelta(days=8+i)).isoformat()} for i in range(8)]
    clustered=deepcopy(canonical)
    for i,snapshot in enumerate(clustered['snapshots'][:3]):
        snapshot['reported_on']=(date.fromisoformat(canonical['snapshots'][0]['reported_on'])+timedelta(days=i)).isoformat()
    unknown=deepcopy(canonical);unknown.pop('baseline');unknown.pop('snapshots')
    for task in unknown['tasks']:task.pop('baseline',None)
    for mark in unknown['milestones']:mark.pop('baseline_date',None)
    unknown['tasks'][0].pop('acceptance',None)
    unknown['tasks'][1]['acceptance']['status']='rejected'
    historical_actual=deepcopy(canonical)
    historical_actual['milestones'][0].pop('forecast_date')
    historical_actual['milestones'][0]['actual_date']=(date.fromisoformat(canonical['as_of'])-timedelta(days=1)).isoformat()
    long=deepcopy(canonical)
    long['tasks'][0]['label']='界'*180
    long['tasks'][0]['owner']='完整保留负责人说明'*25
    def build(name,spec,views,expected=0):
        path=directory/(name+'.json');write_json(path,spec)
        dest=directory/name
        command=[sys.executable,'-B','-I',str(package/'scripts/report_schedule.py'),'render',str(path),'--views',views,'--output',str(dest)]
        result=subprocess.run(command,capture_output=True,text=True,encoding='utf-8')
        require(result.returncode==expected, name+': unexpected render status '+result.stdout+result.stderr)
        if expected:require(not dest.exists(),name+': invalid input created output')
        return dest, {'name':name,'argv':command,'exit_code':result.returncode,'stdout':result.stdout,'expected_rejection':bool(expected)}
    ctx=browser.new_context(viewport={'width':1600,'height':1000},offline=True)
    page=ctx.new_page();results=[]
    try:
        for name,spec,views in (('cross-year',crossyear,'gantt,drift'),('all-actions',actions,'summary'),('long-history',dense,'drift'),('clustered-dates',clustered,'drift'),('no-baseline-unknown',unknown,'gantt,outcomes'),('historical-actual',historical_actual,'drift'),('long-label',long,'gantt')):
            folder,record=build(name,spec,views);results.append(record)
            page.goto((folder/'index.html').as_uri());settle(page)
            count=page.locator('.slide').count();measurements=[]
            for i in range(count):
                page.evaluate('(i)=>reportDeck.goTo(i)',i);settle(page)
                issues=page.evaluate('reportDeck.inspectLayout().issues')
                independent=page.evaluate(MEASURE)
                measurements.append({'page':active(page),'issues':issues,'dom':independent,'svg':page.evaluate(SVG_BOUNDS)})
                if name!='long-label':
                    require(not issues and all(not e['outsideSlide'] and not e['textOutsideSlide'] for s in independent for e in s['elements']),name+': capacity violation')
                page.screenshot(path=str(folder/f'page-{i+1:02}.png'))
            record['measurements']=measurements
            maps=json.loads((folder/'page-map.json').read_text(encoding='utf-8'))['elements']
            if name=='cross-year':
                require('2026-' in page.locator('body').text_content() and '2027-' in page.locator('body').text_content(),'cross-year dates missing')
                circles=page.locator('.schedule-drift circle').evaluate_all('(els)=>els.map(e=>Number(e.getAttribute("cx")))')
                days=[date.fromisoformat(s['reported_on']) for s in spec['snapshots']]
                expected=[(d-days[0]).days/(days[-1]-days[0]).days for d in days]
                actual=[(x-circles[0])/(circles[-1]-circles[0]) for x in circles]
                require(all(abs(a-b)<1e-5 for a,b in zip(expected,actual)), 'drift dates replaced by equal category spacing')
                intervals=[]
                for task in spec['tasks']:
                    if not task.get('actual',{}).get('start'):continue
                    row=page.locator(f'[data-schedule-view="gantt"] tr[id$="-{task["id"]}"]')
                    a=float(row.locator('rect.schedule-actual').get_attribute('width'));b=float(row.locator('rect.schedule-baseline').get_attribute('width'))
                    actual_days=(date.fromisoformat(task['actual'].get('finish',spec['as_of']))-date.fromisoformat(task['actual']['start'])).days+1
                    baseline_days=(date.fromisoformat(task['baseline']['finish'])-date.fromisoformat(task['baseline']['start'])).days+1
                    require(abs(a/b-actual_days/baseline_days)<1e-4,'inclusive calendar interval ratio')
                    intervals.append({'task':task['id'],'actual_days':actual_days,'baseline_days':baseline_days,'actual_width':a,'baseline_width':b})
                record['date_oracle']={'expected_fractions':expected,'actual_fractions':actual,'intervals':intervals}
            elif name=='all-actions':
                emitted=[m['displayed']['id'] for m in maps if m.get('datum_id') and m['displayed'].get('id','').startswith('probe-action-')]
                require(emitted==[a['id'] for a in spec['actions']],'actions omitted/duplicated/reordered')
                require(any(m.get('displayed',{}).get('id')=='launch' for m in maps),'explicit summary milestone missing')
                page.pdf(path=str(folder/'deck.pdf'),prefer_css_page_size=True,print_background=True)
                from pypdf import PdfReader
                require(len(PdfReader(folder/'deck.pdf').pages)==count,'actions PDF count')
                record['actions']=emitted;record['pdf_pages']=count
            elif name in ('long-history','clustered-dates'):
                require(page.locator('.schedule-drift').count()==0,'dense dates must use explicit table fallback')
                dates=[m['displayed']['reported_on'] for m in maps if m.get('datum_id') and 'reported_on' in m['displayed']]
                require(dates==[s['reported_on'] for s in spec['snapshots']],'history records lost in table fallback')
                record['recorded_dates']=dates
            elif name=='no-baseline-unknown':
                require(page.locator('.schedule-time-plot .schedule-baseline').count()==0,'fabricated baseline graphic')
                first=page.locator('[data-schedule-view="outcomes"] tr[id$="-requirements"]').inner_text()
                second=page.locator('[data-schedule-view="outcomes"] tr[id$="-integration"]').inner_text()
                require('记录缺失 / 待核' in first and '未通过' not in first and '未通过' in second,'unknown acceptance conflated with rejection')
                require(all(m['displayed']['deviation_days'] is None for m in maps if m.get('datum_id') and 'deviation_days' in m['displayed']),'missing baseline fabricated variance')
                record['acceptance']={'unknown':first,'rejected':second}
            elif name=='historical-actual':
                warning=page.locator('[data-warning-code="historical_forecast_after_actual"]')
                require(warning.count()==1 and warning.is_visible(),'historical actual warning missing')
                require(page.locator('[data-warning-code="same_day_fs_order_unknown"]').count()==0,'historical warning mislabeled FS')
                detail=warning.inner_text()
                require(all(d in detail for d in (spec['as_of'],spec['milestones'][0]['actual_date'],spec['snapshots'][-1]['forecasts'][0]['date'])),'warning lost actual/report/forecast date')
                dates=[m['displayed']['reported_on'] for m in maps if m.get('datum_id') and 'reported_on' in m['displayed']]
                require(dates==[s['reported_on'] for s in spec['snapshots']],'actual warning rewrote historical records')
                record['visible_warning']=detail;record['preserved_history']=dates
            else:
                require(any(m['issues'] for m in measurements),'max-length valid text falsely treated as fit')
                more_action(page,'#read-all')
                require(long['tasks'][0]['label'] in page.locator('.slide').first.inner_text(),'long schedule label lost')
                record['expected_capacity_failure']=True
        for name,mutate in (
            ('mixed-baseline',lambda s:s['snapshots'][0]['baseline_ref'].update(revision=2)),
            ('missing-history',lambda s:s['snapshots'][1].update(forecasts=[])),
            ('same-day-disagreement',lambda s:s['snapshots'][-1]['forecasts'][0].update(date=(date.fromisoformat(s['milestones'][0]['forecast_date'])+timedelta(days=1)).isoformat())),
            ('oversized-percentage',lambda s:s['tasks'][0]['progress'].update(value=10**1000)),
        ):
            invalid=deepcopy(canonical);mutate(invalid)
            _,record=build(name,invalid,'drift',expected=2);results.append(record)
        receipt['schedule_boundaries']=results
    finally:
        ctx.close()


if __name__=='__main__':
    sys.exit(main())
