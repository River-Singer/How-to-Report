"""User-derived page structures. Global visual values come from template tokens."""
from __future__ import annotations

import hashlib
import json
import math
from xml.etree import ElementTree as ET


def _body_role(c):
    return c.page["config"]["body_role"]


def _cards(c, count, columns, field="items", title="title", body="body"):
    x, y, width, height = c.body
    gap = c.tokens["spacing"]["lg"]
    rows = math.ceil(count / columns)
    card_width = (width - gap * (columns - 1)) / columns
    card_height = (height - gap * (rows - 1)) / rows
    values = c.page["content"].get(field, [])
    for index in range(count):
        item = values[index] if index < len(values) else {}
        left, top = x + index % columns * (card_width + gap), y + index // columns * (card_height + gap)
        c.rect([left, top, card_width, card_height])
        padding = c.tokens["spacing"]["lg"]
        title_frame = [left + padding, top + padding, card_width - 2 * padding, 52]
        body_frame = [left + padding, top + padding + 68, card_width - 2 * padding, card_height - 2 * padding - 68]
        if columns == 1:
            title_frame = [left + padding, top + padding, card_width * .3 - padding, card_height - 2 * padding]
            body_frame = [left + card_width * .34, top + padding, card_width * .66 - padding, card_height - 2 * padding]
        limits = c.variant.get("item_text_limits", {})
        c.text(f"{field}.{index}.{title}", item.get(title, ""), title_frame, "heading", 0, limits.get(title, 24))
        c.text(f"{field}.{index}.{body}", item.get(body, ""), body_frame, _body_role(c), 0, limits.get(body, 120))
        icon_size = min(24, padding * .8)
        _icon(c, item.get("icon_key", ""), [left + card_width - padding - icon_size, top + card_height - (padding + icon_size) / 2, icon_size, icon_size])


def _icon(c, key, frame):
    if not key:
        return
    registry = json.loads((c.template_root / "icons" / "catalog.json").read_text(encoding="utf-8"))
    if key not in registry:
        from report_ppt import TemplateInputError
        raise TemplateInputError(f"unknown user icon_key: {key}")
    if not c.page["config"]["show_icons"]:
        return
    root = ET.parse(c.template_root / "icons" / registry[key]["file"]).getroot()
    vx, vy, vw, vh = map(float, root.get("viewBox").split())
    x, y, width, height = frame
    scale = min(width / vw, height / vh)
    left, top = x + (width - vw * scale) / 2, y + (height - vh * scale) / 2
    bounds = " ".join(str(value) for value in frame)
    group = c.element("g", {"transform": f"translate({left} {top}) scale({scale}) translate({-vx} {-vy})", "data-pptx-bounds": bounds, "data-htr-icon-key": key, "data-htr-icon-frame": bounds})
    for node in root:
        for child in node.iter():
            child.attrib.pop("id", None)
            for attribute in list(child.attrib):
                if attribute.startswith("data-pptx-"):
                    child.attrib.pop(attribute)
            if child.get("fill") not in {None, "none"}:
                child.set("fill", c.color("primary"))
        group.append(node)


def cover(c):
    x, y, width, height = c.body
    content = c.page["content"]
    split = c.variant["id"] == "split"
    text_width = width * (.62 if split else .78)
    c.text("topic", content.get("topic", ""), [x, y + 24, text_width, 42], "heading", 0, 20)
    c.text("subtitle", content.get("subtitle", ""), [x, y + 100, text_width, 156], "chapter", 0, 40)
    if split:
        c.line(x + width * .7, y + 20, x + width * .7, y + height - 20)
    else:
        # Original custom geometry from source slide 6, shape 19.
        # Scale its complete contour uniformly so the rising arrow keeps its bends.
        source_points = (
            (7019290, 0), (7019290, 1303020), (9503409, 1303020),
            (6513830, 4291330), (4109720, 1885950), (0, 5995670),
            (0, 6393179), (1445260, 6393179), (4109720, 3728720),
            (6513830, 6134099), (10424159, 2223770), (10424159, 4707889),
            (11727179, 4707889), (11727179, 0),
        )
        arrow_width = width * .2
        scale = arrow_width / 11727179
        left, top = x + width - arrow_width, y + 180
        points = " ".join(f"{left + px * scale:g},{top + py * scale:g}" for px, py in source_points)
        c.element("polygon", {"points": points, "fill": c.color("secondary")}, "layout", identifier="cover-rising-arrow")
    for index, field in enumerate(("author", "department", "date")):
        left = x + width * .74 if split else x + index * width / 3
        top = y + 280 + index * 58 if split else y + height - 72
        c.text(field, content.get(field, ""), [left, top, width * (.25 if split else .31), 44], "body", 0, 30)


def toc(c):
    _cards(c, c.variant["capacity"], 3 if c.variant["id"] == "grid6" else 1, body="description")


def chapter(c):
    x, y, width, height = c.body
    content = c.page["content"]
    if c.variant["id"] == "number":
        c.text("chapter_number", content["chapter_number"], [x, y + 90, width * .22, 140], "hero", 1, 8, True)
        frame = [x + width * .28, y + 110, width * .68, 240]
    else:
        c.rect([x, y + 70, width, 110])
        c.text("chapter_number", content["chapter_number"], [x + 24, y + 95, width - 48, 62], "chapter", 1, 8, True)
        frame = [x + 24, y + 230, width - 48, 220]
    c.text("description", content.get("description", ""), frame, "heading", 0, 72)


def kpi(c):
    x, y, width, height = c.body
    count = c.variant["capacity"]
    gap = c.tokens["spacing"]["lg"]
    item_width = (width - (count - 1) * gap) / count
    card_height = 350 if count == 3 else 320
    values = c.page["content"]["metrics"]
    for index in range(count):
        item = values[index] if index < len(values) else {}
        left = x + index * (item_width + gap)
        c.rect([left, y, item_width, card_height])
        c.text(f"metrics.{index}.label", item.get("label", ""), [left + 20, y + 24, item_width - 40, 66], "heading", 0, 14)
        value = item.get("value")
        display = "" if value is None else format(value, f",.{c.page['config']['decimals']}f")
        c.text(f"metrics.{index}.value", display, [left + 20, y + 116, item_width - 40, 72], "metric", 0, 16, derived=f"metrics.{index}.value + config.decimals")
        c.text(f"metrics.{index}.unit", item.get("unit", ""), [left + 20, y + 198, item_width - 40, 34], "body", 0, 6)
        c.text(f"metrics.{index}.note", item.get("note", ""), [left + 20, y + 248, item_width - 40, card_height - 264], "caption", 0, 54)
    c.text("summary", c.page["content"].get("summary", ""), [x, y + card_height + 32, width, height - card_height - 32], "body", 0, 100)


def parallel(c):
    columns = c.variant.get("columns", 3 if c.variant["id"] == "columns-3" else 1)
    _cards(c, c.variant["capacity"], columns)


def comparison(c):
    x, y, width, height = c.body
    content = c.page["content"]
    gap = c.tokens["spacing"]["xl"]
    half = (width - gap) / 2
    for column, key in enumerate(("left_heading", "right_heading")):
        c.text(key, content[key], [x + column * (half + gap), y, half, 48], "heading", 2, 16, True)
    row_height = (height - 64) / c.variant["capacity"]
    for index in range(c.variant["capacity"]):
        item = c.item(index)
        top = y + 64 + index * row_height
        for column, field in enumerate(("problem", "solution")):
            left = x + column * (half + gap)
            c.rect([left, top, half, row_height - 16])
            c.text(f"pairs.{index}.{field}", item.get(field, ""), [left + 20, top + 20, half - 40, row_height - 78], _body_role(c), 0, 120 if c.variant["capacity"] == 2 else 80)
        c.text(f"pairs.{index}.action", item.get("action", ""), [x + half + gap + 20, top + row_height - 55, half - 40, 30], "caption", 0, 40)


def timeline(c):
    x, y, width, height = c.body
    count = c.variant["capacity"]
    if c.variant["id"] == "vertical-3":
        c.line(x + 190, y + 32, x + 190, y + height - 32)
        for index in range(count):
            item = c.item(index)
            top = y + index * height / count
            c.text(f"events.{index}.time_label", item.get("time_label", ""), [x, top + 20, 160, 70], "heading", 0, 20)
            c.text(f"events.{index}.title", item.get("title", ""), [x + 220, top + 12, width - 220, 52], "heading", 0, 18)
            c.text(f"events.{index}.body", item.get("body", ""), [x + 220, top + 70, width - 220, height / count - 82], _body_role(c), 0, 96)
    else:
        step = width / count
        c.line(x + 20, y + 170, x + width - 20, y + 170)
        for index in range(count):
            item = c.item(index)
            left = x + index * step
            c.element("circle", {"cx": left + 24, "cy": y + 170, "r": c.tokens["shape"]["nodeRadius"], "fill": c.color("primary")}, "layout")
            c.text(f"events.{index}.time_label", item.get("time_label", ""), [left, y + 86, step - 24, 66], "heading", 0, 20)
            c.text(f"events.{index}.title", item.get("title", ""), [left, y + 210, step - 24, 86], "heading", 0, 18)
            c.text(f"events.{index}.body", item.get("body", ""), [left, y + 310, step - 24, height - 310], _body_role(c), 0, 60)


def process(c):
    if c.variant["id"] != "cycle-4":
        _cards(c, c.variant["capacity"], c.variant["capacity"] if c.variant["id"] == "horizontal-5" else 1, field="steps")
        x, y, width, height = c.body
        count = c.variant["capacity"]
        gap = c.tokens["spacing"]["lg"]
        if c.variant["id"] == "horizontal-5":
            cell = (width - gap * (count - 1)) / count
            for index in range(count - 1):
                start = x + (index + 1) * cell + index * gap
                _arrow(c, start + 2, y + height / 2, start + gap - 2, y + height / 2)
        else:
            cell = (height - gap * (count - 1)) / count
            for index in range(count - 1):
                start = y + (index + 1) * cell + index * gap
                _arrow(c, x + width / 2, start + 2, x + width / 2, start + gap - 2)
        return
    _hub(c, 4, "steps", cycle=True)


def _arrow(c, x1, y1, x2, y2):
    c.line(x1, y1, x2, y2)
    distance = math.hypot(x2 - x1, y2 - y1)
    ux, uy = (x2 - x1) / distance, (y2 - y1) / distance
    arrow = c.tokens["spacing"]["xs"]
    points = [(x2, y2), (x2 - ux * arrow - uy * arrow / 2, y2 - uy * arrow + ux * arrow / 2), (x2 - ux * arrow + uy * arrow / 2, y2 - uy * arrow - ux * arrow / 2)]
    c.element("polygon", {"points": " ".join(f"{px},{py}" for px, py in points), "fill": c.color("primary")}, "layout")


def _hub(c, count, field="nodes", cycle=False):
    x, y, width, height = c.body
    cx, cy = x + width / 2, y + height / 2
    radius_x, radius_y = width * .34, height * .32
    centers = []
    for index in range(count):
        angle = -math.pi / 2 + index * 2 * math.pi / count
        nx, ny = cx + radius_x * math.cos(angle), cy + radius_y * math.sin(angle)
        centers.append((nx, ny))
        if not cycle:
            c.line(cx, cy, nx, ny)
    if cycle:
        for index, (sx, sy) in enumerate(centers):
            tx, ty = centers[(index + 1) % count]
            dx, dy = tx - sx, ty - sy
            inset = min(154 / abs(dx) if dx else 1, 60 / abs(dy) if dy else 1)
            _arrow(c, sx + dx * inset, sy + dy * inset, tx - dx * inset, ty - dy * inset)
    elif c.variant["id"] == "ring-5":
        c.element("ellipse", {"cx": cx, "cy": cy, "rx": radius_x, "ry": radius_y, "fill": "none", "stroke": c.color("primary"), "stroke-width": c.tokens["line"]["divider"]}, "layout")
    c.rect([cx - 130, cy - 64, 260, 128])
    center = c.page["content"].get("center", {})
    c.text("center.title", center.get("title", ""), [cx - 110, cy - 43, 220, 44], "heading", 0, 12)
    c.text("center.body", center.get("body", ""), [cx - 110, cy + 8, 220, 44], "caption", 0, 36)
    values = c.page["content"].get(field, [])
    for index in range(count):
        angle = -math.pi / 2 + index * 2 * math.pi / count
        nx, ny = cx + radius_x * math.cos(angle), cy + radius_y * math.sin(angle)
        item = values[index] if index < len(values) else {}
        c.rect([nx - 154, ny - 60, 308, 120])
        c.text(f"{field}.{index}.title", item.get("title", ""), [nx - 114, ny - 44, 228, 46], "heading", 0, 16)
        c.text(f"{field}.{index}.body", item.get("body", ""), [nx - 114, ny + 8, 228, 44], "caption", 0, 48)
        _icon(c, item.get("icon_key", ""), [nx - 146, ny - 44, 24, 24])


def hub(c):
    _hub(c, c.variant["capacity"])


def ending(c):
    x, y, width, height = c.body
    content = c.page["content"]
    if c.variant["id"] == "actions":
        c.text("closing_message", content["closing_message"], [x, y, width, 56], "body", 2, 48, True)
        for index in range(3):
            item = c.item(index)
            top = y + 80 + index * (height - 80) / 3
            c.rect([x, top, width, (height - 80) / 3 - 16])
            c.text(f"actions.{index}.action", item.get("action", ""), [x + 24, top + 20, width * .62, 104], "body", 0, 60)
            c.text(f"actions.{index}.owner", item.get("owner", ""), [x + width * .68, top + 20, width * .28, 42], "caption", 0, 16)
            c.text(f"actions.{index}.date", item.get("date", ""), [x + width * .68, top + 70, width * .28, 42], "caption", 0, 20)
    else:
        c.text("closing_message", content["closing_message"], [x + 40, y + 82, width - 80, 150], "chapter", 2, 48, True)
        c.text("subtitle", content.get("subtitle", ""), [x + 40, y + 270, width - 80, 106], "body", 0, 64)
        c.text("contact_info", content.get("contact_info", ""), [x + 40, y + 414, width - 80, 64], "body", 0, 64)


def strategy(c):
    x, y, width, height = c.body
    content = c.page["content"]
    c.element("polygon", {"points": f"{x},{y+100} {x+width/2},{y} {x+width},{y+100}", "fill": c.color("primary")}, "layout")
    c.text("mission", content["mission"], [x + width * .31, y + 60, width * .38, 40], "heading", 2, 48, True, color_role="surface")
    c.text("vision", content.get("vision", ""), [x + 32, y + 116, width - 64, 60], "body", 0, 72)
    count = c.variant["capacity"]
    gap = c.tokens["spacing"]["lg"]
    card_width = (width - gap * (count - 1)) / count
    limits = c.variant["item_text_limits"]
    for index in range(count):
        item = c.item(index)
        left = x + index * (card_width + gap)
        c.rect([left, y + 196, card_width, 224])
        c.text(f"pillars.{index}.title", item.get("title", ""), [left + 20, y + 220, card_width - 40, 50], "heading", 0, limits["title"])
        c.text(f"pillars.{index}.body", item.get("body", ""), [left + 20, y + 284, card_width - 40, 100], "body", 0, limits["body"])
        _icon(c, item.get("icon_key", ""), [left + card_width - 44, y + 388, 24, 24])
    foundation = content.get("foundation", {})
    c.rect([x, y + 430, width, 98])
    c.text("foundation.title", foundation.get("title", ""), [x + 20, y + 448, width * .23, 50], "heading", 0, 18)
    c.text("foundation.body", foundation.get("body", ""), [x + width * .27, y + 448, width * .7, 60], "body", 0, 100)


def architecture(c):
    x, y, width, height = c.body
    count = c.variant["capacity"]
    row_height = (height - 24 * (count - 1)) / count
    for index in range(count):
        item = c.item(index)
        left = x + (24 * index if c.variant["id"] == "stack-3" else 0)
        top = y + index * (row_height + 24)
        row_width = width - (48 * index if c.variant["id"] == "stack-3" else 0)
        c.rect([left, top, row_width, row_height])
        c.text(f"layers.{index}.title", item.get("title", ""), [left + 20, top + 20, 230, row_height - 32], "heading", 0, 16)
        c.text(f"layers.{index}.body", item.get("body", ""), [left + 280, top + 20, row_width - 304, row_height - 32], _body_role(c), 0, 100)
        _icon(c, item.get("icon_key", ""), [left + 253, top + 20, 24, 24])


def matrix(c):
    x, y, width, height = c.body
    content = c.page["content"]
    cell_width, cell_height = width / 4, height / 5
    padding = c.tokens["table"]["padding"]
    for row in range(5):
        for column in range(4):
            left, top = x + column * cell_width, y + row * cell_height
            c.rect([left + 1, top + 1, cell_width - 2, cell_height - 2], "surfaceMuted" if row == 0 or column == 0 else "surface")
            c.line(left, top + cell_height, left + cell_width, top + cell_height, color="border")
            field, text = "corner_label", content.get("corner_label", "")
            if row == 0 and column:
                field = f"columns.{column-1}"
                text = content["columns"][column-1] if column <= len(content["columns"]) else ""
            elif column == 0 and row:
                field = f"rows.{row-1}"
                text = content["rows"][row-1] if row <= len(content["rows"]) else ""
            elif row and column:
                field = f"cells.{row-1}.{column-1}"
                text = content["cells"][row-1][column-1] if row <= len(content["rows"]) and column <= len(content["columns"]) else ""
                text = "" if text is None else text
            role = c.tokens["table"]["body_role"] if row and column else c.tokens["table"]["header_role"]
            c.text(field, text, [left + padding, top + padding, cell_width - 2 * padding, cell_height - 2 * padding], role, 0, 40 if row and column else 18)


def gantt(c):
    from datetime import date
    x, y, width, height = c.body
    content = c.page["content"]
    start, end = date.fromisoformat(content["start"]), date.fromisoformat(content["end"])
    label_width, owner_width = 250, 160
    plot_x, plot_width = x + label_width, width - label_width - owner_width
    periods = c.variant["periods"]
    axis_start, axis_end = start.toordinal(), end.toordinal() + 1
    axis_days = axis_end - axis_start
    period = f"{start.isoformat()}\n{end.isoformat()}"
    c.text("period_range", period, [x, y, label_width - 16, 44], "caption", 21, 21,
           derived="content.start/content.end inclusive date range")
    label_format = c.page["config"]["date_format"]
    if label_format == "%m":
        label_format = "%m/%d"
    previous_label = None
    task_height = (height - 72) / c.variant["capacity"]
    for index in range(periods + 1):
        left = plot_x + index * plot_width / periods
        c.line(left, y + 48, left, y + height, color="border")
        if index < periods:
            day = date.fromordinal(axis_start + axis_days * index // periods)
            label = day.strftime(label_format)
            if label == previous_label:
                label = ""
            else:
                previous_label = label
            c.text(f"period_labels.{index}", label, [left + 4, y, plot_width / periods - 8, 36], "caption", 0, 20,
                   derived="inclusive date range + equal time segments + config.date_format; repeated labels suppressed")
    for index in range(c.variant["capacity"]):
        item = c.item(index)
        top = y + 66 + index * task_height
        c.text(f"tasks.{index}.name", item.get("name", ""), [x, top, label_width - 16, task_height - 12], "body", 0, 24)
        owner = item.get("owner", "") if c.page["config"]["show_owner"] else ""
        c.text(f"tasks.{index}.owner", owner, [x + width - owner_width + 12, top, owner_width - 12, task_height - 12], "caption", 0, 16)
        if item:
            task_start, task_end = date.fromisoformat(item["start"]), date.fromisoformat(item["end"])
            left = plot_x + (task_start.toordinal() - axis_start) / axis_days * plot_width
            bar_width = (task_end.toordinal() + 1 - task_start.toordinal()) / axis_days * plot_width
            c.rect([left, top + 8, bar_width, 24], "secondary", layer=None)
        progress = item.get("progress")
        text = "" if progress is None or not c.page["config"]["show_progress"] else f"{progress:g}%"
        c.text(f"tasks.{index}.progress", text, [plot_x + 4, top + 36, plot_width - 8, 24], "caption", 0, 8, derived=f"tasks.{index}.progress + config.show_progress")


def chart(c, *, frame=None, content=None, config=None, field_prefix="", include_conclusions=True):
    from pptx_to_svg.normalized_chart_svg import _nice_scale

    x, y, width, height = c.body
    content = c.page["content"] if content is None else content
    config = c.page["config"] if config is None else config
    side = c.variant["id"] == "side"
    chart_width = width * .7 if side else width
    chart_height = height if side else height - 120
    if frame is not None:
        x, y, chart_width, chart_height = frame
    frame = [x, y, chart_width, chart_height]
    compact = chart_height < 240
    axis_role = "diagramMicro" if compact else c.tokens["chart"]["axis_role"]
    identifier = "chart-data" + ("-" + field_prefix.replace(".", "-") if field_prefix else "")

    def text(field, *arguments, **keywords):
        return c.text(field_prefix + field, *arguments, **keywords)
    categories, series = content["categories"], content["series"]
    values = [value for item in series for value in item["values"] if value is not None]
    scale_values = values if any(values) else [0.0, 1.0]
    if compact and config["show_data_labels"]:
        plot_height = chart_height - (42 if config["show_legend"] else 24) - 24
        label_clearance = c.tokens["font"]["sizes"][axis_role] * 1.8
        span = max(scale_values) - min(scale_values) or 1
        padding = span * label_clearance / max(plot_height - 2 * label_clearance, plot_height * .2)
        scale_values = [min(0, min(scale_values)) - padding, max(0, max(scale_values)) + padding]
    minimum, maximum, ticks = _nice_scale(scale_values, include_zero=True)
    if compact:
        ticks = [minimum, maximum]
    major_unit = ticks[1] - ticks[0]
    native = {
        "name": identifier,
        "type": config["chart_type"],
        "x": x,
        "y": y,
        "width": chart_width,
        "height": chart_height,
        "categories": categories,
        "series": series,
        "show_legend": config["show_legend"],
        "axes": {"value": {"minimum": minimum, "maximum": maximum, "major_unit": major_unit}},
        "style": {
            "colors": [c.color(role) for role in c.tokens["chart"]["series_roles"]],
            "font_family": c.tokens["font"]["families"]["body"],
            "axis_font_size": c.tokens["font"]["sizes"][axis_role],
            "legend_font_size": c.tokens["font"]["sizes"]["caption"],
            "text_color": c.color("text"),
            "axis_color": c.color("border"),
            "grid_color": c.color(c.tokens["chart"]["grid_role"]),
            "chart_area_fill": "#FFFFFF",
            "plot_area_fill": "#FFFFFF",
        },
    }
    if config["show_data_labels"]:
        native["data_labels"] = {
            "show_value": True,
            "number_format": "General",
            "font_size": c.tokens["font"]["sizes"]["caption"],
            "font_family": c.tokens["font"]["families"]["body"],
            "color": c.color("text"),
        }
    dynamic_start, slot_start = len(c.dynamic), len(c.slots)
    if compact and content.get("title"):
        native["title"] = {"text": content["title"], "font_size": c.tokens["font"]["sizes"][axis_role]}
        text("title", content["title"], [x, y, chart_width * .55, 20], axis_role, 1, 24, True)
    axis_caption = content.get("axis_title", "")
    if content.get("unit"):
        axis_caption += f"（{content['unit']}）"
    if axis_caption:
        native["axis_titles"] = {"value": axis_caption}
    text("axis_caption", axis_caption, [x + chart_width - 180, y + (0 if compact else 8), 180, 20 if compact else 32], axis_role, 0, 28, derived="content.axis_title + content.unit")
    compact_top = 42 if config["show_legend"] else 24
    left, top, plot_width, plot_height = (x + 42, y + compact_top, chart_width - 56, chart_height - compact_top - 24) if compact else (x + 80, y + 72, chart_width - 112, chart_height - 138)
    if compact:
        native["plot_area"] = {"x": left, "y": top, "width": plot_width, "height": plot_height}
        native["axes"]["category"] = {"label_position": "low"}
    baseline = top + plot_height * maximum / (maximum - minimum)
    for index, value in enumerate(ticks):
        tick_y = top + plot_height * (maximum - value) / (maximum - minimum)
        c.line(left, tick_y, left + plot_width, tick_y, layer=None, color=c.tokens["chart"]["grid_role"])
        text(f"chart_ticks.{index}", f"{value:g}", [x, tick_y - 8 if compact else tick_y - 10, 36 if compact else 70, 20 if compact else 28], axis_role, 1, 16, derived="data domain and shared nice linear scale")
    step = plot_width / len(categories)
    for index, label in enumerate(categories):
        text(f"categories.{index}", label, [left + index * step + 4, top + plot_height + (4 if compact else 16), step - 8, 20 if compact else 48], axis_role, 1, 24, True)
    for series_index, item in enumerate(series):
        segments, points = [], []
        for index, value in enumerate(item["values"]):
            if value is None:
                if points:
                    segments.append(points)
                    points = []
                continue
            px = left + (index + .5) * step
            py = top + plot_height * (maximum - value) / (maximum - minimum)
            if config["chart_type"] == "line":
                points.append(f"{px},{py}")
            else:
                bar_width = step * .65 / len(series)
                px = left + index * step + step * .175 + (series_index + .45) * bar_width
                if value != 0:
                    c.rect([left + index * step + step * .175 + series_index * bar_width, min(py, baseline), bar_width * .9, abs(baseline-py)], c.tokens["chart"]["series_roles"][series_index], layer=None)
            if config["show_data_labels"]:
                label_width = min(step * .9 / len(series), 110)
                label_top = py - 28 if value >= 0 else py + 6
                if compact:
                    label_top = py - 20 if value >= 0 or config["chart_type"] == "line" else py + 4
                    label_top = min(max(y + 20, label_top), y + chart_height - 20)
                text(f"value_labels.{series_index}.{index}", str(value), [px - label_width / 2, label_top, label_width, 20 if compact else 24], axis_role, 1, 24,
                       derived=f"series.{series_index}.values.{index} + config.show_data_labels")
        if points:
            segments.append(points)
        for segment in segments:
            c.element("polyline", {"points": " ".join(segment), "fill": "none", "stroke": c.color(c.tokens["chart"]["series_roles"][series_index]), "stroke-width": c.tokens["line"]["connector"]})
        label = item["name"] if config["show_legend"] else ""
        text(f"series.{series_index}.name", label, [left + series_index * (plot_width - 180) / 2, y + (20 if compact else 8), (plot_width - 180) / 2, 20 if compact else 32], axis_role, 0, 16)
    group = ET.Element("{http://www.w3.org/2000/svg}g", {"id": identifier, "data-pptx-replace-with": "chart", "data-pptx-native-authority": "json", "data-pptx-bounds": " ".join(str(value) for value in frame)})
    ET.SubElement(group, "{http://www.w3.org/2000/svg}metadata", {"type": "application/json"}).text = json.dumps(native, ensure_ascii=False)
    for slot in c.slots[slot_start:]:
        node = slot[0]
        node.attrib.pop("data-pptx-carrier", None)
        group.append(node)
    del c.slots[slot_start:]
    for node in c.dynamic[dynamic_start:]:
        group.append(node)
    del c.dynamic[dynamic_start:]
    c.dynamic.append(group)
    text_frame = [x + chart_width + 28, y + 24, width - chart_width - 28, height - 24] if side else [x, y + chart_height + 24, width, 96]
    if include_conclusions:
        text("conclusions", content["conclusions"], text_frame, "body", 1, 100, True)


def place_local_image(c, item, frame):
    """Place a local picture with the shared contain/cover and focus contract."""
    if not c.asset_root:
        from report_ppt import TemplateInputError
        raise TemplateInputError("image input requires --assets")
    source = (c.asset_root / item["path"]).resolve()
    if not source.is_relative_to(c.asset_root) or not source.is_file() or source.is_symlink():
        from report_ppt import TemplateInputError
        raise TemplateInputError("image path must be a local asset below --assets")
    data = source.read_bytes()
    relative = "images/" + hashlib.sha256(data).hexdigest()[:16] + source.suffix.lower()
    c.assets[relative] = data
    left, top, width, height = frame
    position = c.page["config"].get("image_position", "xMidYMid")
    fit = "meet" if c.page["config"].get("image_fit", "contain") == "contain" else "slice"
    element = c.element("image", {"x": left, "y": top, "width": width, "height": height, "href": "../" + relative, "preserveAspectRatio": f"{position} {fit}"})
    ET.SubElement(element, "{http://www.w3.org/2000/svg}desc").text = item.get("alt", "")
    return element


def image(c):
    x, y, width, height = c.body
    content = c.page["content"]
    gallery = c.variant["id"] == "gallery-3"
    count = 3 if gallery else 1
    images = content.get("images", [])
    sections = content.get("sections", [])
    for index in range(count):
        frame = [x + index * (width + 24) / 3, y, (width - 48) / 3, 240] if gallery else [x + width * .48, y, width * .52, height - 66]
        c.rect(frame)
        item = images[index] if index < len(images) else {}
        if item.get("path"):
            place_local_image(c, item, frame)
        caption_frame = [frame[0], frame[1] + frame[3] + 12, frame[2], 50]
        c.text(f"images.{index}.caption", item.get("caption", ""), caption_frame, "caption", 0, 40)
        section = sections[index] if index < len(sections) else {}
        tx = frame[0] if gallery else x
        ty = y + 330 if gallery else y + 24
        tw = frame[2] if gallery else width * .43
        c.text(f"sections.{index}.title", section.get("title", ""), [tx, ty, tw, 70], "heading", 0, 18)
        c.text(f"sections.{index}.body", section.get("body", ""), [tx, ty + 86, tw, 110 if gallery else height - 130], "body", 0, 72 if gallery else 120)
        _icon(c, section.get("icon_key", ""), [tx, ty - (28 if gallery else 24), 24, 24])


RENDERERS = {
    "cover": cover,
    "toc": toc,
    "chapter": chapter,
    "kpi": kpi,
    "parallel": parallel,
    "comparison": comparison,
    "chart": chart,
    "timeline": timeline,
    "gantt": gantt,
    "process": process,
    "image": image,
    "ending": ending,
    "strategy": strategy,
    "architecture": architecture,
    "matrix": matrix,
    "hub": hub,
}


def render(canvas):
    if canvas.variant.get("renderer") == "source-diagram":
        from report_ppt_source import render as render_source
        render_source(canvas)
        return
    RENDERERS[canvas.page["family"]](canvas)
