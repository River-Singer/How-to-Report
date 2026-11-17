"""Render parameterized user diagrams while preserving their imported geometry."""
from __future__ import annotations

import copy
import json
from xml.etree import ElementTree as ET


def render(canvas):
    variant = canvas.variant
    root = ET.parse(canvas.template_root / variant["geometry"]).getroot()
    slots = canvas.tokens["theme"]["slots"]
    for node in root.iter():
        for attribute in ("fill", "stroke", "stop-color"):
            slot = node.get("data-htr-" + attribute)
            if slot:
                node.set(attribute, slots[slot])
    transform = "matrix(" + " ".join(str(value) for value in variant["source_transform"]) + ")"
    inherited_names = {"fill", "fill-opacity", "stroke", "stroke-width", "stroke-opacity", "opacity", "stroke-linecap", "stroke-linejoin", "clip-path"}

    def append_atoms(node, inherited, transforms):
        tag = node.tag.rsplit("}", 1)[-1]
        if tag == "defs":
            canvas.fixed.append(copy.deepcopy(node))
            return
        attributes = {**inherited, **node.attrib}
        transforms = transforms + ([node.get("transform")] if node.get("transform") else [])
        if tag in {"svg", "g"}:
            inherited = {key: value for key, value in attributes.items() if key in inherited_names}
            for child in node:
                append_atoms(child, inherited, transforms)
            return
        attributes["transform"] = " ".join(transforms)
        atom = canvas.element(tag, attributes, "layout", "source-atom-" + str(len(canvas.fixed)))
        for child in node:
            atom.append(copy.deepcopy(child))

    append_atoms(root, {}, [transform])
    from report_ppt_layouts import place_local_image
    for key, slot in variant.get("image_slots", {}).items():
        item = canvas.page["content"].get("visuals", {}).get(key)
        if item:
            place_local_image(canvas, item, slot["frame"])
        else:
            x, y, width, height = slot["frame"]
            canvas.element("rect", {"x": x, "y": y, "width": width, "height": height, "fill": "none", "stroke": canvas.color("border"), "stroke-width": canvas.tokens["line"]["hairline"]}, identifier="picture-slot-" + key)
            canvas.line(x, y, x + width, y + height, layer=None, color="border")
            canvas.line(x + width, y, x, y + height, layer=None, color="border")
    from report_ppt_layouts import chart
    for key, slot in variant.get("chart_slots", {}).items():
        content = canvas.page["content"]["charts"][key]
        chart(canvas, frame=slot["frame"], content=content,
              config={"chart_type": content.get("chart_type", "line"), "show_legend": content.get("show_legend", False), "show_data_labels": content.get("show_data_labels", False)},
              field_prefix="charts." + key + ".", include_conclusions=False)
    values = canvas.page["content"]["nodes"]
    for key, field in variant["fields"].items():
        carrier = canvas.text(
            "nodes." + key, values[key], field["frame"], field["font_role"],
            field["min_length"], field["max_length"], True,
            color_role=field["color_role"],
            max_lines=field.get("max_lines"),
            style={"vertical_anchor": {"t": "top", "ctr": "middle", "b": "bottom"}[field.get("vertical_anchor", "t")],
                   "align": {"start": "left", "center": "center", "end": "right"}.get(field.get("align"), "left")},
        )
        carrier[0].set("data-htr-source-ref", field["source_ref"])
        canvas.bindings[-1]["source_ref"] = field["source_ref"]
        canvas.bindings[-1]["source_role"] = field["role"]
        canvas.bindings[-1]["source_text"] = field["source_text"]
        canvas.bindings[-1]["vertical_anchor"] = field.get("vertical_anchor", "t")
        if field.get("rotation"):
            x, y, width, height = field["frame"]
            carrier[0].set("transform", f"rotate({field['rotation']} {x + width / 2} {y + height / 2})")
            canvas.bindings[-1]["rotation"] = field["rotation"]
        if field.get("source_segment"):
            canvas.bindings[-1]["source_segment"] = field["source_segment"]
    if variant.get("title_source_ref"):
        canvas.bindings[0]["source_ref"] = variant["title_source_ref"]
        canvas.bindings[0]["source_text"] = variant.get("title_source_text")
    for source_binding in variant.get("global_metadata_bindings", []):
        binding = next(value for value in canvas.bindings if value["field"] == source_binding["field"])
        binding["source_ref"] = source_binding["source_ref"]
        binding["source_text"] = source_binding["source_text"]


def validate_nodes(content, variant, validate_schema, validate_chart_content, label, catalog):
    schema = {
        "type": "object",
        "properties": {
            key: {"type": "string", "minLength": value["min_length"], "maxLength": value["max_length"],
                  **({"pattern": value["input_pattern"]} if value.get("input_pattern") else {})}
            for key, value in variant["fields"].items()
        },
        "required": list(variant["fields"]),
        "additionalProperties": False,
    }
    validate_schema(content["nodes"], schema, label + ".nodes")
    picture_schema = {
        "type": "object", "additionalProperties": False,
        "properties": {key: {"type": "object", "required": ["path"], "additionalProperties": False,
                             "properties": {"path": {"type": "string", "minLength": 1, "maxLength": 260}, "alt": {"type": "string", "maxLength": 200}}}
                       for key in variant.get("image_slots", {})},
    }
    validate_schema(content.get("visuals", {}), picture_schema, label + ".visuals")
    chart_schema = copy.deepcopy(catalog["families"]["chart"]["content_schema"])
    for key in ("conclusions", "section_name", "source"):
        chart_schema["properties"].pop(key, None)
    chart_schema["properties"].update({"chart_type": {"enum": ["column", "line"]}, "show_legend": {"type": "boolean"}, "show_data_labels": {"type": "boolean"}})
    chart_schema["properties"]["title"].update(minLength=1, maxLength=24)
    chart_schema["required"] = ["title", "categories", "series"]
    charts_schema = {"type": "object", "properties": {key: chart_schema for key in variant.get("chart_slots", {})}, "required": list(variant.get("chart_slots", {})), "additionalProperties": False}
    validate_schema(content.get("charts", {}), charts_schema, label + ".charts")
    for key, chart_content in content.get("charts", {}).items():
        validate_chart_content(chart_content, label + ".charts." + key)


def refresh_source_docs(root, catalog, bindings):
    """Publish a discoverable original-file index and one manual per source page."""
    target = root / "docs" / "source-pages"
    target.mkdir(parents=True, exist_ok=True)
    index = ["# 新增四套源模板索引", "", "按原文件名分组，逐页保留原结构并提供参数入口。画布、标题、页眉页脚统一使用tokens。", "", "固定几何表达定性关系。数量比较、趋势与占比使用由实际数据计算几何的图表。", ""]
    collections = []
    for family_id, family in catalog["families"].items():
        if not family_id.startswith("source-"):
            continue
        group_index = ["# " + family["label"], "", family["purpose"], "", "每页独立调用，源例文作为字段来源说明保留。原型中放不下的长例文使用“说明”或“节点”占位，完整源文可从字段合同回查。", ""]
        pages = []
        for variant_id, variant in family["variants"].items():
            name = family_id.removeprefix("source-") + "-" + variant_id.removeprefix("page-")
            prototype = "../../templates/prototypes/" + variant["prototype"]
            page_bindings = bindings[family_id + "/" + variant_id]
            lines = ["# " + variant["label"], "", "来源为" + variant["source_page"] + "。", "", "## 结构与适用场景", "", variant["description"], "", variant["scenarios"], "", variant["preservation"], "", "固定节点、圆弧、扇区、分面和连接表达定性关系。数量比较、趋势或占比使用数据驱动图表，源页中已登记的微图槽可接收实际数据。", "", "## 预览", "", f"![结构预览]({prototype})", "", "## 调用", "", "将下列完整page对象放入schema_version=1、template_id=business-blue-v1的pages数组，替换各节点内容。nodes键对应原文本框或已明确拆分的语义分段，字段角色及source_ref、segment见下表。", "", "```json", json.dumps({"id": name, "family": family_id, "variant": variant_id, "content": variant["prototype_content"], "config": {"show_source": True, "show_page_number": True}}, ensure_ascii=False, indent=2), "```", "", "config支持show_source、show_page_number、image_fit与image_position。image_fit可选contain或cover，image_position为xMin/xMid/xMax与YMin/YMid/YMax组合的九个焦点，默认为xMidYMid。字体、颜色、全局区和固定字阶取自tokens，节点数与连接结构由variant确定。", "", "## 字段合同", "", "每个业务节点required=true、min=1，max按具体框体登记。字符按规范化后的Unicode码点计数，空格标点换行均计入。build会以实际字体测量宽高，字符数通过后仍可能需要调整文字。", "", "| 字段 | 节点角色与源标签 | 最短/最长 | 字阶 | 框体px | 原框引用 | 分段 | 旋转° | 垂直锚点 |", "|---|---|---|---|---|---|---|---|---|"]
            for field, contract in variant["fields"].items():
                description = contract["role"].replace("|", "&#124;").replace("\n", " / ")
                if contract.get("max_lines"):
                    description += f"，最多{contract['max_lines']}行，按实际字体宽度拒绝折行输入"
                if contract.get("input_pattern"):
                    description += "，输入格式 `" + contract["input_pattern"] + "`"
                if contract.get("source_color_resolution"):
                    description += "，" + contract["source_color_resolution"]
                lines.append(f"| nodes.{field} | {description} | {contract['min_length']}/{contract['max_length']} | {contract['font_role']} | {contract['frame']} | {contract['source_ref']} | {contract.get('source_segment') or ''} | {contract.get('rotation', 0)} | {contract.get('vertical_anchor', 't')} |")
            if variant.get("image_slots"):
                lines.extend(["", "## 可替换图片", "", "在content.visuals提供下列槽位对象，省略时显示中性空槽。每项含path和可选alt，path为--assets目录下的相对本地路径，1至260码点，alt为0至200码点。原案例照片、界面或品牌保留来源引用，默认页使用空槽。", ""])
                for key, slot in variant["image_slots"].items():
                    lines.append(f"- `visuals.{key}`用于{slot['role']}，框体为`{slot['frame']}`，源引用为`{slot['source_refs']}`。")
                lines.extend(["", "```json", json.dumps({"visuals": {key: {"path": "assets/replacement.png", "alt": slot["role"]} for key, slot in variant["image_slots"].items()}}, ensure_ascii=False, indent=2), "```", ""])
            if variant.get("chart_slots"):
                lines.extend(["", "## 数据驱动概览微图", "", "content.charts中的每个已登记槽位均需提供title、categories与series，可配置axis_title、unit、chart_type、show_legend和show_data_labels。chart_type支持line或column。类别与每组数值一一对应，每组至少一个已知数，缺值用null。默认零值用于结构占位。主要数据分析使用专门图表页，微图用于此页复盘关系中的结果概览。", "", "开启数据标签时，SVG与原生图共用带字号留白的轴范围、绘图区和底部类目标签。数值、标题、单位及类别全部来自参数。", ""])
                for key, slot in variant["chart_slots"].items():
                    lines.append(f"- `charts.{key}`的原区域为`{slot['source_ref']}`，实际框体为`{slot['frame']}`。{slot['handling']}。")
            if variant.get("retained_source_images"):
                lines.extend(["", "## 保留的原装饰", "", "本页保留用户原模板的结构图标或装饰图片，逐项身份见source-field-coverage.json中本页retained_source_images。其中图片内固化的字形随整图编辑，可在PowerPoint中原生替换整图；nodes字段控制已登记的可编辑文字。参数图片替换使用本页image_slots列出的槽位。", ""])
            lines.extend(["", "全局title必填、2至32码点，使用统一标题框。section_name可选0至24码点，source可选0至64码点。所有可编辑文本通过独立原生carrier导出，页码为派生文字。", "", "## 来源处理", "", "原生PPTX源件保存于用户材料目录，分发包仅含用户资产衍生的几何、字段和说明。原始逐框文字、源框与标准化框在page-catalog.json的variant.fields中。", "", "源标题引用为`" + str(variant.get("title_source_ref")) + "`，原文为“" + str(variant.get("title_source_text") or "无独立源标题") + "”。模板默认标题依据真实结构设置。", "", "密集全景中的diagramCompact为14px、diagramMicro为12px。适用于体系概览或附录局部标签，现场关键结论用统一标题与正常正文字阶表达。", "", "源画布边界裁切已烘焙为可编辑Bezier几何，3D顶面、侧面与前面通过tokens配色的相对明暗保留。", ""])
            if variant.get("ornament_conversions"):
                lines.append("装饰转换记录为`" + json.dumps(variant["ornament_conversions"], ensure_ascii=False) + "`。")
            (target / (name + ".md")).write_text("\n".join(lines) + "\n", encoding="utf-8")
            group_index.append(f"- [{variant_id} · {variant['label']}]({name}.md) · {variant['scenarios']}")
            pages.append({"source_id": variant["source_id"], "source_page": variant["source_page"], "page_type": variant["page_type"], "family": family_id, "variant": variant_id, "status": "parameterized-original-geometry", "manual": "docs/source-pages/" + name + ".md", "preview": "templates/prototypes/" + variant["prototype"], "editable_text_carriers": len(page_bindings), "source_title_ref": variant.get("title_source_ref"), "source_text_refs": [field["source_ref"] for field in variant["fields"].values()], "ornament_conversions": variant.get("ornament_conversions", []), "removed_decorative_refs": variant.get("removed_decorative_refs", []), "clipped_source_paths": variant.get("clipped_source_paths", [])})
        file_name = family_id.removeprefix("source-") + ".md"
        (target / file_name).write_text("\n".join(group_index) + "\n", encoding="utf-8")
        index.append(f"- [{family['label']}](source-pages/{file_name}) · {len(pages)}页 · {family['purpose']}")
        collections.append({"source_file": family["label"], "family": family_id, "pages": pages})
    (root / "docs" / "SOURCE-COLLECTIONS.md").write_text("\n".join(index) + "\n", encoding="utf-8")
    (root / "templates" / "source-collections.json").write_text(json.dumps({"schema_version": 1, "source_pages": sum(len(group["pages"]) for group in collections), "collections": collections, "excluded_source_textboxes": [{"source_id": "circular-04", "source_ref": "slide:2", "status": "source-hidden", "reason": "原cNvPr hidden=1的校验串水印，保持隐藏，不设可见业务字段"}]}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    usage = root / "docs" / "AI-USAGE.md"
    usage.write_text(usage.read_text(encoding="utf-8") + "\n新增四套源模板的128页入口见[按原文件名索引](SOURCE-COLLECTIONS.md)。每页包含关系、场景、完整调用、逐框字段与可见预览。\n", encoding="utf-8")
    write_source_coverage(root, catalog, bindings)


def write_source_coverage(root, catalog, bindings):
    pages = []
    totals = {"original_textboxes": 0, "original_textboxes_parameterized": 0, "original_textboxes_as_geometry": 0, "original_textboxes_hidden": 0, "table_cell_carriers": 0, "outline_text_carriers": 0, "semantic_segment_extra_carriers": 0}
    unmapped = []
    for family_id, family in catalog["families"].items():
        if not family_id.startswith("source-"):
            continue
        for variant_id, variant in family["variants"].items():
            source_refs = set(variant["original_textbox_refs"])
            page_bindings = bindings[family_id + "/" + variant_id]
            original_records = []
            for reference in sorted(source_refs):
                targets = [{key: binding.get(key) for key in ("field", "selector", "source_segment", "min_length", "max_length", "frame", "rotation", "vertical_anchor")}
                           for binding in page_bindings if binding.get("source_ref") == reference]
                ornament = next((item for item in variant.get("ornament_conversions", []) if item["source_ref"] == reference), None)
                hidden = variant["source_id"] == "circular-04" and reference == "slide:2"
                status = "parameterized" if targets else "geometry-ornament" if ornament else "source-hidden" if hidden else "unmapped"
                original_records.append({"source_ref": reference, "status": status, "parameter_targets": targets, **({"geometry": ornament} if ornament else {})})
                totals["original_textboxes"] += 1
                if targets:
                    totals["original_textboxes_parameterized"] += 1
                    totals["semantic_segment_extra_carriers"] += max(0, len(targets) - 1)
                elif ornament:
                    totals["original_textboxes_as_geometry"] += 1
                elif hidden:
                    totals["original_textboxes_hidden"] += 1
                else:
                    unmapped.append({"source_id": variant["source_id"], "source_ref": reference})
            derived = []
            for key, field in variant["fields"].items():
                if field["source_ref"] in source_refs:
                    continue
                kind = "table-cell" if ":cell:" in field["source_ref"] else "outline-text"
                totals["table_cell_carriers" if kind == "table-cell" else "outline_text_carriers"] += 1
                derived.append({"kind": kind, "field": "nodes." + key, "source_ref": field["source_ref"], "frame": field["frame"]})
            pages.append({"source_id": variant["source_id"], "family": family_id, "variant": variant_id, "original_textboxes": original_records, "derived_text_carriers": derived, "image_slots": variant.get("image_slots", {}), "chart_slots": variant.get("chart_slots", {}), "retained_source_images": variant.get("retained_source_images", [])})
    if unmapped:
        raise ValueError("unmapped original source textboxes: " + json.dumps(unmapped, ensure_ascii=False))
    receipt = {"schema_version": 1, "counting_scope": "原128源页的4154有字文本框单独计数。原表格单元格、轮廓字重建和语义分段增加的最终carrier分别登记。", "totals": totals, "unmapped": unmapped, "pages": pages}
    (root / "templates" / "source-field-coverage.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    provenance_path = root / "asset-provenance.json"
    provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
    provenance["source_example_scope"] = {"included": "用户模板的原例文作为source_text、字段角色与来源说明保留，原结构图标和装饰资产按逐页记录保留。", "visible_defaults": "正文用通用语义占位，源案例照片、截图与已识别品牌改为可替换空槽，源图表用零值结构样本。", "excluded": "飞书测试材料、案例输出及四份原始PPTX源件不进入分发包。", "legacy_business_data_flag_scope": "business_data_included=false针对实际汇报案例材料，模板原例文追溯的范围由本项明确。"}
    provenance["source_page_coverage"] = {"source_pages": len(pages), "collections": 4, "old_compatible_variants": 37, "new_source_variants": len(pages), "field_coverage": "templates/source-field-coverage.json", "index": "docs/SOURCE-COLLECTIONS.md"}
    provenance_path.write_text(json.dumps(provenance, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
