"""Deterministic, measured topology lowering to editable native scene groups.

This is a bounded layout engine, not an arbitrary graph router.  Successful
straight edges are checked against every non-endpoint node's occupied boxes.
"""
from __future__ import annotations

import copy
import math
import re

from presentation_document import resolve_text, resolve_value
from presentation_svg import frame, number, runtime_helpers
from presentation_typography import STYLE_FIELDS, measure_text_block, resolve_text_style
from report_ppt import TemplateInputError, load_template


VERSION = "0.1"
LAYOUTS = ("tree", "layered", "radial", "cycle", "arch")
MAX_NODES = 64
MAX_EDGES = 256
COMMON = {"id", "type", "component", "frame", "metadata", "source_ref", "content_ref", "relation_ref", "role"}
OPTIONS = {"layout", "nodes", "edges", "style", "node_width", "node_height", "node_padding", "node_gap",
           "layer_gap", "padding", "direction", "root_id", "center_id", "arrow", "marker_size", "label_gap", "band", "interior", "variant"}
NODE_FIELDS = {"id", "label", "width", "height", "shape", "fill", "stroke", "style", "role", "marker"}
EDGE_FIELDS = {"id", "from", "to", "arrow", "preset", "label"}
PAINT_FIELDS = {"fill", "stroke", "stroke_width", "marker_fill", "marker_color"}
ID = re.compile(r"[A-Za-z_][A-Za-z0-9_.:-]*\Z")
EPS = .01


class TopologyError(TemplateInputError):
    """A measurable topology failure with machine-readable location and remedy."""

    def __init__(self, message, diagnostic):
        super().__init__(message)
        self.diagnostic = diagnostic


def topology_catalog(name=None, tokens=None):
    """Return the actual supported schema, algorithms, examples and limitations."""
    if name is not None and name not in LAYOUTS:
        raise TemplateInputError(f"unknown topology layout {name!r}")
    if tokens is None:
        _, _, tokens = load_template()
    definitions = {
        "tree": {"purpose": "A rooted directed tree.", "algorithm": "Kahn longest-path ranks; four bounded barycenter sweeps",
                 "constraints": ["one root", "exactly one parent per other node", "connected", "acyclic"]},
        "layered": {"purpose": "A directed acyclic dependency graph.", "algorithm": "Kahn longest-path ranks; four bounded barycenter sweeps",
                    "constraints": ["acyclic", "no isolated nodes unless it is the only node", "long edges may be rejected for node obstruction"]},
        "radial": {"purpose": "A center and variable spokes.", "algorithm": "center plus evenly spaced ellipse angles",
                   "constraints": ["all edges join the center and a spoke", "every spoke connected"]},
        "cycle": {"purpose": "An ordered directed cycle.", "algorithm": "default: evenly spaced ellipse nodes; arrow-ring: measured thick annular arrow segments",
                  "variants": ["default", "arrow-ring"],
                  "constraints": ["at least three nodes (arrow-ring: 3..6)", "explicit edges must follow node order or its reverse"]},
        "arch": {"purpose": "External nodes on an upper elliptical arch with an optional interior layout tree.",
                 "algorithm": "ellipse angles; external labels; maximum-area inner rectangle with clearance",
                 "constraints": ["node markers are ellipses", "optional solid annular band is an editable custom shape, not a connector",
                                 "interior recursively forbids topology", "interior must fit the computed safe rectangle"]},
    }
    examples = {}
    for kind in LAYOUTS:
        nodes = [{"id": "a", "label": "Node A"}, {"id": "b", "label": "Node B"}, {"id": "c", "label": "Node C"}]
        example = {"id": "structure", "type": "component", "component": "topology", "frame": [60, 150, 1160, 510],
                   "layout": kind, "nodes": nodes}
        if kind in {"tree", "layered"}:
            example["edges"] = [{"id": "ab", "from": "a", "to": "b"}, {"id": "ac", "from": "a", "to": "c"}]
        if kind == "arch":
            example["interior"] = {"id": "inside", "type": "column", "gap": 16, "children": [
                {"id": "capability", "type": "leaf", "element": {"type": "text", "role": "heading", "text": "Shared capabilities"}},
                {"id": "foundation", "type": "leaf", "element": {"type": "text", "text": "Common foundation"}}]}
        examples[kind] = example
    selected = [name] if name else list(LAYOUTS)
    return copy.deepcopy({
        "topology_contract": VERSION, "component": "topology", "scene_type": "component",
        "common_required": ["id", "type=component", "component=topology", "frame", "layout", "nodes"],
        "fields": sorted(COMMON | OPTIONS), "node_fields": sorted(NODE_FIELDS), "edge_fields": sorted(EDGE_FIELDS),
        "capacity": {"nodes": [1, MAX_NODES], "edges": [0, MAX_EDGES]},
        "definitions": {key: definitions[key] for key in selected},
        "defaults": {"direction": "down", "node_width": "up to 160px (arch: natural label width capped at 120px)",
                     "node_height": "measured; never shrink font", "node_padding": 12, "node_gap": 20,
                     "layer_gap": 36, "padding": 12, "marker_size": 40, "label_gap": 10, "band": True, "arrow": False},
        "style_fields": sorted(STYLE_FIELDS | PAINT_FIELDS), "text_style": resolve_text_style(tokens, "body"),
        "node_semantics": "width/height are positive explicit sizes; label supports normal fact text bindings; marker is optional short editable text, arch only",
        "direction": ["down", "right"], "padding": "nonnegative number, applied to all four sides",
        "band_fields": ["thickness", "fill", "stroke", "stroke_width"],
        "band_semantics": "arch only; boolean or object; 14px thickness by default; solid theme fill/stroke; no gradient or shadow",
        "variant": {"scope": "cycle only", "default": "default", "arrow-ring": {
            "purpose": "Qualitative closed process; equal angle stages do not encode numeric shares.",
            "capacity": [3, 6], "geometry": "thick solid annular arrows with widened heads; circle fits the allocated frame",
            "labels": "horizontal native text; measured safe rectangle inside each arc body; no font shrinking",
            "colors": "palette categorical order; optional node.fill; automatic contrasting label ink unless explicitly styled",
            "limits": "node_width/node_height, node width/height/shape/stroke and paint style reject; arrows cannot be disabled; no badges or interior",
            "example": {"id": "cycle", "type": "component", "component": "topology", "layout": "cycle", "variant": "arrow-ring",
                        "frame": [100, 140, 600, 510], "nodes": [{"id": "discover", "label": "Discover"}, {"id": "design", "label": "Design"},
                                                               {"id": "verify", "label": "Verify"}, {"id": "improve", "label": "Improve"}]}}},
        "automatic_edges": "radial: first node (or center_id) to every spoke; cycle: node input order closed; tree/layered: explicit edges; arch: none",
        "interior": "arch only: normal row/column/grid/leaf layout root; node IDs are prefixed by topology ID; nested topology is rejected",
        "connectors": {"presets": ["line"], "arrow": "boolean, straight native connectors only", "labels": "not supported; explicit labels reject",
                       "scope": "all endpoints and connectors in the same native group",
                       "routing_check": "straight segments against non-endpoint occupied rectangles; crossings between edges are not removed",
                       "limits": "no obstacle detours, orthogonal routes, edge labels or automatic crossing minimization guarantee"},
        "measurement": "shared DrawingML text estimator; actual PowerPoint rendering remains a separate check",
        "output": "editable native group with topology_report metadata and stable node/edge IDs",
        "examples": {key: examples[key] for key in selected},
    })


def _overlap(a, b, gap=0):
    return (a[0] < b[0] + b[2] + gap - EPS and b[0] < a[0] + a[2] + gap - EPS
            and a[1] < b[1] + b[3] + gap - EPS and b[1] < a[1] + a[3] + gap - EPS)


def _segment_hits_box(start, end, box):
    """Liang-Barsky clipping, excluding tangencies to the rectangle boundary."""
    x, y, width, height = box
    lo, hi = 0., 1.
    dx, dy = end[0] - start[0], end[1] - start[1]
    for origin, delta, minimum, maximum in ((start[0], dx, x + EPS, x + width - EPS),
                                             (start[1], dy, y + EPS, y + height - EPS)):
        if abs(delta) < 1e-12:
            if not minimum < origin < maximum:
                return False
        else:
            first, last = sorted(((minimum - origin) / delta, (maximum - origin) / delta))
            lo, hi = max(lo, first), min(hi, last)
            if lo >= hi:
                return False
    return hi > 0 and lo < 1


class _Topology:
    def __init__(self, item, facts, canvas, tokens):
        self.facts, self.canvas = facts, canvas
        if tokens is None:
            _, _, tokens = load_template()
        self.tokens = tokens
        if not isinstance(item, dict):
            raise TemplateInputError("topology must be an object")
        self.item = resolve_value(copy.deepcopy(item), facts)
        self.identifier = self.item.get("id", "")
        if not isinstance(self.identifier, str) or not ID.fullmatch(self.identifier):
            raise TemplateInputError("topology id must be a stable SVG-compatible identifier")
        self.kind = self.item.get("layout")
        if self.kind not in LAYOUTS:
            self.fail("unknown topology layout", path="layout", reason="unsupported_layout")
        self.variant = self.item.get("variant", "default")
        if self.variant not in ("default", "arrow-ring") or ("variant" in self.item and self.kind != "cycle"):
            self.fail("variant supports default/arrow-ring on cycle only", path="variant", reason="unsupported_variant")
        if self.item.get("type") != "component" or self.item.get("component") != "topology":
            self.fail("requires type=component and component=topology", reason="invalid_component")
        unknown = set(self.item) - COMMON - OPTIONS
        if unknown:
            self.fail(f"unsupported topology fields {sorted(unknown)}", reason="unsupported_fields")
        self.bounds = list(frame(self.item.get("frame"), self.identifier, canvas))
        if not isinstance(self.item.get("metadata", {}), dict):
            self.fail("metadata must be an object", path="metadata")
        self.pad = self.num("padding", 12)
        self.gap = self.num("node_gap", 20)
        self.layer_gap = self.num("layer_gap", 36)
        self.node_pad = self.num("node_padding", 12)
        x, y, width, height = self.bounds
        self.area = [x + self.pad, y + self.pad, width - self.pad * 2, height - self.pad * 2]
        if min(self.area[2:]) <= 0:
            self.fail("padding leaves no topology area", reason="capacity", available=self.bounds[2:])
        self.direction = self.item.get("direction", "down")
        if self.direction not in {"down", "right"}:
            self.fail("direction must be down or right", path="direction")
        for key in ("arrow",):
            if key in self.item and type(self.item[key]) is not bool:
                self.fail(f"{key} must be a boolean", path=key)
        if self.kind != "arch" and set(self.item) & {"interior", "band", "marker_size", "label_gap"}:
            self.fail("interior/band/marker_size/label_gap apply to arch only", reason="unsupported_fields")
        if self.kind not in {"tree", "layered"} and "direction" in self.item:
            self.fail("direction applies to tree/layered only", path="direction")
        if self.kind != "radial" and "center_id" in self.item:
            self.fail("center_id applies to radial only", path="center_id")
        if self.kind not in {"tree", "layered"} and "root_id" in self.item:
            self.fail("root_id applies to tree/layered only", path="root_id")
        self.supplied_style = self.item.get("style", {})
        if not isinstance(self.supplied_style, dict) or set(self.supplied_style) - STYLE_FIELDS - PAINT_FIELDS:
            self.fail("unsupported topology style fields", path="style")
        self.paint = {"fill": "surfaceMuted", "stroke": "primary", "stroke_width": 2,
                      "marker_fill": "primary", "marker_color": "#FFFFFF", **{k: v for k, v in self.supplied_style.items() if k in PAINT_FIELDS}}
        number(self.paint["stroke_width"], self.identifier + ".style.stroke_width", 0)
        self.helpers = runtime_helpers()
        self.children, self.boxes, self.occupied, self.measurements = [], {}, {}, {}
        self.read_graph()

    def fail(self, message, **details):
        details.setdefault("reason", "invalid_input")
        details.setdefault("suggestions", ["enlarge the frame, reduce node count, or simplify the structure; retain the authored font size"])
        diagnostic = {"node_id": details.pop("node_id", self.identifier), "path": details.pop("path", "topology"), **details}
        raise TopologyError(f"{self.identifier}: {message}", diagnostic)

    def num(self, key, default, minimum=0):
        return number(self.item.get(key, default), self.identifier + "." + key, minimum)

    def cid(self, suffix):
        return self.identifier + "--" + suffix

    def shape_id(self, node_id):
        return self.cid("node--" + node_id + "--shape")

    def read_graph(self):
        self.nodes = self.item.get("nodes")
        if not isinstance(self.nodes, list) or not 1 <= len(self.nodes) <= MAX_NODES:
            self.fail(f"nodes capacity is 1..{MAX_NODES}", path="nodes")
        self.by_id = {}
        for index, node in enumerate(self.nodes):
            path = f"nodes[{index}]"
            if not isinstance(node, dict) or set(node) - NODE_FIELDS or not {"id", "label"} <= set(node):
                self.fail("each node requires id/label and supported node fields", path=path)
            identifier = node["id"]
            if not isinstance(identifier, str) or not ID.fullmatch(identifier) or identifier in self.by_id:
                self.fail("node IDs must be unique stable SVG-compatible identifiers", path=path + ".id")
            if self.kind != "arch" and "marker" in node:
                self.fail("marker applies to arch only", path=path + ".marker")
            if self.kind == "arch" and set(node) & {"height", "shape"}:
                self.fail("arch uses measured external labels and ellipse markers; height/shape are unsupported", path=path)
            if node.get("shape", "roundRect") not in {"rect", "roundRect", "ellipse"}:
                self.fail("node shape must be rect, roundRect or ellipse", path=path + ".shape")
            self.by_id[identifier] = node
        self.center = self.item.get("center_id", self.nodes[0]["id"])
        if self.kind == "radial" and (not isinstance(self.center,str) or self.center not in self.by_id):
            self.fail("center_id must name a node", path="center_id")
        edges = self.item.get("edges")
        if edges is None:
            if self.kind == "radial":
                edges = [{"id": "spoke-" + n["id"], "from": self.center, "to": n["id"]} for n in self.nodes if n["id"] != self.center]
            elif self.kind == "cycle":
                edges = [{"id": "cycle-" + n["id"], "from": n["id"], "to": self.nodes[(i + 1) % len(self.nodes)]["id"]} for i, n in enumerate(self.nodes)]
            else:
                edges = []
        if not isinstance(edges, list) or len(edges) > MAX_EDGES:
            self.fail(f"edges capacity is 0..{MAX_EDGES}", path="edges")
        self.edges, seen, pairs = [], set(), set()
        self.parents = {n: [] for n in self.by_id}
        self.successors = {n: [] for n in self.by_id}
        for index, edge in enumerate(edges):
            path = f"edges[{index}]"
            if not isinstance(edge, dict) or set(edge) - EDGE_FIELDS or not {"id", "from", "to"} <= set(edge):
                self.fail("each edge requires id/from/to and supported edge fields", path=path)
            identifier = edge["id"]
            if not isinstance(identifier, str) or not ID.fullmatch(identifier) or identifier in seen:
                self.fail("edge IDs must be unique stable SVG-compatible identifiers", path=path + ".id")
            if not all(isinstance(edge[k],str) and edge[k] in self.by_id for k in ("from","to")):
                self.fail("edge names an unknown endpoint", path=path, reason="unknown_endpoint")
            pair = edge["from"], edge["to"]
            if pair[0] == pair[1] or pair in pairs:
                self.fail("self edges and duplicate directed edges are unsupported", path=path)
            if edge.get("preset", "line") != "line" or "label" in edge:
                self.fail("only straight native connectors without edge labels are supported", path=path, reason="unsupported_route")
            if "arrow" in edge and type(edge["arrow"]) is not bool:
                self.fail("edge arrow must be a boolean", path=path + ".arrow")
            seen.add(identifier)
            pairs.add(pair)
            self.edges.append(edge)
            self.parents[pair[1]].append(pair[0])
            self.successors[pair[0]].append(pair[1])
        if self.kind in {"tree", "layered", "radial"} and len(self.nodes) > 1:
            orphans = [n for n in self.by_id if not self.parents[n] and not self.successors[n]]
            if orphans:
                self.fail(f"isolated nodes have no edges: {orphans}", reason="orphan_nodes", node_id=orphans[0])
        if self.kind == "radial" and any(self.center not in (e["from"], e["to"]) for e in self.edges):
            self.fail("radial edges must join the center and a spoke", reason="invalid_radial_edge")
        if self.kind == "cycle":
            if len(self.nodes) < 3:
                self.fail("cycle requires at least three nodes", path="nodes")
            order = [n["id"] for n in self.nodes]
            forward = {(n, order[(i + 1) % len(order)]) for i, n in enumerate(order)}
            reverse = {(b, a) for a, b in forward}
            if pairs not in (forward, reverse):
                self.fail("cycle edges must form the closed input node order or its reverse", reason="invalid_cycle")

    def node_style(self, node):
        explicit = node.get("style", {})
        if not isinstance(explicit, dict) or set(explicit) - STYLE_FIELDS:
            self.fail("unsupported node text style", node_id=node["id"], path="nodes.style")
        overrides = {"align": "center", "vertical_anchor": "middle", **{k: v for k, v in self.supplied_style.items() if k in STYLE_FIELDS}, **explicit}
        try:
            return resolve_text_style(self.tokens, node.get("role", self.item.get("role", "body")), overrides)
        except ValueError as exc:
            self.fail(str(exc), node_id=node["id"], path="nodes.style")

    def measure(self, node, width, padding=None):
        padding = self.node_pad if padding is None else padding
        style = self.node_style(node)
        left, top, right, bottom = style["insets"]
        content_width = width - padding * 2 - left - right
        if content_width <= 0:
            self.fail("node padding leaves no text width", node_id=node["id"], reason="capacity", available=width)
        try:
            measured = measure_text_block(resolve_text(node["label"], self.facts), content_width, style, self.helpers)
        except ValueError as exc:
            self.fail(str(exc), node_id=node["id"], path="nodes.label", reason="text_measurement", available=content_width)
        height = measured["height"] + padding * 2 + top + bottom
        self.measurements[node["id"]] = {"label": measured["text"], "lines": len(measured["lines"]),
            "text_width": max(measured["widths"]), "required_height": height, "font_size": style["font_size"]}
        return height

    def dimensions(self, width_limit=None):
        width_limit = self.area[2] if width_limit is None else width_limit
        if width_limit <= 0:
            self.fail("nodes and gaps exceed available width", reason="capacity", available=self.area[2], axis="x")
        sizes = {}
        for node in self.nodes:
            width = number(node.get("width", self.item.get("node_width", min(160, width_limit))), "node width", .000001)
            required = self.measure(node, width)
            height = number(node.get("height", self.item.get("node_height", required)), "node height", .000001)
            if height + EPS < required:
                self.fail("node height cannot contain measured text", node_id=node["id"], reason="text_overflow",
                          available=height, required=required, overflow_px=required-height, axis="y")
            sizes[node["id"]] = [width, height]
        return sizes

    def add_node(self, node, bounds):
        identifier = node["id"]
        self.boxes[identifier] = list(bounds)
        self.occupied[identifier] = [list(bounds)]
        self.children.append({"id": self.shape_id(identifier), "type": "shape", "shape": node.get("shape", "roundRect"), "frame": list(bounds),
            "fill": node.get("fill", self.paint["fill"]), "stroke": node.get("stroke", self.paint["stroke"]), "stroke_width": self.paint["stroke_width"]})
        x, y, width, height = bounds
        self.children.append({"id": self.cid("node--" + identifier + "--label"), "type": "text", "text": node["label"],
            "frame": [x+self.node_pad, y+self.node_pad, width-2*self.node_pad, height-2*self.node_pad],
            "role": node.get("role", self.item.get("role", "body")), "style": self.node_style(node)})

    def ranked(self):
        degree = {n: len(p) for n, p in self.parents.items()}
        roots = [n for n in self.by_id if degree[n] == 0]
        ranks = {n: 0 for n in self.by_id}
        pending, visited = list(roots), []
        while pending:
            current = pending.pop(0)
            visited.append(current)
            for child in self.successors[current]:
                ranks[child] = max(ranks[child], ranks[current] + 1)
                degree[child] -= 1
                if degree[child] == 0:
                    pending.append(child)
        if len(visited) != len(self.nodes):
            self.fail("directed cycle in tree/layered topology", reason="directed_cycle", node_id=next(n for n in self.by_id if degree[n]))
        if self.kind == "tree" and (len(roots) != 1 or any(len(p) != 1 for n, p in self.parents.items() if n not in roots)):
            self.fail("tree requires one root and exactly one parent per other node", reason="invalid_tree")
        if "root_id" in self.item and (self.item["root_id"] not in roots or (self.kind == "tree" and roots != [self.item["root_id"]])):
            self.fail("root_id must name a graph root", path="root_id")
        layers = [[n for n in self.by_id if ranks[n] == r] for r in range(max(ranks.values()) + 1)]
        # Stable sorting preserves input order on ties. Four sweeps keep runtime bounded.
        for sweep in range(4):
            sequence = range(1, len(layers)) if sweep % 2 == 0 else range(len(layers)-2, -1, -1)
            for rank in sequence:
                neighbor_rank = rank-1 if sweep % 2 == 0 else rank+1
                positions = {n: i for i, n in enumerate(layers[neighbor_rank])}
                neighbors = self.parents if sweep % 2 == 0 else self.successors
                old = {n: i for i, n in enumerate(layers[rank])}
                def barycenter(n):
                    values = [positions[p] for p in neighbors[n] if p in positions]
                    return sum(values)/len(values) if values else old[n]
                layers[rank].sort(key=barycenter)
        x, y, width, height = self.area
        down = self.direction == "down"
        cross_available, main_available = (width, height) if down else (height, width)
        max_count = max(map(len, layers))
        # For left-to-right, each rank gets an independent measured width and packed heights.
        width_limit = (width-(max_count-1)*self.gap)/max_count if down else (width-(len(layers)-1)*self.layer_gap)/len(layers)
        sizes = self.dimensions(width_limit)
        # Automatic heights may share a rank's measured maximum, keeping adjacent-rank
        # fan-out above the next row. Explicit authored heights remain exact.
        if down:
            for layer in layers:
                rank_height=max(sizes[n][1] for n in layer)
                for n in layer:
                    if "height" not in self.by_id[n] and "node_height" not in self.item:
                        sizes[n][1]=rank_height
        cross_sizes = [sum(sizes[n][0 if down else 1] for n in layer)+(len(layer)-1)*self.gap for layer in layers]
        main_sizes = [max(sizes[n][1 if down else 0] for n in layer) for layer in layers]
        required = sum(main_sizes)+(len(layers)-1)*self.layer_gap
        if max(cross_sizes) > cross_available + EPS or required > main_available + EPS:
            self.fail("ranked nodes do not fit the available frame", reason="capacity", available=[width,height],
                      required=[max(cross_sizes),required] if down else [required,max(cross_sizes)])
        cursor = (y if down else x)+(main_available-required)/2
        for index, layer in enumerate(layers):
            across = (x if down else y)+(cross_available-cross_sizes[index])/2
            for n in layer:
                w, h = sizes[n]
                box = [across,cursor,w,h] if down else [cursor,across,w,h]
                self.add_node(self.by_id[n], box)
                across += (w if down else h)+self.gap
            cursor += main_sizes[index]+self.layer_gap
        self.report["layers"] = layers
        self.report["algorithm"] = "kahn-longest-path+barycenter-4"

    def circular(self):
        sizes = self.dimensions(min(160, self.area[2]/3))
        x, y, width, height = self.area
        maxw, maxh = max(s[0] for s in sizes.values()), max(s[1] for s in sizes.values())
        rx, ry = (width-maxw)/2, (height-maxh)/2
        if min(rx, ry) <= 0:
            self.fail("circular nodes exceed the frame", reason="capacity")
        center = x+width/2, y+height/2
        ring = [n for n in self.nodes if self.kind != "radial" or n["id"] != self.center]
        if self.kind == "radial":
            w, h = sizes[self.center]
            self.add_node(self.by_id[self.center], [center[0]-w/2,center[1]-h/2,w,h])
        for i, node in enumerate(ring):
            angle = -math.pi/2 + math.tau*i/len(ring)
            w, h = sizes[node["id"]]
            self.add_node(node, [center[0]+rx*math.cos(angle)-w/2,center[1]+ry*math.sin(angle)-h/2,w,h])
        self.report.update(algorithm="ellipse-uniform-angle", ellipse={"center": list(center), "radii": [rx,ry]})

    def arch(self):
        x, y, width, height = self.area
        size, label_gap = self.num("marker_size", 40, .000001), self.num("label_gap", 10)
        if "node_height" in self.item:
            self.fail("arch labels are measured; node_height is unsupported", path="node_height")
        labels = {}
        from text_measure import measure_text
        for node in self.nodes:
            style=self.node_style(node)
            value=resolve_text(node["label"],self.facts)
            natural=max(measure_text(line,size=style["font_size"],family=style["font_family"],weight=str(style["weight"])) for line in value.split("\n"))
            natural+=style["insets"][0]+style["insets"][2]+1
            w = number(node.get("width", self.item.get("node_width", min(120,width/5,max(40,natural)))), "arch label width", .000001)
            h = self.measure(node,w,0)
            labels[node["id"]] = w,h
        maxw, maxh = max(v[0] for v in labels.values()), max(v[1] for v in labels.values())
        side = size/2+label_gap+maxw
        top, bottom = size/2+label_gap+maxh, max(size/2,maxh/2)
        cx, cy = x+width/2,y+height-bottom
        rx, ry = width/2-side, height-top-bottom
        if min(rx,ry) <= 0:
            self.fail("arch labels and markers leave no ellipse", reason="capacity", available=[width,height])
        band = self.item.get("band", True)
        if type(band) is not bool and not isinstance(band,dict):
            self.fail("band must be boolean or an object", path="band")
        band_options = band if isinstance(band,dict) else {}
        if set(band_options)-{"thickness","fill","stroke","stroke_width"}:
            self.fail("unsupported band fields", path="band")
        thickness = number(band_options.get("thickness",14),"band.thickness",.000001) if band is not False else 0
        if thickness >= min(rx,ry):
            self.fail("band thickness exceeds ellipse radii", path="band.thickness",reason="capacity")
        if band is not False:
            innerx, innery = rx-thickness,ry-thickness
            path = (f"M {cx-rx:g} {cy:g} A {rx:g} {ry:g} 0 0 1 {cx+rx:g} {cy:g} "
                    f"L {cx+innerx:g} {cy:g} A {innerx:g} {innery:g} 0 0 0 {cx-innerx:g} {cy:g} Z")
            self.children.append({"id":self.cid("arch-band"),"type":"shape","shape":"path","frame":[cx-rx,cy-ry,rx*2,ry],"d":path,
                "fill":band_options.get("fill",self.paint["fill"]),"stroke":band_options.get("stroke",self.paint["stroke"]),
                "stroke_width":number(band_options.get("stroke_width",self.paint["stroke_width"]),"band.stroke_width",0)})
        for i,node in enumerate(self.nodes):
            angle = math.pi/2 if len(self.nodes)==1 else math.pi-math.pi*i/(len(self.nodes)-1)
            cosine,sine = math.cos(angle),math.sin(angle)
            mx,my = cx+rx*cosine,cy-ry*sine
            w,h = labels[node["id"]]
            if cosine < -.55:
                label = [mx-size/2-label_gap-w,my-h/2,w,h]
            elif cosine > .55:
                label = [mx+size/2+label_gap,my-h/2,w,h]
            else:
                label = [mx-w/2,my-size/2-label_gap-h,w,h]
            marker = [mx-size/2,my-size/2,size,size]
            self.boxes[node["id"]] = marker
            self.occupied[node["id"]] = [marker,label]
            self.children.append({"id":self.shape_id(node["id"]),"type":"shape","shape":"ellipse","frame":marker,
                "fill":node.get("fill",self.paint["marker_fill"]),"stroke":node.get("stroke",self.paint["stroke"]),"stroke_width":self.paint["stroke_width"]})
            self.children.append({"id":self.cid("node--"+node["id"]+"--label"),"type":"text","frame":label,
                "text":node["label"],"role":node.get("role",self.item.get("role","body")),"style":self.node_style(node)})
            if "marker" in node:
                marker_style = {**self.node_style(node),"insets":[0,0,0,0],"align":"center","vertical_anchor":"middle","color":self.paint["marker_color"]}
                try:
                    measured=measure_text_block(resolve_text(node["marker"],self.facts),size-8,marker_style,self.helpers)
                except ValueError as exc:
                    self.fail(str(exc),node_id=node["id"],path="nodes.marker",reason="text_measurement")
                if measured["height"] > size-8+EPS:
                    self.fail("marker text exceeds marker",node_id=node["id"],path="nodes.marker",reason="text_overflow")
                self.children.append({"id":self.cid("node--"+node["id"]+"--marker"),"type":"text","text":node["marker"],
                    "frame":[mx-size/2+4,my-size/2+4,size-8,size-8],"style":marker_style})
        # sqrt(2) turns a radial clearance into a conservative axis-aligned box
        # clearance at the 45-degree corner of the inscribed rectangle.
        clearance=max(thickness,math.sqrt(2)*(size/2+self.gap))
        innerx,innery=rx-clearance,ry-clearance
        self.report.update(algorithm="ellipse-arch+maximum-area-inner-rectangle",ellipse={"center":[cx,cy],"radii":[rx,ry]},band_thickness=thickness)
        if "interior" in self.item:
            if min(innerx,innery)<=0:
                self.fail("markers and clearance leave no interior area",path="interior",reason="capacity")
            halfw,tall=innerx/math.sqrt(2),innery/math.sqrt(2)
            bounds=[cx-halfw,cy-tall,halfw*2,tall]
            interior=copy.deepcopy(self.item["interior"])
            self.prepare_interior(interior)
            from presentation_layout import lower_layout_page
            page,report=lower_layout_page({"id":self.cid("interior-page"),"kind":"layout","layout_version":VERSION,"layout":interior},
                self.facts,self.canvas,self.tokens,bounds=bounds)
            self.children.extend(page["elements"])
            self.report.update(interior_bounds=bounds,interior_ellipse_radii=[innerx,innery],interior_report=report)

    def prepare_interior(self, node):
        def visit(value):
            if isinstance(value,dict):
                if value.get("component")=="topology":
                    self.fail("recursive topology inside arch interior is unsupported",path="interior",reason="recursive_topology")
                for child in value.values():
                    visit(child)
            elif isinstance(value,list):
                for child in value:
                    visit(child)
        visit(node)
        # Layout node identity is local to this topology, but the lowered scene is page-global.
        def prefix(current):
            if not isinstance(current,dict):
                return
            if isinstance(current.get("id"),str):
                current["id"]=self.cid("interior--"+current["id"])
            for child in current.get("children",[]):
                prefix(child)
        prefix(node)

    def validate_boxes(self):
        x,y,width,height=self.area
        for identifier,boxes in self.occupied.items():
            for box in boxes:
                bx,by,bw,bh=box
                if bx<x-EPS or by<y-EPS or bx+bw>x+width+EPS or by+bh>y+height+EPS:
                    self.fail("generated node or label exceeds the topology area",node_id=identifier,reason="out_of_bounds",available=self.area,required=box)
        identifiers=list(self.occupied)
        for i,a in enumerate(identifiers):
            for b in identifiers[i+1:]:
                if any(_overlap(first,last,self.gap) for first in self.occupied[a] for last in self.occupied[b]):
                    self.fail(f"nodes or labels {a!r} and {b!r} violate node_gap",node_id=a,reason="node_overlap",other_node_id=b,required_gap=self.gap)

    @staticmethod
    def port(box, target):
        x,y,w,h=box
        dx,dy=target[0]-(x+w/2),target[1]-(y+h/2)
        if abs(dx)/w>=abs(dy)/h:
            return ("right",(x+w,y+h/2)) if dx>=0 else ("left",(x,y+h/2))
        return ("bottom",(x+w/2,y+h)) if dy>=0 else ("top",(x+w/2,y))

    def add_edges(self):
        connectors=[]
        for edge in self.edges:
            a,b=self.boxes[edge["from"]],self.boxes[edge["to"]]
            ca,cb=(a[0]+a[2]/2,a[1]+a[3]/2),(b[0]+b[2]/2,b[1]+b[3]/2)
            if self.kind in {"tree","layered"}:
                if self.direction=="down":
                    from_port,start="bottom",(a[0]+a[2]/2,a[1]+a[3])
                    to_port,end="top",(b[0]+b[2]/2,b[1])
                else:
                    from_port,start="right",(a[0]+a[2],a[1]+a[3]/2)
                    to_port,end="left",(b[0],b[1]+b[3]/2)
            else:
                from_port,start=self.port(a,cb)
                to_port,end=self.port(b,ca)
            for n,boxes in self.occupied.items():
                if n not in {edge["from"],edge["to"]} and any(_segment_hits_box(start,end,box) for box in boxes):
                    self.fail(f"straight edge {edge['id']!r} intersects non-endpoint node {n!r}; obstacle routing is unavailable",
                        node_id=n,path="edges."+edge["id"],reason="edge_obstruction",edge_id=edge["id"],
                        suggestions=["use adjacent ranks, change the graph/order, or split the structure; this version does not detour edges"])
            if "interior_bounds" in self.report and _segment_hits_box(start,end,self.report["interior_bounds"]):
                self.fail(f"straight edge {edge['id']!r} crosses the reserved interior; obstacle routing is unavailable",
                          path="edges."+edge["id"],reason="edge_obstruction",edge_id=edge["id"])
            connectors.append({"id":self.cid("edge--"+edge["id"]),"type":"connector","from":self.shape_id(edge["from"]),
                "to":self.shape_id(edge["to"]),"from_port":from_port,"to_port":to_port,"preset":"line",
                "arrow":edge.get("arrow",self.item.get("arrow",False)),"stroke":self.paint["stroke"],"stroke_width":max(.01,self.paint["stroke_width"])})
        # Behind the nodes, while keeping endpoint shapes and connectors in one scope.
        self.children[0:0]=connectors

    def render(self):
        self.report={"topology_version":VERSION,"layout":self.kind,"node_count":len(self.nodes),"edge_count":len(self.edges),
                     "bounds":self.bounds,"routing":"straight segments; non-endpoint occupied rectangles checked; edge crossings not optimized"}
        if self.variant == "arrow-ring":
            from presentation_cycle_arrows import lower_arrow_ring
            lower_arrow_ring(self)
        elif self.kind in {"tree","layered"}:
            self.ranked()
        elif self.kind in {"radial","cycle"}:
            self.circular()
        else:
            self.arch()
        self.validate_boxes()
        if "interior_bounds" in self.report:
            for identifier,boxes in self.occupied.items():
                if any(_overlap(box,self.report["interior_bounds"],self.gap) for box in boxes):
                    self.fail("interior safe rectangle violates external node clearance",node_id=identifier,path="interior",reason="node_overlap")
        if self.variant != "arrow-ring":
            self.add_edges()
        self.report.update(node_frames=copy.deepcopy(self.boxes),occupied_frames=copy.deepcopy(self.occupied),measurements=self.measurements,
                           checks=["text measurement","component containment","pairwise node and label gap","straight edge obstruction"])
        if self.variant == "arrow-ring":
            self.report["checks"] = ["text measurement", "component containment", "label rectangle inside annular body",
                                     "pairwise label gap", "disjoint directed angular sectors", "palette contrasting label ink"]
        metadata={**self.item.get("metadata",{}),"component":"topology","component_contract":VERSION,"component_frame":self.bounds,"topology_report":self.report}
        result={k:copy.deepcopy(v) for k,v in self.item.items() if k in COMMON-{"type","component","frame","metadata"}}
        return {**result,"type":"group","children":self.children,"metadata":metadata}


def lower_topology(item, facts, canvas, tokens=None):
    """Lower a source topology on every build; never mutate the author graph/tree."""
    return _Topology(item,facts,canvas,tokens).render()
