# 并列事项

展示同层级事项及各自解释

类型为信息结构，语义入口为`ppt.parallel`。

## 使用场景

资料确实形成并列关系，内容不依赖先后。

关系要求为并列。缺少必要输入时说明具体字段与来源缺口，再选择资料能支持的表达。

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
    "items"
  ],
  "additionalProperties": false
}
```

## 变体与容量

并列事项支持两列、三列、三行和四张2×2卡片。省略variant时，两项选择columns-2、四项选择grid-4，一项或三项沿原columns-3。可显式指定rows-3保留原横向长说明。

新增columns-2和grid-4要求数组数量分别为2和4，各卡标题与正文长度见variant表，并继续做真实字体测量。内容以独立文字呈现，关系和说明完整保留。

图标来自用户PPT图标.pptx的首批24项，键与来源见icons/catalog.json。所有本家族variant均消费`content.items[].icon_key`。例如填入`team`并保持`config.show_icons=true`。空键或关闭开关隐藏图标，未知键在validate阶段报错。

图标以primary色等比适配独立预留区，开关使用相同Layout与文字框。并列卡及线性流程使用卡片底部内边距，循环与环绕节点使用左侧栏，战略屋使用支柱底带，架构层使用标题与说明间隙，图片页使用说明标题上方空白。正文容量继续按原文字框实际测量。

### columns-3

三列等宽，适合短说明。

Layout为`parallel-columns-3`，原型为`templates/prototypes/05a_parallel_columns-3.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| items.0.title | 1 | 24 | heading | [72.0, 144.0, 330.6666666666667, 52] |
| items.0.body | 1 | 120 | body | [72.0, 212.0, 330.6666666666667, 412.0] |
| items.1.title | 1 | 24 | heading | [474.6666666666667, 144.0, 330.6666666666667, 52] |
| items.1.body | 1 | 120 | body | [474.6666666666667, 212.0, 330.6666666666667, 412.0] |
| items.2.title | 1 | 24 | heading | [877.3333333333334, 144.0, 330.6666666666667, 52] |
| items.2.body | 1 | 120 | body | [877.3333333333334, 212.0, 330.6666666666667, 412.0] |
### rows-3

三行等高，适合横向长说明。

Layout为`parallel-rows-3`，原型为`templates/prototypes/05b_parallel_rows-3.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| items.0.title | 1 | 24 | heading | [72.0, 144.0, 331.2, 112.0] |
| items.0.body | 1 | 120 | body | [450.56, 144.0, 757.44, 112.0] |
| items.1.title | 1 | 24 | heading | [72.0, 328.0, 331.2, 112.0] |
| items.1.body | 1 | 120 | body | [450.56, 328.0, 757.44, 112.0] |
| items.2.title | 1 | 24 | heading | [72.0, 512.0, 331.2, 112.0] |
| items.2.body | 1 | 120 | body | [450.56, 512.0, 757.44, 112.0] |
### columns-2

2张等宽卡片，2列排布。单卡标题1至17字，正文1至120字，继续检查实际字体与框体。

Layout为`parallel-columns-2`，原型为`templates/prototypes/05c_parallel_columns-2.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| items.0.title | 1 | 17 | heading | [72.0, 144.0, 532.0, 52] |
| items.0.body | 1 | 120 | body | [72.0, 212.0, 532.0, 412.0] |
| items.1.title | 1 | 17 | heading | [676.0, 144.0, 532.0, 52] |
| items.1.body | 1 | 120 | body | [676.0, 212.0, 532.0, 412.0] |
### grid-4

4张等宽卡片，2列排布。单卡标题1至17字，正文1至80字，继续检查实际字体与框体。

Layout为`parallel-grid-4`，原型为`templates/prototypes/05d_parallel_grid-4.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| items.0.title | 1 | 17 | heading | [72.0, 144.0, 532.0, 52] |
| items.0.body | 1 | 80 | body | [72.0, 212.0, 532.0, 136.0] |
| items.1.title | 1 | 17 | heading | [676.0, 144.0, 532.0, 52] |
| items.1.body | 1 | 80 | body | [676.0, 212.0, 532.0, 136.0] |
| items.2.title | 1 | 17 | heading | [72.0, 420.0, 532.0, 52] |
| items.2.body | 1 | 80 | body | [72.0, 488.0, 532.0, 136.0] |
| items.3.title | 1 | 17 | heading | [676.0, 420.0, 532.0, 52] |
| items.3.body | 1 | 80 | body | [676.0, 488.0, 532.0, 136.0] |

## 使用步骤

1. 先确认材料确有本页型所表达的关系，选择`family=parallel`及兼容variant。
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

来源为500页-01商务蓝配色.pptx，第23、531页。原始文件指纹及资产处理见asset-provenance.json。当前原型完成结构生成与文本测量，实际渲染和原生编辑范围以交付检查记录为准。

catalog指纹为`498fe133ea2d00699bb4c4ea5bc798e78130623b21eea5d3cc8cb10e125af78b`，tokens指纹为`2bb967b3a61bf7a4072665f712f39ac49458d22ebe9407f269236c21adc366f3`，参数schema指纹为`6981096e740f47c827294403dd132d6609fd537f46b15e8164c4b630b9822a61`。
