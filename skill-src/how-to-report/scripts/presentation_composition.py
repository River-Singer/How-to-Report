"""Bounded semantic components lowered to the existing editable scene vocabulary."""
from __future__ import annotations

import copy
import math
from decimal import Decimal
import re

from presentation_document import resolve_text, resolve_value
from presentation_svg import frame, number, runtime_helpers
from report_ppt import TemplateInputError, load_template
from presentation_typography import STYLE_FIELDS, measure_text_block, resolve_text_style


COMPONENTS = {
    "topology": {
        "purpose": "Compute editable tree, layered, radial, cycle and arch geometry; cycle arrow-ring provides thick curved stage arrows.",
        "required": ["layout", "nodes"],
        "optional": ["edges", "interior", "variant"],
        "contract_command": "components topology",
        "invariants": ["computed node frames", "native shapes and connector endpoints", "same tokens as the page"],
    },
    "paragraph-flow": {
        "purpose": "Stack measured semantic paragraphs with one shared gap, inset and top alignment.",
        "capacity": {"paragraphs": [1, 20]},
        "required": ["paragraphs"],
        "optional": ["style"],
        "invariants": ["stable paragraph IDs", "text or runs", "shared paragraph gap", "measured overflow rejects publication"],
    },
    "partition": {
        "purpose": "Show an exhaustive composition of one positive total on a shared proportional bar.",
        "capacity": {"segments": [2, 4]},
        "required": ["total", "segments"],
        "optional": ["total_label", "unit", "value_format", "note", "style"],
        "item_fields": {"segments": ["id", "label", "value", "color?", "detail?"]},
        "invariants": ["nonnegative segments sum to total", "stable item IDs", "no inferred missing remainder"],
    },
    "comparison": {
        "purpose": "Compare nonnegative quantities on a common zero-based scale and annotate baseline differences.",
        "capacity": {"rows": [2, 5]},
        "required": ["rows"],
        "optional": ["baseline_id", "delta_label", "unit", "value_format", "note", "style"],
        "item_fields": {"rows": ["id", "label", "value", "color?", "detail?"]},
        "invariants": ["common scale", "baseline must name a row", "differences calculated from the same values"],
    },
    "evidence-map": {
        "purpose": "Connect each evidence statement to its interpretation and proposed action in one row.",
        "capacity": {"rows": [2, 4], "columns": 3},
        "required": ["rows"],
        "optional": ["columns", "note", "style"],
        "item_fields": {"rows": ["id", "evidence", "meaning", "action"]},
        "invariants": ["one row preserves one evidence-to-action mapping", "measured content determines row heights"],
    },
    "progress-ring": {
        "purpose": "Show a bounded share of a positive total as an editable doughnut with label and denominator.",
        "capacity": {"values": 1},
        "required": ["value", "total", "label"],
        "optional": ["detail", "unit", "value_format", "value_prefix", "percent_decimals", "hole_size", "chart_background", "style"],
        "invariants": ["positive total", "0 <= value <= total", "two native data points retain completed and remainder",
                       "label, percentage and value/total remain editable text"],
    },
}

STYLE_SOURCES = {
    "font_family": "font.families.body", "font_size": "font.sizes.body", "value_size": "font.sizes.metric",
    "color": "color.roles.text", "muted": "color.roles.textMuted", "accent": "color.roles.secondary",
    "background": "color.roles.surfaceMuted", "line": "color.roles.border", "difference": "theme.slots.accent5",
}
COMMON = {"id", "type", "component", "frame", "density", "metadata", "source_ref", "content_ref", "relation_ref", "role", "text_roles"}
INTERNAL_LAYOUT = "computed_layout_metrics"
TEXT_ROLES = {"label": "body", "value": "metric", "detail": "caption", "percent": "caption", "note": "caption"}


def component_defaults(tokens):
    """Resolve component defaults from the same validated theme used for rendering."""
    roles, slots = tokens["color"]["roles"], tokens["theme"]["slots"]
    style = {"font_family": tokens["font"]["families"]["body"],
             "font_size": tokens["font"]["sizes"]["body"], "value_size": tokens["font"]["sizes"]["metric"],
             "color": slots[roles["text"]], "muted": slots[roles["textMuted"]],
             "accent": slots[roles["secondary"]], "background": slots[roles["surfaceMuted"]],
             "line": slots[roles["border"]], "difference": slots["accent5"]}
    return style, [slots[f"accent{index}"] for index in range(1, 7)]


def component_catalog(name=None, tokens=None):
    """Return discoverable contracts without leaking mutable module state."""
    if name is not None and name not in COMPONENTS:
        raise TemplateInputError(f"unknown component {name!r}")
    if tokens is None:
        _, _, tokens = load_template()
    from presentation_topology import topology_catalog
    if name == "topology":
        return {**topology_catalog(tokens=tokens),
                "design_preferences": {"automatic_fill": "solid", "gradient": "lowest preference",
                                       "scope": "layout/topology defaults; no general design scoring optimizer"}}
    style, palette = component_defaults(tokens)
    definitions = {name: COMPONENTS[name]} if name else COMPONENTS
    examples = {
        "paragraph-flow": {"id": "flow", "type": "component", "component": "paragraph-flow", "frame": [60, 160, 350, 300],
                           "role": "compactBody", "paragraphs": [{"id": "evidence", "text": "当前观察"},
                                                                   {"id": "next", "text": "后续判断"}],
                           "style": {"paragraph_gap": 12}},
        "partition": {"id": "adoption", "type": "component", "component": "partition", "frame": [60, 150, 1100, 300],
                      "total": {"ref": "total"}, "total_label": "已分配席位", "unit": "人",
                      "segments": [{"id": "enabled", "label": "已激活", "value": {"ref": "enabled"}},
                                   {"id": "remaining", "label": "待激活", "value": {"ref": "remaining"}}]},
        "comparison": {"id": "usage", "type": "component", "component": "comparison", "frame": [60, 150, 1100, 280],
                       "baseline_id": "planned", "delta_label": "差额", "unit": "万点",
                       "rows": [{"id": "planned", "label": "月度基准", "value": {"ref": "planned"}},
                                {"id": "actual", "label": "实际用量", "value": {"ref": "actual"}}]},
        "evidence-map": {"id": "decisions", "type": "component", "component": "evidence-map", "frame": [60, 150, 1100, 430],
                         "columns": ["观察", "判断", "下一步建议"],
                         "rows": [{"id": "activation", "evidence": "启用仍有缺口", "meaning": "先确认未启用人群", "action": "验证一组真实任务"},
                                  {"id": "cost", "evidence": "使用台账存在差异", "meaning": "预算判断需统一口径", "action": "先核对统计范围"}]},
        "progress-ring": {"id": "progress", "type": "component", "component": "progress-ring",
                          "frame": [60, 150, 200, 135], "value": {"ref": "enabled"}, "total": {"ref": "total"},
                          "label": "当前比例", "value_format": ",.0f", "percent_decimals": 1, "hole_size": 75,
                          "style": {"font_size": 12, "value_size": 20}},
    }
    return {"component_contract": "0.1", "scene_type": "component", "definitions": copy.deepcopy(definitions),
            "common_required": ["id", "type=component", "component", "frame"],
            "density": {"default": "comfortable", "values": ["comfortable", "compact"],
                        "compact": "tighter font-relative spacing; partition value and share share one row; explicit font sizes are retained"},
            "style_defaults": style, "style_sources": copy.deepcopy(STYLE_SOURCES), "palette": palette,
            "text_roles": copy.deepcopy(TEXT_ROLES), "text_style_fields": sorted(STYLE_FIELDS),
            "palette_source": "theme.slots.accent1..accent6",
            "examples": {key: examples[key] for key in definitions if key in examples},
            "topology": topology_catalog(tokens=tokens) if name is None else None,
            "design_preferences": {"automatic_fill": "solid", "gradient": "lowest preference",
                                   "scope": "layout/topology defaults; no general design scoring optimizer"},
            "output": "native editable group with stable child IDs",
            "intrinsic_layout": {"entry": "layout leaf sizing=intrinsic", "supported": ["progress-ring"],
                                 "measure": "actual formatted value, label, denominator and detail; typography unchanged",
                                 "uniform": "grid uniform_components=true shares circle and text-slot geometry",
                                 "other_components": "require existing explicit height/aspect/stretched allocation"},
            "failure_behavior": "reject unsupported fields, capacity, invalid values, inconsistent totals and measured overflow without publishing",
            "measurement": "runtime DrawingML estimator; target rendering remains a separate check"}


class Composition:
    def __init__(self, item, facts, canvas, tokens=None):
        self.item, self.facts = item, facts
        self.identifier = item.get("id", "")
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_.:-]*", str(self.identifier)):
            raise TemplateInputError("component id must be a stable SVG-compatible identifier")
        self.kind = item.get("component")
        if self.kind not in COMPONENTS:
            raise TemplateInputError(f"{self.identifier}: unknown component {self.kind!r}")
        definition = COMPONENTS[self.kind]
        unknown = set(item) - COMMON - {INTERNAL_LAYOUT} - set(definition["required"]) - set(definition["optional"])
        if unknown:
            raise TemplateInputError(f"{self.identifier}: unsupported component fields {sorted(unknown)}")
        for key in definition["required"]:
            if key not in item:
                raise TemplateInputError(f"{self.identifier}: missing component field {key}")
        self.x, self.y, self.width, self.height = frame(item.get("frame"), self.identifier, canvas)
        if tokens is None:
            _, _, tokens = load_template()
        defaults, self.palette = component_defaults(tokens)
        self.tokens = tokens
        families = tokens["font"]["families"]
        self.measurement_fonts = {"latin": families["latin"], "ea": families["body"], "cs": families["fallback"]}
        supplied = item.get("style", {})
        if not isinstance(supplied, dict) or set(supplied) - set(STYLE_SOURCES) - STYLE_FIELDS:
            raise TemplateInputError(f"{self.identifier}: unsupported component style fields")
        self.style = {**defaults, **supplied}
        self.supplied_style = supplied
        roles = item.get("text_roles", {})
        if not isinstance(roles, dict) or set(roles) - set(TEXT_ROLES):
            raise TemplateInputError(f"{self.identifier}: unsupported text_roles")
        known_roles = {*tokens["font"]["sizes"], *tokens["font"].get("textStyles", {})}
        default_role = item.get("role", "body")
        default_role = default_role if default_role in known_roles else "body"
        self.text_roles = {**TEXT_ROLES, "label": default_role, **roles}
        self.text_styles = {purpose: self.resolve_component_style(purpose) for purpose in TEXT_ROLES}
        self.size = self.text_styles["label"]["font_size"]
        self.value_size = self.text_styles["value"]["font_size"]
        self.detail_size = self.text_styles["detail"]["font_size"]
        self.percent_size = self.text_styles["percent"]["font_size"]
        density = item.get("density", "comfortable")
        if density not in {"comfortable", "compact"}:
            raise TemplateInputError(f"{self.identifier}: density must be comfortable or compact")
        self.compact = density == "compact"
        self.spacing = self.size / 22 * (.55 if self.compact else 1)
        self.children = []
        if not isinstance(item.get("metadata", {}), dict):
            raise TemplateInputError(f"{self.identifier}: metadata must be an object")
        self.wrap, self.baseline, _, _ = runtime_helpers()
        self.content_bottom = self.y + self.height
        if "note" in item:
            note_height = self.text_height(item["note"], self.width, purpose="note")
            self.content_bottom -= note_height + 16 * self.spacing
            self.text("note", [self.x, self.content_bottom + 16 * self.spacing, self.width, note_height], item["note"],
                      color=self.style["muted"], purpose="note")
        if self.content_bottom <= self.y:
            raise TemplateInputError(f"{self.identifier}: note leaves no component content area")

    def child_id(self, suffix):
        return self.identifier + "--" + suffix

    def resolve_component_style(self, purpose, size=None, weight=None, color=None, align=None):
        supplied = {key: value for key, value in self.supplied_style.items() if key in STYLE_FIELDS}
        if purpose == "value" and "value_size" in self.supplied_style:
            supplied["font_size"] = self.supplied_style["value_size"]
        supplied.update({key: value for key, value in {"font_size": size, "weight": weight, "color": color, "align": align}.items() if value is not None})
        try:
            return resolve_text_style(self.tokens, self.text_roles[purpose], supplied)
        except ValueError as exc:
            raise TemplateInputError(f"{self.identifier}: {exc}") from exc

    def text_height(self, value, width, size=None, weight=None, purpose="label"):
        style = self.resolve_component_style(purpose, size, weight)
        left, top, right, bottom = style["insets"]
        try:
            layout = measure_text_block(resolve_text(value, self.facts), width - left - right, style, (self.wrap, self.baseline))
        except ValueError as exc:
            raise TemplateInputError(f"{self.identifier}: {exc}") from exc
        return layout["height"] + top + bottom

    def text(self, suffix, bounds, value, *, size=None, color=None, weight=None, align=None, purpose=None):
        if purpose is None:
            ending = suffix.rsplit("--", 1)[-1].rsplit("-", 1)[-1]
            purpose = {"value": "value", "percentage": "value", "share": "percent", "detail": "detail", "delta": "detail", "note": "note", "denominator": "detail"}.get(ending, "label")
        style = self.resolve_component_style(purpose, size, weight, color, align)
        self.children.append({"id": self.child_id(suffix), "type": "text", "frame": bounds,
                              "text": value, "role": self.text_roles[purpose], "style": style})

    def paragraph_flow(self):
        paragraphs = self.item["paragraphs"]
        if not isinstance(paragraphs, list) or not 1 <= len(paragraphs) <= 20:
            raise TemplateInputError(f"{self.identifier}: paragraphs capacity is 1..20")
        style = self.text_styles["label"]
        if style["vertical_anchor"] != "top":
            raise TemplateInputError(f"{self.identifier}: paragraph-flow requires top vertical_anchor")
        left, top, right, bottom = style["insets"]
        width = self.width - left - right
        cursor = self.y + top
        seen = set()
        for paragraph in paragraphs:
            if not isinstance(paragraph, dict) or set(paragraph) - {"id", "role", "text", "runs", "style"} or ("text" in paragraph) == ("runs" in paragraph):
                raise TemplateInputError(f"{self.identifier}: paragraph requires id and exactly one of text or runs")
            identifier = paragraph.get("id")
            if not isinstance(identifier, str) or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_.:-]*", identifier) or identifier in seen:
                raise TemplateInputError(f"{self.identifier}: paragraph IDs must be unique stable identifiers")
            seen.add(identifier)
            role = paragraph.get("role", self.text_roles["label"])
            paragraph_style = paragraph.get("style", {})
            if not isinstance(paragraph_style, dict) or {"insets", "paragraph_gap"} & set(paragraph_style):
                raise TemplateInputError(f"{self.identifier}: paragraph insets and paragraph_gap belong to the shared flow style")
            shared_style = {key: value for key, value in self.supplied_style.items() if key in STYLE_FIELDS - {"insets", "paragraph_gap"}}
            local = resolve_text_style(self.tokens, role, {**shared_style, **paragraph_style})
            if local["vertical_anchor"] != "top":
                raise TemplateInputError(f"{self.identifier}: paragraph-flow requires top vertical_anchor")
            local["insets"] = [0, 0, 0, 0]
            local["paragraph_gap"] = 0
            runs = paragraph.get("runs", [{"text": paragraph.get("text", "")}])
            if not isinstance(runs, list) or not runs or any(not isinstance(run, dict) or "text" not in run or set(run) - {"text", "weight", "color"} for run in runs):
                raise TemplateInputError(f"{self.identifier}: paragraph runs require text and support weight/color")
            value = "".join(resolve_text(run["text"], self.facts) for run in runs)
            weights = [resolve_text_style(self.tokens, role, {"weight": run.get("weight", local["weight"])})["weight"] for run in runs]
            layout = measure_text_block(value, width, {**local, "weight": max(weights)}, (self.wrap, self.baseline))
            height = layout["height"]
            self.children.append({"id": self.child_id(identifier), "type": "text", "role": role,
                                  "frame": [self.x + left, cursor, width, height], "runs": runs, "style": local})
            cursor += height + style["paragraph_gap"]
        if cursor - style["paragraph_gap"] > self.y + self.height - bottom + .01:
            raise TemplateInputError(f"{self.identifier}: measured paragraphs exceed component frame")

    def shape(self, suffix, bounds, fill, *, stroke="none", shape="rect"):
        self.children.append({"id": self.child_id(suffix), "type": "shape", "frame": bounds,
                              "shape": shape, "fill": fill, "stroke": stroke, "stroke_width": 1})

    def items(self, key):
        items = self.item.get(key)
        lower, upper = COMPONENTS[self.kind]["capacity"][key]
        if not isinstance(items, list) or not lower <= len(items) <= upper:
            raise TemplateInputError(f"{self.identifier}: {key} capacity is {lower}..{upper}")
        allowed = {field.rstrip("?") for field in COMPONENTS[self.kind]["item_fields"][key]}
        required = {field for field in COMPONENTS[self.kind]["item_fields"][key] if not field.endswith("?")}
        seen = set()
        for item in items:
            if not isinstance(item, dict) or set(item) - allowed or not required.issubset(item):
                raise TemplateInputError(f"{self.identifier}: each {key} item requires {sorted(required)} and supports {sorted(allowed)}")
            identifier = item.get("id")
            if not isinstance(identifier, str) or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_.:-]*", identifier) or identifier in seen:
                raise TemplateInputError(f"{self.identifier}: {key} item IDs must be unique stable identifiers")
            seen.add(identifier)
        return items

    def quantity(self, value, label):
        return number(resolve_value(value, self.facts), self.identifier + "." + label, 0)

    def formatted(self, value):
        return resolve_text({"ref": "value", "format": self.item.get("value_format", "integer")}, {"value": value})

    def value_text(self, value):
        return self.formatted(value) + resolve_text(self.item.get("unit", ""), self.facts)

    def delta_text(self, value, baseline):
        delta = value - baseline
        return resolve_text(self.item.get("delta_label", "Δ"), self.facts) + " " + ("+" if delta > 0 else "") + self.value_text(delta)

    def partition(self):
        segments = self.items("segments")
        total = self.quantity(self.item["total"], "total")
        values = [self.quantity(item["value"], item["id"] + ".value") for item in segments]
        if total <= 0 or abs(sum(Decimal(str(v)) for v in values) - Decimal(str(total))) > Decimal(str(total)) * Decimal("1e-10"):
            raise TemplateInputError(f"{self.identifier}: partition requires a positive total and segments summing to total")
        header_height = max(self.text_height(self.item.get("total_label", ""), self.width * .55),
                            self.text_height(self.value_text(total), self.width * .4, self.value_size, weight=700, purpose="value"))
        if "total_label" in self.item:
            self.text("total-label", [self.x, self.y, self.width * .55, header_height], self.item["total_label"])
        self.text("total-value", [self.x + self.width * .6, self.y, self.width * .4, header_height],
                  self.value_text(total), size=self.value_size, weight=700, align="right")
        bar_y = self.y + header_height + 16 * self.spacing
        bar_height = self.size if self.compact else max(24, self.size * 1.5)
        position = self.x
        gap = 20 * self.spacing
        column_width = (self.width - gap * (len(segments) - 1)) / len(segments)
        label_y = bar_y + bar_height + 20 * self.spacing
        share_color = (self.style["muted"] if "muted" in self.supplied_style
                       or "percent" not in self.item.get("text_roles", {}) else None)
        for index, (item, value) in enumerate(zip(segments, values)):
            color = item.get("color", self.palette[index])
            width = self.width * value / total
            if value > 0:
                self.shape(item["id"] + "--bar", [position, bar_y, width, bar_height], color)
            position += width
            left = self.x + index * (column_width + gap)
            label_inset = max(8, 12 * self.spacing)
            label_height = self.text_height(item["label"], column_width - label_inset)
            key_height = min(self.size, label_height)
            key_top = label_y + (label_height - key_height) / 2
            self.shape(item["id"] + "--key", [left, key_top, 4, key_height], color)
            self.text(item["id"] + "--label", [left + label_inset, label_y, column_width - label_inset, label_height], item["label"])
            top = label_y + label_height + 8 * self.spacing
            metric = self.value_text(value)
            share = format(value / total, ".1%")
            share_size = self.percent_size
            if self.compact:
                from text_measure import measure_text
                share_style = self.resolve_component_style("percent", share_size)
                share_width = (measure_text(share, size=share_size, family=share_style["font_family"], weight=str(share_style["weight"]))
                               + share_style["insets"][0] + share_style["insets"][2] + 2)
                metric_width = column_width - share_width - 8 * self.spacing
            else:
                metric_width = column_width
            metric_height = self.text_height(metric, metric_width, self.value_size, weight=700, purpose="value")
            self.text(item["id"] + "--value", [left, top, metric_width, metric_height], metric, size=self.value_size, weight=700)
            share_height = self.text_height(share, share_width if self.compact else column_width, share_size, purpose="percent")
            if self.compact:
                self.text(item["id"] + "--share", [left + column_width - share_width, top + max(0, metric_height - share_height), share_width, share_height],
                          share, size=share_size, color=share_color, align="right")
                top += max(metric_height, share_height) + 10 * self.spacing
            else:
                top += metric_height + 4 * self.spacing
                self.text(item["id"] + "--share", [left, top, column_width, share_height], share, size=share_size, color=share_color)
                top += share_height + 10 * self.spacing
            if "detail" in item:
                detail_height = self.text_height(item["detail"], column_width, self.detail_size, purpose="detail")
                self.text(item["id"] + "--detail", [left, top, column_width, detail_height], item["detail"],
                          size=self.detail_size, color=self.style["muted"])
                top += detail_height
            if top > self.content_bottom + .01:
                raise TemplateInputError(f"{self.identifier}: partition labels exceed component height, enlarge frame or simplify content")

    def comparison(self):
        rows = self.items("rows")
        values = [self.quantity(row["value"], row["id"] + ".value") for row in rows]
        maximum = max(values)
        if maximum <= 0:
            raise TemplateInputError(f"{self.identifier}: comparison needs at least one positive value")
        baseline_id = self.item.get("baseline_id")
        by_id = {row["id"]: value for row, value in zip(rows, values)}
        if baseline_id is not None and baseline_id not in by_id:
            raise TemplateInputError(f"{self.identifier}: baseline_id must name a comparison row")
        label_width = self.width * .22
        value_width = self.width * .16
        delta_width = self.width * .22 if baseline_id is not None else 0
        bar_x = self.x + label_width + 16
        bar_width = self.width - label_width - value_width - delta_width - 36
        if bar_width < 60:
            raise TemplateInputError(f"{self.identifier}: comparison frame leaves insufficient bar width")
        heights = []
        bottom_gap = 20 * self.spacing
        for row in rows:
            main = max(self.text_height(row["label"], label_width), self.text_height(self.value_text(by_id[row["id"]]), value_width, self.value_size, weight=700, purpose="value"))
            if baseline_id is not None and row["id"] != baseline_id:
                main = max(main, self.text_height(self.delta_text(by_id[row["id"]], by_id[baseline_id]), delta_width, self.detail_size, weight=700, purpose="detail"))
            detail = self.text_height(row["detail"], self.width - label_width - 16, self.detail_size, purpose="detail") + 8 * self.spacing if "detail" in row else 0
            heights.append(max(main, 30) + detail + bottom_gap)
        if sum(heights) > self.content_bottom - self.y + .01:
            raise TemplateInputError(f"{self.identifier}: comparison rows exceed component height, enlarge frame or simplify content")
        free = self.content_bottom - self.y - sum(heights)
        row_gap = min(24 * self.spacing, free / (len(rows) - 1))
        top = self.y
        if baseline_id is not None:
            guide_x = bar_x + bar_width * by_id[baseline_id] / maximum
            self.shape("baseline-guide", [guide_x, self.y, 0, sum(heights) + row_gap * (len(rows) - 1) - bottom_gap],
                       "none", stroke=self.style["line"], shape="line")
        for row, value, height in zip(rows, values, heights):
            self.text(row["id"] + "--label", [self.x, top, label_width, height - bottom_gap], row["label"])
            width = bar_width * value / maximum
            if width > 0:
                self.shape(row["id"] + "--bar", [bar_x, top + 5, width, 22], row.get("color", self.style["accent"]))
            self.text(row["id"] + "--value", [bar_x + bar_width + 12, top, value_width, height - bottom_gap], self.value_text(value), weight=700)
            if baseline_id is not None and row["id"] != baseline_id:
                delta_text = self.delta_text(value, by_id[baseline_id])
                left = self.x + self.width - delta_width
                delta_height = self.text_height(delta_text, delta_width, self.detail_size, weight=700, purpose="detail")
                self.text(row["id"] + "--delta", [left, top, delta_width, delta_height], delta_text,
                          size=self.detail_size, color=self.style["difference"], weight=700)
                if delta_height > height - bottom_gap:
                    raise TemplateInputError(f"{self.identifier}: difference annotation exceeds its row")
            if "detail" in row:
                detail_top = top + height - bottom_gap - self.text_height(row["detail"], self.width - label_width - 16, self.detail_size, purpose="detail")
                self.text(row["id"] + "--detail", [bar_x, detail_top, self.width - label_width - 16, height - (detail_top - top) - bottom_gap],
                          row["detail"], size=self.detail_size, color=self.style["muted"])
            top += height + row_gap

    def evidence_map(self):
        rows = self.items("rows")
        columns = self.item.get("columns", ["证据", "判断", "建议行动"])
        if not isinstance(columns, list) or len(columns) != 3:
            raise TemplateInputError(f"{self.identifier}: evidence-map requires exactly three column titles")
        gap, inset = 26 * self.spacing, 16 * (self.size / 22) * (.65 if self.compact else 1)
        width = (self.width - gap * 2) / 3
        if width <= inset * 2:
            raise TemplateInputError(f"{self.identifier}: evidence-map frame leaves insufficient column width")
        header_height = max(self.text_height(title, width, weight=700) for title in columns)
        for index, title in enumerate(columns):
            self.text(f"column-{index + 1}", [self.x + index * (width + gap), self.y, width, header_height], title,
                      weight=700, color=self.style["muted"])
        heights = [max(self.text_height(row[key], width - inset * 2, weight=700 if key == "meaning" else 400)
                       for key in ("evidence", "meaning", "action")) + inset * 2 for row in rows]
        row_gap = 16 * self.spacing
        top = self.y + header_height + 14 * self.spacing
        if top + sum(heights) + row_gap * (len(rows) - 1) > self.content_bottom + .01:
            needed = top - self.y + sum(heights) + row_gap * (len(rows) - 1)
            raise TemplateInputError(f"{self.identifier}: evidence-map rows need {needed:.1f}px, exceed component content height {self.content_bottom-self.y:.1f}px")
        for row, height in zip(rows, heights):
            for index, key in enumerate(("evidence", "meaning", "action")):
                left = self.x + index * (width + gap)
                suffix = row["id"] + "--" + key
                self.shape(suffix + "-surface", [left, top, width, height], self.style["background"])
                self.text(suffix, [left + inset, top + inset, width - inset * 2, height - inset * 2], row[key],
                          weight=700 if key == "meaning" else 400)
                if index:
                    previous = ("evidence", "meaning")[index - 1]
                    self.children.append({"id": self.child_id(row["id"] + "--edge-" + key), "type": "connector",
                        "from": self.child_id(row["id"] + "--" + previous + "-surface"),
                        "to": self.child_id(suffix + "-surface"), "stroke": self.style["accent"],
                        "stroke_width": 1.5, "arrow": True})
            top += height + row_gap

    def ring_content(self):
        value = self.quantity(self.item["value"], "value")
        total = self.quantity(self.item["total"], "total")
        if total <= 0 or value > total:
            raise TemplateInputError(f"{self.identifier}: progress-ring requires total > 0 and 0 <= value <= total")
        label = resolve_text(self.item["label"], self.facts)
        if not label.strip():
            raise TemplateInputError(f"{self.identifier}: progress-ring requires a visible label")
        precision = number(self.item.get("percent_decimals", 1), self.identifier + ".percent_decimals", 0)
        if precision > 4 or not precision.is_integer():
            raise TemplateInputError(f"{self.identifier}: percent_decimals must be an integer from 0 to 4")
        hole = number(self.item.get("hole_size", 75), self.identifier + ".hole_size", 10)
        if hole > 90 or not hole.is_integer():
            raise TemplateInputError(f"{self.identifier}: hole_size must be an integer from 10 to 90")
        prefix = self.item.get("value_prefix", "")
        if not isinstance(prefix, str):
            raise TemplateInputError(f"{self.identifier}: value_prefix must be a string")
        denominator = prefix + self.formatted(value) + " / " + self.value_text(total)
        percentage = format(value / total, f".{int(precision)}%")
        if value == 0 or value == total:
            percentage = "0%" if value == 0 else "100%"
        return value, total, label, denominator, percentage, int(hole)

    def measure_progress_ring(self):
        """Intrinsic marks keep their size when captions need additional lines."""
        from text_measure import measure_text, text_box
        _, _, label, denominator, percentage, hole = self.ring_content()

        def width(text, purpose, weight=None):
            style = self.resolve_component_style(purpose, weight=weight)
            return max((measure_text(line, size=style["font_size"], family=style["font_family"],
                                     weight=str(style["weight"])) for line in text.split("\n")), default=0) + style["insets"][0] + style["insets"][2]

        value_width = width(percentage, "value", 700) + 2
        value_height = self.text_height(percentage, max(value_width, 1), self.value_size, 700, purpose="value") + 2
        # The entire value rectangle fits inside the circular hole, including
        # its corners. This is a measured geometric minimum, not a chosen px size.
        diameter = math.ceil(math.hypot(value_width, value_height) * 100 / hole * 1000) / 1000
        strings = [(label, "label", 700), (denominator, "detail", None)]
        if "detail" in self.item:
            strings.append((resolve_text(self.item["detail"], self.facts), "detail", None))
        preferred = max(diameter, *(width(value, purpose, weight) for value, purpose, weight in strings))
        # Report true nonbreaking units. Chinese phrases may wrap; a long Latin
        # token or formatted number cannot silently break to fit a thin track.
        minimum = diameter
        for value, purpose, weight in strings:
            style = self.resolve_component_style(purpose, weight=weight)
            for paragraph in value.split("\n"):
                oversized = self.wrap(paragraph, size=style["font_size"], max_width=1,
                                      family=style["font_family"], weight=str(style["weight"]))[2]
                minimum = max(minimum, *(unit_width + style["insets"][0] + style["insets"][2] for _, unit_width in oversized)) if oversized else minimum
        metrics = {"diameter": diameter, "hole_size": hole,
                   "label_height": self.text_height(label, self.width, weight=700),
                   "denominator_height": self.text_height(denominator, self.width, purpose="detail"),
                   "detail_height": self.text_height(self.item["detail"], self.width, purpose="detail") if "detail" in self.item else 0,
                   "gap": max(4, 4*self.spacing)}
        # DrawingML's advance box ends at 0.25em descent, while the existing
        # quality gate uses text_box's visible 0.35em descent. Reserve the
        # measured terminal overhang in the component, including authored
        # bottom insets, without changing legacy explicit-frame text layout.
        terminal = self.item.get("detail", denominator)
        style = self.resolve_component_style("detail")
        left, _top, right, bottom = style["insets"]
        layout = measure_text_block(resolve_text(terminal, self.facts), self.width-left-right,
                                    style, (self.wrap, self.baseline))
        envelope = text_box(x=0, baseline_y=layout["baselines"][-1], size=style["font_size"],
                            lines=1, dy=style["font_size"]*style["line_height"],
                            width=max(layout["widths"], default=0), anchor="start")
        metrics["bottom_padding"] = max(0, envelope["bottom"]-layout["height"]-bottom)
        return {"component": "progress-ring", "minimum_width": minimum, "preferred_width": preferred,
                "natural_height": ring_metrics_height(metrics), "metrics": metrics}

    def progress_ring(self):
        value, total, label, denominator, percentage, hole = self.ring_content()
        label_height = self.text_height(label, self.width, weight=700)
        denominator_height = self.text_height(denominator, self.width, purpose="detail")
        detail_height = self.text_height(self.item["detail"], self.width, purpose="detail") if "detail" in self.item else 0
        gap = max(4, 4 * self.spacing)
        computed = self.item.get(INTERNAL_LAYOUT)
        if computed is not None:
            expected = self.measure_progress_ring()["metrics"]
            if not isinstance(computed, dict) or set(computed) != set(expected):
                raise TemplateInputError(f"{self.identifier}: invalid computed component layout metrics")
            for key in expected:
                number(computed[key], self.identifier + "." + INTERNAL_LAYOUT + "." + key, 0)
                if computed[key] + .001 < expected[key] or key == "hole_size" and computed[key] != expected[key]:
                    raise TemplateInputError(f"{self.identifier}: computed component layout cannot contain current content")
            if computed["diameter"] > self.width + .01 or ring_metrics_height(computed) > self.height + .01:
                raise TemplateInputError(f"{self.identifier}: computed ring geometry exceeds component frame")
            label_height, denominator_height, detail_height, gap = (computed[key] for key in ("label_height", "denominator_height", "detail_height", "gap"))
        top = self.y + label_height + gap
        reserved = denominator_height + gap + (detail_height + gap if detail_height else 0)
        diameter = computed["diameter"] if computed else min(self.width, self.content_bottom - top - reserved)
        if diameter <= 0:
            raise TemplateInputError(f"{self.identifier}: label and denominator leave no ring area")
        left = self.x + (self.width - diameter) / 2
        self.text("label", [self.x, self.y, self.width, label_height], label, weight=700, align="center")
        self.children.append({"id": self.child_id("ring"), "type": "chart", "chart_type": "doughnut",
                              "frame": [left, top, diameter, diameter], "hole_size": int(hole),
                              "categories": ["Value", "Remaining"],
                              "series": [{"name": label, "values": [value, total - value],
                                          "point_colors": [self.style["accent"], self.style["background"]]}],
                              "show_legend": False, "data_labels": False, "plot_padding": [0, 0, 0, 0],
                              "style": {"font_family": self.style["font_family"],
                                        "chart_area_fill": self.item.get("chart_background", "none"),
                                        "plot_area_fill": self.item.get("chart_background", "none")}})
        inner = diameter * hole / 100
        text_height = self.text_height(percentage, inner, self.value_size, 700, purpose="value")
        if text_height > inner:
            raise TemplateInputError(f"{self.identifier}: percentage exceeds ring hole; enlarge the frame or set an explicit smaller value_size")
        self.text("percentage", [left + (diameter - inner) / 2, top + (diameter - text_height) / 2, inner, text_height],
                  percentage, size=self.value_size, weight=700, align="center")
        bottom = top + diameter + gap
        self.text("denominator", [self.x, bottom, self.width, denominator_height], denominator, align="center")
        if detail_height and "detail" in self.item:
            self.text("detail", [self.x, bottom + denominator_height + gap, self.width, detail_height],
                      self.item["detail"], color=self.style["muted"], align="center")

    def render(self):
        getattr(self, self.kind.replace("-", "_"))()
        bounds = (self.x, self.y, self.x + self.width, self.y + self.height)
        for child in self.children:
            if "frame" not in child:
                continue
            x, y, width, height = child["frame"]
            if x < bounds[0] - .01 or y < bounds[1] - .01 or x + width > bounds[2] + .01 or y + height > bounds[3] + .01:
                raise TemplateInputError(f"{self.identifier}: generated child {child['id']} exceeds component frame")
        metadata = {**self.item.get("metadata", {}), "component": self.kind, "component_contract": "0.1",
                    "component_frame": self.item["frame"], "text_roles": self.text_roles}
        group = {key: copy.deepcopy(value) for key, value in self.item.items() if key in COMMON - {"component", "frame", "density", "type", "metadata", "text_roles"}}
        group.update(type="group", children=self.children, metadata=metadata)
        return group


def ring_metrics_height(metrics):
    return (metrics["label_height"] + metrics["diameter"] + metrics["denominator_height"]
            + 2*metrics["gap"] + (metrics["detail_height"] + metrics["gap"] if metrics["detail_height"] else 0)
            + metrics["bottom_padding"])


def measure_component_intrinsic(element, facts, tokens, width=None):
    """Finite first adapter: progress-ring. No arbitrary component guesses."""
    if element.get("component") != "progress-ring":
        raise TemplateInputError("intrinsic sizing currently supports progress-ring only")
    sample = {**copy.deepcopy(element), "id": element.get("id", "intrinsic-probe"),
              "frame": [0, 0, width if width is not None else 1000000, 1000000]}
    sample.pop(INTERNAL_LAYOUT, None)
    return Composition(sample, facts, [1000000, 1000000], tokens).measure_progress_ring()


def expand_page(page, facts, canvas, tokens=None):
    """Return a new page; expansion never mutates its authoring source."""
    def expand(items):
        output = []
        if not isinstance(items, list):
            raise TemplateInputError("elements and children must be arrays")
        for item in items:
            if not isinstance(item, dict):
                raise TemplateInputError("scene elements must be objects")
            if item.get("type") == "component":
                if item.get("component") == "topology":
                    from presentation_topology import lower_topology
                    lowered = lower_topology(item, facts, canvas, tokens)
                    output.append({**lowered, "children": expand(lowered.get("children", []))})
                else:
                    output.append(Composition(item, facts, canvas, tokens).render())
            elif item.get("type") == "group":
                output.append({**copy.deepcopy(item), "children": expand(item.get("children", []))})
            else:
                output.append(copy.deepcopy(item))
        return output
    return {**copy.deepcopy(page), "elements": expand(page.get("elements", []))}
