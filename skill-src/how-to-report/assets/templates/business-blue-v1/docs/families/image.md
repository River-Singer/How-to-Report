# 图文案例

展示图片证据与相应解释

类型为汇报组织，语义入口为`ppt.image`。

## 使用场景

有实际图片或截图，关键区域在最终尺寸可辨。

关系要求为图片与说明对应。缺少必要输入时说明具体字段与来源缺口，再选择资料能支持的表达。

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
    "images": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "path": {
            "type": "string",
            "minLength": 0,
            "maxLength": 240
          },
          "alt": {
            "type": "string",
            "minLength": 0,
            "maxLength": 100
          },
          "caption": {
            "type": "string",
            "minLength": 0,
            "maxLength": 56
          }
        },
        "required": [],
        "additionalProperties": false
      },
      "minItems": 0,
      "maxItems": 3
    },
    "sections": {
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
      "maxItems": 3
    }
  },
  "required": [
    "title",
    "sections"
  ],
  "additionalProperties": false
}
```

## 变体与容量

先判断图片承担数据输入、证据原貌、界面演示或插图的具体用途。数据输入先提炼信息并形成可编辑指标、图形或图表；界面演示与插图按听众需要选择可辨主体。

variant提供统一正文区内的图片框与独立说明框。image_fit=contain完整显示，适合保留轴、单位、日期与界面上下文；image_fit=cover等比填满并裁去框外部分，适合主体可安全保留的插图。

config.image_position提供九锚点焦点，xMin/xMid/xMax对应左/中/右，YMin/YMid/YMax对应上/中/下，默认xMidYMid。例如cover搭配xMaxYMin优先保留右上主体。配置作用于本页图片，需逐图不同焦点时分配到相应页面或在原生PPT中调整。

实际查看图片有效内容与多余白边，再选择框体、完整显示或焦点安全裁剪。重要标签、来源、水印和必要上下文随用途保留，最终尺寸需可读。原始本地资源完整复制到项目images，成品保存原生图片与裁剪参数；嵌入媒体可能按既有引擎规则规范化或等比优化，原始字节由项目资源留存。

caption与sections为独立可编辑文本，alt进入SVG desc；当前未单独验证PowerPoint替代文字。九锚点复用原生srcRect裁剪，任意焦点矩形与像素编辑不在当前参数合同中。

图标来自用户PPT图标.pptx的首批24项，键与来源见icons/catalog.json。所有本家族variant均消费`content.sections[].icon_key`。例如填入`team`并保持`config.show_icons=true`。空键或关闭开关隐藏图标，未知键在validate阶段报错。

图标以primary色等比适配独立预留区，开关使用相同Layout与文字框。并列卡及线性流程使用卡片底部内边距，循环与环绕节点使用左侧栏，战略屋使用支柱底带，架构层使用标题与说明间隙，图片页使用说明标题上方空白。正文容量继续按原文字框实际测量。

### hero-right

左侧说明与右侧完整图片。

Layout为`image-hero-right`，原型为`templates/prototypes/11a_image_hero-right.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| images.0.caption | 0 | 40 | caption | [616.3199999999999, 594, 615.6800000000001, 50] |
| sections.0.title | 1 | 18 | heading | [48, 144, 509.12, 70] |
| sections.0.body | 1 | 120 | body | [48, 230, 509.12, 398] |
### gallery-3

三项图文并列。

Layout为`image-gallery-3`，原型为`templates/prototypes/11b_image_gallery-3.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| images.0.caption | 0 | 40 | caption | [48.0, 372, 378.6666666666667, 50] |
| sections.0.title | 1 | 18 | heading | [48.0, 450, 378.6666666666667, 70] |
| sections.0.body | 1 | 72 | body | [48.0, 536, 378.6666666666667, 110] |
| images.1.caption | 0 | 40 | caption | [450.6666666666667, 372, 378.6666666666667, 50] |
| sections.1.title | 1 | 18 | heading | [450.6666666666667, 450, 378.6666666666667, 70] |
| sections.1.body | 1 | 72 | body | [450.6666666666667, 536, 378.6666666666667, 110] |
| images.2.caption | 0 | 40 | caption | [853.3333333333334, 372, 378.6666666666667, 50] |
| sections.2.title | 1 | 18 | heading | [853.3333333333334, 450, 378.6666666666667, 70] |
| sections.2.body | 1 | 72 | body | [853.3333333333334, 536, 378.6666666666667, 110] |

## 使用步骤

1. 先确认材料确有本页型所表达的关系，选择`family=image`及兼容variant。
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
  "image_fit": {
    "enum": [
      "contain",
      "cover"
    ],
    "default": "contain"
  },
  "image_position": {
    "enum": [
      "xMinYMin",
      "xMidYMin",
      "xMaxYMin",
      "xMinYMid",
      "xMidYMid",
      "xMaxYMid",
      "xMinYMax",
      "xMidYMax",
      "xMaxYMax"
    ],
    "description": "图片完整显示或填框裁剪时的对齐焦点，x为左/中/右，Y为上/中/下。默认xMidYMid。与image_fit共同生效，保留原图完整画面供原生重裁。",
    "default": "xMidYMid"
  },
  "show_icons": {
    "type": "boolean",
    "default": true
  }
}
```

允许字段来自page-catalog.json与pages.schema.json。tokens控制全局几何、字阶、颜色、间距和线条。字号通过body_role选择已登记字阶。切换variant后重新校验输入容量。

## 来源与检查

来源为500页-01商务蓝配色.pptx，第467、475页。原始文件指纹及资产处理见asset-provenance.json。当前原型完成结构生成与文本测量，实际渲染和原生编辑范围以交付检查记录为准。

catalog指纹为`cb0b762dd09720f0095cb5d682a87348e0608e2f8d5fdf784ec1d4ef62f73010`，tokens指纹为`2bb967b3a61bf7a4072665f712f39ac49458d22ebe9407f269236c21adc366f3`，参数schema指纹为`add0f4b9d6bc61cd5cae5ce6d6821748442ed906b6b779cc561790e85b605ff5`。
