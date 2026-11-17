"""Lower measured presentation scene objects to the existing native SVG contract."""
from __future__ import annotations

import copy
import hashlib
import json
import math
from pathlib import Path
import re
from xml.etree import ElementTree as ET

from report_ppt import SVG_NS, TemplateInputError
from presentation_typography import ANCHORS, measure_text_block, resolve_text_style, source_line_ranges


def runtime_helpers():
    """Use the same runtime identity check as native export before importing helpers."""
    import ppt_runtime
    ppt_runtime._engine_modules()
    from text_measure import wrap_text
    from svg_to_pptx.drawingml.text_baseline import drawingml_text_baseline_offset
    from pptx_to_svg.preset_authoring import render_preset_shape_fragment
    from svg_to_pptx.native_objects.chart_data import validate_chart_payload
    return wrap_text, drawingml_text_baseline_offset, render_preset_shape_fragment, validate_chart_payload


def number(value, label, minimum=None):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise TemplateInputError(f"{label}: expected a finite number")
    if minimum is not None and value < minimum:
        raise TemplateInputError(f"{label}: expected at least {minimum}")
    return float(value)


def frame(value, label, canvas, allow_zero=False):
    if not isinstance(value, list) or len(value) != 4:
        raise TemplateInputError(f"{label}: frame must be [x,y,width,height]")
    x, y, width, height = [number(v, label) for v in value]
    minimum = 0 if allow_zero else .000001
    if width < minimum or height < minimum or min(x, y) < 0 or x + width > canvas[0] + .01 or y + height > canvas[1] + .01:
        raise TemplateInputError(f"{label}: frame lies outside the canvas or has invalid dimensions")
    return x, y, width, height


def svg_node(tag, attrs=None, parent=None):
    result = ET.Element(f"{{{SVG_NS}}}{tag}", {k: str(v) for k, v in (attrs or {}).items()})
    if parent is not None:
        parent.append(result)
    return result


def scene_contracts():
    """Return the same property contracts enforced by SceneRenderer.element."""
    common = {"id", "type", "metadata", "source_ref", "content_ref", "relation_ref", "role", "opacity"}
    fields = {
        "text":{"frame","text","runs","style","max_lines","rotation"},
        "shape":{"shape","frame","fill","stroke","stroke_width","rotation","d","rx"},
        "chart":{"frame","chart_type","categories","series","style","axes","show_legend","data_labels","plot_padding","hole_size","text_roles","asset","data","options"},
        "image":{"frame","path","fit","position","alt"},
        "connector":{"from","to","from_port","to_port","stroke","stroke_width","preset","arrow"},
        "group":{"children"},
    }
    return {kind: {"common": sorted(common), "fields": sorted(values)} for kind, values in fields.items()}


class SceneRenderer:
    """A page-local renderer with source mappings and measured editable text units."""

    def __init__(self, page, tokens, asset_root, resolve_text, resolve_value, facts):
        self.page, self.tokens = page, tokens
        self.asset_root_raw = Path(asset_root).absolute() if asset_root else None
        self.asset_root = self.asset_root_raw.resolve() if self.asset_root_raw else None
        self.resolve_text, self.resolve_value, self.facts = resolve_text, resolve_value, facts
        self.canvas = (tokens["canvas"]["width"], tokens["canvas"]["height"])
        self.helpers = runtime_helpers()
        self.assets, self.mapping = {}, []
        self.objects = {}
        self._index(page.get("elements", []), None)
        self.source_ids = {identifier: index + 100 for index, identifier in enumerate(self.objects)}

    def _index(self, elements, parent):
        if not isinstance(elements, list):
            raise TemplateInputError("elements and children must be arrays")
        for item in elements:
            if not isinstance(item, dict) or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_.:-]*", str(item.get("id", ""))):
                raise TemplateInputError("scene object id must be a stable SVG-compatible identifier")
            if item["id"] in self.objects:
                raise TemplateInputError(f"duplicate scene id: {item['id']}")
            self.objects[item["id"]] = (item, parent)
            if item.get("type") == "group":
                self._index(item.get("children", []), item["id"])

    def color(self, value):
        if value == "none":
            return value
        if isinstance(value, str) and re.fullmatch(r"#[0-9A-Fa-f]{6}", value):
            return value
        from presentation_palette import palette_color
        selected = palette_color(self.tokens, value)
        if selected is not None:
            return selected
        role = self.tokens.get("color", {}).get("roles", {}).get(value, value)
        result = self.tokens.get("theme", {}).get("slots", {}).get(role)
        if result is None:
            raise TemplateInputError(f"unknown color: {value}")
        return result

    def render(self):
        width, height = self.canvas
        root = svg_node("svg", {"width": width, "height": height, "viewBox": f"0 0 {width} {height}",
            "data-pptx-master": "engine-white", "data-pptx-master-name": "Engine White",
            "data-pptx-layout": "engine-" + self.page["id"], "data-pptx-layout-name": "Engine " + self.page["id"]})
        svg_node("rect", {"id": "engine-background", "x": 0, "y": 0, "width": width, "height": height,
            "fill": "#FFFFFF", "data-pptx-layer": "master"}, root)
        self.definitions = svg_node("defs", parent=root)
        background = self.page.get("background", "#FFFFFF")
        if background != "#FFFFFF":
            svg_node("rect", {"id": "page-background", "x": 0, "y": 0, "width": width, "height": height,
                "fill": self.color(background)}, root)
        for item in self.page.get("elements", []):
            root.append(self.element(item))
        inline_content = [(node,node.text,node.tail) for text in root.iter(f"{{{SVG_NS}}}text") for node in text.iter()]
        ET.indent(root, space="  ")
        for node, text, tail in inline_content:
            node.text, node.tail = text, tail
        return ET.tostring(root, encoding="unicode") + "\n", self.mapping, self.assets

    def element(self, raw):
        item = self.resolve_value(raw, self.facts)
        kind = item.get("type")
        handlers = {"text": self.text, "shape": self.shape, "chart": self.chart,
                    "image": self.image, "connector": self.connector, "group": self.group}
        if kind not in handlers:
            raise TemplateInputError(f"{item['id']}: unsupported scene type {kind!r}")
        definition = scene_contracts()[kind]
        common, fields = set(definition["common"]), {kind: set(definition["fields"])}
        unknown = set(item) - common - fields[kind]
        if unknown:
            raise TemplateInputError(f"{item['id']}: unsupported {kind} fields {sorted(unknown)}")
        result = handlers[kind](item)
        if "opacity" in item:
            opacity = number(item["opacity"], item["id"] + ".opacity", 0)
            if opacity > 1:
                raise TemplateInputError(f"{item['id']}: opacity must be between zero and one")
            opacity_target = result[0] if kind == "text" and result.tag.rsplit("}",1)[-1] == "g" else result
            opacity_target.set("opacity", str(opacity))
        result.set("data-pptx-shape-name", item["id"])
        self.mapping.append({"author_id": item["id"], "page_id": self.page["id"], "svg_id": item["id"],
            "kind": kind, "frame": item.get("frame"), "source_shape_id": self.source_ids[item["id"]]})
        metadata = item.get("metadata", {})
        component_keys = ("component", "component_contract", "component_frame")
        if isinstance(metadata, dict) and all(key in metadata for key in component_keys):
            self.mapping[-1]["component"] = {key: metadata[key] for key in component_keys}
        return result

    def identity(self, item):
        return {"id": item["id"], "data-pptx-shape-id": self.source_ids[item["id"]], "data-pptx-shape-scope": "slide"}

    def text(self, item):
        x, y, width, height = frame(item.get("frame"), item["id"], self.canvas)
        semantic_role = item.get("role", "body")
        known_roles = {*self.tokens["font"]["sizes"], *self.tokens["font"].get("textStyles", {})}
        role = semantic_role if semantic_role in known_roles else "body"
        try:
            style = resolve_text_style(self.tokens, role, item.get("style"))
        except ValueError as exc:
            raise TemplateInputError(f"{item['id']}: {exc}") from exc
        size, weight, family = style["font_size"], str(style["weight"]), style["font_family"]
        leading, align = style["line_height"], style["align"]
        left, top, right, bottom = style["insets"]
        content_width, content_height = width - left - right, height - top - bottom
        if min(content_width, content_height) <= 0:
            raise TemplateInputError(f"{item['id']}: text insets consume its frame")
        runs = item.get("runs", [{"text": item.get("text", "")}])
        if not isinstance(runs, list) or any(not isinstance(run, dict) or "text" not in run for run in runs):
            raise TemplateInputError(f"{item['id']}: runs must contain text objects")
        if not runs or any(set(run)-{"text","weight","color"} for run in runs):
            raise TemplateInputError(f"{item['id']}: each text run supports text, weight and color")
        resolved_runs = [{**run, "text": self.resolve_text(run["text"], self.facts)} for run in runs]
        value = "".join(run["text"] for run in resolved_runs).replace("\r\n", "\n").replace("\r", "\n")
        run_weights = [resolve_text_style(self.tokens, role, {"weight": run.get("weight", weight)})["weight"] for run in resolved_runs]
        try:
            layout = measure_text_block(value, content_width, {**style, "weight": max(run_weights)}, self.helpers)
        except ValueError as exc:
            raise TemplateInputError(f"{item['id']}: {exc}") from exc
        lines, widths, line_ranges = layout["lines"], layout["widths"], layout["ranges"]
        maximum_lines = item.get("max_lines")
        if maximum_lines is not None and (type(maximum_lines) is not int or maximum_lines < 1):
            raise TemplateInputError(f"{item['id']}: max_lines must be a positive integer")
        measured_height = layout["height"]
        if value and (measured_height > content_height + .5 or item.get("max_lines") is not None and len(lines) > item["max_lines"]):
            raise TemplateInputError(f"{item['id']}: measured text {len(lines)} lines/{measured_height:.1f}px exceeds frame height {content_height:g}")
        vertical_offset = {"top": 0, "middle": (content_height - measured_height) / 2,
                           "bottom": content_height - measured_height}[style["vertical_anchor"]]
        content_x, content_y = x + left, y + top + vertical_offset
        anchor = {"left": "start", "center": "middle", "right": "end"}[align]
        tx = content_x if align == "left" else content_x + content_width / 2 if align == "center" else content_x + content_width
        attrs = {**self.identity(item), "x": tx, "y": content_y + layout["baselines"][0], "font-family": family,
            "font-size": size, "font-weight": weight, "fill": self.color(style.get("color", "text")),
            "text-anchor": anchor, "data-pptx-carrier": "true", "data-pptx-frame": f"{x:g} {y:g} {width:g} {height:g}",
            "data-pptx-text-baseline": "metrics-v1", "data-paragraph-line-height": size * leading,
            "data-htr-text-insets": " ".join(f"{value:g}" for value in style["insets"]),
            "data-htr-vertical-anchor": ANCHORS[style["vertical_anchor"]], "data-htr-text-role": role,
            "data-htr-semantic-role": semantic_role,
            "data-htr-style-overrides": json.dumps(item.get("style", {}), ensure_ascii=False),
            "data-htr-resolved-style": json.dumps(style, ensure_ascii=False)}
        attrs["{http://www.w3.org/XML/1998/namespace}space"] = "preserve"
        result = svg_node("text", attrs)
        char_styles = []
        for run in resolved_runs:
            normalized = run["text"].replace("\r\n", "\n").replace("\r", "\n")
            char_styles.extend((run, char) for char in normalized)
        for index, (line,(start,end)) in enumerate(zip(lines,line_ranges)):
            line_node = svg_node("tspan", {"x": tx, "y": content_y + layout["baselines"][index]}, result)
            if index and index in layout["paragraph_starts"]:
                line_node.set("data-paragraph-space-before", str(style["paragraph_gap"]))
            elif index:
                line_node.set("data-paragraph-line-break", "1")
            if not line:
                continue
            fragment = char_styles[start:end]
            current, buffer = None, ""
            for run, char in fragment:
                signature = (str(resolve_text_style(self.tokens, role, {"weight": run.get("weight", weight)})["weight"]), self.color(run.get("color", style.get("color", "text"))))
                if current is not None and current != signature:
                    svg_node("tspan", {"font-weight": current[0], "fill": current[1]}, line_node).text = buffer
                    buffer = ""
                current, buffer = signature, buffer + char
            if current is not None:
                svg_node("tspan", {"font-weight": current[0], "fill": current[1]}, line_node).text = buffer
        if item.get("rotation"):
            angle = number(item["rotation"], item["id"] + ".rotation")
            result.set("transform", f"rotate({angle:g} {x + width/2:g} {y + height/2:g})")
        if self.objects[item["id"]][1] is not None:
            # Nested native groups use the existing controlled paragraph path.
            # Template placeholder metadata belongs to direct SVG root children.
            result.attrib.pop("data-pptx-carrier")
            for index, span in enumerate(result):
                span.attrib.pop("y", None)
                span.set("dy", "0" if index == 0 else str(layout["baselines"][index] - layout["baselines"][index-1]))
            return result
        wrapper = svg_node("g", {"id":"slot-" + item["id"], "data-pptx-placeholder":"body",
            "data-pptx-idx":self.source_ids[item["id"]], "data-pptx-bounds":f"{x:g} {y:g} {width:g} {height:g}"})
        wrapper.append(result)
        return wrapper

    def shape(self, item):
        kind = item.get("shape", "rect")
        x, y, width, height = frame(item.get("frame"), item["id"], self.canvas, allow_zero=kind == "line")
        style = {"fill": self.color(item.get("fill", "none")), "stroke": self.color(item.get("stroke", "none")),
                 "stroke-width": number(item.get("stroke_width", 1), item["id"] + ".stroke_width", 0)}
        if style["stroke"] == "none":
            # Registered DrawingML presets reject stroke attributes without a
            # visible stroke. Filled presets are valid, including layout surfaces.
            style.pop("stroke-width")
        attrs = {**self.identity(item), **style}
        if kind in {"rect", "roundRect"}:
            radius = number(item.get("rx", 8 if kind == "roundRect" else 0), item["id"] + ".rx", 0)
            result = svg_node("rect", {**attrs, "x": x, "y": y, "width": width, "height": height,
                "rx": radius})
        elif kind == "ellipse":
            result = svg_node("ellipse", {**attrs, "cx": x + width/2, "cy": y + height/2, "rx": width/2, "ry": height/2})
        elif kind == "line":
            result = svg_node("line", {**attrs, "x1": x, "y1": y, "x2": x + width, "y2": y + height})
        elif kind == "path":
            if not isinstance(item.get("d"), str) or not item["d"].strip():
                raise TemplateInputError(f"{item['id']}: path requires d")
            result = svg_node("path", {**attrs, "d": item["d"]})
        else:
            fragment = self.helpers[2](kind, (x, y, width, height), element_id=item["id"], style={k: str(v) for k,v in style.items()})
            result = ET.fromstring(fragment)
            result.attrib.update({key: str(value) for key, value in self.identity(item).items()})
        if item.get("rotation"):
            result.set("transform", f"rotate({number(item['rotation'], 'rotation'):g} {x+width/2:g} {y+height/2:g})")
        return result

    def image(self, item):
        x, y, width, height = frame(item.get("frame"), item["id"], self.canvas)
        if self.asset_root is None or not isinstance(item.get("path"), str):
            raise TemplateInputError(f"{item['id']}: image requires a local asset root and path")
        source = (self.asset_root / item["path"]).resolve()
        supplied = Path(item["path"])
        if supplied.is_absolute() or ".." in supplied.parts:
            raise TemplateInputError(f"{item['id']}: image path must be relative to assets root")
        raw_source = self.asset_root_raw / supplied
        for candidate in (raw_source, *raw_source.parents):
            if candidate.exists() or candidate.is_symlink():
                if candidate.is_symlink() or getattr(candidate.lstat(), "st_file_attributes", 0) & 0x400:
                    raise TemplateInputError(f"{item['id']}: linked image paths are unsupported")
        if not source.is_relative_to(self.asset_root) or not source.is_file() or source.is_symlink():
            raise TemplateInputError(f"{item['id']}: image must be a local file below assets root")
        data = source.read_bytes()
        relative = "images/" + hashlib.sha256(data).hexdigest()[:24] + source.suffix.lower()
        self.assets[relative] = data
        fit, position = item.get("fit", "contain"), item.get("position", "xMidYMid")
        if fit not in {"contain", "cover"} or position not in {f"x{x}Y{y}" for x in ("Min", "Mid", "Max") for y in ("Min", "Mid", "Max")}:
            raise TemplateInputError(f"{item['id']}: invalid image fit or position")
        result = svg_node("image", {**self.identity(item), "x": x, "y": y, "width": width, "height": height,
            "href": "../" + relative, "preserveAspectRatio": position + (" meet" if fit == "contain" else " slice")})
        svg_node("desc", parent=result).text = self.resolve_text(item.get("alt", ""), self.facts)
        return result

    def connector(self, item):
        endpoints = []
        from pptx_shapes import get_preset_registry
        for key in ("from", "to"):
            target, parent = self.objects.get(item.get(key), (None, None))
            if target is None or target.get("type") != "shape":
                raise TemplateInputError(f"{item['id']}: {key} must name a shape on this page")
            if parent != self.objects[item["id"]][1]:
                raise TemplateInputError(f"{item['id']}: connector and endpoints must share a group scope")
            port = item.get(key + "_port", "right" if key == "from" else "left")
            if port not in {"top","left","bottom","right"}:
                raise TemplateInputError(f"{item['id']}: invalid connector port")
            x, y, width, height = frame(target["frame"], target["id"], self.canvas)
            points = {"top": (x+width/2,y), "left": (x,y+height/2), "bottom": (x+width/2,y+height), "right": (x+width,y+height/2)}
            preset = target.get("shape","rect")
            if preset in {"path","line"}:
                raise TemplateInputError(f"{item['id']}: path and line endpoints need an explicit supported connection shape")
            geometry = get_preset_registry().evaluate(preset,width,height)
            if not geometry.connections:
                raise TemplateInputError(f"{item['id']}: target preset has no connection sites")
            point = points[port]
            site, connection = min(enumerate(geometry.connections), key=lambda indexed:
                (x+indexed[1].position.x-point[0])**2+(y+indexed[1].position.y-point[1])**2)
            point = (x+connection.position.x,y+connection.position.y)
            if target.get("rotation"):
                angle=math.radians(number(target["rotation"],target["id"]+".rotation"))
                dx,dy=point[0]-x-width/2,point[1]-y-height/2
                point=(x+width/2+dx*math.cos(angle)-dy*math.sin(angle),y+height/2+dx*math.sin(angle)+dy*math.cos(angle))
            endpoints.append((point, self.source_ids[target["id"]], site))
        (start, start_id, start_site), (end, end_id, end_site) = endpoints
        x, y = min(start[0],end[0]), min(start[1],end[1])
        width, height = abs(end[0]-start[0]), abs(end[1]-start[1])
        preset = item.get("preset", "line")
        style = {"fill":"none", "stroke":self.color(item.get("stroke", "primary")),
                 "stroke-width":str(number(item.get("stroke_width",2),"stroke_width",.01))}
        if preset == "line":
            result = svg_node("line", {**self.identity(item), **style, "x1":start[0], "y1":start[1],
                "x2":end[0], "y2":end[1], "data-pptx-object":"connector", "data-pptx-prst":"line",
                "data-pptx-frame":f"{x:g} {y:g} {width:g} {height:g}"})
        else:
            fragment = self.helpers[2](preset, (x,y,width,height), element_id=item["id"], object_kind="connector", style=style)
            result = ET.fromstring(fragment)
            result.attrib.update({key: str(value) for key, value in self.identity(item).items()})
            if end[0] < start[0] or end[1] < start[1]:
                sx, sy = (-1 if end[0] < start[0] else 1), (-1 if end[1] < start[1] else 1)
                result.set("transform", f"translate({2*x+width if sx<0 else 0:g} {2*y+height if sy<0 else 0:g}) scale({sx} {sy})")
        result.set("data-pptx-start-shape-id", str(start_id))
        result.set("data-pptx-start-site", str(start_site))
        result.set("data-pptx-end-shape-id", str(end_id))
        result.set("data-pptx-end-site", str(end_site))
        if item.get("arrow"):
            if preset != "line":
                raise TemplateInputError(f"{item['id']}: arrow markers currently require a straight connector")
            marker_id = "engine-arrow-" + style["stroke"].lstrip("#")
            if not any(child.get("id") == marker_id for child in self.definitions):
                marker = svg_node("marker", {"id":marker_id, "markerWidth":8, "markerHeight":8,
                    "refX":7, "refY":4, "orient":"auto", "markerUnits":"strokeWidth"}, self.definitions)
                svg_node("path", {"d":"M0 0 L8 4 L0 8 Z", "fill":style["stroke"]}, marker)
            result.set("marker-end", f"url(#{marker_id})")
        return result

    def group(self, item):
        if not item.get("children"):
            raise TemplateInputError(f"{item['id']}: a native group needs visible children")
        result = svg_node("g", {**self.identity(item), "data-pptx-object":"group"})
        for child in item.get("children", []):
            result.append(self.element(child))
        frames = []
        def collect(children):
            for child in children:
                metadata = child.get("metadata", {})
                if child.get("type") == "group" and isinstance(metadata, dict) and "component_contract" in metadata and "component_frame" in metadata:
                    # element(child) has already validated this child's declared outer box.
                    frames.append(frame(metadata["component_frame"], child["id"] + ".component_frame", self.canvas))
                if "frame" in child:
                    frames.append(frame(child["frame"],child["id"],self.canvas,allow_zero=child.get("shape")=="line"))
                collect(child.get("children",[]))
        collect(item["children"])
        if not frames:
            raise TemplateInputError(f"{item['id']}: native group has no measurable child frames")
        left,top=min(f[0] for f in frames),min(f[1] for f in frames)
        right,bottom=max(f[0]+f[2] for f in frames),max(f[1]+f[3] for f in frames)
        metadata = item.get("metadata", {})
        if isinstance(metadata, dict) and "component_contract" in metadata and "component_frame" in metadata:
            if metadata["component_contract"] != "0.1":
                raise TemplateInputError(f"{item['id']}: unsupported component frame contract")
            x, y, width, height = frame(metadata["component_frame"], item["id"] + ".component_frame", self.canvas)
            if left < x - .01 or top < y - .01 or right > x + width + .01 or bottom > y + height + .01:
                raise TemplateInputError(f"{item['id']}: declared component frame does not contain all child frames")
            left, top, right, bottom = x, y, x + width, y + height
        result.set("data-pptx-bounds", f"{left:g} {top:g} {right-left:g} {bottom-top:g}")
        return result

    def chart(self, item):
        return chart_fragment(self, item)


def _plain_text(parent, text, x, y, size, color, anchor="start", family="Arial, Microsoft YaHei", weight=400):
    node = svg_node("text", {"x":x, "y":y, "font-size":size, "font-family":family,
        "fill":color, "text-anchor":anchor, "font-weight":weight}, parent)
    node.text = str(text)


def _role_text(parent, text, x, y, style, anchor="start"):
    _plain_text(parent, text, x, y, style["font_size"], style["color"], anchor,
                style["font_family"], style["weight"])


def _pie_fragment(renderer, item, categories, series, style, bounds, text_styles):
    """Render a nonnegative composition using the existing native pie backend."""
    x, y, width, height = bounds
    if len(series) != 1 or any(value is None or value < 0 for value in series[0]["values"]):
        raise TemplateInputError(f"{item['id']}: pie and doughnut require one nonnegative series without null gaps")
    values = series[0]["values"]
    total = number(sum(values), item["id"] + ".total", 0)
    if total == 0:
        raise TemplateInputError(f"{item['id']}: pie and doughnut require a positive total")
    if item.get("axes", {}) != {}:
        raise TemplateInputError(f"{item['id']}: pie and doughnut do not accept axes")
    for source in (item, series[0]):
        labels = source.get("data_labels")
        if labels is not None and labels is not False:
            raise TemplateInputError(f"{item['id']}: pie-family native data_labels are unsupported; use separate editable text")
    hole = None
    if item["chart_type"] == "doughnut":
        hole = number(item.get("hole_size", 75), item["id"] + ".hole_size", 10)
        if hole > 90 or not hole.is_integer():
            raise TemplateInputError(f"{item['id']}: hole_size must be an integer from 10 to 90")
    palette = [renderer.color(series[0]["color"])] if "color" in series[0] else style["colors"]
    colors = series[0].get("point_colors") or [palette[index % len(palette)] for index in range(len(categories))]
    series[0]["point_colors"] = colors
    padding = item.get("plot_padding", [0, 0, 0, 0])
    if not isinstance(padding, list) or len(padding) != 4:
        raise TemplateInputError(f"{item['id']}: plot_padding must be [left,top,right,bottom]")
    left, top, right, bottom = [number(value, "plot_padding", 0) for value in padding]
    legend_width = width * .4 if item.get("show_legend", False) else 0
    diameter = min(width - left - right - legend_width, height - top - bottom)
    if diameter <= 0:
        raise TemplateInputError(f"{item['id']}: plot padding or legend consumes chart frame")
    px = x + left + (width - left - right - legend_width - diameter) / 2
    py = y + top + (height - top - bottom - diameter) / 2
    payload = {"name": item["id"], "type": item["chart_type"], "x": x, "y": y,
               "width": width, "height": height, "categories": categories, "series": series,
               "show_legend": item.get("show_legend", False), "axes": {}, "style": style,
               "data_labels": False, "plot_area": {"x": px, "y": py, "width": diameter, "height": diameter}}
    payload["text_styles"] = {key: text_styles[key] for key in ("base", "legend")}
    if hole is not None:
        payload["hole_size"] = int(hole)
    renderer.helpers[3](payload)
    result = svg_node("g", {"id": item["id"], "data-pptx-replace-with": "chart",
                           "data-pptx-native-authority": "json", "data-pptx-bounds": f"{x:g} {y:g} {width:g} {height:g}"})
    svg_node("metadata", {"type": "application/json"}, result).text = json.dumps(payload, ensure_ascii=False)
    svg_node("rect", {"x": x, "y": y, "width": width, "height": height, "fill": style["chart_area_fill"]}, result)
    svg_node("rect", {"x": px, "y": py, "width": diameter, "height": diameter, "fill": style["plot_area_fill"]}, result)
    radius = diameter / 2
    inner_radius = radius * hole / 100 if hole is not None else 0
    cx, cy = px + radius, py + radius
    angle = -math.pi / 2
    for value, color in zip(values, colors):
        sweep = 2 * math.pi * value / total
        if value == total and hole is None:
            svg_node("circle", {"cx": cx, "cy": cy, "r": radius, "fill": color}, result)
        elif value == total:
            path = (f"M {cx:g} {cy-radius:g} A {radius:g} {radius:g} 0 1 1 {cx:g} {cy+radius:g} "
                    f"A {radius:g} {radius:g} 0 1 1 {cx:g} {cy-radius:g} "
                    f"M {cx:g} {cy-inner_radius:g} A {inner_radius:g} {inner_radius:g} 0 1 0 {cx:g} {cy+inner_radius:g} "
                    f"A {inner_radius:g} {inner_radius:g} 0 1 0 {cx:g} {cy-inner_radius:g} Z")
            svg_node("path", {"d": path, "fill": color, "fill-rule": "evenodd"}, result)
        elif value > 0:
            sx, sy = cx + radius * math.cos(angle), cy + radius * math.sin(angle)
            ex, ey = cx + radius * math.cos(angle + sweep), cy + radius * math.sin(angle + sweep)
            if hole is None:
                path = f"M {cx:g} {cy:g} L {sx:g} {sy:g} A {radius:g} {radius:g} 0 {int(sweep > math.pi)} 1 {ex:g} {ey:g} Z"
            else:
                ix, iy = cx + inner_radius * math.cos(angle + sweep), cy + inner_radius * math.sin(angle + sweep)
                jx, jy = cx + inner_radius * math.cos(angle), cy + inner_radius * math.sin(angle)
                path = (f"M {sx:g} {sy:g} A {radius:g} {radius:g} 0 {int(sweep > math.pi)} 1 {ex:g} {ey:g} "
                        f"L {ix:g} {iy:g} A {inner_radius:g} {inner_radius:g} 0 {int(sweep > math.pi)} 0 {jx:g} {jy:g} Z")
            svg_node("path", {"d": path, "fill": color}, result)
        angle += sweep
    if legend_width:
        size = number(style["legend_font_size"], "legend_font_size", 1)
        if len(categories) * size * 1.5 > height - top - bottom:
            raise TemplateInputError(f"{item['id']}: legend exceeds chart height")
        legend_x = x + width - right - legend_width + 8
        for index, (category, color) in enumerate(zip(categories, colors)):
            baseline = y + top + size * (1 + index * 1.5)
            svg_node("rect", {"x": legend_x, "y": baseline - size * .75, "width": size * .65, "height": size * .65, "fill": color}, result)
            _plain_text(result, category, legend_x + size, baseline, size, text_styles["legend"]["color"], family=text_styles["legend"]["font_family"], weight=text_styles["legend"]["weight"])
    return result


def chart_fragment(renderer, item):
    """Generate one editable chart and a fallback from the same data and scale."""
    if "asset" in item:
        from presentation_chart_assets import render_chart_asset
        return render_chart_asset(renderer, item)
    x, y, width, height = frame(item.get("frame"), item["id"], renderer.canvas)
    kind = item.get("chart_type", "column")
    if kind not in {"bar", "column", "line", "pie", "doughnut"}:
        raise TemplateInputError(f"{item['id']}: chart_type must be bar, column, line, pie or doughnut")
    if "hole_size" in item and kind != "doughnut":
        raise TemplateInputError(f"{item['id']}: hole_size applies to doughnut only")
    categories, series = item.get("categories"), copy.deepcopy(item.get("series"))
    if not isinstance(categories, list) or not categories or not isinstance(series, list) or not series:
        raise TemplateInputError(f"{item['id']}: chart requires categories and series")
    for entry in series:
        if not isinstance(entry, dict) or len(entry.get("values", [])) != len(categories):
            raise TemplateInputError(f"{item['id']}: series values must match categories")
        for value in entry["values"]:
            if value is not None:
                number(value, item["id"] + ".values")
        if entry.get("point_colors") is not None:
            if len(entry["point_colors"]) != len(categories):
                raise TemplateInputError(f"{item['id']}: point_colors must match categories")
            entry["point_colors"] = [renderer.color(value) for value in entry["point_colors"]]
    values = [value for entry in series for value in entry["values"] if value is not None]
    if not values:
        raise TemplateInputError(f"{item['id']}: chart needs at least one numeric value")
    if not isinstance(item.get("style",{}),dict):
        raise TemplateInputError(f"{item['id']}: chart style must be an object")
    roles = {"base": "body", "axis": "caption", "legend": "caption", "data_label": "caption"}
    declared_roles = item.get("text_roles", {})
    if not isinstance(declared_roles, dict) or set(declared_roles) - set(roles):
        raise TemplateInputError(f"{item['id']}: unsupported chart text_roles")
    roles.update(declared_roles)
    text_styles = {}
    for purpose, role in roles.items():
        overrides = {key: value for key, value in item.get("style", {}).items() if key == "font_family"}
        size_key = {"axis": "axis_font_size", "legend": "legend_font_size"}.get(purpose)
        if size_key in item.get("style", {}):
            overrides["font_size"] = item["style"][size_key]
        if purpose == "data_label" and isinstance(item.get("data_labels"), dict) and "font_size" in item["data_labels"]:
            overrides["font_size"] = item["data_labels"]["font_size"]
        if "text_color" in item.get("style", {}):
            overrides["color"] = item["style"]["text_color"]
        if purpose == "data_label" and isinstance(item.get("data_labels"), dict):
            overrides.update({key: item["data_labels"][key] for key in ("font_family", "color") if key in item["data_labels"]})
        text_styles[purpose] = resolve_text_style(renderer.tokens, role, overrides)
        text_styles[purpose]["color"] = renderer.color(text_styles[purpose]["color"])
    default_colors = [renderer.color(f"accent{index}") for index in range(1, 7)] if kind in {"pie", "doughnut"} else [renderer.color("primary"), renderer.color("accent2")]
    style = {"colors":default_colors,
        "font_family":text_styles["base"]["font_family"], "axis_font_size":text_styles["axis"]["font_size"], "legend_font_size":text_styles["legend"]["font_size"],
        "text_color":text_styles["base"]["color"], "axis_color":"#CCD6E0", "grid_color":"#E8EDF2",
        "chart_area_fill":"#FFFFFF", "plot_area_fill":"#FFFFFF", **item.get("style", {})}
    if set(item.get("style",{})) - {"colors","font_family","axis_font_size","legend_font_size","text_color","axis_color","grid_color","chart_area_fill","plot_area_fill"}:
        raise TemplateInputError(f"{item['id']}: unsupported chart style fields")
    style["colors"] = [renderer.color(value) for value in style["colors"]]
    for key in ("chart_area_fill", "plot_area_fill"):
        style[key] = renderer.color("none" if style[key] == "transparent" else style[key])
    if not style["colors"]:
        raise TemplateInputError(f"{item['id']}: chart needs at least one color")
    if kind in {"pie", "doughnut"}:
        return _pie_fragment(renderer, item, categories, series, style, (x, y, width, height), text_styles)
    style["colors"] = [renderer.color(entry.get("color",style["colors"][index%len(style["colors"])])) for index,entry in enumerate(series)]
    axes = copy.deepcopy(item.get("axes", {}))
    value_axis = axes.setdefault("value", {})
    minimum = number(value_axis.get("minimum", min(0,min(values))), "chart minimum")
    maximum = number(value_axis.get("maximum", max(1,max(values)) * 1.15), "chart maximum")
    if minimum >= maximum or min(values) < minimum or max(values) > maximum:
        raise TemplateInputError(f"{item['id']}: chart domain must contain all data values")
    if kind in {"bar", "column"} and not minimum <= 0 <= maximum:
        raise TemplateInputError(f"{item['id']}: bar and column domains must contain zero")
    value_axis.update({"minimum":minimum, "maximum":maximum})
    category_axis = axes.setdefault("category", {})
    axis_text_styles = {}
    for name, axis in (("value", value_axis), ("category", category_axis)):
        local = {key: axis[key] for key in ("font_size", "font_family", "color") if key in axis}
        axis_text_styles[name] = resolve_text_style(renderer.tokens, roles["axis"], {**text_styles["axis"], **local})
        axis_text_styles[name]["color"] = renderer.color(axis_text_styles[name]["color"])
    if kind == "bar":
        category_axis.setdefault("reverse", True)
    padding = item.get("plot_padding", [150,16,70,36] if kind == "bar" else [60,20,26,62])
    if not isinstance(padding, list) or len(padding) != 4:
        raise TemplateInputError(f"{item['id']}: plot_padding must be [left,top,right,bottom]")
    left, top, right, bottom = [number(v, "plot_padding", 0) for v in padding]
    px, py, pw, ph = x+left, y+top, width-left-right, height-top-bottom
    if min(pw,ph) <= 0:
        raise TemplateInputError(f"{item['id']}: plot padding consumes chart frame")
    labels = item.get("data_labels", {"show_value":True, "font_size":text_styles["data_label"]["font_size"], "position":"outEnd" if kind != "line" else "above"})
    if labels is False:
        labels = {"show_value":False}
    if not isinstance(labels, dict):
        raise TemplateInputError(f"{item['id']}: data_labels must be a dict or false")
    payload = {"name":item["id"], "type":kind, "x":x, "y":y, "width":width, "height":height,
        "categories":categories, "series":series, "show_legend":item.get("show_legend",False),
        "axes":axes, "style":style, "data_labels":labels, "text_styles": text_styles,
        "plot_area":{"x":px,"y":py,"width":pw,"height":ph}}
    renderer.helpers[3](payload)
    result = svg_node("g", {"id":item["id"], "data-pptx-replace-with":"chart",
        "data-pptx-native-authority":"json", "data-pptx-bounds":f"{x:g} {y:g} {width:g} {height:g}"})
    svg_node("metadata", {"type":"application/json"}, result).text = json.dumps(payload, ensure_ascii=False)
    svg_node("rect", {"x":x,"y":y,"width":width,"height":height,"fill":style["chart_area_fill"]},result)
    if style["plot_area_fill"] != style["chart_area_fill"]:
        svg_node("rect", {"x":px,"y":py,"width":pw,"height":ph,"fill":style["plot_area_fill"]}, result)
    size = number(style["axis_font_size"], "axis_font_size",1)
    text_color = renderer.color(style["text_color"])
    value_visible = value_axis.get("visible",True)
    category_visible = category_axis.get("visible",True)
    if value_visible:
        for index in range(5):
            value = minimum + (maximum-minimum)*index/4
            if kind == "bar":
                axis_x = px + pw*index/4
                svg_node("line",{"x1":axis_x,"y1":py,"x2":axis_x,"y2":py+ph,"stroke":style["grid_color"]},result)
                _role_text(result,f"{value:g}",axis_x,py+ph+size*1.4,axis_text_styles["value"],"middle")
            else:
                axis_y = py+ph-ph*index/4
                svg_node("line",{"x1":px,"y1":axis_y,"x2":px+pw,"y2":axis_y,"stroke":style["grid_color"]},result)
                _role_text(result,f"{value:g}",px-8,axis_y+size*.3,axis_text_styles["value"],"end")
    count = len(categories)
    band = (ph if kind == "bar" else pw)/count
    baseline = (px + pw*(0-minimum)/(maximum-minimum)) if kind == "bar" else (py+ph-ph*(0-minimum)/(maximum-minimum))
    for index, category in enumerate(categories):
        if category_visible:
            if kind == "bar":
                order = index if category_axis.get("reverse",True) else count-1-index
                _role_text(result,category,px-12,py+(order+.5)*band+size*.3,axis_text_styles["category"],"end")
            else:
                _role_text(result,category,px+(index+.5)*band,py+ph+size*1.6,axis_text_styles["category"],"middle")
    for series_index, entry in enumerate(series):
        points = []
        for index, value in enumerate(entry["values"]):
            if value is None:
                if points:
                    svg_node("polyline",{"points":" ".join(points),"fill":"none","stroke":style["colors"][series_index%len(style["colors"])]},result)
                    points=[]
                continue
            color = entry.get("point_colors", [style["colors"][series_index%len(style["colors"])]]*count)[index]
            size_label = number(labels.get("font_size",size),"data label font size",1)
            if kind == "bar":
                order = index if category_axis.get("reverse",True) else count-1-index
                bar_h = band*.64/len(series)
                start = py+order*band+band*.18+series_index*bar_h
                endpoint = px+pw*(value-minimum)/(maximum-minimum)
                if value:
                    svg_node("rect",{"x":min(baseline,endpoint),"y":start,"width":abs(endpoint-baseline),"height":bar_h*.9,"fill":color},result)
                lx=endpoint+8 if value >= 0 else endpoint-8
                ly=start+bar_h*.7
                anchor="start" if value >= 0 else "end"
            else:
                endpoint=py+ph-ph*(value-minimum)/(maximum-minimum)
                if kind == "column":
                    bar_w=band*.64/len(series)
                    start=px+index*band+band*.18+series_index*bar_w
                    if value:
                        svg_node("rect",{"x":start,"y":min(baseline,endpoint),"width":bar_w*.9,"height":abs(endpoint-baseline),"fill":color},result)
                    lx=start+bar_w*.45
                else:
                    lx=px+(index+.5)*band
                    points.append(f"{lx:g},{endpoint:g}")
                ly=endpoint-8 if value >= 0 or kind == "line" else endpoint+size_label
                anchor="middle"
            if labels.get("show_value",False):
                _role_text(result,f"{value:,g}",lx,ly,text_styles["data_label"],anchor)
        if points:
            svg_node("polyline",{"points":" ".join(points),"fill":"none","stroke":style["colors"][series_index%len(style["colors"])],"stroke-width":2.5},result)
    if payload["show_legend"]:
        for index, entry in enumerate(series):
            _role_text(result,entry.get("name",""),x+index*width/len(series),y+height-2,text_styles["legend"])
    return result


