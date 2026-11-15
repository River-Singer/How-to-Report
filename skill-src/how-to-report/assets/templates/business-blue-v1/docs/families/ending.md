# 结束与行动

收束认识或列出实际下一步

类型为汇报组织，语义入口为`ppt.ending`。

## 使用场景

结尾与本次汇报目标相关，负责人和日期来自实际安排。

关系要求为收束或实际行动。缺少必要输入时说明具体字段与来源缺口，再选择资料能支持的表达。

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
    "closing_message": {
      "type": "string",
      "minLength": 1,
      "maxLength": 48
    },
    "subtitle": {
      "type": "string",
      "minLength": 0,
      "maxLength": 64
    },
    "contact_info": {
      "type": "string",
      "minLength": 0,
      "maxLength": 64
    },
    "actions": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "action": {
            "type": "string",
            "minLength": 1,
            "maxLength": 60
          },
          "owner": {
            "type": "string",
            "minLength": 0,
            "maxLength": 16
          },
          "date": {
            "type": "string",
            "minLength": 0,
            "maxLength": 20
          }
        },
        "required": [
          "action"
        ],
        "additionalProperties": false
      },
      "minItems": 0,
      "maxItems": 3
    }
  },
  "required": [
    "title",
    "closing_message"
  ],
  "additionalProperties": false
}
```

## 变体与容量

### thanks

收束句与补充信息。

Layout为`ending-thanks`，原型为`templates/prototypes/12a_ending_thanks.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| closing_message | 2 | 48 | chapter | [88, 202, 1104, 150] |
| subtitle | 0 | 64 | body | [88, 390, 1104, 106] |
| contact_info | 0 | 64 | body | [88, 534, 1104, 64] |
### actions

三项行动与责任日期。

Layout为`ending-actions`，原型为`templates/prototypes/12b_ending_actions.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| closing_message | 2 | 48 | body | [48, 120, 1184, 56] |
| actions.0.action | 1 | 60 | body | [72, 220.0, 734.08, 104] |
| actions.0.owner | 0 | 16 | caption | [853.12, 220.0, 331.52000000000004, 42] |
| actions.0.date | 0 | 20 | caption | [853.12, 270.0, 331.52000000000004, 42] |
| actions.1.action | 1 | 60 | body | [72, 369.33333333333337, 734.08, 104] |
| actions.1.owner | 0 | 16 | caption | [853.12, 369.33333333333337, 331.52000000000004, 42] |
| actions.1.date | 0 | 20 | caption | [853.12, 419.33333333333337, 331.52000000000004, 42] |
| actions.2.action | 1 | 60 | body | [72, 518.6666666666667, 734.08, 104] |
| actions.2.owner | 0 | 16 | caption | [853.12, 518.6666666666667, 331.52000000000004, 42] |
| actions.2.date | 0 | 20 | caption | [853.12, 568.6666666666667, 331.52000000000004, 42] |

## 使用步骤

1. 先确认材料确有本页型所表达的关系，选择`family=ending`及兼容variant。
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

来源为500页-01商务蓝配色.pptx，第185页及计划类结构。原始文件指纹及资产处理见asset-provenance.json。当前原型完成结构生成与文本测量，实际渲染和原生编辑范围以交付检查记录为准。

catalog指纹为`cb0b762dd09720f0095cb5d682a87348e0608e2f8d5fdf784ec1d4ef62f73010`，tokens指纹为`2bb967b3a61bf7a4072665f712f39ac49458d22ebe9407f269236c21adc366f3`，参数schema指纹为`add0f4b9d6bc61cd5cae5ce6d6821748442ed906b6b779cc561790e85b605ff5`。
