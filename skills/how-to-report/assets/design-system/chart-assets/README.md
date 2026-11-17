# PPT engine chart asset handbook

This catalogue contains 68 executable chart assets across the nine FT Visual Vocabulary categories. Each asset accepts data, validates its contract and calculates geometry inside the engine. AI selects an asset ID and supplies data; no user-authored coordinates, font overrides or raster chart screenshots are accepted.

## Output and typography

- Output: native editable PowerPoint vector shapes and text. These are not Excel-linked PowerPoint chart objects; edit data in the request and rebuild to recompute.
- Authoring: a chart leaf lives inside a persistent computed layout tree. The engine owns its final frame.
- Typography: report-14pt profile; body text14pt, chart dataCaption9pt, all label colours resolve through theme tokens to80% black. Captions outside the chart use the muted annotation role. No smaller label fallback.
- Capacity: measured labels that cannot fit are rejected. Increase the container, shorten labels, aggregate with an explicit rule or split the page.
- Fill: solid fills and discrete sequential value colours. No SVG linear/radial gradients.
- Examples below are synthetic algorithm demonstrations, including the invented square regions. They are not evidence about any company, population or real geographic boundary.

## Choosing a chart

Start with the relationship in the data. Confirm units, time windows, populations and denominators before choosing a chart. Distribution charts require observations, geographic charts require coordinates or boundaries, and flow charts require explicit links. The engine cannot infer causes, missing business facts, forecasts, geographic boundaries or stakeholder decisions.

The compiler checks geometry and numeric contracts; the report workflow still checks audience relevance, evidence, appropriate chart choice and truthful claims. Data requests for the author must remain outside leadership-facing slides.

## Categories

- **deviation**: chart.diverging-bar, chart.diverging-stacked-bar, chart.spine, chart.surplus-deficit-filled-line
- **correlation**: chart.scatterplot, chart.column-line, chart.connected-scatterplot, chart.bubble, chart.xy-heatmap
- **change-over-time**: chart.column-line, chart.connected-scatterplot, chart.slope, chart.line, chart.column, chart.area, chart.candlestick, chart.fan-chart, chart.calendar-heatmap, chart.priestley-timeline, chart.circle-timeline, chart.vertical-timeline, chart.seismogram, chart.streamgraph
- **ranking**: chart.ordered-bar, chart.ordered-column, chart.ordered-proportional-symbol, chart.dot-strip-plot, chart.slope, chart.lollipop, chart.bump
- **distribution**: chart.dot-strip-plot, chart.histogram, chart.dot-plot, chart.barcode-plot, chart.boxplot, chart.violin-plot, chart.population-pyramid, chart.cumulative-curve, chart.frequency-polygons, chart.beeswarm
- **magnitude**: chart.lollipop, chart.column, chart.bar, chart.paired-column, chart.paired-bar, chart.marimekko, chart.proportional-symbol, chart.isotype, chart.radar, chart.parallel-coordinates, chart.bullet, chart.grouped-symbol, chart.proportional-stacked-bar
- **part-to-whole**: chart.marimekko, chart.stacked-column-bar, chart.pie, chart.doughnut, chart.treemap, chart.voronoi, chart.arc, chart.gridplot, chart.venn, chart.waterfall, chart.proportional-stacked-bar, chart.sunburst
- **flow**: chart.waterfall, chart.sankey, chart.chord, chart.network
- **spatial**: chart.choropleth, chart.map-proportional-symbol, chart.flow-map, chart.contour-map, chart.equalised-cartogram, chart.scaled-cartogram, chart.dot-density, chart.map-heatmap

## Calling the engine

```python
from presentation_chart_assets import chart_assets, describe_chart_asset, instantiate_chart_asset, chart_story
from presentation_compiler import build_project

detail = describe_chart_asset("chart.doughnut")
leaf = instantiate_chart_asset(detail["id"], data, options={})  # no frame; insert in layout tree
author = chart_story(detail["id"], data, options={"title": "A supported conclusion"})
build_project(author, output_dir, geometry_policy="computed")
```

`describe_chart_asset` returns a real JSON Schema, its example, use cases, contraindications and exact capability limits. Structural schema validation is followed by semantic checks: finite numbers, array alignment, unique keys, positive totals, distribution requirements, flow conservation and measured capacity. `show_values=false` is allowed only for Sankey; unknown or irrelevant options are rejected.

## Asset contracts and synthetic requests

### Diverging bar — `chart.diverging-bar`

- Status: executable; editable native vectors.
- Categories: deviation
- Required data: `series`, `categories`
- Options: `note`, `title`
- Use: 比较相对零点或明确参考值的正负偏差。
- Avoid: Do not invent missing data or replace unknown values with zero. Keep units, populations, periods and denominators comparable.
- Limits: PPT output is editable shapes; change the data and rebuild to recalculate. It is not an Excel-linked native chart. Examples are synthetic. This contract does not establish business comparability or causality. Category positions are equally spaced; irregular time intervals require connected-scatterplot with numeric time coordinates.

```json
{
  "asset": "chart.diverging-bar",
  "data": {
    "categories": [
      "A",
      "B",
      "C",
      "D"
    ],
    "series": [
      {
        "name": "Observed",
        "values": [
          25,
          -10,
          30,
          -15
        ]
      }
    ]
  },
  "options": {}
}
```

### Diverging stacked bar — `chart.diverging-stacked-bar`

- Status: executable; editable native vectors.
- Categories: deviation
- Required data: `series`, `categories`
- Options: `note`, `title`
- Use: 比较相对零点或明确参考值的正负偏差。
- Avoid: Do not invent missing data or replace unknown values with zero. Keep units, populations, periods and denominators comparable.
- Limits: PPT output is editable shapes; change the data and rebuild to recalculate. It is not an Excel-linked native chart. Examples are synthetic. This contract does not establish business comparability or causality. Category positions are equally spaced; irregular time intervals require connected-scatterplot with numeric time coordinates.

```json
{
  "asset": "chart.diverging-stacked-bar",
  "data": {
    "categories": [
      "A",
      "B",
      "C",
      "D"
    ],
    "series": [
      {
        "name": "Observed",
        "values": [
          25,
          -10,
          30,
          -15
        ]
      },
      {
        "name": "Reference",
        "values": [
          35,
          28,
          45,
          42
        ]
      }
    ]
  },
  "options": {}
}
```

### Spine — `chart.spine`

- Status: executable; editable native vectors.
- Categories: deviation
- Required data: `series`, `categories`
- Options: `note`, `title`
- Use: 比较相对零点或明确参考值的正负偏差。
- Avoid: Do not invent missing data or replace unknown values with zero. Keep units, populations, periods and denominators comparable. Parts must be mutually exclusive and belong to the same complete population.
- Limits: PPT output is editable shapes; change the data and rebuild to recalculate. It is not an Excel-linked native chart. Examples are synthetic. This contract does not establish business comparability or causality. Category positions are equally spaced; irregular time intervals require connected-scatterplot with numeric time coordinates. Two complementary nonnegative series, independently normalized to100% per category.

```json
{
  "asset": "chart.spine",
  "data": {
    "categories": [
      "A",
      "B",
      "C",
      "D"
    ],
    "series": [
      {
        "name": "Observed",
        "values": [
          25,
          40,
          30,
          55
        ]
      },
      {
        "name": "Reference",
        "values": [
          35,
          28,
          45,
          42
        ]
      }
    ]
  },
  "options": {}
}
```

### Surplus/deficit filled line — `chart.surplus-deficit-filled-line`

- Status: executable; editable native vectors.
- Categories: deviation
- Required data: `series`, `categories`
- Options: `note`, `title`
- Use: 比较相对零点或明确参考值的正负偏差。
- Avoid: Do not invent missing data or replace unknown values with zero. Keep units, populations, periods and denominators comparable.
- Limits: PPT output is editable shapes; change the data and rebuild to recalculate. It is not an Excel-linked native chart. Examples are synthetic. This contract does not establish business comparability or causality. Category positions are equally spaced; irregular time intervals require connected-scatterplot with numeric time coordinates. Single signed-deviation series with a zero reference. Positive and negative regions are split exactly at interpolated zero crossings.

```json
{
  "asset": "chart.surplus-deficit-filled-line",
  "data": {
    "categories": [
      "A",
      "B",
      "C",
      "D"
    ],
    "series": [
      {
        "name": "Observed",
        "values": [
          25,
          -10,
          30,
          -15
        ]
      }
    ]
  },
  "options": {}
}
```

### Scatterplot — `chart.scatterplot`

- Status: executable; editable native vectors.
- Categories: correlation
- Required data: `series`
- Options: `note`, `title`
- Use: 观察变量共同变化，不能据此声称因果。
- Avoid: Do not invent missing data or replace unknown values with zero. Keep units, populations, periods and denominators comparable. Association does not demonstrate causality. A dual axis must not imply equal units or scale.
- Limits: PPT output is editable shapes; change the data and rebuild to recalculate. It is not an Excel-linked native chart. Examples are synthetic. This contract does not establish business comparability or causality.

```json
{
  "asset": "chart.scatterplot",
  "data": {
    "series": [
      {
        "name": "A",
        "points": [
          [
            1,
            2
          ],
          [
            2,
            4
          ],
          [
            3,
            3
          ],
          [
            4,
            6
          ],
          [
            5,
            5
          ]
        ]
      }
    ]
  },
  "options": {}
}
```

### Column + line timeline — `chart.column-line`

- Status: executable; editable native vectors.
- Categories: correlation, change-over-time
- Required data: `series`, `categories`, `series_units`
- Options: `note`, `title`
- Use: 观察变量共同变化，不能据此声称因果。 显示有顺序的时间变化，保持期间与频率一致。
- Avoid: Do not invent missing data or replace unknown values with zero. Keep units, populations, periods and denominators comparable. Order must have an explicit meaning; equal category spacing assumes equal time intervals. Association does not demonstrate causality. A dual axis must not imply equal units or scale.
- Limits: PPT output is editable shapes; change the data and rebuild to recalculate. It is not an Excel-linked native chart. Examples are synthetic. This contract does not establish business comparability or causality. Category positions are equally spaced; irregular time intervals require connected-scatterplot with numeric time coordinates. Exactly two series with explicit units. Bars use the left axis and line the right axis; independent scales are always labelled.

```json
{
  "asset": "chart.column-line",
  "data": {
    "categories": [
      "A",
      "B",
      "C",
      "D"
    ],
    "series": [
      {
        "name": "Observed",
        "values": [
          25,
          40,
          30,
          55
        ]
      },
      {
        "name": "Rate",
        "values": [
          0.2,
          0.3,
          0.4,
          0.35
        ]
      }
    ],
    "series_units": [
      "units",
      "ratio"
    ]
  },
  "options": {}
}
```

### Connected scatterplot — `chart.connected-scatterplot`

- Status: executable; editable native vectors.
- Categories: correlation, change-over-time
- Required data: `series`
- Options: `note`, `title`
- Use: 观察变量共同变化，不能据此声称因果。 显示有顺序的时间变化，保持期间与频率一致。
- Avoid: Do not invent missing data or replace unknown values with zero. Keep units, populations, periods and denominators comparable. Association does not demonstrate causality. A dual axis must not imply equal units or scale.
- Limits: PPT output is editable shapes; change the data and rebuild to recalculate. It is not an Excel-linked native chart. Examples are synthetic. This contract does not establish business comparability or causality.

```json
{
  "asset": "chart.connected-scatterplot",
  "data": {
    "series": [
      {
        "name": "A",
        "points": [
          [
            1,
            2
          ],
          [
            2,
            4
          ],
          [
            3,
            3
          ],
          [
            4,
            6
          ],
          [
            5,
            5
          ]
        ]
      }
    ]
  },
  "options": {}
}
```

### Bubble — `chart.bubble`

- Status: executable; editable native vectors.
- Categories: correlation
- Required data: `series`
- Options: `note`, `title`
- Use: 观察变量共同变化，不能据此声称因果。
- Avoid: Do not invent missing data or replace unknown values with zero. Keep units, populations, periods and denominators comparable. Association does not demonstrate causality. A dual axis must not imply equal units or scale.
- Limits: PPT output is editable shapes; change the data and rebuild to recalculate. It is not an Excel-linked native chart. Examples are synthetic. This contract does not establish business comparability or causality.

```json
{
  "asset": "chart.bubble",
  "data": {
    "series": [
      {
        "name": "A",
        "points": [
          [
            1,
            2,
            10
          ],
          [
            2,
            4,
            20
          ],
          [
            3,
            3,
            35
          ],
          [
            4,
            6,
            15
          ]
        ]
      }
    ]
  },
  "options": {}
}
```

### XY heatmap — `chart.xy-heatmap`

- Status: executable; editable native vectors.
- Categories: correlation
- Required data: `x_labels`, `y_labels`, `values`
- Options: `note`, `title`
- Use: 观察变量共同变化，不能据此声称因果。
- Avoid: Do not invent missing data or replace unknown values with zero. Keep units, populations, periods and denominators comparable.
- Limits: PPT output is editable shapes; change the data and rebuild to recalculate. It is not an Excel-linked native chart. Examples are synthetic. This contract does not establish business comparability or causality.

```json
{
  "asset": "chart.xy-heatmap",
  "data": {
    "x_labels": [
      "A",
      "B",
      "C"
    ],
    "y_labels": [
      "Group 1",
      "Group 2"
    ],
    "values": [
      [
        2,
        8,
        4
      ],
      [
        7,
        3,
        9
      ]
    ]
  },
  "options": {}
}
```

### Ordered bar — `chart.ordered-bar`

- Status: executable; editable native vectors.
- Categories: ranking
- Required data: `series`, `categories`
- Options: `note`, `title`
- Use: 比较有序位置，保留同口径和并列关系。
- Avoid: Do not invent missing data or replace unknown values with zero. Keep units, populations, periods and denominators comparable.
- Limits: PPT output is editable shapes; change the data and rebuild to recalculate. It is not an Excel-linked native chart. Examples are synthetic. This contract does not establish business comparability or causality. Category positions are equally spaced; irregular time intervals require connected-scatterplot with numeric time coordinates.

```json
{
  "asset": "chart.ordered-bar",
  "data": {
    "categories": [
      "A",
      "B",
      "C",
      "D"
    ],
    "series": [
      {
        "name": "Observed",
        "values": [
          25,
          40,
          30,
          55
        ]
      }
    ]
  },
  "options": {}
}
```

### Ordered column — `chart.ordered-column`

- Status: executable; editable native vectors.
- Categories: ranking
- Required data: `series`, `categories`
- Options: `note`, `title`
- Use: 比较有序位置，保留同口径和并列关系。
- Avoid: Do not invent missing data or replace unknown values with zero. Keep units, populations, periods and denominators comparable.
- Limits: PPT output is editable shapes; change the data and rebuild to recalculate. It is not an Excel-linked native chart. Examples are synthetic. This contract does not establish business comparability or causality. Category positions are equally spaced; irregular time intervals require connected-scatterplot with numeric time coordinates.

```json
{
  "asset": "chart.ordered-column",
  "data": {
    "categories": [
      "A",
      "B",
      "C",
      "D"
    ],
    "series": [
      {
        "name": "Observed",
        "values": [
          25,
          40,
          30,
          55
        ]
      }
    ]
  },
  "options": {}
}
```

### Ordered proportional symbol — `chart.ordered-proportional-symbol`

- Status: executable; editable native vectors.
- Categories: ranking
- Required data: `series`, `categories`
- Options: `note`, `title`
- Use: 比较有序位置，保留同口径和并列关系。
- Avoid: Do not invent missing data or replace unknown values with zero. Keep units, populations, periods and denominators comparable.
- Limits: PPT output is editable shapes; change the data and rebuild to recalculate. It is not an Excel-linked native chart. Examples are synthetic. This contract does not establish business comparability or causality. Category positions are equally spaced; irregular time intervals require connected-scatterplot with numeric time coordinates.

```json
{
  "asset": "chart.ordered-proportional-symbol",
  "data": {
    "categories": [
      "A",
      "B",
      "C",
      "D"
    ],
    "series": [
      {
        "name": "Observed",
        "values": [
          25,
          40,
          30,
          55
        ]
      }
    ]
  },
  "options": {}
}
```

### Dot strip plot — `chart.dot-strip-plot`

- Status: executable; editable native vectors.
- Categories: ranking, distribution
- Required data: `series`
- Options: `note`, `title`
- Use: 比较有序位置，保留同口径和并列关系。 观察真实样本的分布、范围及异常值。
- Avoid: Do not invent missing data or replace unknown values with zero. Keep units, populations, periods and denominators comparable. Provide observed samples, not summary averages presented as a distribution.
- Limits: PPT output is editable shapes; change the data and rebuild to recalculate. It is not an Excel-linked native chart. Examples are synthetic. This contract does not establish business comparability or causality.

```json
{
  "asset": "chart.dot-strip-plot",
  "data": {
    "series": [
      {
        "name": "A",
        "values": [
          2,
          3,
          3,
          5,
          6,
          8,
          8,
          9,
          10,
          12
        ]
      },
      {
        "name": "B",
        "values": [
          4,
          4,
          6,
          7,
          8,
          9,
          10,
          14
        ]
      }
    ]
  },
  "options": {}
}
```

### Slope — `chart.slope`

- Status: executable; editable native vectors.
- Categories: ranking, change-over-time
- Required data: `series`, `categories`
- Options: `note`, `title`
- Use: 比较有序位置，保留同口径和并列关系。 显示有顺序的时间变化，保持期间与频率一致。
- Avoid: Do not invent missing data or replace unknown values with zero. Keep units, populations, periods and denominators comparable. Order must have an explicit meaning; equal category spacing assumes equal time intervals.
- Limits: PPT output is editable shapes; change the data and rebuild to recalculate. It is not an Excel-linked native chart. Examples are synthetic. This contract does not establish business comparability or causality. Category positions are equally spaced; irregular time intervals require connected-scatterplot with numeric time coordinates.

```json
{
  "asset": "chart.slope",
  "data": {
    "categories": [
      "Before",
      "After"
    ],
    "series": [
      {
        "name": "A",
        "values": [
          25,
          40
        ]
      },
      {
        "name": "B",
        "values": [
          45,
          30
        ]
      }
    ]
  },
  "options": {}
}
```

### Lollipop — `chart.lollipop`

- Status: executable; editable native vectors.
- Categories: ranking, magnitude
- Required data: `series`, `categories`
- Options: `note`, `title`
- Use: 比较有序位置，保留同口径和并列关系。 在共同尺度下比较数量大小。
- Avoid: Do not invent missing data or replace unknown values with zero. Keep units, populations, periods and denominators comparable.
- Limits: PPT output is editable shapes; change the data and rebuild to recalculate. It is not an Excel-linked native chart. Examples are synthetic. This contract does not establish business comparability or causality. Category positions are equally spaced; irregular time intervals require connected-scatterplot with numeric time coordinates.

```json
{
  "asset": "chart.lollipop",
  "data": {
    "categories": [
      "A",
      "B",
      "C",
      "D"
    ],
    "series": [
      {
        "name": "Observed",
        "values": [
          25,
          40,
          30,
          55
        ]
      }
    ]
  },
  "options": {}
}
```

### Bump — `chart.bump`

- Status: executable; editable native vectors.
- Categories: ranking
- Required data: `series`, `categories`
- Options: `note`, `title`
- Use: 比较有序位置，保留同口径和并列关系。
- Avoid: Do not invent missing data or replace unknown values with zero. Keep units, populations, periods and denominators comparable. Order must have an explicit meaning; equal category spacing assumes equal time intervals.
- Limits: PPT output is editable shapes; change the data and rebuild to recalculate. It is not an Excel-linked native chart. Examples are synthetic. This contract does not establish business comparability or causality. Category positions are equally spaced; irregular time intervals require connected-scatterplot with numeric time coordinates. Competition ranks are calculated independently at each category; ties share a rank. Rank1 appears at the top.

```json
{
  "asset": "chart.bump",
  "data": {
    "categories": [
      "A",
      "B",
      "C",
      "D"
    ],
    "series": [
      {
        "name": "Observed",
        "values": [
          25,
          40,
          30,
          55
        ]
      },
      {
        "name": "Reference",
        "values": [
          35,
          28,
          45,
          42
        ]
      }
    ]
  },
  "options": {}
}
```

### Histogram — `chart.histogram`

- Status: executable; editable native vectors.
- Categories: distribution
- Required data: `series`
- Options: `bins`, `note`, `title`
- Use: 观察真实样本的分布、范围及异常值。
- Avoid: Do not invent missing data or replace unknown values with zero. Keep units, populations, periods and denominators comparable. Provide observed samples, not summary averages presented as a distribution.
- Limits: PPT output is editable shapes; change the data and rebuild to recalculate. It is not an Excel-linked native chart. Examples are synthetic. This contract does not establish business comparability or causality. Equal-width bins across pooled observed samples; automatic bin count ceil(sqrt(n)), capped at20. Multiple distributions overlay translucent count bars.

```json
{
  "asset": "chart.histogram",
  "data": {
    "series": [
      {
        "name": "A",
        "values": [
          2,
          3,
          3,
          5,
          6,
          8,
          8,
          9,
          10,
          12
        ]
      },
      {
        "name": "B",
        "values": [
          4,
          4,
          6,
          7,
          8,
          9,
          10,
          14
        ]
      }
    ]
  },
  "options": {}
}
```

### Dot plot — `chart.dot-plot`

- Status: executable; editable native vectors.
- Categories: distribution
- Required data: `categories`, `ranges`
- Options: `note`, `title`
- Use: 观察真实样本的分布、范围及异常值。
- Avoid: Do not invent missing data or replace unknown values with zero. Keep units, populations, periods and denominators comparable.
- Limits: PPT output is editable shapes; change the data and rebuild to recalculate. It is not an Excel-linked native chart. Examples are synthetic. This contract does not establish business comparability or causality.

```json
{
  "asset": "chart.dot-plot",
  "data": {
    "categories": [
      "A",
      "B",
      "C"
    ],
    "ranges": [
      {
        "low": 10,
        "high": 40,
        "value": 25,
        "target": 30
      },
      {
        "low": 20,
        "high": 55,
        "value": 40,
        "target": 45
      },
      {
        "low": 30,
        "high": 70,
        "value": 50,
        "target": 55
      }
    ]
  },
  "options": {}
}
```

### Barcode plot — `chart.barcode-plot`

- Status: executable; editable native vectors.
- Categories: distribution
- Required data: `series`
- Options: `note`, `title`
- Use: 观察真实样本的分布、范围及异常值。
- Avoid: Do not invent missing data or replace unknown values with zero. Keep units, populations, periods and denominators comparable. Provide observed samples, not summary averages presented as a distribution.
- Limits: PPT output is editable shapes; change the data and rebuild to recalculate. It is not an Excel-linked native chart. Examples are synthetic. This contract does not establish business comparability or causality.

```json
{
  "asset": "chart.barcode-plot",
  "data": {
    "series": [
      {
        "name": "A",
        "values": [
          2,
          3,
          3,
          5,
          6,
          8,
          8,
          9,
          10,
          12
        ]
      },
      {
        "name": "B",
        "values": [
          4,
          4,
          6,
          7,
          8,
          9,
          10,
          14
        ]
      }
    ]
  },
  "options": {}
}
```

### Boxplot — `chart.boxplot`

- Status: executable; editable native vectors.
- Categories: distribution
- Required data: `series`
- Options: `note`, `title`
- Use: 观察真实样本的分布、范围及异常值。
- Avoid: Do not invent missing data or replace unknown values with zero. Keep units, populations, periods and denominators comparable. Provide observed samples, not summary averages presented as a distribution.
- Limits: PPT output is editable shapes; change the data and rebuild to recalculate. It is not an Excel-linked native chart. Examples are synthetic. This contract does not establish business comparability or causality. Linear interpolated quartiles; Tukey 1.5-IQR whiskers terminate at observed samples. Outliers stay visible.

```json
{
  "asset": "chart.boxplot",
  "data": {
    "series": [
      {
        "name": "A",
        "values": [
          2,
          3,
          3,
          5,
          6,
          8,
          8,
          9,
          10,
          12
        ]
      },
      {
        "name": "B",
        "values": [
          4,
          4,
          6,
          7,
          8,
          9,
          10,
          14
        ]
      }
    ]
  },
  "options": {}
}
```

### Violin plot — `chart.violin-plot`

- Status: executable; editable native vectors.
- Categories: distribution
- Required data: `series`
- Options: `bandwidth`, `note`, `title`
- Use: 观察真实样本的分布、范围及异常值。
- Avoid: Do not invent missing data or replace unknown values with zero. Keep units, populations, periods and denominators comparable. Provide observed samples, not summary averages presented as a distribution.
- Limits: PPT output is editable shapes; change the data and rebuild to recalculate. It is not an Excel-linked native chart. Examples are synthetic. This contract does not establish business comparability or causality. Gaussian KDE with Scott/Silverman-style bandwidth based on sample standard deviation; automatic bandwidth is recorded by formula, optional explicit bandwidth. Density support is clipped to observed pooled extrema.

```json
{
  "asset": "chart.violin-plot",
  "data": {
    "series": [
      {
        "name": "A",
        "values": [
          2,
          3,
          3,
          5,
          6,
          8,
          8,
          9,
          10,
          12
        ]
      },
      {
        "name": "B",
        "values": [
          4,
          4,
          6,
          7,
          8,
          9,
          10,
          14
        ]
      }
    ]
  },
  "options": {}
}
```

### Population pyramid — `chart.population-pyramid`

- Status: executable; editable native vectors.
- Categories: distribution
- Required data: `series`, `categories`
- Options: `note`, `title`
- Use: 观察真实样本的分布、范围及异常值。
- Avoid: Do not invent missing data or replace unknown values with zero. Keep units, populations, periods and denominators comparable.
- Limits: PPT output is editable shapes; change the data and rebuild to recalculate. It is not an Excel-linked native chart. Examples are synthetic. This contract does not establish business comparability or causality. Category positions are equally spaced; irregular time intervals require connected-scatterplot with numeric time coordinates. Two nonnegative groups on opposing sides of a zero baseline, with shared magnitude scale.

```json
{
  "asset": "chart.population-pyramid",
  "data": {
    "categories": [
      "A",
      "B",
      "C",
      "D"
    ],
    "series": [
      {
        "name": "Observed",
        "values": [
          25,
          40,
          30,
          55
        ]
      },
      {
        "name": "Reference",
        "values": [
          35,
          28,
          45,
          42
        ]
      }
    ]
  },
  "options": {}
}
```

### Cumulative curve — `chart.cumulative-curve`

- Status: executable; editable native vectors.
- Categories: distribution
- Required data: `series`
- Options: `note`, `title`
- Use: 观察真实样本的分布、范围及异常值。
- Avoid: Do not invent missing data or replace unknown values with zero. Keep units, populations, periods and denominators comparable. Provide observed samples, not summary averages presented as a distribution.
- Limits: PPT output is editable shapes; change the data and rebuild to recalculate. It is not an Excel-linked native chart. Examples are synthetic. This contract does not establish business comparability or causality. Empirical cumulative distribution (ECDF), not a cumulative monetary or percentage sum.

```json
{
  "asset": "chart.cumulative-curve",
  "data": {
    "series": [
      {
        "name": "A",
        "values": [
          2,
          3,
          3,
          5,
          6,
          8,
          8,
          9,
          10,
          12
        ]
      },
      {
        "name": "B",
        "values": [
          4,
          4,
          6,
          7,
          8,
          9,
          10,
          14
        ]
      }
    ]
  },
  "options": {}
}
```

### Frequency polygons — `chart.frequency-polygons`

- Status: executable; editable native vectors.
- Categories: distribution
- Required data: `series`
- Options: `bins`, `note`, `title`
- Use: 观察真实样本的分布、范围及异常值。
- Avoid: Do not invent missing data or replace unknown values with zero. Keep units, populations, periods and denominators comparable. Provide observed samples, not summary averages presented as a distribution.
- Limits: PPT output is editable shapes; change the data and rebuild to recalculate. It is not an Excel-linked native chart. Examples are synthetic. This contract does not establish business comparability or causality. Equal-width bins from pooled real samples; lines connect bin-centre counts. Same bin edges for every series.

```json
{
  "asset": "chart.frequency-polygons",
  "data": {
    "series": [
      {
        "name": "A",
        "values": [
          2,
          3,
          3,
          5,
          6,
          8,
          8,
          9,
          10,
          12
        ]
      },
      {
        "name": "B",
        "values": [
          4,
          4,
          6,
          7,
          8,
          9,
          10,
          14
        ]
      }
    ]
  },
  "options": {}
}
```

### Beeswarm — `chart.beeswarm`

- Status: executable; editable native vectors.
- Categories: distribution
- Required data: `series`
- Options: `note`, `title`
- Use: 观察真实样本的分布、范围及异常值。
- Avoid: Do not invent missing data or replace unknown values with zero. Keep units, populations, periods and denominators comparable. Provide observed samples, not summary averages presented as a distribution.
- Limits: PPT output is editable shapes; change the data and rebuild to recalculate. It is not an Excel-linked native chart. Examples are synthetic. This contract does not establish business comparability or causality.

```json
{
  "asset": "chart.beeswarm",
  "data": {
    "series": [
      {
        "name": "A",
        "values": [
          2,
          3,
          3,
          5,
          6,
          8,
          8,
          9,
          10,
          12
        ]
      },
      {
        "name": "B",
        "values": [
          4,
          4,
          6,
          7,
          8,
          9,
          10,
          14
        ]
      }
    ]
  },
  "options": {}
}
```

### Line — `chart.line`

- Status: executable; editable native vectors.
- Categories: change-over-time
- Required data: `series`, `categories`
- Options: `note`, `title`
- Use: 显示有顺序的时间变化，保持期间与频率一致。
- Avoid: Do not invent missing data or replace unknown values with zero. Keep units, populations, periods and denominators comparable. Order must have an explicit meaning; equal category spacing assumes equal time intervals.
- Limits: PPT output is editable shapes; change the data and rebuild to recalculate. It is not an Excel-linked native chart. Examples are synthetic. This contract does not establish business comparability or causality. Category positions are equally spaced; irregular time intervals require connected-scatterplot with numeric time coordinates.

```json
{
  "asset": "chart.line",
  "data": {
    "categories": [
      "A",
      "B",
      "C",
      "D"
    ],
    "series": [
      {
        "name": "Observed",
        "values": [
          25,
          40,
          30,
          55
        ]
      }
    ]
  },
  "options": {}
}
```

### Column — `chart.column`

- Status: executable; editable native vectors.
- Categories: change-over-time, magnitude
- Required data: `series`, `categories`
- Options: `note`, `title`
- Use: 显示有顺序的时间变化，保持期间与频率一致。 在共同尺度下比较数量大小。
- Avoid: Do not invent missing data or replace unknown values with zero. Keep units, populations, periods and denominators comparable.
- Limits: PPT output is editable shapes; change the data and rebuild to recalculate. It is not an Excel-linked native chart. Examples are synthetic. This contract does not establish business comparability or causality. Category positions are equally spaced; irregular time intervals require connected-scatterplot with numeric time coordinates.

```json
{
  "asset": "chart.column",
  "data": {
    "categories": [
      "A",
      "B",
      "C",
      "D"
    ],
    "series": [
      {
        "name": "Observed",
        "values": [
          25,
          40,
          30,
          55
        ]
      }
    ]
  },
  "options": {}
}
```

### Area chart — `chart.area`

- Status: executable; editable native vectors.
- Categories: change-over-time
- Required data: `series`, `categories`
- Options: `note`, `title`
- Use: 显示有顺序的时间变化，保持期间与频率一致。
- Avoid: Do not invent missing data or replace unknown values with zero. Keep units, populations, periods and denominators comparable. Order must have an explicit meaning; equal category spacing assumes equal time intervals.
- Limits: PPT output is editable shapes; change the data and rebuild to recalculate. It is not an Excel-linked native chart. Examples are synthetic. This contract does not establish business comparability or causality. Category positions are equally spaced; irregular time intervals require connected-scatterplot with numeric time coordinates.

```json
{
  "asset": "chart.area",
  "data": {
    "categories": [
      "A",
      "B",
      "C",
      "D"
    ],
    "series": [
      {
        "name": "Observed",
        "values": [
          25,
          40,
          30,
          55
        ]
      }
    ]
  },
  "options": {}
}
```

### Candlestick — `chart.candlestick`

- Status: executable; editable native vectors.
- Categories: change-over-time
- Required data: `categories`, `ranges`
- Options: `note`, `title`
- Use: 显示有顺序的时间变化，保持期间与频率一致。
- Avoid: Do not invent missing data or replace unknown values with zero. Keep units, populations, periods and denominators comparable.
- Limits: PPT output is editable shapes; change the data and rebuild to recalculate. It is not an Excel-linked native chart. Examples are synthetic. This contract does not establish business comparability or causality.

```json
{
  "asset": "chart.candlestick",
  "data": {
    "categories": [
      "A",
      "B",
      "C"
    ],
    "ranges": [
      {
        "low": 10,
        "high": 40,
        "open": 20,
        "close": 30
      },
      {
        "low": 20,
        "high": 55,
        "open": 45,
        "close": 30
      },
      {
        "low": 30,
        "high": 70,
        "open": 40,
        "close": 60
      }
    ]
  },
  "options": {}
}
```

### Fan chart (projections) — `chart.fan-chart`

- Status: executable; editable native vectors.
- Categories: change-over-time
- Required data: `categories`, `ranges`
- Options: `note`, `title`
- Use: 显示有顺序的时间变化，保持期间与频率一致。
- Avoid: Do not invent missing data or replace unknown values with zero. Keep units, populations, periods and denominators comparable. Order must have an explicit meaning; equal category spacing assumes equal time intervals.
- Limits: PPT output is editable shapes; change the data and rebuild to recalculate. It is not an Excel-linked native chart. Examples are synthetic. This contract does not establish business comparability or causality. One externally supplied interval band and central estimate. Engine does not produce forecasts or infer statistical confidence.

```json
{
  "asset": "chart.fan-chart",
  "data": {
    "categories": [
      "A",
      "B",
      "C"
    ],
    "ranges": [
      {
        "low": 10,
        "high": 40,
        "value": 25,
        "target": 30
      },
      {
        "low": 20,
        "high": 55,
        "value": 40,
        "target": 45
      },
      {
        "low": 30,
        "high": 70,
        "value": 50,
        "target": 55
      }
    ]
  },
  "options": {}
}
```

### Calendar heatmap — `chart.calendar-heatmap`

- Status: executable; editable native vectors.
- Categories: change-over-time
- Required data: `x_labels`, `y_labels`, `values`
- Options: `note`, `title`
- Use: 显示有顺序的时间变化，保持期间与频率一致。
- Avoid: Do not invent missing data or replace unknown values with zero. Keep units, populations, periods and denominators comparable.
- Limits: PPT output is editable shapes; change the data and rebuild to recalculate. It is not an Excel-linked native chart. Examples are synthetic. This contract does not establish business comparability or causality.

```json
{
  "asset": "chart.calendar-heatmap",
  "data": {
    "x_labels": [
      "Mon",
      "Tue",
      "Wed",
      "Thu",
      "Fri",
      "Sat",
      "Sun"
    ],
    "y_labels": [
      "Week 1",
      "Week 2"
    ],
    "values": [
      [
        1,
        3,
        8,
        5,
        2,
        0,
        0
      ],
      [
        2,
        5,
        4,
        6,
        3,
        1,
        0
      ]
    ]
  },
  "options": {}
}
```

### Priestley timeline — `chart.priestley-timeline`

- Status: executable; editable native vectors.
- Categories: change-over-time
- Required data: `rows`
- Options: `note`, `title`
- Use: 显示有顺序的时间变化，保持期间与频率一致。
- Avoid: Do not invent missing data or replace unknown values with zero. Keep units, populations, periods and denominators comparable.
- Limits: PPT output is editable shapes; change the data and rebuild to recalculate. It is not an Excel-linked native chart. Examples are synthetic. This contract does not establish business comparability or causality.

```json
{
  "asset": "chart.priestley-timeline",
  "data": {
    "rows": [
      {
        "label": "A",
        "start": 0,
        "end": 4,
        "value": 10
      },
      {
        "label": "B",
        "start": 2,
        "end": 8,
        "value": 20
      },
      {
        "label": "C",
        "start": 6,
        "end": 10,
        "value": 15
      }
    ]
  },
  "options": {}
}
```

### Circle timeline — `chart.circle-timeline`

- Status: executable; editable native vectors.
- Categories: change-over-time
- Required data: `rows`
- Options: `note`, `title`
- Use: 显示有顺序的时间变化，保持期间与频率一致。
- Avoid: Do not invent missing data or replace unknown values with zero. Keep units, populations, periods and denominators comparable.
- Limits: PPT output is editable shapes; change the data and rebuild to recalculate. It is not an Excel-linked native chart. Examples are synthetic. This contract does not establish business comparability or causality.

```json
{
  "asset": "chart.circle-timeline",
  "data": {
    "rows": [
      {
        "label": "A",
        "start": 0,
        "end": 4,
        "value": 10
      },
      {
        "label": "B",
        "start": 2,
        "end": 8,
        "value": 20
      },
      {
        "label": "C",
        "start": 6,
        "end": 10,
        "value": 15
      }
    ]
  },
  "options": {}
}
```

### Vertical timeline — `chart.vertical-timeline`

- Status: executable; editable native vectors.
- Categories: change-over-time
- Required data: `rows`
- Options: `note`, `title`
- Use: 显示有顺序的时间变化，保持期间与频率一致。
- Avoid: Do not invent missing data or replace unknown values with zero. Keep units, populations, periods and denominators comparable.
- Limits: PPT output is editable shapes; change the data and rebuild to recalculate. It is not an Excel-linked native chart. Examples are synthetic. This contract does not establish business comparability or causality.

```json
{
  "asset": "chart.vertical-timeline",
  "data": {
    "rows": [
      {
        "label": "A",
        "start": 0,
        "end": 4,
        "value": 10
      },
      {
        "label": "B",
        "start": 2,
        "end": 8,
        "value": 20
      },
      {
        "label": "C",
        "start": 6,
        "end": 10,
        "value": 15
      }
    ]
  },
  "options": {}
}
```

### Seismogram — `chart.seismogram`

- Status: executable; editable native vectors.
- Categories: change-over-time
- Required data: `series`, `categories`
- Options: `note`, `title`
- Use: 显示有顺序的时间变化，保持期间与频率一致。
- Avoid: Do not invent missing data or replace unknown values with zero. Keep units, populations, periods and denominators comparable. Order must have an explicit meaning; equal category spacing assumes equal time intervals.
- Limits: PPT output is editable shapes; change the data and rebuild to recalculate. It is not an Excel-linked native chart. Examples are synthetic. This contract does not establish business comparability or causality. Category positions are equally spaced; irregular time intervals require connected-scatterplot with numeric time coordinates.

```json
{
  "asset": "chart.seismogram",
  "data": {
    "categories": [
      "A",
      "B",
      "C",
      "D"
    ],
    "series": [
      {
        "name": "Observed",
        "values": [
          25,
          -10,
          30,
          -15
        ]
      }
    ]
  },
  "options": {}
}
```

### Streamgraph — `chart.streamgraph`

- Status: executable; editable native vectors.
- Categories: change-over-time
- Required data: `series`, `categories`
- Options: `note`, `title`
- Use: 显示有顺序的时间变化，保持期间与频率一致。
- Avoid: Do not invent missing data or replace unknown values with zero. Keep units, populations, periods and denominators comparable. Order must have an explicit meaning; equal category spacing assumes equal time intervals.
- Limits: PPT output is editable shapes; change the data and rebuild to recalculate. It is not an Excel-linked native chart. Examples are synthetic. This contract does not establish business comparability or causality. Category positions are equally spaced; irregular time intervals require connected-scatterplot with numeric time coordinates.

```json
{
  "asset": "chart.streamgraph",
  "data": {
    "categories": [
      "A",
      "B",
      "C",
      "D"
    ],
    "series": [
      {
        "name": "Observed",
        "values": [
          25,
          40,
          30,
          55
        ]
      },
      {
        "name": "Reference",
        "values": [
          35,
          28,
          45,
          42
        ]
      }
    ]
  },
  "options": {}
}
```

### Bar — `chart.bar`

- Status: executable; editable native vectors.
- Categories: magnitude
- Required data: `series`, `categories`
- Options: `note`, `title`
- Use: 在共同尺度下比较数量大小。
- Avoid: Do not invent missing data or replace unknown values with zero. Keep units, populations, periods and denominators comparable.
- Limits: PPT output is editable shapes; change the data and rebuild to recalculate. It is not an Excel-linked native chart. Examples are synthetic. This contract does not establish business comparability or causality. Category positions are equally spaced; irregular time intervals require connected-scatterplot with numeric time coordinates.

```json
{
  "asset": "chart.bar",
  "data": {
    "categories": [
      "A",
      "B",
      "C",
      "D"
    ],
    "series": [
      {
        "name": "Observed",
        "values": [
          25,
          40,
          30,
          55
        ]
      }
    ]
  },
  "options": {}
}
```

### Paired column — `chart.paired-column`

- Status: executable; editable native vectors.
- Categories: magnitude
- Required data: `series`, `categories`
- Options: `note`, `title`
- Use: 在共同尺度下比较数量大小。
- Avoid: Do not invent missing data or replace unknown values with zero. Keep units, populations, periods and denominators comparable.
- Limits: PPT output is editable shapes; change the data and rebuild to recalculate. It is not an Excel-linked native chart. Examples are synthetic. This contract does not establish business comparability or causality. Category positions are equally spaced; irregular time intervals require connected-scatterplot with numeric time coordinates.

```json
{
  "asset": "chart.paired-column",
  "data": {
    "categories": [
      "A",
      "B",
      "C",
      "D"
    ],
    "series": [
      {
        "name": "Observed",
        "values": [
          25,
          40,
          30,
          55
        ]
      },
      {
        "name": "Reference",
        "values": [
          35,
          28,
          45,
          42
        ]
      }
    ]
  },
  "options": {}
}
```

### Paired bar — `chart.paired-bar`

- Status: executable; editable native vectors.
- Categories: magnitude
- Required data: `series`, `categories`
- Options: `note`, `title`
- Use: 在共同尺度下比较数量大小。
- Avoid: Do not invent missing data or replace unknown values with zero. Keep units, populations, periods and denominators comparable.
- Limits: PPT output is editable shapes; change the data and rebuild to recalculate. It is not an Excel-linked native chart. Examples are synthetic. This contract does not establish business comparability or causality. Category positions are equally spaced; irregular time intervals require connected-scatterplot with numeric time coordinates.

```json
{
  "asset": "chart.paired-bar",
  "data": {
    "categories": [
      "A",
      "B",
      "C",
      "D"
    ],
    "series": [
      {
        "name": "Observed",
        "values": [
          25,
          40,
          30,
          55
        ]
      },
      {
        "name": "Reference",
        "values": [
          35,
          28,
          45,
          42
        ]
      }
    ]
  },
  "options": {}
}
```

### Marimekko — `chart.marimekko`

- Status: executable; editable native vectors.
- Categories: magnitude, part-to-whole
- Required data: `series`, `categories`
- Options: `note`, `title`
- Use: 在共同尺度下比较数量大小。 展示同一整体内互斥且完整的组成。
- Avoid: Do not invent missing data or replace unknown values with zero. Keep units, populations, periods and denominators comparable. Parts must be mutually exclusive and belong to the same complete population.
- Limits: PPT output is editable shapes; change the data and rebuild to recalculate. It is not an Excel-linked native chart. Examples are synthetic. This contract does not establish business comparability or causality. Category positions are equally spaced; irregular time intervals require connected-scatterplot with numeric time coordinates.

```json
{
  "asset": "chart.marimekko",
  "data": {
    "categories": [
      "A",
      "B",
      "C",
      "D"
    ],
    "series": [
      {
        "name": "Observed",
        "values": [
          25,
          40,
          30,
          55
        ]
      },
      {
        "name": "Reference",
        "values": [
          35,
          28,
          45,
          42
        ]
      }
    ]
  },
  "options": {}
}
```

### Proportional symbol — `chart.proportional-symbol`

- Status: executable; editable native vectors.
- Categories: magnitude
- Required data: `series`, `categories`
- Options: `note`, `title`
- Use: 在共同尺度下比较数量大小。
- Avoid: Do not invent missing data or replace unknown values with zero. Keep units, populations, periods and denominators comparable.
- Limits: PPT output is editable shapes; change the data and rebuild to recalculate. It is not an Excel-linked native chart. Examples are synthetic. This contract does not establish business comparability or causality. Category positions are equally spaced; irregular time intervals require connected-scatterplot with numeric time coordinates.

```json
{
  "asset": "chart.proportional-symbol",
  "data": {
    "categories": [
      "A",
      "B",
      "C",
      "D"
    ],
    "series": [
      {
        "name": "Observed",
        "values": [
          25,
          40,
          30,
          55
        ]
      }
    ]
  },
  "options": {}
}
```

### Isotype (pictogram) — `chart.isotype`

- Status: executable; editable native vectors.
- Categories: magnitude
- Required data: `series`, `categories`
- Options: `note`, `symbol_unit`, `title`
- Use: 在共同尺度下比较数量大小。
- Avoid: Do not invent missing data or replace unknown values with zero. Keep units, populations, periods and denominators comparable.
- Limits: PPT output is editable shapes; change the data and rebuild to recalculate. It is not an Excel-linked native chart. Examples are synthetic. This contract does not establish business comparability or causality. Category positions are equally spaced; irregular time intervals require connected-scatterplot with numeric time coordinates. Repeated editable person glyphs; whole people only, never fractional body parts. At most400 symbols.

```json
{
  "asset": "chart.isotype",
  "data": {
    "categories": [
      "A",
      "B",
      "C",
      "D"
    ],
    "series": [
      {
        "name": "Observed",
        "values": [
          25,
          40,
          30,
          55
        ]
      }
    ]
  },
  "options": {}
}
```

### Radar — `chart.radar`

- Status: executable; editable native vectors.
- Categories: magnitude
- Required data: `series`, `categories`
- Options: `note`, `title`
- Use: 在共同尺度下比较数量大小。
- Avoid: Do not invent missing data or replace unknown values with zero. Keep units, populations, periods and denominators comparable. Axes require comparable numeric units; normalize externally and declare that normalization when necessary.
- Limits: PPT output is editable shapes; change the data and rebuild to recalculate. It is not an Excel-linked native chart. Examples are synthetic. This contract does not establish business comparability or causality. Category positions are equally spaced; irregular time intervals require connected-scatterplot with numeric time coordinates.

```json
{
  "asset": "chart.radar",
  "data": {
    "categories": [
      "A",
      "B",
      "C",
      "D"
    ],
    "series": [
      {
        "name": "Observed",
        "values": [
          25,
          40,
          30,
          55
        ]
      }
    ]
  },
  "options": {}
}
```

### Parallel coordinates — `chart.parallel-coordinates`

- Status: executable; editable native vectors.
- Categories: magnitude
- Required data: `series`, `categories`
- Options: `note`, `title`
- Use: 在共同尺度下比较数量大小。
- Avoid: Do not invent missing data or replace unknown values with zero. Keep units, populations, periods and denominators comparable. Axes require comparable numeric units; normalize externally and declare that normalization when necessary.
- Limits: PPT output is editable shapes; change the data and rebuild to recalculate. It is not an Excel-linked native chart. Examples are synthetic. This contract does not establish business comparability or causality. Category positions are equally spaced; irregular time intervals require connected-scatterplot with numeric time coordinates.

```json
{
  "asset": "chart.parallel-coordinates",
  "data": {
    "categories": [
      "A",
      "B",
      "C",
      "D"
    ],
    "series": [
      {
        "name": "Observed",
        "values": [
          25,
          40,
          30,
          55
        ]
      }
    ]
  },
  "options": {}
}
```

### Bullet — `chart.bullet`

- Status: executable; editable native vectors.
- Categories: magnitude
- Required data: `categories`, `ranges`
- Options: `note`, `title`
- Use: 在共同尺度下比较数量大小。
- Avoid: Do not invent missing data or replace unknown values with zero. Keep units, populations, periods and denominators comparable.
- Limits: PPT output is editable shapes; change the data and rebuild to recalculate. It is not an Excel-linked native chart. Examples are synthetic. This contract does not establish business comparability or causality.

```json
{
  "asset": "chart.bullet",
  "data": {
    "categories": [
      "A",
      "B",
      "C"
    ],
    "ranges": [
      {
        "low": 10,
        "high": 40,
        "value": 25,
        "target": 30
      },
      {
        "low": 20,
        "high": 55,
        "value": 40,
        "target": 45
      },
      {
        "low": 30,
        "high": 70,
        "value": 50,
        "target": 55
      }
    ]
  },
  "options": {}
}
```

### Grouped symbol — `chart.grouped-symbol`

- Status: executable; editable native vectors.
- Categories: magnitude
- Required data: `series`, `categories`
- Options: `note`, `symbol_unit`, `title`
- Use: 在共同尺度下比较数量大小。
- Avoid: Do not invent missing data or replace unknown values with zero. Keep units, populations, periods and denominators comparable.
- Limits: PPT output is editable shapes; change the data and rebuild to recalculate. It is not an Excel-linked native chart. Examples are synthetic. This contract does not establish business comparability or causality. Category positions are equally spaced; irregular time intervals require connected-scatterplot with numeric time coordinates. Repeated equal-size circles from integer counts, max400. symbol_unit controls the count represented by one circle.

```json
{
  "asset": "chart.grouped-symbol",
  "data": {
    "categories": [
      "A",
      "B",
      "C",
      "D"
    ],
    "series": [
      {
        "name": "Observed",
        "values": [
          25,
          40,
          30,
          55
        ]
      }
    ]
  },
  "options": {}
}
```

### Stacked column/bar — `chart.stacked-column-bar`

- Status: executable; editable native vectors.
- Categories: part-to-whole
- Required data: `series`, `categories`
- Options: `note`, `title`
- Use: 展示同一整体内互斥且完整的组成。
- Avoid: Do not invent missing data or replace unknown values with zero. Keep units, populations, periods and denominators comparable.
- Limits: PPT output is editable shapes; change the data and rebuild to recalculate. It is not an Excel-linked native chart. Examples are synthetic. This contract does not establish business comparability or causality. Category positions are equally spaced; irregular time intervals require connected-scatterplot with numeric time coordinates.

```json
{
  "asset": "chart.stacked-column-bar",
  "data": {
    "categories": [
      "A",
      "B",
      "C",
      "D"
    ],
    "series": [
      {
        "name": "Observed",
        "values": [
          25,
          40,
          30,
          55
        ]
      },
      {
        "name": "Reference",
        "values": [
          35,
          28,
          45,
          42
        ]
      }
    ]
  },
  "options": {}
}
```

### Pie — `chart.pie`

- Status: executable; editable native vectors.
- Categories: part-to-whole
- Required data: `series`, `categories`
- Options: `note`, `title`
- Use: 展示同一整体内互斥且完整的组成。
- Avoid: Do not invent missing data or replace unknown values with zero. Keep units, populations, periods and denominators comparable. Parts must be mutually exclusive and belong to the same complete population.
- Limits: PPT output is editable shapes; change the data and rebuild to recalculate. It is not an Excel-linked native chart. Examples are synthetic. This contract does not establish business comparability or causality. Category positions are equally spaced; irregular time intervals require connected-scatterplot with numeric time coordinates.

```json
{
  "asset": "chart.pie",
  "data": {
    "categories": [
      "A",
      "B",
      "C",
      "D"
    ],
    "series": [
      {
        "name": "Observed",
        "values": [
          25,
          40,
          30,
          55
        ]
      }
    ]
  },
  "options": {}
}
```

### Donut — `chart.doughnut`

- Status: executable; editable native vectors.
- Categories: part-to-whole
- Required data: `series`, `categories`
- Options: `note`, `title`
- Use: 展示同一整体内互斥且完整的组成。
- Avoid: Do not invent missing data or replace unknown values with zero. Keep units, populations, periods and denominators comparable. Parts must be mutually exclusive and belong to the same complete population.
- Limits: PPT output is editable shapes; change the data and rebuild to recalculate. It is not an Excel-linked native chart. Examples are synthetic. This contract does not establish business comparability or causality. Category positions are equally spaced; irregular time intervals require connected-scatterplot with numeric time coordinates.

```json
{
  "asset": "chart.doughnut",
  "data": {
    "categories": [
      "A",
      "B",
      "C",
      "D"
    ],
    "series": [
      {
        "name": "Observed",
        "values": [
          25,
          40,
          30,
          55
        ]
      }
    ]
  },
  "options": {}
}
```

### Treemap — `chart.treemap`

- Status: executable; editable native vectors.
- Categories: part-to-whole
- Required data: `paths`, `values`
- Options: `note`, `title`
- Use: 展示同一整体内互斥且完整的组成。
- Avoid: Do not invent missing data or replace unknown values with zero. Keep units, populations, periods and denominators comparable. Parts must be mutually exclusive and belong to the same complete population.
- Limits: PPT output is editable shapes; change the data and rebuild to recalculate. It is not an Excel-linked native chart. Examples are synthetic. This contract does not establish business comparability or causality. Recursive slice-and-dice rectangles. Not a squarified treemap; very small leaves may have no internal label.

```json
{
  "asset": "chart.treemap",
  "data": {
    "paths": [
      [
        "North",
        "A"
      ],
      [
        "North",
        "B"
      ],
      [
        "South",
        "C"
      ],
      [
        "South",
        "D"
      ]
    ],
    "values": [
      30,
      20,
      40,
      10
    ]
  },
  "options": {}
}
```

### Voronoi — `chart.voronoi`

- Status: executable; editable native vectors.
- Categories: part-to-whole
- Required data: `sites`, `bounds`
- Options: `note`, `title`
- Use: 展示同一整体内互斥且完整的组成。
- Avoid: Do not invent missing data or replace unknown values with zero. Keep units, populations, periods and denominators comparable. Voronoi area is determined by distance to sites, not the magnitude of category values.
- Limits: PPT output is editable shapes; change the data and rebuild to recalculate. It is not an Excel-linked native chart. Examples are synthetic. This contract does not establish business comparability or causality. Unweighted Euclidean Voronoi cells, clipped to supplied bounds. This is not a weighted part-to-whole treemap.

```json
{
  "asset": "chart.voronoi",
  "data": {
    "bounds": [
      0,
      0,
      10,
      6
    ],
    "sites": [
      {
        "label": "A",
        "point": [
          2,
          2
        ]
      },
      {
        "label": "B",
        "point": [
          6,
          1
        ]
      },
      {
        "label": "C",
        "point": [
          4,
          5
        ]
      },
      {
        "label": "D",
        "point": [
          9,
          4
        ]
      }
    ]
  },
  "options": {}
}
```

### Arc — `chart.arc`

- Status: executable; editable native vectors.
- Categories: part-to-whole
- Required data: `series`, `categories`
- Options: `note`, `symbol_unit`, `title`
- Use: 展示同一整体内互斥且完整的组成。
- Avoid: Do not invent missing data or replace unknown values with zero. Keep units, populations, periods and denominators comparable.
- Limits: PPT output is editable shapes; change the data and rebuild to recalculate. It is not an Excel-linked native chart. Examples are synthetic. This contract does not establish business comparability or causality. Category positions are equally spaced; irregular time intervals require connected-scatterplot with numeric time coordinates. Schematic hemicycle seats from integer counts, max400. Seat colours encode categories; positions do not encode ideological order unless caller orders categories.

```json
{
  "asset": "chart.arc",
  "data": {
    "categories": [
      "A",
      "B",
      "C",
      "D"
    ],
    "series": [
      {
        "name": "Observed",
        "values": [
          25,
          40,
          30,
          55
        ]
      }
    ]
  },
  "options": {}
}
```

### Gridplot — `chart.gridplot`

- Status: executable; editable native vectors.
- Categories: part-to-whole
- Required data: `series`, `categories`
- Options: `note`, `symbol_unit`, `title`
- Use: 展示同一整体内互斥且完整的组成。
- Avoid: Do not invent missing data or replace unknown values with zero. Keep units, populations, periods and denominators comparable.
- Limits: PPT output is editable shapes; change the data and rebuild to recalculate. It is not an Excel-linked native chart. Examples are synthetic. This contract does not establish business comparability or causality. Category positions are equally spaced; irregular time intervals require connected-scatterplot with numeric time coordinates. Whole symbols only. Every category count must be an integer multiple of symbol_unit; at most400 symbols.

```json
{
  "asset": "chart.gridplot",
  "data": {
    "categories": [
      "A",
      "B",
      "C",
      "D"
    ],
    "series": [
      {
        "name": "Observed",
        "values": [
          25,
          40,
          30,
          55
        ]
      }
    ]
  },
  "options": {}
}
```

### Venn — `chart.venn`

- Status: executable; editable native vectors.
- Categories: part-to-whole
- Required data: `sets`
- Options: `note`, `title`
- Use: 展示同一整体内互斥且完整的组成。
- Avoid: Do not invent missing data or replace unknown values with zero. Keep units, populations, periods and denominators comparable. Circle areas are schematic, never a quantitative encoding of set sizes.
- Limits: PPT output is editable shapes; change the data and rebuild to recalculate. It is not an Excel-linked native chart. Examples are synthetic. This contract does not establish business comparability or causality. Two or three finite member sets. Intersections are computed exactly, but circle geometry is schematic.

```json
{
  "asset": "chart.venn",
  "data": {
    "sets": [
      {
        "label": "A",
        "members": [
          "1",
          "2",
          "3",
          "4"
        ]
      },
      {
        "label": "B",
        "members": [
          "3",
          "4",
          "5"
        ]
      },
      {
        "label": "C",
        "members": [
          "4",
          "5",
          "6"
        ]
      }
    ]
  },
  "options": {}
}
```

### Waterfall — `chart.waterfall`

- Status: executable; editable native vectors.
- Categories: part-to-whole, flow
- Required data: `series`, `categories`
- Options: `note`, `title`
- Use: 展示同一整体内互斥且完整的组成。 表达有定义的连接或守恒的数量流。
- Avoid: Do not invent missing data or replace unknown values with zero. Keep units, populations, periods and denominators comparable.
- Limits: PPT output is editable shapes; change the data and rebuild to recalculate. It is not an Excel-linked native chart. Examples are synthetic. This contract does not establish business comparability or causality. Category positions are equally spaced; irregular time intervals require connected-scatterplot with numeric time coordinates. Input values are signed increments; running totals and connectors are computed from zero. Subtotal/total rows are not supported.

```json
{
  "asset": "chart.waterfall",
  "data": {
    "categories": [
      "A",
      "B",
      "C",
      "D"
    ],
    "series": [
      {
        "name": "Observed",
        "values": [
          25,
          -10,
          30,
          -15
        ]
      }
    ]
  },
  "options": {}
}
```

### Basic choropleth (rate/ratio) — `chart.choropleth`

- Status: executable; editable native vectors.
- Categories: spatial
- Required data: `regions`, `coordinates`, `metric_type`
- Options: `note`, `title`
- Use: 使用真实地理边界、坐标和明确连接键。
- Avoid: Do not invent missing data or replace unknown values with zero. Keep units, populations, periods and denominators comparable. Do not substitute invented geographic boundaries, random point locations, or unmatched administrative IDs.
- Limits: PPT output is editable shapes; change the data and rebuild to recalculate. It is not an Excel-linked native chart. Examples are synthetic. This contract does not establish business comparability or causality. Only planar coordinates or regional equirectangular lonlat projection. No antimeridian crossing, polar projection, automatic geocoding, polygon holes or multipolygons. Requires already-normalized rate, ratio or density values. Engine does not infer denominators.

```json
{
  "asset": "chart.choropleth",
  "data": {
    "coordinates": "planar",
    "regions": [
      {
        "id": "A",
        "label": "A",
        "boundary": [
          [
            0,
            0
          ],
          [
            1,
            0
          ],
          [
            1,
            1
          ],
          [
            0,
            1
          ]
        ],
        "value": 0.2
      },
      {
        "id": "B",
        "label": "B",
        "boundary": [
          [
            1,
            0
          ],
          [
            2,
            0
          ],
          [
            2,
            1
          ],
          [
            1,
            1
          ]
        ],
        "value": 0.5
      },
      {
        "id": "C",
        "label": "C",
        "boundary": [
          [
            0,
            1
          ],
          [
            1,
            1
          ],
          [
            1,
            2
          ],
          [
            0,
            2
          ]
        ],
        "value": 0.7
      },
      {
        "id": "D",
        "label": "D",
        "boundary": [
          [
            1,
            1
          ],
          [
            2,
            1
          ],
          [
            2,
            2
          ],
          [
            1,
            2
          ]
        ],
        "value": 0.9
      }
    ],
    "metric_type": "rate"
  },
  "options": {}
}
```

### Proportional symbol (count/magnitude) — `chart.map-proportional-symbol`

- Status: executable; editable native vectors.
- Categories: spatial
- Required data: `regions`, `coordinates`
- Options: `note`, `title`
- Use: 使用真实地理边界、坐标和明确连接键。
- Avoid: Do not invent missing data or replace unknown values with zero. Keep units, populations, periods and denominators comparable. Do not substitute invented geographic boundaries, random point locations, or unmatched administrative IDs.
- Limits: PPT output is editable shapes; change the data and rebuild to recalculate. It is not an Excel-linked native chart. Examples are synthetic. This contract does not establish business comparability or causality. Only planar coordinates or regional equirectangular lonlat projection. No antimeridian crossing, polar projection, automatic geocoding, polygon holes or multipolygons.

```json
{
  "asset": "chart.map-proportional-symbol",
  "data": {
    "coordinates": "planar",
    "regions": [
      {
        "id": "A",
        "label": "A",
        "boundary": [
          [
            0,
            0
          ],
          [
            1,
            0
          ],
          [
            1,
            1
          ],
          [
            0,
            1
          ]
        ],
        "value": 0.2
      },
      {
        "id": "B",
        "label": "B",
        "boundary": [
          [
            1,
            0
          ],
          [
            2,
            0
          ],
          [
            2,
            1
          ],
          [
            1,
            1
          ]
        ],
        "value": 0.5
      },
      {
        "id": "C",
        "label": "C",
        "boundary": [
          [
            0,
            1
          ],
          [
            1,
            1
          ],
          [
            1,
            2
          ],
          [
            0,
            2
          ]
        ],
        "value": 0.7
      },
      {
        "id": "D",
        "label": "D",
        "boundary": [
          [
            1,
            1
          ],
          [
            2,
            1
          ],
          [
            2,
            2
          ],
          [
            1,
            2
          ]
        ],
        "value": 0.9
      }
    ]
  },
  "options": {}
}
```

### Flow map — `chart.flow-map`

- Status: executable; editable native vectors.
- Categories: spatial
- Required data: `regions`, `coordinates`, `links`
- Options: `note`, `title`
- Use: 使用真实地理边界、坐标和明确连接键。
- Avoid: Do not invent missing data or replace unknown values with zero. Keep units, populations, periods and denominators comparable. Do not substitute invented geographic boundaries, random point locations, or unmatched administrative IDs.
- Limits: PPT output is editable shapes; change the data and rebuild to recalculate. It is not an Excel-linked native chart. Examples are synthetic. This contract does not establish business comparability or causality. Only planar coordinates or regional equirectangular lonlat projection. No antimeridian crossing, polar projection, automatic geocoding, polygon holes or multipolygons. Straight centroid-to-centroid directed links; widths encode supplied flow. Geographic routes are not inferred.

```json
{
  "asset": "chart.flow-map",
  "data": {
    "coordinates": "planar",
    "regions": [
      {
        "id": "A",
        "label": "A",
        "boundary": [
          [
            0,
            0
          ],
          [
            1,
            0
          ],
          [
            1,
            1
          ],
          [
            0,
            1
          ]
        ],
        "value": 0.2
      },
      {
        "id": "B",
        "label": "B",
        "boundary": [
          [
            1,
            0
          ],
          [
            2,
            0
          ],
          [
            2,
            1
          ],
          [
            1,
            1
          ]
        ],
        "value": 0.5
      },
      {
        "id": "C",
        "label": "C",
        "boundary": [
          [
            0,
            1
          ],
          [
            1,
            1
          ],
          [
            1,
            2
          ],
          [
            0,
            2
          ]
        ],
        "value": 0.7
      },
      {
        "id": "D",
        "label": "D",
        "boundary": [
          [
            1,
            1
          ],
          [
            2,
            1
          ],
          [
            2,
            2
          ],
          [
            1,
            2
          ]
        ],
        "value": 0.9
      }
    ],
    "links": [
      {
        "source": "A",
        "target": "D",
        "value": 30
      },
      {
        "source": "B",
        "target": "C",
        "value": 10
      }
    ]
  },
  "options": {}
}
```

### Contour map — `chart.contour-map`

- Status: executable; editable native vectors.
- Categories: spatial
- Required data: `x`, `y`, `values`, `levels`, `coordinates`
- Options: `note`, `title`
- Use: 使用真实地理边界、坐标和明确连接键。
- Avoid: Do not invent missing data or replace unknown values with zero. Keep units, populations, periods and denominators comparable. Do not substitute invented geographic boundaries, random point locations, or unmatched administrative IDs.
- Limits: PPT output is editable shapes; change the data and rebuild to recalculate. It is not an Excel-linked native chart. Examples are synthetic. This contract does not establish business comparability or causality. Only planar coordinates or regional equirectangular lonlat projection. No antimeridian crossing, polar projection, automatic geocoding, polygon holes or multipolygons. Marching-squares isolines from a supplied rectangular sample grid. Saddle ambiguity uses centre value; contours do not invent observations.

```json
{
  "asset": "chart.contour-map",
  "data": {
    "coordinates": "planar",
    "x": [
      0,
      1,
      2,
      3
    ],
    "y": [
      0,
      1,
      2,
      3
    ],
    "values": [
      [
        1,
        2,
        3,
        2
      ],
      [
        2,
        4,
        6,
        3
      ],
      [
        3,
        5,
        7,
        4
      ],
      [
        2,
        3,
        4,
        2
      ]
    ],
    "levels": [
      2.5,
      4.5,
      6.5
    ]
  },
  "options": {}
}
```

### Equalised cartogram — `chart.equalised-cartogram`

- Status: executable; editable native vectors.
- Categories: spatial
- Required data: `regions`, `coordinates`
- Options: `note`, `title`
- Use: 使用真实地理边界、坐标和明确连接键。
- Avoid: Do not invent missing data or replace unknown values with zero. Keep units, populations, periods and denominators comparable. Do not substitute invented geographic boundaries, random point locations, or unmatched administrative IDs.
- Limits: PPT output is editable shapes; change the data and rebuild to recalculate. It is not an Excel-linked native chart. Examples are synthetic. This contract does not establish business comparability or causality. Only planar coordinates or regional equirectangular lonlat projection. No antimeridian crossing, polar projection, automatic geocoding, polygon holes or multipolygons. One equal-size tile per region. Deterministic nearest-free grid assignment approximates relative location; boundaries and adjacency are not preserved.

```json
{
  "asset": "chart.equalised-cartogram",
  "data": {
    "coordinates": "planar",
    "regions": [
      {
        "id": "A",
        "label": "A",
        "boundary": [
          [
            0,
            0
          ],
          [
            1,
            0
          ],
          [
            1,
            1
          ],
          [
            0,
            1
          ]
        ],
        "value": 0.2
      },
      {
        "id": "B",
        "label": "B",
        "boundary": [
          [
            1,
            0
          ],
          [
            2,
            0
          ],
          [
            2,
            1
          ],
          [
            1,
            1
          ]
        ],
        "value": 0.5
      },
      {
        "id": "C",
        "label": "C",
        "boundary": [
          [
            0,
            1
          ],
          [
            1,
            1
          ],
          [
            1,
            2
          ],
          [
            0,
            2
          ]
        ],
        "value": 0.7
      },
      {
        "id": "D",
        "label": "D",
        "boundary": [
          [
            1,
            1
          ],
          [
            2,
            1
          ],
          [
            2,
            2
          ],
          [
            1,
            2
          ]
        ],
        "value": 0.9
      }
    ]
  },
  "options": {}
}
```

### Scaled cartogram (value) — `chart.scaled-cartogram`

- Status: executable; editable native vectors.
- Categories: spatial
- Required data: `regions`, `coordinates`
- Options: `note`, `title`
- Use: 使用真实地理边界、坐标和明确连接键。
- Avoid: Do not invent missing data or replace unknown values with zero. Keep units, populations, periods and denominators comparable. Do not substitute invented geographic boundaries, random point locations, or unmatched administrative IDs.
- Limits: PPT output is editable shapes; change the data and rebuild to recalculate. It is not an Excel-linked native chart. Examples are synthetic. This contract does not establish business comparability or causality. Only planar coordinates or regional equirectangular lonlat projection. No antimeridian crossing, polar projection, automatic geocoding, polygon holes or multipolygons. Noncontiguous polygon-area cartogram; relative area is proportional to value. It is not a contiguous topology-preserving cartogram.

```json
{
  "asset": "chart.scaled-cartogram",
  "data": {
    "coordinates": "planar",
    "regions": [
      {
        "id": "A",
        "label": "A",
        "boundary": [
          [
            0,
            0
          ],
          [
            1,
            0
          ],
          [
            1,
            1
          ],
          [
            0,
            1
          ]
        ],
        "value": 0.2
      },
      {
        "id": "B",
        "label": "B",
        "boundary": [
          [
            1,
            0
          ],
          [
            2,
            0
          ],
          [
            2,
            1
          ],
          [
            1,
            1
          ]
        ],
        "value": 0.5
      },
      {
        "id": "C",
        "label": "C",
        "boundary": [
          [
            0,
            1
          ],
          [
            1,
            1
          ],
          [
            1,
            2
          ],
          [
            0,
            2
          ]
        ],
        "value": 0.7
      },
      {
        "id": "D",
        "label": "D",
        "boundary": [
          [
            1,
            1
          ],
          [
            2,
            1
          ],
          [
            2,
            2
          ],
          [
            1,
            2
          ]
        ],
        "value": 0.9
      }
    ]
  },
  "options": {}
}
```

### Dot density — `chart.dot-density`

- Status: executable; editable native vectors.
- Categories: spatial
- Required data: `regions`, `coordinates`, `points`
- Options: `note`, `title`
- Use: 使用真实地理边界、坐标和明确连接键。
- Avoid: Do not invent missing data or replace unknown values with zero. Keep units, populations, periods and denominators comparable. Do not substitute invented geographic boundaries, random point locations, or unmatched administrative IDs.
- Limits: PPT output is editable shapes; change the data and rebuild to recalculate. It is not an Excel-linked native chart. Examples are synthetic. This contract does not establish business comparability or causality. Only planar coordinates or regional equirectangular lonlat projection. No antimeridian crossing, polar projection, automatic geocoding, polygon holes or multipolygons. One point per supplied observed event location; no random population redistribution or synthetic density dots.

```json
{
  "asset": "chart.dot-density",
  "data": {
    "coordinates": "planar",
    "regions": [
      {
        "id": "A",
        "label": "A",
        "boundary": [
          [
            0,
            0
          ],
          [
            1,
            0
          ],
          [
            1,
            1
          ],
          [
            0,
            1
          ]
        ],
        "value": 0.2
      },
      {
        "id": "B",
        "label": "B",
        "boundary": [
          [
            1,
            0
          ],
          [
            2,
            0
          ],
          [
            2,
            1
          ],
          [
            1,
            1
          ]
        ],
        "value": 0.5
      },
      {
        "id": "C",
        "label": "C",
        "boundary": [
          [
            0,
            1
          ],
          [
            1,
            1
          ],
          [
            1,
            2
          ],
          [
            0,
            2
          ]
        ],
        "value": 0.7
      },
      {
        "id": "D",
        "label": "D",
        "boundary": [
          [
            1,
            1
          ],
          [
            2,
            1
          ],
          [
            2,
            2
          ],
          [
            1,
            2
          ]
        ],
        "value": 0.9
      }
    ],
    "points": [
      [
        0.2,
        0.3
      ],
      [
        0.4,
        0.6
      ],
      [
        0.7,
        0.3
      ],
      [
        1.4,
        0.2
      ],
      [
        1.6,
        1.7
      ]
    ]
  },
  "options": {}
}
```

### Heat map — `chart.map-heatmap`

- Status: executable; editable native vectors.
- Categories: spatial
- Required data: `x`, `y`, `values`, `levels`, `coordinates`
- Options: `note`, `title`
- Use: 使用真实地理边界、坐标和明确连接键。
- Avoid: Do not invent missing data or replace unknown values with zero. Keep units, populations, periods and denominators comparable. Do not substitute invented geographic boundaries, random point locations, or unmatched administrative IDs.
- Limits: PPT output is editable shapes; change the data and rebuild to recalculate. It is not an Excel-linked native chart. Examples are synthetic. This contract does not establish business comparability or causality. Only planar coordinates or regional equirectangular lonlat projection. No antimeridian crossing, polar projection, automatic geocoding, polygon holes or multipolygons. Sample-centred grid cells with explicit thresholds; midpoint cell boundaries support nonuniform sample spacing. No spatial interpolation.

```json
{
  "asset": "chart.map-heatmap",
  "data": {
    "coordinates": "planar",
    "x": [
      0,
      1,
      2,
      3
    ],
    "y": [
      0,
      1,
      2,
      3
    ],
    "values": [
      [
        1,
        2,
        3,
        2
      ],
      [
        2,
        4,
        6,
        3
      ],
      [
        3,
        5,
        7,
        4
      ],
      [
        2,
        3,
        4,
        2
      ]
    ],
    "levels": [
      2.5,
      4.5,
      6.5
    ]
  },
  "options": {}
}
```

### Sankey — `chart.sankey`

- Status: executable; editable native vectors.
- Categories: flow
- Required data: `nodes`, `links`
- Options: `note`, `show_values`, `title`
- Use: 表达有定义的连接或守恒的数量流。
- Avoid: Do not invent missing data or replace unknown values with zero. Keep units, populations, periods and denominators comparable. Intermediate inflow and outflow must balance; cycles and missing flows are rejected.
- Limits: PPT output is editable shapes; change the data and rebuild to recalculate. It is not an Excel-linked native chart. Examples are synthetic. This contract does not establish business comparability or causality. Acyclic balanced flow network. Node levels use longest predecessor rank; port offsets and ribbon thickness are computed from conserved quantities.

```json
{
  "asset": "chart.sankey",
  "data": {
    "nodes": [
      {
        "id": "A",
        "label": "A"
      },
      {
        "id": "B",
        "label": "B"
      },
      {
        "id": "C",
        "label": "C"
      },
      {
        "id": "D",
        "label": "D"
      }
    ],
    "links": [
      {
        "source": "A",
        "target": "B",
        "value": 30
      },
      {
        "source": "A",
        "target": "C",
        "value": 20
      },
      {
        "source": "B",
        "target": "D",
        "value": 30
      },
      {
        "source": "C",
        "target": "D",
        "value": 20
      }
    ]
  },
  "options": {}
}
```

### Chord — `chart.chord`

- Status: executable; editable native vectors.
- Categories: flow
- Required data: `nodes`, `links`
- Options: `note`, `title`
- Use: 表达有定义的连接或守恒的数量流。
- Avoid: Do not invent missing data or replace unknown values with zero. Keep units, populations, periods and denominators comparable.
- Limits: PPT output is editable shapes; change the data and rebuild to recalculate. It is not an Excel-linked native chart. Examples are synthetic. This contract does not establish business comparability or causality. Incident arc allocation and ribbon widths represent supplied link values. Aggregated directional endpoints are recorded, but ribbons have no directional arrowheads.

```json
{
  "asset": "chart.chord",
  "data": {
    "nodes": [
      {
        "id": "A",
        "label": "A"
      },
      {
        "id": "B",
        "label": "B"
      },
      {
        "id": "C",
        "label": "C"
      },
      {
        "id": "D",
        "label": "D"
      }
    ],
    "links": [
      {
        "source": "A",
        "target": "B",
        "value": 30
      },
      {
        "source": "A",
        "target": "C",
        "value": 20
      },
      {
        "source": "B",
        "target": "D",
        "value": 30
      },
      {
        "source": "C",
        "target": "D",
        "value": 20
      }
    ]
  },
  "options": {}
}
```

### Network — `chart.network`

- Status: executable; editable native vectors.
- Categories: flow
- Required data: `nodes`, `links`
- Options: `note`, `title`
- Use: 表达有定义的连接或守恒的数量流。
- Avoid: Do not invent missing data or replace unknown values with zero. Keep units, populations, periods and denominators comparable.
- Limits: PPT output is editable shapes; change the data and rebuild to recalculate. It is not an Excel-linked native chart. Examples are synthetic. This contract does not establish business comparability or causality. Deterministic circular node layout; line width encodes link weight. No automatic community discovery or force-directed optimization.

```json
{
  "asset": "chart.network",
  "data": {
    "nodes": [
      {
        "id": "A",
        "label": "A"
      },
      {
        "id": "B",
        "label": "B"
      },
      {
        "id": "C",
        "label": "C"
      },
      {
        "id": "D",
        "label": "D"
      }
    ],
    "links": [
      {
        "source": "A",
        "target": "B",
        "value": 30
      },
      {
        "source": "A",
        "target": "C",
        "value": 20
      },
      {
        "source": "B",
        "target": "D",
        "value": 30
      },
      {
        "source": "C",
        "target": "D",
        "value": 20
      }
    ]
  },
  "options": {}
}
```

### Proportional stacked bar — `chart.proportional-stacked-bar`

- Status: executable; editable native vectors.
- Categories: part-to-whole, magnitude
- Required data: `series`, `categories`
- Options: `note`, `title`
- Use: 展示同一整体内互斥且完整的组成。 在共同尺度下比较数量大小。
- Avoid: Do not invent missing data or replace unknown values with zero. Keep units, populations, periods and denominators comparable. Parts must be mutually exclusive and belong to the same complete population.
- Limits: PPT output is editable shapes; change the data and rebuild to recalculate. It is not an Excel-linked native chart. Examples are synthetic. This contract does not establish business comparability or causality. Category positions are equally spaced; irregular time intervals require connected-scatterplot with numeric time coordinates.

```json
{
  "asset": "chart.proportional-stacked-bar",
  "data": {
    "categories": [
      "A",
      "B",
      "C",
      "D"
    ],
    "series": [
      {
        "name": "Observed",
        "values": [
          25,
          40,
          30,
          55
        ]
      },
      {
        "name": "Reference",
        "values": [
          35,
          28,
          45,
          42
        ]
      }
    ]
  },
  "options": {}
}
```

### Sunburst — `chart.sunburst`

- Status: executable; editable native vectors.
- Categories: part-to-whole
- Required data: `paths`, `values`
- Options: `note`, `title`
- Use: 展示同一整体内互斥且完整的组成。
- Avoid: Do not invent missing data or replace unknown values with zero. Keep units, populations, periods and denominators comparable. Parts must be mutually exclusive and belong to the same complete population.
- Limits: PPT output is editable shapes; change the data and rebuild to recalculate. It is not an Excel-linked native chart. Examples are synthetic. This contract does not establish business comparability or causality. Hierarchical leaf paths determine branch totals and arc spans. Maximum four levels; labels appear only where measured capacity permits.

```json
{
  "asset": "chart.sunburst",
  "data": {
    "paths": [
      [
        "North",
        "A"
      ],
      [
        "North",
        "B"
      ],
      [
        "South",
        "C"
      ],
      [
        "South",
        "D"
      ]
    ],
    "values": [
      30,
      20,
      40,
      10
    ]
  },
  "options": {}
}
```

## Provenance

Discovery taxonomy: Financial Times Visual Vocabulary, poster and website union (66 poster entries plus proportional-stacked-bar and sunburst). The original source and license metadata are retained in `../visual-vocabulary.json` and in each catalogue record. The engine implementations and synthetic examples are local code, not scraped screenshots.

This handbook and `catalog.json` are generated snapshots of the executable Python registry. The Python registry is authoritative.
