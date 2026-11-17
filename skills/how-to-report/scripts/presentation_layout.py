"""Deterministic, bounded row/column/grid layout for editable presentation scenes.

Widths flow down the tree and measured heights flow up. This is a documented
subset, rather than a CSS implementation; no geometry is written to the author.
"""
from __future__ import annotations

import copy
import math
import re

from report_ppt import TemplateInputError
from presentation_svg import runtime_helpers, scene_contracts
from presentation_typography import measure_text_block, resolve_text_style


VERSION = "0.1"
ALGORITHM = "width-down-height-up-spans-v4"
TOLERANCE = .01
PRECISION = 6
EPSILON = .000001
LIMITS = {"nodes": 256, "depth": 12, "children": 64, "tracks": 12}
ALIGN = {"start", "center", "end", "stretch"}
COMMON = {"id", "type", "width", "height", "min_width", "max_width", "min_height", "max_height",
          "basis", "grow", "shrink", "align_self", "column_span", "metadata", "source_ref", "content_ref", "relation_ref"}
CONTAINER = {"children", "padding", "gap", "align", "justify", "surface", "connect"}


class LayoutError(TemplateInputError):
    """An author-addressable syntax, dependency, or capacity diagnostic."""

    def __init__(self, diagnostic):
        self.diagnostic = copy.deepcopy(diagnostic)
        super().__init__(f"{diagnostic.get('path', 'layout')}: {diagnostic['reason']}")


def _fail(node, path, reason, *, axis=None, available=None, required=None, code="layout_invalid"):
    if any(value is not None and not math.isfinite(value) for value in (available, required)):
        available, required = None, None
        reason += "; size arithmetic exceeds finite range"
        code = "layout_invalid"
    diagnostic = {"code": code, "node_id": node.get("id") if isinstance(node, dict) else None,
                  "path": path, "reason": reason}
    if axis is not None:
        diagnostic["axis"] = axis
    if available is not None:
        diagnostic["available"] = available
    if required is not None:
        diagnostic["required"] = required
    if available is not None and required is not None:
        diagnostic["overflow_px"] = max(0, required - available)
        diagnostic["suggestions"] = [{"action": "increase_width" if axis == "x" else "increase_height",
                                       "minimum": required}, {"action": "split_at_node_boundary"}]
    if code == "layout_overflow" and isinstance(node, dict):
        pending, causes = [node], []
        while pending:
            current = pending.pop()
            if current.get("type") == "leaf":
                causes.append(current["id"])
            pending.extend(reversed(current.get("children", [])))
        diagnostic["causes"] = causes
    raise LayoutError(diagnostic)


def _number(value, node, path, minimum=0, positive=False):
    try:
        finite = isinstance(value, (int, float)) and math.isfinite(value)
    except OverflowError:
        finite = False
    if (isinstance(value, bool) or not finite
            or value < minimum or positive and value == 0):
        _fail(node, path, "expected a positive finite number" if positive else f"expected a finite number >= {minimum}")
    return float(value)


def _padding(node):
    value = node.get("padding", 0)
    padding = [value] * 4 if isinstance(value, (int, float)) else list(value)
    accent = node.get("surface", {}).get("accent")
    if accent:
        reserve = accent.get("thickness", 4) + accent.get("gap", 12)
        edges = {"rail": (0,), "rule": (1,), "bracket": (0, 1, 3)}[accent["kind"]]
        for edge in edges:
            padding[edge] = max(padding[edge], reserve)
    return padding


def _grid_cells(children, count):
    """Ordered, non-dense placement. An item never splits across rows."""
    row, column, cells = 0, 0, []
    for child in children:
        span = child.get("column_span", 1)
        if column + span > count:
            row, column = row + 1, 0
        cells.append((row, column, span))
        column += span
    return cells


def _sequence_id(node, left, right):
    return f"{node['id']}--link-{left['id']}-to-{right['id']}"


def _span_requirements(values, columns, cells, requirements, gap, node, path, *, strict=True):
    """Monotone bounded constraints; fr weights split a span deficit, auto uses 1.

    This conservative algorithm is not CSS intrinsic track negotiation. Raising
    an overlapping constraint never reduces a previously satisfied minimum.
    """
    for (_, column, span), required in zip(cells, requirements):
        indices = list(range(column, column + span))
        available = sum(values[i] for i in indices) + gap * (span - 1)
        deficit = required - available
        if deficit <= TOLERANCE:
            continue
        flexible = [i for i in indices if not isinstance(columns[i], (int, float))]
        if not flexible:
            if strict:
                _fail(node, path, "fixed spanned tracks violate child minimum width", axis="x", available=available,
                      required=required, code="layout_overflow")
            continue
        weights = [columns[i]["fr"] if isinstance(columns[i], dict) else 1 for i in flexible]
        scale = max(weights)
        weights = [weight / scale for weight in weights]
        total = sum(weights)
        for i, weight in zip(flexible, weights):
            values[i] += deficit * weight / total
    return values


def _dimension(node, axis):
    value = node.get("width" if axis == "x" else "height", "auto")
    return None if value == "auto" else float(value)


def _limits(node, axis):
    suffix = "width" if axis == "x" else "height"
    return float(node.get("min_" + suffix, 0)), float(node.get("max_" + suffix, math.inf))


def _clamp(value, node, axis):
    low, high = _limits(node, axis)
    return max(low, min(high, value))


def _quantize(value):
    return round(float(value), PRECISION)


def validate_layout_page(page):
    """Validate syntax without evaluated facts, runtime imports, or author mutation."""
    if not isinstance(page, dict) or page.get("kind") != "layout" or page.get("layout_version") != VERSION:
        _fail(page, "layout", 'expected kind="layout" and layout_version="0.1"')
    if "elements" in page or "components" in page:
        _fail(page, "layout", "layout pages use one layout tree, without scene elements/components")
    identifiers, surfaces, active = set(), [], set()

    def finite_json(value, node, path, visiting=None, depth=0):
        if visiting is None:
            visiting = set()
        if depth > 128 or isinstance(value, (dict, list)) and id(value) in visiting:
            _fail(node, path, "payload must be acyclic and at most 128 levels deep")
        if isinstance(value, float) and not math.isfinite(value):
            _fail(node, path, "non-finite input is unsupported")
        if isinstance(value, (dict, list)):
            visiting.add(id(value))
        if isinstance(value, dict):
            for key, child in value.items():
                finite_json(child, node, path + "." + str(key), visiting, depth + 1)
        elif isinstance(value, list):
            for index, child in enumerate(value):
                finite_json(child, node, f"{path}[{index}]", visiting, depth + 1)
        if isinstance(value, (dict, list)):
            visiting.remove(id(value))

    def tracks(value, node, path):
        if not isinstance(value, list) or not 1 <= len(value) <= LIMITS["tracks"]:
            _fail(node, path, "tracks must be a nonempty array of at most 12 entries")
        for index, track in enumerate(value):
            location = f"{path}[{index}]"
            if track == "auto":
                continue
            if isinstance(track, dict) and set(track) == {"fr"}:
                _number(track["fr"], node, location + ".fr", positive=True)
            else:
                _number(track, node, location, positive=True)

    def visit(node, path, depth, parent=None):
        if depth > LIMITS["depth"]:
            _fail(node, path, "layout depth exceeds 12")
        if not isinstance(node, dict) or id(node) in active:
            _fail(node, path, "expected an acyclic layout node object")
        identifier, kind = node.get("id"), node.get("type")
        if not isinstance(identifier, str) or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_.:-]*", identifier):
            _fail(node, path + ".id", "expected a stable SVG-compatible ID")
        if identifier in identifiers:
            _fail(node, path + ".id", "duplicate layout ID")
        identifiers.add(identifier)
        if len(identifiers) > LIMITS["nodes"]:
            _fail(node, path, "layout node count exceeds 256")
        if not isinstance(kind, str) or kind not in {"row", "column", "grid", "leaf"}:
            _fail(node, path + ".type", "expected row, column, grid or leaf")
        allowed = COMMON | ({"element", "aspect_ratio", "sizing"} if kind == "leaf" else CONTAINER)
        if kind == "grid":
            allowed |= {"columns", "rows", "uniform_components", "row_gap", "column_gap"}
        unknown = set(node) - allowed
        if unknown:
            _fail(node, path, f"unsupported layout fields {sorted(unknown)}")
        if "column_span" in node:
            span = node["column_span"]
            if not parent or parent["type"] != "grid":
                _fail(node, path + ".column_span", "column_span requires a direct grid parent")
            if isinstance(parent["columns"], dict):
                _fail(node, path + ".column_span", "column_span requires explicit columns; auto_fit is unsupported")
            if type(span) is not int or not 1 <= span <= len(parent["columns"]):
                _fail(node, path + ".column_span", "column_span must be an integer from 1 to the column count")
            if span > 1 and parent.get("uniform_components"):
                _fail(node, path + ".column_span", "column_span cannot combine with uniform_components")
        for field in ("metadata", "source_ref", "content_ref", "relation_ref"):
            if field in node:
                finite_json(node[field], node, path + "." + field)
        for axis in ("x", "y"):
            suffix = "width" if axis == "x" else "height"
            for field in (suffix, "min_" + suffix, "max_" + suffix):
                if field in node:
                    if field == suffix and node[field] == "auto":
                        continue
                    _number(node[field], node, path + "." + field, positive=not field.startswith("min_"))
            if _limits(node, axis)[0] > _limits(node, axis)[1]:
                _fail(node, path, "minimum dimension exceeds maximum")
        for field in ("grow", "shrink", "basis"):
            if field in node and not (field == "basis" and node[field] == "auto"):
                _number(node[field], node, path + "." + field)
        if "align_self" in node and (not isinstance(node["align_self"], str) or node["align_self"] not in ALIGN):
            _fail(node, path + ".align_self", "unsupported alignment")
        active.add(id(node))
        if kind == "leaf":
            element = node.get("element")
            if not isinstance(element, dict) or not isinstance(element.get("type"), str) or element.get("type") not in {"text", "shape", "image", "chart", "component"}:
                _fail(node, path + ".element", "expected text, shape, image, chart or component payload")
            if set(element) & {"id", "frame", "x", "y", "width", "height"}:
                _fail(node, path + ".element", "leaf element ID and geometry are assigned by layout")
            if element["type"] == "shape" and (element.get("shape") == "path" or "d" in element):
                _fail(node, path + ".element", "layout shape leaves require registered shape presets; handwritten path geometry is unsupported")
            if element["type"] == "component":
                if not isinstance(element.get("component"), str) or not element["component"].strip():
                    _fail(node, path + ".element", "component name must be nonempty")
            else:
                contract = scene_contracts()[element["type"]]
                unknown = set(element) - set(contract["common"]) - set(contract["fields"])
                if unknown:
                    _fail(node, path + ".element", f"unsupported element fields {sorted(unknown)}")
            if "computed_layout_metrics" in element:
                _fail(node, path + ".element", "computed_layout_metrics is assigned by the engine, not authored")
            if "sizing" in node:
                if node["sizing"] != "intrinsic" or element.get("type") != "component" or element.get("component") != "progress-ring":
                    _fail(node, path + ".sizing", "intrinsic sizing currently supports progress-ring components only")
                if "aspect_ratio" in node:
                    _fail(node, path, "intrinsic sizing cannot be combined with aspect_ratio")
            if "aspect_ratio" in node:
                _number(node["aspect_ratio"], node, path + ".aspect_ratio", positive=True)
                if element["type"] == "text":
                    _fail(node, path, "text uses measured height, without aspect_ratio")
            if element["type"] == "text" and "text" in element and "runs" in element:
                _fail(node, path + ".element", "text and runs are mutually exclusive")
            finite_json(element, node, path + ".element")
        else:
            children = node.get("children")
            if not isinstance(children, list) or not 1 <= len(children) <= LIMITS["children"]:
                _fail(node, path + ".children", "containers require 1..64 children")
            authored_padding = node.get("padding", 0)
            padding = [authored_padding] * 4 if isinstance(authored_padding, (int, float)) else authored_padding
            if not isinstance(padding, list) or len(padding) != 4:
                _fail(node, path + ".padding", "padding must be a number or [left,top,right,bottom]")
            for value in padding:
                _number(value, node, path + ".padding")
            _number(node.get("gap", 0), node, path + ".gap")
            if (not isinstance(node.get("align", "stretch"), str) or node.get("align", "stretch") not in ALIGN
                    or not isinstance(node.get("justify", "start"), str) or node.get("justify", "start") not in {"start", "center", "end", "space-between"}):
                _fail(node, path, "unsupported align/justify")
            if "surface" in node:
                surface = node["surface"]
                if not isinstance(surface, dict) or set(surface) - {"fill", "stroke", "stroke_width", "shape", "accent"}:
                    _fail(node, path + ".surface", "unsupported surface fields")
                for field in ("fill", "stroke", "shape"):
                    if field in surface and (not isinstance(surface[field], str) or not surface[field]):
                        _fail(node, path + ".surface." + field, "expected a nonempty string (solid color/token for fill/stroke)")
                if surface.get("shape", "rect") in {"path", "line"}:
                    _fail(node, path + ".surface.shape", "surface requires an area shape")
                if "stroke_width" in surface:
                    _number(surface["stroke_width"], node, path + ".surface.stroke_width")
                surfaces.append((identifier + "--surface", node, path))
                if "accent" in surface:
                    accent = surface["accent"]
                    if not isinstance(accent, dict) or set(accent) - {"kind", "color", "thickness", "gap"}:
                        _fail(node, path + ".surface.accent", "accent accepts kind, color, thickness and gap")
                    if not isinstance(accent.get("kind"), str) or accent.get("kind") not in {"rail", "rule", "bracket"}:
                        _fail(node, path + ".surface.accent.kind", "expected rail, rule or bracket")
                    color = accent.get("color", "primary")
                    if not isinstance(color, str) or not color or color == "none":
                        _fail(node, path + ".surface.accent.color", "expected a solid color or token")
                    _number(accent.get("thickness", 4), node, path + ".surface.accent.thickness", positive=True)
                    _number(accent.get("gap", 12), node, path + ".surface.accent.gap")
                    for part in ("rail", "top", "bottom") if accent["kind"] == "bracket" else (accent["kind"],):
                        surfaces.append((identifier + "--accent-" + part, node, path))
            if "connect" in node:
                if kind not in {"row", "column"} or node["connect"] != "sequence":
                    _fail(node, path + ".connect", 'connect="sequence" is only supported on row/column')
                if len(children) < 2 or node.get("gap", 0) <= 0:
                    _fail(node, path + ".connect", "sequence needs at least two children and a positive gap")
                for child in children:
                    if not isinstance(child, dict):
                        _fail(node, path + ".connect", "sequence targets must be layout nodes")
                    target = child.get("element", {}) if child.get("type") == "leaf" else child.get("surface")
                    if not isinstance(target, dict) or child.get("type") == "leaf" and target.get("type") != "shape" or target.get("shape", "rect") in {"path", "line"} or target.get("rotation"):
                        _fail(node, path + ".connect", "sequence targets need unrotated shape leaves or container surfaces")
                for left_child, right_child in zip(children, children[1:]):
                    if "id" in left_child and "id" in right_child:
                        surfaces.append((_sequence_id(node, left_child, right_child), node, path))
            if kind == "grid":
                columns = node.get("columns")
                if isinstance(columns, dict):
                    if set(columns) - {"auto_fit", "max_columns"} or "auto_fit" not in columns:
                        _fail(node, path + ".columns", "automatic columns accept auto_fit and max_columns")
                    if columns["auto_fit"] != "content":
                        _number(columns["auto_fit"], node, path + ".columns.auto_fit", positive=True)
                    maximum = columns.get("max_columns", LIMITS["tracks"])
                    if type(maximum) is not int or not 1 <= maximum <= LIMITS["tracks"]:
                        _fail(node, path + ".columns.max_columns", "max_columns must be an integer from 1 to 12")
                    if "rows" in node:
                        _fail(node, path + ".rows", "automatic columns use content-measured rows")
                    if columns["auto_fit"] == "content" and any(not isinstance(c, dict) or c.get("sizing") != "intrinsic" for c in children):
                        _fail(node, path + ".columns", "content auto_fit currently requires intrinsic component leaves")
                else:
                    tracks(columns, node, path + ".columns")
                for field in ("row_gap", "column_gap"):
                    if field in node:
                        _number(node[field], node, path + "." + field)
                if "uniform_components" in node and type(node["uniform_components"]) is not bool:
                    _fail(node, path + ".uniform_components", "expected a boolean")
                if node.get("uniform_components") and any(not isinstance(c, dict) or c.get("type") != "leaf" or c.get("sizing") != "intrinsic" for c in children):
                    _fail(node, path + ".uniform_components", "uniform_components requires direct intrinsic component leaves")
                if "rows" in node:
                    tracks(node["rows"], node, path + ".rows")
            for index, child in enumerate(children):
                visit(child, f"{path}.children[{index}]", depth + 1, node)
            if kind == "grid" and "rows" in node and len(node["rows"]) != _grid_cells(children, len(node["columns"]))[-1][0] + 1:
                _fail(node, path + ".rows", "rows must match occupied row count after column_span placement")
        active.remove(id(node))

    visit(page.get("layout"), "layout", 1)
    generated = set()
    for identifier, node, path in surfaces:
        if identifier in identifiers or identifier in generated:
            _fail(node, path, f"generated visual ID collides with {identifier!r}")
        generated.add(identifier)


def _distribute(bases, lows, highs, grow, shrink, available, node, path, axis, reserved=0):
    """Weighted flex with bounded clamp/freeze; at most one pass per item."""
    sizes = [max(low, min(high, basis)) for basis, low, high in zip(bases, lows, highs)]
    free = available - sum(sizes)
    if not math.isfinite(free):
        _fail(node, path, "size arithmetic exceeds finite range")
    if free >= 0:
        scale = max(grow, default=0) or 1
        weights = [weight / scale for weight in grow]
    else:
        # Scaling both factors preserves shrink*basis ratios without overflow.
        weight_scale, basis_scale = max(shrink, default=0) or 1, max(bases, default=0) or 1
        weights = [(weight / weight_scale) * (basis / basis_scale) for weight, basis in zip(shrink, bases)]
    active = {i for i, weight in enumerate(weights) if weight > 0}
    for _ in range(len(sizes) + 1):
        free = available - sum(sizes)
        if abs(free) <= EPSILON or not active:
            break
        total = sum(weights[i] for i in active)
        proposals = {i: sizes[i] + free * weights[i] / total for i in active}
        frozen = {i for i, value in proposals.items() if value < lows[i] or value > highs[i]}
        if not frozen:
            for i, value in proposals.items():
                sizes[i] = value
            break
        for i in frozen:
            sizes[i] = max(lows[i], min(highs[i], proposals[i]))
        active -= frozen
    if sum(sizes) > available + TOLERANCE:
        _fail(node, path, "children cannot fit available main-axis space", axis=axis,
              available=available + reserved, required=sum(sizes) + reserved, code="layout_overflow")
    return sizes


def _position(justify, available, sizes, gap):
    free = max(0, available - sum(sizes) - gap * (len(sizes) - 1))
    start = free / 2 if justify == "center" else free if justify == "end" else 0
    if justify == "space-between" and len(sizes) > 1:
        gap += free / (len(sizes) - 1)
    positions, cursor = [], start
    for size in sizes:
        positions.append(cursor)
        cursor += size + gap
    return positions


def _fraction_sizes(bases, lows, highs, weights, available, node, path, axis, reserved=0):
    """fr tracks share total remaining space proportionally, freezing at minima."""
    sizes = list(bases)
    if not math.isfinite(available) or not math.isfinite(sum(sizes)):
        _fail(node, path, "size arithmetic exceeds finite range")
    scale = max(weights, default=0) or 1
    weights = [weight / scale for weight in weights]
    active = {i for i, weight in enumerate(weights) if weight > 0}
    for _ in range(len(active) + 1):
        remaining = available - sum(size for i, size in enumerate(sizes) if i not in active)
        total = sum(weights[i] for i in active)
        if not active:
            break
        proposed = {i: remaining * weights[i] / total for i in active}
        frozen = {i for i, size in proposed.items() if size < lows[i] or size > highs[i]}
        if not frozen:
            for i, size in proposed.items():
                sizes[i] = size
            break
        for i in frozen:
            sizes[i] = max(lows[i], min(highs[i], proposed[i]))
        active -= frozen
    if sum(sizes) > available + TOLERANCE:
        _fail(node, path, "grid tracks cannot fit available space", axis=axis, available=available + reserved,
              required=sum(sizes) + reserved, code="layout_overflow")
    return sizes


class _Solver:
    def __init__(self, facts, tokens):
        self.facts, self.tokens = facts, tokens
        self.helpers = None
        self.text_cache = {}
        self.component_cache, self.uniform_metrics, self.grid_choices = {}, {}, {}

    def intrinsic(self, node, path, width=None):
        from presentation_composition import measure_component_intrinsic, ring_metrics_height
        key = (node["id"], width)
        try:
            if key not in self.component_cache:
                self.component_cache[key] = measure_component_intrinsic({**node["element"], "id": node["id"]}, self.facts, self.tokens, width)
            result = copy.deepcopy(self.component_cache[key])
            if width is not None and width + TOLERANCE < result["minimum_width"]:
                _fail(node, path, "component width cannot contain intrinsic geometry/readout", axis="x", available=width,
                      required=result["minimum_width"], code="layout_overflow")
            if width is not None and node["id"] in self.uniform_metrics:
                result["metrics"] = copy.deepcopy(self.uniform_metrics[node["id"]])
                result["natural_height"] = ring_metrics_height(result["metrics"])
            return result
        except (ValueError, TypeError, KeyError) as exc:
            if isinstance(exc, LayoutError):
                raise
            _fail(node, path, str(exc), code="layout_measurement")

    def text(self, node, path, width=None):
        from presentation_document import resolve_text, resolve_value
        if self.helpers is None:
            self.helpers = runtime_helpers()
        try:
            element = resolve_value(node["element"], self.facts)
            role = element.get("role", "body")
            known = {*self.tokens["font"]["sizes"], *self.tokens["font"].get("textStyles", {})}
            role = role if role in known else "body"
            style = resolve_text_style(self.tokens, role, element.get("style"))
            runs = element.get("runs", [{"text": element.get("text", "")}])
            if not isinstance(runs, list) or not runs or any(not isinstance(run, dict) or "text" not in run or set(run) - {"text", "weight", "color"} for run in runs):
                raise ValueError("runs require text and support only weight/color overrides")
            value = "".join(resolve_text(run["text"], self.facts) for run in runs)
            style["weight"] = max(resolve_text_style(self.tokens, role, {"weight": run.get("weight", style["weight"])})["weight"] for run in runs)
            left, top, right, bottom = style["insets"]
            if width is None:
                from text_measure import measure_text
                preferred = max(measure_text(line, size=style["font_size"], family=style["font_family"], weight=str(style["weight"])) if line else 0
                                for line in value.replace("\r\n", "\n").replace("\r", "\n").split("\n"))
                return max(EPSILON, preferred + left + right)
            content_width = width - left - right
            if content_width <= 0:
                _fail(node, path, "text insets consume allocated width", axis="x", available=width,
                      required=left + right + EPSILON, code="layout_overflow")
            key = (node["id"], width)
            if key not in self.text_cache:
                self.text_cache[key] = measure_text_block(value, content_width, style, self.helpers)
            measured = self.text_cache[key]
            maximum = element.get("max_lines")
            if maximum is not None and (type(maximum) is not int or maximum < 1 or len(measured["lines"]) > maximum):
                raise ValueError("measured lines exceed max_lines, or max_lines is invalid")
            # The native quality gate uses text_box's visible descent envelope,
            # which is wider than DrawingML's advance-box descent. Consume the
            # existing runtime helper rather than weakening that separate gate.
            from text_measure import text_box
            envelope = text_box(x=0, baseline_y=measured["baselines"][-1], size=style["font_size"],
                                lines=1, dy=style["font_size"] * style["line_height"],
                                width=max(measured["widths"], default=0), anchor="start")
            measured = {**measured, "envelope_height": max(measured["height"], envelope["bottom"])}
            if style["vertical_anchor"] == "bottom":
                # The renderer anchors the advance box to the bottom inset.
                # Reserve the additional visible descent in the solved style,
                # since adding frame height alone cannot move that bottom edge.
                safe_bottom = max(bottom, measured["envelope_height"] - measured["height"])
                if safe_bottom > bottom:
                    effective_insets = [left, top, right, safe_bottom]
                    measured["style_overrides"] = {**copy.deepcopy(element.get("style", {})),
                                                   "insets": effective_insets}
                    measured["computed_text_insets"] = {"requested": list(style["insets"]),
                                                        "effective": effective_insets,
                                                        "reason": "bottom-anchor visible descent envelope"}
                    bottom = safe_bottom
            return measured["envelope_height"] + top + bottom, measured
        except (ValueError, TypeError, KeyError) as exc:
            if isinstance(exc, LayoutError):
                raise
            if "unbreakable text unit" in str(exc) and width is not None:
                oversized = []
                for paragraph in value.replace("\r\n", "\n").replace("\r", "\n").split("\n"):
                    oversized.extend(self.helpers[0](paragraph, size=style["font_size"], max_width=content_width,
                                                    family=style["font_family"], weight=str(style["weight"]))[2])
                if oversized:
                    _fail(node, path + ".element", str(exc), axis="x", available=width,
                          required=max(unit_width for _, unit_width in oversized) + left + right, code="layout_overflow")
            _fail(node, path + ".element", str(exc), axis="x" if width is not None else None,
                  available=width, code="layout_measurement")

    def preferred(self, node, path):
        explicit = _dimension(node, "x")
        if explicit is not None:
            return _clamp(explicit, node, "x")
        if node["type"] == "leaf":
            if node.get("sizing") == "intrinsic":
                return _clamp(self.intrinsic(node, path)["preferred_width"], node, "x")
            if node["element"]["type"] == "text":
                return _clamp(self.text(node, path), node, "x")
            low, high = _limits(node, "x")
            if low > 0:
                return low
            _fail(node, path, "auto width needs width/min_width, a row basis, or cross-axis stretch")
        left, _, right, _ = _padding(node)
        preferred = [self.preferred(child, f"{path}.children[{i}]") for i, child in enumerate(node["children"])]
        gap = node.get("gap", 0)
        if node["type"] == "row":
            width = sum(preferred) + gap * (len(preferred) - 1)
        elif node["type"] == "column":
            width = max(preferred)
        else:
            if isinstance(node["columns"], dict):
                return _clamp(max(preferred) + left + right, node, "x")
            count = len(node["columns"])
            column_gap = node.get("column_gap", gap)
            cells = _grid_cells(node["children"], count)
            values = [float(track) if isinstance(track, (int, float)) else 0 for track in node["columns"]]
            width = sum(_span_requirements(values, node["columns"], cells, preferred, column_gap,
                                          node, path + ".columns", strict=False)) + column_gap * (count - 1)
        return _clamp(width + left + right, node, "x")

    def cross_width(self, child, parent, available, path):
        align = child.get("align_self", parent.get("align", "stretch"))
        width = _dimension(child, "x")
        if width is None:
            width = available if align == "stretch" else min(available, self.preferred(child, path))
        width = _clamp(width, child, "x")
        if width > available + TOLERANCE:
            _fail(child, path, "child exceeds available cross-axis width", axis="x", available=available,
                  required=width, code="layout_overflow")
        return width

    def solve(self, node, path, width, height=None):
        width = _quantize(width)
        if not math.isfinite(width) or height is not None and not math.isfinite(height):
            _fail(node, path, "size arithmetic exceeds finite range")
        low, high = _limits(node, "x")
        if width < low - TOLERANCE or width > high + TOLERANCE or width <= 0:
            _fail(node, path, "allocated width violates size constraints", axis="x", available=width,
                  required=max(low, EPSILON), code="layout_overflow")
        target = height if height is not None else _dimension(node, "y")
        if target is not None:
            target = _clamp(target, node, "y")
        if node["type"] == "leaf":
            measured = None
            if node["element"]["type"] == "text":
                natural, measured = self.text(node, path, width)
                minimum = max(natural, _limits(node, "y")[0])
            elif node.get("sizing") == "intrinsic":
                measured = {"component_intrinsic": self.intrinsic(node, path, width)}
                natural = measured["component_intrinsic"]["natural_height"]
                minimum = max(natural, _limits(node, "y")[0])
            else:
                natural = _dimension(node, "y")
                if natural is None and "aspect_ratio" in node:
                    natural = width / node["aspect_ratio"]
                if natural is None:
                    natural = target
                if natural is None:
                    _fail(node, path, "non-text leaf needs height, aspect_ratio or definite stretched height")
                minimum = max(EPSILON, _limits(node, "y")[0])
            result_height = _clamp(natural if target is None else target, node, "y")
            if result_height < minimum - TOLERANCE or result_height <= 0:
                _fail(node, path, "height cannot contain measured content/minimum", axis="y", available=result_height,
                      required=minimum, code="layout_overflow")
            return {"node": node, "path": path, "width": width, "height": result_height,
                    "minimum_height": minimum, "measured": measured, "children": []}
        left, top, right, bottom = _padding(node)
        inner_width = _quantize(width - left - right)
        if inner_width <= 0:
            _fail(node, path, "padding consumes allocated width", axis="x", available=width,
                  required=left + right + EPSILON, code="layout_overflow")
        children, gap = node["children"], node.get("gap", 0)
        inner_target = None if target is None else target - top - bottom
        if inner_target is not None and inner_target <= 0:
            _fail(node, path, "padding consumes allocated height", axis="y", available=target,
                  required=top + bottom + EPSILON, code="layout_overflow")
        if node["type"] == "grid":
            solved, natural, minimum = self.grid(node, path, inner_width, inner_target)
        elif node["type"] == "row":
            bases = [float(c["basis"]) if c.get("basis", "auto") != "auto" else self.preferred(c, f"{path}.children[{i}]") for i, c in enumerate(children)]
            widths = _distribute(bases, [_limits(c, "x")[0] for c in children], [_limits(c, "x")[1] for c in children],
                                 [c.get("grow", 0) for c in children], [c.get("shrink", 0) for c in children],
                                 inner_width - gap * (len(children) - 1), node, path, "x", gap * (len(children) - 1) + left + right)
            solved = []
            for i, (child, child_width) in enumerate(zip(children, widths)):
                align = child.get("align_self", node.get("align", "stretch"))
                assigned = inner_target if align == "stretch" and _dimension(child, "y") is None else None
                deferred = (assigned is None and align == "stretch" and child["type"] == "leaf"
                            and child["element"]["type"] != "text" and _dimension(child, "y") is None
                            and "aspect_ratio" not in child and child.get("sizing") != "intrinsic")
                solved.append(None if deferred else self.solve(child, f"{path}.children[{i}]", child_width, assigned))
            if any(child is None for child in solved):
                measured_siblings = [child["height"] for child in solved if child is not None]
                if not measured_siblings:
                    _fail(node, path, "non-text leaves need a definite stretched height or measured sibling height")
                sibling_height = max(measured_siblings)
                solved = [child if child is not None else self.solve(children[i], f"{path}.children[{i}]", widths[i], max(sibling_height, _limits(children[i], "y")[0])) for i, child in enumerate(solved)]
            natural = max(c["height"] for c in solved)
            minimum = max(c["minimum_height"] if c["node"].get("align_self", node.get("align", "stretch")) == "stretch" and _dimension(c["node"], "y") is None else c["height"] for c in solved)
            positions = _position(node.get("justify", "start"), inner_width, widths, gap)
            for child, x in zip(solved, positions):
                child["x"] = x
        else:
            solved = []
            for i, child in enumerate(children):
                location = f"{path}.children[{i}]"
                child_width = self.cross_width(child, node, inner_width, location)
                assigned = None
                if child["type"] == "leaf" and child["element"]["type"] != "text" and _dimension(child, "y") is None and "aspect_ratio" not in child and child.get("sizing") != "intrinsic":
                    if child.get("basis", "auto") != "auto":
                        assigned = max(EPSILON, float(child["basis"]))
                    elif inner_target is not None and child.get("grow", 0) > 0:
                        assigned = max(EPSILON, _limits(child, "y")[0])
                solved.append(self.solve(child, location, child_width, max(EPSILON, assigned) if assigned is not None else None))
            starting = [max(c["minimum_height"], _clamp(float(c["node"]["basis"]), c["node"], "y")) if c["node"].get("basis", "auto") != "auto" else c["height"] for c in solved]
            natural = sum(starting) + gap * (len(solved) - 1)
            minimum = sum(c["minimum_height"] if c["node"].get("shrink", 0) > 0 else initial for c, initial in zip(solved, starting)) + gap * (len(solved) - 1)
        result_height = _clamp(natural + top + bottom if target is None else target, node, "y")
        available_height = result_height - top - bottom
        if minimum > available_height + TOLERANCE:
            _fail(node, path, "container cannot contain its children", axis="y", available=result_height,
                  required=minimum + top + bottom, code="layout_overflow")
        if node["type"] == "column":
            heights = _distribute([float(c["node"]["basis"]) if c["node"].get("basis", "auto") != "auto" else c["height"] for c in solved], [c["minimum_height"] for c in solved],
                                   [_limits(c, "y")[1] for c in children], [c.get("grow", 0) for c in children],
                                   [c.get("shrink", 0) for c in children], available_height - gap * (len(children) - 1), node, path, "y", gap * (len(children) - 1) + top + bottom)
            solved = [c if abs(c["height"] - h) <= EPSILON else self.solve(c["node"], c["path"], c["width"], h) for c, h in zip(solved, heights)]
            positions = _position(node.get("justify", "start"), available_height, heights, gap)
            for child, y in zip(solved, positions):
                align = child["node"].get("align_self", node.get("align", "stretch"))
                free = max(0, inner_width - child["width"])
                child["x"] = free / 2 if align == "center" else free if align == "end" else 0
                child["y"] = y
        elif node["type"] == "row":
            for i, child in enumerate(solved):
                align = child["node"].get("align_self", node.get("align", "stretch"))
                if align == "stretch" and _dimension(child["node"], "y") is None:
                    if abs(child["height"] - available_height) > EPSILON:
                        child = self.solve(child["node"], child["path"], child["width"], available_height)
                    child["x"] = positions[i]
                    solved[i] = child
                free = max(0, available_height - child["height"])
                child["y"] = free / 2 if align == "center" else free if align == "end" else 0
        for child in solved:
            child["x"] += left
            child["y"] += top
        return {"node": node, "path": path, "width": width, "height": result_height,
                "minimum_height": max(_limits(node, "y")[0], minimum + top + bottom), "children": solved,
                **({"grid_selection": copy.deepcopy(self.grid_choices[node["id"]])} if node["id"] in self.grid_choices else {})}

    def grid(self, node, path, width, height):
        columns, children, gap = node["columns"], node["children"], node.get("gap", 0)
        column_gap, row_gap = node.get("column_gap", gap), node.get("row_gap", gap)
        if isinstance(columns, dict):
            candidates, failures = [], []
            maximum = min(columns.get("max_columns", LIMITS["tracks"]), len(children))
            for count in range(maximum, 0, -1):
                track_width = (width-column_gap*(count-1))/count
                if track_width <= 0 or columns["auto_fit"] != "content" and track_width + TOLERANCE < columns["auto_fit"]:
                    continue
                try:
                    result = self.grid({**node, "columns": [{"fr": 1}]*count}, path, width, height)
                    candidates.append((result[2], -count, result))
                except LayoutError as exc:
                    failures.append(exc)
            if not candidates:
                if failures:
                    raise failures[-1]
                _fail(node, path + ".columns", "automatic column minimum exceeds available width", axis="x", available=width,
                      required=columns["auto_fit"] if columns["auto_fit"] != "content" else width+1, code="layout_overflow")
            minimum, negative_count, result = min(candidates, key=lambda item: (round(item[0], 6), item[1]))
            count = -negative_count
            self.grid_choices[node["id"]] = {"columns": count, "rows": math.ceil(len(children)/count),
                "column_gap": column_gap, "row_gap": row_gap, "required_height": minimum,
                "candidate_count": len(candidates), "selection": "minimum required height, then more columns"}
            return result
        count = len(columns)
        cells = _grid_cells(children, count)
        sizes, lows, highs, grow = [], [], [], []
        for index, track in enumerate(columns):
            members = [(i, child) for i, child in enumerate(children) if cells[i][1:] == (index, 1)]
            low = max((_limits(child, "x")[0] for _, child in members), default=0)
            if isinstance(track, (int, float)):
                basis = float(track)
                if basis < low - TOLERANCE:
                    _fail(node, path + ".columns", "fixed track violates child minimum width", axis="x", available=basis, required=low, code="layout_overflow")
                sizes.append(basis); lows.append(basis); highs.append(basis); grow.append(0)
            elif track == "auto":
                preferred = max((self.preferred(child, f"{path}.children[{i}]") for i, child in members), default=EPSILON)
                sizes.append(max(low, preferred)); lows.append(max(low, preferred)); highs.append(math.inf); grow.append(0)
            else:
                sizes.append(low); lows.append(low); highs.append(math.inf); grow.append(track["fr"])
        _span_requirements(lows, columns, cells, [_limits(child, "x")[0] for child in children],
                           column_gap, node, path + ".columns")
        sizes = [max(size, low) for size, low in zip(sizes, lows)]
        # An auto track reserves preferred content size; fr tracks only reserve minima.
        auto_requirements = [self.preferred(child, f"{path}.children[{i}]")
                             if any(columns[c] == "auto" for c in range(cells[i][1], cells[i][1] + cells[i][2]))
                             else 0 for i, child in enumerate(children)]
        _span_requirements(sizes, columns, cells, auto_requirements, column_gap, node, path + ".columns", strict=False)
        lows = [max(low, size) if track == "auto" else low for low, size, track in zip(lows, sizes, columns)]
        left, top, right, bottom = _padding(node)
        widths = _fraction_sizes(sizes, lows, highs, grow, width - column_gap * (count - 1), node, path + ".columns", "x", column_gap * (count - 1) + left + right)
        cell_widths = [sum(widths[column:column + span]) + column_gap * (span - 1) for _, column, span in cells]
        for child in children:
            self.uniform_metrics.pop(child["id"], None)
        if node.get("uniform_components"):
            measured = [self.intrinsic(child, f"{path}.children[{i}]", self.cross_width(child, node, widths[i%count], path))
                        for i, child in enumerate(children)]
            if len({item["metrics"]["hole_size"] for item in measured}) != 1:
                _fail(node, path + ".uniform_components", "uniform rings require the same hole_size")
            common = {key: max(item["metrics"][key] for item in measured) for key in measured[0]["metrics"]}
            if common["diameter"] > min(widths) + TOLERANCE:
                _fail(node, path, "uniform component geometry exceeds column width", axis="x", available=min(widths),
                      required=common["diameter"], code="layout_overflow")
            for child in children:
                self.uniform_metrics[child["id"]] = common
        row_count = cells[-1][0] + 1
        rows = node.get("rows", ["auto"] * row_count)
        if height is None and any(isinstance(track, dict) for track in rows):
            _fail(node, path + ".rows", "fr rows require a definite container height")
        solved = []
        for i, child in enumerate(children):
            row = rows[cells[i][0]]
            assigned = float(row) if isinstance(row, (int, float)) and child.get("align_self", node.get("align", "stretch")) == "stretch" and _dimension(child, "y") is None else None
            if assigned is None and isinstance(row, dict) and child["type"] == "leaf" and child["element"]["type"] != "text" and _dimension(child, "y") is None and "aspect_ratio" not in child and child.get("sizing") != "intrinsic":
                assigned = max(EPSILON, _limits(child, "y")[0])
            location = f"{path}.children[{i}]"
            child_width = self.cross_width(child, node, cell_widths[i], location)
            deferred = (assigned is None and child.get("align_self", node.get("align", "stretch")) == "stretch"
                        and child["type"] == "leaf" and child["element"]["type"] != "text"
                        and _dimension(child, "y") is None and "aspect_ratio" not in child and child.get("sizing") != "intrinsic")
            solved.append(None if deferred else self.solve(child, location, child_width, assigned))
        for row_index in range(row_count):
            indices = [i for i, cell in enumerate(cells) if cell[0] == row_index]
            if any(solved[i] is None for i in indices):
                measured_siblings = [solved[i]["height"] for i in indices if solved[i] is not None]
                if not measured_siblings:
                    _fail(node, path + ".rows", "auto grid row needs a measured child or explicit row height")
                sibling_height = max(measured_siblings)
                for i in indices:
                    if solved[i] is None:
                        location = f"{path}.children[{i}]"
                        child_width = self.cross_width(children[i], node, cell_widths[i], location)
                        solved[i] = self.solve(children[i], location, child_width, max(sibling_height, _limits(children[i], "y")[0]))
        natural_rows = [max(child["height"] for child, cell in zip(solved, cells) if cell[0] == row) for row in range(row_count)]
        row_sizes, row_lows, row_highs, row_grow = [], [], [], []
        for track, natural in zip(rows, natural_rows):
            fixed = isinstance(track, (int, float))
            if fixed and natural > track + TOLERANCE:
                _fail(node, path + ".rows", "fixed row is shorter than its content", axis="y", available=track, required=natural, code="layout_overflow")
            row_sizes.append(float(track) if fixed else natural)
            row_lows.append(float(track) if fixed else natural)
            row_highs.append(float(track) if fixed else math.inf)
            row_grow.append(track["fr"] if isinstance(track, dict) else 0)
        if height is not None:
            row_sizes = _fraction_sizes(row_sizes, row_lows, row_highs, row_grow,
                                    height - row_gap * (row_count - 1), node, path + ".rows", "y", row_gap * (row_count - 1) + top + bottom)
        natural = sum(row_sizes) + row_gap * (row_count - 1)
        xs = _position("start", width, widths, column_gap)
        ys = _position(node.get("justify", "start"), natural if height is None else height, row_sizes, row_gap)
        for i, child in enumerate(solved):
            row, column, span = cells[i]
            align = child["node"].get("align_self", node.get("align", "stretch"))
            if align == "stretch" and _dimension(child["node"], "y") is None:
                if abs(child["height"] - row_sizes[row]) > EPSILON:
                    child = self.solve(child["node"], child["path"], child["width"], row_sizes[row])
                solved[i] = child
            free_x, free_y = max(0, cell_widths[i] - child["width"]), max(0, row_sizes[row] - child["height"])
            child["x"] = xs[column] + (free_x / 2 if align == "center" else free_x if align == "end" else 0)
            child["y"] = ys[row] + (free_y / 2 if align == "center" else free_y if align == "end" else 0)
            child["grid_cell"] = {"row": row, "column": column, "column_span": span, "allocated_width": cell_widths[i]}
        return solved, natural, sum(row_lows) + row_gap * (row_count - 1)


def lower_layout_page(page, facts, canvas, tokens, *, bounds=None):
    """Return a fresh scene page and measured trace, leaving the author untouched."""
    validate_layout_page(page)
    if not isinstance(canvas, (list, tuple)) or len(canvas) != 2:
        _fail(page, "canvas", "expected [width,height]")
    cw, ch = [_number(value, page, "canvas", positive=True) for value in canvas]
    bounds = [0, 0, cw, ch] if bounds is None else bounds
    if not isinstance(bounds, (list, tuple)) or len(bounds) != 4:
        _fail(page, "bounds", "expected [x,y,width,height]")
    x, y, width, height = [_number(value, page, "bounds") for value in bounds]
    if min(width, height) <= 0 or x + width > cw + TOLERANCE or y + height > ch + TOLERANCE:
        _fail(page, "bounds", "bounds must be a positive rectangle inside the canvas")
    root = page["layout"]
    root_width = _clamp(_dimension(root, "x") or width, root, "x")
    root_height = _clamp(_dimension(root, "y") or height, root, "y")
    if root_width > width + TOLERANCE or root_height > height + TOLERANCE:
        _fail(root, "layout", "root size exceeds allocated bounds")
    solved = _Solver(facts, tokens).solve(root, "layout", root_width, root_height)
    elements, nodes = [], []

    def emit(result, px, py, parent=None):
        node = result["node"]
        box = [_quantize(value) for value in (px, py, result["width"], result["height"])]
        if any(not math.isfinite(value) for value in box):
            _fail(node, result["path"], "size arithmetic exceeds finite range")
        record = {"id": node["id"], "node_id": node["id"], "path": result["path"], "type": node["type"],
                  "parent_id": parent, "frame": box, "minimum_height": result["minimum_height"]}
        for field in ("metadata", "source_ref", "content_ref", "relation_ref"):
            if field in node:
                record[field] = copy.deepcopy(node[field])
        measured = result.get("measured")
        if measured is not None and "component_intrinsic" in measured:
            record["component_intrinsic"] = copy.deepcopy(measured["component_intrinsic"])
            record["measurement_width"] = result["width"]
        elif measured is not None:
            record.update({"measured_height": measured["height"], "line_count": len(measured["lines"]),
                           "envelope_height": measured["envelope_height"],
                           "text_ranges": [list(pair) for pair in measured["ranges"]],
                           "measurement_width": result["width"], "measurement": "runtime DrawingML estimator"})
            if "computed_text_insets" in measured:
                record["computed_text_insets"] = copy.deepcopy(measured["computed_text_insets"])
        for field in ("grid_selection", "grid_cell"):
            if field in result:
                record[field] = copy.deepcopy(result[field])
        if node["type"] != "leaf":
            record["effective_padding"] = _padding(node)
        nodes.append(record)
        if "surface" in node:
            surface = {"id": node["id"] + "--surface", "type": "shape", "frame": box,
                       "shape": "rect", "role": "decoration", **copy.deepcopy(node["surface"])}
            accent = surface.pop("accent", None)
            elements.append(surface)
            record["surface_id"] = surface["id"]
            if accent:
                thickness = accent.get("thickness", 4)
                bx, by, bw, bh = box
                if thickness >= min(bw, bh):
                    _fail(node, result["path"] + ".surface.accent", "accent thickness must be smaller than its surface")
                pieces = {"rail": [bx, by, thickness, bh], "rule": [bx, by, bw, thickness]}
                if accent["kind"] == "bracket":
                    length = min(bw, max(thickness, min(bw, bh) / 4))
                    pieces = {"rail": pieces["rail"], "top": [bx, by, length, thickness],
                              "bottom": [bx, by + bh - thickness, length, thickness]}
                else:
                    pieces = {accent["kind"]: pieces[accent["kind"]]}
                record["accent_ids"] = []
                for part, piece in pieces.items():
                    identifier = node["id"] + "--accent-" + part
                    elements.append({"id": identifier, "type": "shape", "shape": "rect", "role": "decoration",
                                     "frame": [_quantize(value) for value in piece], "fill": accent.get("color", "primary"),
                                     "stroke": "none", "metadata": {"layout_owner": node["id"], "purpose": "section accent"}})
                    record["accent_ids"].append(identifier)
        if node.get("connect") == "sequence":
            record["connector_ids"] = []
            for left_child, right_child in zip(node["children"], node["children"][1:]):
                identifier = _sequence_id(node, left_child, right_child)
                endpoint = lambda child: child["id"] if child["type"] == "leaf" else child["id"] + "--surface"
                connector = {"id": identifier, "type": "connector", "from": endpoint(left_child), "to": endpoint(right_child),
                             "from_port": "right" if node["type"] == "row" else "bottom",
                             "to_port": "left" if node["type"] == "row" else "top", "stroke": "primary", "stroke_width": 2,
                             "arrow": True, "metadata": {"layout_owner": node["id"], "relation": "declared sequence"}}
                if "relation_ref" in node:
                    connector["relation_ref"] = copy.deepcopy(node["relation_ref"])
                elements.append(connector)
                record["connector_ids"].append(identifier)
        if node["type"] == "leaf":
            element = {**copy.deepcopy(node["element"]), "id": node["id"], "frame": box}
            if measured is not None and "style_overrides" in measured:
                element["style"] = copy.deepcopy(measured["style_overrides"])
            if measured is not None and "component_intrinsic" in measured:
                element["computed_layout_metrics"] = copy.deepcopy(measured["component_intrinsic"]["metrics"])
            for field in ("metadata", "source_ref", "content_ref", "relation_ref"):
                if field in node:
                    element.setdefault(field, copy.deepcopy(node[field]))
            elements.append(element)
        for child in result["children"]:
            cx, cy = px + child["x"], py + child["y"]
            if (cx < px - TOLERANCE or cy < py - TOLERANCE or cx + child["width"] > px + result["width"] + TOLERANCE
                    or cy + child["height"] > py + result["height"] + TOLERANCE):
                _fail(child["node"], child["path"], "final child frame exceeds its parent", code="layout_overflow")
            emit(child, cx, cy, node["id"])

    emit(solved, x, y)
    scene = {key: copy.deepcopy(value) for key, value in page.items() if key not in {"layout", "layout_version"}}
    scene.update({"kind": "scene", "elements": elements})
    report = {"layout_version": VERSION, "algorithm_version": ALGORITHM, "page_id": page.get("id"),
              "bounds": list(bounds), "nodes": nodes, "precision_decimals": PRECISION,
              "tolerance_px": TOLERANCE, "measurement": "runtime DrawingML estimator; target rendering checked separately"}
    return scene, report


def layout_catalog(name=None, tokens=None):
    """Discover the exact finite subset, defaults, limits, and executable examples."""
    if name is not None and name not in {"row", "column", "grid", "leaf"}:
        raise TemplateInputError(f"unknown layout {name!r}")
    definitions = {
        "column": {"purpose": "Document flow: determine widths, measure natural heights, then place in order.", "fields": sorted(COMMON | CONTAINER)},
        "row": {"purpose": "One flex row: allocate widths with freeze/clamp, then remeasure text heights.", "fields": sorted(COMMON | CONTAINER)},
        "grid": {"purpose": "Row-major fixed/auto/fr tracks or measured automatic column selection.", "fields": sorted(COMMON | CONTAINER | {"columns", "rows", "row_gap", "column_gap", "uniform_components"})},
        "leaf": {"purpose": "Measured text, opt-in intrinsic component, or primitive with declared design height.", "fields": sorted(COMMON | {"element", "aspect_ratio", "sizing"})},
    }
    example = {"id": "layout-example", "kind": "layout", "layout_version": VERSION,
               "layout": {"id": "body", "type": "column", "padding": [48, 36, 48, 30], "gap": 20,
                          "children": [{"id": "headline", "type": "leaf", "element": {"type": "text", "role": "title", "text": "当前判断"}},
                                       {"id": "copy", "type": "leaf", "element": {"type": "text", "role": "body", "text": "正文随可用宽度测高，后续内容自动顺排。"}}]}}
    return {"layout_version": VERSION, "algorithm_version": ALGORITHM,
            "definitions": copy.deepcopy({name: definitions[name]} if name else definitions),
            "defaults": {"width": "auto", "height": "auto", "basis": "auto", "grow": 0, "shrink": 0,
                         "align": "stretch", "justify": "start", "gap": 0, "padding": 0, "rows": "auto per occupied row"},
            "units": "SVG px; padding [left,top,right,bottom]; aspect_ratio=width/height",
            "tracks": "positive fixed px, auto preferred-content width (nonshrinking), or {fr:positive}; fr rows require definite height",
            "automatic_grid": {"columns": {"auto_fit": "content or positive minimum track width", "max_columns": "integer 1..12 (default 12)"},
                               "selection": "measure every candidate at final track width; minimize required total height; ties prefer more columns",
                               "uniform_components": "direct intrinsic leaves only; same hole size; share maximum measured circle and text slots across every occupied row",
                               "row_gap": "defaults to gap; space between grid rows", "column_gap": "defaults to gap; space between grid columns"},
            "column_span": {"scope": "direct children of a grid with explicit columns", "value": "integer 1..column count",
                            "placement": "ordered row-major, advance to next row if remaining columns cannot hold item; no backfill",
                            "measurement": "sum of covered track widths plus internal column gaps",
                            "minimums": "monotone span deficits split across flexible tracks by fr weight (auto weight 1); conservative, not CSS track sizing",
                            "unsupported": ["auto_fit with column_span", "spans greater than 1 with uniform_components", "row_span", "subgrid"]},
            "surface_accent": {"fields": {"kind": "rail | rule | bracket", "color": "solid color/token; default primary",
                                          "thickness": "positive px; default 4", "gap": "nonnegative clearance px; default 12"},
                               "safe_insets": "effective padding reserves thickness+gap on left (rail), top (rule), or left/top/bottom (bracket)",
                               "geometry": "native rectangles inside computed parent; bracket return = one quarter of shorter side",
                               "purpose": "section grouping and hierarchy; excluded from content occupancy"},
            "sequence": {"connect": "sequence", "scope": "row/column direct children, at least two, positive gap",
                         "targets": "unrotated area-shape leaves or container surfaces; source presets need connection sites",
                         "layering": "parent surface then accents then declared links then child subtrees; stable child-derived IDs",
                         "meaning": "explicit sequence only; never inferred from sibling placement; no obstacle routing"},
            "intrinsic_components": {"sizing": "intrinsic", "supported": ["progress-ring"],
                                     "height": "omit for hug; explicit height must contain measured content",
                                     "width": "assigned by parent; unbreakable units and measured circle define hard minimum",
                                     "fill": "grow/fr allocates the outer box; intrinsic marks retain their measured diameter",
                                     "internal_geometry": "computed_layout_metrics is emitted by solver and cannot be authored in layout input"},
            "sizing": "Numeric dimensions are preferred sizes clamped to explicit min/max; shrink requires explicit weight. Text height cannot shrink below measured content. Flex shrink weight = shrink * basis. Cross stretch applies to auto dimensions.",
            "bounds": "whole canvas by default; optional bounds allocates a rectangle; root explicit size/min/max is honored inside it",
            "limits": copy.deepcopy(LIMITS), "precision_decimals": PRECISION, "tolerance_px": TOLERANCE,
            "unsupported": ["percentages", "wrap", "row_span", "subgrid", "absolute positioning", "semantic pagination", "automatic font shrinking", "gradient surfaces"],
            "shape_geometry": "leaf shapes use registered presets; authored path/d geometry is rejected. Algorithm-generated topology geometry remains internal to component expansion.",
            "measurement": "shared runtime DrawingML estimator, not target-software measurement",
            "design_preferences": {"automatic_surface": "solid", "gradient": "lowest preference; unsupported by layout surfaces"},
            "component_validation": "payload syntax/capacity is checked by existing component expansion after layout",
            "example": example}
