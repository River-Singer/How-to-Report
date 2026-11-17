# 能力矩阵

交叉两个维度定位单元格

类型为信息结构，语义入口为`ppt.matrix`。

## 使用场景

行、列具有明确不同维度，单元格有对应含义。

关系要求为两个维度的交叉。缺少必要输入时说明具体字段与来源缺口，再选择资料能支持的表达。

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
    "rows": {
      "type": "array",
      "items": {
        "type": "string",
        "minLength": 1,
        "maxLength": 18
      },
      "minItems": 1,
      "maxItems": 4
    },
    "columns": {
      "type": "array",
      "items": {
        "type": "string",
        "minLength": 1,
        "maxLength": 18
      },
      "minItems": 1,
      "maxItems": 3
    },
    "cells": {
      "type": "array",
      "items": {
        "type": "array",
        "items": {
          "type": [
            "string",
            "null"
          ],
          "maxLength": 40
        },
        "minItems": 1,
        "maxItems": 3
      },
      "minItems": 1,
      "maxItems": 4
    },
    "corner_label": {
      "type": "string",
      "minLength": 0,
      "maxLength": 18
    }
  },
  "required": [
    "title",
    "rows",
    "columns",
    "cells"
  ],
  "additionalProperties": false
}
```

## 变体与容量

### grid-4x3

四行三列矩阵，逐格可编辑。

Layout为`matrix-grid-4x3`，原型为`templates/prototypes/15a_matrix_grid-4x3.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| corner_label | 0 | 18 | heading | [64.0, 136.0, 264.0, 73.6] |
| columns.0 | 1 | 18 | heading | [360.0, 136.0, 264.0, 73.6] |
| columns.1 | 1 | 18 | heading | [656.0, 136.0, 264.0, 73.6] |
| columns.2 | 1 | 18 | heading | [952.0, 136.0, 264.0, 73.6] |
| rows.0 | 1 | 18 | heading | [64.0, 241.6, 264.0, 73.6] |
| cells.0.0 | 0 | 40 | body | [360.0, 241.6, 264.0, 73.6] |
| cells.0.1 | 0 | 40 | body | [656.0, 241.6, 264.0, 73.6] |
| cells.0.2 | 0 | 40 | body | [952.0, 241.6, 264.0, 73.6] |
| rows.1 | 1 | 18 | heading | [64.0, 347.2, 264.0, 73.6] |
| cells.1.0 | 0 | 40 | body | [360.0, 347.2, 264.0, 73.6] |
| cells.1.1 | 0 | 40 | body | [656.0, 347.2, 264.0, 73.6] |
| cells.1.2 | 0 | 40 | body | [952.0, 347.2, 264.0, 73.6] |
| rows.2 | 1 | 18 | heading | [64.0, 452.79999999999995, 264.0, 73.6] |
| cells.2.0 | 0 | 40 | body | [360.0, 452.79999999999995, 264.0, 73.6] |
| cells.2.1 | 0 | 40 | body | [656.0, 452.79999999999995, 264.0, 73.6] |
| cells.2.2 | 0 | 40 | body | [952.0, 452.79999999999995, 264.0, 73.6] |
| rows.3 | 1 | 18 | heading | [64.0, 558.4, 264.0, 73.6] |
| cells.3.0 | 0 | 40 | body | [360.0, 558.4, 264.0, 73.6] |
| cells.3.1 | 0 | 40 | body | [656.0, 558.4, 264.0, 73.6] |
| cells.3.2 | 0 | 40 | body | [952.0, 558.4, 264.0, 73.6] |

## 使用步骤

1. 先确认材料确有本页型所表达的关系，选择`family=matrix`及兼容variant。
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
  }
}
```

允许字段来自page-catalog.json与pages.schema.json。tokens控制全局几何、字阶、颜色、间距和线条。字号通过body_role选择已登记字阶。切换variant后重新校验输入容量。

## 来源与检查

来源为蓝色逻辑架构图.pptx，第3页；房子图战略图.pptx，第5页。原始文件指纹及资产处理见asset-provenance.json。当前原型完成结构生成与文本测量，实际渲染和原生编辑范围以交付检查记录为准。

catalog指纹为`498fe133ea2d00699bb4c4ea5bc798e78130623b21eea5d3cc8cb10e125af78b`，tokens指纹为`2bb967b3a61bf7a4072665f712f39ac49458d22ebe9407f269236c21adc366f3`，参数schema指纹为`6981096e740f47c827294403dd132d6609fd537f46b15e8164c4b630b9822a61`。
