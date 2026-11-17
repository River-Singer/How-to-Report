"""Independent probes of emitted paths, not only their topology report."""
import json
import math
from pathlib import Path
import re
import sys
import unittest

PROJECT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(PROJECT / "skill-src/how-to-report/scripts"), str(PROJECT / "skill-src/shared/scripts")]

from presentation_compiler import _compiler_identity
from presentation_palette import apply_palette
from presentation_topology import lower_topology


def path_polygon(path, center):
    """Sample the actual emitted M/A/L/Z path, independently of its bbox."""
    words = re.findall(r"[A-Za-z]|[-+]?\d+(?:\.\d+)?", path)
    points, i = [], 0
    while i < len(words):
        command = words[i]
        i += 1
        if command in ("M", "L"):
            points.append((float(words[i]), float(words[i + 1])))
            i += 2
        elif command == "A":
            rx, ry, rotation, large, sweep, x, y = map(float, words[i:i + 7])
            i += 7
            assert rx == ry and rotation == 0 and large == 0
            start = math.atan2(points[-1][1] - center[1], points[-1][0] - center[0])
            end = math.atan2(y - center[1], x - center[0])
            delta = (end - start) % math.tau if sweep else -((start - end) % math.tau)
            points.extend((center[0] + rx * math.cos(start + delta * t / 128),
                           center[1] + ry * math.sin(start + delta * t / 128)) for t in range(1, 129))
        else:
            assert command == "Z"
    return points


def inside(point, polygon):
    x, y = point
    result = False
    for (ax, ay), (bx, by) in zip(polygon, polygon[1:] + polygon[:1]):
        if (ay > y) != (by > y) and x < (bx - ax) * (y - ay) / (by - ay) + ax:
            result = not result
    return result


class CycleArrowsReviewTests(unittest.TestCase):
    def test_actual_paths_have_disjoint_angular_support_and_contain_complete_labels(self):
        tokens = json.loads((PROJECT / "skill-src/how-to-report/assets/design-profiles/report-14pt.json").read_text(encoding="utf-8"))
        tokens = apply_palette(tokens, "consulting-spectrum")
        for count in range(3, 7):
            for reverse in (False, True):
                with self.subTest(count=count, reverse=reverse):
                    item = {"id": "ring", "type": "component", "component": "topology", "layout": "cycle",
                            "variant": "arrow-ring", "frame": [100, 80, 700, 550],
                            "nodes": [{"id": f"n{i}", "label": f"阶段{i}"} for i in range(count)]}
                    if reverse:
                        item["edges"] = [{"id": f"e{i}", "from": f"n{i}", "to": f"n{(i-1)%count}"} for i in range(count)]
                    result = lower_topology(item, {}, [1280, 720], tokens)
                    report = result["metadata"]["topology_report"]
                    center = report["center"]
                    paths = [n for n in result["children"] if n["type"] == "shape"]
                    polygons = [path_polygon(n["d"], center) for n in paths]
                    for i, (polygon, segment) in enumerate(zip(polygons, report["segments"])):
                        # Every curve/head vertex belongs to one directed sector.
                        sign = -1 if reverse else 1
                        for px, py in polygon:
                            angle = math.atan2(py-center[1], px-center[0])
                            delta = (sign * (angle - segment["start_radians"])) % math.tau
                            if math.tau-delta < 1e-8:
                                delta = 0
                            self.assertLessEqual(delta, abs(segment["sweep_radians"]) + 1e-8)
                        # The actual filled path contains corners, edges and center
                        # of the measured label, including the inner-hole edge.
                        x, y, w, h = segment["label_safe_frame"]
                        for a in (0, .25, .5, .75, 1):
                            for b in (0, .25, .5, .75, 1):
                                self.assertTrue(inside((x+a*w, y+b*h), polygon))
                        for j, other in enumerate(polygons):
                            if i != j:
                                self.assertFalse(any(inside(p, other) for p in polygon[::8]))
                    self.assertTrue(all(s["label_contrast_ratio"] >= 4.5 for s in report["segments"]))

    def test_new_geometry_and_recipe_helpers_are_part_of_compiler_identity(self):
        identity = _compiler_identity()
        for module in ("presentation_cycle_arrows.py", "presentation_visual_recipes.py"):
            self.assertIn(module, identity)
            self.assertEqual(len(identity[module]), 64)

    def test_library_preview_and_storybook_invocation_select_the_same_variant(self):
        import hashlib
        from presentation_library import library
        from presentation_storybook import _add_invocation
        source = PROJECT / "skill-src/how-to-report"
        record = library(identifier="component.topology")
        self.assertEqual(len(record["preview_refs"]), 2)
        for preview in record["preview_refs"]:
            self.assertEqual(preview["variant"], "arrow-ring")
            self.assertEqual(hashlib.sha256((source / preview["ref"]).read_bytes()).hexdigest(), preview["sha256"])
        _add_invocation(record)
        author = record["invocation"]["request"]
        def variants(node):
            result = [node["element"]["variant"]] if node.get("element", {}).get("component") == "topology" else []
            return result + [value for child in node.get("children", []) for value in variants(child)]
        self.assertEqual(variants(author["pages"][0]["layout"]), ["arrow-ring"])


if __name__ == "__main__":
    unittest.main()
