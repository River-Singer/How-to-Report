"""Independent checks of palette semantics in the actual rendered chart SVG."""
import unittest
from xml.etree import ElementTree as ET

import test_presentation_chart_assets as base
from presentation_palette import apply_palette, contrast_ratio, describe_palette

SVG = base.SVG


class PaletteReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        base.ChartAssetsTests.setUpClass()
        cls.tokens = base.ChartAssetsTests.tokens

    def render(self, chart, data, palette):
        author = base.charts.chart_story(chart, data)
        tokens = apply_palette(self.tokens, palette)
        scene, _ = base.lower_layout_page(author['pages'][0], {}, (1280, 720), tokens)
        svg, _, _ = base.SceneRenderer(scene, tokens, None, base.resolve_text, base.resolve_value, {}).render()
        xml = ET.fromstring(svg)
        return next(n for n in xml.iter(SVG + 'g') if n.get('id') == 'chart')

    def test_signed_heatmap_midpoint_and_legend_keep_same_colour_meaning(self):
        data = {'coordinates': 'planar', 'x': [0, 1], 'y': [0, 1],
                'values': [[-2, 0], [0, 2]], 'levels': [-1, 1]}
        chart = self.render('map-heatmap', data, 'carbon-indigo')
        rectangles = list(chart.iter(SVG + 'rect'))
        cells = [r for r in rectangles if float(r.get('width')) > 20]
        legend = [r for r in rectangles if float(r.get('width')) < 20]
        self.assertEqual(len(cells), 4)
        self.assertEqual(len(legend), 3)
        self.assertEqual([c.get('fill') for c in cells],
                         [legend[i].get('fill') for i in [0, 1, 1, 2]])
        self.assertEqual(legend[1].get('fill'), describe_palette('carbon-indigo')['diverging'][1])
        self.assertNotEqual(legend[0].get('fill'), legend[2].get('fill'))

    def test_voronoi_small_labels_reach_contrast_on_actual_fills(self):
        data = {'bounds': [0, 0, 6, 4], 'sites': [
            {'label': name, 'point': list(point)} for name, point in
            zip('ABCDEF', [(1, 1), (3, 1), (5, 1), (1, 3), (3, 3), (5, 3)])]}
        for palette in ('ant-business', 'carbon-teal', 'carbon-indigo', 'nord-report'):
            with self.subTest(palette=palette):
                chart = self.render('voronoi', data, palette)
                regions = list(chart.iter(SVG + 'path'))
                labels = [t for t in chart.iter(SVG + 'text') if t.text in 'ABCDEF']
                self.assertEqual(len(regions), 6)
                self.assertEqual(len(labels), 6)
                for region, label in zip(regions, labels):
                    self.assertGreaterEqual(contrast_ratio(region.get('fill'), label.get('fill')), 4.5)


if __name__ == '__main__':
    unittest.main()
