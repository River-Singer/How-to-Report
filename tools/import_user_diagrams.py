"""Compile the four user-owned source collections into callable diagram variants.

Development-only entry point. Input is the inspected authoring SVG projection,
never an upstream template library. Chromium supplies transformed SVG bounds.
"""
from __future__ import annotations

import argparse
import base64
import colorsys
import copy
from functools import lru_cache
import hashlib
import json
import math
from pathlib import Path
import re
import sys
from zipfile import ZipFile
from xml.etree import ElementTree as ET

PROJECT = Path(__file__).resolve().parents[1]
WORKSPACE = PROJECT.parent
TEMPLATE = PROJECT / "skill-src/how-to-report/assets/templates/business-blue-v1"
SOURCE = WORKSPACE / "tmp/ppt-template-analysis-v1/new-template-analysis"
RESEARCH = WORKSPACE / ".trellis/tasks/11-14-ppt-production-extraction/research/additional-template-coverage"
NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", NS)
COLLECTIONS = {
    "house": ("房子图战略图.pptx", 30, "战略屋与目标支撑"),
    "architecture": ("蓝色逻辑架构图.pptx", 24, "模块接口与分层架构"),
    "spatial": ("立体结构逻辑图1122.pptx", 34, "立体层次与结构关系"),
    "circular": ("圆形逻辑图PPT模版.pptx", 40, "环绕扇区与循环关系"),
}


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


@lru_cache(maxsize=1)
def source_metadata():
    records = read(RESEARCH / "source-textbox-metadata.json")["textboxes"]
    return {(record["source_id"], record["source_ref"]): record for record in records}


def source_font_reference(group, number, reference):
    """Read the original style fallback instead of the SVG import's fallback ink."""
    namespaces = {"p": "http://schemas.openxmlformats.org/presentationml/2006/main", "a": "http://schemas.openxmlformats.org/drawingml/2006/main"}
    with ZipFile(SOURCE / group / "sources/source.pptx") as package:
        slide = ET.fromstring(package.read(f"ppt/slides/slide{number}.xml"))
    identifier = reference.removeprefix("slide:")
    for shape in slide.findall(".//p:sp", namespaces):
        properties = shape.find("p:nvSpPr/p:cNvPr", namespaces)
        if properties is not None and properties.get("id") == identifier:
            color = shape.find("p:style/a:fontRef/a:schemeClr", namespaces)
            return color.get("val") if color is not None else None
    return None


def apply_text_placements(root, records, group, number):
    """Resolve imported rotations and the four source pages using text warp."""
    sys.path.insert(0, str(PROJECT / "skill-src/how-to-report/runtime/ppt-engine/scripts"))
    from svg_to_pptx.drawingml.utils import matrix_multiply, parse_transform_matrix
    parents = {child: parent for parent in root.iter() for child in parent}
    source_id = f"{group}-{number:02d}"
    for record in records:
        original = source_metadata().get((source_id, record["ref"]))
        if original:
            record["text"] = original["text"]
        chain, node = [], record["texts"][0]
        while node in parents:
            chain.append(node)
            node = parents[node]
        matrix = (1, 0, 0, 1, 0, 0)
        for node in reversed(chain):
            matrix = matrix_multiply(matrix, parse_transform_matrix(node.get("transform", "")))
        a, b, c, d, e, f = matrix
        x, y, width, height = record["frame"]
        center_x, center_y = x + width / 2, y + height / 2
        width *= math.hypot(a, b)
        height *= math.hypot(c, d)
        record["placement_frame"] = [a * center_x + c * center_y + e - width / 2, b * center_x + d * center_y + f - height / 2, width, height]
        record["rotation"] = math.degrees(math.atan2(b, a))
        if original and original.get("local_frame_emu"):
            source_rotation = original["local_frame_emu"]["rotation_degrees"] + sum(context["frame_emu"]["rotation_degrees"] for context in original["group_context"])
            record["rotation"] = (source_rotation + 180) % 360 - 180
    placements = {}
    if source_id == "circular-03":
        for refs, radius, width, height in (([4, 31, 32, 33], 344, 184, 58), ([34, 35, 37, 36], 465, 190, 44), ([42, 41, 40, 39], 575, 230, 44)):
            for ref, angle in zip(refs, (-157.5, -112.5, -67.5, -22.5)):
                radians = math.radians(angle)
                placements[ref] = (640 + radius * math.cos(radians), 681 + radius * math.sin(radians), width, height, angle + 90)
    if source_id == "circular-02":
        placements = {125: (640, 425, 180, 40, 0), 127: (420, 601, 180, 40, -74.79), 129: (861, 602, 180, 40, 75), 131: (304, 614, 90, 38, -85.19), 133: (334, 509, 90, 38, -60.11), 134: (412, 407, 90, 38, -40.8), 135: (876, 427, 90, 38, 47.97), 136: (949, 521, 90, 38, 67.56), 137: (982, 637, 90, 38, 90), 138: (643, 335, 300, 40, 0), 139: (315, 425, 260, 38, -53.5), 140: (987, 425, 330, 38, 57.12), 141: (1065, 351, 330, 38, 57.12), 142: (656, 132, 330, 38, 0), 144: (216, 389, 420, 38, -54)}
    if source_id == "circular-20":
        placements = {58: (775, 272, 90, 38, -45), 59: (958, 236, 210, 38, 28.18), 60: (1095, 409, 130, 38, 90), 61: (963, 578, 180, 38, -16.12), 62: (747, 485, 150, 38, 60)}
    if source_id == "spatial-25":
        placements = {94: (654, 622, 180, 38, 0)}
        original = next(record for record in records if record["ref"] == "slide:137")
        records.remove(original)
        for index, (cx, cy, angle) in enumerate(((481, 225, -45), (596, 167, -12), (735, 167, 12), (847, 225, 45)), 1):
            segment = {**original, "key": "shape_137_segment_" + str(index), "segment": index, "placement_frame": [cx - 85, cy - 16, 170, 32], "rotation": angle}
            records.append(segment)
    for record in records:
        identifier = record["ref"].removeprefix("slide:")
        if identifier.isdigit() and int(identifier) in placements:
            cx, cy, width, height, angle = placements[int(identifier)]
            record["placement_frame"] = [cx - width / 2, cy - height / 2, width, height]
            record["rotation"] = angle
            record["warp_handling"] = "源曲线文字按实际扇区位置和切线角度转为独立原生文字，原变形信息保留追溯"
            record["align"] = "center"


def display_title(semantic):
    group, number = semantic["source_id"].rsplit("-", 1)
    return read(RESEARCH / "source-page-default-titles.json")[group][int(number) - 1]


def label(node):
    return "".join(node.itertext()).strip()


def expand_assets(root, group):
    """Recover vectors extracted as icons and the one editable source table."""
    for parent in list(root.iter()):
        for child in list(parent):
            tag = child.tag.rsplit("}", 1)[-1]
            if tag == "use" and child.get("data-icon"):
                asset = SOURCE / group / "icons" / (child.get("data-icon") + ".svg")
                wrapper = ET.Element(f"{{{NS}}}g")
                for node in ET.parse(asset).getroot():
                    wrapper.append(copy.deepcopy(node))
                parent.insert(list(parent).index(child), wrapper)
                parent.remove(child)
            if tag == "image":
                href = child.get("href", child.get("{http://www.w3.org/1999/xlink}href", ""))
                if href.startswith("data:"):
                    continue
                asset = (SOURCE / group / "authoring-svg" / href).resolve()
                child.set("data-htr-source-image", href)
                child.set("data-htr-source-image-sha256", hashlib.sha256(asset.read_bytes()).hexdigest())
                mime = "image/svg+xml" if asset.suffix.lower() == ".svg" else "image/jpeg" if asset.suffix.lower() in {".jpg", ".jpeg"} else "image/png"
                child.set("href", f"data:{mime};base64," + base64.b64encode(asset.read_bytes()).decode())
    for parent in list(root.iter()):
        metadata = next((node for node in parent if node.tag == f"{{{NS}}}metadata" and node.text and '"ppt-master.semantic-table.v2"' in node.text), None)
        if metadata is None:
            continue
        table = json.loads(metadata.text)
        parent_ref = parent.get("data-pptx-source-ref", "slide:" + parent.get("id", "table"))
        for child in list(parent):
            parent.remove(child)
        y = table["y"]
        for row_number, row in enumerate(table["rows"]):
            height = table["row_heights"][row_number]
            x = table["x"]
            for column_number, cell in enumerate(row):
                width = table["column_widths"][column_number]
                cell_group = ET.SubElement(parent, f"{{{NS}}}g", {
                    "data-pptx-source-ref": f"{parent_ref}:cell:{row_number}:{column_number}",
                    "data-pptx-frame": f"{x + 6} {y + 3} {width - 12} {height - 6}",
                })
                ET.SubElement(cell_group, f"{{{NS}}}rect", {"x": str(x), "y": str(y), "width": str(width), "height": str(height), "fill": "#518AF5" if row_number == 0 else "#C1D4FB"})
                text = ET.SubElement(cell_group, f"{{{NS}}}text", {"x": str(x + 6), "y": str(y + height * .7), "font-size": "13.333", "fill": "#FFFFFF" if row_number == 0 else "#383535"})
                text.text = "\n".join("".join(run.get("text", "") for run in paragraph["runs"]) for paragraph in cell["paragraphs"])
                x += width
            y += height


def replace_business_examples(root, records, group, number):
    """Expose business photos, screenshots, and two source brands as inputs."""
    parents = {child: parent for parent in root.iter() for child in parent}
    slots = {}
    charts = {}
    retained = []
    for image in list(root.iter(f"{{{NS}}}image")):
        current = image
        while current is not root and not current.get("data-pptx-source-ref"):
            current = parents[current]
        reference = current.get("data-pptx-source-ref")
        file_name = image.get("data-htr-source-image", "")
        if image.get("data-pptx-replacement-status") == "unsupported-date-axis":
            frame = [float(value) for value in image.get("data-pptx-frame").split()]
            charts["chart_" + reference.removeprefix("slide:")] = {"source_ref": reference, "source_frame": frame, "axis_mode": "ordered-categories", "source_axis": "date-axis", "handling": "原日期轴区域改用数据驱动原生类目轴图表，类目按输入等距排列，日期间隔不编码为横向距离"}
            parents[image].remove(image)
            continue
        business = (group == "house" and number == 3 and not file_name.endswith(".svg")
                    or group == "house" and number == 16 and reference == "slide:129"
                    or group == "house" and number == 23
                    or group == "spatial" and number == 7
                    or group == "circular" and number == 7)
        if not business:
            retained.append({"source_ref": reference, "source_image": file_name, "sha256": image.get("data-htr-source-image-sha256"), "handling": "用户原有结构图标或装饰图片，保留原资产"})
            continue
        frame_source = image if image.get("data-pptx-frame") else current
        frame = [float(value) for value in frame_source.get("data-pptx-frame").split()]
        key = "picture_" + reference.removeprefix("slide:")
        role = "案例照片或截图" if group == "house" and number == 3 else "业务界面截图" if group == "house" and number == 23 else "品牌或形象" if group in {"house", "spatial"} else "中心产品图片"
        slots[key] = {"source_refs": [reference], "source_frame": frame, "source_image": file_name, "source_sha256": image.get("data-htr-source-image-sha256"), "role": role}
        parents[image].remove(image)
    if group == "circular" and number == 7:
        sources = [value["source_refs"][0] for value in slots.values()]
        slots = {"product_image": {"source_refs": sources, "source_frame": [505, 405, 270, 280], "role": "中心产品图，原两张同产品透明裁片合并为一个可替换图片槽", "source_image": "image3.png + image4.png"}}
    brand_refs = {2: "slide:95", 15: "slide:25", 17: "slide:13", 33: "slide:30"}
    if group == "circular" and number in brand_refs:
        target_ref = brand_refs[number]
        brand_frame = None
        for parent in root.iter():
            for child in list(parent):
                if child.get("data-pptx-source-ref") == target_ref:
                    brand_frame = [float(value) for value in child.get("data-pptx-frame").split()]
                    parent.remove(child)
        slots["brand_mark"] = {"source_refs": [target_ref], "source_frame": brand_frame, "role": "品牌标识，替换原矢量品牌或应用标识", "source_image": "source-vector-brand"}
    outline_labels = {20: {50: "1.1 数据沉淀"}, 25: {16: "细节处理", 26: "把握程度", 27: "标准化"}}
    if group == "circular" and number in outline_labels:
        for parent in root.iter():
            for child in list(parent):
                reference = child.get("data-pptx-source-ref", "")
                identifier = reference.removeprefix("slide:")
                if not identifier.isdigit() or int(identifier) not in outline_labels[number]:
                    continue
                frame = [float(value) for value in child.get("data-pptx-frame").split()]
                text = ET.Element(f"{{{NS}}}text", {"font-size": "18", "fill": "#FFFFFF"})
                records.append({"element": ET.Element(f"{{{NS}}}g"), "texts": [text], "ref": reference, "key": "shape_" + identifier, "frame": frame, "placement_frame": frame, "text": outline_labels[number][int(identifier)], "size": 18, "align": "center", "source_handling": "原轮廓业务文字重建为独立可编辑字段"})
                parent.remove(child)
    return slots, retained, charts


def source_texts(root):
    parents = {child: parent for parent in root.iter() for child in parent}
    groups = {}
    for text in root.iter(f"{{{NS}}}text"):
        parent = parents[text]
        while parent is not root and not parent.get("data-pptx-source-ref") and not parent.get("data-pptx-frame"):
            parent = parents[parent]
        ref = parent.get("data-pptx-source-ref")
        if not ref:
            shape = re.search(r"shape-(\d+)", parent.get("id", ""))
            ref = "slide:" + shape.group(1) if shape else None
        if not ref:
            raise ValueError("Source text has no source-ref")
        record = groups.setdefault(ref, {"element": parent, "texts": [], "ref": ref})
        record["texts"].append(text)
    records = []
    for index, record in enumerate(groups.values()):
        element = record["element"]
        frame = [float(value) for value in element.get("data-pptx-frame").split()]
        text = "\n".join(label(node) for node in record["texts"])
        size = max(float(node.get("font-size", 16)) for node in record["texts"])
        record.update(frame=frame, text=text, size=size, key="shape_" + re.sub(r"\W", "_", record["ref"].removeprefix("slide:")))
        records.append(record)
    return records


def color_slot(value):
    if not re.fullmatch(r"#[0-9a-fA-F]{6}", value):
        return None
    red, green, blue = (int(value[index:index + 2], 16) / 255 for index in (1, 3, 5))
    _, lightness, saturation = colorsys.rgb_to_hls(red, green, blue)
    if saturation < .12:
        return "lt1" if lightness > .96 else "lt2" if lightness > .8 else "dk2" if lightness > .45 else "dk1"
    if lightness > .9:
        return "lt2"
    if lightness > .75:
        return "accent4"
    if lightness > .6:
        return "accent3"
    if lightness > .45:
        return "accent2"
    return "accent1"


def flatten_geometry(root):
    """Bake source transforms into paths, including reflected arrow directions."""
    sys.path.insert(0, str(PROJECT / "skill-src/how-to-report/runtime/ppt-engine/scripts"))
    from svg_to_pptx.drawingml.paths import normalize_path_commands, parse_svg_path, svg_path_to_absolute, transform_path_commands
    from svg_to_pptx.drawingml.utils import matrix_multiply, parse_transform_matrix
    import pathops
    from fontTools.svgLib.path import parse_path
    flattened = ET.Element(root.tag, root.attrib)
    gradients = {node.get("id"): node for node in root.iter() if node.tag == f"{{{NS}}}linearGradient"}
    gradient_number = 0
    inherited_names = {"fill", "fill-opacity", "stroke", "stroke-width", "stroke-opacity", "stroke-linecap", "stroke-linejoin", "stroke-dasharray", "clip-path"}

    def append(node, inherited, matrix, opacity, source_ref):
        nonlocal gradient_number
        tag = node.tag.rsplit("}", 1)[-1]
        if tag == "defs":
            flattened.append(copy.deepcopy(node))
            return
        matrix = matrix_multiply(matrix, parse_transform_matrix(node.get("transform", "")))
        opacity *= float(node.get("opacity", "1"))
        attributes = {**inherited, **node.attrib}
        source_ref = node.get("data-pptx-source-ref", source_ref)
        if tag in {"g", "svg"}:
            inherited = {key: value for key, value in attributes.items() if key in inherited_names}
            for child in node:
                append(child, inherited, matrix, opacity, source_ref)
            return
        attributes.pop("transform", None)
        attributes["opacity"] = str(opacity)
        if source_ref:
            attributes["data-htr-source-ref"] = source_ref
        if tag == "path":
            source_path = pathops.Path()
            parse_path(node.get("d", ""), source_path.getPen())
            old_bounds = source_path.bounds
            new_bounds = source_path.transform(*matrix).bounds
            if matrix != (1, 0, 0, 1, 0, 0) and new_bounds[2] - new_bounds[0] > .01 and new_bounds[3] - new_bounds[1] > .01:
                for paint in ("fill", "stroke"):
                    reference = re.fullmatch(r"url\(#(.+)\)", attributes.get(paint, ""))
                    if not reference or reference.group(1) not in gradients:
                        continue
                    gradient = gradients[reference.group(1)]
                    baked = copy.deepcopy(gradient)
                    gradient_number += 1
                    identifier = f"baked-gradient-{gradient_number}"
                    baked.set("id", identifier)
                    baked.set("gradientUnits", "objectBoundingBox")
                    a, b, c, d, e, f = matrix
                    for suffix in ("1", "2"):
                        gx = float(gradient.get("x" + suffix, "0" if suffix == "1" else "1"))
                        gy = float(gradient.get("y" + suffix, "0"))
                        if gradient.get("gradientUnits") != "userSpaceOnUse":
                            gx = old_bounds[0] + gx * (old_bounds[2] - old_bounds[0])
                            gy = old_bounds[1] + gy * (old_bounds[3] - old_bounds[1])
                        world_x, world_y = a * gx + c * gy + e, b * gx + d * gy + f
                        baked.set("x" + suffix, str(min(1.1, max(-.1, (world_x - new_bounds[0]) / (new_bounds[2] - new_bounds[0])))))
                        baked.set("y" + suffix, str(min(1.1, max(-.1, (world_y - new_bounds[1]) / (new_bounds[3] - new_bounds[1])))))
                    flattened.find(f"{{{NS}}}defs").append(baked)
                    attributes[paint] = "url(#" + identifier + ")"
            commands = normalize_path_commands(svg_path_to_absolute(parse_svg_path(node.get("d", ""))))
            commands = transform_path_commands(commands, matrix)
            attributes["d"] = " ".join(command.cmd + " " + " ".join(f"{value:.6f}".rstrip("0").rstrip(".") for value in command.args) for command in commands)
        elif matrix != (1, 0, 0, 1, 0, 0):
            attributes["transform"] = "matrix(" + " ".join(str(value) for value in matrix) + ")"
        atom = ET.SubElement(flattened, node.tag, attributes)
        for child in node:
            atom.append(copy.deepcopy(child))

    append(root, {}, (1, 0, 0, 1, 0, 0), 1, None)
    root[:] = list(flattened)


def clip_source_paths(root):
    """Bake source-canvas clipping into editable Bezier geometry at import time."""
    import pathops
    from fontTools.svgLib.path import parse_path
    from fontTools.pens.svgPathPen import SVGPathPen
    sys.path.insert(0, str(PROJECT / "skill-src/how-to-report/runtime/ppt-engine/scripts"))
    from svg_to_pptx.drawingml.utils import matrix_multiply, parse_transform_matrix
    parents = {child: parent for parent in root.iter() for child in parent}
    crop = pathops.Path()
    parse_path("M 0 0 L 1280 0 L 1280 720 L 0 720 Z", crop.getPen())
    clipped = []
    for node in list(root.iter(f"{{{NS}}}path")):
        ancestors = []
        current = node
        while current in parents:
            ancestors.append(current)
            current = parents[current]
        if any(ancestor.tag == f"{{{NS}}}defs" for ancestor in ancestors):
            continue
        if node.get("fill") == "none" and node.get("stroke") in {None, "none"}:
            continue
        matrix = (1, 0, 0, 1, 0, 0)
        for ancestor in reversed(ancestors):
            matrix = matrix_multiply(matrix, parse_transform_matrix(ancestor.get("transform", "")))
        path = pathops.Path()
        parse_path(node.get("d", ""), path.getPen())
        world = path.transform(*matrix)
        left, top, right, bottom = world.bounds
        if left >= -.01 and top >= -.01 and right <= 1280.01 and bottom <= 720.01:
            continue
        node.set("data-htr-original-bounds", " ".join(str(value) for value in path.bounds))
        if node.get("fill") == "none":
            path.stroke(float(node.get("stroke-width", "1")), pathops.LineCap.ROUND_CAP if node.get("stroke-linecap") == "round" else pathops.LineCap.BUTT_CAP, pathops.LineJoin.ROUND_JOIN if node.get("stroke-linejoin") == "round" else pathops.LineJoin.MITER_JOIN, 4, dash_array=[float(value) for value in node.get("stroke-dasharray", "").replace(",", " ").split()] or None)
            world = path.transform(*matrix)
            node.set("fill", node.get("stroke"))
            if node.get("stroke-opacity"):
                node.set("fill-opacity", node.get("stroke-opacity"))
            node.set("stroke", "none")
            for attribute in ("marker-start", "marker-end", "stroke-dasharray"):
                node.attrib.pop(attribute, None)
        result = pathops.op(world, crop, pathops.PathOp.INTERSECTION)
        a, b, c, d, e, f = matrix
        determinant = a * d - b * c
        inverse = (d / determinant, -b / determinant, -c / determinant, a / determinant, (c * f - d * e) / determinant, (b * e - a * f) / determinant)
        local = result.transform(*inverse)
        pen = SVGPathPen(None)
        local.draw(pen)
        commands = pen.getCommands()
        if commands:
            node.set("d", commands)
        else:
            parents[node].remove(node)
        source_ref = next((ancestor.get("data-pptx-source-ref", ancestor.get("data-htr-source-ref")) for ancestor in ancestors if ancestor.get("data-pptx-source-ref", ancestor.get("data-htr-source-ref"))), None)
        clipped.append(source_ref)
    return clipped


def normalize_gradient_paints(root):
    from svg_to_pptx.drawingml.paths import _project_path_like_bounds
    definitions = root.find(f"{{{NS}}}defs")
    gradients = {node.get("id"): node for node in root.iter() if node.tag in {f"{{{NS}}}linearGradient", f"{{{NS}}}radialGradient"}}
    for index, node in enumerate(list(root.iter())):
        for attribute in ("fill", "stroke"):
            match = re.fullmatch(r"url\(#(.+)\)", node.get(attribute, ""))
            if not match or match.group(1) not in gradients:
                continue
            gradient = gradients[match.group(1)]
            extent = _project_path_like_bounds(node)
            marker_stroke = attribute == "stroke" and (node.get("marker-start") or node.get("marker-end"))
            degenerate = extent is not None and (extent[2] - extent[0] < .01 or extent[3] - extent[1] < .01)
            if marker_stroke or attribute == "stroke" and degenerate:
                stops = list(gradient.findall(f"{{{NS}}}stop"))
                node.set(attribute, stops[0].get("stop-color", "#5385C5"))
                opacity = max(float(stop.get("stop-opacity", "1")) for stop in stops)
                node.set(attribute + "-opacity", str(float(node.get(attribute + "-opacity", "1")) * opacity))
                continue
            if gradient.get("gradientUnits") != "userSpaceOnUse" and not node.get("data-htr-original-bounds"):
                continue
            if extent is None or degenerate:
                continue
            old_extent = [float(value) for value in node.get("data-htr-original-bounds", " ".join(str(value) for value in extent)).split()]
            converted = copy.deepcopy(gradient)
            converted.set("id", f"normalized-gradient-{index}-{attribute}")
            converted.set("gradientUnits", "objectBoundingBox")
            for coordinate in ("x1", "y1", "x2", "y2"):
                if coordinate not in converted.attrib:
                    continue
                axis = 0 if coordinate.startswith("x") else 1
                value = float(converted.get(coordinate))
                if gradient.get("gradientUnits") != "userSpaceOnUse":
                    value = old_extent[axis] + value * (old_extent[axis + 2] - old_extent[axis])
                normalized = (value - extent[axis]) / (extent[axis + 2] - extent[axis])
                converted.set(coordinate, str(min(1.1, max(-.1, normalized))))
            definitions.append(converted)
            node.set(attribute, "url(#" + converted.get("id") + ")")


def prepare(root, records, title, group, number):
    for parent in root.iter():
        for child in list(parent):
            if child.tag == f"{{{NS}}}text":
                parent.remove(child)
    # Full-slide backgrounds and decorative shapes outside the source canvas
    # have no node role. Their removal makes the shared white canvas visible.
    removed = []
    for parent in list(root.iter()):
        for child in list(parent):
            if group == "circular" and number == 12 and child.get("data-pptx-source-ref") == "slide:63":
                removed.append(child.get("data-pptx-source-ref"))
                parent.remove(child)
            if parent is root and child.tag == f"{{{NS}}}rect" and float(child.get("width", 0)) >= 1280 and float(child.get("height", 0)) >= 720:
                parent.remove(child)
    for shape in root.iter():
        if shape.get("data-pptx-prst") == "arc":
            for path in shape.findall(f"{{{NS}}}path"):
                if path.get("fill") == "none" and "Z" in path.get("d", ""):
                    path.set("d", path.get("d").rsplit("Z", 1)[-1].strip())
    flatten_geometry(root)
    clipped = clip_source_paths(root)
    normalize_gradient_paints(root)
    for node in root.iter():
        for attribute in list(node.attrib):
            if attribute.startswith("data-pptx-"):
                node.attrib.pop(attribute)
        node.attrib.pop("filter", None)
        node.attrib.pop("data-icon", None)
        for attribute in ("fill", "stroke", "stop-color"):
            slot = color_slot(node.get(attribute, ""))
            if slot:
                node.set("data-htr-" + attribute, slot)
    for parent in root.iter():
        for node in list(parent):
            if node.get("gradientUnits") == "userSpaceOnUse" and node.get("id", "").startswith("mstrokegrad"):
                parent.remove(node)
    definitions = root.find(f"{{{NS}}}defs")
    markers = {node.get("id"): node for node in root.iter(f"{{{NS}}}marker")}
    for node in list(root.iter()):
        for attribute in ("marker-start", "marker-end"):
            reference = re.fullmatch(r"url\(#(.+)\)", node.get(attribute, ""))
            if not reference or reference.group(1) not in markers:
                continue
            color = node.get("stroke", "#5385C5")
            slot = node.get("data-htr-stroke", "accent2")
            identifier = reference.group(1) + "-" + slot
            if definitions.find(f".//*[@id='{identifier}']") is None:
                marker = copy.deepcopy(markers[reference.group(1)])
                marker.set("id", identifier)
                for descendant in marker.iter():
                    for paint in ("fill", "stroke"):
                        if descendant.get(paint) not in {None, "none"}:
                            descendant.set(paint, color)
                            descendant.set("data-htr-" + paint, slot)
                definitions.append(marker)
            node.set(attribute, "url(#" + identifier + ")")
    return removed, clipped


def bounds(page, root):
    ET.register_namespace("", NS)
    markup = ET.tostring(root, encoding="unicode")
    page.set_content('<html><body style="margin:0">' + markup + '</body></html>')
    return page.evaluate("""() => [...document.querySelector('svg').querySelectorAll('path,rect,line,polygon,polyline,circle,ellipse,image')]
      .filter(n=>!n.closest('defs') && (n.tagName==='image' || (getComputedStyle(n).fill!=='none' || getComputedStyle(n).stroke!=='none')))
      .map(n=>{const r=n.getBoundingClientRect();return [r.x,r.y,r.width,r.height]})
      .filter(r=>r[2]>0 && r[3]>0 && r[0]+r[2]>0 && r[1]+r[3]>0 && r[0]<1280 && r[1]<720)""")


def role_for(size, height, width):
    candidates = [(28, "heading"), (24, "body"), (20, "compactBody"), (16, "caption"), (14, "diagramCompact"), (12, "diagramMicro")]
    return next((role for value, role in candidates if value <= size * 1.12 and value <= height and value <= width), "diagramMicro")


def compile_page(group, number, browser_page, tokens):
    path = SOURCE / group / "authoring-svg" / f"slide_{number:02d}.svg"
    root = ET.parse(path).getroot()
    expand_assets(root, group)
    records = source_texts(root)
    apply_text_placements(root, records, group, number)
    visual_slots, retained_images, chart_slots = replace_business_examples(root, records, group, number)
    ornaments = []
    for record in list(records):
        if record["text"] and set(record["text"]) <= {"|", "\n", " "}:
            x, y, width, height = record["frame"]
            count = record["text"].count("|")
            for tick in range(count):
                angle = 2 * math.pi * tick / count
                ET.SubElement(record["element"], f"{{{NS}}}line", {
                    "x1": str(x + width / 2 + width * .45 * math.cos(angle)),
                    "y1": str(y + height / 2 + height * .45 * math.sin(angle)),
                    "x2": str(x + width / 2 + width * .5 * math.cos(angle)),
                    "y2": str(y + height / 2 + height * .5 * math.sin(angle)),
                    "stroke": "#5385C5", "stroke-width": "1", "fill": "none",
                })
            ornaments.append({"source_ref": record["ref"], "reason": "原文本为textCircle变形的重复竖线装饰，转换为可编辑径向刻线，不设业务文字字段", "ticks": count})
            records.remove(record)
    candidates = [record for record in records if record["frame"][1] < 150 and 24 <= record["size"] <= 64]
    title = min(candidates, key=lambda record: (-record["size"], record["frame"][1])) if candidates else None
    if group == "circular" and number == 36:
        title = None
    metadata = []
    if title:
        subtitles = [record for record in records if record is not title
                     and record["frame"][1] < 165
                     and abs(record["frame"][0] - title["frame"][0]) < 32
                     and abs(record["frame"][1] - title["frame"][1]) < 80
                     and record["size"] <= 24]
        if subtitles:
            subtitle = min(subtitles, key=lambda record: abs(record["frame"][1] - title["frame"][1]))
            metadata.append({"source_ref": subtitle["ref"], "source_text": subtitle["text"], "field": "section_name", "handling": "可选全局页脚元信息，默认留空"})
            records.remove(subtitle)
    removed, clipped = prepare(root, records, title, group, number)
    frames = bounds(browser_page, root)
    body_records = [record for record in records if record is not title]
    frames += [record["placement_frame"] for record in body_records]
    frames += [slot["source_frame"] for slot in list(visual_slots.values()) + list(chart_slots.values())]
    if not frames:
        frames = [[0, 0, 1280, 720]]
    left = max(0, min(frame[0] for frame in frames))
    top = max(0, min(frame[1] for frame in frames))
    right = min(1280, max(frame[0] + frame[2] for frame in frames))
    bottom = min(720, max(frame[1] + frame[3] for frame in frames))
    bx, by, bw, bh = tokens["body"]["frame"]
    scale = min(bw / max(right - left, 1), bh / max(bottom - top, 1))
    dx = bx + (bw - (right - left) * scale) / 2 - left * scale
    dy = by + (bh - (bottom - top) * scale) / 2 - top * scale
    for slot in list(visual_slots.values()) + list(chart_slots.values()):
        x, y, width, height = slot["source_frame"]
        slot["frame"] = [round(x * scale + dx, 4), round(y * scale + dy, 4), round(width * scale, 4), round(height * scale, 4)]
        if slot.get("axis_mode"):
            slot["frame"][2] = round(slot["frame"][2] - 24 * scale, 4)
            slot["frame"][1] = round(slot["frame"][1] - 16, 4)
            slot["frame"][3] = round(slot["frame"][3] + 16, 4)
    fields, values = {}, {}
    sys.path.insert(0, str(PROJECT / "skill-src/how-to-report/runtime/ppt-engine/scripts"))
    from text_measure import wrap_text
    for record in body_records:
        x, y, width, height = record["placement_frame"]
        frame = [max(bx, x * scale + dx), max(by, y * scale + dy), width * scale, height * scale]
        frame[2] = min(frame[2], bx + bw - frame[0])
        frame[3] = min(max(frame[3], 12), by + bh - frame[1])
        role = role_for(record["size"] * scale, frame[3], frame[2])
        if group == "circular" and number == 12 and record["ref"] == "slide:61":
            frame = [471.2 * scale + dx, 328 * scale + dy, 334.74 * scale, 80 * scale]
            role = "metric"
        size = tokens["font"]["sizes"][role]
        if frame[2] < size * 1.12:
            frame[0] -= (size * 1.12 - frame[2]) / 2
            frame[2] = size * 1.12
            frame[0] = min(max(bx, frame[0]), bx + bw - frame[2])
        if frame[3] < size * 1.25:
            frame[1] -= (size * 1.25 - frame[3]) / 2
            frame[3] = size * 1.25
            frame[1] = min(max(by, frame[1]), by + bh - frame[3])
        leading = tokens["font"]["lineHeight"].get(role, 1.3)
        # The contract uses CJK-sized code points as a conservative ceiling.
        columns = max(1, math.floor(frame[2] / (size * .45)))
        rows = max(1, math.floor((frame[3] - size * 1.25) / (size * leading)) + 1)
        maximum = columns * rows
        original = record["text"]
        sample = "说明" if len(original) > 12 else "模块"
        if group == "house":
            sample = "目标" if y < 180 else "能力" if y < 250 else "支撑说明" if len(original) > 12 else "行动"
        if group == "spatial":
            sample = "关系说明" if len(original) > 12 else "层级"
        if group == "circular":
            sample = "中心主题" if record["size"] > 60 else "节点说明" if len(original) > 12 else "节点"
        def fits(value):
            lines, _, oversized = wrap_text(value, size=size, max_width=frame[2], family="Arial, Microsoft YaHei, Microsoft YaHei", weight=str(tokens["font"]["weights"][role]))
            return not oversized and size * 1.25 + (len(lines) - 1) * size * leading <= frame[3] + .01
        if len(sample) > maximum or not fits(sample):
            # Prototype labels are explicit semantic placeholders. Complete
            # source wording remains inspectable in every field contract.
            sample = "说明" if len(original) > 12 else "节点"
            if not fits(sample):
                sample = "项"
        color = record["texts"][0].get("fill", "#000000")
        white = color.upper() == "#FFFFFF"
        horizontal = "左" if frame[0] + frame[2] / 2 < 440 else "右" if frame[0] > 840 else "中"
        vertical = "上" if frame[1] < 280 else "下" if frame[1] > 475 else "中"
        role_description = f"{vertical}{horizontal}节点，源标签“{original[:40]}”"
        fields[record["key"]] = {
            "source_ref": record["ref"], "source_text": original, "role": role_description,
            "frame": [round(value, 4) for value in frame], "source_frame": record["frame"],
            "font_role": role, "min_length": 1, "max_length": maximum,
            "align": record.get("align", {"middle": "center", "end": "end"}.get(record["texts"][0].get("text-anchor"), "start")),
            "rotation": round(record.get("rotation", 0), 4), "source_segment": record.get("segment"), "warp_handling": record.get("warp_handling"),
            "vertical_anchor": "ctr" if record.get("warp_handling") else source_metadata().get((f"{group}-{number:02d}", record["ref"]), {}).get("body_properties", {}).get("anchor", "t"),
            "color_role": "surface" if white else "primary" if record["size"] > 60 or color_slot(color) not in {None, "dk1", "dk2"} else "text",
        }
        field = fields[record["key"]]
        if group == "circular" and number == 13 and record["ref"] == "slide:8":
            if source_font_reference(group, number, record["ref"]) != "lt1":
                raise ValueError("circular-13 slide:8 source fontRef changed")
            field["color_role"] = "surface"
            field["source_color_resolution"] = "原fontRef为lt1白色，保留白底上的源重复标签及独立参数，主要可见标签对应slide:22"
        if group == "circular" and number == 35 and record["ref"] in {"slide:7", "slide:8", "slide:9", "slide:11", "slide:13"}:
            field.update(role="服务编号，源编号“" + original + "”", max_length=2, max_lines=1, input_pattern=r"^[0-9]{1,2}$")
            field["frame"][3] = round(min(field["frame"][3], 40), 4)
            sample = original
        if group == "spatial" and number == 7:
            pairs = {"slide:120": "slide:122", "slide:124": "slide:125", "slide:127": "slide:129", "slide:131": "slide:132", "slide:134": "slide:136", "slide:138": "slide:139"}
            if record["ref"] in pairs:
                unit_record = next(item for item in body_records if item["ref"] == pairs[record["ref"]])
                unit_x = unit_record["placement_frame"][0] * scale + dx
                field["frame"][2] = round(min(field["frame"][2], unit_x - field["frame"][0] - 6), 4)
                field.update(role="指标主值，与右侧独立单位配对，源值“" + original + "”", max_lines=1, input_pattern=r"^(?:T[+-])?[+-]?[0-9]+(?:[.,][0-9]+)?[+%]?$", max_length=max(1, math.ceil(field["frame"][2] / (size * .45))))
                sample = "0"
            if record["ref"] in pairs.values():
                field.update(role="指标单位，与左侧数值配对，源单位“" + original + "”", max_lines=1, max_length=4, input_pattern=r"^[^\r\n]+$")
                sample = "项"
        values[record["key"]] = sample
    geometry = f"templates/source-geometry/{group}-{number:02d}.svg"
    target = TEMPLATE / geometry
    target.parent.mkdir(parents=True, exist_ok=True)
    ET.indent(root, space="  ")
    ET.register_namespace("", NS)
    target.write_text(ET.tostring(root, encoding="unicode") + "\n", encoding="utf-8")
    source_id = f"{group}-{number:02d}"
    semantic = next(row for row in read(RESEARCH / "source-page-semantics.json")["pages"] if row["source_id"] == source_id)
    semantics = [semantic["title_or_source_labels"], semantic["observed_relation"], semantic["reporting_scenarios"], semantic["parameterization_notes"]]
    source_name = COLLECTIONS[group][0]
    return {
        "id": f"page-{number:02d}", "renderer": "source-diagram", "capacity": len(fields),
        "text_height_factor": 1.25,
        "layout_key": f"source-{group}-{number:02d}", "prototype": f"source-{group}-{number:02d}.svg",
        "geometry": geometry, "source_transform": [round(scale, 8), 0, 0, round(scale, 8), round(dx, 8), round(dy, 8)],
        "source_page": f"{source_name}#{number}", "source_svg_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "source_id": source_id, "page_type": semantic["page_type"], "label": display_title(semantic),
        "source_bounds": [left, top, right - left, bottom - top],
        "title_source_ref": title["ref"] if title else None,
        "title_source_text": title["text"] if title else None,
        "global_metadata_bindings": metadata,
        "description": semantics[1] if semantics else COLLECTIONS[group][2] + f"，原第{number}页完整结构",
        "scenarios": semantics[2] if len(semantics) > 2 else "依据预览中的节点、方向与层次组织材料。",
        "preservation": semantics[3] if len(semantics) > 3 else "保留原图节点、分面、连接与分组。",
        "geometry_use": "qualitative-fixed", "removed_decorative_refs": removed,
        "clipped_source_paths": clipped,
        "ornament_conversions": ornaments,
        "fields": fields,
        "image_slots": visual_slots, "retained_source_images": retained_images,
        "chart_slots": chart_slots,
        "original_textbox_refs": sorted(reference for (page_id, reference) in source_metadata() if page_id == source_id),
        "prototype_content": {"title": display_title(semantic), "nodes": values, **({"charts": {key: {"title": "变化趋势", "axis_title": "指标", "unit": "", "categories": ["阶段一", "阶段二", "阶段三"], "series": [{"name": "指标", "values": [0, 0, 0]}], "chart_type": "line", "show_legend": False, "show_data_labels": False} for key in chart_slots}} if chart_slots else {})},
    }


def install_tokens():
    path = TEMPLATE / "templates/tokens.json"
    tokens = read(path)
    schema_path = TEMPLATE / "templates/tokens.schema.json"
    schema = read(schema_path)
    for role, size in {"diagramCompact": 14, "diagramMicro": 12}.items():
        tokens["font"]["sizes"][role] = size
        tokens["font"]["weights"][role] = 400
        tokens["font"]["lineHeight"][role] = 1.2
        for key in ("sizes", "weights", "lineHeight"):
            spec = schema["properties"]["font"]["properties"][key]
            spec["properties"][role] = copy.deepcopy(spec["properties"]["caption"])
    write(path, tokens)
    write(schema_path, schema)
    return tokens


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot", action="store_true")
    args = parser.parse_args()
    from playwright.sync_api import sync_playwright
    tokens = install_tokens()
    catalog_path = TEMPLATE / "templates/page-catalog.json"
    catalog = read(catalog_path)
    pages_path = TEMPLATE / "templates/pages.schema.json"
    pages = read(pages_path)
    base_schema = copy.deepcopy(catalog["families"]["hub"]["content_schema"])
    common = {key: base_schema["properties"][key] for key in ("title", "section_name", "source")}
    with sync_playwright() as driver:
        browser = driver.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 720})
        for group, (name, count, purpose) in COLLECTIONS.items():
            numbers = {"house": [2], "architecture": [12], "spatial": [18], "circular": [12]}[group] if args.pilot else range(1, count + 1)
            variants = {f"page-{number:02d}": compile_page(group, number, page, tokens) for number in numbers}
            family_id = "source-" + group
            catalog["families"][family_id] = {
                "label": name, "purpose": purpose, "type": "定性关系图", "capability_id": family_id,
                "source": name + "，逐页结构见variants与来源索引", "scenarios": "按原文件名索引、逐页预览和结构说明选择关系图。",
                "relations": "节点归属、层次、支撑或方向以原图几何表达，逐variant说明。",
                "usage_notes": ["固定分面、扇区、圆环和立体几何用于定性关系。实际数量比较或占比应选择由数据计算几何的chart家族。", "diagramCompact为14px、diagramMicro为12px，限密集体系总览或附录的局部标签。关键判断使用全局标题和正常正文字阶。源图的所有文本框各有独立字段，实际输入同时接受长度和字体框体测量。"],
                "array_key": None, "default_variant": next(iter(variants)),
                "content_schema": {"type": "object", "properties": {**common, "nodes": {"type": "object", "additionalProperties": {"type": "string"}}, "visuals": {"type": "object"}, "charts": {"type": "object"}}, "required": ["title", "nodes"], "additionalProperties": False},
                "prototype_content": {"title": purpose, "nodes": {}},
                "config_fields": ["show_source", "show_page_number", "image_fit", "image_position"], "variants": variants,
            }
            families = pages["properties"]["pages"]["items"]["properties"]["family"]["enum"]
            if family_id not in families:
                families.append(family_id)
            print(group, len(variants), sum(len(variant["fields"]) for variant in variants.values()), flush=True)
        browser.close()
    catalog["revision"] = 4
    write(catalog_path, catalog)
    write(pages_path, pages)


if __name__ == "__main__":
    main()
