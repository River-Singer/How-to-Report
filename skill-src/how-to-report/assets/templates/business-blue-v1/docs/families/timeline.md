# 时间轴

解释有据的时间顺序与节点

类型为信息结构，语义入口为`ppt.timeline`。

## 使用场景

各节点日期或顺序有来源。

关系要求为时间先后。缺少必要输入时说明具体字段与来源缺口，再选择资料能支持的表达。

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
    "events": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "time_label": {
            "type": "string",
            "minLength": 1,
            "maxLength": 20
          },
          "title": {
            "type": "string",
            "minLength": 1,
            "maxLength": 18
          },
          "body": {
            "type": "string",
            "minLength": 0,
            "maxLength": 96
          }
        },
        "required": [
          "time_label",
          "title"
        ],
        "additionalProperties": false
      },
      "minItems": 1,
      "maxItems": 4
    }
  },
  "required": [
    "title",
    "events"
  ],
  "additionalProperties": false
}
```

## 变体与容量

### horizontal-4

四点横向时间轴。

Layout为`timeline-horizontal-4`，原型为`templates/prototypes/08a_timeline_horizontal-4.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| events.0.time_label | 1 | 20 | heading | [48.0, 206, 272.0, 66] |
| events.0.title | 1 | 18 | heading | [48.0, 330, 272.0, 86] |
| events.0.body | 0 | 60 | body | [48.0, 430, 272.0, 218] |
| events.1.time_label | 1 | 20 | heading | [344.0, 206, 272.0, 66] |
| events.1.title | 1 | 18 | heading | [344.0, 330, 272.0, 86] |
| events.1.body | 0 | 60 | body | [344.0, 430, 272.0, 218] |
| events.2.time_label | 1 | 20 | heading | [640.0, 206, 272.0, 66] |
| events.2.title | 1 | 18 | heading | [640.0, 330, 272.0, 86] |
| events.2.body | 0 | 60 | body | [640.0, 430, 272.0, 218] |
| events.3.time_label | 1 | 20 | heading | [936.0, 206, 272.0, 66] |
| events.3.title | 1 | 18 | heading | [936.0, 330, 272.0, 86] |
| events.3.body | 0 | 60 | body | [936.0, 430, 272.0, 218] |
### vertical-3

三点纵向长说明。

Layout为`timeline-vertical-3`，原型为`templates/prototypes/08b_timeline_vertical-3.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| events.0.time_label | 1 | 20 | heading | [48, 140.0, 160, 70] |
| events.0.title | 1 | 18 | heading | [268, 132.0, 964, 52] |
| events.0.body | 0 | 96 | body | [268, 190.0, 964, 94.0] |
| events.1.time_label | 1 | 20 | heading | [48, 316.0, 160, 70] |
| events.1.title | 1 | 18 | heading | [268, 308.0, 964, 52] |
| events.1.body | 0 | 96 | body | [268, 366.0, 964, 94.0] |
| events.2.time_label | 1 | 20 | heading | [48, 492.0, 160, 70] |
| events.2.title | 1 | 18 | heading | [268, 484.0, 964, 52] |
| events.2.body | 0 | 96 | body | [268, 542.0, 964, 94.0] |

## 使用步骤

1. 先确认材料确有本页型所表达的关系，选择`family=timeline`及兼容variant。
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

来源为500页-01商务蓝配色.pptx，第300页。原始文件指纹及资产处理见asset-provenance.json。当前原型完成结构生成与文本测量，实际渲染和原生编辑范围以交付检查记录为准。

catalog指纹为`cb0b762dd09720f0095cb5d682a87348e0608e2f8d5fdf784ec1d4ef62f73010`，tokens指纹为`2bb967b3a61bf7a4072665f712f39ac49458d22ebe9407f269236c21adc366f3`，参数schema指纹为`add0f4b9d6bc61cd5cae5ce6d6821748442ed906b6b779cc561790e85b605ff5`。
