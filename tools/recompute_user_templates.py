"""Reproducible, offline source-shape extraction and template constraint migration.

Development tool: never modifies source PPTX or previously maintained template workspaces.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import html
import json
import math
from pathlib import Path
import re
import shutil
import sys
from xml.etree import ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[2]
TASK = ROOT / ".trellis/tasks/11-15-ppt-engine-v1-implementation/research/layout-engine"
CACHE = ROOT / "tmp/ppt-template-analysis-v1"
CANONICAL = ROOT / "project/skill-src/how-to-report"
ICONS = CANONICAL / "assets/templates/business-blue-v1/icons"
OUTPUT = ROOT / "template-library/computed-v1"
SVG = "http://www.w3.org/2000/svg"
NS = {"p": "http://schemas.openxmlformats.org/presentationml/2006/main", "a": "http://schemas.openxmlformats.org/drawingml/2006/main"}
ET.register_namespace("", SVG)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def source_records():
    inventory = json.loads((TASK / "source-inventory.json").read_text(encoding="utf-8"))
    cache_names = {"500页-01商务蓝配色.pptx": ("business-blue", CACHE / "business-blue-import"),
                   "PPT图标.pptx": ("icons", CACHE / "icons-import"),
                   "战略屋.pptx": ("house", CACHE / "new-template-analysis/house"),
                   "蓝色逻辑架构图.pptx": ("architecture", CACHE / "new-template-analysis/architecture"),
                   "循环逻辑图.pptx": ("circular", CACHE / "new-template-analysis/circular"),
                   "立体结构逻辑图1122.pptx": ("spatial", CACHE / "new-template-analysis/spatial")}
    result = []
    for record in inventory["sources"]:
        path = Path(record["path"])
        if path.name.startswith("~$"):
            continue
        match = cache_names.get(path.name)
        if match is None:
            # Directory cache source bytes provide an unambiguous identity for less stable filenames.
            for candidate in [CACHE / "new-template-analysis" / key for key in ("house", "architecture", "circular", "spatial")]:
                if sha(candidate / "sources/source.pptx") == record["sha256"]:
                    match = (candidate.name, candidate)
                    break
        if match is None:
            raise ValueError(f"unknown cache mapping: {path}")
        key, folder = match
        actual = sha(path)
        cached = sha(folder / "sources/source.pptx")
        if actual != record["sha256"] or actual != cached:
            raise ValueError(f"source SHA mismatch: {path}")
        result.append({**record, "key": key, "cache": folder, "source_verified_sha256": actual})
    return result


def svg_shapes(root):
    return [node for node in root.iter() if node.get("data-pptx-frame") and node.get("id", "").startswith("shape-")]


def extract_icons(records):
    record = next(item for item in records if item["key"] == "icons")
    registry = json.loads((ICONS / "catalog.json").read_text(encoding="utf-8"))
    aliases = {key: value for key, value in registry.items() if not key.startswith("ppt-icons-")}
    alias_by_source = {(item["source_slide"], str(item["source_shape_id"])): key for key, item in aliases.items()}
    registry = copy.deepcopy(aliases)
    source_path = Path(record["path"])
    receipt = {"contract_version": "0.1", "algorithm": "independent-source-shape-normalization-v1", "source": str(source_path.relative_to(ROOT)),
               "source_sha256": record["sha256"], "cached_source_sha256": sha(record["cache"] / "sources/source.pptx"), "pages": [], "items": []}
    with zipfile.ZipFile(source_path) as package:
        for page in range(1, record["page_count"] + 1):
            native = ET.fromstring(package.read(f"ppt/slides/slide{page}.xml"))
            native_shapes = native.findall(".//p:sp", NS)
            native_ids = {node.find("p:nvSpPr/p:cNvPr", NS).get("id"): node for node in native_shapes}
            native_groups = native.findall(".//p:grpSp", NS)
            source_svg = record["cache"] / f"authoring-svg/slide_{page:02d}.svg"
            root = ET.parse(source_svg).getroot()
            shapes = svg_shapes(root)
            if native_groups or len(shapes) != len(native_shapes):
                raise ValueError(f"icon source granularity mismatch: page {page}")
            ids = {node.get("id").removeprefix("shape-") for node in shapes}
            if ids != set(native_ids):
                raise ValueError(f"icon shape identity mismatch: page {page}")
            page_items = []
            for node in shapes:
                shape_id = node.get("id").removeprefix("shape-")
                if native_ids[shape_id].find("p:spPr/a:custGeom", NS) is None:
                    raise ValueError(f"icon is not custom geometry: {page}/{shape_id}")
                x, y, width, height = map(float, node.get("data-pptx-frame").split())
                if min(width, height) <= 0 or not list(node.iter(f"{{{SVG}}}path")):
                    raise ValueError(f"icon has no positive vector geometry: {page}/{shape_id}")
                key = f"ppt-icons-p{page:02d}-shape-{shape_id}"
                svg = ET.Element(f"{{{SVG}}}svg", {"viewBox": f"0 0 {width:g} {height:g}", "width": f"{width:g}", "height": f"{height:g}", "role": "img"})
                group = copy.deepcopy(node)
                group.set("transform", f"translate({-x:g} {-y:g})")
                group.set("data-htr-source-key", key)
                for child in group.iter():
                    if child.get("fill") not in {None, "none"}:
                        child.set("fill", "currentColor")
                    if child.get("stroke") not in {None, "none"}:
                        child.set("stroke", "currentColor")
                svg.append(group)
                file = key + ".svg"
                (ICONS / file).write_text(ET.tostring(svg, encoding="unicode") + "\n", encoding="utf-8")
                alias = alias_by_source.get((page, shape_id))
                item = {"file": file, "source_slide": page, "source_shape_id": shape_id, "source_sha256": record["sha256"],
                        "title": f"源图标 第{page}页 · shape {shape_id}", "tags": ["源图标", f"page-{page}", "custom-shape"] + ([alias] if alias else []),
                        "aliases": [alias] if alias else [], "source_frame": [x, y, width, height],
                        "source": {"file": str(source_path.relative_to(ROOT)).replace("\\", "/"), "sha256": record["sha256"], "slide": page,
                                   "shape_id": shape_id, "part": f"ppt/slides/slide{page}.xml", "geometry": "custGeom", "group_depth": 0},
                        "asset_sha256": sha(ICONS / file), "path_count": len(list(group.iter(f"{{{SVG}}}path")))}
                registry[key] = item
                receipt["items"].append({"key": key, **item})
                page_items.append(key)
            receipt["pages"].append({"page": page, "native_custom_shapes": len(native_shapes), "independent_svg_count": len(page_items), "keys": page_items})
    if len(receipt["items"]) != 847:
        raise ValueError(f"expected 847 source icons, got {len(receipt['items'])}")
    for alias, item in aliases.items():
        item["alias_of"] = f"ppt-icons-p{item['source_slide']:02d}-shape-{item['source_shape_id']}"
        registry[alias] = item
    write_json(ICONS / "catalog.json", registry)
    receipt.update(source_asset_count=847, legacy_alias_count=len(aliases), total_catalog_keys=len(registry))
    write_json(TASK / "assets/icon-extraction-receipt.json", receipt)
    icon_gallery(receipt)
    print(json.dumps({key: receipt[key] for key in ("source_asset_count", "legacy_alias_count", "total_catalog_keys")}), flush=True)


def icon_gallery(receipt):
    cards = []
    for item in receipt["items"]:
        key = item["key"]
        cards.append(f'<button class="card" data-search="{html.escape(key + " " + " ".join(item["tags"]))}" onclick="copyKey(this)"><img loading="lazy" src="{item["file"]}" alt="{key}"><code>{key}</code><span>{html.escape(" / ".join(item["aliases"]))}</span></button>')
    document = '''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>PPT单图标目录</title><style>
body{font:16px system-ui;margin:32px;color:#26354a;background:#f5f7fa}header{position:sticky;top:0;background:#f5f7fa;padding:16px 0;z-index:2}input{padding:10px;width:450px;max-width:90%}.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(210px,1fr));gap:12px}.card{background:white;border:1px solid #d8dfeb;padding:16px;display:grid;justify-items:center;gap:8px;cursor:pointer;min-height:160px}.card img{width:72px;height:72px;object-fit:contain}.card code{font-size:11px}.card span{min-height:16px}button:focus-visible{outline:3px solid #2368c4}</style>
<header><h1>847个源图标 · 24个兼容别名</h1><p>每项均来自PPT图标.pptx的独立原生custom shape。点击复制稳定key。没有可靠语义名称的项按源页/shape ID登记。</p><input id="search" aria-label="搜索key、源页或已有标签" placeholder="搜索key / page-3 / team"><span id="status" role="status"></span></header><main class="grid">'''+"".join(cards)+'''</main><script>
const cards=[...document.querySelectorAll('.card')];search.oninput=()=>{const q=search.value.toLowerCase().split(/\\s+/).filter(Boolean);let n=0;for(const c of cards){const yes=q.every(t=>c.dataset.search.toLowerCase().includes(t));c.hidden=!yes;c.style.display=yes?'grid':'none';n+=yes}document.getElementById('status').textContent=' '+n+' 项'};
async function copyKey(card){const key=card.querySelector('code').textContent;try{await navigator.clipboard.writeText(key);document.getElementById('status').textContent='已复制 '+key}catch(e){prompt('复制图标key',key)}}
</script></html>'''
    (ICONS / "gallery.html").write_text(document, encoding="utf-8")


def source_anchor(frame, source_canvas, target_canvas):
    """Solve four normalized edge constraints; preserves signed source geometry."""
    x, y, width, height = frame
    sw, sh = source_canvas
    tw, th = target_canvas
    constraints = {"left": x / sw, "top": y / sh,
                   "right": (x + width) / sw, "bottom": (y + height) / sh}
    solved = [constraints["left"] * tw, constraints["top"] * th,
              (constraints["right"] - constraints["left"]) * tw,
              (constraints["bottom"] - constraints["top"]) * th]
    if not all(math.isfinite(value) for value in solved):
        raise ValueError("nonfinite source geometry")
    return constraints, solved


def pure_colors(root):
    replacements = {}
    for node in root.iter():
        if node.tag.split("}")[-1] in {"linearGradient", "radialGradient"}:
            stops = list(node.iter(f"{{{SVG}}}stop"))
            if not stops:
                continue
            middle = stops[len(stops) // 2]
            color = middle.get("stop-color")
            if color is None:
                match = re.search(r"stop-color\s*:\s*([^;]+)", middle.get("style", ""))
                color = match.group(1).strip() if match else None
            if color:
                replacements[node.get("id")] = color
    changed = []
    for node in root.iter():
        for attribute in ("fill", "stroke"):
            value = node.get(attribute, "")
            match = re.fullmatch(r"url\(#([^)]*)\)", value)
            if match and match.group(1) in replacements:
                color = replacements[match.group(1)]
                changed.append({"element": node.get("id"), "attribute": attribute, "gradient": match.group(1), "solid": color})
                node.set(attribute, color)
    return changed


def _visible_geometry(node):
    for child in node.iter():
        if child.tag.split("}")[-1] in {"path", "rect", "circle", "ellipse", "polygon", "image"}:
            if child.tag.split("}")[-1] == "image" or child.get("fill", "none") != "none" or child.get("stroke", "none") != "none":
                return True
    return False


def reflow_candidates(root, frames, page_id, tokens):
    """Recognize only disjoint, sibling text runs. Never infer business topology."""
    from presentation_layout import lower_layout_page
    candidates = []
    for parent in root.iter():
        pure = []
        for node in parent:
            if node.get("id") not in frames or _visible_geometry(node):
                continue
            texts = list(node.iter(f"{{{SVG}}}text"))
            if not texts or any(child.get("data-pptx-object") == "group" for child in node):
                continue
            text = "\n".join("".join(child.itertext()).strip() for child in texts).strip()
            frame = frames[node.get("id")]
            if text and frame[2] > 1 and frame[3] > 1:
                pure.append((node.get("id"), text, frame))
        for axis, kind in ((0, "row"), (1, "column")):
            groups = {}
            cross = 1 - axis
            for item in pure:
                frame = item[2]
                groups.setdefault(round(frame[cross] / 4), []).append(item)
            for bucket in groups.values():
                ordered = sorted(bucket, key=lambda item: item[2][axis])
                if not 3 <= len(ordered) <= 12:
                    continue
                if any(a[2][axis] + a[2][axis + 2] > b[2][axis] + .01 for a, b in zip(ordered, ordered[1:])):
                    continue
                # Source label placement is recognized; measured new text can change vertical flow.
                identifier = f"{page_id}-flow-{len(candidates)+1}"
                children = [{"id": item[0], "type": "leaf", "grow": 1 if kind == "row" else 0,
                             "basis": 0 if kind == "row" else "auto", "element": {"type": "text", "text": item[1], "role": "body"}} for item in ordered]
                model = {"id": identifier, "kind": "layout", "layout_version": "0.1", "layout": {"id": identifier + "-root", "type": kind,
                         "gap": 12, "children": children}}
                try:
                    scene, result = lower_layout_page(model, {}, [1440, 810], tokens, bounds=[36, 36, 1368, 738])
                    candidates.append({"source_ids": [item[0] for item in ordered], "scope": "local sibling text-label excerpt; does not replace surrounding source geometry",
                                       "kind": kind, "status": "computed", "model": model, "scene": scene, "report": result})
                except Exception as error:
                    candidates.append({"source_ids": [item[0] for item in ordered], "kind": kind, "status": "capacity_rejected",
                                       "model": model, "diagnostic": getattr(error, "diagnostic", {"reason": str(error)})})
                if len(candidates) >= 8:
                    return candidates
    return candidates


def _overlap(a, b):
    return min(a[0] + a[2], b[0] + b[2]) > max(a[0], b[0]) + 1e-7 and min(a[1] + a[3], b[1] + b[3]) > max(a[1], b[1]) + 1e-7


def refresh_missing_pages(records):
    """Re-import cache omissions using the current bundled converter, preserving diagnostics."""
    sys.path[:0] = [str(CANONICAL / "runtime/ppt-engine/scripts"), str(CANONICAL.parent / "shared/scripts")]
    from pptx_to_svg.converter import ConvertOptions, ConvertResult, _convert_slide, _extract_theme_info, _make_palette
    from pptx_to_svg.ooxml_loader import OoxmlPackage
    index = json.loads((OUTPUT / "index.json").read_text(encoding="utf-8"))
    receipts = []
    for record in records:
        pages = [item for item in index["pages"] if item["source_key"] == record["key"] and item["source_import_missing"]]
        if not pages:
            continue
        with OoxmlPackage(Path(record["path"])) as package:
            for item in pages:
                slide = package.get_slide(item["source_page"])
                options = ConvertOptions(embed_images=True, inheritance_mode="flat")
                result = ConvertResult(source_file=Path(record["path"]).name)
                theme = package.resolve_theme(slide.master)
                palette = _make_palette(slide.master, theme, options, result, part_path=slide.part.path, slide_index=slide.index)
                _, fonts = _extract_theme_info(theme, palette) if theme is not None else ({}, {})
                artifact = _convert_slide(package, slide, palette, options, result.diagnostics, fonts)
                target = TASK / f"assets/reimported-source-svg/{record['key']}/slide_{slide.index:02d}.svg"
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(artifact.svg, encoding="utf-8")
                actual = {node.get("id").removeprefix("shape-") for node in svg_shapes(ET.fromstring(artifact.svg))}
                recovered = sorted(set(item["source_import_missing"]) & actual)
                receipts.append({"id": item["id"], "source_sha256": record["sha256"], "prior_missing": item["source_import_missing"],
                                 "recovered": recovered, "remaining": sorted(set(item["source_import_missing"]) - actual),
                                 "diagnostics": [diagnostic.to_dict() if hasattr(diagnostic, "to_dict") else vars(diagnostic) for diagnostic in result.diagnostics],
                                 "svg_sha256": sha(target)})
        print(json.dumps({"refreshed_source": record["key"], "pages": len(pages)}), flush=True)
    write_json(TASK / "assets/source-reimport-receipt.json", {"pages": receipts})


def migrate_templates(records):
    sys.path.insert(0, str(CANONICAL / "scripts"))
    sys.path.insert(0, str(CANONICAL.parent / "shared/scripts"))
    from report_ppt import load_template
    _, _, tokens = load_template()
    target = [1440, 810]
    tokens["canvas"].update(width=1440, height=810)
    manifest = {"contract_version": "0.1", "algorithm": "normalized-source-edge-constraints-v1", "target_canvas": target,
                "scope": "Every original object is recalculated independently. Fixed source anchors preserve layering; they do not implement arbitrary content reflow or infer topology.",
                "sources": [], "pages": []}
    for record in records:
        if record["key"] == "icons":
            continue
        folder = OUTPUT / record["key"]
        (folder / "svg").mkdir(parents=True, exist_ok=True)
        images = record["cache"] / "images"
        if images.is_dir():
            shutil.copytree(images, folder / "images", dirs_exist_ok=True)
        manifest["sources"].append({"key": record["key"], "path": str(Path(record["path"]).relative_to(ROOT)), "sha256": record["sha256"],
                                    "cache_sha256": record["source_verified_sha256"], "page_count": record["page_count"]})
        with zipfile.ZipFile(record["path"]) as package:
            for page in range(1, record["page_count"] + 1):
                identifier = f"{record['key']}-p{page:03d}"
                source_svg = record["cache"] / f"authoring-svg/slide_{page:02d}.svg"
                refreshed = TASK / f"assets/reimported-source-svg/{record['key']}/slide_{page:02d}.svg"
                if refreshed.is_file():
                    source_svg = refreshed
                root = ET.parse(source_svg).getroot()
                source_canvas = list(map(float, root.get("viewBox").split()[2:]))
                shapes = svg_shapes(root)
                frames = {node.get("id"): list(map(float, node.get("data-pptx-frame").split())) for node in shapes}
                parent_map = {child: parent for parent in root.iter() for child in parent}
                model = {"id": identifier, "source": {"file": str(Path(record["path"]).relative_to(ROOT)), "sha256": record["sha256"], "page": page,
                         "svg_sha256": sha(source_svg)}, "algorithm": manifest["algorithm"], "source_canvas": source_canvas, "target_canvas": target,
                         "constraints": [], "shape_hierarchy": [], "fixed_source_anchors": True, "arbitrary_content_reflow": False}
                results, diagnostics = [], []
                for node in shapes:
                    original = frames[node.get("id")]
                    constraints, solved = source_anchor(original, source_canvas, target)
                    parent = parent_map.get(node)
                    parent_id = parent.get("id") if parent is not None else None
                    model["constraints"].append({"id": node.get("id"), "type": node.get("data-pptx-object"), "normalized_edges": constraints,
                                                 "source_frame": original, "source_ref": node.get("data-pptx-source-ref")})
                    model["shape_hierarchy"].append({"id": node.get("id"), "parent": parent_id})
                    results.append({"id": node.get("id"), "frame": solved, "source_frame": original})
                    if original[2] < 0 or original[3] < 0:
                        diagnostics.append({"code": "source_signed_frame", "id": node.get("id"), "frame": original})
                    if original[0] < -.01 or original[1] < -.01 or original[0] + original[2] > source_canvas[0] + .01 or original[1] + original[3] > source_canvas[1] + .01:
                        diagnostics.append({"code": "source_existing_outside_canvas", "id": node.get("id"), "source_frame": original,
                                            "target_frame": solved, "disposition": "source cropping retained, no new normalized overflow"})
                solid = pure_colors(root)
                # Keep group wrappers and source stacking order. Only terminal objects receive an independent matrix.
                for node in shapes:
                    if any(child.get("id") in frames for child in node.iter() if child is not node):
                        continue
                    sx, sy = target[0] / source_canvas[0], target[1] / source_canvas[1]
                    existing = node.get("transform", "")
                    node.set("transform", f"matrix({sx:.12g} 0 0 {sy:.12g} 0 0)" + (" " + existing if existing else ""))
                    node.set("data-htr-layout", "normalized-source-edge-constraints-v1")
                # Imported slide-background paint can be outside the per-shape carrier wrappers.
                for node in root:
                    if node.tag.split("}")[-1] in {"defs", "metadata", "title", "desc"} or any(child.get("id") in frames for child in node.iter()):
                        continue
                    sx, sy = target[0] / source_canvas[0], target[1] / source_canvas[1]
                    existing = node.get("transform", "")
                    node.set("transform", f"matrix({sx:.12g} 0 0 {sy:.12g} 0 0)" + (" " + existing if existing else ""))
                    node.set("data-htr-layout", "source-background-affine")
                # Frame annotations are in the target coordinate system, including retained group wrappers.
                for result in results:
                    node = next(item for item in shapes if item.get("id") == result["id"])
                    node.set("data-pptx-frame", " ".join(f"{value:.10g}" for value in result["frame"]))
                root.set("viewBox", "0 0 1440 810")
                root.set("width", "1440")
                root.set("height", "810")
                root.set("data-htr-source-page", identifier)
                # Source and target pairwise intersection relations must be identical under positive scaling.
                new_overlap, original_overlap = [], 0
                for index, left in enumerate(results):
                    for right in results[index + 1:]:
                        before, after = _overlap(left["source_frame"], right["source_frame"]), _overlap(left["frame"], right["frame"])
                        original_overlap += before
                        if after != before:
                            new_overlap.append([left["id"], right["id"]])
                if new_overlap:
                    diagnostics.append({"code": "new_overlap_relation", "pairs": new_overlap})
                native = ET.fromstring(package.read(f"ppt/slides/slide{page}.xml"))
                native_ids = {node.get("id") for node in native.findall(".//p:cNvPr", NS)} - {"1"}
                svg_ids = {node.get("id").removeprefix("shape-") for node in shapes}
                missing = sorted(native_ids - svg_ids)
                if missing:
                    diagnostics.append({"code": "source_import_object_missing", "shape_ids": missing, "disposition": "requires source-native inspection; import completeness not asserted"})
                candidates = reflow_candidates(root, frames, identifier, tokens)
                model["recognized_local_flows"] = [{key: value for key, value in candidate.items() if key not in {"scene", "report"}} for candidate in candidates]
                output = folder / f"svg/slide_{page:03d}.svg"
                output.write_text(ET.tostring(root, encoding="unicode") + "\n", encoding="utf-8")
                status = "computed_with_source_import_gaps" if missing else "computed_source_anchors"
                report = {"id": identifier, "status": status, "algorithm": manifest["algorithm"], "nodes": results, "diagnostics": diagnostics,
                          "source_overlap_pair_count": original_overlap, "new_overlap_pairs": new_overlap, "pure_color_replacements": solid,
                          "local_reflow_results": candidates, "result_svg_sha256": sha(output), "source_object_count": len(native_ids), "imported_object_count": len(svg_ids)}
                write_json(folder / f"constraints/slide_{page:03d}.json", model)
                write_json(folder / f"reports/slide_{page:03d}.json", report)
                text = " ".join("".join(node.itertext()) for node in root.iter(f"{{{SVG}}}text"))
                manifest["pages"].append({"id": identifier, "source_key": record["key"], "source_page": page, "status": status,
                                           "shape_count": len(results), "source_import_missing": missing,
                                           "preview": f"{record['key']}/svg/slide_{page:03d}.svg", "constraints": f"{record['key']}/constraints/slide_{page:03d}.json",
                                           "report": f"{record['key']}/reports/slide_{page:03d}.json", "search_text": text[:3000],
                                           "local_flow_count": sum(item["status"] == "computed" for item in candidates), "source_sha256": record["sha256"]})
        print(json.dumps({"source": record["key"], "completed_pages": record["page_count"]}), flush=True)
    if len(manifest["pages"]) != 673:
        raise ValueError(f"expected 673 template pages, got {len(manifest['pages'])}")
    manifest["summary"] = {"template_pages": len(manifest["pages"]), "recomputed_objects": sum(item["shape_count"] for item in manifest["pages"]),
                           "pages_with_import_gaps": sum(bool(item["source_import_missing"]) for item in manifest["pages"]),
                           "pages_with_local_text_flows": sum(bool(item["local_flow_count"]) for item in manifest["pages"]),
                           "local_text_flow_excerpts": sum(item["local_flow_count"] for item in manifest["pages"]), "whole_page_arbitrary_reflow": 0}
    write_json(OUTPUT / "index.json", manifest)
    write_json(TASK / "assets/template-migration-summary.json", {key: value for key, value in manifest.items() if key != "pages"})
    template_gallery(manifest)
    print(json.dumps(manifest["summary"]), flush=True)


def template_gallery(manifest):
    cards = []
    for page in manifest["pages"]:
        label = html.escape(page["id"])
        search = html.escape(label + " " + page["search_text"])
        cards.append(f'<article data-search="{search}"><a href="{page["preview"]}"><img loading="lazy" src="{page["preview"]}" alt="{label}"></a><p>{label} · {page["shape_count"]}对象 · {page["status"]}</p><a href="{page["constraints"]}">约束</a> <a href="{page["report"]}">计算记录</a></article>')
    document = '''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>673页源模板数学重算</title><style>body{font:15px system-ui;margin:30px;background:#f5f7fa;color:#26354a}header{position:sticky;top:0;padding:12px;background:#f5f7fa;z-index:2}input{padding:10px;width:500px;max-width:90%}main{display:grid;grid-template-columns:repeat(auto-fill,minmax(380px,1fr));gap:20px}article{background:white;padding:14px}img{width:100%;aspect-ratio:16/9;object-fit:contain}p{font-size:13px}a{color:#175bba}</style><header><h1>673页源模板 · 逐形状锚点数学重算</h1><p>画布1440×810。固定源锚点保留图层、包含和相交关系；纯色派生替换渐变。局部row/column文字流的实际求解范围见计算记录，不代表全页任意内容回流。</p><input id="search" aria-label="检索页码、源集合或原文" placeholder="检索页码 / house / 原文"><span id="count"></span></header><main>'''+"".join(cards)+'''</main><script>const cards=[...document.querySelectorAll('article')];search.oninput=()=>{let n=0;const q=search.value.toLowerCase().split(/\\s+/).filter(Boolean);for(const c of cards){const yes=q.every(t=>c.dataset.search.toLowerCase().includes(t));c.style.display=yes?'block':'none';n+=yes}count.textContent=' '+n+'页'};</script></html>'''
    (OUTPUT / "gallery.html").write_text(document, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["icons", "templates", "all", "refresh-missing"])
    args = parser.parse_args()
    records = source_records()
    if args.mode == "refresh-missing":
        refresh_missing_pages(records)
    if args.mode in {"icons", "all"}:
        extract_icons(records)
    if args.mode in {"templates", "all"}:
        migrate_templates(records)


if __name__ == "__main__":
    main()
