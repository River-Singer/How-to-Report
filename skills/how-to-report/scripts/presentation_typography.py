"""Resolve role-based typography and measure the exact text sent to DrawingML."""
from __future__ import annotations

import copy
import math


STYLE_FIELDS = {"font_family", "font_size", "weight", "line_height", "paragraph_gap", "insets",
                "align", "vertical_anchor", "color"}
ANCHORS = {"top": "t", "middle": "ctr", "bottom": "b"}


def _number(value, name, minimum):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < minimum:
        raise ValueError(f"{name} must be a finite number >= {minimum}")
    return value


def resolve_text_style(tokens, role="body", style=None):
    """Resolve font tokens, inherited role style, then explicit element overrides."""
    font = tokens["font"]
    roles = font.get("textStyles", {})

    def inherited(current, visiting):
        if not isinstance(current, str) or current in visiting:
            raise ValueError(f"unknown or cyclic typography role: {current!r}")
        definition = roles.get(current, {})
        if not isinstance(definition, dict) or set(definition) - STYLE_FIELDS - {"base_role"}:
            raise ValueError(f"{current}: unsupported typography role fields")
        if "base_role" in definition:
            result = inherited(definition["base_role"], visiting + [current])
        elif current in font["sizes"]:
            title = current in {"hero", "chapter", "title", "heading", "metric"}
            result = {"font_family": font["families"]["title" if title else "body"],
                      "font_size": font["sizes"][current], "weight": font["weights"].get(current, 400),
                      "line_height": font["lineHeight"].get(current, font["lineHeight"]["body"]),
                      "paragraph_gap": 0, "insets": [0, 0, 0, 0], "align": "left",
                      "vertical_anchor": "top", "color": "primary" if title else "text"}
        else:
            raise ValueError(f"unknown typography role or missing base_role: {current!r}")
        result.update({key: value for key, value in definition.items() if key != "base_role"})
        return result

    if style is None:
        style = {}
    if not isinstance(style, dict) or set(style) - STYLE_FIELDS:
        raise ValueError("unsupported text style fields")
    result = {**inherited(role, []), **style}
    if not isinstance(result["font_family"], str) or not result["font_family"].strip():
        raise ValueError("font_family must be a nonempty string")
    if not isinstance(result["color"], str) or not result["color"].strip():
        raise ValueError("color must be a nonempty string")
    _number(result["font_size"], "font_size", .000001)
    _number(result["line_height"], "line_height", 1)
    _number(result["paragraph_gap"], "paragraph_gap", 0)
    weight = result["weight"]
    if isinstance(weight, str) and weight.isdigit():
        weight = int(weight)
    if type(weight) is not int or weight not in range(100, 1000, 100):
        raise ValueError("font weight must be 100..900")
    result["weight"] = 700 if weight >= 600 else 400
    if result["align"] not in {"left", "center", "right"} or result["vertical_anchor"] not in ANCHORS:
        raise ValueError("unsupported text alignment or vertical_anchor")
    insets = result["insets"]
    if not isinstance(insets, list) or len(insets) != 4:
        raise ValueError("insets must be [left,top,right,bottom]")
    for value in insets:
        _number(value, "inset", 0)
    return copy.deepcopy(result)


def source_line_ranges(paragraph, lines):
    """Map normalized wrap results to the exact original character ranges."""
    ranges, cursor = [], 0
    for line in lines:
        start = cursor
        for char in line:
            if char.isspace():
                continue
            while cursor < len(paragraph) and paragraph[cursor].isspace():
                cursor += 1
            if cursor >= len(paragraph) or paragraph[cursor] != char:
                raise ValueError("measured text characters differ from the original paragraph")
            cursor += 1
        while cursor < len(paragraph) and paragraph[cursor].isspace():
            cursor += 1
        ranges.append((start, cursor))
    if cursor != len(paragraph):
        raise ValueError("measured text omitted original paragraph characters")
    return ranges


def measure_text_block(text, width, style, helpers):
    """Return shared exact-character wrapping, baselines and measured content height."""
    from text_measure import measure_text
    _number(width, "text width", .000001)
    size, family = style["font_size"], style["font_family"]
    weight, advance = str(style["weight"]), size * style["line_height"]
    value = text.replace("\r\n", "\n").replace("\r", "\n")
    wrap, baseline_offset = helpers[:2]
    lines, widths, ranges, starts = [], [], [], []
    offset = 0
    for paragraph in value.split("\n"):
        search_width = width
        for _attempt in range(8):
            wrapped, _, oversized = wrap(paragraph, size=size, max_width=search_width, family=family, weight=weight)
            local_ranges = source_line_ranges(paragraph, wrapped or [""])
            exact = [paragraph[start:end] for start, end in local_ranges]
            exact_widths = [measure_text(line, size=size, family=family, weight=weight) if line else 0 for line in exact]
            if oversized:
                raise ValueError("an unbreakable text unit exceeds its frame")
            excess = max([actual - width for actual in exact_widths] + [0])
            if excess <= .01:
                break
            search_width -= max(excess, 1)
            if search_width <= 0:
                raise ValueError("preserved whitespace exceeds its frame")
        else:
            raise ValueError("preserved whitespace cannot fit the current frame")
        starts.append(len(lines))
        lines.extend(exact)
        widths.extend(exact_widths)
        ranges.extend((offset + start, offset + end) for start, end in local_ranges)
        offset += len(paragraph) + 1
    baseline = baseline_offset([{"text": lines[0] or " ", "font_size": size, "font_family": family, "font_weight": weight}],
                               {"latin": family.split(",")[0].strip(), "ea": family.split(",")[0].strip(), "cs": family.split(",")[0].strip()},
                               default_size=size, line_spacing_px=advance if len(lines) > 1 else None)
    baselines = []
    extra = 0
    for index in range(len(lines)):
        if index in starts[1:]:
            extra += style["paragraph_gap"]
        baselines.append(baseline + index * advance + extra)
    return {"text": value, "lines": lines, "widths": widths, "ranges": ranges, "baselines": baselines,
            "paragraph_starts": starts, "height": baselines[-1] + size * .25}


def typography_catalog(tokens):
    roles = list(dict.fromkeys([*tokens["font"]["sizes"], *tokens["font"].get("textStyles", {})]))
    return {"roles": {role: resolve_text_style(tokens, role) for role in roles},
            "units": {"font_size": "SVG px; native pt = px * 0.75", "line_height": "font-size multiplier",
                      "paragraph_gap": "SVG px between paragraphs", "insets": "SVG px [left,top,right,bottom]"},
            "precedence": ["font tokens", "base_role style", "role textStyles", "element style", "run weight/color"],
            "native_weights": {"100..500": 400, "600..900": 700}}
