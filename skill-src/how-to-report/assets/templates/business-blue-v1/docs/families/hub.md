# 中心辐射

解释共同中心与周边对象的关系

类型为信息结构，语义入口为`ppt.hub`。

## 使用场景

中心归属或关联由来源支持。

关系要求为中心归属或关联。缺少必要输入时说明具体字段与来源缺口，再选择资料能支持的表达。

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
    "center": {
      "type": "object",
      "properties": {
        "title": {
          "type": "string",
          "minLength": 1,
          "maxLength": 12
        },
        "body": {
          "type": "string",
          "minLength": 0,
          "maxLength": 36
        }
      },
      "required": [
        "title"
      ],
      "additionalProperties": false
    },
    "nodes": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "title": {
            "type": "string",
            "minLength": 1,
            "maxLength": 24
          },
          "body": {
            "type": "string",
            "minLength": 1,
            "maxLength": 120
          },
          "icon_key": {
            "type": "string",
            "minLength": 0,
            "maxLength": 40
          }
        },
        "required": [
          "title",
          "body"
        ],
        "additionalProperties": false
      },
      "minItems": 1,
      "maxItems": 5
    }
  },
  "required": [
    "title",
    "center",
    "nodes"
  ],
  "additionalProperties": false
}
```

## 变体与容量

图标来自用户PPT图标.pptx的首批24项，键与来源见icons/catalog.json。所有本家族variant均消费`content.nodes[].icon_key`。例如填入`team`并保持`config.show_icons=true`。空键或关闭开关隐藏图标，未知键在validate阶段报错。

图标以primary色等比适配独立预留区，开关使用相同Layout与文字框。并列卡及线性流程使用卡片底部内边距，循环与环绕节点使用左侧栏，战略屋使用支柱底带，架构层使用标题与说明间隙，图片页使用说明标题上方空白。正文容量继续按原文字框实际测量。

### spokes-4

中心及四个周边关联。

Layout为`hub-spokes-4`，原型为`templates/prototypes/16a_hub_spokes-4.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| center.title | 1 | 12 | heading | [530.0, 341.0, 220, 44] |
| center.body | 0 | 36 | caption | [530.0, 392.0, 220, 44] |
| nodes.0.title | 1 | 16 | heading | [526.0, 171.04, 228, 46] |
| nodes.0.body | 1 | 48 | caption | [526.0, 223.04, 228, 44] |
| nodes.1.title | 1 | 16 | heading | [928.56, 340.0, 228, 46] |
| nodes.1.body | 1 | 48 | caption | [928.56, 392.0, 228, 44] |
| nodes.2.title | 1 | 16 | heading | [526.0, 508.96000000000004, 228, 46] |
| nodes.2.body | 1 | 48 | caption | [526.0, 560.96, 228, 44] |
| nodes.3.title | 1 | 16 | heading | [123.44, 340.0, 228, 46] |
| nodes.3.body | 1 | 48 | caption | [123.44, 392.0, 228, 44] |
### ring-5

中心及五个环形分区。

Layout为`hub-ring-5`，原型为`templates/prototypes/16b_hub_ring-5.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| center.title | 1 | 12 | heading | [530.0, 341.0, 220, 44] |
| center.body | 0 | 36 | caption | [530.0, 392.0, 220, 44] |
| nodes.0.title | 1 | 16 | heading | [526.0, 171.04, 228, 46] |
| nodes.0.body | 1 | 48 | caption | [526.0, 223.04, 228, 44] |
| nodes.1.title | 1 | 16 | heading | [908.8573111997771, 287.7884886304089, 228, 46] |
| nodes.1.body | 1 | 48 | caption | [908.8573111997771, 339.7884886304089, 228, 44] |
| nodes.2.title | 1 | 16 | heading | [762.618831162858, 476.6915113695911, 228, 46] |
| nodes.2.body | 1 | 48 | caption | [762.618831162858, 528.6915113695911, 228, 44] |
| nodes.3.title | 1 | 16 | heading | [289.38116883714207, 476.6915113695911, 228, 46] |
| nodes.3.body | 1 | 48 | caption | [289.38116883714207, 528.6915113695911, 228, 44] |
| nodes.4.title | 1 | 16 | heading | [143.14268880022297, 287.7884886304089, 228, 46] |
| nodes.4.body | 1 | 48 | caption | [143.14268880022297, 339.7884886304089, 228, 44] |

## 使用步骤

1. 先确认材料确有本页型所表达的关系，选择`family=hub`及兼容variant。
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
  "show_icons": {
    "type": "boolean",
    "default": true
  }
}
```

允许字段来自page-catalog.json与pages.schema.json。tokens控制全局几何、字阶、颜色、间距和线条。字号通过body_role选择已登记字阶。切换variant后重新校验输入容量。

## 来源与检查

来源为圆形逻辑图PPT模版.pptx，第17、19页。原始文件指纹及资产处理见asset-provenance.json。当前原型完成结构生成与文本测量，实际渲染和原生编辑范围以交付检查记录为准。

catalog指纹为`cb0b762dd09720f0095cb5d682a87348e0608e2f8d5fdf784ec1d4ef62f73010`，tokens指纹为`2bb967b3a61bf7a4072665f712f39ac49458d22ebe9407f269236c21adc366f3`，参数schema指纹为`add0f4b9d6bc61cd5cae5ce6d6821748442ed906b6b779cc561790e85b605ff5`。
