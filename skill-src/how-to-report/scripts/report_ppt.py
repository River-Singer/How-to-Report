#!/usr/bin/env python3
"""Compile typed user-template parameters into editable, structured SVG slides."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
import re
import shutil
import sys
from xml.etree import ElementTree as ET

SCRIPT_ROOT = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_ROOT.parent
DEFAULT_TEMPLATE = SKILL_ROOT / "assets" / "templates" / "business-blue-v1"
ENGINE_SCRIPTS = SKILL_ROOT / "runtime" / "ppt-engine" / "scripts"
SVG_NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG_NS)


class TemplateInputError(ValueError):
    """A parameter, token or measured text frame is invalid."""


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")).hexdigest()


def external_target(path):
    # The shared helper is materialized alongside this script in installed Skills.
    shared = SKILL_ROOT.parent / "shared" / "scripts"
    if shared.is_dir() and str(shared) not in sys.path:
        sys.path.insert(0, str(shared))
    from write_boundary import require_external_write
    return require_external_write(path)


def load_template(root=DEFAULT_TEMPLATE, tokens=None):
    root = Path(root).resolve()
    catalog = read_json(root / "templates" / "page-catalog.json")
    values = read_json(tokens or root / "templates" / "tokens.json")
    validate_schema(values, read_json(root / "templates" / "tokens.schema.json"), "tokens")
    width, height = values["canvas"]["width"], values["canvas"]["height"]
    for name, frame in (("header", values["header"]["frame"]), ("title", values["header"]["titleFrame"]), ("body", values["body"]["frame"]), ("footer", values["footer"]["frame"]), ("footer text", values["footer"]["textFrame"])):
        x, y, w, h = frame
        if min(x, y) < 0 or min(w, h) <= 0 or x + w > width or y + h > height:
            raise TemplateInputError(f"tokens.{name}: frame must lie inside the canvas")
    header, body, footer = values["header"]["frame"], values["body"]["frame"], values["footer"]["frame"]
    if header[1] + header[3] > body[1] or body[1] + body[3] > footer[1]:
        raise TemplateInputError("tokens: header, body and footer regions overlap")
    return root, catalog, values


def validate_schema(value, schema, label="input"):
    try:
        from jsonschema import Draft202012Validator
    except ImportError as exc:
        raise TemplateInputError("Install jsonschema from the PPT runtime requirements") from exc
    errors = sorted(Draft202012Validator(schema).iter_errors(value), key=lambda error: str(list(error.absolute_path)))
    if errors:
        error = errors[0]
        path = ".".join(str(part) for part in error.absolute_path)
        raise TemplateInputError(f"{label}{'.' if path else ''}{path}: {error.message}")
    _check_semantic_values(value, schema, label)


def _check_semantic_values(value, schema, path):
    if isinstance(value, float) and not math.isfinite(value):
        raise TemplateInputError(f"{path}: number must be finite")
    if isinstance(value, str):
        _normalized_text(value, path)
        if schema.get("minLength", 0) > 0 and not value.strip():
            raise TemplateInputError(f"{path}: required text must contain visible characters")
    if isinstance(value, dict):
        for key, child in value.items():
            _check_semantic_values(child, schema.get("properties", {}).get(key, {}), f"{path}.{key}")
    if isinstance(value, list):
        for index, child in enumerate(value):
            _check_semantic_values(child, schema.get("items", {}), f"{path}.{index}")


def _normalize_values(value):
    if isinstance(value, str):
        return value.replace("\r\n", "\n").replace("\r", "\n")
    if isinstance(value, list):
        return [_normalize_values(child) for child in value]
    if isinstance(value, dict):
        return {key: _normalize_values(child) for key, child in value.items()}
    return value


def _field_schema(schema, field):
    for part in field.split("."):
        schema = schema.get("items", {}) if part.isdigit() else schema.get("properties", {}).get(part, {})
    return schema


def _normalized_text(text, path):
    if not isinstance(text, str):
        raise TemplateInputError(f"{path}: expected text")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    if any(0xD800 <= ord(char) <= 0xDFFF for char in text):
        raise TemplateInputError(f"{path}: invalid Unicode surrogate")
    if any(ord(char) < 32 and char not in "\n\t" or ord(char) in {0xFFFE, 0xFFFF} for char in text):
        raise TemplateInputError(f"{path}: character is invalid in XML text")
    return text


def validate_chart_content(content, prefix):
    categories = content["categories"]
    for series_index, series in enumerate(content["series"]):
        if len(series["values"]) != len(categories):
            raise TemplateInputError(f"{prefix}.series.{series_index}.values: align with categories")
        if not any(value is not None for value in series["values"]):
            raise TemplateInputError(f"{prefix}.series.{series_index}.values: provide at least one known numeric value")


def validate_document(document, catalog, root):
    document = _normalize_values(document)
    validate_schema(document, read_json(root / "templates" / "pages.schema.json"))
    page_ids = set()
    result = copy.deepcopy(document)
    for index, page in enumerate(result["pages"]):
        prefix = f"pages.{index}"
        if page["id"] in page_ids:
            raise TemplateInputError(f"{prefix}.id: duplicate page id")
        page_ids.add(page["id"])
        family = catalog["families"][page["family"]]
        variant_id = page.get("variant")
        if variant_id is None:
            items = page["content"].get(family.get("array_key"), [])
            item_count = len(items) if isinstance(items, list) else 0
            variant_id = family.get("auto_variant_by_items", {}).get(str(item_count), family["default_variant"])
        variant = family["variants"].get(variant_id)
        if variant is None:
            raise TemplateInputError(f"{prefix}.variant: choose {list(family['variants'])}")
        page["variant"] = variant["id"]
        allowed_config = family["config_fields"]
        unknown_config = set(page.get("config", {})) - set(allowed_config)
        if unknown_config:
            raise TemplateInputError(f"{prefix}.config: fields do not apply to {page['family']}: {sorted(unknown_config)}")
        page["config"] = {**{key: catalog["config_defaults"][key] for key in allowed_config}, **page.get("config", {})}
        validate_schema(page["content"], family["content_schema"], prefix + ".content")
        if variant.get("renderer") == "source-diagram":
            from report_ppt_source import validate_nodes
            validate_nodes(page["content"], variant, validate_schema, validate_chart_content, prefix + ".content", catalog)
        content = page["content"]
        array_key = family.get("array_key")
        if array_key and "icon_key" in family["content_schema"]["properties"][array_key].get("items", {}).get("properties", {}):
            registry = read_json(root / "icons" / "catalog.json")
            for item_index, item in enumerate(content.get(array_key, [])):
                key = item.get("icon_key", "")
                if key and key not in registry:
                    raise TemplateInputError(f"{prefix}.content.{array_key}.{item_index}.icon_key: unknown user icon_key {key!r}; choose a key from icons/catalog.json")
        if array_key and len(content.get(array_key, [])) > variant["capacity"]:
            raise TemplateInputError(f"{prefix}.content.{array_key}: capacity {variant['capacity']} for {page['variant']}")
        if array_key and len(content.get(array_key, [])) < variant.get("min_items", 0):
            raise TemplateInputError(f"{prefix}.content.{array_key}: provide {variant['min_items']} items for {page['variant']}, or omit variant to select by item count")
        for item_index, item in enumerate(content.get(array_key, [])):
            for field, maximum in variant.get("item_text_limits", {}).items():
                if len(item.get(field, "")) > maximum:
                    raise TemplateInputError(f"{prefix}.content.{array_key}.{item_index}.{field}: {len(item[field])} characters exceeds {maximum} for {page['variant']}; shorten this field or use a lower-density variant")
        if page["family"] == "chart":
            validate_chart_content(content, prefix + ".content")
        if page["family"] == "matrix":
            if len(content["cells"]) != len(content["rows"]) or any(len(row) != len(content["columns"]) for row in content["cells"]):
                raise TemplateInputError(f"{prefix}.content.cells: align with row and column headers")
        if page["family"] == "image" and len(content.get("images", [])) > variant["capacity"]:
            raise TemplateInputError(f"{prefix}.content.images: capacity {variant['capacity']} for {page['variant']}; choose a compatible image variant")
        if page["family"] == "gantt":
            from datetime import date
            try:
                start, end = date.fromisoformat(content["start"]), date.fromisoformat(content["end"])
                if start >= end:
                    raise ValueError("start must precede end")
                for task in content["tasks"]:
                    task_start, task_end = date.fromisoformat(task["start"]), date.fromisoformat(task["end"])
                    if not start <= task_start <= task_end <= end:
                        raise ValueError("task dates must lie inside period")
            except ValueError as exc:
                raise TemplateInputError(f"{prefix}.content: {exc}") from exc
    return result


class Canvas:
    """A complete slide with a common Master and measured parameter bindings."""

    def __init__(self, page, family, variant, tokens, template_root, page_number, asset_root=None):
        self.page, self.family, self.variant = page, family, variant
        self.tokens, self.template_root = tokens, template_root
        self.asset_root = Path(asset_root).resolve() if asset_root else None
        self.bindings, self.assets = [], {}
        self.body = tokens["body"]["frame"]
        self.root = ET.Element(f"{{{SVG_NS}}}svg", {
            "width": str(tokens["canvas"]["width"]), "height": str(tokens["canvas"]["height"]),
            "viewBox": f"0 0 {tokens['canvas']['width']} {tokens['canvas']['height']}",
            "data-pptx-master": "business-blue-white", "data-pptx-master-name": "Business Blue White",
            "data-pptx-layout": variant["layout_key"], "data-pptx-layout-name": variant["layout_key"],
        })
        self.fixed, self.dynamic, self.slots = [], [], []
        background = self.rect([0, 0, tokens["canvas"]["width"], tokens["canvas"]["height"]], "surface", layer="master", identifier="canvas-background")
        background.set("fill", tokens["canvas"]["background"])
        title_frame = tokens["header"]["titleFrame"]
        margin, right = title_frame[0], title_frame[0] + title_frame[2]
        self.line(margin, tokens["header"]["ruleY"], right, tokens["header"]["ruleY"], layer="master", identifier="header-rule")
        self.line(margin, tokens["footer"]["ruleY"], right, tokens["footer"]["ruleY"], layer="master", identifier="footer-rule", color="border", width_role="hairline")
        self.text("title", page["content"]["title"], tokens["header"]["titleFrame"], "title", 2, 32, True)
        footer_frame = tokens["footer"]["textFrame"]
        x, y, width, height = footer_frame
        config = page["config"]
        self.text("section_name", page["content"].get("section_name", ""), [x, y, width * .26, height], "caption", 0, 24)
        source = page["content"].get("source", "") if config["show_source"] else ""
        self.text("source", source, [x + width * .28, y, width * .62, height], "caption", 0, 64)
        number = str(page_number) if config["show_page_number"] else ""
        self.text("page_number", number, [x + width * .92, y, width * .08, height], "caption", 0, 12, derived="page order + config.show_page_number")

    def color(self, role):
        slot = self.tokens["color"]["roles"][role]
        return self.tokens["theme"]["slots"][slot]

    def rect(self, frame, color="surfaceMuted", layer="layout", identifier=None):
        x, y, width, height = frame
        attrs = {"x": x, "y": y, "width": width, "height": height, "fill": self.color(color)}
        if layer == "layout":
            attrs["rx"] = self.tokens["shape"]["cardRadius"]
        return self.element("rect", attrs, layer, identifier)

    def element(self, tag, attrs, layer=None, identifier=None):
        attrs = {key: str(value) for key, value in attrs.items()}
        attrs["id"] = identifier or (f"atom-{len(self.fixed)}" if layer else f"data-{len(self.dynamic)}")
        if layer:
            attrs["data-pptx-layer"] = layer
        element = ET.Element(f"{{{SVG_NS}}}{tag}", attrs)
        (self.fixed if layer else self.dynamic).append(element)
        return element

    def line(self, x1, y1, x2, y2, layer="layout", identifier=None, color="primary", width_role="divider"):
        return self.element("line", {"x1": x1, "y1": y1, "x2": x2, "y2": y2, "stroke": self.color(color), "stroke-width": self.tokens["line"][width_role]}, layer, identifier)

    def text(self, field, value, frame, role="body", minimum=0, maximum=100, required=False, derived=None, color_role=None, max_lines=None):
        path = f"{self.page['id']}.content.{field}"
        value = _normalized_text(value, path)
        field_schema = _field_schema(self.family["content_schema"], field)
        minimum = max(minimum, field_schema.get("minLength", 0))
        maximum = min(maximum, field_schema.get("maxLength", maximum))
        active = bool(value) or required
        if active and (not minimum <= len(value) <= maximum or required and not value.strip()):
            raise TemplateInputError(f"{path}: {len(value)} characters, allowed {minimum}..{maximum}; variant {self.variant['id']}")
        if str(ENGINE_SCRIPTS) not in sys.path:
            sys.path.insert(0, str(ENGINE_SCRIPTS))
        from text_measure import wrap_text
        size = self.tokens["font"]["sizes"][role]
        font = self.tokens["font"]["families"]["title" if role in {"title", "heading", "metric", "chapter"} else "body"]
        font_family = f"{self.tokens['font']['families']['latin']}, {font}, {self.tokens['font']['families']['fallback']}"
        weight = str(self.tokens["font"]["weights"][role])
        x, y, width, height = frame
        leading = self.tokens["font"]["lineHeight"].get(role, 1.3)
        lines, widths, oversized = [], [], []
        for paragraph in value.split("\n"):
            paragraph_lines, paragraph_widths, paragraph_oversized = wrap_text(paragraph, size=size, max_width=width, family=font_family, weight=weight)
            lines.extend(paragraph_lines)
            widths.extend(paragraph_widths)
            oversized.extend(paragraph_oversized)
        measured_height = size * self.variant.get("text_height_factor", 1) + (len(lines) - 1) * size * leading
        if value and max_lines is not None and len(lines) > max_lines:
            raise TemplateInputError(f"{path}: measured {len(lines)} lines, allowed {max_lines}; fit this field within {width:.1f}px at {size}px or shorten it")
        if value and (oversized or measured_height > height + .01):
            raise TemplateInputError(f"{path}: measured {max(widths, default=0):.1f}×{measured_height:.1f}px exceeds {width:.1f}×{height:.1f}px; choose a compatible variant or revise this field")
        if field not in {"title", "section_name", "source", "page_number"}:
            bx, by, bw, bh = self.body
            if x < bx - .01 or y < by - .01 or x + width > bx + bw + .01 or y + height > by + bh + .01:
                raise TemplateInputError(f"{path}: text frame lies outside the global body region")
        identifier = "text-" + re.sub(r"[^a-zA-Z0-9_-]", "-", field)
        group = ET.Element(f"{{{SVG_NS}}}g", {"id": "slot-" + identifier, "data-pptx-placeholder": "title" if field == "title" else "body", "data-pptx-idx": str(len(self.slots)), "data-pptx-bounds": " ".join(f"{n:g}" for n in frame)})
        node = ET.SubElement(group, f"{{{SVG_NS}}}text", {
            "id": identifier,
            "data-pptx-carrier": "true",
            "x": str(x),
            "y": str(y + size * .88),
            "font-family": font_family,
            "font-size": str(size),
            "font-weight": weight,
            "fill": self.color(color_role or ("primary" if role in {"title", "heading", "metric", "chapter"} else "text")),
        })
        for index, line in enumerate(lines):
            span = ET.SubElement(node, f"{{{SVG_NS}}}tspan", {"x": str(x), "y": str(y + size * .88 + index * size * leading)})
            span.text = line
        self.slots.append(group)
        self.bindings.append({"selector": identifier, "field": field, "derived_from": derived, "required": required or minimum > 0, "active": active, "inactive_when": "optional field hidden or capacity slot has no corresponding input item", "min_length": minimum, "max_length": maximum, "counting": "Unicode code points after CRLF normalization; whitespace and punctuation count", "font_role": role, "frame": frame, "text": value, "measured_width": max(widths, default=0), "measured_height": measured_height})
        if max_lines is not None:
            self.bindings[-1]["max_lines"] = max_lines
        return group

    def item(self, index):
        key = self.family.get("array_key")
        values = self.page["content"].get(key, []) if key else []
        return values[index] if index < len(values) else {}

    def finish(self):
        for node in self.fixed + self.slots + self.dynamic:
            self.root.append(node)
        texts = self.root.findall(f".//{{{SVG_NS}}}text")
        selectors = {binding["selector"] for binding in self.bindings}
        if any(text.get("id") not in selectors for text in texts):
            raise TemplateInputError("editable text has no parameter binding")
        ET.indent(self.root, space="  ")
        return ET.tostring(self.root, encoding="unicode") + "\n"


def render_page(page, catalog, tokens, template_root, number=1, asset_root=None):
    from report_ppt_layouts import render
    family = catalog["families"][page["family"]]
    variant = family["variants"][page["variant"]]
    canvas = Canvas(page, family, variant, tokens, template_root, number, asset_root)
    render(canvas)
    return canvas.finish(), canvas.bindings, canvas.assets


def build_project(document, output, template_root=DEFAULT_TEMPLATE, tokens=None, asset_root=None):
    root, catalog, values = load_template(template_root, tokens)
    document = validate_document(document, catalog, root)
    output = external_target(output)
    if output.exists():
        raise TemplateInputError(f"output already exists: {output}")
    # Render and validate everything before creating the output directory.
    rendered = []
    for number, page in enumerate(document["pages"], 1):
        rendered.append((page, *render_page(page, catalog, values, root, number, asset_root)))
    output.mkdir(parents=True)
    svg_dir = output / "svg_output"
    svg_dir.mkdir()
    notes_dir = output / "notes"
    notes_dir.mkdir()
    receipts = []
    prefix_width = max(2, len(str(len(rendered))))
    for index, (page, svg, bindings, assets) in enumerate(rendered, 1):
        stem = f"{index:0{prefix_width}d}_{page['id']}"
        (svg_dir / f"{stem}.svg").write_text(svg, encoding="utf-8")
        (notes_dir / f"{stem}.md").write_text(page.get("notes", ""), encoding="utf-8")
        for relative, data in assets.items():
            target = output / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        receipts.append({"id": page["id"], "family": page["family"], "variant": page["variant"], "svg": f"svg_output/{stem}.svg", "svg_sha256": hashlib.sha256(svg.encode()).hexdigest(), "text_bindings": bindings})
    write_json(output / "tokens.json", values)
    write_json(output / "parameters.json", document)
    receipt = {"template_id": catalog["template_id"], "revision": catalog["revision"], "tokens_sha256": fingerprint(values), "catalog_sha256": fingerprint(catalog), "input_sha256": fingerprint(document), "pages": receipts}
    write_json(output / "parameter-receipt.json", receipt)
    return receipt


def refresh(template_root=DEFAULT_TEMPLATE):
    """Regenerate derived prototypes and AI manuals from the canonical catalog."""
    root, catalog, tokens = load_template(template_root)
    pages_schema = read_json(root / "templates" / "pages.schema.json")
    prototype_dir = root / "templates" / "prototypes"
    prototype_dir.mkdir(exist_ok=True)
    docs = root / "docs" / "families"
    docs.mkdir(parents=True, exist_ok=True)
    all_bindings = {}
    index = ["# 自有参数模板使用说明", "", "画布为纯白16∶9，全部页型共用标题、页眉、页脚及正文区。", "", "在安装包根目录使用下列命令，输入与生成项目保存在安装包外。", "", "```text", "python scripts/report_ppt.py catalog", "python scripts/report_ppt.py describe kpi", "python scripts/report_ppt.py validate --input <参数JSON>", "python scripts/report_ppt.py build --input <参数JSON> --output <新项目目录> --assets <图片资源根>", "python scripts/report_ppt.py copy-template --output <私有模板根>", "```", "", "通过ppt_runtime.py的check/export/inspect检查、导出与回读项目，完整命令见包内references/ppt-production.md。模板根通过report_ppt.py的全局--template参数指定，修改私有tokens后执行refresh重生成原型与使用说明。", "", "输入顶层包含schema_version=1、template_id=business-blue-v1和pages数组。每页包含id、family、variant、content及可选config/notes。content_source可保存当前材料身份。每家族content schema和config默认值见下列说明。", "", "字符按CRLF规范化后的Unicode码点计数，空格、标点和换行计入。每项长度检查后继续做字体与框体测量。数组空余槽及关闭的可选槽保留空carrier，有对应输入项时执行字段min/max。数值和页码通过明确派生规则生成显示文字。", "", "原型使用语义标记及技术轴线占位，业务生成应传入实际内容。原始材料没有相应关系或数据时，记录具体缺口并选择资料能够支持的页型。", ""]
    index.extend(["制作前先读安装包references/ppt-production.md的图表选择与图片用途，现场主画面优先清晰图形，精确查值或交叉定位需要时使用简洁表格。图片焦点与完整显示/裁剪配置见image说明。", ""])
    for family_id, family in catalog["families"].items():
        lines = [f"# {family['label']}", "", family["purpose"], "", f"类型为{family['type']}，语义入口为`{family['capability_id']}`。", "", "## 使用场景", "", family["scenarios"], "", f"关系要求为{family['relations']}。缺少必要输入时说明具体字段与来源缺口，再选择资料能支持的表达。", "", "## 输入与参数", "", "content按以下schema提供，所有可见文字均为输入或明确派生显示。数组空余槽及隐藏可选槽允许空carrier，对应输入项存在时执行字段min/max。", "", "```json", json.dumps(family["content_schema"], ensure_ascii=False, indent=2), "```", "", "## 变体与容量", ""]
        for note in family.get("usage_notes", []):
            lines.extend([note, ""])
        icon_array = family.get("array_key")
        if icon_array and "icon_key" in family["content_schema"]["properties"][icon_array].get("items", {}).get("properties", {}):
            lines.extend(["图标来自用户PPT图标.pptx的首批24项，键与来源见icons/catalog.json。所有本家族variant均消费`content." + icon_array + "[].icon_key`。例如填入`team`并保持`config.show_icons=true`。空键或关闭开关隐藏图标，未知键在validate阶段报错。", "", "图标以primary色等比适配独立预留区，开关使用相同Layout与文字框。并列卡及线性流程使用卡片底部内边距，循环与环绕节点使用左侧栏，战略屋使用支柱底带，架构层使用标题与说明间隙，图片页使用说明标题上方空白。正文容量继续按原文字框实际测量。", ""])
        for variant_id, variant in family["variants"].items():
            page = {"id": "prototype", "family": family_id, "variant": variant_id, "content": copy.deepcopy(family["prototype_content"]), "config": {key: catalog["config_defaults"][key] for key in family["config_fields"]}}
            page["content"].update(copy.deepcopy(variant.get("prototype_content", {})))
            array_key = family.get("array_key")
            if array_key:
                page["content"][array_key] = page["content"][array_key][:variant["capacity"]]
            svg, bindings, _ = render_page(page, catalog, tokens, root)
            name = variant["prototype"]
            (prototype_dir / name).write_text(svg, encoding="utf-8")
            all_bindings[f"{family_id}/{variant_id}"] = bindings
            lines.extend([f"### {variant_id}", "", variant["description"], "", f"Layout为`{variant['layout_key']}`，原型为`templates/prototypes/{name}`。", "", "| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |", "|---|---:|---:|---|---|"])
            for binding in bindings:
                lines.append(f"| {binding['field']} | {binding['min_length']} | {binding['max_length']} | {binding['font_role']} | {binding['frame']} |")
        config_properties = pages_schema["properties"]["pages"]["items"]["properties"]["config"]["properties"]
        config_contract = {key: {**config_properties[key], "default": catalog["config_defaults"][key]} for key in family["config_fields"]}
        lines.extend([
            "", "## 使用步骤", "",
            f"1. 先确认材料确有本页型所表达的关系，选择`family={family_id}`及兼容variant。",
            "2. 提供完整content，按schema控制config。可选内容可留空，正文含义由实际汇报任务确定。",
            "3. 执行validate和build，处理具体字段的长度、容量或字体测量错误。",
            "4. 对生成项目执行check、export、inspect，并查看最终页面和所需编辑操作。",
            "", "## 配置与tokens", "", "本页型的config类型、可选值与默认值如下。", "",
            "```json", json.dumps(config_contract, ensure_ascii=False, indent=2), "```", "",
            "允许字段来自page-catalog.json与pages.schema.json。tokens控制全局几何、字阶、颜色、间距和线条。字号通过body_role选择已登记字阶。切换variant后重新校验输入容量。",
            "", "## 来源与检查", "",
            f"来源为{family['source']}。原始文件指纹及资产处理见asset-provenance.json。当前原型完成结构生成与文本测量，实际渲染和原生编辑范围以交付检查记录为准。",
            "", f"catalog指纹为`{fingerprint(catalog)}`，tokens指纹为`{fingerprint(tokens)}`，参数schema指纹为`{fingerprint(pages_schema)}`。", "",
        ])
        (docs / f"{family_id}.md").write_text("\n".join(lines), encoding="utf-8")
        index.append(f"- [{family['label']}](families/{family_id}.md) · {family['purpose']}")
    (root / "docs" / "AI-USAGE.md").write_text("\n".join(index) + "\n", encoding="utf-8")
    write_json(root / "templates" / "text-bindings.json", {"tokens_sha256": fingerprint(tokens), "catalog_sha256": fingerprint(catalog), "pages_schema_sha256": fingerprint(pages_schema), "variants": all_bindings})
    from report_ppt_source import refresh_source_docs
    refresh_source_docs(root, catalog, all_bindings)
    provenance = read_json(root / "asset-provenance.json")
    provenance["generated_assets"] = {str(path.relative_to(root)).replace("\\", "/"): hashlib.sha256(path.read_bytes()).hexdigest() for path in sorted(root.rglob("*.svg"))}
    write_json(root / "asset-provenance.json", provenance)
    return {"families": len(catalog["families"]), "variants": len(all_bindings), "tokens_sha256": fingerprint(tokens)}


def copy_template(template_root, output):
    root, _, _ = load_template(template_root)
    output = external_target(output)
    if output.exists():
        raise TemplateInputError(f"output already exists: {output}")
    files = sorted(path for path in root.rglob("*") if path.is_file())
    if any(path.is_symlink() for path in root.rglob("*")):
        raise TemplateInputError("template contains a linked path")
    manifest = {str(path.relative_to(root)).replace("\\", "/"): hashlib.sha256(path.read_bytes()).hexdigest() for path in files}
    shutil.copytree(root, output)
    write_json(output / "source-manifest.json", {"template_id": "business-blue-v1", "files": manifest})
    return {"path": str(output), "files": len(manifest), "source_manifest": "source-manifest.json"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--template", type=Path, default=DEFAULT_TEMPLATE)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("catalog")
    describe = sub.add_parser("describe")
    describe.add_argument("family")
    sub.add_parser("refresh")
    copier = sub.add_parser("copy-template")
    copier.add_argument("--output", required=True, type=Path)
    for name in ("validate", "build"):
        command = sub.add_parser(name)
        command.add_argument("--input", required=True, type=Path)
        command.add_argument("--tokens", type=Path)
        command.add_argument("--assets", type=Path)
        if name == "build":
            command.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    try:
        root, catalog, tokens = load_template(args.template, getattr(args, "tokens", None))
        if args.command == "catalog":
            result = {"template_id": catalog["template_id"], "families": {key: {"label": value["label"], "purpose": value["purpose"], "variants": value["variants"]} for key, value in catalog["families"].items()}}
        elif args.command == "describe":
            family = catalog["families"][args.family]
            properties = read_json(root / "templates" / "pages.schema.json")["properties"]["pages"]["items"]["properties"]["config"]["properties"]
            result = {**family, "config_contract": {key: {**properties[key], "default": catalog["config_defaults"][key]} for key in family["config_fields"]}}
        elif args.command == "refresh":
            external_target(root)
            result = refresh(root)
        elif args.command == "copy-template":
            result = copy_template(root, args.output)
        elif args.command == "build":
            result = build_project(read_json(args.input), args.output, root, args.tokens, args.assets or args.input.parent)
        else:
            document = validate_document(read_json(args.input), catalog, root)
            for number, page in enumerate(document["pages"], 1):
                render_page(page, catalog, tokens, root, number, args.assets or args.input.parent)
            result = {"valid": True, "pages": len(document["pages"])}
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (ValueError, KeyError, OSError) as exc:
        print(json.dumps({"valid": False, "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
