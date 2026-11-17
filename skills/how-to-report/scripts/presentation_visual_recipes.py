"""Finite visual recipes: semantic slots become a measured layout, never caller frames."""
from __future__ import annotations

from presentation_layout import lower_layout_page
from presentation_palette import describe_palette, label_ink

NAMES = {"editorial-pillars", "capability-platform", "stage-ribbon"}


def _platform_links(elements, prefix, input_count, output_count):
    """Connect every measured panel through a shared bus, without caller coordinates."""
    shapes = {e["id"]: e for e in elements if e["type"] == "shape"}
    platform_id = prefix + "platform--surface"
    platform = shapes[platform_id]["frame"]
    result = []

    def point(name, x, y):
        identifier = prefix + name
        result.append({"id": identifier, "type": "shape", "shape": "rect",
                       "frame": [x-.05, y-.05, .1, .1], "fill": "none", "stroke": "none",
                       "role": "decoration", "metadata": {"purpose": "computed shared-bus junction"}})
        return identifier

    def link(name, source, target, first="bottom", last="top", arrow=False):
        result.append({"id": prefix + name, "type": "connector", "from": source, "to": target,
                       "from_port": first, "to_port": last, "arrow": arrow,
                       "stroke": "primary", "stroke_width": 2,
                       "metadata": {"relation": "inputs-to-shared-platform-to-outputs"}})

    for name, count in (("inputs", input_count), ("outputs", output_count)):
        panel_ids = [prefix + f"{name}-{i}--surface" for i in range(count)]
        boxes = [shapes[identifier]["frame"] for identifier in panel_ids]
        y = ((max(box[1]+box[3] for box in boxes)+platform[1])/2 if name == "inputs"
             else (platform[1]+platform[3]+min(box[1] for box in boxes))/2)
        junctions = [point(f"{name}-junction-{i}", box[0]+box[2]/2, y) for i,box in enumerate(boxes)]
        center = point(name + "-center", platform[0]+platform[2]/2, y)
        link(name + "-bus", junctions[0], junctions[-1], "right", "left")
        for i, panel in enumerate(panel_ids):
            if name == "inputs": link(f"{name}-branch-{i}", panel, junctions[i])
            else: link(f"{name}-branch-{i}", junctions[i], panel, arrow=True)
        if name == "inputs": link(name + "-trunk", center, platform_id, arrow=True)
        else: link(name + "-trunk", platform_id, center)
    # Wires/junctions precede filled surfaces; text stays above its containing surface.
    return result + elements


def visual_recipe(page, tokens, facts):
    prefix = page["id"] + "--ui-"
    palette = tokens.get("color", {}).get("palette") or describe_palette("report-default")
    colors = palette["categorical"]
    slots = page["slots"]

    def text(name, value, role="body", **style):
        return {"id": prefix + name, "type": "leaf", "element": {
            "type": "text", "text": value, "role": role, "style": style}}

    def col(name, children, **options):
        return {"id": prefix + name, "type": "column", "gap": 16, "children": children, **options}

    def grid(name, children):
        return {"id": prefix + name, "type": "grid", "columns": [{"fr": 1}] * len(children),
                "gap": 28, "children": children}

    def bar(name, title, color, shape="rect"):
        return col(name, [text(name + "-label", title, "heading", color=label_ink(color), align="center")],
                   min_height=66, padding=[32, 18, 36, 18], surface={"shape": shape, "fill": color})

    kind = page["recipe"]
    if kind == "editorial-pillars":
        columns = []
        for i, item in enumerate(slots["items"]):
            color = colors[i % len(colors)]
            columns.append(col(f"pillar-{i}", [bar(f"pillar-title-{i}", item["title"], color),
                text(f"pillar-copy-{i}", item["body"])], padding=[0, 0, 18, 0]))
        body = col("body", [grid("pillars", columns),
            col("closing", [text("closing-copy", slots["closing"], "bodyStrong")],
                padding=18, surface={"fill": "surfaceMuted", "accent": {"kind": "rail", "color": "accent"}})], gap=32)
    elif kind == "stage-ribbon":
        heads, copies = [], []
        for i, item in enumerate(slots["steps"]):
            color = colors[i % len(colors)]
            heads.append(bar(f"step-{i}", item["title"], color, "chevron"))
            copies.append(col(f"step-detail-{i}", [text(f"step-copy-{i}", item["body"])],
                padding=[16, 12, 12, 12], surface={"fill": "none", "accent": {"kind": "rail", "color": color}}))
        sequence = {"id": prefix + "sequence", "type": "row", "gap": 26, "connect": "sequence",
                    "children": [{**node, "grow": 1, "basis": 0} for node in heads]}
        body = col("body", [sequence, grid("details", copies),
            col("result", [text("result-copy", slots["result"], "bodyStrong")], padding=20,
                surface={"fill": "surfaceMuted", "accent": {"kind": "rule", "color": "accent"}})], gap=24)
    else:
        def layer(name, items):
            panels = [col(f"{name}-{i}", [text(f"{name}-title-{i}", item["title"], "bodyStrong"),
                          text(f"{name}-copy-{i}", item["body"])], padding=18,
                          surface={"fill": "surfaceMuted", "accent": {"kind": "rule", "color": colors[i % len(colors)]}})
                      for i, item in enumerate(items)]
            return {**grid(name, panels), "surface": {"fill": "none"}}
        platform_ink = label_ink(palette["roles"]["primary"])
        platform = col("platform", [text("platform-title", slots["platform"]["title"], "heading", color=platform_ink),
                    text("platform-copy", slots["platform"]["body"], color=platform_ink)], padding=24,
                    surface={"fill": "primary"})
        body = col("body", [layer("inputs", slots["inputs"]), platform, layer("outputs", slots["outputs"])], gap=40)
    scene, _ = lower_layout_page({"id": page["id"], "kind": "layout", "layout_version": "0.1", "layout": body},
                                     facts, (tokens["canvas"]["width"], tokens["canvas"]["height"]), tokens,
                                     bounds=tokens["body"]["frame"])
    # All frames below are computed; the persisted recipe is replayed on every build.
    if kind == "capability-platform":
        return _platform_links(scene["elements"], prefix, len(slots["inputs"]), len(slots["outputs"]))
    return scene["elements"]
