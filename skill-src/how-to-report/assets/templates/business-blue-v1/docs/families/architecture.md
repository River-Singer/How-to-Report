# 分层架构

解释层级与各层职责

类型为信息结构，语义入口为`ppt.architecture`。

## 使用场景

资料确有分层、依赖或支撑关系。

关系要求为层级与职责。缺少必要输入时说明具体字段与来源缺口，再选择资料能支持的表达。

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
    "layers": {
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
      "maxItems": 4
    }
  },
  "required": [
    "title",
    "layers"
  ],
  "additionalProperties": false
}
```

## 变体与容量

图标来自用户PPT图标.pptx的首批24项，键与来源见icons/catalog.json。所有本家族variant均消费`content.layers[].icon_key`。例如填入`team`并保持`config.show_icons=true`。空键或关闭开关隐藏图标，未知键在validate阶段报错。

图标以primary色等比适配独立预留区，开关使用相同Layout与文字框。并列卡及线性流程使用卡片底部内边距，循环与环绕节点使用左侧栏，战略屋使用支柱底带，架构层使用标题与说明间隙，图片页使用说明标题上方空白。正文容量继续按原文字框实际测量。

### layers-4

四层平行分区。

Layout为`architecture-layers-4`，原型为`templates/prototypes/14a_architecture_layers-4.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| layers.0.title | 1 | 16 | heading | [68, 140.0, 230, 82.0] |
| layers.0.body | 1 | 100 | body | [328, 140.0, 880, 82.0] |
| layers.1.title | 1 | 16 | heading | [68, 278.0, 230, 82.0] |
| layers.1.body | 1 | 100 | body | [328, 278.0, 880, 82.0] |
| layers.2.title | 1 | 16 | heading | [68, 416.0, 230, 82.0] |
| layers.2.body | 1 | 100 | body | [328, 416.0, 880, 82.0] |
| layers.3.title | 1 | 16 | heading | [68, 554.0, 230, 82.0] |
| layers.3.body | 1 | 100 | body | [328, 554.0, 880, 82.0] |
### stack-3

三层逐级堆叠。

Layout为`architecture-stack-3`，原型为`templates/prototypes/14b_architecture_stack-3.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| layers.0.title | 1 | 16 | heading | [68, 140.0, 230, 128.0] |
| layers.0.body | 1 | 100 | body | [328, 140.0, 880, 128.0] |
| layers.1.title | 1 | 16 | heading | [92, 324.0, 230, 128.0] |
| layers.1.body | 1 | 100 | body | [352, 324.0, 832, 128.0] |
| layers.2.title | 1 | 16 | heading | [116, 508.0, 230, 128.0] |
| layers.2.body | 1 | 100 | body | [376, 508.0, 784, 128.0] |

## 使用步骤

1. 先确认材料确有本页型所表达的关系，选择`family=architecture`及兼容variant。
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

来源为蓝色逻辑架构图.pptx，第12页；立体结构逻辑图1122.pptx，第18、31页。原始文件指纹及资产处理见asset-provenance.json。当前原型完成结构生成与文本测量，实际渲染和原生编辑范围以交付检查记录为准。

catalog指纹为`498fe133ea2d00699bb4c4ea5bc798e78130623b21eea5d3cc8cb10e125af78b`，tokens指纹为`2bb967b3a61bf7a4072665f712f39ac49458d22ebe9407f269236c21adc366f3`，参数schema指纹为`6981096e740f47c827294403dd132d6609fd537f46b15e8164c4b630b9822a61`。
