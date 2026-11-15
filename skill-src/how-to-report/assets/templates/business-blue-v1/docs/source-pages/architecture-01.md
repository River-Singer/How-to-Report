# 平台能力全景

来源为蓝色逻辑架构图.pptx#1。

## 结构与适用场景

触点11列、应用8椭圆、业务/数据双中台、云平台底座4层；左层标签；立体底板

平台全景架构

与house29同语义近重复；每层模块结构不同，层内列表分别绑定

固定节点、圆弧、扇区、分面和连接表达定性关系。数量比较、趋势或占比使用数据驱动图表，源页中已登记的微图槽可接收实际数据。

## 预览

![结构预览](../../templates/prototypes/source-architecture-01.svg)

## 调用

将下列完整page对象放入schema_version=1、template_id=business-blue-v1的pages数组，替换各节点内容。nodes键对应原文本框或已明确拆分的语义分段，字段角色及source_ref、segment见下表。

```json
{
  "id": "architecture-01",
  "family": "source-architecture",
  "variant": "page-01",
  "content": {
    "title": "平台能力全景",
    "nodes": {
      "shape_11": "模块",
      "shape_13": "说明",
      "shape_53": "模块",
      "shape_54": "说明",
      "shape_55": "模块",
      "shape_56": "说明",
      "shape_57": "模块",
      "shape_58": "说明",
      "shape_59": "模块",
      "shape_60": "说明",
      "shape_450": "模块",
      "shape_451": "说明",
      "shape_477": "模块",
      "shape_479": "模块",
      "shape_481": "模块",
      "shape_483": "模块",
      "shape_485": "模块",
      "shape_487": "模块",
      "shape_489": "模块",
      "shape_491": "模块",
      "shape_493": "模块",
      "shape_512": "模块",
      "shape_515": "模块",
      "shape_516": "模块",
      "shape_517": "模块",
      "shape_518": "模块",
      "shape_525": "模块",
      "shape_531": "模块",
      "shape_533": "模块",
      "shape_535": "模块",
      "shape_537": "模块",
      "shape_539": "模块",
      "shape_540": "模块",
      "shape_542": "模块",
      "shape_550": "模块",
      "shape_552": "模块",
      "shape_554": "模块",
      "shape_556": "模块",
      "shape_560": "模块",
      "shape_561": "说明",
      "shape_565": "模块",
      "shape_566": "说明",
      "shape_568": "模块",
      "shape_569": "说明",
      "shape_571": "模块",
      "shape_572": "说明",
      "shape_574": "模块",
      "shape_575": "说明",
      "shape_577": "模块",
      "shape_578": "说明",
      "shape_580": "模块",
      "shape_581": "说明",
      "shape_583": "模块",
      "shape_584": "说明",
      "shape_585": "模块",
      "shape_586": "模块",
      "shape_587": "模块",
      "shape_588": "模块",
      "shape_589": "模块",
      "shape_590": "模块",
      "shape_591": "模块",
      "shape_592": "模块",
      "shape_593": "模块",
      "shape_594": "模块"
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
| nodes.shape_11 | 下左节点，源标签“云平台” | 1/16 | caption | [218.4764, 561.1924, 121.5707, 26.0069] | slide:11 |  | 0.0 | t |
| nodes.shape_13 | 下左节点，源标签“Enter your title” | 1/20 | diagramMicro | [218.4764, 582.386, 108.9023, 21.2783] | slide:13 |  | 0.0 | t |
| nodes.shape_53 | 中左节点，源标签“双中台” | 1/16 | caption | [218.4764, 392.583, 121.5707, 26.0069] | slide:53 |  | 0.0 | t |
| nodes.shape_54 | 中左节点，源标签“Enter your title” | 1/20 | diagramMicro | [218.4764, 413.7843, 108.9023, 21.2783] | slide:54 |  | 0.0 | t |
| nodes.shape_55 | 中左节点，源标签“应用层” | 1/16 | caption | [218.4764, 290.8736, 121.5707, 26.0069] | slide:55 |  | 0.0 | t |
| nodes.shape_56 | 中左节点，源标签“Enter your title” | 1/20 | diagramMicro | [218.4764, 312.0672, 108.9023, 21.2783] | slide:56 |  | 0.0 | t |
| nodes.shape_57 | 上左节点，源标签“触点” | 1/16 | caption | [218.4764, 222.6027, 121.5707, 26.0069] | slide:57 |  | 0.0 | t |
| nodes.shape_58 | 上左节点，源标签“Enter your title” | 1/20 | diagramMicro | [218.4764, 243.804, 108.9023, 21.2783] | slide:58 |  | 0.0 | t |
| nodes.shape_59 | 中左节点，源标签“业务中台” | 1/16 | caption | [359.6774, 392.583, 121.5707, 26.0069] | slide:59 |  | 0.0 | t |
| nodes.shape_60 | 中中节点，源标签“Enter your title” | 1/20 | diagramMicro | [431.6525, 396.9572, 108.9023, 21.2783] | slide:60 |  | 0.0 | t |
| nodes.shape_450 | 中中节点，源标签“数据中台” | 1/16 | caption | [737.6046, 392.583, 121.5707, 26.0069] | slide:450 |  | 0.0 | t |
| nodes.shape_451 | 中中节点，源标签“Enter your title” | 1/20 | diagramMicro | [809.5798, 396.9572, 108.9023, 21.2783] | slide:451 |  | 0.0 | t |
| nodes.shape_477 | 中左节点，源标签“用户中心” | 1/14 | diagramMicro | [372.9465, 429.8643, 76.6267, 21.2783] | slide:477 |  | 0.0 | t |
| nodes.shape_479 | 中中节点，源标签“商品中心” | 1/14 | diagramMicro | [487.7709, 429.8643, 76.6267, 21.2783] | slide:479 |  | 0.0 | t |
| nodes.shape_481 | 中中节点，源标签“交易中心” | 1/14 | diagramMicro | [602.6031, 429.8643, 76.6267, 21.2783] | slide:481 |  | 0.0 | t |
| nodes.shape_483 | 中左节点，源标签“计划中心” | 1/14 | diagramMicro | [372.9465, 467.7695, 76.6267, 21.2783] | slide:483 |  | 0.0 | t |
| nodes.shape_485 | 中中节点，源标签“渠道中心” | 1/14 | diagramMicro | [487.7709, 467.7695, 76.6267, 21.2783] | slide:485 |  | 0.0 | t |
| nodes.shape_487 | 中中节点，源标签“库存中心” | 1/14 | diagramMicro | [602.6031, 467.7695, 76.6267, 21.2783] | slide:487 |  | 0.0 | t |
| nodes.shape_489 | 下左节点，源标签“数据中心” | 1/14 | diagramMicro | [372.9465, 505.6747, 76.6267, 21.2783] | slide:489 |  | 0.0 | t |
| nodes.shape_491 | 下中节点，源标签“物流中心” | 1/14 | diagramMicro | [487.7709, 505.6747, 76.6267, 21.2783] | slide:491 |  | 0.0 | t |
| nodes.shape_493 | 下中节点，源标签“生产中心” | 1/14 | diagramMicro | [602.6031, 505.6747, 76.6267, 21.2783] | slide:493 |  | 0.0 | t |
| nodes.shape_512 | 中中节点，源标签“数据运营体系” | 1/20 | diagramMicro | [756.9731, 439.3753, 26.184, 85.1056] | slide:512 |  | 0.0 | t |
| nodes.shape_515 | 中中节点，源标签“数据资产管理” | 1/14 | diagramMicro | [804.5278, 435.7172, 78.1284, 20.0924] | slide:515 |  | 0.0 | t |
| nodes.shape_516 | 中中节点，源标签“数据资产体系” | 1/14 | diagramMicro | [804.5278, 470.8346, 78.1284, 20.0924] | slide:516 |  | 0.0 | t |
| nodes.shape_517 | 下中节点，源标签“数据汇集” | 1/14 | diagramMicro | [831.5974, 505.9519, 78.1284, 20.0924] | slide:517 |  | 0.0 | t |
| nodes.shape_518 | 下右节点，源标签“数据开发” | 1/14 | diagramMicro | [977.9197, 505.9519, 78.1284, 20.0924] | slide:518 |  | 0.0 | t |
| nodes.shape_525 | 中右节点，源标签“元数据管理” | 1/11 | diagramMicro | [886.2218, 436.0792, 63.011, 17.7281] | slide:525 |  | 0.0 | t |
| nodes.shape_531 | 中右节点，源标签“数据血缘” | 1/11 | diagramMicro | [952.9217, 436.0792, 60.5697, 17.7281] | slide:531 |  | 0.0 | t |
| nodes.shape_533 | 中右节点，源标签“数据质量” | 1/11 | diagramMicro | [1018.397, 436.0792, 60.5697, 17.7281] | slide:533 |  | 0.0 | t |
| nodes.shape_535 | 中右节点，源标签“主题域” | 1/10 | diagramMicro | [889.8799, 471.1965, 55.6949, 17.7281] | slide:535 |  | 0.0 | t |
| nodes.shape_537 | 中右节点，源标签“ODS” | 1/10 | diagramMicro | [955.363, 471.1965, 55.6949, 17.7281] | slide:537 |  | 0.0 | t |
| nodes.shape_539 | 中右节点，源标签“ODW” | 1/10 | diagramMicro | [1020.8383, 471.1965, 55.6949, 17.7281] | slide:539 |  | 0.0 | t |
| nodes.shape_540 | 下中节点，源标签“私有云/共有云平台” | 1/23 | caption | [419.2151, 570.6417, 165.7754, 26.0069] | slide:540 |  | 0.0 | t |
| nodes.shape_542 | 下中节点，源标签“监控服务体系” | 1/14 | diagramMicro | [581.3864, 574.9852, 78.1284, 20.0924] | slide:542 |  | 0.0 | t |
| nodes.shape_550 | 下中节点，源标签“日志服务体系” | 1/14 | diagramMicro | [680.3926, 574.9852, 78.1284, 19.4994] | slide:550 |  | 0.0 | t |
| nodes.shape_552 | 下中节点，源标签“元数据库” | 1/14 | diagramMicro | [779.4066, 574.9852, 78.1284, 20.0924] | slide:552 |  | 0.0 | t |
| nodes.shape_554 | 下右节点，源标签“平台负载均衡” | 1/14 | diagramMicro | [878.4206, 574.9852, 78.1284, 20.0924] | slide:554 |  | 0.0 | t |
| nodes.shape_556 | 下右节点，源标签“中间件” | 1/14 | diagramMicro | [965.1665, 574.9852, 78.1284, 20.0924] | slide:556 |  | 0.0 | t |
| nodes.shape_560 | 中左节点，源标签“营销管理系统” | 1/20 | diagramMicro | [374.0015, 286.3838, 109.3181, 21.2783] | slide:560 |  | 0.0 | t |
| nodes.shape_561 | 中左节点，源标签“Enter your title” | 1/20 | diagramMicro | [374.0015, 299.8147, 108.9023, 21.2783] | slide:561 |  | 0.0 | t |
| nodes.shape_565 | 中左节点，源标签“ERP管理” | 1/19 | diagramMicro | [374.0015, 335.9177, 106.8538, 21.2783] | slide:565 |  | 0.0 | t |
| nodes.shape_566 | 中左节点，源标签“Enter your title” | 1/20 | diagramMicro | [374.0015, 349.3486, 108.9023, 21.2783] | slide:566 |  | 0.0 | t |
| nodes.shape_568 | 中中节点，源标签“微信小商城” | 1/19 | diagramMicro | [562.5262, 286.3838, 106.8538, 21.2783] | slide:568 |  | 0.0 | t |
| nodes.shape_569 | 中中节点，源标签“Enter your title” | 1/20 | diagramMicro | [562.5262, 299.8147, 108.9023, 21.2783] | slide:569 |  | 0.0 | t |
| nodes.shape_571 | 中中节点，源标签“CRM客户管理系统” | 1/23 | diagramMicro | [562.5262, 335.9177, 125.9527, 21.2783] | slide:571 |  | 0.0 | t |
| nodes.shape_572 | 中中节点，源标签“Enter your title” | 1/20 | diagramMicro | [562.5262, 349.3486, 108.9023, 21.2783] | slide:572 |  | 0.0 | t |
| nodes.shape_574 | 中中节点，源标签“OMS管理系统” | 1/19 | diagramMicro | [751.0509, 286.3838, 106.8538, 21.2783] | slide:574 |  | 0.0 | t |
| nodes.shape_575 | 中中节点，源标签“Enter your title” | 1/20 | diagramMicro | [751.0509, 299.8147, 108.9023, 21.2783] | slide:575 |  | 0.0 | t |
| nodes.shape_577 | 中中节点，源标签“WMS仓储管理” | 1/19 | diagramMicro | [751.0509, 335.9177, 106.8538, 21.2783] | slide:577 |  | 0.0 | t |
| nodes.shape_578 | 中中节点，源标签“Enter your title” | 1/20 | diagramMicro | [751.0509, 349.3486, 108.9023, 21.2783] | slide:578 |  | 0.0 | t |
| nodes.shape_580 | 中右节点，源标签“互联网营销系统” | 1/19 | diagramMicro | [939.5756, 286.3838, 106.8538, 21.2783] | slide:580 |  | 0.0 | t |
| nodes.shape_581 | 中右节点，源标签“Enter your title” | 1/20 | diagramMicro | [939.5756, 299.8147, 108.9023, 21.2783] | slide:581 |  | 0.0 | t |
| nodes.shape_583 | 中右节点，源标签“MES生产制作系统” | 1/23 | diagramMicro | [939.5756, 335.9177, 126.5688, 21.2783] | slide:583 |  | 0.0 | t |
| nodes.shape_584 | 中右节点，源标签“Enter your title” | 1/20 | diagramMicro | [939.5756, 349.3486, 108.9023, 21.2783] | slide:584 |  | 0.0 | t |
| nodes.shape_585 | 上左节点，源标签“电商 / 平台” | 1/22 | diagramMicro | [351.1291, 227.2773, 62.7491, 35.4639] | slide:585 |  | 0.0 | t |
| nodes.shape_586 | 上中节点，源标签“微欣 / 公众浩” | 1/22 | diagramMicro | [426.6852, 227.2773, 62.7491, 35.4639] | slide:586 |  | 0.0 | t |
| nodes.shape_587 | 上中节点，源标签“小红书 / 微博等” | 1/22 | diagramMicro | [502.2491, 227.2773, 62.7491, 35.4639] | slide:587 |  | 0.0 | t |
| nodes.shape_588 | 上中节点，源标签“线下 / 门店” | 1/22 | diagramMicro | [577.813, 227.2773, 62.7491, 35.4639] | slide:588 |  | 0.0 | t |
| nodes.shape_589 | 上中节点，源标签“地推 / 广告” | 1/22 | diagramMicro | [653.3769, 227.2773, 62.7491, 35.4639] | slide:589 |  | 0.0 | t |
| nodes.shape_590 | 上中节点，源标签“会展 / 展览” | 1/22 | diagramMicro | [728.9331, 227.2773, 62.7491, 35.4639] | slide:590 |  | 0.0 | t |
| nodes.shape_591 | 上中节点，源标签“异业 / 合作” | 1/22 | diagramMicro | [804.497, 227.2773, 62.7491, 35.4639] | slide:591 |  | 0.0 | t |
| nodes.shape_592 | 上右节点，源标签“官方 / 网站” | 1/22 | diagramMicro | [880.0609, 227.2773, 62.7491, 35.4639] | slide:592 |  | 0.0 | t |
| nodes.shape_593 | 上右节点，源标签“电视 / 广告” | 1/22 | diagramMicro | [955.6171, 227.2773, 62.7491, 35.4639] | slide:593 |  | 0.0 | t |
| nodes.shape_594 | 上右节点，源标签“垂直 / 媒体” | 1/22 | diagramMicro | [1031.181, 227.2773, 62.7491, 35.4639] | slide:594 |  | 0.0 | t |

## 保留的原装饰

本页保留用户原模板的结构图标或装饰图片，逐项身份见source-field-coverage.json中本页retained_source_images。其中图片内固化的字形随整图编辑，可在PowerPoint中原生替换整图；nodes字段控制已登记的可编辑文字。参数图片替换使用本页image_slots列出的槽位。


全局title必填、2至32码点，使用统一标题框。section_name可选0至24码点，source可选0至64码点。所有可编辑文本通过独立原生carrier导出，页码为派生文字。

## 来源处理

原生PPTX源件保存于用户材料目录，分发包仅含用户资产衍生的几何、字段和说明。原始逐框文字、源框与标准化框在page-catalog.json的variant.fields中。

源标题引用为`slide:126`，原文为“平台架构图”。模板默认标题依据真实结构设置。

密集全景中的diagramCompact为14px、diagramMicro为12px。适用于体系概览或附录局部标签，现场关键结论用统一标题与正常正文字阶表达。

源画布边界裁切已烘焙为可编辑Bezier几何，3D顶面、侧面与前面通过tokens配色的相对明暗保留。

