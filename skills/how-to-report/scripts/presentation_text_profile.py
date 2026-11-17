"""Discover and demonstrate the existing global report typography contract."""
from __future__ import annotations

import copy
import json
import math
from xml.etree import ElementTree as ET

from presentation_library import profile_identity, profile_path
from presentation_typography import STYLE_FIELDS, typography_catalog
from report_ppt import TemplateInputError, load_template


def _profile(identifier):
    if not isinstance(identifier, str):
        raise TemplateInputError("text profile ID must be a registered string")
    key = identifier.removeprefix("profile.")
    return key, profile_path(key)


def validate_profile_text_floor(document, page, svg, geometry_policy):
    """Enforce report-14pt's 9pt floor on fresh computed text before publication.

    Template source geometry may contain preserved source text; only its marked
    generated text carriers are checked. Native replay never uses this entry.
    """
    declaration = document.get("brief", {}).get("design_profile", {})
    if geometry_policy != "computed" or not isinstance(declaration, dict) or declaration.get("id") != "report-14pt":
        return
    source_template = page.get("kind") == "template"

    def check_size(size, identifier):
        # Generated SVG/font JSON uses unitless px; rendering already validates
        # unsupported units. Keep a direct finite check for meaningful errors.
        try:
            pixels = float(size)
        except (TypeError, ValueError) as exc:
            raise TemplateInputError(f"{page['id']}/{identifier}: cannot verify generated text font size") from exc
        if not math.isfinite(pixels) or pixels * .75 < 9 - 1e-6:
            error = TemplateInputError(f"{page['id']}/{identifier}: computed report-14pt text is {pixels*.75:g}pt; minimum is 9pt")
            error.diagnostic = {"code": "typography_minimum_font", "page_id": page["id"], "object_id": identifier,
                                "effective_pt": pixels * .75, "minimum_pt": 9,
                                "reason": "Use a supported role or provide more space; do not shrink below 9pt."}
            raise error

    def check_chart(value, path):
        if isinstance(value, dict):
            for key, child in value.items():
                if key in {"font_size", "axis_font_size", "legend_font_size"}:
                    check_size(child, path + "." + key)
                else:
                    check_chart(child, path + "." + key)
        elif isinstance(value, list):
            for index, child in enumerate(value):
                check_chart(child, f"{path}[{index}]")

    def visit(node, inherited_size=None, identifier=None, generated=False, in_chart=False):
        identifier = node.get("id", identifier or "generated-text")
        generated = generated or bool(node.get("data-htr-text-role"))
        size = node.get("font-size", inherited_size)
        kind = node.tag.rsplit("}", 1)[-1]
        in_chart = in_chart or node.get("data-pptx-replace-with") == "chart"
        if kind in {"text", "tspan"} and (not source_template or generated) and "".join(node.itertext()).strip():
            if size is None:
                raise TemplateInputError(f"{page['id']}/{identifier}: generated text has no verifiable font size")
            check_size(size, identifier)
        if kind == "metadata" and in_chart and not source_template and node.text:
            check_chart(json.loads(node.text), identifier + ".chart")
        for child in node:
            visit(child, size, identifier, generated, in_chart)

    visit(ET.fromstring(svg))


def describe_text_profile(identifier="report-14pt"):
    """Resolve actual shared styles; pt values are derived from SVG px, not copied."""
    key, path = _profile(identifier)
    _, _, tokens = load_template(tokens=path)
    catalog = typography_catalog(tokens)
    roles = {}
    for role, style in catalog["roles"].items():
        color_role = style["color"]
        slot = tokens["color"]["roles"].get(color_role, color_role)
        color = tokens["theme"]["slots"].get(slot, color_role)
        roles[role] = {
            "font_family": style["font_family"], "font_size_px": style["font_size"],
            "font_size_pt": style["font_size"] * .75, "weight": style["weight"],
            "line_height_multiplier": style["line_height"],
            "line_height_px": style["font_size"] * style["line_height"],
            "line_height_pt": style["font_size"] * style["line_height"] * .75,
            "paragraph_gap_px": style["paragraph_gap"], "paragraph_gap_pt": style["paragraph_gap"] * .75,
            "insets_px": style["insets"], "insets_pt": [v * .75 for v in style["insets"]],
            "align": style["align"], "vertical_anchor": style["vertical_anchor"],
            "color_role": color_role, "color_hex": color,
        }
    identity = profile_identity(key)
    return {
        "id": "profile." + key, "profile_id": key, "kind": "profile", "label": "全局文字规范 · 正文14pt",
        "identity": identity, "roles": roles, "tokens": tokens, "contract": catalog,
        "global_binding": {"field": "brief.design_profile", "value": identity,
                           "scope": "whole computed author project", "palette_field": "brief.palette_id"},
        "font_policy": {
            "declared_families": copy.deepcopy(tokens["font"]["families"]),
            "effective_script_mapping": "每个文字角色解析一个font_family；该字体用于Latin、East Asian及Complex Script。当前profile均为Microsoft YaHei。",
            "fallback": "latin/fallback为现有tokens声明；当前角色渲染未实现独立的中西文或逐字字体回退链。字体缺失时由本机环境替代，须在目标PowerPoint检查。",
            "embedding": "不自动嵌入字体。SVG预览、测量及PowerPoint的字体环境可能不同。",
            "weight_mapping": catalog["native_weights"],
        },
        "supported_fields": sorted(STYLE_FIELDS),
        "rich_text": {
            "run_fields": ["text", "weight", "color"],
            "supported": ["同一文本内普通/加粗及局部语义色", "显式换行分段与自动折行", "同一文本框统一字体、字号及行距",
                          "左/中/右对齐与上/中/下垂直定位", "文本框四边内距", "paragraph-flow按角色组合独立段落"],
            "unsupported": ["独立段前和段后参数；当前仅paragraph_gap作用于后续段前", "逐run字号或字体", "斜体、下划线、删除线",
                            "上下标、富文本超链接", "原生项目符号/编号、首行或悬挂缩进", "两端对齐、分栏及竖排", "自动读取Markdown/HTML作为富文本"],
            "paragraph_semantics": "单一文本中的换行产生逻辑段，自动折行不额外增加段距；paragraph_gap不加在首段前或末段后。paragraph-flow的gap作用于独立子段之间，其内部换行保持原行距。",
            "validation": "未支持的run/style字段由正常构建明确拒绝；不静默忽略。",
        },
        "standards": {"body_pt": roles["body"]["font_size_pt"], "minimum_role_pt": min(v["font_size_pt"] for v in roles.values()),
                      "minimum_computed_pt": 9,
                      "minimum_scope": "computed + brief.design_profile=report-14pt: generated text, components, charts and marked template text; excludes preserved source geometry, images, legacy-replay and unbound compatibility builds",
                      "body_color": roles["body"]["color_hex"], "annotation_color": roles["caption"]["color_hex"],
                      "units": "SVG px; native pt = px × 0.75; 1px = 9525EMU"},
        "precedence": catalog["precedence"],
        "limitations": ["这是已有report-14pt规范的查询与取用，不新增任意可调字体主题。",
                        "绑定report-14pt的新computed文字不能通过局部覆盖降到9pt以下；该闸门不追溯原生源保真、图片内部字或legacy-replay。",
                        "role颜色由全局palette解析；关键数据用text，不使用低对比度注释灰。",
                        "原生源资产保真取用保留原字体和段落；该profile不自动重排或重格式化原件。"],
    }


def text_profile_story(identifier="report-14pt"):
    """Three editable computed pages, including real rich text and paragraph gaps."""
    description = describe_text_profile(identifier)

    def text(identifier, value, role="body", *, style=None, **constraints):
        element = {"type": "text", "role": role}
        element.update({"runs": value} if isinstance(value, list) else {"text": value})
        if style:
            element["style"] = style
        return {"id": identifier, "type": "leaf", "element": element, **constraints}

    def column(identifier, children, **constraints):
        return {"id": identifier, "type": "column", "gap": 8, "children": children, **constraints}

    def page(identifier, title, content, note):
        return {"id": identifier, "kind": "layout", "layout_version": "0.1", "intent": "demo", "job": title,
                "layout": column(identifier + "-root", [text(identifier + "-title", title, "title"), content,
                    text(identifier + "-note", note, "caption")], padding=40, gap=20)}

    cards = []
    for role, style in description["roles"].items():
        sample = "数据 9,876" if role in {"hero", "metric", "metricCompact"} else "清晰表达 Report"
        cards.append(column("type-" + role, [
            text("label-" + role, f"{role} · {style['font_size_pt']:g}pt / {style['weight']}", "caption"),
            text("sample-" + role, sample, role),
        ], padding=10, gap=6, surface={"fill": "surfaceMuted"}))
    role_grid = {"id": "type-grid", "type": "grid", "columns": [{"fr": 1}] * 3, "gap": 12, "children": cards}
    roles_page = page("type-roles", "文字角色 · 字号与字重从统一规范解析", role_grid,
                      "字号从profile实时计算：正文14pt，最小9pt。示例中没有业务结论。")

    paragraphs = "第一段：页面先表达读者需要理解的结论，再呈现支持判断的数字与范围。自动折行只使用行距。\n第二段：明确换行形成下一逻辑段。段间距由paragraph_gap统一计算，不靠空格或额外空白行。"
    paragraph_grid = {"id": "paragraph-grid", "type": "grid", "columns": [{"fr": 1}, {"fr": 1}], "gap": 24,
        "children": [column("paragraph-default", [text("paragraph-default-title", "统一正文 · 默认段距0", "heading"),
            text("paragraph-default-copy", paragraphs), text("paragraph-default-caption", "14pt × 1.3 = 18.2pt行距", "caption")],
            padding=20, surface={"fill": "surfaceMuted"}),
        column("paragraph-spaced", [text("paragraph-spaced-title", "段距示例 · 后续段前9pt", "heading"),
            text("paragraph-spaced-copy", paragraphs, style={"paragraph_gap": 12}),
            text("paragraph-spaced-caption", "局部示例覆盖paragraph_gap=12px；默认profile仍为0", "caption")],
            padding=20, surface={"fill": "surfaceMuted"})]}
    rich = column("rich-example", [text("rich-title", "局部富文本 · 同字号内的字重与颜色", "heading"),
        text("rich-copy", [{"text": "合成示例："}, {"text": "本周完成率", "weight": 700}, {"text": "达到"},
                           {"text": "82%", "weight": 700, "color": "secondary"}, {"text": "，较参考值增加12个百分点。"}]),
        text("rich-limit", "仅支持text / weight / color；斜体、下划线、上下标和逐run字号尚不支持。", "dataCaption")],
        padding=20, surface={"fill": "surfaceMuted"})
    paragraph_page = page("type-paragraphs", "行距、段距与富文本 · 使用已实现的属性", column("paragraph-content", [paragraph_grid, rich], gap=24),
                          "段距与内距均由engine测量并生成；独立段前/段后控制尚不支持。")

    alignments = []
    for align, anchor, label in [("left", "top", "左对齐 / 顶部"), ("center", "middle", "居中 / 中部"), ("right", "bottom", "右对齐 / 底部")]:
        alignments.append(column("align-" + align, [text("align-title-" + align, label, "heading"),
            text("align-copy-" + align, "正文14pt\n内距12pt", style={"align": align, "vertical_anchor": anchor,
                 "insets": [16, 16, 16, 16]}, height=180)], padding=12, surface={"fill": "surfaceMuted", "stroke": "border"}))
    alignment_grid = {"id": "alignment-grid", "type": "grid", "columns": [{"fr": 1}] * 3, "gap": 20, "children": alignments}
    font_block = column("font-policy", [text("font-policy-title", "中西文与回退 · 当前真实边界", "heading"),
        text("font-policy-copy", "中文说明、Latin Report、123,456、标点：Aa（示例）\n当前所有文字角色统一Microsoft YaHei；未实现独立中西文或逐字回退链。"),
        text("font-policy-note", "不自动嵌入字体；缺失字体由目标环境替代。原生源保真资产保留原字体，不随profile自动改写。", "dataCaption")],
        padding=20, surface={"fill": "surfaceMuted"})
    alignment_page = page("type-alignment", "对齐、内边距与字体 · 同一全局profile", column("alignment-content", [alignment_grid, font_block], gap=24),
                          "此页用于规范展示与导出核验；不代表对所有字体环境自动验收。")
    return {"schema_version": "0.1", "project_id": "text-profile-story", "revision": 1,
            "brief": {"audience": "使用PPT组件库的作者", "purpose": "展示真实全局文字规范及支持边界",
                      "design_profile": description["identity"]}, "sources": [], "facts": {},
            "pages": [roles_page, paragraph_page, alignment_page]}
