# 树状层级

表达根节点、分支与子项的有据归属关系

类型为信息结构，语义入口为`ppt.hierarchy`。

## 使用场景

组织结构、职责分解、决策分类树。二至三层且每个子项有唯一父节点。

关系要求为有根层级与唯一父节点归属。缺少必要输入时说明具体字段与来源缺口，再选择资料能支持的表达。

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
    "root": {
      "type": "object",
      "properties": {
        "title": {
          "type": "string",
          "minLength": 1,
          "maxLength": 12
        },
        "body": {
          "type": "string",
          "minLength": 1,
          "maxLength": 36
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
    "branches": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "title": {
            "type": "string",
            "minLength": 1,
            "maxLength": 12
          },
          "body": {
            "type": "string",
            "minLength": 1,
            "maxLength": 36
          },
          "icon_key": {
            "type": "string",
            "minLength": 0,
            "maxLength": 40
          },
          "children": {
            "type": "array",
            "items": {
              "type": "object",
              "properties": {
                "title": {
                  "type": "string",
                  "minLength": 1,
                  "maxLength": 6
                },
                "body": {
                  "type": "string",
                  "minLength": 1,
                  "maxLength": 18
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
            "minItems": 0,
            "maxItems": 2
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
    "root",
    "branches"
  ],
  "additionalProperties": false
}
```

## 变体与容量

`tree`支持一个根节点、一至三个分支及每分支零至两个子项，共二至三层、最多十个节点。数组顺序决定同级顺序，每个children项只归属其所在分支。

根与分支标题最多12字符、正文最多36字符。叶节点标题最多6字符、正文最多18字符。字号来自tokens，真实文字超出槽位时明确报错。

输出为可编辑原生矩形、文字及保留端点的连接器。节点沿Layout数量身份派生。每个节点的文字与矩形分别可编辑。

图标来自用户PPT图标.pptx的首批24项，键与来源见icons/catalog.json。所有本家族variant均消费`content.branches[].icon_key`。例如填入`team`并保持`config.show_icons=true`。空键或关闭开关隐藏图标，未知键在validate阶段报错。

图标以primary色等比适配独立预留区，开关使用相同Layout与文字框。并列卡及线性流程使用卡片底部内边距，循环与环绕节点使用左侧栏，战略屋使用支柱底带，架构层使用标题与说明间隙，图片页使用说明标题上方空白。正文容量继续按原文字框实际测量。

### tree

一个根节点、一至三个分支，每分支零至两个子项，实际生成二至三层树。连接表示归属，无流程箭头。

Layout为`hierarchy-tree`，原型为`templates/prototypes/17a_hierarchy_tree.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| root.title | 1 | 12 | heading | [536.0, 136, 236.0, 42] |
| root.body | 1 | 36 | caption | [508.0, 184, 264.0, 46.72] |
| branches.0.title | 1 | 12 | heading | [133.33333333333334, 336.64, 236.0, 42] |
| branches.0.body | 1 | 36 | caption | [105.33333333333334, 384.64, 264.0, 46.72] |
| branches.1.title | 1 | 12 | heading | [536.0, 336.64, 236.0, 42] |
| branches.1.body | 1 | 36 | caption | [508.0, 384.64, 264.0, 46.72] |
| branches.2.title | 1 | 12 | heading | [938.6666666666667, 336.64, 236.0, 42] |
| branches.2.body | 1 | 36 | caption | [910.6666666666667, 384.64, 264.0, 46.72] |
| branches.0.children.0.title | 1 | 6 | compactBody | [92.0, 537.28, 117.33333333333334, 42] |
| branches.0.children.0.body | 1 | 18 | caption | [64.0, 585.28, 145.33333333333334, 46.72] |
| branches.0.children.1.title | 1 | 6 | compactBody | [293.33333333333337, 537.28, 117.33333333333334, 42] |
| branches.0.children.1.body | 1 | 18 | caption | [265.33333333333337, 585.28, 145.33333333333334, 46.72] |
| branches.1.children.0.title | 1 | 6 | compactBody | [494.6666666666667, 537.28, 117.33333333333334, 42] |
| branches.1.children.0.body | 1 | 18 | caption | [466.6666666666667, 585.28, 145.33333333333334, 46.72] |
| branches.1.children.1.title | 1 | 6 | compactBody | [696.0, 537.28, 117.33333333333334, 42] |
| branches.1.children.1.body | 1 | 18 | caption | [668.0, 585.28, 145.33333333333334, 46.72] |
| branches.2.children.0.title | 1 | 6 | compactBody | [897.3333333333334, 537.28, 117.33333333333334, 42] |
| branches.2.children.0.body | 1 | 18 | caption | [869.3333333333334, 585.28, 145.33333333333334, 46.72] |
| branches.2.children.1.title | 1 | 6 | compactBody | [1098.6666666666667, 537.28, 117.33333333333334, 42] |
| branches.2.children.1.body | 1 | 18 | caption | [1070.6666666666667, 585.28, 145.33333333333334, 46.72] |

## 使用步骤

1. 先确认材料确有本页型所表达的关系，选择`family=hierarchy`及兼容variant。
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

来源为现有用户模板tokens及矩形语言的原创结构扩展，语义参考Microsoft SmartArt Hierarchy。原始文件指纹及资产处理见asset-provenance.json。当前原型完成结构生成与文本测量，实际渲染和原生编辑范围以交付检查记录为准。

catalog指纹为`498fe133ea2d00699bb4c4ea5bc798e78130623b21eea5d3cc8cb10e125af78b`，tokens指纹为`2bb967b3a61bf7a4072665f712f39ac49458d22ebe9407f269236c21adc366f3`，参数schema指纹为`6981096e740f47c827294403dd132d6609fd537f46b15e8164c4b630b9822a61`。
