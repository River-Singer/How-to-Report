"""Actual headless-browser geometry checks for offline user-derived assets."""
from __future__ import annotations

import argparse
import asyncio
import base64
import copy
import json
from pathlib import Path
import sys
from xml.etree import ElementTree as ET

from recompute_user_templates import ICONS, OUTPUT, ROOT, SVG, TASK, sha, write_json

def browser_executable(value: str) -> str:
    path = Path(value).expanduser()
    if not path.is_file():
        raise argparse.ArgumentTypeError(f"browser executable must be an existing file: {value}")
    return str(path.resolve())


async def verify_icons(browser):
    registry = json.loads((ICONS / "catalog.json").read_text(encoding="utf-8"))
    items = [(key, item) for key, item in registry.items() if key.startswith("ppt-icons-")]
    page = await browser.new_page(viewport={"width": 1600, "height": 1200})
    markup = '<main>' + ''.join(f'<div data-key="{key}">{(ICONS / item["file"]).read_text(encoding="utf-8")}</div>' for key, item in items) + '</main>'
    await page.set_content(markup)
    boxes = await page.evaluate('''() => [...document.querySelectorAll('main>div')].map(div=>{
      const b=div.firstElementChild.getBBox();return {key:div.dataset.key,bbox:[b.x,b.y,b.width,b.height]};
    })''')
    receipt = json.loads((TASK / "assets/icon-extraction-receipt.json").read_text(encoding="utf-8"))
    by_key = {item["key"]: item for item in receipt["items"]}
    for result in boxes:
        key, box = result["key"], result["bbox"]
        if min(box[2:]) <= 0:
            raise ValueError(f"empty browser geometry: {key}")
        item = registry[key]
        root = ET.parse(ICONS / item["file"]).getroot()
        x, y, width, height = item["source_frame"]
        # Imported source frames and paths were rounded separately; normalize to measured vector extents.
        root.set("viewBox", f"0 0 {box[2]:.12g} {box[3]:.12g}")
        root.set("width", f"{box[2]:.12g}")
        root.set("height", f"{box[3]:.12g}")
        root[0].set("transform", f"translate({-x-box[0]:.12g} {-y-box[1]:.12g})")
        (ICONS / item["file"]).write_text(ET.tostring(root, encoding="unicode") + "\n", encoding="utf-8")
        item["asset_sha256"] = sha(ICONS / item["file"])
        item["normalized_vector_bounds"] = [0, 0, box[2], box[3]]
        by_key[key].update(item)
    write_json(ICONS / "catalog.json", registry)
    markup = '<main>' + ''.join(f'<div data-key="{key}">{(ICONS / item["file"]).read_text(encoding="utf-8")}</div>' for key, item in items) + '</main>'
    await page.set_content(markup)
    errors = await page.evaluate('''() => [...document.querySelectorAll('main>div')].flatMap(div=>{
      const svg=div.firstElementChild,b=svg.getBBox(),v=svg.viewBox.baseVal;
      const error=Math.max(Math.abs(b.x),Math.abs(b.y),Math.abs(b.width-v.width),Math.abs(b.height-v.height));
      return error>.001?[{key:div.dataset.key,error}]:[];
    })''')
    if errors:
        raise ValueError(f"normalized bbox verification failed: {errors[:10]}")
    # Readable per-source-page contact sheets; each item has its full stable key.
    contact = TASK / "assets/icon-contact-sheets"
    contact.mkdir(parents=True, exist_ok=True)
    for source_page in range(1, 13):
        cards = []
        for key, item in items:
            if item["source_slide"] == source_page:
                svg = (ICONS / item["file"]).read_bytes()
                cards.append(f'<div><img src="data:image/svg+xml;base64,{base64.b64encode(svg).decode()}"><code>{key}</code></div>')
        await page.set_content(f'<style>body{{font:18px system-ui;margin:28px;color:#26354a}}main{{display:grid;grid-template-columns:repeat(8,1fr);gap:12px}}main div{{display:grid;justify-items:center;gap:10px;border:1px solid #cbd4e3;padding:14px}}img{{width:80px;height:80px}}code{{font-size:10px}}</style><h1>PPT图标 · 源第{source_page}页 · {len(cards)}个独立对象</h1><main>{"".join(cards)}</main>')
        await page.locator("img").evaluate_all("els => Promise.all(els.map(img=>img.decode()))")
        await page.screenshot(path=str(contact / f"page-{source_page:02d}.png"), full_page=True)
    receipt["browser_verification"] = {"engine": browser.version, "individually_measured": len(boxes),
                                       "positive_vector_bounds": len(boxes), "normalization": "native SVG getBBox vector extents, no raster crop",
                                       "max_tolerance_px": .001, "normalized_bounds_failures": errors,
                                       "contact_sheets": 12}
    write_json(TASK / "assets/icon-extraction-receipt.json", receipt)
    await page.close()
    print(json.dumps(receipt["browser_verification"]), flush=True)


async def verify_templates(browser):
    index = json.loads((OUTPUT / "index.json").read_text(encoding="utf-8"))
    jobs = asyncio.Queue()
    for item in index["pages"]:
        jobs.put_nowait(item)
    results = []

    async def worker():
        page = await browser.new_page(viewport={"width": 1440, "height": 810})
        while not jobs.empty():
            item = await jobs.get()
            errors = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            await page.goto((OUTPUT / item["preview"]).as_uri(), wait_until="load")
            result = await page.evaluate('''() => {
              const svg=document.documentElement,shapes=[...document.querySelectorAll('[id^="shape-"][data-pptx-frame]')];
              const images=[...document.querySelectorAll('image')].map(i=>i.getAttribute('href')||i.getAttributeNS('http://www.w3.org/1999/xlink','href'));
              return {width:svg.viewBox.baseVal.width,height:svg.viewBox.baseVal.height,shape_count:shapes.length,
                paths:document.querySelectorAll('path').length,texts:document.querySelectorAll('text').length,
                gradients_used:[...document.querySelectorAll('*')].filter(n=>/^url\\(#/.test(n.getAttribute('fill')||'')||/^url\\(#/.test(n.getAttribute('stroke')||'')).length,
                finite_geometry:shapes.every(n=>{const b=n.getBBox();return [b.x,b.y,b.width,b.height].every(Number.isFinite)}),images};
            }''')
            missing_images = []
            svg_path = OUTPUT / item["preview"]
            for path in result["images"]:
                if path and not path.startswith(("data:", "http:", "https:")) and not (svg_path.parent / path).exists():
                    missing_images.append(path)
            status = "pass" if (result["shape_count"] == item["shape_count"] and result["finite_geometry"] and not errors and not missing_images) else "fail"
            results.append({"id": item["id"], "status": status, **result, "browser_errors": errors, "missing_images": missing_images})
            jobs.task_done()
        await page.close()

    await asyncio.gather(*(worker() for _ in range(4)))
    report = {"engine": browser.version, "pages_checked": len(results), "passed": sum(item["status"] == "pass" for item in results),
              "scope": "All SVGs parsed in Chromium; finite per-shape bounding boxes, object count, local image availability and remaining gradient paint checked. This does not assert human visual quality, native Office editing, or import fidelity.",
              "results": sorted(results, key=lambda item: item["id"])}
    write_json(TASK / "assets/template-browser-verification.json", report)
    print(json.dumps({key: report[key] for key in ("pages_checked", "passed")}), flush=True)


async def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["icons", "templates", "all"])
    parser.add_argument(
        "--browser-executable", type=browser_executable,
        help="Optional browser executable; defaults to Playwright's installed Chromium.",
    )
    args = parser.parse_args()
    from playwright.async_api import async_playwright
    async with async_playwright() as playwright:
        launch_options = {"headless": True}
        if args.browser_executable is not None:
            launch_options["executable_path"] = args.browser_executable
        browser = await playwright.chromium.launch(**launch_options)
        try:
            if args.mode in {"icons", "all"}:
                await verify_icons(browser)
            if args.mode in {"templates", "all"}:
                await verify_templates(browser)
        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
