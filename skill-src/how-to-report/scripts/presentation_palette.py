"""Registered colour policies for computed author documents, not native replay."""
from __future__ import annotations

import copy
import hashlib
import json

from report_ppt import SKILL_ROOT, TemplateInputError

PALETTES = SKILL_ROOT / "assets/design-system/palettes.json"


def _rgb(color):
    return [int(color[i:i+2], 16) / 255 for i in (1, 3, 5)]


def contrast_ratio(first, second):
    def luminance(color):
        channels = [v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4 for v in _rgb(color)]
        return sum(v * w for v, w in zip(channels, (.2126, .7152, .0722)))
    a, b = sorted((luminance(first), luminance(second)))
    return (b + .05) / (a + .05)


def label_ink(background):
    """Small labels on data marks: prefer body ink, then white, then black."""
    for ink in ("#333333", "#FFFFFF", "#000000"):
        if contrast_ratio(ink, background) >= 4.5:
            return ink
    return max(("#000000", "#FFFFFF"), key=lambda ink: contrast_ratio(ink, background))


def interpolate_scale(colors, value, low, high):
    """Sample an ordered colour scale; each mark receives a solid fill."""
    t = max(0., min(1., (value - low) / (high - low))) if high > low else .5
    position = t * (len(colors) - 1)
    left = min(len(colors) - 2, int(position))
    fraction = position - left
    return "#" + "".join(f"{round((a+(b-a)*fraction)*255):02X}" for a, b in zip(_rgb(colors[left]), _rgb(colors[left+1])))


def palette_catalog():
    payload = json.loads(PALETTES.read_text(encoding="utf-8"))
    digest = hashlib.sha256(PALETTES.read_bytes()).hexdigest()
    records = []
    for raw in payload["palettes"]:
        record = copy.deepcopy(raw)
        record.update(kind="palette", executable=True, version=payload["version"], registry_sha256=digest,
                      geometry_policy="computed", native_source_recolor=False)
        record["contrast"] = {key: {"on_white": round(contrast_ratio(color, "#FFFFFF"), 3),
                                    "white_text": round(contrast_ratio(color, "#FFFFFF"), 3),
                                    "body_text": round(contrast_ratio(color, "#333333"), 3)}
                              for key, color in record["roles"].items()}
        record["limitations"] = [
            "这是本项目根据所列设计系统派生的PPT配色，不是原站官方PPT主题。",
            "正文固定80%黑，注释35%黑。注释对比度较低，只用于次要注释，不能承担关键数据。",
            "浅色强调色用于图形；文字需检查对比度。语义状态同时使用文字或标记，不只靠颜色。",
            "全局主题作用于engine语义颜色；原生保真资产、图片内部颜色及显式固定色不会自动重着色。",
        ]
        records.append(record)
    return records


def describe_palette(identifier):
    if not isinstance(identifier, str):
        raise TemplateInputError("palette_id must be a registered string ID")
    key = identifier.removeprefix("palette.")
    for record in palette_catalog():
        if record["id"] == key:
            return record
    raise TemplateInputError(f"unknown palette_id: {identifier!r}")


def apply_palette(tokens, identifier):
    """Keep typography and geometry intact; resolve registered colour roles once."""
    result = copy.deepcopy(tokens)
    if identifier is None:
        return result
    record = describe_palette(identifier)
    if record["id"] == "report-default":
        return result
    roles = record["roles"]
    slots = result["theme"]["slots"]
    slots.update(dk1=roles["body"], dk2=roles["muted"], lt1=roles["surface"], lt2=roles["surfaceMuted"],
                 accent1=roles["primary"], accent2=roles["secondary"], accent3=roles["tertiary"],
                 accent4=roles["border"], accent5=roles["accent"], accent6=roles["accentSurface"],
                 hlink=roles["secondary"])
    # Existing mappings remain valid; full semantic roles/scales are a snapshot.
    result["color"]["palette"] = {key: copy.deepcopy(record[key]) for key in
                                   ("id", "registry_sha256", "roles", "categorical", "sequential", "diverging", "provenance")}
    return result


def palette_color(tokens, value):
    """Return a registered semantic colour, or None for the legacy resolver."""
    selected = tokens.get("color", {}).get("palette", {}).get("roles", {})
    if value in selected:
        return selected[value]
    # New semantic aliases do not override any existing role or theme slot.
    if value in {"body", "muted", "accent", "positive", "negative", "neutral", "success", "warning", "danger"}:
        return describe_palette("report-default")["roles"][value]
    return None


def palette_story(identifier):
    """A real computed colour sample; Storybook can invoke it as an author request."""
    from presentation_chart_assets import chart_story
    palette = describe_palette(identifier)
    author = chart_story("chart.paired-bar", data={"categories": ["甲", "乙", "丙"],
        "series": [{"name": "本期", "values": [35, 55, 70]}, {"name": "参考", "values": [25, 45, 60]}],
        "scope": "合成示例"}, options={"title": palette["label"], "note": "同一组数据，切换全局配色"})
    author["brief"]["palette_id"] = palette["id"]
    for page in author["pages"]:
        page["intent"] = "demo"
    return author
