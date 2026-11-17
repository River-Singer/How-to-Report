"""Measured graph geometry, arch containment and real native connector regressions."""
from __future__ import annotations

import copy
from pathlib import Path
import sys
import tempfile
import unittest
from xml.etree import ElementTree as ET
from zipfile import ZipFile

PROJECT = Path(__file__).resolve().parents[1]
SCRIPTS = PROJECT / "skill-src" / "how-to-report" / "scripts"
sys.path.insert(0, str(PROJECT / "skill-src" / "shared" / "scripts"))
sys.path.insert(0, str(SCRIPTS))

from presentation_document import resolve_text, resolve_value
from presentation_svg import SceneRenderer
from presentation_topology import TopologyError, lower_topology, topology_catalog
from report_ppt import TemplateInputError, load_template


def topology(kind="tree", count=5):
    nodes = [{"id": "n" + str(i), "label": "Node " + str(i)} for i in range(count)]
    item = {"id": "graph", "type": "component", "component": "topology", "frame": [60, 130, 1160, 540],
            "layout": kind, "nodes": nodes}
    if kind in {"tree", "layered"}:
        item["edges"] = [{"id": "e" + str(i), "from": "n0", "to": "n" + str(i)} for i in range(1, count)]
    return item


class PresentationTopologyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tokens = load_template()[2]

    def lower(self, item, facts=None, tokens=None):
        return lower_topology(item, facts or {}, [1280, 720], tokens or self.tokens)

    def test_catalog_exposes_executable_scope_and_detached_examples(self):
        catalog = topology_catalog(tokens=self.tokens)
        self.assertEqual(set(catalog["definitions"]), {"tree", "layered", "radial", "cycle", "arch"})
        self.assertEqual(catalog["connectors"]["presets"], ["line"])
        self.assertIn("not supported", catalog["connectors"]["labels"])
        catalog["examples"]["tree"]["nodes"][0]["label"] = "Changed"
        self.assertEqual(topology_catalog("tree", self.tokens)["examples"]["tree"]["nodes"][0]["label"], "Node A")
        with self.assertRaisesRegex(TemplateInputError, "unknown topology"):
            topology_catalog("unknown")
        for item in topology_catalog(tokens=self.tokens)["examples"].values():
            self.lower(item)

    def test_node_count_changes_graph_geometry_and_edge_endpoints(self):
        for kind in ("tree", "layered", "radial", "cycle", "arch"):
            for count in (3, 5, 7):
                with self.subTest(kind=kind, count=count):
                    group = self.lower(topology(kind, count))
                    report = group["metadata"]["topology_report"]
                    self.assertEqual(report["node_count"], count)
                    shapes = {c["id"] for c in group["children"] if c["type"] == "shape"}
                    edges = [c for c in group["children"] if c["type"] == "connector"]
                    self.assertEqual(len(edges), count if kind == "cycle" else (0 if kind == "arch" else count - 1))
                    for edge in edges:
                        self.assertIn(edge["from"], shapes)
                        self.assertIn(edge["to"], shapes)
                        self.assertEqual(edge["preset"], "line")
                        self.assertIn(edge["from_port"], {"top", "bottom", "left", "right"})
                    self.assertEqual(len(report["node_frames"]), count)

    def test_build_is_deterministic_does_not_mutate_author_and_preserves_source_metadata(self):
        item = topology()
        item.update(source_ref="source#figure", metadata={"authored": True})
        original = copy.deepcopy(item)
        first, second = self.lower(item), self.lower(item)
        self.assertEqual(first, second)
        self.assertEqual(item, original)
        self.assertEqual(first["source_ref"], "source#figure")
        self.assertTrue(first["metadata"]["authored"])

    def test_actual_font_measurement_changes_node_height_without_shrinking(self):
        item = topology(count=3)
        item["node_width"] = 170
        item["nodes"][1]["label"] = ["Measured: ", {"ref": "value"}]
        short = self.lower(item, {"value": "short"})
        long = self.lower(item, {"value": "Many words wrap over more lines to show that the text stays at the same font size."})
        first, second = short["metadata"]["topology_report"], long["metadata"]["topology_report"]
        self.assertGreater(second["node_frames"]["n1"][3], first["node_frames"]["n1"][3])
        self.assertGreater(second["measurements"]["n1"]["lines"], 1)
        self.assertEqual(second["measurements"]["n1"]["font_size"], self.tokens["font"]["sizes"]["body"])
        # A longer child changes its rank's position instead of overwriting the saved author frame.
        self.assertNotEqual(second["node_frames"]["n1"][1], first["node_frames"]["n1"][1])

    def test_explicit_insufficient_height_reports_capacity_and_exact_node(self):
        item = topology(count=3)
        item["nodes"][1]["height"] = 10
        with self.assertRaises(TopologyError) as raised:
            self.lower(item)
        self.assertEqual(raised.exception.diagnostic["node_id"], "n1")
        self.assertEqual(raised.exception.diagnostic["reason"], "text_overflow")
        self.assertGreater(raised.exception.diagnostic["overflow_px"], 0)

    def test_theme_and_role_are_used_for_node_text_and_solid_paint(self):
        tokens = copy.deepcopy(self.tokens)
        tokens["font"]["sizes"]["body"] = 18
        tokens["font"]["families"]["body"] = "Arial"
        item = topology(count=3)
        item["style"] = {"fill": "#EFF8F2", "stroke": "#285A42"}
        group = self.lower(item, tokens=tokens)
        label = next(c for c in group["children"] if c["type"] == "text")
        self.assertEqual(label["style"]["font_size"], 18)
        self.assertEqual(label["style"]["font_family"], "Arial")
        shape = next(c for c in group["children"] if c["type"] == "shape")
        self.assertEqual(shape["fill"], "#EFF8F2")
        self.assertEqual(shape["stroke"], "#285A42")

    def test_tree_and_layered_reject_directed_cycles(self):
        for kind in ("tree", "layered"):
            item = topology(kind, 3)
            item["edges"] = [{"id": "ab", "from": "n0", "to": "n1"}, {"id": "bc", "from": "n1", "to": "n2"},
                             {"id": "ca", "from": "n2", "to": "n0"}]
            with self.assertRaises(TopologyError) as raised:
                self.lower(item)
            self.assertEqual(raised.exception.diagnostic["reason"], "directed_cycle")

    def test_tree_rejects_multiple_roots_and_multiple_parents(self):
        item = topology(count=4)
        item["edges"] = [{"id": "ab", "from": "n0", "to": "n2"}, {"id": "bc", "from": "n1", "to": "n2"},
                         {"id": "cd", "from": "n2", "to": "n3"}]
        with self.assertRaises(TopologyError) as raised:
            self.lower(item)
        self.assertEqual(raised.exception.diagnostic["reason"], "invalid_tree")
        item["layout"] = "layered"
        group = self.lower(item)
        self.assertEqual(len(group["metadata"]["topology_report"]["layers"]), 3)

    def test_orphan_unknown_endpoint_duplicate_edge_and_bad_port_style_reject(self):
        mutations = [
            (lambda a: a["edges"].pop(), "orphan_nodes"),
            (lambda a: a["edges"][0].update(to="missing"), "unknown_endpoint"),
            (lambda a: a["edges"].append({"id": "copy", "from": "n0", "to": "n1"}), "invalid_input"),
            (lambda a: a["edges"][0].update(preset="bentConnector3"), "unsupported_route"),
            (lambda a: a["edges"][0].update(label="Not silently dropped"), "unsupported_route"),
        ]
        for mutate, reason in mutations:
            item = topology(count=3)
            mutate(item)
            with self.assertRaises(TopologyError) as raised:
                self.lower(item)
            self.assertEqual(raised.exception.diagnostic["reason"], reason)

    def test_radial_rejects_non_spoke_edges_and_cycle_requires_ordered_closed_graph(self):
        item = topology("radial", 3)
        item["edges"] = [{"id": "a", "from": "n0", "to": "n1"}, {"id": "b", "from": "n1", "to": "n2"}]
        with self.assertRaisesRegex(TopologyError, "center and a spoke"):
            self.lower(item)
        item = topology("cycle", 4)
        item["edges"] = [{"id": str(i) + "bad", "from": "n" + str(i), "to": "n" + str((i+2) % 4)} for i in range(4)]
        # IDs must be SVG compatible; use valid IDs so the graph contract is reached.
        for edge in item["edges"]:
            edge["id"] = "e" + edge["id"]
        with self.assertRaisesRegex(TopologyError, "closed input node order"):
            self.lower(item)
        with self.assertRaisesRegex(TopologyError, "at least three"):
            self.lower(topology("cycle", 2))

    def test_horizontal_layered_positions_and_bounded_reordering(self):
        item = topology("layered", 5)
        item["direction"] = "right"
        item["nodes"] = item["nodes"][:3]
        item["edges"] = [{"id": "a", "from": "n0", "to": "n1"}, {"id": "b", "from": "n1", "to": "n2"}]
        report = self.lower(item)["metadata"]["topology_report"]
        self.assertEqual(report["layers"], [["n0"], ["n1"], ["n2"]])
        self.assertLess(report["node_frames"]["n0"][0], report["node_frames"]["n1"][0])
        self.assertIn("barycenter-4", report["algorithm"])

    def test_crowded_graph_rejects_and_large_explicit_nodes_do_not_escape(self):
        for item in (topology("radial", 45), topology("cycle", 45), topology("tree", 40), topology("arch", 40)):
            with self.assertRaises(TopologyError):
                self.lower(item)
        item = topology(count=3)
        item["node_width"] = 1500
        with self.assertRaises(TopologyError):
            self.lower(item)

    def test_invalid_capacity_numbers_ids_and_arch_only_fields_reject(self):
        cases = [
            {"nodes": []}, {"node_gap": -1}, {"node_width": True},
            {"nodes": [{"id": "same", "label": "A"}, {"id": "same", "label": "B"}]},
            {"nodes": [{"id": "a", "label": "A"}], "edges": [{"id": "x", "from": [], "to": "a"}]},
            {"interior": {"id": "unused", "type": "column", "children": []}},
        ]
        for update in cases:
            item=topology(count=3)
            item.update(update)
            with self.subTest(update=update), self.assertRaises(TemplateInputError):
                self.lower(item)
        item=topology("radial",3)
        item["center_id"]=[]
        with self.assertRaises(TopologyError):
            self.lower(item)

    def test_arch_band_can_be_disabled_and_invalid_thickness_marker_text_reject(self):
        item=topology("arch",5)
        item["band"]=False
        self.assertFalse(any(c["id"].endswith("--arch-band") for c in self.lower(item)["children"]))
        item["band"]={"thickness":1000}
        with self.assertRaises(TopologyError):
            self.lower(item)
        item["band"]=True
        item["nodes"][0]["marker"]="A very long marker"
        with self.assertRaises(TopologyError):
            self.lower(item)

    def test_long_layer_skipping_edge_cannot_cross_an_intermediate_node(self):
        item = topology("layered", 3)
        item["edges"] = [{"id": "a", "from": "n0", "to": "n1"}, {"id": "b", "from": "n1", "to": "n2"},
                         {"id": "skip", "from": "n0", "to": "n2"}]
        with self.assertRaises(TopologyError) as raised:
            self.lower(item)
        self.assertEqual(raised.exception.diagnostic["reason"], "edge_obstruction")
        self.assertEqual(raised.exception.diagnostic["edge_id"], "skip")

    def test_arch_eleven_external_nodes_measured_labels_and_editable_band(self):
        item = topology("arch", 11)
        for i, node in enumerate(item["nodes"]):
            node["label"] = "行业" + str(i)
        item["nodes"][5]["marker"] = "A"
        group = self.lower(item)
        report = group["metadata"]["topology_report"]
        self.assertEqual(report["node_count"], 11)
        band = next(c for c in group["children"] if c["id"] == "graph--arch-band")
        self.assertEqual(band["shape"], "path")
        self.assertEqual(band["fill"], "surfaceMuted")
        self.assertIn(" A ", band["d"])
        self.assertTrue(any(c["id"].endswith("--marker") for c in group["children"]))
        for identifier, box in report["node_frames"].items():
            cx, cy = report["ellipse"]["center"]
            rx, ry = report["ellipse"]["radii"]
            self.assertAlmostEqual(((box[0]+box[2]/2-cx)/rx)**2 + ((box[1]+box[3]/2-cy)/ry)**2, 1)
            self.assertEqual(len(report["occupied_frames"][identifier]), 2)

    def test_arch_interior_grid_column_row_and_components_use_safe_rectangle(self):
        item = topology("arch", 7)
        item["interior"] = {"id": "capabilities", "type": "column", "gap": 12, "children": [
            {"id": "heading", "type": "leaf", "element": {"type": "text", "text": "Shared layer"}},
            {"id": "cards", "type": "grid", "columns": [{"fr": 1}, {"fr": 1}], "gap": 12, "children": [
                {"id": "card-a", "type": "leaf", "element": {"type": "text", "text": "Capability A"}},
                {"id": "card-b", "type": "leaf", "element": {"type": "text", "text": "Capability B"}}]},
            {"id": "base", "type": "row", "gap": 12, "children": [
                {"id": "base-text", "type": "leaf", "grow": 1, "element": {"type": "text", "text": "Foundation"}},
                {"id": "normal-component", "type": "leaf", "grow": 1, "basis": 0, "height": 65, "element": {
                    "type": "component", "component": "paragraph-flow", "paragraphs": [{"id": "p", "text": "Native content"}]}}]}]}
        original = copy.deepcopy(item)
        group = self.lower(item)
        report = group["metadata"]["topology_report"]
        x,y,w,h = report["interior_bounds"]
        cx,cy = report["ellipse"]["center"]
        rx,ry = report["interior_ellipse_radii"]
        for px,py in ((x,y),(x+w,y),(x,y+h),(x+w,y+h)):
            self.assertLessEqual(((px-cx)/rx)**2+((py-cy)/ry)**2, 1+1e-8)
        internal = [c for c in group["children"] if c["id"].startswith("graph--interior--")]
        self.assertGreaterEqual(len(internal), 5)
        self.assertTrue(any(c["type"] == "component" for c in internal))
        for child in internal:
            bx,by,bw,bh = child["frame"]
            self.assertGreaterEqual(bx, x-.01)
            self.assertGreaterEqual(by, y-.01)
            self.assertLessEqual(bx+bw, x+w+.01)
            self.assertLessEqual(by+bh, y+h+.01)
        self.assertEqual(item, original)

    def test_arch_rejects_recursive_topology_and_excessive_interior_capacity(self):
        item = topology("arch", 5)
        item["interior"] = {"id": "nested", "type": "leaf", "height": 30,
                            "element": {"type": "component", "component": "topology", "layout": "cycle", "nodes": []}}
        with self.assertRaises(TopologyError) as raised:
            self.lower(item)
        self.assertEqual(raised.exception.diagnostic["reason"], "recursive_topology")
        item["interior"] = {"id": "oversized", "type": "leaf", "height": 1000, "element": {"type": "shape", "fill": "primary"}}
        with self.assertRaises(TemplateInputError):
            self.lower(item)

    def test_arch_edges_cannot_cut_across_reserved_interior(self):
        item = topology("arch", 5)
        item["edges"] = [{"id": "across", "from": "n0", "to": "n4"}]
        item["interior"] = {"id": "inside", "type": "leaf", "element": {"type": "text", "text": "Inner content"}}
        # Endpoint chord at the baseline is tangent to the safe interior; use elevated nodes instead.
        item["edges"][0].update(**{"from": "n0", "to": "n3"})
        with self.assertRaises(TopologyError) as raised:
            self.lower(item)
        self.assertEqual(raised.exception.diagnostic["reason"], "edge_obstruction")

    def test_native_svg_has_same_scope_real_endpoint_ids_and_arrow_markers(self):
        item = topology(count=3)
        item["arrow"] = True
        group = self.lower(item)
        svg, _, _ = SceneRenderer({"id": "page", "elements": [group]}, self.tokens, None, resolve_text, resolve_value, {}).render()
        root = ET.fromstring(svg)
        native = root.find("{*}g")
        self.assertEqual(native.get("data-pptx-object"), "group")
        shapes = {e.get("data-pptx-shape-id") for e in native if e.tag.rsplit("}", 1)[-1] == "rect"}
        edges = [e for e in native if e.get("data-pptx-object") == "connector"]
        self.assertEqual(len(edges), 2)
        for edge in edges:
            self.assertIn(edge.get("data-pptx-start-shape-id"), shapes)
            self.assertIn(edge.get("data-pptx-end-shape-id"), shapes)
            self.assertIsNotNone(edge.get("data-pptx-start-site"))
            self.assertIsNotNone(edge.get("data-pptx-end-site"))
            self.assertTrue(edge.get("marker-end").startswith("url("))

    def test_normal_build_exports_real_native_groups_text_and_connected_edges(self):
        from presentation_compiler import build_project
        import ppt_runtime
        item = topology(count=3)
        item["arrow"] = True
        document = {"schema_version": "0.1", "project_id": "topology-native", "revision": 1, "brief": {}, "facts": {},
                    "pages": [{"id": "p1", "kind": "scene", "elements": [item]},
                              {"id": "p2", "kind": "scene", "elements": [topology("arch", 5)]}]}
        # Author IDs are page-global in this engine; use a distinct second topology ID.
        document["pages"][1]["elements"][0]["id"] = "arch"
        with tempfile.TemporaryDirectory(prefix="topology-native-") as temp:
            target, output = Path(temp) / "project", Path(temp) / "topology.pptx"
            build_project(document, target)
            ppt_runtime.check_project(target, target / "tokens.json")
            ppt_runtime.export_project(target, output, target / "tokens.json")
            with ZipFile(output) as archive:
                root = ET.fromstring(archive.read("ppt/slides/slide1.xml"))
                ns = {"p": "http://schemas.openxmlformats.org/presentationml/2006/main",
                      "a": "http://schemas.openxmlformats.org/drawingml/2006/main"}
                group = root.find(".//p:grpSp", ns)
                self.assertIsNotNone(group)
                shape_ids = {n.get("id") for n in group.findall("p:sp/p:nvSpPr/p:cNvPr", ns)}
                connectors = group.findall("p:cxnSp", ns)
                self.assertEqual(len(connectors), 2)
                for edge in connectors:
                    self.assertIn(edge.find("p:nvCxnSpPr/p:cNvCxnSpPr/a:stCxn", ns).get("id"), shape_ids)
                    self.assertIn(edge.find("p:nvCxnSpPr/p:cNvCxnSpPr/a:endCxn", ns).get("id"), shape_ids)
                    ends=edge.findall("p:spPr/a:ln/a:tailEnd",ns)+edge.findall("p:spPr/a:ln/a:headEnd",ns)
                    self.assertTrue(any(e.get("type") not in (None,"none") for e in ends))
                self.assertIn("Node 0", "".join(root.itertext()))
                arch = ET.fromstring(archive.read("ppt/slides/slide2.xml"))
                self.assertIsNotNone(arch.find(".//a:custGeom", ns))


if __name__ == "__main__":
    unittest.main()
