# 数据与结论

由明确数值及尺度说明比较或趋势

类型为数据表达，语义入口为`ppt.chart`。

## 使用场景

类别、数列、单位及解释有依据；趋势需要实际有序数据。

关系要求为同尺度数量比较或有序趋势。缺少必要输入时说明具体字段与来源缺口，再选择资料能支持的表达。

## 输入与参数

content按以下schema提供，所有可见文字均为输入或明确派生显示。数组空余槽及隐藏可选槽允许空carrier，对应输入项存在时执行字段min/max。

```json
{
  "type": "object",
  "properties": {
    "title": {
      "type": "string",
      "minLength": 2,
      "maxLength": 32
    },
    "section_name": {
      "type": "string",
      "minLength": 0,
      "maxLength": 24
    },
    "source": {
      "type": "string",
      "minLength": 0,
      "maxLength": 64
    },
    "categories": {
      "type": "array",
      "items": {
        "type": "string",
        "minLength": 1,
        "maxLength": 24
      },
      "minItems": 1,
      "maxItems": 6
    },
    "series": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "name": {
            "type": "string",
            "minLength": 1,
            "maxLength": 16
          },
          "values": {
            "type": "array",
            "items": {
              "type": [
                "number",
                "null"
              ]
            },
            "minItems": 1,
            "maxItems": 6
          }
        },
        "required": [
          "name",
          "values"
        ],
        "additionalProperties": false
      },
      "minItems": 1,
      "maxItems": 2
    },
    "conclusions": {
      "type": "string",
      "minLength": 1,
      "maxLength": 100
    },
    "unit": {
      "type": "string",
      "minLength": 0,
      "maxLength": 8
    },
    "axis_title": {
      "type": "string",
      "minLength": 0,
      "maxLength": 18
    }
  },
  "required": [
    "title",
    "categories",
    "series",
    "conclusions"
  ],
  "additionalProperties": false
}
```

## 变体与容量

config.show_data_labels默认false，设为true可在SVG和原生图表中显示各已知数值。空值保留缺口，零值显示为0；标签使用原值。数轴包含零基线，复用友好间隔算法，SVG与原生图表共享最小值、最大值和主刻度间隔。多系列或高密度标签需实际回看，出现拥挤时按本场重点调整显示或选择兼容版式。

### side

左侧主图与右侧结论。

Layout为`chart-side`，原型为`templates/prototypes/07a_chart_side.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| axis_caption | 0 | 28 | caption | [696.8, 128, 180, 32] |
| chart_ticks.0 | 1 | 16 | caption | [48, 572.0, 70, 28] |
| chart_ticks.1 | 1 | 16 | caption | [48, 494.0, 70, 28] |
| chart_ticks.2 | 1 | 16 | caption | [48, 416.0, 70, 28] |
| chart_ticks.3 | 1 | 16 | caption | [48, 338.0, 70, 28] |
| chart_ticks.4 | 1 | 16 | caption | [48, 260.0, 70, 28] |
| chart_ticks.5 | 1 | 16 | caption | [48, 182.0, 70, 28] |
| categories.0 | 1 | 24 | caption | [132.0, 598, 708.8, 48] |
| series.0.name | 1 | 16 | caption | [128.0, 128, 268.4, 32] |
| conclusions | 1 | 100 | body | [904.8, 144, 327.20000000000005, 504] |
### wide

全宽主图与下方结论。

Layout为`chart-wide`，原型为`templates/prototypes/07b_chart_wide.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| axis_caption | 0 | 28 | caption | [1052, 128, 180, 32] |
| chart_ticks.0 | 1 | 16 | caption | [48, 452.0, 70, 28] |
| chart_ticks.1 | 1 | 16 | caption | [48, 398.0, 70, 28] |
| chart_ticks.2 | 1 | 16 | caption | [48, 344.0, 70, 28] |
| chart_ticks.3 | 1 | 16 | caption | [48, 290.0, 70, 28] |
| chart_ticks.4 | 1 | 16 | caption | [48, 236.0, 70, 28] |
| chart_ticks.5 | 1 | 16 | caption | [48, 182.0, 70, 28] |
| categories.0 | 1 | 24 | caption | [132.0, 478, 1064.0, 48] |
| series.0.name | 1 | 16 | caption | [128.0, 128, 446.0, 32] |
| conclusions | 1 | 100 | body | [48, 552, 1184, 96] |

## 使用步骤

1. 先确认材料确有本页型所表达的关系，选择`family=chart`及兼容variant。
2. 提供完整content，按schema控制config。可选内容可留空，正文含义由实际汇报任务确定。
3. 执行validate和build，处理具体字段的长度、容量或字体测量错误。
4. 对生成项目执行check、export、inspect，并查看最终页面和所需编辑操作。

## 配置与tokens

本页型的config类型、可选值与默认值如下。

```json
{
  "body_role": {
    "enum": [
      "body",
      "compactBody"
    ],
    "default": "body"
  },
  "show_source": {
    "type": "boolean",
    "default": true
  },
  "show_page_number": {
    "type": "boolean",
    "default": true
  },
  "chart_type": {
    "enum": [
      "column",
      "line"
    ],
    "default": "column"
  },
  "show_legend": {
    "type": "boolean",
    "default": true
  },
  "show_data_labels": {
    "type": "boolean",
    "description": "显示各已知数据点的原值，SVG与原生图表共同生效。默认false。",
    "default": false
  }
}
```

允许字段来自page-catalog.json与pages.schema.json。tokens控制全局几何、字阶、颜色、间距和线条。字号通过body_role选择已登记字阶。切换variant后重新校验输入容量。

## 来源与检查

来源为500页-01商务蓝配色.pptx，第422页。原始文件指纹及资产处理见asset-provenance.json。当前原型完成结构生成与文本测量，实际渲染和原生编辑范围以交付检查记录为准。

catalog指纹为`cb0b762dd09720f0095cb5d682a87348e0608e2f8d5fdf784ec1d4ef62f73010`，tokens指纹为`2bb967b3a61bf7a4072665f712f39ac49458d22ebe9407f269236c21adc366f3`，参数schema指纹为`add0f4b9d6bc61cd5cae5ce6d6821748442ed906b6b779cc561790e85b605ff5`。
