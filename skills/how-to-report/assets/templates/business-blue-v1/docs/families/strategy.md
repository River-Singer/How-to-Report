# 战略屋

说明共同目标、能力支柱与基础

类型为信息结构，语义入口为`ppt.strategy`。

## 使用场景

资料确有支撑关系，目标、支柱和基础各有内容。

关系要求为目标、支柱与共同基础。缺少必要输入时说明具体字段与来源缺口，再选择资料能支持的表达。

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
    "mission": {
      "type": "string",
      "minLength": 1,
      "maxLength": 48
    },
    "vision": {
      "type": "string",
      "minLength": 0,
      "maxLength": 72
    },
    "pillars": {
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
      "maxItems": 6
    },
    "foundation": {
      "type": "object",
      "properties": {
        "title": {
          "type": "string",
          "minLength": 0,
          "maxLength": 18
        },
        "body": {
          "type": "string",
          "minLength": 0,
          "maxLength": 100
        }
      },
      "required": [],
      "additionalProperties": false
    }
  },
  "required": [
    "title",
    "mission",
    "pillars"
  ],
  "additionalProperties": false
}
```

## 变体与容量

灰色支柱卡支持2至6张等宽单行布局。省略variant时，按content.pillars实际数量选择house-2至house-6，卡片宽度、间距及文字框随所选结构计算。

也可显式指定house-2、house-3、house-4、house-5或house-6。新变体要求支柱数组数量与variant一致。原有显式house-3及单支柱旧输入继续接受1至3项，保留三槽布局；两项内容选择house-2可铺满两张卡。

每张卡的title与body分别提供内容，字符按本说明计数。各variant的最短最长长度见下表，随后执行真实字体测量。5至6张卡应使用简短标题和摘要，详细解释可放口播或另页。超出容量或框体时返回具体字段错误，正文保留完整输入。

调用示意为family=strategy、content.pillars=[{title, body}, …]。增加或减少数组项后重新validate和build；省略variant即可按2至6项重新排布。PowerPoint成品中的卡片是可编辑形状与文字，手工新增后需自行对齐，参数化重排通过修改JSON并重新生成完成。

图标来自用户PPT图标.pptx的首批24项，键与来源见icons/catalog.json。所有本家族variant均消费`content.pillars[].icon_key`。例如填入`team`并保持`config.show_icons=true`。空键或关闭开关隐藏图标，未知键在validate阶段报错。

图标以primary色等比适配独立预留区，开关使用相同Layout与文字框。并列卡及线性流程使用卡片底部内边距，循环与环绕节点使用左侧栏，战略屋使用支柱底带，架构层使用标题与说明间隙，图片页使用说明标题上方空白。正文容量继续按原文字框实际测量。

### house-3

3张等宽支柱卡、目标屋顶和共同基础。单卡标题1至16字，正文1至72字，继续检查实际字体与框体。

Layout为`strategy-house-3`，原型为`templates/prototypes/13a_strategy_house-3.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| mission | 2 | 48 | heading | [415.04, 180, 449.92, 40] |
| vision | 0 | 72 | body | [80, 236, 1120, 60] |
| pillars.0.title | 1 | 16 | heading | [68.0, 340, 338.6666666666667, 50] |
| pillars.0.body | 1 | 72 | body | [68.0, 404, 338.6666666666667, 100] |
| pillars.1.title | 1 | 16 | heading | [470.6666666666667, 340, 338.6666666666667, 50] |
| pillars.1.body | 1 | 72 | body | [470.6666666666667, 404, 338.6666666666667, 100] |
| pillars.2.title | 1 | 16 | heading | [873.3333333333334, 340, 338.6666666666667, 50] |
| pillars.2.body | 1 | 72 | body | [873.3333333333334, 404, 338.6666666666667, 100] |
| foundation.title | 0 | 18 | heading | [68, 568, 272.32, 50] |
| foundation.body | 0 | 100 | body | [367.68, 568, 828.8, 60] |
### house-2

2张等宽支柱卡、目标屋顶和共同基础。单卡标题1至18字，正文1至63字，继续检查实际字体与框体。

Layout为`strategy-house-2`，原型为`templates/prototypes/13b_strategy_house-2.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| mission | 2 | 48 | heading | [415.04, 180, 449.92, 40] |
| vision | 0 | 72 | body | [80, 236, 1120, 60] |
| pillars.0.title | 1 | 18 | heading | [68.0, 340, 540.0, 50] |
| pillars.0.body | 1 | 63 | body | [68.0, 404, 540.0, 100] |
| pillars.1.title | 1 | 18 | heading | [672.0, 340, 540.0, 50] |
| pillars.1.body | 1 | 63 | body | [672.0, 404, 540.0, 100] |
| foundation.title | 0 | 18 | heading | [68, 568, 272.32, 50] |
| foundation.body | 0 | 100 | body | [367.68, 568, 828.8, 60] |
### house-4

4张等宽支柱卡、目标屋顶和共同基础。单卡标题1至8字，正文1至27字，继续检查实际字体与框体。

Layout为`strategy-house-4`，原型为`templates/prototypes/13c_strategy_house-4.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| mission | 2 | 48 | heading | [415.04, 180, 449.92, 40] |
| vision | 0 | 72 | body | [80, 236, 1120, 60] |
| pillars.0.title | 1 | 8 | heading | [68.0, 340, 238.0, 50] |
| pillars.0.body | 1 | 27 | body | [68.0, 404, 238.0, 100] |
| pillars.1.title | 1 | 8 | heading | [370.0, 340, 238.0, 50] |
| pillars.1.body | 1 | 27 | body | [370.0, 404, 238.0, 100] |
| pillars.2.title | 1 | 8 | heading | [672.0, 340, 238.0, 50] |
| pillars.2.body | 1 | 27 | body | [672.0, 404, 238.0, 100] |
| pillars.3.title | 1 | 8 | heading | [974.0, 340, 238.0, 50] |
| pillars.3.body | 1 | 27 | body | [974.0, 404, 238.0, 100] |
| foundation.title | 0 | 18 | heading | [68, 568, 272.32, 50] |
| foundation.body | 0 | 100 | body | [367.68, 568, 828.8, 60] |
### house-5

5张等宽支柱卡、目标屋顶和共同基础。单卡标题1至5字，正文1至18字，继续检查实际字体与框体。

Layout为`strategy-house-5`，原型为`templates/prototypes/13d_strategy_house-5.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| mission | 2 | 48 | heading | [415.04, 180, 449.92, 40] |
| vision | 0 | 72 | body | [80, 236, 1120, 60] |
| pillars.0.title | 1 | 5 | heading | [68.0, 340, 177.6, 50] |
| pillars.0.body | 1 | 18 | body | [68.0, 404, 177.6, 100] |
| pillars.1.title | 1 | 5 | heading | [309.6, 340, 177.6, 50] |
| pillars.1.body | 1 | 18 | body | [309.6, 404, 177.6, 100] |
| pillars.2.title | 1 | 5 | heading | [551.2, 340, 177.6, 50] |
| pillars.2.body | 1 | 18 | body | [551.2, 404, 177.6, 100] |
| pillars.3.title | 1 | 5 | heading | [792.8, 340, 177.6, 50] |
| pillars.3.body | 1 | 18 | body | [792.8, 404, 177.6, 100] |
| pillars.4.title | 1 | 5 | heading | [1034.4, 340, 177.6, 50] |
| pillars.4.body | 1 | 18 | body | [1034.4, 404, 177.6, 100] |
| foundation.title | 0 | 18 | heading | [68, 568, 272.32, 50] |
| foundation.body | 0 | 100 | body | [367.68, 568, 828.8, 60] |
### house-6

6张等宽支柱卡、目标屋顶和共同基础。单卡标题1至4字，正文1至15字，继续检查实际字体与框体。

Layout为`strategy-house-6`，原型为`templates/prototypes/13e_strategy_house-6.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| mission | 2 | 48 | heading | [415.04, 180, 449.92, 40] |
| vision | 0 | 72 | body | [80, 236, 1120, 60] |
| pillars.0.title | 1 | 4 | heading | [68.0, 340, 137.33333333333334, 50] |
| pillars.0.body | 1 | 15 | body | [68.0, 404, 137.33333333333334, 100] |
| pillars.1.title | 1 | 4 | heading | [269.33333333333337, 340, 137.33333333333334, 50] |
| pillars.1.body | 1 | 15 | body | [269.33333333333337, 404, 137.33333333333334, 100] |
| pillars.2.title | 1 | 4 | heading | [470.6666666666667, 340, 137.33333333333334, 50] |
| pillars.2.body | 1 | 15 | body | [470.6666666666667, 404, 137.33333333333334, 100] |
| pillars.3.title | 1 | 4 | heading | [672.0, 340, 137.33333333333334, 50] |
| pillars.3.body | 1 | 15 | body | [672.0, 404, 137.33333333333334, 100] |
| pillars.4.title | 1 | 4 | heading | [873.3333333333334, 340, 137.33333333333334, 50] |
| pillars.4.body | 1 | 15 | body | [873.3333333333334, 404, 137.33333333333334, 100] |
| pillars.5.title | 1 | 4 | heading | [1074.6666666666667, 340, 137.33333333333334, 50] |
| pillars.5.body | 1 | 15 | body | [1074.6666666666667, 404, 137.33333333333334, 100] |
| foundation.title | 0 | 18 | heading | [68, 568, 272.32, 50] |
| foundation.body | 0 | 100 | body | [367.68, 568, 828.8, 60] |

## 使用步骤

1. 先确认材料确有本页型所表达的关系，选择`family=strategy`及兼容variant。
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

来源为房子图战略图.pptx，第2、21页。原始文件指纹及资产处理见asset-provenance.json。当前原型完成结构生成与文本测量，实际渲染和原生编辑范围以交付检查记录为准。

catalog指纹为`498fe133ea2d00699bb4c4ea5bc798e78130623b21eea5d3cc8cb10e125af78b`，tokens指纹为`2bb967b3a61bf7a4072665f712f39ac49458d22ebe9407f269236c21adc366f3`，参数schema指纹为`6981096e740f47c827294403dd132d6609fd537f46b15e8164c4b630b9822a61`。
