# 目录

说明报告的组成及顺序

类型为汇报组织，语义入口为`ppt.toc`。

## 使用场景

存在真实章节与顺序，需要听众建立路线。

关系要求为章节顺序。缺少必要输入时说明具体字段与来源缺口，再选择资料能支持的表达。

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
    "items": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "title": {
            "type": "string",
            "minLength": 1,
            "maxLength": 24
          },
          "description": {
            "type": "string",
            "minLength": 0,
            "maxLength": 64
          }
        },
        "required": [
          "title"
        ],
        "additionalProperties": false
      },
      "minItems": 1,
      "maxItems": 6
    }
  },
  "required": [
    "title",
    "items"
  ],
  "additionalProperties": false
}
```

## 变体与容量

### grid6

三列两行，最多六项。

Layout为`toc-grid6`，原型为`templates/prototypes/02a_toc_grid6.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| items.0.title | 1 | 24 | heading | [72.0, 144.0, 330.6666666666667, 52] |
| items.0.description | 0 | 64 | body | [72.0, 212.0, 330.6666666666667, 136.0] |
| items.1.title | 1 | 24 | heading | [474.6666666666667, 144.0, 330.6666666666667, 52] |
| items.1.description | 0 | 64 | body | [474.6666666666667, 212.0, 330.6666666666667, 136.0] |
| items.2.title | 1 | 24 | heading | [877.3333333333334, 144.0, 330.6666666666667, 52] |
| items.2.description | 0 | 64 | body | [877.3333333333334, 212.0, 330.6666666666667, 136.0] |
| items.3.title | 1 | 24 | heading | [72.0, 420.0, 330.6666666666667, 52] |
| items.3.description | 0 | 64 | body | [72.0, 488.0, 330.6666666666667, 136.0] |
| items.4.title | 1 | 24 | heading | [474.6666666666667, 420.0, 330.6666666666667, 52] |
| items.4.description | 0 | 64 | body | [474.6666666666667, 488.0, 330.6666666666667, 136.0] |
| items.5.title | 1 | 24 | heading | [877.3333333333334, 420.0, 330.6666666666667, 52] |
| items.5.description | 0 | 64 | body | [877.3333333333334, 488.0, 330.6666666666667, 136.0] |
### list4

四行长标题与描述。

Layout为`toc-list4`，原型为`templates/prototypes/02b_toc_list4.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| items.0.title | 1 | 24 | heading | [72.0, 144.0, 331.2, 66.0] |
| items.0.description | 0 | 64 | body | [450.56, 144.0, 757.44, 66.0] |
| items.1.title | 1 | 24 | heading | [72.0, 282.0, 331.2, 66.0] |
| items.1.description | 0 | 64 | body | [450.56, 282.0, 757.44, 66.0] |
| items.2.title | 1 | 24 | heading | [72.0, 420.0, 331.2, 66.0] |
| items.2.description | 0 | 64 | body | [450.56, 420.0, 757.44, 66.0] |
| items.3.title | 1 | 24 | heading | [72.0, 558.0, 331.2, 66.0] |
| items.3.description | 0 | 64 | body | [450.56, 558.0, 757.44, 66.0] |

## 使用步骤

1. 先确认材料确有本页型所表达的关系，选择`family=toc`及兼容variant。
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

来源为500页-01商务蓝配色.pptx，第8页。原始文件指纹及资产处理见asset-provenance.json。当前原型完成结构生成与文本测量，实际渲染和原生编辑范围以交付检查记录为准。

catalog指纹为`cb0b762dd09720f0095cb5d682a87348e0608e2f8d5fdf784ec1d4ef62f73010`，tokens指纹为`2bb967b3a61bf7a4072665f712f39ac49458d22ebe9407f269236c21adc366f3`，参数schema指纹为`add0f4b9d6bc61cd5cae5ce6d6821748442ed906b6b779cc561790e85b605ff5`。
