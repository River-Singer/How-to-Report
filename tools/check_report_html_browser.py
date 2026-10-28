#!/usr/bin/env python3
"""Development-only actual Chromium probe; never a semantic/model evaluation.

Requires an existing Playwright Python/browser installation. Runtime Skills do not.
Creates a new evidence directory; neither plans nor installed packages are changed.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import math
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def render(renderer, plan, output):
    command = [sys.executable, "-B", "-I", str(renderer), "render", str(plan), "--output", str(output)]
    result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8")
    if result.returncode:
        raise RuntimeError(f"renderer failed ({result.returncode}): {result.stdout} {result.stderr}")
    return {"argv": command, "exit_code": result.returncode, "stdout": result.stdout, "stderr": result.stderr}


def toggle_read_all(page):
    """The 0.2 shell puts this control in More; older decks expose it directly."""
    if not page.locator("#read-all").is_visible():
        page.locator("#more-toggle").click()
    page.locator("#read-all").click()


# Read rendered DOM, independently of the product's inspectLayout implementation.
MEASURE = r"""() => {
 const rect = r => ({x:r.x,y:r.y,width:r.width,height:r.height,right:r.right,bottom:r.bottom});
 const visible = el => getComputedStyle(el).display !== 'none' && getComputedStyle(el).visibility !== 'hidden' && el.getBoundingClientRect().width > 0;
 const slides = [...document.querySelectorAll('.slide')].filter(visible);
 return slides.map(slide => {
   const outer = slide.getBoundingClientRect();
   const elements = [...slide.querySelectorAll('.page-element')].filter(visible).map(el => {
     const r = el.getBoundingClientRect();
     const range = document.createRange(); range.selectNodeContents(el);
     const boxes = [...range.getClientRects()].filter(r => r.width && r.height);
     return {id:el.dataset.elementId,refs:el.dataset.refs,rect:rect(r),
       scrollWidth:el.scrollWidth,clientWidth:el.clientWidth,scrollHeight:el.scrollHeight,clientHeight:el.clientHeight,
       outsideSlide:r.left<outer.left-2 || r.top<outer.top-2 || r.right>outer.right+2 || r.bottom>outer.bottom+2,
       textOutsideSlide:boxes.some(t=>t.left<outer.left-2 || t.right>outer.right+2 || t.top<outer.top-2 || t.bottom>outer.bottom+2)};
   });
   return {id:slide.dataset.pageId,rect:rect(outer),elements,text:slide.innerText};
 });
}"""


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--renderer", type=Path, required=True)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--browser", type=Path, help="optional existing Chromium executable")
    parser.add_argument("--canvas", nargs=2, type=int, metavar=("WIDTH", "HEIGHT"), help="test an explicitly configured canvas")
    args = parser.parse_args(argv)
    renderer, plan, output = args.renderer.resolve(strict=True), args.plan.resolve(strict=True), args.output.resolve()
    if output.exists() or output.is_relative_to(renderer.parent.parent):
        parser.error("evidence destination must be new and outside the installed Skill")
    output.mkdir(parents=False, exist_ok=False)
    receipt = {"captured_at_utc": datetime.now(timezone.utc).isoformat(), "scope": "synthetic_engineering_browser_probe_only", "model_execution": False,
               "renderer_sha256": digest(renderer), "input_sha256": digest(plan), "checks": [], "errors": [], "semantic_quality": "not_assessed"}
    try:
        plan_data = json.loads(plan.read_text(encoding="utf-8-sig"))
        if args.canvas:
            plan_data["canvas"] = dict(zip(("width", "height"), args.canvas))
            plan = output / "configured-plan.json"
            write_json(plan, plan_data)
        receipt["effective_input_sha256"] = digest(plan)
        receipt["render"] = render(renderer, plan, output / "base")
        receipt["html_sha256"] = digest(output / "base/index.html")
        plan_data = json.loads(plan.read_text(encoding="utf-8-sig"))
        dense = deepcopy(plan_data)
        dense["pages"][0]["elements"][0]["body"] = "容量检查必须保留所有重要限制。" * 800
        write_json(output / "dense-plan.json", dense)
        receipt["dense_render"] = render(renderer, output / "dense-plan.json", output / "dense")
        hostile = deepcopy(plan_data)
        hostile["pages"][0]["elements"][0]["body"] = '<img src="https://example.invalid/probe" onerror="window.__HTML_ATTACKED__=true"> & <script>window.__HTML_ATTACKED__=true</script>'
        write_json(output / "hostile-plan.json", hostile)
        receipt["hostile_render"] = render(renderer, output / "hostile-plan.json", output / "hostile")
        long_label = deepcopy(plan_data)
        label_target = next(e for p in long_label["pages"] for e in p["elements"] if e.get("type") == "chart" and e["chart"]["kind"] == "bar")
        label_target["chart"]["items"][0]["label"] = "必须完整保留的真实长类别标签" * 80
        write_json(output / "long-label-plan.json", long_label)
        receipt["long_label_render"] = render(renderer, output / "long-label-plan.json", output / "long-label")
        from playwright.sync_api import sync_playwright
        with sync_playwright() as engine:
            options = {"headless": True}
            if args.browser: options["executable_path"] = str(args.browser.resolve(strict=True))
            browser = engine.chromium.launch(**options)
            receipt["browser"] = {"name": "Chromium", "version": browser.version}
            try:
                run_browser(browser, output, receipt, plan_data)
            finally:
                browser.close()
    except Exception as exc:
        receipt["errors"].append(f"{type(exc).__name__}: {exc}")
    receipt["passed"] = not receipt["errors"]
    receipt["evidence_files"] = [{"path": p.relative_to(output).as_posix(), "sha256": digest(p)} for p in sorted(output.rglob("*")) if p.is_file()]
    write_json(output / "browser-receipt.json", receipt)
    print(json.dumps({"passed": receipt["passed"], "errors": receipt["errors"], "receipt": str(output / "browser-receipt.json")}, ensure_ascii=True))
    return 0 if receipt["passed"] else 1


def run_browser(browser, output, receipt, plan):
    context = browser.new_context(viewport={"width": 1600, "height": 1000}, device_scale_factor=1)
    page = context.new_page()
    console_errors, script_errors, requests = [], [], []
    page.on("console", lambda message: console_errors.append(message.text) if message.type == "error" else None)
    page.on("pageerror", lambda error: script_errors.append(str(error)))
    page.on("request", lambda request: requests.append(request.url) if not request.url.startswith(("file:", "data:", "about:")) else None)
    context.route("http://**/*", lambda route: route.abort())
    context.route("https://**/*", lambda route: route.abort())
    url = (output / "base/index.html").as_uri()
    checks = receipt["checks"]
    def require(condition, message):
        if not condition:
            raise AssertionError(message)
    def active():
        return page.evaluate("() => [...document.querySelectorAll('.slide')].filter(s=>getComputedStyle(s).display!=='none' && s.getBoundingClientRect().width>0).map(s=>s.dataset.pageId)")
    def settle():
        page.evaluate("() => document.fonts.ready")
        page.evaluate("() => new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)))")
    try:
        page.goto(url, wait_until="load")
        page.wait_for_function("() => Boolean(window.reportDeck)")
        for viewport in ({"width":1600,"height":1000},{"width":1280,"height":720},{"width":1024,"height":768},{"width":390,"height":844}):
            page.set_viewport_size(viewport)
            settle()
            measurements = []
            for index, definition in enumerate(plan["pages"]):
                page.evaluate("index => window.reportDeck.goTo(index)", index)
                settle()
                actual = page.evaluate(MEASURE)
                require(len(actual) == 1 and actual[0]["id"] == definition["id"], "unexpected active page")
                slide = actual[0]
                box = slide["rect"]
                canvas = plan.get("canvas", {"width": 1600, "height": 900})
                require(abs(box["width"] / box["height"] - canvas["width"]/canvas["height"]) < 0.005, "stage ratio differs from configured canvas")
                require(box["x"] >= -2 and box["y"] >= -2 and box["right"] <= viewport["width"]+2 and box["bottom"] <= viewport["height"]+2, "stage leaves viewport")
                require(all(not e["outsideSlide"] and not e["textOutsideSlide"] for e in slide["elements"]), "mapped content leaves slide")
                require(len(slide["elements"]) == len(definition["elements"]), "mapped element missing")
                require(all(e["refs"] is not None for e in slide["elements"]), "element reference mapping absent")
                for limit in definition["limits"]:
                    require(limit in slide["text"], "visible limitation lost")
                geometry = page.evaluate("() => window.reportDeck.inspectLayout()")
                require(not geometry["issues"], "runtime reports overflow in base fixture")
                measurements.append({"page": definition["id"], "dom": slide, "runtime": geometry})
                if viewport["width"] == 1600:
                    page.screenshot(path=str(output / f"page-{index+1}.png"), full_page=True)
                elif viewport["width"] == 390 and index == 0:
                    page.screenshot(path=str(output / "mobile-deck.png"), full_page=True)
            checks.append({"kind":"viewport_geometry", "viewport":viewport,"pages":measurements,"passed":True})
        # Reconstruct typed datum/series identities from the authored plan rather than
        # trusting the renderer's own inspection/mapping as the numerical oracle.
        typed = []
        for index, definition in enumerate(plan["pages"]):
            if definition["layout"] != "composed":
                continue
            page.evaluate("index => window.reportDeck.goTo(index)", index); settle()
            for element in definition["elements"]:
                panel = page.locator(f'#element-{element["id"]}')
                require(all(x in panel.inner_text() for x in element["limits"]), "typed element limitation missing")
                datums = []
                if element["type"] == "hierarchy":
                    datums = element["levels"]
                elif element["type"] == "metric":
                    metric = panel.locator(".metric-value")
                    require(json.loads(metric.get_attribute("data-value")) == element["value"], "metric value changed")
                    require(element["unit"] in metric.inner_text(), "metric unit missing")
                    typed.append({"id":element["id"], "value":element["value"], "text":metric.inner_text()})
                elif element["type"] == "chart":
                    chart = element["chart"]
                    require(chart["unit"] in panel.inner_text(), "chart unit missing")
                    if chart["kind"] == "bar": datums = chart["items"]
                    elif chart["kind"] == "heatmap":
                        datums = [d for row in chart["cells"] for d in row]
                        require(all(label in panel.inner_text() for label in chart["rows"]+chart["columns"]), "matrix labels missing")
                    else:
                        require(all(label in panel.inner_text() for label in chart["x_labels"]), "line x labels missing")
                        for series in chart["series"]:
                            datums.extend(series["points"])
                            require(series["label"] in panel.inner_text(), "series label missing")
                            lengths, current = [], 0
                            for datum in series["points"] + [{"value": None}]:
                                if datum["value"] is None:
                                    if current >= 2: lengths.append(current)
                                    current = 0
                                else: current += 1
                            segments = panel.locator(f'path[data-series-id="{series["id"]}"]').evaluate_all("els=>els.map(e=>Number(e.dataset.pointCount))")
                            require(segments == lengths, "line connects through missing data or loses known segments")
                            expected_points = [d["id"] for d in series["points"] if d["value"] is not None]
                            actual_points = panel.locator("[data-point-id]").evaluate_all("els=>els.map(e=>e.dataset.pointId)")
                            require(all(x in actual_points for x in expected_points), "known line point missing")
                for datum in datums:
                    node = panel.locator(f'#datum-{datum["id"]}')
                    require(node.count() == 1, "typed datum mapping missing")
                    require(json.loads(node.get_attribute("data-refs")) == datum["refs"], "typed datum references changed")
                    if "value" in datum:
                        actual_value = json.loads(node.get_attribute("data-value"))
                        require(actual_value == datum["value"], "typed numeric value changed")
                        shown = node.inner_text()
                        require(("缺失" in shown or "Unavailable" in shown) if datum["value"] is None else str(datum["value"]) in shown.replace("−", "-"), "typed displayed value differs")
                    if "label" in datum: require(datum["label"] in node.inner_text(), "typed label changed")
                    typed.append({"id": datum["id"], "value": datum.get("value"), "text": node.inner_text()})
            svg = page.locator(".slide:visible svg").evaluate_all("els=>els.map(e=>{const b=e.getBBox(),v=e.viewBox.baseVal;return {x:b.x,y:b.y,width:b.width,height:b.height,vx:v.x,vy:v.y,vw:v.width,vh:v.height}})")
            require(all(math.isfinite(n) for item in svg for n in item.values()), "nonfinite SVG geometry")
            require(all(b["x"] >= b["vx"]-1 and b["y"] >= b["vy"]-1 and b["x"]+b["width"] <= b["vx"]+b["vw"]+1 and b["y"]+b["height"] <= b["vy"]+b["vh"]+1 for b in svg), "SVG geometry leaves viewBox")
            checks.append({"kind":"independent_svg_bounds", "page":definition["id"], "bounds":svg,"passed":True})
        checks.append({"kind":"typed_data_labels_missing_segments_identity", "data":typed,"passed":True})
        # Navigation is exercised through keyboard/buttons, not only the test API.
        page.set_viewport_size({"width":1280,"height":800})
        page.keyboard.press("Home"); settle()
        require(active() == [plan["pages"][0]["id"]], "Home navigation failed")
        page.locator("#next").click(); settle()
        require(active() == [plan["pages"][1]["id"]], "next button failed")
        page.keyboard.press("ArrowLeft"); settle()
        require(active() == [plan["pages"][0]["id"]], "left keyboard navigation failed")
        page.keyboard.press("End"); settle()
        require(active() == [plan["pages"][-1]["id"]], "End navigation failed")
        last_hash = page.evaluate("location.hash")
        require(last_hash == "#" + plan["pages"][-1]["id"], "deep link does not identify page")
        page.reload(); settle()
        require(active() == [plan["pages"][-1]["id"]], "deep-link reload failed")
        page.locator("#previous").click(); settle()
        require(active() == [plan["pages"][-2]["id"]], "previous button failed")
        checks.append({"kind":"navigation_and_deep_link", "passed":True,"hash":last_hash})
        # Inspect real displayed numeric text; null may not become zero.
        numeric = []
        for index, definition in enumerate(plan["pages"]):
            if definition["layout"] != "data": continue
            page.evaluate("index=>window.reportDeck.goTo(index)",index); settle()
            for element in definition["elements"]:
                item = page.locator(f'[data-element-id="{element["id"]}"]')
                shown = item.locator(".value").inner_text()
                if element["value"] is None:
                    require(shown.strip() not in ("0","0.0","0%"), "missing value rendered as zero")
                else:
                    require(str(element["value"]) in shown.replace("−","-"), "numeric label changed")
                require(element["title"] in item.inner_text(), "data label truncated or changed")
                numeric.append({"id":element["id"],"input":element["value"],"shown":shown})
        bars = page.locator(".bar").evaluate_all("els=>els.map(e=>({width:e.getBoundingClientRect().width,left:e.getBoundingClientRect().left}))")
        require(all(math.isfinite(b["width"]) and b["width"]>=0 and math.isfinite(b["left"]) for b in bars), "nonfinite bar geometry")
        checks.append({"kind":"numeric_identity", "values":numeric,"bars":bars,"passed":True})
        saved_page = active()[0]
        toggle_read_all(page); settle()
        require(len(active()) == len(plan["pages"]), "read-all omits pages")
        require(page.locator("#read-all").get_attribute("aria-pressed") == "true", "read-all state not exposed")
        page.evaluate("() => window.reportDeck.inspectLayout()"); settle()
        require(len(active()) == len(plan["pages"]), "geometry inspection did not restore read-all")
        page.set_viewport_size({"width":390,"height":844}); settle()
        page.screenshot(path=str(output / "mobile-read-all.png"))
        mobile_charts = page.locator(".chart-content").evaluate_all("""els=>els.map(e=>{
          const table=e.querySelector('table'),svg=e.querySelector('svg');
          const prior=e.scrollLeft;e.scrollLeft=e.scrollWidth;const maximum=e.scrollLeft;
          let alignment=[];
          if(svg&&table){const cells=[...table.querySelectorAll('tbody tr:first-child td')];
            alignment=[...svg.querySelectorAll('[data-point-id]')].map(point=>{
              const cell=table.querySelector('#datum-'+point.dataset.pointId),a=point.getBoundingClientRect(),b=cell.getBoundingClientRect();
              return {id:point.dataset.pointId,delta:Math.abs(a.x+a.width/2-b.x-b.width/2)};});}
          const r={kind:e.dataset.chartKind,clientWidth:e.clientWidth,scrollWidth:e.scrollWidth,scrollLeft:maximum,
            svgWidth:svg?.getBoundingClientRect().width,tableWidth:table?.getBoundingClientRect().width,alignment};
          e.scrollLeft=prior;return r;
        })""")
        require(all(c["scrollWidth"] <= c["clientWidth"]+1 or c["scrollLeft"] > 0 for c in mobile_charts), "mobile chart content is unreachable by horizontal scrolling")
        require(all(abs(c["svgWidth"]-c["tableWidth"]) < 1 and all(p["delta"]<2 for p in c["alignment"]) for c in mobile_charts if c["kind"] == "line"), "mobile line points do not align with time columns")
        checks.append({"kind":"mobile_chart_scroll_and_time_alignment","charts":mobile_charts,"passed":True})
        for definition in plan["pages"]:
            if definition["layout"] == "composed":
                page.locator(f'#page-{definition["id"]}').scroll_into_view_if_needed()
                page.screenshot(path=str(output / f'mobile-read-all-{definition["id"]}.png'))
        toggle_read_all(page); settle()
        require(active() == [saved_page], "read-all exit lost active page")
        page.set_viewport_size({"width":1280,"height":800}); settle()
        checks.append({"kind":"read_all_and_return", "pages":len(plan["pages"]),"restored_page":saved_page,"passed":True})
        toggle_read_all(page); settle()
        page.emulate_media(media="print"); settle()
        printed = page.evaluate(MEASURE)
        require(len(printed) == len(plan["pages"]), "print omits pages")
        page.pdf(path=str(output / "print.pdf"), print_background=True, prefer_css_page_size=True)
        checks.append({"kind":"print_all_pages", "pages":len(printed),"passed":True})
        page.emulate_media(media="screen")
        require(page.locator("#read-all").get_attribute("aria-pressed") == "true", "printing lost read-all mode")
        page.goto((output / "long-label/index.html").as_uri(), wait_until="load"); settle()
        label_page = next(i for i,p in enumerate(plan["pages"]) if any(e.get("type") == "chart" and e["chart"]["kind"] == "bar" for e in p["elements"]))
        page.evaluate("index=>window.reportDeck.goTo(index)",label_page); settle()
        label_geometry = page.evaluate("() => window.reportDeck.inspectLayout()")
        require(bool(label_geometry["issues"]), "long labels fail to trigger capacity issues")
        require("必须完整保留的真实长类别标签" * 80 in page.locator(".slide:visible").inner_text(), "long label text lost")
        require(page.locator("#layout-warning").is_visible(), "long label warning missing")
        page.screenshot(path=str(output / "long-label-overflow.png"),full_page=True)
        checks.append({"kind":"long_label_negative_fixture", "runtime":label_geometry,"passed":True})
        page.goto((output / "dense/index.html").as_uri(), wait_until="load"); settle()
        dense = page.evaluate("() => window.reportDeck.inspectLayout()")
        require(bool(dense["issues"]), "dense content fails to trigger layout issues")
        require(page.locator("#layout-warning").is_visible() and bool(page.locator("#layout-warning").inner_text().strip()), "dense warning is not visible")
        page.screenshot(path=str(output / "overflow.png"),full_page=True)
        checks.append({"kind":"overflow_negative_fixture", "runtime":dense,"passed":True})
        toggle_read_all(page); settle()
        full_body = page.locator(".page-element p").first.inner_text()
        require(full_body == "容量检查必须保留所有重要限制。" * 800, "read-all lost dense body text")
        require(page.evaluate("document.documentElement.scrollHeight > innerHeight"), "dense read-all cannot scroll")
        page.locator(".slide").first.locator(".page-footer").scroll_into_view_if_needed()
        page.screenshot(path=str(output / "dense-read-all-footer.png"))
        checks.append({"kind":"dense_read_all_preserves_text", "body_characters":len(full_body),"passed":True})
        page.goto((output / "hostile/index.html").as_uri(), wait_until="load"); settle()
        require(page.evaluate("() => window.__HTML_ATTACKED__ === undefined"), "text executed JavaScript")
        require(page.locator("img").count() == 0, "injected image element created")
        require("<img src=" in page.locator(".slide").first.inner_text(), "hostile text not preserved visibly")
        checks.append({"kind":"hostile_text_is_literal", "passed":True})
        require(not console_errors and not script_errors and not requests, "browser errors or unexpected requests")
    finally:
        receipt["console_errors"], receipt["script_errors"], receipt["unexpected_requests"] = console_errors, script_errors, requests
        context.close()


if __name__ == "__main__":
    sys.exit(main())
