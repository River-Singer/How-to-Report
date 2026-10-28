#!/usr/bin/env python3
"""Render a declared page plan to an offline deck; do not certify its meaning."""
from __future__ import annotations

import argparse
import hashlib
from html import escape
import json
import math
import os
from pathlib import Path
import re
import stat
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from report_run import local_path, resolve_path, require_local
from validate_run import unique_keys

PACKAGE = Path(__file__).resolve().parent.parent
ASSETS = PACKAGE / "assets" / "report-html"
VERSION = "0.1"
DEFAULT_CANVAS = {"width": 1600, "height": 900}
ID = re.compile(r"[A-Za-z][A-Za-z0-9_-]{0,63}\Z")


def digest(value):
    return hashlib.sha256(value).hexdigest()


def encode(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode("utf-8")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def fields(obj, required, optional, where):
    require(isinstance(obj, dict), where + ": expected object")
    require(set(required) <= obj.keys(), where + ": missing required fields")
    require(obj.keys() <= set(required) | set(optional), where + ": unknown fields")


def string(value, where):
    require(isinstance(value, str) and bool(value.strip()), where + ": expected nonempty text")
    require(not any(ord(c) < 32 and c not in "\n\t\r" for c in value), where + ": control characters unsupported")


def refs(values, where):
    require(isinstance(values, list), where + ": expected list")
    seen = set()
    for i, value in enumerate(values):
        at = f"{where}[{i}]"
        fields(value, ("id", "revision"), ("locator",), at)
        string(value["id"], at + ".id")
        require(type(value["revision"]) is int and value["revision"] > 0, at + ": positive integer revision required")
        if "locator" in value:
            string(value["locator"], at + ".locator")
        identity = (value["id"], value["revision"], value.get("locator"))
        require(identity not in seen, at + ": duplicate reference")
        seen.add(identity)


def identifier(value, seen, where):
    string(value, where)
    require(ID.fullmatch(value) is not None and value not in seen, where + ": invalid/duplicate ID")
    seen.add(value)


def number(value, where):
    require(value is None or (type(value) in (int, float) and -1e12 <= value <= 1e12 and math.isfinite(value)), where + ": expected null or finite number within ±1e12")


def labels(values, minimum, maximum, where):
    require(isinstance(values, list) and minimum <= len(values) <= maximum, where + ": invalid label count")
    for value in values:
        string(value, where)
    require(len({v.strip().casefold() for v in values}) == len(values), where + ": duplicate labels")


def limitations(values, where):
    require(isinstance(values, list) and len(values) >= 1, where + ": state at least one scope/limitation")
    for value in values:
        string(value, where)


def datum(value, seen, where, extra=()):
    fields(value, ("id", "value", "refs") + extra, (), where)
    identifier(value["id"], seen, where)
    number(value["value"], where)
    refs(value["refs"], where)
    for key in extra:
        string(value[key], where + "." + key)


def composition(page, seen, where):
    """Semantic blocks and their data are independent from a spatial-only tree."""
    require("unit" not in page and "tree" in page, where + ": composed requires tree, not page unit")
    require(1 <= len(page["elements"]) <= 12, where + ": composed requires 1–12 elements")
    common = ("id", "type", "role", "title", "body", "refs", "limits")
    for element in page["elements"]:
        require(isinstance(element, dict), where + ": expected typed element")
        kind = element.get("type")
        require(isinstance(kind, str) and kind in ("text", "metric", "hierarchy", "chart"), where + ": unknown element type")
        extra = {"text": (), "metric": ("unit", "value"), "hierarchy": ("levels",), "chart": ("chart",)}[kind]
        fields(element, common + extra, (), where)
        identifier(element["id"], seen, where)
        for key in ("title", "body"):
            string(element[key], where + "." + key)
        require(element["role"] in ("primary", "supporting", "context"), where + ": invalid visual role")
        refs(element["refs"], where)
        limitations(element["limits"], where)
        if kind == "metric":
            string(element["unit"], where)
            number(element["value"], where)
        if kind == "hierarchy":
            levels = element["levels"]
            require(isinstance(levels, list) and 2 <= len(levels) <= 5, where + ": hierarchy requires 2–5 levels")
            for level in levels:
                fields(level, ("id", "label", "body", "refs"), (), where)
                identifier(level["id"], seen, where)
                string(level["body"], where)
                refs(level["refs"], where)
            labels([v["label"] for v in levels], 2, 5, where)
        if kind != "chart":
            continue
        chart = element["chart"]
        require(isinstance(chart, dict), where + ": expected chart object")
        ck = chart.get("kind")
        require(isinstance(ck, str) and ck in ("bar", "line", "heatmap"), where + ": unsupported chart")
        fields(chart, ("kind", "unit") + {"bar": ("items",), "line": ("x_labels", "series"), "heatmap": ("rows", "columns", "cells")}[ck], (), where)
        string(chart["unit"], where)
        if ck == "bar":
            require(isinstance(chart["items"], list), where + ": expected items")
            for item in chart["items"]:
                datum(item, seen, where, ("label",))
            labels([v["label"] for v in chart["items"]], 1, 8, where)
        elif ck == "line":
            labels(chart["x_labels"], 2, 8, where)
            require(isinstance(chart["series"], list) and 1 <= len(chart["series"]) <= 3, where + ": expected 1–3 series")
            for series in chart["series"]:
                fields(series, ("id", "label", "points"), (), where)
                identifier(series["id"], seen, where)
                require(isinstance(series["points"], list) and len(series["points"]) == len(chart["x_labels"]), where + ": point count differs from x labels")
                for point in series["points"]:
                    datum(point, seen, where)
            labels([v["label"] for v in chart["series"]], 1, 3, where)
        else:
            labels(chart["rows"], 1, 6, where)
            labels(chart["columns"], 1, 6, where)
            require(isinstance(chart["cells"], list) and len(chart["cells"]) == len(chart["rows"]), where + ": heatmap row count mismatch")
            for row in chart["cells"]:
                require(isinstance(row, list) and len(row) == len(chart["columns"]), where + ": heatmap column count mismatch")
                for cell in row:
                    datum(cell, seen, where)
    leaves = []
    count = 0
    def walk(node, depth):
        nonlocal count
        count += 1
        require(depth <= 5 and count <= 31, where + ": layout depth/node budget exceeded")
        require(isinstance(node, dict), where + ": expected layout node")
        if "element" in node:
            fields(node, ("element",), (), where)
            string(node["element"], where)
            leaves.append(node["element"])
            return
        fields(node, ("type", "weights", "children"), (), where)
        require(node["type"] in ("row", "column"), where + ": invalid layout direction")
        children, weights = node["children"], node["weights"]
        require(isinstance(children, list) and 2 <= len(children) <= 6, where + ": expected 2–6 children")
        require(isinstance(weights, list) and len(weights) == len(children), where + ": layout weight count mismatch")
        require(all(type(w) in (int, float) and 0.1 <= w <= 100 and math.isfinite(w) for w in weights), where + ": weights must be finite numbers within 0.1–100")
        for child in children:
            walk(child, depth + 1)
    walk(page["tree"], 1)
    require(leaves == [v["id"] for v in page["elements"]], where + ": tree must map every element exactly once in declared reading order")


def validate(plan):
    fields(plan, ("page_plan_version", "title", "language", "pages"), ("canvas",), "plan")
    require(plan["page_plan_version"] == VERSION, "unsupported page_plan_version")
    string(plan["title"], "title")
    require(isinstance(plan["language"], str) and plan["language"] in ("zh-CN", "en"), "language must be zh-CN or en")
    require(isinstance(plan["pages"], list) and 1 <= len(plan["pages"]) <= 100, "pages must contain 1–100 pages")
    if "canvas" in plan:
        canvas = plan["canvas"]
        fields(canvas, ("width", "height"), (), "canvas")
        require(type(canvas["width"]) is int and 1200 <= canvas["width"] <= 2400, "canvas.width must be an integer within 1200–2400")
        require(type(canvas["height"]) is int and 675 <= canvas["height"] <= 1600, "canvas.height must be an integer within 675–1600")
        require(1.2 <= canvas["width"] / canvas["height"] <= 2.4, "canvas aspect ratio must be within 1.2–2.4")
    seen = set()
    for i, page in enumerate(plan["pages"]):
        at = f"pages[{i}]"
        fields(page, ("id", "layout", "question", "title", "takeaway", "limits", "refs", "elements"), ("unit", "tree"), at)
        for field in ("id", "question", "title", "takeaway"):
            string(page[field], at + "." + field)
        require(ID.fullmatch(page["id"]) is not None and page["id"] not in seen, at + ": invalid/duplicate ID")
        seen.add(page["id"])
        layout = page["layout"]
        require(isinstance(layout, str) and layout in ("focus", "compare", "sequence", "data", "composed"), at + ": unknown layout")
        require(isinstance(page["limits"], list) and len(page["limits"]) >= 1, at + ": state at least one scope/limitation")
        for limit in page["limits"]:
            string(limit, at + ".limits")
        refs(page["refs"], at + ".refs")
        require(isinstance(page["elements"], list), at + ": elements must be list")
        if layout == "composed":
            composition(page, seen, at)
            continue
        require("tree" not in page, at + ": tree belongs only to composed pages")
        minimum, maximum = {"focus": (1, 3), "compare": (2, 2), "sequence": (2, 5), "data": (1, 8)}[layout]
        require(minimum <= len(page["elements"]) <= maximum, at + ": invalid element count for layout")
        if layout == "data":
            string(page.get("unit"), at + ".unit")
        else:
            require("unit" not in page, at + ": unit belongs only to data pages")
        labels = set()
        for j, element in enumerate(page["elements"]):
            elt = f"{at}.elements[{j}]"
            required = ("id", "title", "body", "refs") + (("value",) if layout == "data" else ())
            fields(element, required, (), elt)
            for field in ("id", "title", "body"):
                string(element[field], elt + "." + field)
            require(ID.fullmatch(element["id"]) is not None and element["id"] not in seen, elt + ": invalid/duplicate ID")
            seen.add(element["id"])
            refs(element["refs"], elt + ".refs")
            if layout == "data":
                label = element["title"].strip().casefold()
                require(label not in labels, elt + ": duplicate data label")
                labels.add(label)
                value = element["value"]
                require(value is None or (type(value) in (int, float) and -1e12 <= value <= 1e12 and math.isfinite(value)), elt + ": expected null or finite number within ±1e12")
    return plan


def text(value):
    return escape(str(value), quote=True)


def reference_text(values, language):
    if not values:
        return "未提供引用" if language == "zh-CN" else "No reference supplied"
    return "; ".join(f'{v["id"]}@{v["revision"]}' + (" · " + v["locator"] if "locator" in v else "") for v in values)


def composed_body(page, plan, mapping):
    zh = plan["language"] == "zh-CN"
    missing = "缺失" if zh else "Unavailable"
    unit_label = "单位" if zh else "Unit"
    blocks = {}
    for element in page["elements"]:
        eid, kind = element["id"], element["type"]
        declared = []
        def markers(values):
            codes = []
            for ref in values:
                if ref not in declared:
                    declared.append(ref)
                codes.append(str(declared.index(ref) + 1))
            return '<sup class="source-marker">[' + (",".join(codes) if codes else ("无引用" if zh else "no ref")) + ']</sup>'
        def value_label(value):
            return missing if value is None else str(value)
        def datum_attrs(item, extra=None):
            displayed = dict(item)
            displayed.update(extra or {})
            mapping.append({"page_id": page["id"], "element_id": eid, "datum_id": item["id"], "selector": "#datum-" + item["id"], "refs": item["refs"], "displayed": displayed})
            attrs = f'id="datum-{item["id"]}" data-datum-id="{item["id"]}" data-refs="{text(json.dumps(item["refs"], ensure_ascii=False))}"'
            if "value" in item:
                attrs += f' data-value="{text("null" if item["value"] is None else item["value"])}"'
            return attrs
        sources = markers(element["refs"])
        main = ""
        if kind == "text":
            main = '<div class="text-space" aria-hidden="true"></div>'
        elif kind == "metric":
            main = f'<p class="metric-value" data-value="{text("null" if element["value"] is None else element["value"])}">{text(value_label(element["value"]))}<span class="metric-unit">{text(element["unit"])}</span></p>'
        elif kind == "hierarchy":
            levels = []
            for n, level in enumerate(element["levels"]):
                width = 64 + n * 36 / (len(element["levels"]) - 1)
                levels.append(f'<li {datum_attrs(level, {"level": n+1})} style="width:{width:.6f}%"><strong>{text(level["label"])}</strong>{markers(level["refs"])}<p>{text(level["body"])}</p></li>')
            notice = "层级宽度仅示意，不编码数量。" if zh else "Tier widths are schematic, not quantities."
            main = '<ol class="hierarchy-levels">' + "".join(levels) + f'</ol><p class="chart-legend">{notice}</p>'
        else:
            chart = element["chart"]
            ck, unit = chart["kind"], chart["unit"]
            if ck == "bar":
                numbers = [v["value"] for v in chart["items"] if v["value"] is not None]
                low, high = min([0] + numbers), max([0] + numbers)
                span, zero = high - low or 1, -low / (high - low or 1) * 100
                rows = []
                for item in chart["items"]:
                    value = item["value"]
                    bar = "" if value is None else f'<span class="bar {"negative" if value < 0 else "positive"}" style="left:{min(zero, (value-low)/span*100):.8f}%;width:{abs(value)/span*100:.8f}%"></span>'
                    rows.append(f'<div class="chart-bar-row" {datum_attrs(item, {"unit": unit})}><span class="chart-label">{text(item["label"])}</span><span class="track"><span class="zero" style="left:{zero:.8f}%"></span>{bar}</span><span class="chart-value">{text(value_label(value))}{markers(item["refs"])}</span></div>')
                main = f'<div class="chart-unit">{unit_label}: {text(unit)}</div><div class="chart-bars">{"".join(rows)}</div>'
            elif ck == "line":
                numbers = [p["value"] for s in chart["series"] for p in s["points"] if p["value"] is not None]
                low, high = min([0] + numbers), max([0] + numbers)
                span = high - low or 1
                vectors, rows = [], []
                for si, series in enumerate(chart["series"]):
                    segments, current = [], []
                    cells = []
                    for pi, point in enumerate(series["points"]):
                        value = point["value"]
                        if value is None:
                            if current:
                                segments.append(current)
                                current = []
                        else:
                            # Match HTML table column centers: first column is the series legend.
                            x, y = 168 + (pi + 0.5) * 632 / len(chart["x_labels"]), 108 - (value - low) / span * 96
                            current.append((x, y))
                            vectors.append(f'<circle class="line-point series-{si}" cx="{x:.8f}" cy="{y:.8f}" r="3" data-point-id="{point["id"]}"></circle>')
                        cells.append(f'<td {datum_attrs(point, {"unit": unit, "series_id": series["id"], "series_label": series["label"], "x_label": chart["x_labels"][pi]})}>{text(value_label(value))}{markers(point["refs"])}</td>')
                    if current:
                        segments.append(current)
                    for segment in segments:
                        if len(segment) >= 2:
                            path = "M" + " L".join(f"{x:.8f},{y:.8f}" for x, y in segment)
                            vectors.append(f'<path class="line-segment series-{si}" data-series-id="{series["id"]}" data-point-count="{len(segment)}" d="{path}"></path>')
                    pattern = (("实线", "虚线", "点线") if zh else ("solid", "dashed", "dotted"))[si]
                    rows.append(f'<tr data-series-id="{series["id"]}"><th scope="row"><span class="series-key series-{si}" aria-hidden="true"></span>{text(series["label"])} <span class="series-style">{pattern}</span></th>{"".join(cells)}</tr>')
                zero_y = 108 - (0 - low) / span * 96
                heads = "".join(f'<th scope="col">{text(label)}</th>' for label in chart["x_labels"])
                main = f'<div class="chart-unit">{unit_label}: {text(unit)} · {"纵轴" if zh else "Y scale"} {text(low)} — {text(high)}</div><svg class="line-plot" viewBox="0 0 800 120" preserveAspectRatio="none" role="img" aria-label="{text(element["title"])}"><line class="line-zero" x1="168" x2="800" y1="{zero_y:.8f}" y2="{zero_y:.8f}"></line>{"".join(vectors)}</svg><table class="line-values"><thead><tr><th scope="col">{"序列 / 时间" if zh else "Series / time"}</th>{heads}</tr></thead><tbody>{"".join(rows)}</tbody></table>'
            else:
                values = [v["value"] for row in chart["cells"] for v in row if v["value"] is not None]
                maximum = max([abs(v) for v in values] + [0])
                rows = []
                for ri, row in enumerate(chart["cells"]):
                    cells = []
                    for ci, cell in enumerate(row):
                        value = cell["value"]
                        intensity = 0 if value is None or maximum == 0 else abs(value) / maximum
                        color = "transparent" if value is None else f'rgba({("210,126,60" if value < 0 else "46,147,207")},{intensity*.58:.8f})'
                        cells.append(f'<td class="heat-cell {"missing-cell" if value is None else ""}" {datum_attrs(cell, {"unit": unit, "row": chart["rows"][ri], "column": chart["columns"][ci]})} style="background-color:{color}">{text(value_label(value))}{markers(cell["refs"])}</td>')
                    rows.append(f'<tr><th scope="row">{text(chart["rows"][ri])}</th>{"".join(cells)}</tr>')
                heads = "".join(f'<th scope="col">{text(label)}</th>' for label in chart["columns"])
                legend = f'颜色深浅表示绝对值 0–{maximum}；蓝为非负，棕为负，缺失不着色。' if zh else f'Intensity represents magnitude 0–{maximum}; blue nonnegative, brown negative, unavailable unfilled.'
                main = f'<div class="chart-unit">{unit_label}: {text(unit)}</div><table class="heatmap"><thead><tr><th scope="col">{"对象 / 维度" if zh else "Item / dimension"}</th>{heads}</tr></thead><tbody>{"".join(rows)}</tbody></table><p class="chart-legend">{text(legend)}</p>'
            main = f'<div class="chart-content chart-{ck}" data-chart-kind="{ck}" data-unit="{text(unit)}">{main}</div>'
        limits = " · ".join(element["limits"])
        legend = " · ".join(f'[{i+1}] {reference_text([ref], plan["language"])}' for i, ref in enumerate(declared)) or reference_text([], plan["language"])
        blocks[eid] = f'<section class="page-element composed-element role-{element["role"]} type-{kind}" id="element-{eid}" data-element-id="{eid}" data-element-type="{kind}" data-refs="{text(json.dumps(element["refs"], ensure_ascii=False))}"><header class="element-header"><h2>{text(element["title"])}{sources}</h2><p>{text(element["body"])}</p></header>{main}<footer class="element-footer"><p class="element-limits">{text(limits)}</p><small class="references">{text(legend)}</small></footer></section>'
        mapping.append({"page_id": page["id"], "element_id": eid, "selector": f"#element-{eid}", "refs": element["refs"], "displayed": element})
    def tree(node):
        if "element" in node:
            return blocks[node["element"]]
        axis = "columns" if node["type"] == "row" else "rows"
        weights = " ".join(f"minmax(0,{weight}fr)" for weight in node["weights"])
        return f'<div class="layout-node layout-{node["type"]}" style="grid-template-{axis}:{weights}">{"".join(tree(child) for child in node["children"])}</div>'
    return tree(page["tree"])


def render_document(plan):
    zh = plan["language"] == "zh-CN"
    pages = []
    mapping = []
    for index, page in enumerate(plan["pages"]):
        layout = page["layout"]
        blocks = []
        values = [e["value"] for e in page["elements"] if layout == "data" and e["value"] is not None]
        low, high = min([0] + values), max([0] + values)
        span = high - low or 1
        zero = -low / span * 100
        for n, element in enumerate(page["elements"] if layout != "composed" else []):
            identity = element["id"]
            attr = text(json.dumps(element["refs"], ensure_ascii=False))
            reference = text(reference_text(element["refs"], plan["language"]))
            if layout == "data":
                value = element["value"]
                label = ("缺失" if zh else "Unavailable") if value is None else str(value)
                bar = "" if value is None else f'<span class="bar {"negative" if value < 0 else "positive"}" style="left:{min(zero, (value-low)/span*100):.8f}%;width:{abs(value)/span*100:.8f}%"></span>'
                blocks.append(f'<tr id="element-{identity}" class="page-element data-row" data-element-id="{identity}" data-refs="{attr}" data-value="{text("null" if value is None else value)}"><th scope="row">{text(element["title"])}</th><td class="measure"><span class="track"><span class="zero" style="left:{zero:.8f}%"></span>{bar}</span><span class="value">{text(label)}</span></td><td class="data-explanation"><p>{text(element["body"])}</p><small class="references">{reference}</small></td></tr>')
            else:
                number = f'<span class="step-number">{n+1:02d}</span>' if layout == "sequence" else ""
                blocks.append(f'<section id="element-{identity}" class="page-element" data-element-id="{identity}" data-refs="{attr}">{number}<h2>{text(element["title"])}</h2><p>{text(element["body"])}</p><small class="references">{reference}</small></section>')
            mapping.append({"page_id": page["id"], "element_id": identity, "selector": f"#element-{identity}", "refs": element["refs"], "displayed": element})
        if layout == "composed":
            body = composed_body(page, plan, mapping)
        elif layout == "data":
            body = f'<table><caption>{"单位" if zh else "Unit"}: {text(page["unit"])}</caption><thead><tr><th>{"项目" if zh else "Item"}</th><th>{"数值" if zh else "Value"}</th><th>{"解释与依据" if zh else "Meaning and evidence"}</th></tr></thead><tbody>{"".join(blocks)}</tbody></table>'
        else:
            body = "".join(blocks)
        limits = "".join(f"<li>{text(limit)}</li>" for limit in page["limits"])
        pages.append(f'<article class="slide layout-{layout}" id="page-{page["id"]}" data-page-id="{page["id"]}" data-layout="{layout}" aria-labelledby="title-{page["id"]}"><header class="page-header"><div class="eyebrow"><span>{text(plan["title"])}</span><span>{index+1:02d} / {len(plan["pages"]):02d}</span></div><p class="question">{text(page["question"])}</p><h1 id="title-{page["id"]}">{text(page["title"])}</h1><p class="takeaway">{text(page["takeaway"])}</p></header><div class="page-content">{body}</div><footer class="page-footer"><div class="limitations"><strong>{"范围与限制" if zh else "Scope and limits"}</strong><ul>{limits}</ul></div><p class="page-references">{text(reference_text(page["refs"], plan["language"]))}</p></footer></article>')
        mapping.append({"page_id": page["id"], "selector": f"#page-{page['id']}", "refs": page["refs"], "displayed": {k: page[k] for k in ("layout", "question", "title", "takeaway", "limits", "unit", "tree") if k in page}})
    css = (ASSETS / "deck.css").read_text(encoding="utf-8")
    canvas = plan.get("canvas", DEFAULT_CANVAS)
    css += f'\n:root{{--canvas-width:{canvas["width"]}px;--canvas-height:{canvas["height"]}px}}\n@page{{size:{canvas["width"]/96:.8f}in {canvas["height"]/96:.8f}in;margin:0}}\n'
    js = (ASSETS / "deck.js").read_text(encoding="utf-8")
    labels = {"previous": "上一页" if zh else "Previous", "next": "下一页" if zh else "Next", "all": "阅读全部" if zh else "Read all", "deck": "返回演示" if zh else "Back to deck", "warning": "内容超出页面，请拆页；阅读全部可查看完整文本。" if zh else "Content exceeds the page. Split the page; Read all shows full text."}
    labels_json = json.dumps(labels, ensure_ascii=True)
    document = f'''<!doctype html>
<html lang="{plan['language']}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; img-src 'none'; connect-src 'none'; base-uri 'none'; form-action 'none'"><title>{text(plan['title'])}</title><style>{css}</style></head><body>
<div class="deck-shell"><main id="deck" aria-label="{text(plan['title'])}">{''.join(pages)}</main></div>
<nav aria-label="{'页面导航' if zh else 'Page navigation'}"><button id="previous" type="button">{labels['previous']}</button><output id="page-number" aria-live="polite"></output><button id="next" type="button">{labels['next']}</button><button id="read-all" type="button" aria-pressed="false">{labels['all']}</button></nav><p id="layout-warning" role="status" hidden>{labels['warning']}</p>
<noscript>{'脚本未运行，以下保留全部页面；未执行布局检查。' if zh else 'Scripts unavailable: all pages remain visible; layout unchecked.'}</noscript><script>const DECK_LABELS={labels_json};\n{js}</script></body></html>'''
    return document.encode("utf-8"), mapping


def output_path(directory):
    require_local(directory)
    absolute = directory.absolute()
    for part in [absolute, *absolute.parents]:
        if os.path.lexists(part):
            info = part.lstat()
            require(not stat.S_ISLNK(info.st_mode) and not getattr(info, "st_file_attributes", 0) & 0x400, "output path contains a link/reparse point")
    resolved = resolve_path(directory)
    require(not resolved.is_relative_to(PACKAGE), "output must be outside the installed Skill")
    require(not os.path.lexists(directory), "output already exists; choose a new directory")
    require(resolved.parent.is_dir(), "output parent must exist")
    return resolved


def render(plan_path, directory):
    source = local_path(plan_path)
    raw = source.read_bytes()
    plan = validate(json.loads(raw.decode("utf-8-sig"), object_pairs_hook=unique_keys, parse_constant=lambda v: (_ for _ in ()).throw(ValueError("nonfinite JSON constant"))))
    destination = output_path(directory)
    html, mapping = render_document(plan)
    canvas = plan.get("canvas", DEFAULT_CANVAS)
    payload = {"index.html": html, "plan.json": raw, "page-map.json": encode({"page_plan_version": VERSION, "plan_sha256": digest(raw), "canvas": canvas, "scope": "declared_mapping_not_semantic_verification", "elements": mapping})}
    receipt = {"renderer_contract_version": VERSION, "plan_sha256": digest(raw), "files": {name: digest(data) for name, data in payload.items()}, "page_count": len(plan["pages"]), "canvas": canvas, "browser_validation": "not_run", "semantic_validation": "not_run", "run_mutation": "not_performed"}
    payload["render-receipt.json"] = encode(receipt)
    destination.mkdir(exist_ok=False)
    for name, data in payload.items():
        with (destination / name).open("xb") as output:
            output.write(data)
    return {"valid": True, "output_directory": str(destination), **receipt}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    command = sub.add_parser("render")
    command.add_argument("plan", type=Path)
    command.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        result = render(args.plan, args.output)
    except (ValueError, OSError, UnicodeError, RecursionError) as exc:
        print(json.dumps({"valid": False, "error": str(exc), "browser_validation": "not_run", "semantic_validation": "not_run", "partial_output": "if_created_preserved"}, ensure_ascii=True))
        return 2
    print(json.dumps(result, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
