"""Export a portable, offline view of real engine assets and their contracts."""
from __future__ import annotations

import copy
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import tempfile

from report_ppt import DEFAULT_TEMPLATE, SKILL_ROOT, external_target, load_template, read_json

SCHEMA = "how-to-report.storybook.v1"
RESOURCES = SKILL_ROOT / "assets/storybook"
CHUNK_SIZE = 256


def _json(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), allow_nan=False).replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")


def _local(root, reference):
    if not isinstance(reference, str) or not reference or "\\" in reference or ":" in reference:
        raise ValueError("storybook catalog index must be a relative local path")
    path = root / reference
    if any(part in {".", ".."} for part in reference.split("/")) or path.is_absolute() and Path(reference).is_absolute():
        raise ValueError("storybook index escapes catalog")
    resolved = path.resolve()
    if not resolved.is_relative_to(root.resolve()):
        raise ValueError("storybook index escapes catalog")
    for item in (path, *path.parents):
        if item == root.parent:
            break
        if item.is_symlink() or (item.exists() and getattr(item.lstat(), "st_file_attributes", 0) & 0x400):
            raise ValueError("storybook index links are not allowed")
    return path


def _native_records(catalog):
    root = Path(catalog).resolve()
    if root.is_file():
        root = root.parent
    manifest = json.loads((root / "catalog.json").read_text(encoding="utf-8"))
    if manifest.get("schema") != "how-to-report.native-catalog.v1":
        raise ValueError("unsupported native catalog schema")
    for source in manifest["sources"]:
        for page in source["pages"]:
            payload = _local(root, page["index"]).read_bytes()
            if hashlib.sha256(payload).hexdigest() != page.get("sha256"):
                raise ValueError("catalog page index hash mismatch")
            index = json.loads(payload)
            for original in index["assets"]:
                record = copy.deepcopy(original)
                record["kind"] = "native-" + record["kind"]
                record["label"] = record.get("name") or record["id"]
                record["purpose"] = record.get("text_excerpt") or "原生源对象"
                origin = source.get("source", source["id"])
                record["source_name"] = origin.get("name", source["id"]) if isinstance(origin, dict) else str(origin)
                record["mode"] = "source-anchor"
                record["style_scope"] = "保留原PPT字体、字号、颜色和效果；不自动套用14pt报告规范"
                record["preview_scope"] = "源页面区域，可能包含邻近或遮叠对象；实际摘取范围见对象层级"
                yield record


def _builtin_records(template):
    # Adapt the existing registries rather than maintaining a second template list.
    from presentation_library import _records, _describe
    _, catalog, _ = load_template(template)
    for summary in _records(template):
        if summary["kind"] == "chart-vocabulary":
            continue  # The chart adapter below owns the live vocabulary state.
        record = _describe(summary, template) if summary["kind"] != "icon" else copy.deepcopy(summary)
        record["label"] = record.get("label") or record.get("purpose") or record["id"]
        if record["kind"] == "component":
            record["label"] = {"topology": "拓扑结构", "paragraph-flow": "段落文档流", "partition": "整体构成",
                               "comparison": "基准比较", "evidence-map": "证据与解释", "progress-ring": "进度环形图"}[record["id"].split(".", 1)[1]]
        if record["kind"] == "profile":
            from presentation_text_profile import describe_text_profile
            record.update(describe_text_profile(record["id"].split(".", 1)[1]))
            record.update(kind="profile", label="全局文字规范 · report-14pt", executable=True)
        record["mode"] = "computed" if record["kind"] in {"template", "component", "recipe", "profile"} else "registered"
        record["style_scope"] = "report-14pt：正文14pt、最低9pt、正文80%黑、注释35%黑" if record["kind"] in {"component", "recipe"} else "当前模板或原资产声明的样式"
        if record["kind"] == "template":
            record["style_scope"] = "新请求的角色文字使用report-14pt；原型预览保留原模板样式，源几何/图像内文字不承诺改写"
            record["contract"]["array_key"] = catalog["families"][record["family"]].get("array_key")
            if record["contract"]["variant"].get("renderer") == "source-diagram":
                record["mode"] = "source-parameter"
                record["limitations"] = ["从源模板派生的固定锚点参数模板；支持声明的文字/数据槽，不支持任意节点增删和拓扑重排。原始PPT完整保真重放请使用原生资产。"]
        if record["kind"] == "primitive":
            record["executable"] = False
            record["limitations"] = ["底层绘图合同；AI新稿须通过参数组件或计算容器调用，不直接填写自由几何。"]
        record["preview_scope"] = "原模板原型；下载的新稿请求按report-14pt重新计算文字，预览未随请求重算" if record["kind"] == "template" else "独立资产"
        refs = record.get("preview_refs", [])
        if refs:
            ref = refs[0]
            root = SKILL_ROOT if ref["scope"] == "package" else Path(template)
            record["preview"] = {"image": str(root / ref["ref"])}
        _add_invocation(record)
        yield record
    from presentation_chart_assets import chart_assets, describe_chart_asset
    for summary in chart_assets():
        record = describe_chart_asset(summary["id"])
        record.update(kind="chart", mode="computed" if record["executable"] else "planned",
                      preview_scope="引擎按示例数据计算的SVG；示例不代表业务事实",
                      style_scope="report-14pt：正文14pt、最低9pt、正文80%黑、注释35%黑")
        yield record
    from presentation_palette import palette_catalog, palette_story
    for palette in palette_catalog():
        record = copy.deepcopy(palette)
        identifier = record["id"]
        record.update(id="palette." + identifier, palette_id=identifier, mode="computed",
                      preview_scope="引擎按该色卡计算的同数据示例；选择全局配色后，其他静态预览不会自动重算",
                      style_scope="仅替换语义颜色，正文14pt/80%黑、注释35%黑；原生保真资产不改色",
                      invocation={"mode": "author", "request": palette_story(identifier)})
        yield record


def _leaf_story(element, title):
    from presentation_library import profile_identity
    element = copy.deepcopy(element)
    element.pop("frame", None)
    element.pop("id", None)
    if "style" in element:
        element["style"] = {k: v for k, v in element["style"].items() if k not in {"font_size", "value_size"}}
    return {"schema_version": "0.1", "project_id": "selected-component", "revision": 1,
            "brief": {"audience": "组件库使用者", "synthetic": True, "design_profile": profile_identity()},
            "sources": [], "facts": {key: {"value": value} for key, value in
                {"total": 100, "enabled": 40, "remaining": 60, "planned": 60, "actual": 80}.items()},
            "pages": [{"id": "story", "kind": "layout", "layout_version": "0.1", "title": title,
                "layout": {"id": "page", "type": "column", "padding": [48, 32, 48, 30], "gap": 16,
                    "children": [{"id": "title", "type": "leaf", "element": {"type": "text", "role": "title", "text": title}},
                                 {"id": "component", "type": "leaf", "height": 510, "element": element},
                                 {"id": "source", "type": "leaf", "element": {"type": "text", "role": "caption", "text": "Synthetic data / engine component example"}}]}}]}


def _add_invocation(record):
    """Adapt registry examples into actual geometry-free public author requests."""
    kind = record["kind"]
    if kind == "profile":
        from presentation_text_profile import text_profile_story
        record["invocation"] = {"mode": "author", "request": text_profile_story(record["profile_id"])}
        record["preview_scope"] = "引擎按现有report-14pt规范计算的角色、段落与富文本示例，可切换实际预览页"
        record["style_scope"] = "通过brief.design_profile绑定全局文字规范；原生源格式保持不变"
    elif kind == "component":
        variant_example = record.get("variant_examples", {}).get("arrow-ring")
        if variant_example:
            record["invocation"] = {"mode": "author", "request": read_json(SKILL_ROOT / variant_example["example_ref"])}
            record["preview_scope"] = "arrow-ring变体的实际合成示例；其他topology布局见组件合同，不表示数量占比"
            return
        examples = record.get("contract", {}).get("examples", {})
        if examples:
            record["invocation"] = {"mode": "author", "request": _leaf_story(next(iter(examples.values())), record["label"])}
            record["preview_scope"] = "引擎计算的独立组件示例；示例不代表业务事实"
    elif kind == "icon":
        record["invocation"] = {"mode": "author", "asset_root": str(SKILL_ROOT),
                                "request": _leaf_story({"type": "image", "path": record["asset_ref"], "fit": "contain"}, record["label"])}
        record["limitations"] = ["此请求输出SVG图像对象；内部路径不自动变成可分别编辑的PowerPoint形状。需要原生形状时选择原生组合或原子。"]
    elif kind == "recipe":
        request = copy.deepcopy(record["example"])
        key = record["id"].split(".", 1)[1]
        request["pages"] = [p for p in request["pages"] if p["recipe"] == key]
        if request["pages"]:
            record["invocation"] = {"mode": "recipe", "request": request}
            record["preview_scope"] = "引擎计算的组合示例；示例不代表业务事实"
    elif kind == "template":
        from presentation_library import profile_identity
        content = copy.deepcopy(record["contract"].get("prototype_content", {}))
        variant = record["contract"]["variant"]
        content.update(copy.deepcopy(variant.get("prototype_content", {})))
        array_key = record["contract"].get("array_key")
        if array_key:
            content[array_key] = content[array_key][:variant["capacity"]]
        if record["family"] == "gantt" and not content["tasks"]:
            content["tasks"] = [{"name": "示例任务", "start": content["start"], "end": content["end"]}]
            content["source"] = "合成示例，需替换为实际任务与期间"
        record["invocation"] = {"mode": "author", "request": {
            "schema_version": "0.1", "project_id": "selected-template", "revision": 1,
            "brief": {"audience": "填写实际听众", "purpose": "填写汇报目的", "design_profile": profile_identity()}, "facts": {},
            "pages": [{"id": "page-1", "kind": "template", "job": "填写本页需要回答的问题",
                       "template": {"family": record["family"], "variant": record["variant"],
                                    "content": content}}]}}


def _component_previews(records, work, template):
    from presentation_compiler import build_project
    from presentation_recipes import compose_document
    for record in records:
        if record["kind"] not in {"component", "recipe", "palette", "profile"} or "invocation" not in record:
            continue
        request = record["invocation"]["request"]
        author = compose_document(request, template_root=template) if record["kind"] == "recipe" else request
        output = work / record["id"]
        receipt = build_project(author, output, template_root=template, geometry_policy="computed")
        record["preview"] = {"image": str(output / receipt["pages"][0]["svg"])}
        if len(receipt["pages"]) > 1:
            labels = {"type-roles": "文字角色", "type-paragraphs": "段落与富文本", "type-alignment": "对齐与内边距"} if record["kind"] == "profile" else {}
            record["preview_pages"] = [{"image": str(output / page["svg"]), "page_id": page["id"],
                                        "title": labels.get(page["id"], author["pages"][i].get("title", page["id"]))}
                                       for i, page in enumerate(receipt["pages"])]


def _chart_previews(records, work, template):
    from presentation_chart_assets import chart_story
    from presentation_compiler import build_project
    charts = [r for r in records if r["kind"] == "chart" and r.get("executable")]
    if not charts:
        return
    stories = [chart_story(r["id"]) for r in charts]
    author = copy.deepcopy(stories[0])
    author["project_id"] = "storybook-chart-examples"
    author["pages"] = []
    for number, story in enumerate(stories, 1):
        page = copy.deepcopy(story["pages"][0])
        page["id"] = f"chart-{number:03}"
        def prefix_layout(node):
            node["id"] = page["id"] + "--" + node["id"]
            for child in node.get("children", []):
                prefix_layout(child)
        prefix_layout(page["layout"])
        author["pages"].append(page)
    receipt = build_project(author, work, template_root=template, geometry_policy="computed")
    for record, page in zip(charts, receipt["pages"]):
        record["preview"] = {"image": str(work / page["svg"])}


def _valid_crop(preview):
    crop, size = preview.get("crop_emu"), preview.get("slide_emu")
    if crop is None and size is None:
        return
    if not isinstance(crop, list) or len(crop) != 4 or not isinstance(size, list) or len(size) != 2:
        raise ValueError("storybook crop requires crop_emu[4] and slide_emu[2]")
    if any(type(n) not in {int, float} or not math.isfinite(n) for n in crop + size) or min(crop[2:]) < 0 or min(size) <= 0:
        raise ValueError("storybook crop must have finite coordinates, nonnegative object size and positive canvas dimensions")
    if 0 in crop[2:]:
        adjusted = list(crop)
        for axis in (0, 1):
            if crop[axis + 2] == 0:
                padding = size[axis] / 200
                adjusted[axis] -= padding
                adjusted[axis + 2] = 2 * padding
        preview["crop_emu"] = adjusted
        preview["viewport_adjustment"] = "Zero-thickness line viewport padded; native bbox and geometry unchanged"


def _publish(records, stage, catalog, title):
    (stage / "data").mkdir()
    (stage / "media").mkdir()
    media = {}
    index = []
    seen = set()
    chunks = []
    for number, record in enumerate(records):
        if not isinstance(record, dict) or not isinstance(record.get("id"), str) or record["id"] in seen:
            raise ValueError("storybook assets require unique string IDs")
        seen.add(record["id"])
        previews = [record.get("preview") or {}, *record.get("preview_pages", [])]
        for preview in previews:
            if not preview.get("image"):
                continue
            path = Path(preview["image"])
            if not path.is_file():
                raise ValueError(f"storybook preview is missing: {path}")
            if path.suffix.lower() not in {".svg", ".png", ".jpg", ".jpeg", ".webp"}:
                raise ValueError("unsupported storybook preview format")
            key = str(path.resolve())
            if key not in media:
                raw = path.read_bytes()
                relative = "media/" + hashlib.sha256(raw).hexdigest() + path.suffix.lower()
                destination = stage / relative
                if not destination.exists():
                    destination.write_bytes(raw)
                media[key] = relative
            _valid_crop(preview)
            preview["image"] = media[key]
        chunk = number // CHUNK_SIZE
        if chunk == len(chunks):
            chunks.append([])
        chunks[chunk].append(record)
        index.append({key: copy.deepcopy(record.get(key)) for key in (
            "id", "kind", "label", "purpose", "executable", "mode", "source_id", "source_name",
            "slide_number", "hidden", "conditional", "visible_default", "categories", "relations", "preview", "preview_scope",
            "presentation_role", "selection_guidance")})
        index[-1]["chunk"] = f"chunk-{chunk:04}"
    for number, records_chunk in enumerate(chunks):
        (stage / "data" / f"chunk-{number:04}.js").write_text(
            f"window.STORYBOOK_CHUNKS['chunk-{number:04}']={_json(records_chunk)};\n", encoding="utf-8")
    config = {"schema": SCHEMA, "title": title, "catalog": str(Path(catalog).resolve()) if catalog else None,
              "cli": str(SKILL_ROOT / "scripts/report_engine.py"), "count": len(index), "page_size": 24,
              "palettes": [{key: copy.deepcopy(r.get(key)) for key in ("id", "palette_id", "label", "roles", "categorical")}
                           for r in records if r["kind"] == "palette"],
              "items": index}
    profile = next((r for r in records if r["kind"] == "profile" and r.get("profile_id") == "report-14pt"), None)
    if profile:
        role_sizes = [r["font_size_pt"] for r in profile["roles"].values()]
        config["text_profile"] = {"id": profile["id"], "label": profile["label"], "identity": profile["identity"],
                                  "body_pt": round(profile["roles"]["body"]["font_size_pt"], 4), "minimum_pt": round(min(role_sizes), 4)}
    (stage / "data/index.js").write_text("window.STORYBOOK_INDEX=" + _json(config) + ";\n", encoding="utf-8")
    for name in ("index.html", "storybook.css", "storybook-requests.js", "storybook.js"):
        shutil.copyfile(RESOURCES / name, stage / name)
    return {"asset_count": len(index), "preview_files": len(set(media.values())), "detail_chunks": len(chunks),
            "counts": {kind: sum(r["kind"] == kind for r in index) for kind in sorted({r["kind"] for r in index})},
            "executable_count": sum(r["executable"] is True for r in index)}


def build_storybook(catalog, output, *, template=DEFAULT_TEMPLATE, extra_records=None,
                    title="PPT Storybook", include_builtin=True, chart_previews=True):
    """Export immutable HTML, data chunks and local previews; preserve sources."""
    output = external_target(output)
    if output.exists():
        raise ValueError("storybook output already exists")
    if not isinstance(title, str) or not title or len(title) > 160:
        raise ValueError("storybook title must be text of 1..160 characters")
    records = list(_native_records(catalog)) if catalog is not None else []
    if include_builtin:
        records.extend(_builtin_records(template))
    if extra_records is not None:
        if not isinstance(extra_records, list):
            raise ValueError("extra_records must be a list")
        records.extend(copy.deepcopy(extra_records))
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".storybook-", dir=output.parent) as temporary:
        temporary = Path(temporary)
        if include_builtin and chart_previews:
            _chart_previews(records, temporary / "chart-previews", template)
            _component_previews(records, temporary / "component-previews", template)
        stage = temporary / "site"
        stage.mkdir()
        summary = _publish(records, stage, catalog, title)
        report = {"schema": SCHEMA, "title": title, **summary,
                  "preview_status": "source-region and engine-SVG previews; actual target validation separate",
                  "source_catalog": str(Path(catalog).resolve()) if catalog else None,
                  "offline": True, "generation": "download parameter requests, execute normal engine CLI"}
        (stage / "storybook-manifest.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        if output.exists():
            raise ValueError("storybook output appeared during build")
        os.rename(stage, output)
    return {**report, "output": str(output), "entry": str(output / "index.html")}
