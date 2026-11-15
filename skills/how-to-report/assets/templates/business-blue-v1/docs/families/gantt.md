# 甘特计划

说明任务持续时间与重叠安排

类型为数据表达，语义入口为`ppt.gantt`。

## 使用场景

任务有起止日期和可比较的计划期间。采用任意合法起止日期，12或6个等长时间区段共享同一时间比例。刻度显示月日，图上标注完整期间；短跨度重复刻度留空。

关系要求为任务持续时间与重叠。缺少必要输入时说明具体字段与来源缺口，再选择资料能支持的表达。

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
    "start": {
      "type": "string",
      "minLength": 1,
      "maxLength": 10,
      "pattern": "^\\d{4}-\\d{2}-\\d{2}$",
      "description": "ISO日期，计划期间起日，须早于止日。"
    },
    "end": {
      "type": "string",
      "minLength": 1,
      "maxLength": 10,
      "pattern": "^\\d{4}-\\d{2}-\\d{2}$",
      "description": "ISO日期，计划期间止日。任意合法期间按12或6个等长时间区段绘制，任务止日包含在时间条内。"
    },
    "tasks": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "name": {
            "type": "string",
            "minLength": 1,
            "maxLength": 24
          },
          "start": {
            "type": "string",
            "minLength": 1,
            "maxLength": 10
          },
          "end": {
            "type": "string",
            "minLength": 1,
            "maxLength": 10
          },
          "owner": {
            "type": "string",
            "minLength": 0,
            "maxLength": 16
          },
          "progress": {
            "type": [
              "number",
              "null"
            ],
            "minimum": 0,
            "maximum": 100
          }
        },
        "required": [
          "name",
          "start",
          "end"
        ],
        "additionalProperties": false
      },
      "minItems": 1,
      "maxItems": 6
    }
  },
  "required": [
    "title",
    "start",
    "end",
    "tasks"
  ],
  "additionalProperties": false
}
```

## 变体与容量

### annual-12

十二时间区段、六任务，适用于较细的计划概览；期间由输入日期决定。

Layout为`gantt-annual-12`，原型为`templates/prototypes/09a_gantt_annual-12.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| period_range | 21 | 21 | caption | [48, 120, 234, 44] |
| period_labels.0 | 0 | 20 | caption | [302.0, 120, 56.5, 36] |
| period_labels.1 | 0 | 20 | caption | [366.5, 120, 56.5, 36] |
| period_labels.2 | 0 | 20 | caption | [431.0, 120, 56.5, 36] |
| period_labels.3 | 0 | 20 | caption | [495.5, 120, 56.5, 36] |
| period_labels.4 | 0 | 20 | caption | [560.0, 120, 56.5, 36] |
| period_labels.5 | 0 | 20 | caption | [624.5, 120, 56.5, 36] |
| period_labels.6 | 0 | 20 | caption | [689.0, 120, 56.5, 36] |
| period_labels.7 | 0 | 20 | caption | [753.5, 120, 56.5, 36] |
| period_labels.8 | 0 | 20 | caption | [818.0, 120, 56.5, 36] |
| period_labels.9 | 0 | 20 | caption | [882.5, 120, 56.5, 36] |
| period_labels.10 | 0 | 20 | caption | [947.0, 120, 56.5, 36] |
| period_labels.11 | 0 | 20 | caption | [1011.5, 120, 56.5, 36] |
| tasks.0.name | 1 | 24 | body | [48, 186.0, 234, 64.0] |
| tasks.0.owner | 0 | 16 | caption | [1084, 186.0, 148, 64.0] |
| tasks.0.progress | 0 | 8 | caption | [302, 222.0, 766, 24] |
| tasks.1.name | 1 | 24 | body | [48, 262.0, 234, 64.0] |
| tasks.1.owner | 0 | 16 | caption | [1084, 262.0, 148, 64.0] |
| tasks.1.progress | 0 | 8 | caption | [302, 298.0, 766, 24] |
| tasks.2.name | 1 | 24 | body | [48, 338.0, 234, 64.0] |
| tasks.2.owner | 0 | 16 | caption | [1084, 338.0, 148, 64.0] |
| tasks.2.progress | 0 | 8 | caption | [302, 374.0, 766, 24] |
| tasks.3.name | 1 | 24 | body | [48, 414.0, 234, 64.0] |
| tasks.3.owner | 0 | 16 | caption | [1084, 414.0, 148, 64.0] |
| tasks.3.progress | 0 | 8 | caption | [302, 450.0, 766, 24] |
| tasks.4.name | 1 | 24 | body | [48, 490.0, 234, 64.0] |
| tasks.4.owner | 0 | 16 | caption | [1084, 490.0, 148, 64.0] |
| tasks.4.progress | 0 | 8 | caption | [302, 526.0, 766, 24] |
| tasks.5.name | 1 | 24 | body | [48, 566.0, 234, 64.0] |
| tasks.5.owner | 0 | 16 | caption | [1084, 566.0, 148, 64.0] |
| tasks.5.progress | 0 | 8 | caption | [302, 602.0, 766, 24] |
### halfyear-6

六时间区段、四任务，适用于较疏的计划概览；默认展示全年，也支持半年、跨年或其他合法期间。

Layout为`gantt-halfyear-6`，原型为`templates/prototypes/09b_gantt_halfyear-6.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| period_range | 21 | 21 | caption | [48, 120, 234, 44] |
| period_labels.0 | 0 | 20 | caption | [302.0, 120, 121.0, 36] |
| period_labels.1 | 0 | 20 | caption | [431.0, 120, 121.0, 36] |
| period_labels.2 | 0 | 20 | caption | [560.0, 120, 121.0, 36] |
| period_labels.3 | 0 | 20 | caption | [689.0, 120, 121.0, 36] |
| period_labels.4 | 0 | 20 | caption | [818.0, 120, 121.0, 36] |
| period_labels.5 | 0 | 20 | caption | [947.0, 120, 121.0, 36] |
| tasks.0.name | 1 | 24 | body | [48, 186.0, 234, 102.0] |
| tasks.0.owner | 0 | 16 | caption | [1084, 186.0, 148, 102.0] |
| tasks.0.progress | 0 | 8 | caption | [302, 222.0, 766, 24] |
| tasks.1.name | 1 | 24 | body | [48, 300.0, 234, 102.0] |
| tasks.1.owner | 0 | 16 | caption | [1084, 300.0, 148, 102.0] |
| tasks.1.progress | 0 | 8 | caption | [302, 336.0, 766, 24] |
| tasks.2.name | 1 | 24 | body | [48, 414.0, 234, 102.0] |
| tasks.2.owner | 0 | 16 | caption | [1084, 414.0, 148, 102.0] |
| tasks.2.progress | 0 | 8 | caption | [302, 450.0, 766, 24] |
| tasks.3.name | 1 | 24 | body | [48, 528.0, 234, 102.0] |
| tasks.3.owner | 0 | 16 | caption | [1084, 528.0, 148, 102.0] |
| tasks.3.progress | 0 | 8 | caption | [302, 564.0, 766, 24] |

## 使用步骤

1. 先确认材料确有本页型所表达的关系，选择`family=gantt`及兼容variant。
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
  "date_format": {
    "enum": [
      "%m",
      "%Y-%m",
      "%m-%d"
    ],
    "description": "甘特刻度使用各等时间区段的实际起始日期。兼容值%m显示为月/日以区分同月刻度，%Y-%m或%m-%d沿所选格式显示；相邻重复标签留空。完整首末日期始终显示。",
    "default": "%m"
  },
  "show_owner": {
    "type": "boolean",
    "default": true
  },
  "show_progress": {
    "type": "boolean",
    "default": true
  }
}
```

允许字段来自page-catalog.json与pages.schema.json。tokens控制全局几何、字阶、颜色、间距和线条。字号通过body_role选择已登记字阶。切换variant后重新校验输入容量。

## 来源与检查

来源为500页-01商务蓝配色.pptx，第250、256页。原始文件指纹及资产处理见asset-provenance.json。当前原型完成结构生成与文本测量，实际渲染和原生编辑范围以交付检查记录为准。

catalog指纹为`cb0b762dd09720f0095cb5d682a87348e0608e2f8d5fdf784ec1d4ef62f73010`，tokens指纹为`2bb967b3a61bf7a4072665f712f39ac49458d22ebe9407f269236c21adc366f3`，参数schema指纹为`add0f4b9d6bc61cd5cae5ce6d6821748442ed906b6b779cc561790e85b605ff5`。
