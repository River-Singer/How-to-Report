"""Measured qualitative cycle: thick curved arrows, native paths and text.

Every stage owns one disjoint angular sector. Labels occupy an axis-aligned
rectangle proven inside the annular body, before its widened arrowhead. This
is a bounded 3..6-stage layout, not a quantitative doughnut or a shape boolean
engine. Coordinates are calculated from the allocated component frame.
"""
from __future__ import annotations

import math

from presentation_document import resolve_text
from presentation_palette import contrast_ratio, describe_palette, label_ink, palette_color
from presentation_typography import measure_text_block
from report_ppt import TemplateInputError


def point(center, radius, angle):
    return (center[0] + radius * math.cos(angle), center[1] + radius * math.sin(angle))


def rect_in_sector(box, center, inner, outer, start, sweep):
    """Exact containment of a rectangle in an annular sector <= 180 degrees.

The outer disk and angular wedge are convex (corner checks suffice); the
inner disk is excluded by the closest point of the whole rectangle.
"""
    x, y, w, h = box
    cx, cy = center
    nearest = (max(x, min(cx, x + w)), max(y, min(cy, y + h)))
    if math.hypot(nearest[0] - cx, nearest[1] - cy) < inner - 1e-8:
        return False
    sign = 1 if sweep > 0 else -1
    for px, py in ((x, y), (x+w, y), (x, y+h), (x+w, y+h)):
        if math.hypot(px-cx, py-cy) > outer + 1e-8:
            return False
        delta = (sign * (math.atan2(py-cy, px-cx) - start)) % math.tau
        if delta > abs(sweep) + 1e-8:
            return False
    return True


def _path(center, radius, start, sweep, head):
    sign = 1 if sweep > 0 else -1
    end, base = start + sweep, start + sweep - sign * head
    outer, inner = .92 * radius, .44 * radius
    a, b = point(center, outer, start), point(center, outer, base)
    wing1, tip, wing2 = point(center, radius, base), point(center, .68*radius, end), point(center, .36*radius, base)
    c, d = point(center, inner, base), point(center, inner, start)
    fmt = lambda p: f"{p[0]:.8f} {p[1]:.8f}"
    flag = 1 if sign > 0 else 0
    path = (f"M {fmt(a)} A {outer:.8f} {outer:.8f} 0 0 {flag} {fmt(b)} "
            f"L {fmt(wing1)} L {fmt(tip)} L {fmt(wing2)} L {fmt(c)} "
            f"A {inner:.8f} {inner:.8f} 0 0 {1-flag} {fmt(d)} Z")
    points = [a, b, wing1, tip, wing2, c, d]
    for angle in (0, math.pi/2, math.pi, math.pi*1.5):
        if (sign * (angle-start)) % math.tau <= abs(base-start):
            points.extend((point(center, outer, angle), point(center, inner, angle)))
    xs, ys = zip(*points)
    return path, [min(xs), min(ys), max(xs)-min(xs), max(ys)-min(ys)]


def _color(topology, value):
    if not isinstance(value, str):
        topology.fail("cycle stage color must be a semantic role or hexadecimal string", path="nodes.fill")
    if isinstance(value, str) and len(value) == 7 and value.startswith("#"):
        try:
            int(value[1:], 16)
            return value
        except ValueError:
            pass
    selected = palette_color(topology.tokens, value)
    if selected is not None:
        return selected
    role = topology.tokens.get("color", {}).get("roles", {}).get(value, value)
    result = topology.tokens.get("theme", {}).get("slots", {}).get(role)
    if result is None:
        raise TemplateInputError(f"unknown cycle stage color: {value!r}")
    return result


def _label(topology, node, center, radius, angle, start, sweep):
    style = topology.node_style(node)
    value = resolve_text(node["label"], topology.facts)
    left, top, right, bottom = style["insets"]
    # Padding is geometric clearance around the complete text box, not a
    # license to overlap the hole or squeeze the text into the arrowhead.
    clearance = topology.node_pad
    inner, outer = .44*radius + clearance, .92*radius - clearance
    center_label = point(center, .68*radius, angle)
    candidates = []
    # Width candidates are deterministic; measurement keeps exact characters,
    # font size, paragraph gaps and explicit newlines. Prefer fewer lines.
    for step in range(96, 0, -1):
        width = radius * 1.6 * step / 96
        if width <= left + right:
            continue
        try:
            measured = measure_text_block(value, width-left-right, style, topology.helpers)
        except ValueError:
            continue
        height = max(measured["height"], len(measured["lines"]) * style["font_size"]) + top + bottom
        box = [center_label[0]-width/2, center_label[1]-height/2, width, height]
        if rect_in_sector(box, center, inner, outer, start, sweep):
            candidates.append((len(measured["lines"]), -width, box, measured))
    if not candidates:
        topology.fail("arrow-ring label cannot fit its measured annular safe area; enlarge the component or shorten the label",
                      node_id=node["id"], reason="text_overflow", path="nodes.label", available_radius=radius,
                      font_size=style["font_size"])
    _, _, box, measured = min(candidates, key=lambda candidate: candidate[:2])
    topology.measurements[node["id"]] = {"label": measured["text"], "lines": len(measured["lines"]),
        "text_width": max(measured["widths"]), "required_height": box[3], "font_size": style["font_size"]}
    return box, style


def lower_arrow_ring(topology):
    count = len(topology.nodes)
    if not 3 <= count <= 6:
        topology.fail("arrow-ring supports 3..6 qualitative stages", path="nodes", reason="capacity")
    unused = set(topology.item) & {"node_width", "node_height"}
    if unused or set(topology.supplied_style) & {"fill", "stroke", "stroke_width", "marker_fill", "marker_color"}:
        topology.fail("arrow-ring computes stage geometry and palette fills; node_width/node_height and paint style are unsupported", reason="unsupported_fields")
    if topology.item.get("arrow", True) is False or any(edge.get("arrow", True) is False for edge in topology.edges):
        topology.fail("arrow-ring encodes a directed cycle and cannot disable arrowheads", path="arrow")
    for node in topology.nodes:
        if set(node) & {"width", "height", "shape", "stroke"}:
            topology.fail("arrow-ring computes curved stage geometry; width/height/shape/stroke are unsupported", node_id=node["id"], reason="unsupported_fields")
    x, y, w, h = topology.area
    radius = min(w, h) / 2
    center = (x+w/2, y+h/2)
    ids = [node["id"] for node in topology.nodes]
    sign = 1 if (ids[0], ids[1]) in {(e["from"], e["to"]) for e in topology.edges} else -1
    step = math.tau / count
    # A relative angle keeps small and large rings similar; the radial band
    # remains thick, while the wider shoulders read as an actual arrowhead.
    gap, head = math.radians(5), min(math.radians(24), step*.27)
    sweep = step-gap
    body = sweep-head
    colors = topology.tokens.get("color", {}).get("palette", {}).get("categorical")
    colors = colors or describe_palette("report-default")["categorical"]
    stages, labels, segments = [], [], []
    for index, node in enumerate(topology.nodes):
        angle = -math.pi/2 + index*step
        start = angle-sign*body/2
        path, bounds = _path(center, radius, start, sign*sweep, head)
        box, style = _label(topology, node, center, radius, angle, start, sign*body)
        fill = _color(topology, node.get("fill", colors[index % len(colors)]))
        # Respect explicit text ink; otherwise compute accessible ink for the
        # actual selected palette stage fill rather than assuming white.
        if "color" not in node.get("style", {}) and "color" not in topology.supplied_style:
            style = {**style, "color": label_ink(fill)}
        topology.boxes[node["id"]] = box
        topology.occupied[node["id"]] = [box]
        stages.append({"id": topology.shape_id(node["id"]), "type": "shape", "shape": "path",
                       "frame": bounds, "d": path, "fill": fill, "stroke": "none"})
        labels.append({"id": topology.cid("node--"+node["id"]+"--label"), "type": "text", "frame": box,
                       "text": node["label"], "role": node.get("role", topology.item.get("role", "body")), "style": style})
        segments.append({"node_id": node["id"], "start_radians": start, "sweep_radians": sign*sweep,
                         "body_sweep_radians": sign*body, "head_radians": head, "fill": fill,
                         "label_contrast_ratio": round(contrast_ratio(fill, _color(topology, style["color"])), 3),
                         "shape_bounds": bounds, "label_safe_frame": box})
    topology.children.extend(stages + labels)
    topology.report.update(variant="arrow-ring", algorithm="equal-angle-annular-arrows-v1", center=list(center), radius=radius,
        direction="clockwise" if sign > 0 else "counterclockwise", gap_radians=gap,
        body_radii=[.44*radius, .92*radius], label_clearance=topology.node_pad, segments=segments,
        encoding="qualitative ordered stages; equal angular allocation does not encode numeric shares",
        routing="filled native custom shapes embody directed edges; no overlaid straight connectors")
