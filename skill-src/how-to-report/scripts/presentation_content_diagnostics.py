"""Observable page-content diagnostics; never a semantic or aesthetic score.

These observations are for the author/reviewer. They do not add slide text,
change geometry, infer business evidence, or certify the quality of a page.
"""
from __future__ import annotations

from collections import Counter
import json
import math
import xml.etree.ElementTree as ET


VERSION = "0.2"
INTENTS = {"cover", "section", "summary", "analysis", "comparison", "process",
           "architecture", "decision", "appendix", "demo"}
SPARSE_REVIEW_INTENTS = {"analysis", "comparison", "decision"}
LOW_CONTENT_EXEMPT = {"cover", "section", "demo"}
HEURISTICS = {"large_topology_canvas_fraction": .30, "few_topology_nodes": 3,
              "few_topology_edges": 2, "few_body_text_blocks": 1}
OCCUPANCY_THRESHOLDS = {"low_content_fraction": .30, "large_chart_region_fraction": .16,
                        "few_chart_records": 4}


def validate_page_intent(page):
    """Optional for existing documents; no page role is guessed from its text."""
    if "intent" in page and (not isinstance(page["intent"], str) or page["intent"] not in INTENTS):
        raise ValueError(f"page {page.get('id')}: intent must be one of {sorted(INTENTS)}")
    config = page.get("content_diagnostics", {})
    if not isinstance(config, dict) or set(config) - {"region_node_id", "thresholds"}:
        raise ValueError("content_diagnostics accepts region_node_id and thresholds")
    if "region_node_id" in config and (not isinstance(config["region_node_id"], str) or not config["region_node_id"].strip()):
        raise ValueError("content_diagnostics.region_node_id must be a nonempty layout node ID")
    thresholds = config.get("thresholds", {})
    if not isinstance(thresholds, dict) or set(thresholds) - set(OCCUPANCY_THRESHOLDS):
        raise ValueError("content_diagnostics.thresholds contains unsupported fields")
    for key, value in thresholds.items():
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
            raise ValueError(f"content_diagnostics.thresholds.{key} must be finite")
        if key == "few_chart_records":
            if type(value) is not int or not 1 <= value <= 1000:
                raise ValueError("few_chart_records must be an integer from 1 to 1000")
        elif not 0 <= value <= 1:
            raise ValueError(f"content_diagnostics.thresholds.{key} must be between zero and one")


def rectangle_union_area(rectangles):
    """Exact union of axis-aligned rectangles, avoiding overlap double counting."""
    boxes = [r for r in rectangles if r[2] > 0 and r[3] > 0]
    xs = sorted({v for x, _, w, _ in boxes for v in (x, x + w)})
    area = 0.
    for left, right in zip(xs, xs[1:]):
        spans = sorted((y, y + h) for x, y, w, h in boxes if x < right and x + w > left)
        length = 0.
        lower = upper = None
        for start, end in spans:
            if upper is None or start > upper:
                if upper is not None:
                    length += upper - lower
                lower, upper = start, end
            else:
                upper = max(upper, end)
        if upper is not None:
            length += upper - lower
        area += (right - left) * length
    return area


def _clip(rect, canvas):
    x, y, w, h = rect
    x2, y2 = min(canvas[0], x + w), min(canvas[1], y + h)
    x, y = max(0., x), max(0., y)
    return [x, y, max(0., x2 - x), max(0., y2 - y)]


def _rotated_bounds(rect, angle, center):
    if not angle:
        return rect
    x, y, w, h = rect
    radians = math.radians(angle)
    c, s = math.cos(radians), math.sin(radians)
    cx, cy = center
    points = [(cx + (px-cx)*c - (py-cy)*s, cy + (px-cx)*s + (py-cy)*c)
              for px, py in ((x, y), (x+w, y), (x+w, y+h), (x, y+h))]
    left, right = min(p[0] for p in points), max(p[0] for p in points)
    top, bottom = min(p[1] for p in points), max(p[1] for p in points)
    return [left, top, right-left, bottom-top]


def _text_region(item, facts, tokens):
    # The same role resolver and DrawingML estimator as SceneRenderer.text.
    from presentation_document import resolve_text
    from presentation_svg import runtime_helpers
    from presentation_typography import measure_text_block, resolve_text_style
    role = item.get("role", "body")
    known = {*tokens["font"]["sizes"], *tokens["font"].get("textStyles", {})}
    style = resolve_text_style(tokens, role if role in known else "body", item.get("style"))
    runs = item.get("runs", [{"text": item.get("text", "")}])
    text = "".join(resolve_text(run["text"], facts) for run in runs)
    if not text.strip():
        return None
    style["weight"] = max(resolve_text_style(tokens, role if role in known else "body",
                          {"weight": run.get("weight", style["weight"])})["weight"] for run in runs)
    x, y, w, h = item["frame"]
    left, top, right, bottom = style["insets"]
    measurement = measure_text_block(text, w-left-right, style, runtime_helpers())
    width, height = max(measurement["widths"], default=0), measurement["height"]
    dx = {"left": 0, "center": (w-left-right-width)/2, "right": w-left-right-width}[style["align"]]
    dy = {"top": 0, "middle": (h-top-bottom-height)/2, "bottom": h-top-bottom-height}[style["vertical_anchor"]]
    rectangle = _rotated_bounds([x+left+dx, y+top+dy, width, height], item.get("rotation", 0), (x+w/2, y+h/2))
    line_rectangles = []
    for line, line_width, baseline in zip(measurement["lines"], measurement["widths"], measurement["baselines"]):
        if not line.strip():
            continue
        offset = {"left": 0, "center": (w-left-right-line_width)/2,
                  "right": w-left-right-line_width}[style["align"]]
        line_rectangles.append(_rotated_bounds(
            [x+left+offset, y+top+dy+baseline-style["font_size"]*.8, line_width, style["font_size"]*1.05],
            item.get("rotation", 0), (x+w/2, y+h/2)))
    return {"id": item["id"], "role": role, "text": text, "line_count": len(measurement["lines"]),
            "rectangle": [round(v, 4) for v in rectangle],
            "line_rectangles": [[round(v, 4) for v in r] for r in line_rectangles]}


def _intersection(rect, region):
    x, y = max(rect[0], region[0]), max(rect[1], region[1])
    return [x, y, max(0., min(rect[0]+rect[2], region[0]+region[2])-x),
            max(0., min(rect[1]+rect[3], region[1]+region[3])-y)]


def _region(page, canvas, layout_report):
    identifier = page.get("content_diagnostics", {}).get("region_node_id")
    if identifier is None:
        return [0., 0., *canvas], "canvas"
    nodes = (layout_report or {}).get("nodes", [])
    matches = [node for node in nodes if node.get("id") == identifier]
    if len(matches) != 1:
        raise ValueError(f"content_diagnostics.region_node_id: no unique solved node {identifier!r}")
    region = _clip(matches[0]["frame"], canvas)
    if region[2] * region[3] <= 0:
        raise ValueError("content_diagnostics region has no visible area")
    return region, "layout_node:" + identifier


def _ring_rectangles(plot, hole):
    """Midpoint strip approximation; no chart-frame or hole counted as marks."""
    radius = min(plot["width"], plot["height"])/2
    cx, cy = plot["x"]+plot["width"]/2, plot["y"]+plot["height"]/2
    inner = radius * hole/100
    count = 128
    step = 2*radius/count
    rectangles = []
    for index in range(count):
        y = cy-radius+index*step
        dy = y+step/2-cy
        outer_x = math.sqrt(max(0., radius*radius-dy*dy))
        inner_x = math.sqrt(max(0., inner*inner-dy*dy))
        if inner_x:
            rectangles.extend([[cx-outer_x, y, outer_x-inner_x, step], [cx+inner_x, y, outer_x-inner_x, step]])
        else:
            rectangles.append([cx-outer_x, y, 2*outer_x, step])
    return rectangles


def _chart_content(item, svg_index):
    """Read this build's actual classic Chart fallback, not a second chart layout."""
    node = svg_index.get(item["id"])
    if node is None or node.get("transform"):
        return None
    metadata = next((child for child in node if child.tag.rsplit("}", 1)[-1] == "metadata"), None)
    if metadata is None:
        # The registered basic bar/column assets emit direct SVG marks, without
        # the native Chart JSON payload. Other asset geometries stay unknown.
        kind = str(item.get("asset", "")).removeprefix("chart.")
        if kind not in {"bar", "column"}:
            return None
        payload = dict(zip(("x", "y", "width", "height"), item["frame"]))
        plot = None
    else:
        payload = json.loads(metadata.text)
        kind, plot = payload.get("type"), payload.get("plot_area")
        if kind not in {"pie", "doughnut", "bar", "column"} or not isinstance(plot, dict):
            return None
    rectangles = []
    if kind in {"pie", "doughnut"}:
        rectangles.extend(_ring_rectangles(plot, payload.get("hole_size", 0)))
    from presentation_svg import runtime_helpers
    runtime_helpers()
    from text_measure import measure_text
    for child in node:
        tag = child.tag.rsplit("}", 1)[-1]
        if tag == "rect":
            rect = [float(child.get(key, 0)) for key in ("x", "y", "width", "height")]
            # Only the rendered chart/plot surfaces are excluded; marks and legend keys remain.
            surfaces = [[payload[key] for key in ("x", "y", "width", "height")]]
            if plot is not None:
                surfaces.append([plot[key] for key in ("x", "y", "width", "height")])
            if any(all(abs(a-b) < .01 for a, b in zip(rect, surface)) for surface in surfaces):
                continue
            if child.get("fill", "none") != "none":
                rectangles.append(rect)
        elif tag == "text":
            text = "".join(child.itertext())
            if not text.strip():
                continue
            size = float(child.get("font-size", 12))
            width = measure_text(text, size=size, family=child.get("font-family", "Arial"),
                                 weight=child.get("font-weight", "400"))
            x, y = float(child.get("x", 0)), float(child.get("y", 0))
            x -= {"middle": width/2, "end": width}.get(child.get("text-anchor"), 0)
            rectangles.append([x, y-size*.8, width, size*1.05])
    return rectangles


def _occupancy(page, scene, texts, canvas, layout_report, rendered_svg):
    region, source = _region(page, canvas, layout_report)
    area = region[2]*region[3]
    thresholds = {**OCCUPANCY_THRESHOLDS, **page.get("content_diagnostics", {}).get("thresholds", {})}
    result = {"region": region, "region_source": source, "region_area": area,
              "thresholds": thresholds, "semantic_quality": "not_assessed",
              "method": "union of estimated text-line rectangles, rendered classic-chart marks and topology node envelopes; circle marks use 128 midpoint strips",
              "limits": "Not pixel ink or information value. Text uses shared font estimates; rotated text and topology use enclosing rectangles. Backgrounds, decoration, chart grids and unclassified shape paths are excluded."}
    if scene is None:
        return {**result, "status": "not_assessable", "allocated_fraction": None,
                "estimated_content_fraction": None, "estimated_blank_fraction": None,
                "unknown_visual_ids": [page["id"]]}
    svg_index = {node.get("id"): node for node in ET.fromstring(rendered_svg).iter() if node.get("id")} if rendered_svg else {}
    allocated, content, unknown, chart_observations = [], [], [], []
    allocations, text_rectangles, chart_rectangles, topology_rectangles = [], [], [], []
    text_index = {text["id"]: text for text in texts}

    def allocate(identifier, kind, rectangle):
        allocated.append(rectangle)
        visible = _intersection(rectangle, region)
        if visible[2]*visible[3] > 0:
            allocations.append({"id": identifier, "kind": kind, "rectangle": rectangle,
                                "region_fraction": round(visible[2]*visible[3]/area, 6)})

    def visit(items, component_frame=None):
        for item in items:
            meta = item.get("metadata", {})
            meta = meta if isinstance(meta, dict) else {}
            if item.get("opacity") == 0 or meta.get("decorative") is True:
                continue
            kind = item.get("type")
            box = item.get("frame")
            visible_box = (_rotated_bounds(box, item.get("rotation", 0),
                           (box[0]+box[2]/2, box[1]+box[3]/2)) if box else None)
            current_component = meta.get("component_frame", component_frame)
            if "component_frame" in meta:
                allocate(item["id"], "component", meta["component_frame"])
                if meta.get("component") in {"partition", "comparison"}:
                    # These data components lower to ordinary shapes, not chart
                    # objects. Their text remains measurable below, but excluding
                    # their marks must not certify a complete content estimate.
                    unknown.append({"id": item["id"], "frame": meta["component_frame"],
                        "reason": "shape-based data component marks not supported by occupancy estimator"})
            if kind in {"text", "chart", "image"} and box:
                allocate(item["id"], kind, visible_box)
            topology = meta.get("topology_report")
            if isinstance(topology, dict):
                topology_rectangles.extend(r for boxes in topology.get("occupied_frames", {}).values() for r in boxes)
            if kind == "text" and item["id"] in text_index:
                text_rectangles.extend(text_index[item["id"]]["line_rectangles"])
            elif kind == "chart":
                marks = _chart_content(item, svg_index)
                if marks is None:
                    unknown.append({"id": item["id"], "frame": visible_box, "reason": "chart marks not supported by occupancy estimator"})
                else:
                    chart_rectangles.extend(marks)
                outer = current_component or box
                clipped = _intersection(outer, region)
                chart_observations.append({"id": item["id"], "supplied_record_count": _records(item),
                    "allocation_region_fraction": round(clipped[2]*clipped[3]/area, 6),
                    "allocation_source": "component_frame" if current_component else "chart_frame",
                    "mark_estimate": "available" if marks is not None else "unknown"})
            elif kind == "image":
                unknown.append({"id": item["id"], "frame": visible_box, "reason": "image interior is not interpreted"})
            if kind == "group":
                visit(item.get("children", []), current_component)

    visit(scene.get("elements", []))
    content = text_rectangles + chart_rectangles + topology_rectangles
    def fraction(rectangles):
        return min(1., rectangle_union_area([_intersection(r, region) for r in rectangles])/area)
    known = fraction(content)
    unknown = [record for record in unknown if math.prod(_intersection(record["frame"], region)[2:]) > 0]
    upper = fraction(content+[record["frame"] for record in unknown])
    complete = not unknown
    result.update(status="complete_estimate" if complete else "partial", allocated_fraction=round(fraction(allocated), 6),
                  estimated_content_fraction=round(known, 6) if complete else None,
                  estimated_blank_fraction=round(1-known, 6) if complete else None,
                  known_content_fraction=round(known, 6), content_fraction_bounds=[round(known, 6), round(upper, 6)],
                  unknown_visual_ids=[record["id"] for record in unknown], unknown_visuals=unknown,
                  allocation_regions=allocations, estimated_text_line_fraction=round(fraction(text_rectangles), 6),
                  known_chart_footprint_fraction=round(fraction(chart_rectangles), 6),
                  topology_node_envelope_fraction=round(fraction(topology_rectangles), 6),
                  charts=chart_observations)
    return result


def _records(chart):
    """Count supplied observations, not their inferred business importance."""
    data = chart.get("data", chart)
    series = data.get("series")
    if isinstance(series, list):
        return sum(len(s.get("values", s.get("points", []))) for s in series if isinstance(s, dict))
    for key in ("points", "ranges", "rows", "regions", "sites", "links", "paths"):
        if isinstance(data.get(key), list):
            return len(data[key])
    if isinstance(data.get("values"), list):
        return sum(len(row) if isinstance(row, list) else 1 for row in data["values"])
    return 0


def analyze_page(page, scene, tokens, facts=None, *, layout_report=None, rendered_svg=None):
    """Inspect an already expanded, successfully rendered scene without edits."""
    validate_page_intent(page)
    facts = facts or {}
    canvas = (tokens["canvas"]["width"], tokens["canvas"]["height"])
    area = canvas[0] * canvas[1]
    intent = page.get("intent")
    result = {"version": VERSION, "page_id": page["id"], "intent": intent,
              "job": page.get("job"), "semantic_quality": "not_assessed",
              "scope": "measured text rectangles and declared visual data/graph structure; not pixel ink density or information value",
              "heuristics": dict(HEURISTICS), "observations": {}, "warnings": []}

    def warn(code, ids, observation, question):
        result["warnings"].append({"code": code, "severity": "review", "object_ids": ids,
                                   "observation": observation, "review_question": question})

    if intent is None:
        warn("intent_not_declared", [page["id"]], "No page.intent was declared; page type was not inferred.",
             "Declare this page's purpose and review it against page.job before judging whether its whitespace is useful.")
    if scene is None:
        result.update(status="not_assessable", review_required=True)
        result["observations"] = {"reason": "This page has no expanded scene available; source/template interiors are not estimated from a container."}
        result["occupancy"] = _occupancy(page, scene, [], canvas, layout_report, rendered_svg)
        return result

    from presentation_document import resolve_value
    scene = resolve_value(scene, facts)

    texts, charts, images, topologies, skipped = [], [], [], [], []

    def visit(items):
        for item in items:
            metadata = item.get("metadata", {})
            if item.get("opacity") == 0 or isinstance(metadata, dict) and metadata.get("decorative") is True:
                skipped.append(item["id"])
                continue
            topology = metadata.get("topology_report") if isinstance(metadata, dict) else None
            if isinstance(topology, dict):
                labels = [m["label"].strip() for m in topology.get("measurements", {}).values() if m.get("label", "").strip()]
                counts = Counter(labels)
                box = topology["bounds"]
                occupied = [r for rectangles in topology.get("occupied_frames", {}).values() for r in rectangles]
                topologies.append({"id": item["id"], "layout": topology["layout"],
                    "node_count": topology["node_count"], "edge_count": topology["edge_count"],
                    "allocated_rectangle": box, "allocated_canvas_fraction": round(box[2]*box[3]/area, 6),
                    "node_rectangle_union_canvas_fraction": round(rectangle_union_area([_clip(r, canvas) for r in occupied])/area, 6),
                    "repeated_labels": {label: count for label, count in counts.items() if count > 1},
                    "has_interior": "interior_bounds" in topology})
            kind = item.get("type")
            if kind == "text":
                region = _text_region(item, facts, tokens)
                if region is not None:
                    texts.append(region)
            elif kind == "chart":
                charts.append({"id": item["id"], "asset": item.get("asset", item.get("chart_type")),
                               "supplied_record_count": _records(item)})
            elif kind == "image":
                images.append({"id": item["id"], "content": "not_interpreted"})
            if kind == "group":
                visit(item.get("children", []))

    visit(scene.get("elements", []))
    body = [t for t in texts if t["role"] not in {"title", "hero", "chapter", "heading", "caption", "dataCaption"}]
    text_area = rectangle_union_area([_clip(t["rectangle"], canvas) for t in texts])
    result["observations"] = {"text_block_count": len(texts), "body_text_block_count": len(body),
        "text_rectangle_union_area": round(text_area, 4), "canvas_area": area,
        "text_rectangle_union_canvas_fraction": round(text_area/area, 6), "text_regions": texts,
        "data_visualizations": charts, "supplied_data_record_count": sum(c["supplied_record_count"] for c in charts),
        "images": images, "topologies": topologies, "excluded_invisible_or_declared_decorative": skipped,
        "excluded_geometry": "unlabelled shapes, connector paths, container backgrounds and chart frames are not counted as text content"}
    occupancy = _occupancy(page, scene, texts, canvas, layout_report, rendered_svg)
    result["occupancy"] = occupancy
    if occupancy["status"] == "partial":
        warn("measurement_incomplete", occupancy["unknown_visual_ids"],
             "Some visible data-visualization or image interiors are not supported by the footprint estimator; total content/blank fractions remain unknown.",
             "Inspect these objects in the rendered page. Do not read the known-only footprint or its estimated bounds as a complete blank-area measurement.")
    if intent not in LOW_CONTENT_EXEMPT:
        if occupancy["estimated_content_fraction"] is not None and occupancy["estimated_content_fraction"] < occupancy["thresholds"]["low_content_fraction"]:
            warn("low_content_occupancy", [page["id"]],
                 f"Estimated content occupies {occupancy['estimated_content_fraction']:.1%} of {occupancy['region_source']}; estimated blank area is {occupancy['estimated_blank_fraction']:.1%}.",
                 "Review the page's agreed topic and required evidence. Could related information fit here or should this page be combined? Do not enlarge marks, add decoration or invent facts to meet a percentage.")
        for chart in occupancy["charts"]:
            if chart["allocation_region_fraction"] >= occupancy["thresholds"]["large_chart_region_fraction"] and chart["supplied_record_count"] <= occupancy["thresholds"]["few_chart_records"]:
                warn("large_chart_few_records", [chart["id"]], chart,
                     "This large chart/component presents few supplied values. Would a compact chart leave useful space for the rest of this page's topic? Record count is not information value.")
    if intent in SPARSE_REVIEW_INTENTS and len(body) <= HEURISTICS["few_body_text_blocks"] and not charts and not images and not any(t["edge_count"] for t in topologies):
        warn("limited_analysis_support", [t["id"] for t in texts],
             "Declared analytical/decision page has at most one body text block, no data chart/image and no graph edge.",
             "Does this page show the evidence, comparison or reasoning needed for its task? A single supported conclusion can be intentional; do not add filler.")
    if intent not in LOW_CONTENT_EXEMPT:
        for topology in topologies:
            if (topology["allocated_canvas_fraction"] >= HEURISTICS["large_topology_canvas_fraction"]
                and topology["node_count"] <= HEURISTICS["few_topology_nodes"]
                and topology["edge_count"] <= HEURISTICS["few_topology_edges"] and not topology["has_interior"]):
                warn("large_frame_few_graph_items", [topology["id"]],
                     f"Topology uses {topology['allocated_canvas_fraction']:.1%} of canvas for {topology['node_count']} nodes and {topology['edge_count']} edges.",
                     "Is this a useful main visual, or should a smaller intrinsic layout leave room for explanation? Frame occupancy does not establish information value.")
            if topology["repeated_labels"]:
                warn("repeated_topology_labels", [topology["id"]], topology["repeated_labels"],
                     "Do repeated labels denote distinct entities or repeat the same content? Confirm their meaning rather than automatically deleting them.")
    result.update(status="review_required" if result["warnings"] else "observed", review_required=bool(result["warnings"]))
    return result
