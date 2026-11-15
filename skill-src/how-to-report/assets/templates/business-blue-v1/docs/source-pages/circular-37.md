# 产品与服务组合

来源为圆形逻辑图PPT模版.pptx#37。

## 结构与适用场景

底部中心半圆，6产品图标沿上半圆等距；虚线外弧

产品服务组合

6并列产品，半圆裁切；节点数变化应重新排弧

固定节点、圆弧、扇区、分面和连接表达定性关系。数量比较、趋势或占比使用数据驱动图表，源页中已登记的微图槽可接收实际数据。

## 预览

![结构预览](../../templates/prototypes/source-circular-37.svg)

## 调用

将下列完整page对象放入schema_version=1、template_id=business-blue-v1的pages数组，替换各节点内容。nodes键对应原文本框或已明确拆分的语义分段，字段角色及source_ref、segment见下表。

```json
{
  "id": "circular-37",
  "family": "source-circular",
  "variant": "page-37",
  "content": {
    "title": "产品与服务组合",
    "nodes": {
      "shape_12": "节点",
      "shape_13": "节点",
      "shape_14": "节点",
      "shape_15": "节点",
      "shape_16": "节点",
      "shape_18": "节点",
      "shape_68": "节点"
    }
  },
  "config": {
    "show_source": true,
    "show_page_number": true
  }
}
```

config支持show_source、show_page_number、image_fit与image_position。image_fit可选contain或cover，image_position为xMin/xMid/xMax与YMin/YMid/YMax组合的九个焦点，默认为xMidYMid。字体、颜色、全局区和固定字阶取自tokens，节点数与连接结构由variant确定。

## 字段合同

每个业务节点required=true、min=1，max按具体框体登记。字符按规范化后的Unicode码点计数，空格标点换行均计入。build会以实际字体测量宽高，字符数通过后仍可能需要调整文字。

| 字段 | 节点角色与源标签 | 最短/最长 | 字阶 | 框体px | 原框引用 | 分段 | 旋转° | 垂直锚点 |
|---|---|---|---|---|---|---|---|---|
| nodes.shape_12 | 中左节点，源标签“元宇宙教育平台” | 1/17 | compactBody | [163.1521, 445.9798, 161.9915, 33.233] | slide:12 |  | 0.0 | t |
| nodes.shape_13 | 中左节点，源标签“VR教育产品展示系统” | 1/23 | compactBody | [239.7216, 290.6211, 211.6011, 33.233] | slide:13 |  | 0.0 | t |
| nodes.shape_14 | 上中节点，源标签“XR教育实训解决方案” | 1/23 | compactBody | [643.205, 207.8729, 209.7243, 33.233] | slide:14 |  | 0.0 | t |
| nodes.shape_15 | 中右节点，源标签“虚拟仿真系统” | 1/15 | compactBody | [883.1972, 294.2461, 141.2188, 33.233] | slide:15 |  | 0.0 | t |
| nodes.shape_16 | 上中节点，源标签“沉浸式系统” | 1/13 | compactBody | [466.4652, 210.5809, 120.4546, 33.233] | slide:16 |  | 0.0 | t |
| nodes.shape_18 | 下中节点，源标签“产品及服务” | 1/31 | heading | [444.6212, 555.7823, 395.0595, 63.5866] | slide:18 |  | 0.0 | t |
| nodes.shape_68 | 中右节点，源标签“旅游实训平台” | 1/15 | compactBody | [975.6292, 445.7998, 141.2188, 33.233] | slide:68 |  | 0.0 | t |

全局title必填、2至32码点，使用统一标题框。section_name可选0至24码点，source可选0至64码点。所有可编辑文本通过独立原生carrier导出，页码为派生文字。

## 来源处理

原生PPTX源件保存于用户材料目录，分发包仅含用户资产衍生的几何、字段和说明。原始逐框文字、源框与标准化框在page-catalog.json的variant.fields中。

源标题引用为`slide:42`，原文为“系统解决方案”。模板默认标题依据真实结构设置。

密集全景中的diagramCompact为14px、diagramMicro为12px。适用于体系概览或附录局部标签，现场关键结论用统一标题与正常正文字阶表达。

源画布边界裁切已烘焙为可编辑Bezier几何，3D顶面、侧面与前面通过tokens配色的相对明暗保留。

