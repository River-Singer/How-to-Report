# 核心指标

比较同层级指标及必要解释

类型为数据表达，语义入口为`ppt.kpi`。

## 使用场景

已给出有口径的数值、单位和标签。

关系要求为同层级指标。缺少必要输入时说明具体字段与来源缺口，再选择资料能支持的表达。

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
    "metrics": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "label": {
            "type": "string",
            "minLength": 1,
            "maxLength": 14
          },
          "value": {
            "type": [
              "number",
              "null"
            ]
          },
          "decimals": {
            "type": "integer",
            "minimum": 0,
            "maximum": 4
          },
          "unit": {
            "type": "string",
            "minLength": 0,
            "maxLength": 6
          },
          "note": {
            "type": "string",
            "minLength": 0,
            "maxLength": 72
          }
        },
        "required": [
          "label",
          "value"
        ],
        "additionalProperties": false
      },
      "minItems": 1,
      "maxItems": 4
    },
    "summary": {
      "type": "string",
      "minLength": 0,
      "maxLength": 100
    }
  },
  "required": [
    "title",
    "metrics"
  ],
  "additionalProperties": false
}
```

## 变体与容量

### strip-4

四项指标并列与下方解释。

Layout为`kpi-strip-4`，原型为`templates/prototypes/04a_kpi_strip-4.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| metrics.0.label | 1 | 14 | heading | [68.0, 144, 238.0, 66] |
| metrics.0.value | 0 | 16 | metric | [68.0, 236, 238.0, 72] |
| metrics.0.unit | 0 | 6 | body | [68.0, 318, 238.0, 34] |
| metrics.0.note | 0 | 54 | caption | [68.0, 368, 238.0, 56] |
| metrics.1.label | 1 | 14 | heading | [370.0, 144, 238.0, 66] |
| metrics.1.value | 0 | 16 | metric | [370.0, 236, 238.0, 72] |
| metrics.1.unit | 0 | 6 | body | [370.0, 318, 238.0, 34] |
| metrics.1.note | 0 | 54 | caption | [370.0, 368, 238.0, 56] |
| metrics.2.label | 1 | 14 | heading | [672.0, 144, 238.0, 66] |
| metrics.2.value | 0 | 16 | metric | [672.0, 236, 238.0, 72] |
| metrics.2.unit | 0 | 6 | body | [672.0, 318, 238.0, 34] |
| metrics.2.note | 0 | 54 | caption | [672.0, 368, 238.0, 56] |
| metrics.3.label | 1 | 14 | heading | [974.0, 144, 238.0, 66] |
| metrics.3.value | 0 | 16 | metric | [974.0, 236, 238.0, 72] |
| metrics.3.unit | 0 | 6 | body | [974.0, 318, 238.0, 34] |
| metrics.3.note | 0 | 54 | caption | [974.0, 368, 238.0, 56] |
| summary | 0 | 100 | body | [48, 472, 1184, 176] |
### cards-3

三项较宽指标与解释。

Layout为`kpi-cards-3`，原型为`templates/prototypes/04b_kpi_cards-3.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| metrics.0.label | 1 | 14 | heading | [68.0, 144, 338.6666666666667, 66] |
| metrics.0.value | 0 | 16 | metric | [68.0, 236, 338.6666666666667, 72] |
| metrics.0.unit | 0 | 6 | body | [68.0, 318, 338.6666666666667, 34] |
| metrics.0.note | 0 | 54 | caption | [68.0, 368, 338.6666666666667, 86] |
| metrics.1.label | 1 | 14 | heading | [470.6666666666667, 144, 338.6666666666667, 66] |
| metrics.1.value | 0 | 16 | metric | [470.6666666666667, 236, 338.6666666666667, 72] |
| metrics.1.unit | 0 | 6 | body | [470.6666666666667, 318, 338.6666666666667, 34] |
| metrics.1.note | 0 | 54 | caption | [470.6666666666667, 368, 338.6666666666667, 86] |
| metrics.2.label | 1 | 14 | heading | [873.3333333333334, 144, 338.6666666666667, 66] |
| metrics.2.value | 0 | 16 | metric | [873.3333333333334, 236, 338.6666666666667, 72] |
| metrics.2.unit | 0 | 6 | body | [873.3333333333334, 318, 338.6666666666667, 34] |
| metrics.2.note | 0 | 54 | caption | [873.3333333333334, 368, 338.6666666666667, 86] |
| summary | 0 | 100 | body | [48, 502, 1184, 146] |

## 使用步骤

1. 先确认材料确有本页型所表达的关系，选择`family=kpi`及兼容variant。
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
  "decimals": {
    "type": "integer",
    "minimum": 0,
    "maximum": 4,
    "default": 0
  }
}
```

允许字段来自page-catalog.json与pages.schema.json。tokens控制全局几何、字阶、颜色、间距和线条。字号通过body_role选择已登记字阶。切换variant后重新校验输入容量。

## 来源与检查

来源为500页-01商务蓝配色.pptx，第23页。原始文件指纹及资产处理见asset-provenance.json。当前原型完成结构生成与文本测量，实际渲染和原生编辑范围以交付检查记录为准。

catalog指纹为`498fe133ea2d00699bb4c4ea5bc798e78130623b21eea5d3cc8cb10e125af78b`，tokens指纹为`2bb967b3a61bf7a4072665f712f39ac49458d22ebe9407f269236c21adc366f3`，参数schema指纹为`6981096e740f47c827294403dd132d6609fd537f46b15e8164c4b630b9822a61`。
