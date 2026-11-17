"""Independent quantitative regression checks for chart coordinate semantics."""
from __future__ import annotations

import re
import unittest

import test_presentation_chart_assets as base

SVG = base.SVG


class ChartReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        base.ChartAssetsTests.setUpClass()
        cls.renderer = base.ChartAssetsTests()

    def test_signed_stacks_use_one_zero_origin_and_separate_positive_negative_sums(self):
        data = {"categories": ["A"], "series": [
            {"name": "First", "values": [10]}, {"name": "Second", "values": [-5]},
            {"name": "Third", "values": [20]}, {"name": "Fourth", "values": [-15]}]}
        xml, _, _ = self.renderer.render("diverging-stacked-bar", data)
        chart = next(n for n in xml.iter(SVG + "g") if n.get("id") == "chart")
        bars = [r for r in chart.iter(SVG + "rect") if float(r.get("height")) > 20]
        self.assertEqual(len(bars), 4)
        x = [float(r.get("x")) for r in bars]
        w = [float(r.get("width")) for r in bars]
        zero = x[0]
        self.assertAlmostEqual(x[1] + w[1], zero, places=2)
        self.assertAlmostEqual(x[2], x[0] + w[0], places=2)
        self.assertAlmostEqual(x[3] + w[3], x[1], places=2)
        self.assertAlmostEqual(w[2] / w[0], 2, places=3)
        self.assertAlmostEqual(w[3] / w[1], 3, places=3)

    def test_pie_area_tracks_shares_and_does_not_give_zero_a_slice(self):
        xml, _, _ = self.renderer.render("pie", {"categories": ["A", "B", "Zero"],
            "series": [{"name": "Parts", "values": [1, 3, 0]}]})
        chart = next(n for n in xml.iter(SVG + "g") if n.get("id") == "chart")
        sectors = list(chart.iter(SVG + "path"))
        self.assertEqual(len(sectors), 2)
        def area(path):
            numbers = [float(n) for n in re.findall(r"-?\d+(?:\.\d+)?", path.get("d"))]
            pts = list(zip(numbers[::2], numbers[1::2]))
            return abs(sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(pts, pts[1:] + pts[:1]))) / 2
        self.assertAlmostEqual(area(sectors[1]) / area(sectors[0]), 3, places=3)
        self.assertTrue(any("Zero" in (n.text or "") and "0.0%" in n.text for n in chart.iter(SVG + "text")))

    def test_ecdf_ties_add_empirical_mass_and_reach_one(self):
        xml, _, _ = self.renderer.render("cumulative-curve", {"series": [{"name": "Sample", "values": [0, 0, 1, 4]}]})
        chart = next(n for n in xml.iter(SVG + "g") if n.get("id") == "chart")
        path = next(chart.iter(SVG + "path"))
        coordinates = [float(n) for n in re.findall(r"-?\d+(?:\.\d+)?", path.get("d"))]
        points = list(zip(coordinates[::2], coordinates[1::2]))
        bottom, top = points[0][1], points[-1][1]
        at_minimum = [y for x, y in points if abs(x - points[0][0]) < .01]
        self.assertAlmostEqual((bottom - min(at_minimum)) / (bottom - top), .5, places=3)
        axes_one = next(n for n in chart.iter(SVG + "text") if n.text == "1")
        expected_top = float(axes_one.get("y")) - .3 * float(axes_one.get("font-size"))
        self.assertAlmostEqual(top, expected_top, places=2)

    def test_fan_category_labels_share_actual_data_x_positions(self):
        data = {"categories": ["first", "middle", "last"], "ranges": [
            {"low": 1, "value": 2, "high": 3},
            {"low": 2, "value": 4, "high": 5},
            {"low": 3, "value": 5, "high": 7}]}
        xml, _, _ = self.renderer.render("fan-chart", data)
        paths = list(xml.iter(SVG + "path"))
        central = next(p for p in paths if p.get("fill") == "none")
        coordinates = [float(n) for n in re.findall(r"-?\d+(?:\.\d+)?", central.get("d"))]
        labels = {n.text: float(n.get("x")) for n in xml.iter(SVG + "text") if n.text in data["categories"]}
        for label, x in zip(data["categories"], coordinates[::2]):
            self.assertAlmostEqual(labels[label], x, places=2)

    def test_heatmap_legend_covers_bins_with_identical_plot_colours(self):
        data = {"coordinates": "planar", "x": [0, 1], "y": [0, 1],
                "values": [[0, 10], [15, 25]], "levels": [10, 20]}
        xml, _, _ = self.renderer.render("map-heatmap", data)
        chart = next(n for n in xml.iter(SVG + "g") if n.get("id") == "chart")
        rectangles = list(chart.iter(SVG + "rect"))
        cells = [r for r in rectangles if float(r.get("width")) > 20]
        legend = [r for r in rectangles if float(r.get("width")) < 20]
        self.assertEqual(len(cells), 4)
        self.assertEqual(len(legend), 3)
        self.assertEqual([c.get("fill") for c in cells],
                         [legend[i].get("fill") for i in [0, 0, 1, 2]])
        labels = {n.text for n in xml.iter(SVG + "text")}
        self.assertTrue({"≤10", "(10, 20]", ">20"} <= labels)


if __name__ == "__main__":
    unittest.main()
