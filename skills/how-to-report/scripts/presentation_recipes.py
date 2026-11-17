"""Three finite page recipes lowered to ordinary presentation 0.1 scenes."""
from __future__ import annotations

import copy
import hashlib
from pathlib import Path
import re
import tempfile

from report_ppt import DEFAULT_TEMPLATE, TemplateInputError, external_target, load_template, read_json, validate_schema, fingerprint
from presentation_document import evaluate_facts, resolve_text, resolve_value, validate_document
from presentation_library import SYSTEM, library, profile_identity, profile_path
from presentation_typography import STYLE_FIELDS, measure_text_block, resolve_text_style
from presentation_svg import runtime_helpers


CHILDREN = {"primitive.chart", "primitive.image", "component.partition", "component.comparison",
            "component.progress-ring", "component.paragraph-flow"}
READOUT_ROLES = {"primitive.chart": {"axis": "dataCaption", "legend": "dataCaption", "data_label": "dataCaption"},
                 "component.progress-ring": {"detail": "dataCaption"},
                 "component.partition": {"percent": "dataCaption"}}


def _keys(value, allowed, where):
    if not isinstance(value, dict) or set(value) - set(allowed):
        raise TemplateInputError(f"{where}: expected fields {sorted(allowed)}")


def _identifier(value, where):
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_.-]*", value):
        raise TemplateInputError(f"{where}: require a stable identifier")
    return value


def _text(identifier, bounds, content, role="body", **style):
    return {"id": identifier, "type": "text", "frame": bounds, "text": content,
            "role": role, "style": style}


def _flow(identifier, bounds, paragraphs, gap, role="body"):
    return {"id": identifier, "type": "component", "component": "paragraph-flow", "frame": bounds,
            "role": role, "paragraphs": paragraphs, "style": {"paragraph_gap": gap}}


def _line(tokens, role):
    style = resolve_text_style(tokens, role)
    measured = measure_text_block("0", tokens["canvas"]["width"], style, runtime_helpers())
    return max(style["font_size"] * style["line_height"], measured["height"]) + tokens["spacing"]["xs"]


def _forbid_layout(value, where):
    if isinstance(value, dict):
        forbidden = (STYLE_FIELDS - {"color", "align", "vertical_anchor"}) | {
            "frame", "rotation", "transform", "value_size", "axis_font_size", "legend_font_size",
            "font_face", "bold", "italic", "underline", "plot_padding"}
        normalized = {key.replace("_", "").casefold() for key in value}
        if normalized & {key.replace("_", "").casefold() for key in forbidden}:
            raise TemplateInputError(f"{where}: recipe allocates frames and typography; child geometry/font overrides are unsupported")
        for key, child in value.items():
            _forbid_layout(child, where + "." + key)
    elif isinstance(value, list):
        for child in value:
            _forbid_layout(child, where)


def _forbid_label_colors(value, where):
    if isinstance(value, dict):
        if {key.replace("_", "").casefold() for key in value} & {"color", "colors", "labelcolors", "fontcolor"}:
            raise TemplateInputError(f"{where}: important chart text colors come from dataCaption")
        for key, child in value.items():
            _forbid_label_colors(child, where + "." + key)
    elif isinstance(value, list):
        for child in value:
            _forbid_label_colors(child, where)


def _forbid_chart_text_colors(child, where):
    style = child.get("style", {})
    if isinstance(style, dict) and "textcolor" in {key.replace("_", "").casefold() for key in style}:
        raise TemplateInputError(f"{where}.style: important chart text colors come from dataCaption")
    series = child.get("series", [])
    for scope in [child, *(series if isinstance(series, list) else [])]:
        if isinstance(scope, dict):
            for key, labels in scope.items():
                if key.replace("_", "").casefold() == "datalabels":
                    _forbid_label_colors(labels, where + "." + key)


def _child(child, bounds, where, allowed=CHILDREN):
    if not isinstance(child, dict):
        raise TemplateInputError(f"{where}: expected a registered child")
    _forbid_layout(child, where)
    use = child.get("use")
    if not isinstance(use, str):
        raise TemplateInputError(f"{where}.use: require a library ID")
    if use not in allowed:
        entry = library(identifier=use)
        raise TemplateInputError(f"{where}: {use} status={entry['status']} is not an executable child for this slot")
    result = copy.deepcopy(child)
    result.pop("use")
    _identifier(result.get("id"), where + ".id")
    if "type" in result or "component" in result:
        raise TemplateInputError(f"{where}: use defines child type and component")
    if use.startswith("primitive."):
        result["type"] = use.split(".", 1)[1]
        if result["type"] == "chart" and result.get("chart_type", "column") not in {"bar", "column", "line", "pie", "doughnut"}:
            raise TemplateInputError(f"{where}: chart type has no high-level recipe contract")
        if result["type"] == "chart":
            _forbid_chart_text_colors(result, where)
    else:
        result.update(type="component", component=use.split(".", 1)[1])
    if use in READOUT_ROLES:
        roles = result.get("text_roles", {})
        important_roles = READOUT_ROLES[use]
        if not isinstance(roles, dict) or any(roles.get(key, role) != role for key, role in important_roles.items()):
            raise TemplateInputError(f"{where}: important readout roles must use dataCaption in this recipe")
        style = result.get("style", {})
        if not isinstance(style, dict):
            raise TemplateInputError(f"{where}.style: expected an object")
        if use != "primitive.chart" and {"muted", "color"} & set(style):
            raise TemplateInputError(f"{where}.style: important readout colors come from dataCaption")
        result["text_roles"] = {**roles, **important_roles}
    result["frame"] = bounds
    if bounds[2] < 120 or bounds[3] < 72:
        raise TemplateInputError(f"{where}: slot is below its minimum width/height")
    return result


def _paragraphs(value, where, minimum=1, maximum=3):
    if not isinstance(value, list) or not minimum <= len(value) <= maximum:
        raise TemplateInputError(f"{where}: capacity {minimum}..{maximum}")
    result = []
    for row in value:
        _keys(row, {"id", "text"}, where)
        _identifier(row.get("id"), where + ".id")
        if "text" not in row:
            raise TemplateInputError(f"{where}: paragraph text required")
        result.append(copy.deepcopy(row))
    return result


def _header(page, tokens, index, count):
    identifier = page["id"]
    width = tokens["canvas"]["width"]
    title_frame = tokens["header"]["titleFrame"]
    source_frame = list(tokens["footer"]["textFrame"])
    page_width = tokens["spacing"]["xl"] * 2
    source_frame[2] -= page_width + tokens["spacing"]["md"]
    return [
        _text(identifier + "--title", title_frame, page["title"], "title"),
        {"id": identifier + "--header-rule", "type": "shape", "shape": "line",
         "frame": [tokens["body"]["frame"][0], tokens["header"]["ruleY"], tokens["body"]["frame"][2], 0],
         "stroke": "border", "stroke_width": tokens["line"]["hairline"]},
        _text(identifier + "--source", source_frame, page.get("source", ""), "caption"),
        _text(identifier + "--page", [width - tokens["body"]["frame"][0] - page_width,
              source_frame[1], page_width, source_frame[3]], f"{index}/{count}", "caption", align="right"),
    ]


def _kpi(page, tokens, facts):
    slots = page["slots"]
    _keys(slots, {"metrics", "main", "explanation"}, page["id"] + ".slots")
    metrics = slots.get("metrics")
    if not isinstance(metrics, list) or not 1 <= len(metrics) <= 3:
        raise TemplateInputError("metrics capacity is 1..3")
    x, y, width, height = tokens["body"]["frame"]
    gap = tokens["spacing"]["lg"]
    label_height, value_height, context_height = [_line(tokens, role) for role in ("body", "metric", "dataCaption")]
    value_top = label_height + tokens["spacing"]["xs"]
    context_top = value_top + value_height + tokens["spacing"]["xs"]
    band = context_top + context_height
    metric_width = (width - gap * (len(metrics) - 1)) / len(metrics)
    result = []
    for index, metric in enumerate(metrics):
        _keys(metric, {"id", "label", "value", "unit", "context"}, "metric")
        mid = _identifier(metric.get("id"), "metric.id")
        if not resolve_text(metric.get("label", ""), facts).strip() or not resolve_text(metric.get("unit", ""), facts).strip():
            raise TemplateInputError(f"{mid}: metric label and unit required")
        value = resolve_value(metric.get("value"), facts)
        if type(value) not in (int, float) and not isinstance(value, str):
            raise TemplateInputError(f"{mid}: metric value required")
        raw_value = metric.get("value")
        if isinstance(raw_value, dict) and "ref" in raw_value:
            raw_value = {"ref": raw_value["ref"]}
        if type(resolve_value(raw_value, facts)) not in (int, float):
            raise TemplateInputError(f"{mid}: KPI value must reference or contain a number")
        helpers = runtime_helpers()
        value_layout = measure_text_block(resolve_text(metric["value"], facts), metric_width,
                                         resolve_text_style(tokens, "metric"), helpers)
        unit_layout = measure_text_block(resolve_text(metric["unit"], facts), metric_width,
                                        resolve_text_style(tokens, "body"), helpers)
        if len(value_layout["lines"]) != 1 or len(unit_layout["lines"]) != 1:
            raise TemplateInputError(f"{mid}: metric value and unit must each fit on one line")
        value_width = value_layout["widths"][0] + 2
        unit_width = unit_layout["widths"][0] + 2
        unit_gap = tokens["spacing"]["xs"]
        if value_width + unit_gap + unit_width > metric_width:
            raise TemplateInputError(f"{mid}: adjacent value and unit exceed metric slot width")
        unit_top = value_top + value_layout["baselines"][0] - unit_layout["baselines"][0]
        left = x + index * (metric_width + gap)
        result.extend([
            _text(mid + "--label", [left, y, metric_width, label_height], metric["label"], "body"),
            _text(mid + "--value", [left, y + value_top, value_width, value_height], metric["value"], "metric"),
            _text(mid + "--unit", [left + value_width + unit_gap, y + unit_top,
                                   unit_width, label_height], metric["unit"], "body"),
            _text(mid + "--context", [left, y + context_top, metric_width, context_height], metric.get("context", ""), "dataCaption"),
        ])
    top = y + band + gap
    main_width = (width - gap) * .65
    result.append(_child(slots.get("main"), [x, top, main_width, height - band - gap], "main",
                         CHILDREN - {"component.paragraph-flow", "primitive.image"}))
    paragraphs = _paragraphs(slots.get("explanation"), "explanation")
    result.append(_flow(page["id"] + "--explanation", [x + main_width + gap, top, width - main_width - gap, height - band - gap],
                        paragraphs, tokens["spacing"]["md"]))
    return result


def _paired(page, tokens, facts):
    slots = page["slots"]
    _keys(slots, {"charts", "conclusion"}, page["id"] + ".slots")
    charts = slots.get("charts")
    if not isinstance(charts, list) or len(charts) != 2:
        raise TemplateInputError("paired charts require exactly two charts")
    semantics = []
    children = []
    x, y, width, height = tokens["body"]["frame"]
    gap = tokens["spacing"]["lg"]
    cell = (width - gap) / 2
    heading_height, scope_height = _line(tokens, "heading"), _line(tokens, "dataCaption")
    chart_top = heading_height + scope_height + tokens["spacing"]["sm"] * 2
    conclusion_height = _line(tokens, "body") * 3 + gap
    chart_height = height - conclusion_height - gap - chart_top
    if chart_height < 200:
        raise TemplateInputError("paired chart slot needs at least 200px height")
    for index, panel in enumerate(charts):
        _keys(panel, {"id", "title", "chart", "semantics"}, "paired panel")
        panel_id = _identifier(panel.get("id"), "panel.id")
        semantic = panel.get("semantics")
        _keys(semantic, {"unit", "scope", "period", "scale"}, "chart semantics")
        for key in ("unit", "scope", "period"):
            if not isinstance(semantic.get(key), str) or not semantic[key].strip():
                raise TemplateInputError(f"paired semantics.{key}: nonempty declaration required")
        scale = semantic.get("scale")
        if not isinstance(scale, list) or len(scale) != 2 or any(type(number) not in (int, float) for number in scale):
            raise TemplateInputError("paired scale requires two numeric endpoints")
        if scale[0] != 0 or scale[1] <= scale[0]:
            raise TemplateInputError("paired scale must be zero-based and increasing")
        left = x + index * (cell + gap)
        child = _child(panel.get("chart"), [left, y + chart_top, cell, chart_height], panel_id,
                       {"primitive.chart"})
        if child.get("chart_type", "column") not in {"bar", "column", "line"}:
            raise TemplateInputError("paired charts accept bar, column or line only")
        resolved = resolve_value(child, facts)
        values = [value for series in resolved.get("series", []) for value in series.get("values", [])]
        if not values or any(type(value) not in (int, float) or not scale[0] <= value <= scale[1] for value in values):
            raise TemplateInputError(f"{panel_id}: all series values must be numeric and within declared shared scale")
        supplied_axes = child.get("axes", {})
        axis = supplied_axes.get("value", {})
        if axis.get("minimum", scale[0]) != scale[0] or axis.get("maximum", scale[1]) != scale[1]:
            raise TemplateInputError("chart axes conflict with declared shared scale")
        child["axes"] = copy.deepcopy(supplied_axes)
        child["axes"]["value"] = {**axis, "minimum": scale[0], "maximum": scale[1]}
        semantics.append(semantic)
        children.extend([
            _text(panel_id + "--heading", [left, y, cell, heading_height], panel["title"], "heading"),
            _text(panel_id + "--scope", [left, y + heading_height + tokens["spacing"]["sm"], cell, scope_height],
                  f"{semantic['unit']} · {semantic['scope']} · {semantic['period']}", "dataCaption"), child])
    if any(semantics[0][key] != semantics[1][key] for key in ("unit", "scale")):
        raise TemplateInputError("paired charts require identical declared unit and scale")
    children.append(_flow(page["id"] + "--conclusion", [x, y + height - conclusion_height, width, conclusion_height],
                          _paragraphs(slots.get("conclusion"), "conclusion", maximum=2), tokens["spacing"]["sm"]))
    return children


def _evidence(page, tokens, facts):
    slots = page["slots"]
    _keys(slots, {"rows"}, page["id"] + ".slots")
    rows = slots.get("rows")
    if not isinstance(rows, list) or not 2 <= len(rows) <= 4:
        raise TemplateInputError("evidence-action rows capacity is 2..4")
    x, y, width, height = tokens["body"]["frame"]
    gap, padding = tokens["spacing"]["md"], tokens["spacing"]["md"]
    row_height = (height - gap * (len(rows) - 1)) / len(rows)
    widths = [(width - gap * 2) * ratio for ratio in (.36, .34, .30)]
    result = []
    for index, row in enumerate(rows):
        _keys(row, {"id", "evidence", "action", "verification"}, "evidence row")
        identifier = _identifier(row.get("id"), "row.id")
        top = y + index * (row_height + gap)
        left = x
        for column, width_ in zip(("evidence", "action", "verification"), widths):
            result.append({"id": identifier + "--" + column + "-surface", "type": "shape", "shape": "rect",
                           "frame": [left, top, width_, row_height], "fill": "surfaceMuted", "stroke": "none"})
            bounds = [left + padding, top + padding, width_ - padding * 2, row_height - padding * 2]
            if column == "evidence":
                result.append(_child(row.get(column), bounds, identifier + ".evidence"))
            else:
                paragraphs = [{"id": identifier + "--" + column + "-label", "text": "建议动作" if column == "action" else "复核判断", "role": "bodyStrong"},
                              {"id": identifier + "--" + column + "-text", "text": row.get(column, "")}]
                if not resolve_text(row.get(column, ""), facts).strip():
                    raise TemplateInputError(f"{identifier}.{column}: text required")
                result.append(_flow(identifier + "--" + column, bounds, paragraphs, tokens["spacing"]["sm"]))
            left += width_ + gap
    return result


BUILDERS = {"kpi-chart-explanation": _kpi, "paired-charts-conclusion": _paired, "evidence-action": _evidence}


def lower_recipe_page(page, tokens, facts, index, count, *, schema=None):
    """Recompute a saved recipe request; cached author frames are never consumed."""
    schema = schema if schema is not None else read_json(SYSTEM / "recipe-request.schema.json")
    validate_schema(page, schema["properties"]["pages"]["items"], "recipe source")
    recipe = page["recipe"]
    if recipe not in BUILDERS:
        raise TemplateInputError(f"recipe is not executable: {recipe}")
    return {"id": page["id"], "kind": "scene", "job": page.get("job", page["title"]),
            **({"intent": page["intent"]} if "intent" in page else {}),
            "notes": copy.deepcopy(page.get("notes", "")),
            "elements": _header(page, tokens, index, count) + BUILDERS[recipe](page, tokens, facts)}


def compose_document(request, *, template_root=DEFAULT_TEMPLATE, tokens=None, profile=None, asset_root=None):
    """Lower and actually compile-measure the result before callers publish author JSON."""
    validate_schema(request, read_json(SYSTEM / "recipe-request.schema.json"), "recipe request")
    temporary_root = external_target(tempfile.gettempdir())
    selected = profile or request.get("profile", "report-14pt")
    if profile and "profile" in request and profile != request["profile"]:
        raise TemplateInputError("profile argument conflicts with request")
    identity = profile_identity(selected)
    path = profile_path(selected)
    if tokens is not None and hashlib.sha256(Path(tokens).read_bytes()).hexdigest() != identity["sha256"]:
        raise TemplateInputError("explicit tokens conflict with selected recipe profile")
    _, _, values = load_template(template_root, tokens or path)
    result = {"schema_version": "0.1", "project_id": request["project_id"], "revision": request.get("revision", 1),
              "brief": copy.deepcopy(request.get("brief", {})), "sources": copy.deepcopy(request.get("sources", [])),
              "facts": copy.deepcopy(request["facts"]), "pages": []}
    if "design_profile" in result["brief"] and result["brief"]["design_profile"] != identity:
        raise TemplateInputError("brief.design_profile conflicts with recipe profile")
    result["brief"]["design_profile"] = identity
    usage = {"contract": "0.1", "request_sha256": fingerprint(request), "recipes": {},
             "recipe_source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
             "schema_sha256": hashlib.sha256((SYSTEM / "recipe-request.schema.json").read_bytes()).hexdigest(),
             "comparability_scope": "equal unit and numeric scale/domain are machine-checked; panel scope/period must be declared and displayed; truth and business comparability require review"}
    result["brief"]["recipe_usage"] = usage
    facts = evaluate_facts(result)
    for index, page in enumerate(request["pages"], 1):
        identifier = _identifier(page["id"], "page.id")
        recipe = page["recipe"]
        if recipe not in BUILDERS:
            status = library(identifier=recipe if "." in recipe else "recipe." + recipe)["status"]
            raise TemplateInputError(f"recipe is not executable: {recipe} status={status}")
        lowered = lower_recipe_page(page, values, facts, index, len(request["pages"]))
        lowered["recipe_source"] = copy.deepcopy(page)
        result["pages"].append(lowered)
        usage["recipes"][recipe] = usage["recipes"].get(recipe, 0) + 1
    validate_document(result)
    from presentation_compiler import build_project
    with tempfile.TemporaryDirectory(prefix="htr-recipe-validation-", dir=temporary_root) as temporary:
        build_project(result, Path(temporary) / "project", template_root=template_root,
                      tokens=tokens or path, asset_root=asset_root, geometry_policy="computed")
    return result
