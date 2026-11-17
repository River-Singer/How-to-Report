# 封面

交代汇报主题和发言信息

类型为汇报组织，语义入口为`ppt.cover`。

## 使用场景

开始汇报，需要明确主题、身份和日期。

关系要求为主题和身份。缺少必要输入时说明具体字段与来源缺口，再选择资料能支持的表达。

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
    "topic": {
      "type": "string",
      "minLength": 0,
      "maxLength": 20
    },
    "subtitle": {
      "type": "string",
      "minLength": 0,
      "maxLength": 40
    },
    "author": {
      "type": "string",
      "minLength": 0,
      "maxLength": 20
    },
    "department": {
      "type": "string",
      "minLength": 0,
      "maxLength": 30
    },
    "date": {
      "type": "string",
      "minLength": 0,
      "maxLength": 20
    }
  },
  "required": [
    "title"
  ],
  "additionalProperties": false
}
```

## 变体与容量

### arrow

白底完整上升折线箭头，按源第6页shape 19的14点轮廓等比缩放，适合主题与简短副标题。

Layout为`cover-arrow`，原型为`templates/prototypes/01a_cover_arrow.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| topic | 0 | 20 | heading | [48, 144, 923.52, 42] |
| subtitle | 0 | 40 | chapter | [48, 220, 923.52, 156] |
| author | 0 | 20 | body | [48.0, 576, 367.04, 44] |
| department | 0 | 30 | body | [442.6666666666667, 576, 367.04, 44] |
| date | 0 | 20 | body | [837.3333333333334, 576, 367.04, 44] |
### split

主题与发言信息分区，适合多项身份信息。

Layout为`cover-split`，原型为`templates/prototypes/01b_cover_split.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| topic | 0 | 20 | heading | [48, 144, 734.08, 42] |
| subtitle | 0 | 40 | chapter | [48, 220, 734.08, 156] |
| author | 0 | 20 | body | [924.16, 400, 296.0, 44] |
| department | 0 | 30 | body | [924.16, 458, 296.0, 44] |
| date | 0 | 20 | body | [924.16, 516, 296.0, 44] |

## 使用步骤

1. 先确认材料确有本页型所表达的关系，选择`family=cover`及兼容variant。
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

来源为500页-01商务蓝配色.pptx，第6页。原始文件指纹及资产处理见asset-provenance.json。当前原型完成结构生成与文本测量，实际渲染和原生编辑范围以交付检查记录为准。

catalog指纹为`498fe133ea2d00699bb4c4ea5bc798e78130623b21eea5d3cc8cb10e125af78b`，tokens指纹为`2bb967b3a61bf7a4072665f712f39ac49458d22ebe9407f269236c21adc366f3`，参数schema指纹为`6981096e740f47c827294403dd132d6609fd537f46b15e8164c4b630b9822a61`。
