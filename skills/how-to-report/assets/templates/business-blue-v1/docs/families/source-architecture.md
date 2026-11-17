# 蓝色逻辑架构图.pptx

模块接口与分层架构

类型为定性关系图，语义入口为`source-architecture`。

## 使用场景

按原文件名索引、逐页预览和结构说明选择关系图。

关系要求为节点归属、层次、支撑或方向以原图几何表达，逐variant说明。。缺少必要输入时说明具体字段与来源缺口，再选择资料能支持的表达。

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
    "nodes": {
      "type": "object",
      "additionalProperties": {
        "type": "string"
      }
    },
    "visuals": {
      "type": "object"
    },
    "charts": {
      "type": "object"
    }
  },
  "required": [
    "title",
    "nodes"
  ],
  "additionalProperties": false
}
```

## 变体与容量

固定分面、扇区、圆环和立体几何用于定性关系。实际数量比较或占比应选择由数据计算几何的chart家族。

diagramCompact为14px、diagramMicro为12px，限密集体系总览或附录的局部标签。关键判断使用全局标题和正常正文字阶。源图的所有文本框各有独立字段，实际输入同时接受长度和字体框体测量。

### page-01

触点11列、应用8椭圆、业务/数据双中台、云平台底座4层；左层标签；立体底板

Layout为`source-architecture-01`，原型为`templates/prototypes/source-architecture-01.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_11 | 1 | 16 | caption | [218.4764, 561.1924, 121.5707, 26.0069] |
| nodes.shape_13 | 1 | 20 | diagramMicro | [218.4764, 582.386, 108.9023, 21.2783] |
| nodes.shape_53 | 1 | 16 | caption | [218.4764, 392.583, 121.5707, 26.0069] |
| nodes.shape_54 | 1 | 20 | diagramMicro | [218.4764, 413.7843, 108.9023, 21.2783] |
| nodes.shape_55 | 1 | 16 | caption | [218.4764, 290.8736, 121.5707, 26.0069] |
| nodes.shape_56 | 1 | 20 | diagramMicro | [218.4764, 312.0672, 108.9023, 21.2783] |
| nodes.shape_57 | 1 | 16 | caption | [218.4764, 222.6027, 121.5707, 26.0069] |
| nodes.shape_58 | 1 | 20 | diagramMicro | [218.4764, 243.804, 108.9023, 21.2783] |
| nodes.shape_59 | 1 | 16 | caption | [359.6774, 392.583, 121.5707, 26.0069] |
| nodes.shape_60 | 1 | 20 | diagramMicro | [431.6525, 396.9572, 108.9023, 21.2783] |
| nodes.shape_450 | 1 | 16 | caption | [737.6046, 392.583, 121.5707, 26.0069] |
| nodes.shape_451 | 1 | 20 | diagramMicro | [809.5798, 396.9572, 108.9023, 21.2783] |
| nodes.shape_477 | 1 | 14 | diagramMicro | [372.9465, 429.8643, 76.6267, 21.2783] |
| nodes.shape_479 | 1 | 14 | diagramMicro | [487.7709, 429.8643, 76.6267, 21.2783] |
| nodes.shape_481 | 1 | 14 | diagramMicro | [602.6031, 429.8643, 76.6267, 21.2783] |
| nodes.shape_483 | 1 | 14 | diagramMicro | [372.9465, 467.7695, 76.6267, 21.2783] |
| nodes.shape_485 | 1 | 14 | diagramMicro | [487.7709, 467.7695, 76.6267, 21.2783] |
| nodes.shape_487 | 1 | 14 | diagramMicro | [602.6031, 467.7695, 76.6267, 21.2783] |
| nodes.shape_489 | 1 | 14 | diagramMicro | [372.9465, 505.6747, 76.6267, 21.2783] |
| nodes.shape_491 | 1 | 14 | diagramMicro | [487.7709, 505.6747, 76.6267, 21.2783] |
| nodes.shape_493 | 1 | 14 | diagramMicro | [602.6031, 505.6747, 76.6267, 21.2783] |
| nodes.shape_512 | 1 | 20 | diagramMicro | [756.9731, 439.3753, 26.184, 85.1056] |
| nodes.shape_515 | 1 | 14 | diagramMicro | [804.5278, 435.7172, 78.1284, 20.0924] |
| nodes.shape_516 | 1 | 14 | diagramMicro | [804.5278, 470.8346, 78.1284, 20.0924] |
| nodes.shape_517 | 1 | 14 | diagramMicro | [831.5974, 505.9519, 78.1284, 20.0924] |
| nodes.shape_518 | 1 | 14 | diagramMicro | [977.9197, 505.9519, 78.1284, 20.0924] |
| nodes.shape_525 | 1 | 11 | diagramMicro | [886.2218, 436.0792, 63.011, 17.7281] |
| nodes.shape_531 | 1 | 11 | diagramMicro | [952.9217, 436.0792, 60.5697, 17.7281] |
| nodes.shape_533 | 1 | 11 | diagramMicro | [1018.397, 436.0792, 60.5697, 17.7281] |
| nodes.shape_535 | 1 | 10 | diagramMicro | [889.8799, 471.1965, 55.6949, 17.7281] |
| nodes.shape_537 | 1 | 10 | diagramMicro | [955.363, 471.1965, 55.6949, 17.7281] |
| nodes.shape_539 | 1 | 10 | diagramMicro | [1020.8383, 471.1965, 55.6949, 17.7281] |
| nodes.shape_540 | 1 | 23 | caption | [419.2151, 570.6417, 165.7754, 26.0069] |
| nodes.shape_542 | 1 | 14 | diagramMicro | [581.3864, 574.9852, 78.1284, 20.0924] |
| nodes.shape_550 | 1 | 14 | diagramMicro | [680.3926, 574.9852, 78.1284, 19.4994] |
| nodes.shape_552 | 1 | 14 | diagramMicro | [779.4066, 574.9852, 78.1284, 20.0924] |
| nodes.shape_554 | 1 | 14 | diagramMicro | [878.4206, 574.9852, 78.1284, 20.0924] |
| nodes.shape_556 | 1 | 14 | diagramMicro | [965.1665, 574.9852, 78.1284, 20.0924] |
| nodes.shape_560 | 1 | 20 | diagramMicro | [374.0015, 286.3838, 109.3181, 21.2783] |
| nodes.shape_561 | 1 | 20 | diagramMicro | [374.0015, 299.8147, 108.9023, 21.2783] |
| nodes.shape_565 | 1 | 19 | diagramMicro | [374.0015, 335.9177, 106.8538, 21.2783] |
| nodes.shape_566 | 1 | 20 | diagramMicro | [374.0015, 349.3486, 108.9023, 21.2783] |
| nodes.shape_568 | 1 | 19 | diagramMicro | [562.5262, 286.3838, 106.8538, 21.2783] |
| nodes.shape_569 | 1 | 20 | diagramMicro | [562.5262, 299.8147, 108.9023, 21.2783] |
| nodes.shape_571 | 1 | 23 | diagramMicro | [562.5262, 335.9177, 125.9527, 21.2783] |
| nodes.shape_572 | 1 | 20 | diagramMicro | [562.5262, 349.3486, 108.9023, 21.2783] |
| nodes.shape_574 | 1 | 19 | diagramMicro | [751.0509, 286.3838, 106.8538, 21.2783] |
| nodes.shape_575 | 1 | 20 | diagramMicro | [751.0509, 299.8147, 108.9023, 21.2783] |
| nodes.shape_577 | 1 | 19 | diagramMicro | [751.0509, 335.9177, 106.8538, 21.2783] |
| nodes.shape_578 | 1 | 20 | diagramMicro | [751.0509, 349.3486, 108.9023, 21.2783] |
| nodes.shape_580 | 1 | 19 | diagramMicro | [939.5756, 286.3838, 106.8538, 21.2783] |
| nodes.shape_581 | 1 | 20 | diagramMicro | [939.5756, 299.8147, 108.9023, 21.2783] |
| nodes.shape_583 | 1 | 23 | diagramMicro | [939.5756, 335.9177, 126.5688, 21.2783] |
| nodes.shape_584 | 1 | 20 | diagramMicro | [939.5756, 349.3486, 108.9023, 21.2783] |
| nodes.shape_585 | 1 | 22 | diagramMicro | [351.1291, 227.2773, 62.7491, 35.4639] |
| nodes.shape_586 | 1 | 22 | diagramMicro | [426.6852, 227.2773, 62.7491, 35.4639] |
| nodes.shape_587 | 1 | 22 | diagramMicro | [502.2491, 227.2773, 62.7491, 35.4639] |
| nodes.shape_588 | 1 | 22 | diagramMicro | [577.813, 227.2773, 62.7491, 35.4639] |
| nodes.shape_589 | 1 | 22 | diagramMicro | [653.3769, 227.2773, 62.7491, 35.4639] |
| nodes.shape_590 | 1 | 22 | diagramMicro | [728.9331, 227.2773, 62.7491, 35.4639] |
| nodes.shape_591 | 1 | 22 | diagramMicro | [804.497, 227.2773, 62.7491, 35.4639] |
| nodes.shape_592 | 1 | 22 | diagramMicro | [880.0609, 227.2773, 62.7491, 35.4639] |
| nodes.shape_593 | 1 | 22 | diagramMicro | [955.6171, 227.2773, 62.7491, 35.4639] |
| nodes.shape_594 | 1 | 22 | diagramMicro | [1031.181, 227.2773, 62.7491, 35.4639] |
### page-02

STEP01–05竖向步骤；用户目标、原则、模式、技术、资产；模式层左组件分级、右3平台；技术4端

Layout为`source-architecture-02`，原型为`templates/prototypes/source-architecture-02.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_78 | 1 | 9 | diagramCompact | [69.4877, 145.3341, 57.5241, 17.5] |
| nodes.shape_79 | 1 | 9 | diagramCompact | [68.6203, 220.3705, 59.2589, 17.5] |
| nodes.shape_80 | 1 | 9 | diagramCompact | [68.5274, 361.4808, 59.4344, 17.5] |
| nodes.shape_81 | 1 | 9 | diagramCompact | [68.4448, 521.5282, 59.6099, 17.5] |
| nodes.shape_82 | 1 | 9 | diagramCompact | [68.4448, 609.6472, 59.6099, 17.5] |
| nodes.shape_83 | 1 | 9 | caption | [183.9681, 144.0682, 66.7243, 20.0214] |
| nodes.shape_84 | 1 | 18 | caption | [183.9681, 205.9601, 66.7243, 46.3002] |
| nodes.shape_85 | 1 | 9 | caption | [183.9681, 360.2252, 66.7243, 20.0214] |
| nodes.shape_86 | 1 | 9 | caption | [183.9681, 520.2727, 66.7243, 20.0214] |
| nodes.shape_87 | 1 | 9 | caption | [183.9681, 608.3814, 66.7243, 20.0214] |
| nodes.shape_88 | 1 | 29 | caption | [651.5234, 144.0682, 215.1347, 20.0214] |
| nodes.shape_92 | 1 | 30 | diagramMicro | [307.2872, 301.6244, 165.4374, 15.0] |
| nodes.shape_93 | 1 | 23 | diagramMicro | [507.7595, 301.6244, 126.5098, 15.0] |
| nodes.shape_94 | 1 | 30 | diagramMicro | [307.2872, 342.927, 165.4374, 15.0] |
| nodes.shape_95 | 1 | 27 | diagramMicro | [488.306, 342.927, 145.9736, 15.0] |
| nodes.shape_96 | 1 | 32 | diagramMicro | [307.2872, 383.5481, 175.1642, 15.0] |
| nodes.shape_97 | 1 | 27 | diagramMicro | [488.306, 383.5481, 145.9736, 15.0] |
| nodes.shape_98 | 1 | 36 | diagramMicro | [307.2872, 424.8506, 194.628, 15.0] |
| nodes.shape_99 | 1 | 19 | diagramMicro | [529.3091, 424.8506, 104.9601, 15.0] |
| nodes.shape_100 | 1 | 8 | caption | [696.2954, 349.0116, 30.5845, 42.4384] |
| nodes.shape_101 | 1 | 14 | diagramCompact | [793.3771, 290.9257, 88.2739, 17.5] |
| nodes.shape_102 | 1 | 18 | diagramCompact | [941.1164, 290.9257, 115.7298, 17.5] |
| nodes.shape_103 | 1 | 11 | diagramCompact | [1124.2829, 290.9257, 69.5122, 17.5] |
| nodes.shape_104 | 1 | 7 | diagramMicro | [786.4383, 327.8027, 38.9277, 24.9571] |
| nodes.shape_105 | 1 | 5 | diagramMicro | [853.9473, 327.8027, 29.1906, 24.9571] |
| nodes.shape_106 | 1 | 3 | diagramMicro | [796.165, 369.1053, 19.4638, 24.9571] |
| nodes.shape_107 | 1 | 7 | diagramMicro | [849.0736, 369.1053, 38.9277, 24.9571] |
| nodes.shape_108 | 1 | 2 | diagramMicro | [831.6439, 409.0111, 14.6005, 15.0] |
| nodes.shape_109 | 1 | 9 | diagramMicro | [974.6644, 326.0652, 48.6544, 15.0] |
| nodes.shape_110 | 1 | 9 | diagramMicro | [974.6644, 353.9444, 48.6544, 15.0] |
| nodes.shape_111 | 1 | 9 | diagramMicro | [972.9193, 381.1525, 52.1342, 15.0] |
| nodes.shape_112 | 1 | 2 | diagramMicro | [991.6914, 409.3622, 14.6005, 15.0] |
| nodes.shape_113 | 1 | 3 | diagramMicro | [1117.9843, 327.8027, 19.4638, 24.9571] |
| nodes.shape_114 | 1 | 3 | diagramMicro | [1180.6299, 327.8027, 19.4638, 24.9571] |
| nodes.shape_115 | 1 | 5 | diagramMicro | [1113.1209, 374.4349, 29.1906, 15.0] |
| nodes.shape_116 | 1 | 3 | diagramMicro | [1180.6299, 374.4349, 19.4638, 15.0] |
| nodes.shape_117 | 1 | 2 | diagramMicro | [1151.7388, 409.7029, 14.6005, 15.0] |
| nodes.shape_118 | 1 | 5 | diagramCompact | [391.3379, 483.8499, 34.0643, 17.5] |
| nodes.shape_119 | 1 | 6 | diagramCompact | [629.1065, 483.8499, 41.7053, 17.5] |
| nodes.shape_120 | 1 | 8 | diagramCompact | [856.4048, 483.8499, 55.6036, 17.5] |
| nodes.shape_121 | 1 | 4 | diagramCompact | [1111.3759, 483.8499, 29.5417, 17.5] |
| nodes.shape_122 | 1 | 5 | diagramMicro | [386.2061, 563.1213, 28.1477, 15.0] |
| nodes.shape_123 | 1 | 25 | diagramMicro | [570.3329, 563.1213, 136.5876, 15.0] |
| nodes.shape_124 | 1 | 15 | diagramMicro | [837.6018, 563.1213, 81.1492, 15.0] |
| nodes.shape_125 | 1 | 6 | diagramMicro | [1104.8707, 563.1213, 33.3621, 15.0] |
| nodes.shape_89 | 1 | 30 | diagramCompact | [661.7768, 205.45, 194.628, 17.5] |
| nodes.shape_90 | 1 | 61 | diagramCompact | [564.4576, 233.2156, 389.256, 17.5] |
| nodes.shape_131 | 1 | 7 | diagramMicro | [320.4008, 513.6511, 38.9277, 15.0] |
| nodes.shape_132 | 1 | 7 | diagramMicro | [320.4008, 541.8711, 38.9277, 15.0] |
| nodes.shape_133 | 1 | 7 | diagramMicro | [379.608, 513.6511, 38.9277, 15.0] |
| nodes.shape_134 | 1 | 7 | diagramMicro | [379.608, 541.8711, 38.9277, 15.0] |
| nodes.shape_135 | 1 | 2 | diagramMicro | [450.6278, 513.6511, 15.2923, 15.0] |
| nodes.shape_136 | 1 | 3 | diagramMicro | [448.542, 541.8711, 19.4638, 15.0] |
| nodes.shape_137 | 1 | 2 | diagramMicro | [591.738, 541.8711, 15.2923, 15.0] |
| nodes.shape_138 | 1 | 7 | diagramMicro | [579.9254, 513.6511, 38.9277, 15.0] |
| nodes.shape_139 | 1 | 7 | diagramMicro | [648.7562, 541.8711, 38.9277, 15.0] |
| nodes.shape_140 | 1 | 10 | diagramMicro | [639.0294, 513.6511, 58.3915, 15.0] |
| nodes.shape_141 | 1 | 2 | diagramMicro | [831.2928, 541.8711, 15.2923, 15.0] |
| nodes.shape_142 | 1 | 7 | diagramMicro | [819.4803, 513.6511, 38.9277, 15.0] |
| nodes.shape_143 | 1 | 7 | diagramMicro | [888.311, 513.6511, 38.9277, 15.0] |
| nodes.shape_144 | 1 | 10 | diagramMicro | [878.5843, 541.8711, 58.3915, 15.0] |
| nodes.shape_145 | 1 | 7 | diagramMicro | [1068.669, 528.107, 38.9277, 15.0] |
| nodes.shape_146 | 1 | 7 | diagramMicro | [1127.8659, 528.107, 38.9277, 15.0] |
| nodes.shape_147 | 1 | 26 | diagramMicro | [327.2983, 610.8802, 143.5367, 15.0135] |
| nodes.shape_148 | 1 | 30 | diagramMicro | [556.1661, 610.8802, 164.9108, 15.0135] |
| nodes.shape_149 | 1 | 30 | diagramMicro | [796.8465, 610.8802, 162.6495, 15.0135] |
| nodes.shape_150 | 1 | 34 | diagramMicro | [1023.897, 610.8802, 187.6789, 15.0135] |
### page-03

行业场景6列、应用服务图标行、平台4能力组、数据5模块；左4层标签

Layout为`source-architecture-03`，原型为`templates/prototypes/source-architecture-03.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_109 | 1 | 13 | diagramCompact | [1096.7916, 120, 86.552, 24.3855] |
| nodes.shape_110 | 1 | 12 | diagramCompact | [131.6546, 269.6241, 79.2505, 25.9137] |
| nodes.shape_111 | 1 | 11 | diagramCompact | [134.1922, 354.2893, 74.1753, 25.9137] |
| nodes.shape_112 | 1 | 11 | diagramCompact | [134.1922, 497.442, 74.1753, 25.9137] |
| nodes.shape_113 | 1 | 11 | diagramCompact | [134.1922, 614.4641, 74.1753, 25.9137] |
| nodes.shape_114 | 1 | 25 | diagramCompact | [265.5059, 614.832, 158.001, 25.9137] |
| nodes.shape_115 | 1 | 19 | diagramCompact | [468.5233, 614.832, 124.5028, 25.9137] |
| nodes.shape_116 | 1 | 19 | diagramCompact | [654.07, 614.832, 125.9272, 25.9137] |
| nodes.shape_117 | 1 | 25 | diagramCompact | [824.2967, 614.832, 158.001, 25.9137] |
| nodes.shape_118 | 1 | 20 | diagramCompact | [1024.5313, 614.832, 130.0591, 25.9137] |
| nodes.shape_119 | 1 | 21 | diagramCompact | [305.7774, 406.1922, 135.9267, 25.9137] |
| nodes.shape_120 | 1 | 11 | diagramCompact | [581.4135, 406.1922, 74.0149, 25.9137] |
| nodes.shape_121 | 1 | 16 | diagramCompact | [788.3553, 406.1922, 101.7964, 25.9137] |
| nodes.shape_122 | 1 | 9 | diagramCompact | [1029.6442, 406.1922, 60.2043, 25.9137] |
| nodes.shape_123 | 1 | 16 | diagramCompact | [322.3897, 461.51, 102.1172, 25.9137] |
| nodes.shape_124 | 1 | 11 | diagramCompact | [587.4038, 461.51, 74.1753, 25.9137] |
| nodes.shape_125 | 1 | 11 | diagramCompact | [802.0432, 461.51, 74.1753, 25.9137] |
| nodes.shape_126 | 1 | 15 | diagramCompact | [1011.7018, 461.51, 96.0798, 25.9137] |
| nodes.shape_127 | 1 | 10 | diagramCompact | [282.4484, 506.3284, 69.0906, 24.3855] |
| nodes.shape_128 | 1 | 10 | diagramCompact | [282.4484, 554.0522, 69.0906, 24.3855] |
| nodes.shape_129 | 1 | 10 | diagramCompact | [394.7443, 506.3284, 69.0906, 24.3855] |
| nodes.shape_130 | 1 | 10 | diagramCompact | [394.7443, 554.0522, 69.0906, 24.3855] |
| nodes.shape_131 | 1 | 10 | diagramCompact | [528.8503, 506.3284, 69.0906, 24.3855] |
| nodes.shape_132 | 1 | 14 | diagramCompact | [516.1529, 554.0522, 94.4949, 24.3855] |
| nodes.shape_133 | 1 | 10 | diagramCompact | [640.5236, 506.3284, 69.0906, 24.3855] |
| nodes.shape_134 | 1 | 14 | diagramCompact | [629.7317, 554.0522, 90.6838, 24.3855] |
| nodes.shape_135 | 1 | 14 | diagramCompact | [790.6853, 506.3284, 94.4949, 24.3855] |
| nodes.shape_136 | 1 | 14 | diagramCompact | [790.6853, 554.0522, 94.4949, 24.3855] |
| nodes.shape_137 | 1 | 15 | diagramCompact | [952.5257, 506.3284, 98.7777, 24.3855] |
| nodes.shape_138 | 1 | 10 | diagramCompact | [967.3645, 554.0522, 69.0906, 24.3855] |
| nodes.shape_139 | 1 | 10 | diagramCompact | [1078.085, 506.3284, 69.0906, 24.3855] |
| nodes.shape_140 | 1 | 14 | diagramCompact | [1065.3876, 554.0522, 94.4949, 24.3855] |
| nodes.shape_141 | 1 | 11 | diagramCompact | [308.0791, 355.8081, 74.1753, 25.9137] |
| nodes.shape_142 | 1 | 11 | diagramCompact | [506.0025, 355.8081, 74.1753, 25.9137] |
| nodes.shape_143 | 1 | 11 | diagramCompact | [702.7466, 355.8081, 74.1753, 25.9137] |
| nodes.shape_144 | 1 | 11 | diagramCompact | [898.406, 355.8081, 74.1753, 25.9137] |
| nodes.shape_145 | 1 | 11 | diagramCompact | [1091.6126, 355.8081, 74.1753, 25.9137] |
| nodes.shape_146 | 1 | 36 | diagramMicro | [280.1749, 280.482, 97.9193, 43.6675] |
| nodes.shape_147 | 1 | 36 | diagramMicro | [433.5818, 280.482, 102.1172, 43.6675] |
| nodes.shape_148 | 1 | 36 | diagramMicro | [592.0073, 280.482, 102.1172, 43.6675] |
| nodes.shape_149 | 1 | 36 | diagramMicro | [737.2259, 280.482, 102.1172, 43.6675] |
| nodes.shape_150 | 1 | 36 | diagramMicro | [893.8213, 280.482, 102.1172, 43.6675] |
| nodes.shape_151 | 1 | 36 | diagramMicro | [1061.1803, 280.482, 102.1172, 43.6675] |
| nodes.shape_152 | 1 | 7 | diagramCompact | [304.8246, 238.9276, 46.2334, 25.9137] |
| nodes.shape_153 | 1 | 7 | diagramCompact | [461.4954, 238.9276, 46.2334, 25.9137] |
| nodes.shape_154 | 1 | 7 | diagramCompact | [619.9492, 238.9276, 46.2334, 25.9137] |
| nodes.shape_155 | 1 | 7 | diagramCompact | [770.3751, 238.9276, 48.1389, 25.9137] |
| nodes.shape_156 | 1 | 11 | diagramCompact | [912.858, 238.9276, 74.1753, 25.9137] |
| nodes.shape_157 | 1 | 7 | diagramCompact | [1082.547, 238.9276, 46.2334, 25.9137] |
### page-04

左5类输入；教育/业务/众创3平台上下需求成果流；中心能力与成果转化；右近期/远期目标各3块

Layout为`source-architecture-04`，原型为`templates/prototypes/source-architecture-04.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_63 | 1 | 6 | caption | [97.1391, 251.2783, 47.1417, 20.0] |
| nodes.shape_85 | 1 | 6 | caption | [97.1391, 313.542, 47.1417, 20.0] |
| nodes.shape_86 | 1 | 6 | caption | [97.1391, 376.6834, 47.1417, 20.0] |
| nodes.shape_87 | 1 | 6 | caption | [97.1391, 438.9472, 47.1417, 20.0] |
| nodes.shape_88 | 1 | 6 | caption | [97.1391, 502.0987, 47.1417, 20.0] |
| nodes.shape_90 | 1 | 13 | caption | [247.0786, 171.3452, 97.8344, 20.0] |
| nodes.shape_95 | 1 | 13 | caption | [247.0786, 610.7122, 97.8344, 20.0] |
| nodes.shape_96 | 1 | 4 | compactBody | [428.8964, 239.4669, 44.4683, 25.0] |
| nodes.shape_97 | 1 | 4 | compactBody | [428.8964, 382.6675, 44.4683, 25.0] |
| nodes.shape_98 | 1 | 4 | compactBody | [428.8964, 524.0825, 44.4683, 25.0] |
| nodes.shape_65 | 1 | 32 | caption | [847.482, 232.0127, 115.6197, 40.2616] |
| nodes.shape_67 | 1 | 80 | caption | [831.916, 357.8113, 146.7516, 82.0062] |
| nodes.shape_69 | 1 | 36 | caption | [839.9159, 521.9649, 130.7418, 40.2616] |
| nodes.shape_108 | 1 | 20 | caption | [831.916, 155.3051, 146.7516, 20.0] |
| nodes.shape_66 | 1 | 22 | caption | [1088.6078, 232.0127, 80.9368, 40.2616] |
| nodes.shape_68 | 1 | 48 | caption | [1083.2712, 357.3775, 91.61, 82.0062] |
| nodes.shape_70 | 1 | 54 | caption | [1061.4809, 510.3938, 135.1906, 61.1339] |
| nodes.shape_109 | 1 | 20 | caption | [1055.7004, 155.3051, 146.7516, 20.0] |
| nodes.shape_89 | 1 | 6 | caption | [206.3227, 336.7699, 49.805, 20.0] |
| nodes.shape_99 | 1 | 6 | caption | [206.3227, 434.6043, 49.805, 20.0] |
| nodes.shape_64 | 1 | 10 | caption | [301.4635, 259.9944, 76.488, 20.0] |
| nodes.shape_83 | 1 | 10 | caption | [301.4635, 383.8561, 76.488, 20.0] |
| nodes.shape_84 | 1 | 10 | caption | [301.4635, 511.6622, 76.488, 20.0] |
| nodes.shape_100 | 1 | 6 | caption | [277.0604, 322.5154, 49.805, 20.0] |
| nodes.shape_105 | 1 | 6 | caption | [277.0604, 446.1451, 49.805, 20.0] |
| nodes.shape_106 | 1 | 6 | caption | [351.7729, 322.5154, 49.805, 20.0] |
| nodes.shape_107 | 1 | 6 | caption | [351.7729, 446.1451, 49.805, 20.0] |
| nodes.shape_101 | 1 | 11 | caption | [657.4726, 286.9346, 81.8246, 20.0] |
| nodes.shape_102 | 1 | 11 | caption | [507.7753, 486.1645, 81.8246, 20.0] |
| nodes.shape_103 | 1 | 11 | caption | [602.0486, 486.1645, 81.8246, 20.0] |
| nodes.shape_104 | 1 | 11 | caption | [700.7808, 486.1645, 81.8246, 20.0] |
| nodes.shape_110 | 1 | 60 | caption | [522.1811, 212.5426, 219.6886, 45.2855] |
| nodes.shape_111 | 1 | 130 | caption | [535.0737, 344.8077, 193.8933, 115.7912] |
| nodes.shape_112 | 1 | 30 | caption | [522.1811, 546.7009, 219.6886, 21.8105] |
### page-05

左市场监管贯穿5阶段；右上5类使用主体、中间交易/运维机构、底层5类生产单位；上下双向流

Layout为`source-architecture-05`，原型为`templates/prototypes/source-architecture-05.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_108 | 1 | 12 | caption | [416.0432, 175.3001, 93.4326, 20.0] |
| nodes.shape_109 | 1 | 10 | caption | [423.6859, 426.7002, 78.1377, 20.0] |
| nodes.shape_110 | 1 | 10 | caption | [423.6859, 577.0345, 78.1377, 20.0] |
| nodes.shape_111 | 1 | 12 | caption | [565.1038, 175.3001, 93.4326, 20.0] |
| nodes.shape_112 | 1 | 12 | caption | [565.1038, 426.7002, 93.4326, 20.0] |
| nodes.shape_113 | 1 | 10 | caption | [572.7464, 577.0345, 78.1377, 20.0] |
| nodes.shape_114 | 1 | 12 | caption | [713.7366, 175.3001, 93.4326, 20.0] |
| nodes.shape_115 | 1 | 19 | caption | [690.8086, 426.7002, 139.2981, 20.0] |
| nodes.shape_116 | 1 | 10 | caption | [721.3792, 577.0345, 78.1377, 20.0] |
| nodes.shape_117 | 1 | 12 | caption | [862.3788, 175.3001, 93.4326, 20.0] |
| nodes.shape_118 | 1 | 10 | caption | [870.0215, 426.7002, 78.1377, 20.0] |
| nodes.shape_119 | 1 | 10 | caption | [870.0215, 577.0345, 78.1377, 20.0] |
| nodes.shape_120 | 1 | 8 | caption | [1026.7247, 175.3001, 62.8524, 20.0] |
| nodes.shape_121 | 1 | 10 | caption | [1019.0821, 426.7002, 78.1377, 20.0] |
| nodes.shape_122 | 1 | 10 | caption | [1019.0821, 577.0345, 78.1377, 20.0] |
| nodes.shape_123 | 1 | 10 | caption | [1019.0821, 231.3559, 78.1377, 20.0] |
| nodes.shape_124 | 1 | 10 | caption | [1019.0821, 287.4116, 78.1377, 20.0] |
| nodes.shape_125 | 1 | 30 | caption | [423.2581, 225.7996, 78.9932, 79.9914] |
| nodes.shape_126 | 1 | 30 | caption | [572.7464, 225.7996, 78.1377, 79.9914] |
| nodes.shape_127 | 1 | 36 | caption | [713.7366, 225.7996, 93.4326, 79.9914] |
| nodes.shape_128 | 1 | 30 | caption | [870.0215, 225.7996, 78.1377, 79.9914] |
| nodes.shape_12 | 1 | 18 | heading | [126.5439, 273.3952, 44.3446, 212.065] |
| nodes.shape_152 | 1 | 32 | compactBody | [222.7332, 170.8941, 147.0263, 52.1679] |
| nodes.shape_153 | 1 | 32 | compactBody | [222.7332, 269.8685, 147.0263, 52.1679] |
| nodes.shape_154 | 1 | 32 | compactBody | [222.7332, 371.4761, 147.0263, 52.1679] |
| nodes.shape_155 | 1 | 32 | compactBody | [222.7332, 474.8042, 147.0263, 52.1679] |
| nodes.shape_156 | 1 | 32 | compactBody | [222.7332, 577.8091, 147.0263, 52.1679] |
### page-06

中央创新中心→主任→下属4大模块；左管理委员会与单位、右技术委员会与专家；虚线汇报/顾问连接

Layout为`source-architecture-06`，原型为`templates/prototypes/source-architecture-06.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_187 | 1 | 14 | compactBody | [1058.1503, 130.777, 129.8881, 25.0] |
| nodes.shape_188 | 1 | 10 | compactBody | [73.9173, 132.5347, 92.7698, 25.0] |
| nodes.shape_189 | 1 | 10 | compactBody | [73.9173, 199.3247, 92.7698, 25.0] |
| nodes.shape_190 | 1 | 10 | compactBody | [73.9173, 267.0508, 92.7698, 25.0] |
| nodes.shape_201 | 1 | 6 | compactBody | [92.4712, 340.445, 55.6619, 25.0] |
| nodes.shape_202 | 1 | 14 | compactBody | [1058.1503, 184.5773, 129.8881, 25.0] |
| nodes.shape_203 | 1 | 14 | compactBody | [1058.1503, 238.3879, 129.8881, 25.0] |
| nodes.shape_204 | 1 | 14 | compactBody | [1058.1503, 292.1985, 129.8881, 25.0] |
| nodes.shape_205 | 1 | 14 | compactBody | [1058.1503, 346.0091, 129.8881, 25.0] |
| nodes.shape_206 | 1 | 8 | compactBody | [951.9445, 173.3336, 22.4, 111.9789] |
| nodes.shape_207 | 1 | 8 | compactBody | [285.2555, 172.408, 22.4, 111.9789] |
| nodes.shape_185 | 1 | 14 | heading | [550.6623, 151.5435, 185.5499, 35.0] |
| nodes.shape_208 | 1 | 31 | caption | [529.7787, 182.1164, 227.2963, 20.0] |
| nodes.shape_191 | 1 | 6 | compactBody | [108.3221, 468.408, 22.4, 89.5873] |
| nodes.shape_192 | 1 | 6 | compactBody | [177.9099, 468.408, 22.4, 89.5873] |
| nodes.shape_193 | 1 | 2 | compactBody | [249.3384, 486.0363, 22.4, 44.7936] |
| nodes.shape_194 | 1 | 8 | compactBody | [369.0239, 474.9081, 22.4, 111.9789] |
| nodes.shape_195 | 1 | 8 | compactBody | [438.6012, 474.9081, 22.4, 111.9789] |
| nodes.shape_196 | 1 | 8 | compactBody | [508.1785, 474.9081, 22.4, 111.9789] |
| nodes.shape_197 | 1 | 8 | compactBody | [876.5015, 474.9081, 22.4, 111.9789] |
| nodes.shape_198 | 1 | 6 | compactBody | [955.3557, 474.9081, 22.4, 89.5873] |
| nodes.shape_199 | 1 | 10 | compactBody | [1086.7362, 462.2407, 22.4, 134.3809] |
| nodes.shape_200 | 1 | 10 | compactBody | [1165.6009, 462.2407, 22.4, 134.3809] |
| nodes.shape_209 | 1 | 21 | caption | [106.6051, 620.2612, 153.0805, 20.166] |
| nodes.shape_210 | 1 | 21 | caption | [493.482, 620.2612, 153.0805, 20.166] |
| nodes.shape_211 | 1 | 21 | caption | [848.8047, 620.2612, 153.0805, 20.166] |
| nodes.shape_212 | 1 | 21 | caption | [1063.1112, 620.2612, 153.0805, 20.166] |
| nodes.shape_213 | 1 | 126 | caption | [623.2869, 473.1609, 152.1549, 131.7081] |
| nodes.shape_186 | 1 | 15 | compactBody | [571.5667, 274.1542, 140.0906, 25.0] |
### page-07

3阶段时间轴与目标/视角/结构/内容/效果泳道；底部曲面感知带

Layout为`source-architecture-07`，原型为`templates/prototypes/source-architecture-07.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_239 | 1 | 9 | caption | [164.2733, 157.6467, 69.0501, 20.7121] |
| nodes.shape_240 | 1 | 9 | caption | [164.2733, 212.8788, 69.0501, 20.7121] |
| nodes.shape_241 | 1 | 9 | caption | [164.2733, 258.2481, 69.0501, 20.7121] |
| nodes.shape_242 | 1 | 11 | caption | [155.6433, 319.6545, 86.3102, 20.7121] |
| nodes.shape_243 | 1 | 8 | diagramMicro | [174.8957, 341.615, 47.8054, 15.0] |
| nodes.shape_246 | 1 | 11 | caption | [155.6433, 414.9991, 86.3102, 20.7121] |
| nodes.shape_247 | 1 | 8 | diagramMicro | [174.8957, 436.9595, 47.8054, 15.0] |
| nodes.shape_249 | 1 | 11 | caption | [155.6433, 514.2888, 86.3102, 20.7121] |
| nodes.shape_250 | 1 | 8 | diagramMicro | [174.8957, 536.2493, 47.8054, 15.0] |
| nodes.shape_251 | 1 | 9 | caption | [164.2733, 594.2473, 69.0501, 20.7121] |
| nodes.shape_252 | 1 | 31 | caption | [375.0828, 157.6467, 224.4104, 20.7121] |
| nodes.shape_257 | 1 | 28 | caption | [784.1462, 157.6467, 207.1503, 20.7121] |
| nodes.shape_258 | 1 | 4 | caption | [396.5444, 212.8788, 34.53, 20.7121] |
| nodes.shape_259 | 1 | 4 | caption | [671.0682, 212.8788, 34.53, 20.7121] |
| nodes.shape_260 | 1 | 4 | caption | [945.582, 212.8788, 34.53, 20.7121] |
| nodes.shape_261 | 1 | 2 | caption | [404.8544, 258.2481, 17.92, 20.7121] |
| nodes.shape_262 | 1 | 2 | caption | [679.0427, 258.2481, 17.92, 20.7121] |
| nodes.shape_263 | 1 | 2 | caption | [953.8821, 258.2481, 17.92, 20.7121] |
| nodes.shape_264 | 1 | 12 | diagramCompact | [373.9781, 320.3532, 79.6724, 17.5] |
| nodes.shape_265 | 1 | 12 | diagramCompact | [648.1665, 320.3532, 79.6724, 17.5] |
| nodes.shape_266 | 1 | 12 | diagramCompact | [923.0059, 320.3532, 79.6724, 17.5] |
| nodes.shape_267 | 1 | 36 | diagramCompact | [572.7253, 521.2208, 230.555, 17.5] |
| nodes.shape_269 | 1 | 8 | caption | [384.6005, 402.8736, 58.4278, 20.0] |
| nodes.shape_272 | 1 | 3 | caption | [399.7006, 420.6663, 28.2177, 20.0] |
| nodes.shape_273 | 1 | 8 | caption | [659.1143, 402.8736, 58.4278, 20.0] |
| nodes.shape_274 | 1 | 5 | caption | [668.4939, 420.6663, 39.6685, 20.0] |
| nodes.shape_275 | 1 | 8 | caption | [932.6419, 402.8736, 58.4278, 20.0] |
| nodes.shape_276 | 1 | 6 | caption | [937.3761, 420.6663, 48.9693, 20.0] |
| nodes.shape_277 | 1 | 21 | diagramCompact | [621.6058, 595.8533, 132.794, 17.5] |
| nodes.shape_278 | 1 | 25 | diagramCompact | [335.1282, 595.8533, 159.3449, 17.5] |
| nodes.shape_279 | 1 | 18 | diagramCompact | [902.1064, 595.8533, 119.5087, 17.5] |
### page-08

前台7应用；中台开发/标准/治理3列；统一查询；基础设施；数据源4类；向上依赖箭头

Layout为`source-architecture-08`，原型为`templates/prototypes/source-architecture-08.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_213 | 1 | 8 | compactBody | [104.0889, 145.7143, 72.2898, 25.0] |
| nodes.shape_214 | 1 | 8 | compactBody | [270.6828, 145.7143, 72.2898, 25.0] |
| nodes.shape_221 | 1 | 8 | compactBody | [437.2664, 145.7143, 72.2898, 25.0] |
| nodes.shape_223 | 1 | 8 | compactBody | [603.85, 145.7143, 72.2898, 25.0] |
| nodes.shape_227 | 1 | 10 | compactBody | [761.4089, 145.7143, 90.3597, 25.0] |
| nodes.shape_229 | 1 | 10 | compactBody | [927.9925, 145.7143, 90.3597, 25.0] |
| nodes.shape_230 | 1 | 12 | compactBody | [1085.5412, 145.7143, 108.4399, 25.0] |
| nodes.shape_234 | 1 | 8 | compactBody | [101.3113, 390.8864, 77.8553, 25.0] |
| nodes.shape_235 | 1 | 8 | compactBody | [104.0889, 517.4375, 72.2898, 25.0] |
| nodes.shape_237 | 1 | 6 | compactBody | [113.1342, 599.3508, 54.2199, 25.0] |
| nodes.shape_238 | 1 | 6 | compactBody | [329.2808, 599.3508, 54.2199, 25.0] |
| nodes.shape_253 | 1 | 8 | compactBody | [570.8079, 599.3508, 72.2898, 25.0] |
| nodes.shape_254 | 1 | 10 | compactBody | [812.3453, 599.3508, 90.3597, 25.0] |
| nodes.shape_255 | 1 | 8 | compactBody | [1065.0654, 599.3508, 72.2898, 25.0] |
| nodes.shape_256 | 1 | 32 | compactBody | [584.2209, 517.4375, 289.1593, 25.0] |
| nodes.shape_268 | 1 | 12 | compactBody | [674.5806, 225.5625, 108.4399, 25.0] |
| nodes.shape_270 | 1 | 12 | compactBody | [335.1768, 272.379, 116.7727, 25.0] |
| nodes.shape_271 | 1 | 17 | compactBody | [648.1986, 272.379, 155.7004, 25.0] |
| nodes.shape_280 | 1 | 12 | compactBody | [1002.8947, 272.379, 116.7727, 25.0] |
| nodes.shape_281 | 1 | 20 | diagramCompact | [612.5029, 368.9297, 63.2549, 35.6544] |
| nodes.shape_282 | 1 | 20 | diagramCompact | [724.7116, 368.9297, 63.2549, 35.6544] |
| nodes.shape_283 | 1 | 17 | caption | [635.591, 328.8559, 129.2874, 20.0214] |
| nodes.shape_284 | 1 | 15 | caption | [643.0564, 426.3093, 114.3462, 20.0214] |
| nodes.shape_285 | 1 | 13 | caption | [1010.8971, 426.3093, 100.0968, 20.0214] |
| nodes.shape_286 | 1 | 13 | caption | [1010.8971, 376.7462, 100.0968, 20.0214] |
| nodes.shape_287 | 1 | 9 | caption | [972.5064, 327.1832, 66.7243, 20.0214] |
| nodes.shape_288 | 1 | 9 | caption | [1082.65, 327.1832, 66.7243, 20.0214] |
| nodes.shape_289 | 1 | 13 | caption | [343.1688, 327.1832, 100.0968, 20.0214] |
| nodes.shape_290 | 1 | 13 | caption | [343.1688, 376.7462, 100.0968, 20.0214] |
| nodes.shape_291 | 1 | 13 | caption | [343.1688, 426.3093, 100.0968, 20.0214] |
| nodes.shape_292 | 1 | 9 | diagramCompact | [827.3588, 353.3896, 21.7768, 66.7243] |
### page-09

6行业列、应用行、SaaS/API/SDK/小程序行、4平台组、5数据模块

Layout为`source-architecture-09`，原型为`templates/prototypes/source-architecture-09.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_278 | 1 | 8 | compactBody | [90.0254, 200.6313, 80.4574, 25.0] |
| nodes.shape_279 | 1 | 8 | compactBody | [94.1143, 293.5621, 72.2898, 25.0] |
| nodes.shape_293 | 1 | 8 | compactBody | [94.1143, 435.0233, 72.2898, 25.0] |
| nodes.shape_294 | 1 | 8 | compactBody | [94.1143, 578.5498, 72.2898, 25.0] |
| nodes.shape_295 | 1 | 4 | diagramCompact | [289.4858, 173.5592, 27.807, 17.5] |
| nodes.shape_296 | 1 | 38 | diagramMicro | [250.7337, 219.9462, 105.3112, 32.1024] |
| nodes.shape_297 | 1 | 4 | diagramCompact | [459.5078, 173.5592, 27.807, 17.5] |
| nodes.shape_298 | 1 | 38 | diagramMicro | [420.7557, 219.9462, 105.3112, 32.1024] |
| nodes.shape_299 | 1 | 4 | diagramCompact | [629.5401, 173.5592, 27.807, 17.5] |
| nodes.shape_300 | 1 | 38 | diagramMicro | [590.788, 219.9462, 105.3112, 32.1024] |
| nodes.shape_301 | 1 | 4 | diagramCompact | [798.2611, 173.5592, 30.409, 17.5] |
| nodes.shape_302 | 1 | 38 | diagramMicro | [760.8204, 219.9462, 105.3112, 32.1024] |
| nodes.shape_303 | 1 | 8 | diagramCompact | [955.6962, 173.5592, 55.6036, 17.5] |
| nodes.shape_304 | 1 | 20 | diagramMicro | [955.0044, 219.9462, 56.9975, 32.1024] |
| nodes.shape_305 | 1 | 8 | diagramCompact | [1125.7285, 173.5592, 55.6036, 17.5] |
| nodes.shape_306 | 1 | 38 | diagramMicro | [1100.8747, 219.9462, 105.3112, 32.1024] |
| nodes.shape_307 | 1 | 8 | diagramCompact | [289.8472, 298.1588, 55.6036, 17.5] |
| nodes.shape_308 | 1 | 8 | diagramCompact | [507.2433, 297.1468, 55.6036, 17.5] |
| nodes.shape_309 | 1 | 8 | diagramCompact | [718.9396, 298.1588, 55.6036, 17.5] |
| nodes.shape_310 | 1 | 8 | diagramCompact | [932.7113, 298.1588, 55.6036, 17.5] |
| nodes.shape_311 | 1 | 8 | diagramCompact | [1149.6221, 298.1588, 55.6036, 17.5] |
| nodes.shape_312 | 1 | 13 | diagramCompact | [310.5501, 413.8059, 83.4105, 17.5] |
| nodes.shape_313 | 1 | 9 | diagramMicro | [266.6558, 462.258, 50.0484, 15.5814] |
| nodes.shape_314 | 1 | 9 | diagramMicro | [387.8169, 462.258, 50.0484, 15.5814] |
| nodes.shape_315 | 1 | 9 | diagramMicro | [266.6558, 515.9514, 50.0484, 15.5814] |
| nodes.shape_316 | 1 | 9 | diagramMicro | [387.8169, 515.9514, 50.0484, 15.5814] |
| nodes.shape_317 | 1 | 9 | diagramMicro | [532.7166, 462.258, 50.0484, 15.5814] |
| nodes.shape_318 | 1 | 9 | diagramMicro | [653.8674, 462.258, 50.0484, 15.5814] |
| nodes.shape_319 | 1 | 13 | diagramMicro | [520.2019, 515.9514, 75.0674, 15.5814] |
| nodes.shape_320 | 1 | 13 | diagramMicro | [642.8396, 515.9514, 72.1143, 15.5814] |
| nodes.shape_321 | 1 | 13 | diagramMicro | [822.4025, 462.258, 75.0674, 15.5814] |
| nodes.shape_322 | 1 | 13 | diagramMicro | [822.4025, 515.9514, 75.0674, 15.5814] |
| nodes.shape_323 | 1 | 14 | diagramMicro | [1002.5539, 462.258, 80.2819, 15.5814] |
| nodes.shape_324 | 1 | 9 | diagramMicro | [1017.681, 515.9514, 50.0484, 15.5814] |
| nodes.shape_325 | 1 | 9 | diagramMicro | [1138.8318, 462.258, 50.0484, 15.5814] |
| nodes.shape_326 | 1 | 13 | diagramMicro | [1126.3171, 515.9514, 75.0674, 15.5814] |
| nodes.shape_327 | 1 | 8 | diagramCompact | [590.8603, 413.8059, 55.6036, 17.5] |
| nodes.shape_328 | 1 | 8 | diagramCompact | [832.1292, 413.8059, 55.6036, 17.5] |
| nodes.shape_329 | 1 | 12 | diagramCompact | [1064.0948, 413.8059, 78.3716, 17.5] |
| nodes.shape_330 | 1 | 19 | caption | [280.6677, 351.9595, 143.1857, 20.0214] |
| nodes.shape_331 | 1 | 9 | caption | [584.2519, 351.9595, 68.8101, 20.0214] |
| nodes.shape_332 | 1 | 14 | caption | [807.9776, 351.9595, 103.9173, 20.0214] |
| nodes.shape_333 | 1 | 6 | caption | [1078.2512, 351.9595, 50.0484, 20.0214] |
| nodes.shape_334 | 1 | 23 | diagramMicro | [258.3746, 584.3794, 125.1158, 15.0135] |
| nodes.shape_335 | 1 | 17 | diagramMicro | [476.4728, 584.3794, 96.4415, 15.0135] |
| nodes.shape_336 | 1 | 17 | diagramMicro | [679.888, 584.3794, 97.1436, 15.0135] |
| nodes.shape_338 | 1 | 25 | diagramMicro | [863.4056, 584.3794, 137.6305, 15.0135] |
| nodes.shape_339 | 1 | 18 | diagramMicro | [1085.9232, 584.3794, 100.0968, 15.0135] |
### page-10

新客迁入→沉淀→复购→分享/流失；4泳道用户路径/运营方法/工具/组织分工

Layout为`source-architecture-10`，原型为`templates/prototypes/source-architecture-10.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_262 | 1 | 8 | compactBody | [94.1143, 271.0005, 72.2898, 25.0] |
| nodes.shape_263 | 1 | 8 | compactBody | [94.1143, 151.9046, 72.2898, 25.0] |
| nodes.shape_265 | 1 | 8 | compactBody | [94.1143, 425.8852, 72.2898, 25.0] |
| nodes.shape_266 | 1 | 8 | compactBody | [94.1143, 556.6697, 72.2898, 25.0] |
| nodes.shape_268 | 1 | 23 | caption | [235.9267, 154.399, 166.8211, 20.0214] |
| nodes.shape_269 | 1 | 9 | caption | [606.5966, 154.399, 66.7243, 20.0214] |
| nodes.shape_270 | 1 | 9 | caption | [881.2586, 154.399, 66.7243, 20.0214] |
| nodes.shape_271 | 1 | 8 | diagramCompact | [474.8311, 155.6649, 55.6036, 17.5] |
| nodes.shape_274 | 1 | 11 | diagramCompact | [742.5336, 155.6649, 69.5122, 17.5] |
| nodes.shape_275 | 1 | 8 | diagramCompact | [1024.1552, 155.6649, 55.6036, 17.5] |
| nodes.shape_277 | 1 | 13 | diagramMicro | [242.4422, 208.2473, 75.0674, 15.5814] |
| nodes.shape_280 | 1 | 9 | diagramMicro | [254.9568, 241.9708, 50.0484, 15.5814] |
| nodes.shape_281 | 1 | 9 | diagramMicro | [254.9568, 275.7047, 50.0484, 15.5814] |
| nodes.shape_282 | 1 | 13 | diagramMicro | [242.4422, 309.4385, 75.0674, 15.5814] |
| nodes.shape_283 | 1 | 13 | diagramMicro | [242.4422, 343.1621, 75.0674, 15.5814] |
| nodes.shape_284 | 1 | 80 | caption | [382.1687, 240.0812, 150.1452, 86.8386] |
| nodes.shape_285 | 1 | 9 | diagramMicro | [921.3015, 208.2473, 50.0484, 15.5814] |
| nodes.shape_286 | 1 | 9 | diagramMicro | [921.3015, 241.9708, 50.0484, 15.5814] |
| nodes.shape_287 | 1 | 9 | diagramMicro | [921.3015, 275.7047, 50.0484, 15.5814] |
| nodes.shape_288 | 1 | 9 | diagramMicro | [921.3015, 309.4385, 50.0484, 15.5814] |
| nodes.shape_289 | 1 | 9 | diagramMicro | [921.3015, 343.1621, 50.0484, 15.5814] |
| nodes.shape_290 | 1 | 11 | diagramMicro | [625.9262, 339.7236, 62.5631, 15.5814] |
| nodes.shape_291 | 1 | 9 | diagramMicro | [625.9881, 302.5513, 50.0484, 15.5814] |
| nodes.shape_292 | 1 | 4 | diagramMicro | [696.3264, 302.5513, 25.019, 15.5814] |
| nodes.shape_337 | 1 | 4 | diagramMicro | [741.7592, 302.5513, 25.019, 15.5814] |
| nodes.shape_340 | 1 | 6 | diagramMicro | [708.6552, 339.7236, 37.5337, 15.5814] |
| nodes.shape_341 | 1 | 9 | diagramMicro | [625.9881, 248.858, 50.0484, 15.5814] |
| nodes.shape_342 | 1 | 9 | diagramMicro | [625.9881, 211.6857, 50.0484, 15.5814] |
| nodes.shape_343 | 1 | 11 | diagramMicro | [696.1405, 248.858, 62.5631, 15.5814] |
| nodes.shape_344 | 1 | 6 | diagramMicro | [696.2644, 211.6857, 37.5337, 15.5814] |
| nodes.shape_345 | 1 | 6 | diagramMicro | [754.088, 211.6857, 37.5337, 15.5814] |
| nodes.shape_346 | 1 | 4 | diagramMicro | [778.9315, 248.858, 25.019, 15.5814] |
| nodes.shape_347 | 1 | 2 | diagramCompact | [581.9051, 221.3815, 15.68, 33.3621] |
| nodes.shape_348 | 1 | 2 | diagramCompact | [581.9051, 312.2471, 15.68, 33.3621] |
| nodes.shape_349 | 1 | 2 | diagramCompact | [864.8277, 266.8143, 15.68, 33.3621] |
| nodes.shape_350 | 1 | 9 | diagramMicro | [1162.9215, 189.6611, 50.0484, 15.5814] |
| nodes.shape_351 | 1 | 11 | diagramMicro | [1156.6642, 223.3846, 62.5631, 15.5814] |
| nodes.shape_352 | 1 | 9 | diagramMicro | [1162.9215, 309.4385, 50.0484, 15.5814] |
| nodes.shape_353 | 1 | 9 | diagramMicro | [1162.9215, 343.1621, 50.0484, 15.5814] |
| nodes.shape_354 | 1 | 9 | caption | [1154.5784, 154.399, 66.7243, 20.0214] |
| nodes.shape_355 | 1 | 9 | caption | [1154.5784, 271.7913, 66.7243, 20.0214] |
| nodes.shape_356 | 1 | 170 | diagramMicro | [256.1753, 395.7609, 188.7218, 85.2485] |
| nodes.shape_357 | 1 | 185 | diagramMicro | [511.4871, 395.7609, 204.7058, 85.2485] |
| nodes.shape_358 | 1 | 136 | diagramMicro | [256.1753, 535.694, 188.7218, 67.9014] |
| nodes.shape_359 | 1 | 185 | diagramMicro | [511.2186, 526.5455, 204.9743, 85.2485] |
| nodes.shape_360 | 1 | 60 | diagramMicro | [782.1015, 395.7609, 166.8211, 33.1969] |
| nodes.shape_361 | 1 | 68 | diagramMicro | [1028.1925, 395.7609, 188.7218, 33.1969] |
| nodes.shape_362 | 1 | 136 | diagramMicro | [782.1015, 535.2293, 188.7218, 67.9014] |
| nodes.shape_363 | 1 | 102 | diagramMicro | [1028.1925, 535.2293, 188.7218, 50.544] |
### page-11

4阶段导入/沉淀/转化/持续运营；底部ABC回路与顶部反馈箭头；公私域与内容/CRM模块

Layout为`source-architecture-11`，原型为`templates/prototypes/source-architecture-11.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_328 | 1 | 9 | caption | [135.9351, 172.6331, 66.8356, 20.0548] |
| nodes.shape_329 | 1 | 9 | caption | [452.4269, 172.6331, 66.8356, 20.0548] |
| nodes.shape_330 | 1 | 9 | caption | [768.9187, 172.6331, 66.8356, 20.0548] |
| nodes.shape_331 | 1 | 9 | caption | [1085.4105, 172.6331, 66.8356, 20.0548] |
| nodes.shape_332 | 1 | 16 | compactBody | [92.8053, 252.8776, 144.8209, 25.0] |
| nodes.shape_333 | 1 | 16 | compactBody | [92.8053, 386.2696, 144.8209, 25.0] |
| nodes.shape_334 | 1 | 4 | diagramMicro | [85.8032, 323.1012, 25.0608, 15.6074] |
| nodes.shape_335 | 1 | 4 | diagramMicro | [153.3732, 323.1012, 25.0608, 15.6074] |
| nodes.shape_336 | 1 | 4 | diagramMicro | [220.9431, 323.1012, 25.0608, 15.6074] |
| nodes.shape_338 | 1 | 6 | diagramMicro | [81.7074, 456.8655, 33.242, 15.6074] |
| nodes.shape_339 | 1 | 6 | diagramMicro | [147.1054, 456.8655, 37.5963, 15.6074] |
| nodes.shape_364 | 1 | 4 | diagramMicro | [220.9431, 456.8655, 25.0608, 15.6074] |
| nodes.shape_368 | 1 | 4 | diagramMicro | [85.8032, 536.8573, 25.0608, 15.6074] |
| nodes.shape_369 | 1 | 4 | diagramMicro | [220.9431, 536.8573, 25.0608, 15.6074] |
| nodes.shape_370 | 1 | 9 | diagramMicro | [386.9979, 301.0398, 50.1319, 15.6074] |
| nodes.shape_371 | 1 | 6 | diagramMicro | [463.5972, 301.0398, 37.5963, 15.6074] |
| nodes.shape_372 | 1 | 4 | diagramMicro | [540.1965, 301.0398, 25.0608, 15.6074] |
| nodes.shape_373 | 1 | 9 | diagramMicro | [415.2753, 347.9241, 50.1319, 15.6074] |
| nodes.shape_374 | 1 | 8 | diagramMicro | [501.059, 347.9241, 44.0399, 15.6074] |
| nodes.shape_375 | 1 | 8 | compactBody | [446.1901, 252.8776, 72.4104, 25.0] |
| nodes.shape_376 | 1 | 8 | compactBody | [446.1901, 468.4334, 72.4104, 25.0] |
| nodes.shape_377 | 1 | 6 | diagramMicro | [463.5972, 416.88, 37.5963, 15.6074] |
| nodes.shape_378 | 1 | 4 | diagramMicro | [402.9776, 534.7887, 25.0608, 15.6074] |
| nodes.shape_379 | 1 | 4 | diagramMicro | [469.7822, 534.7887, 25.2366, 15.6074] |
| nodes.shape_380 | 1 | 3 | diagramMicro | [542.1306, 534.7887, 17.0554, 15.6074] |
| nodes.shape_381 | 1 | 13 | diagramMicro | [708.1957, 326.5454, 75.1927, 15.6074] |
| nodes.shape_382 | 1 | 13 | diagramMicro | [819.216, 326.5454, 75.1927, 15.6074] |
| nodes.shape_383 | 1 | 13 | caption | [750.136, 254.5176, 100.2638, 20.0548] |
| nodes.shape_384 | 1 | 13 | caption | [750.136, 281.9262, 100.2638, 20.0548] |
| nodes.shape_385 | 1 | 9 | diagramMicro | [650.0584, 400.3314, 50.1319, 15.6074] |
| nodes.shape_386 | 1 | 7 | diagramMicro | [637.6987, 500.44, 38.9926, 24.9987] |
| nodes.shape_387 | 1 | 7 | diagramMicro | [755.2557, 461.658, 38.9926, 15.0] |
| nodes.shape_388 | 1 | 7 | diagramMicro | [753.694, 491.3007, 42.1265, 15.0] |
| nodes.shape_389 | 1 | 7 | diagramMicro | [755.2557, 520.9537, 38.9926, 15.0] |
| nodes.shape_390 | 1 | 7 | diagramMicro | [755.2557, 550.6067, 38.9926, 15.0] |
| nodes.shape_391 | 1 | 4 | diagramMicro | [844.2458, 501.3709, 22.2785, 26.7363] |
| nodes.shape_392 | 1 | 7 | diagramMicro | [890.7473, 501.8156, 38.9926, 24.9987] |
| nodes.shape_393 | 1 | 12 | diagramMicro | [290.0335, 452.8108, 68.2319, 15.0] |
| nodes.shape_394 | 1 | 10 | diagramMicro | [294.905, 482.5052, 58.4889, 15.0] |
| nodes.shape_395 | 1 | 10 | diagramMicro | [294.905, 309.8207, 58.4889, 15.0] |
| nodes.shape_396 | 1 | 7 | diagramMicro | [304.6583, 339.515, 38.9926, 15.0] |
| nodes.shape_397 | 1 | 6 | compactBody | [957.283, 361.9283, 24.7298, 86.8904] |
| nodes.shape_398 | 1 | 13 | diagramMicro | [1078.4704, 265.1811, 75.1927, 15.6074] |
| nodes.shape_399 | 1 | 18 | diagramMicro | [1065.9348, 331.3755, 100.2638, 15.6074] |
| nodes.shape_400 | 1 | 13 | diagramMicro | [1078.4704, 397.5698, 75.1927, 15.6074] |
| nodes.shape_401 | 1 | 13 | diagramMicro | [1078.4704, 463.7642, 75.1927, 15.6074] |
| nodes.shape_402 | 1 | 13 | diagramMicro | [1078.4704, 529.9586, 75.1927, 15.6074] |
| nodes.shape_403 | 1 | 2 | diagramMicro | [316.5836, 395.0979, 14.449, 15.0385] |
| nodes.shape_404 | 1 | 2 | diagramMicro | [633.6753, 290.2936, 16.0108, 15.0385] |
| nodes.shape_405 | 1 | 2 | diagramMicro | [648.7552, 455.0865, 16.1866, 15.0385] |
| nodes.shape_406 | 1 | 2 | diagramMicro | [159.1887, 607.7266, 13.44, 20.0548] |
| nodes.shape_407 | 1 | 2 | diagramMicro | [475.6753, 607.7266, 13.44, 20.0548] |
| nodes.shape_408 | 1 | 2 | diagramMicro | [832.856, 607.7266, 13.44, 20.0548] |
### page-12

门户表现层；应用层分管理平台与第三方；服务层含共性模块和接口；系统层数据库/中间件/OS；双向依赖箭头

Layout为`source-architecture-12`，原型为`templates/prototypes/source-architecture-12.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_282 | 1 | 6 | compactBody | [84.9845, 171.433, 54.3384, 25.0] |
| nodes.shape_283 | 1 | 6 | compactBody | [84.9845, 303.5485, 54.3384, 25.0] |
| nodes.shape_284 | 1 | 6 | compactBody | [84.9845, 435.664, 54.3384, 25.0] |
| nodes.shape_285 | 1 | 6 | compactBody | [84.9845, 562.5951, 54.3384, 25.0] |
| nodes.shape_286 | 1 | 14 | compactBody | [641.5419, 148.1496, 127.8314, 25.0] |
| nodes.shape_287 | 1 | 17 | compactBody | [436.8441, 262.5696, 158.4827, 25.0] |
| nodes.shape_288 | 1 | 10 | compactBody | [1009.255, 262.5696, 90.5571, 25.0] |
| nodes.shape_289 | 1 | 9 | diagramMicro | [391.312, 303.0615, 50.1577, 15.6154] |
| nodes.shape_290 | 1 | 9 | diagramMicro | [483.7628, 191.3009, 50.1577, 15.6154] |
| nodes.shape_291 | 1 | 9 | diagramMicro | [616.4579, 191.3009, 50.1577, 15.6154] |
| nodes.shape_292 | 1 | 9 | diagramMicro | [745.9139, 191.3009, 50.1577, 15.6154] |
| nodes.shape_293 | 1 | 9 | diagramMicro | [876.9946, 191.3009, 50.1577, 15.6154] |
| nodes.shape_294 | 1 | 9 | diagramMicro | [521.6994, 303.0615, 50.1577, 15.6154] |
| nodes.shape_296 | 1 | 9 | diagramMicro | [652.7801, 303.0615, 50.1577, 15.6154] |
| nodes.shape_307 | 1 | 9 | diagramMicro | [260.2417, 303.0615, 50.1577, 15.6154] |
| nodes.shape_308 | 1 | 9 | diagramMicro | [391.312, 344.4543, 50.1577, 15.6154] |
| nodes.shape_309 | 1 | 9 | diagramMicro | [521.6994, 344.4543, 50.1577, 15.6154] |
| nodes.shape_310 | 1 | 9 | diagramMicro | [260.2417, 344.4543, 50.1577, 15.6154] |
| nodes.shape_317 | 1 | 9 | diagramMicro | [963.9195, 303.0615, 50.1577, 15.6154] |
| nodes.shape_318 | 1 | 9 | diagramMicro | [1094.9898, 303.0615, 50.1577, 15.6154] |
| nodes.shape_319 | 1 | 9 | diagramMicro | [963.9195, 344.4543, 50.1577, 15.6154] |
| nodes.shape_320 | 1 | 9 | diagramMicro | [1094.9898, 344.4543, 50.1577, 15.6154] |
| nodes.shape_321 | 1 | 7 | diagramMicro | [967.6552, 419.6547, 42.6656, 15.6154] |
| nodes.shape_322 | 1 | 9 | diagramMicro | [1094.9898, 419.6547, 50.1577, 15.6154] |
| nodes.shape_323 | 1 | 9 | diagramMicro | [963.9195, 461.0476, 50.1577, 15.6154] |
| nodes.shape_327 | 1 | 9 | diagramMicro | [1094.9898, 461.0476, 50.1577, 15.6154] |
| nodes.shape_337 | 1 | 4 | diagramMicro | [403.854, 419.6547, 25.0737, 15.6154] |
| nodes.shape_340 | 1 | 4 | diagramMicro | [534.2414, 419.6547, 25.0737, 15.6154] |
| nodes.shape_341 | 1 | 4 | diagramMicro | [665.3221, 419.6547, 25.0737, 15.6154] |
| nodes.shape_342 | 1 | 4 | diagramMicro | [272.7733, 419.6547, 25.0737, 15.6154] |
| nodes.shape_343 | 1 | 4 | diagramMicro | [403.854, 461.0476, 25.0737, 15.6154] |
| nodes.shape_344 | 1 | 4 | diagramMicro | [534.2414, 461.0476, 25.0737, 15.6154] |
| nodes.shape_345 | 1 | 4 | diagramMicro | [665.3221, 461.0476, 25.0737, 15.6154] |
| nodes.shape_346 | 1 | 4 | diagramMicro | [272.7733, 461.0476, 25.0737, 15.6154] |
| nodes.shape_347 | 1 | 32 | caption | [309.7889, 537.7795, 235.9804, 20.8206] |
| nodes.shape_348 | 1 | 19 | caption | [905.7729, 537.7795, 143.6745, 20.8206] |
| nodes.shape_349 | 1 | 36 | caption | [576.0481, 590.9072, 259.4915, 20.8206] |
### page-13

阶段性/驱动性/流程性/抽象性4横向箭头；左特征→判断→定位→编排→工具；4列内角色与模块

Layout为`source-architecture-13`，原型为`templates/prototypes/source-architecture-13.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_311 | 1 | 4 | compactBody | [67.7839, 139.8287, 36.1501, 25.0] |
| nodes.shape_312 | 1 | 4 | compactBody | [67.7839, 225.1908, 36.1501, 25.0] |
| nodes.shape_313 | 1 | 4 | compactBody | [67.7839, 343.4091, 36.1501, 25.0] |
| nodes.shape_314 | 1 | 4 | compactBody | [67.7839, 479.2016, 36.1501, 25.0] |
| nodes.shape_315 | 1 | 4 | compactBody | [67.7839, 588.6534, 36.1501, 25.0] |
| nodes.shape_316 | 1 | 6 | compactBody | [256.103, 139.8287, 54.2199, 25.0] |
| nodes.shape_324 | 1 | 6 | compactBody | [532.7992, 139.8287, 54.2199, 25.0] |
| nodes.shape_325 | 1 | 6 | compactBody | [806.7695, 139.8287, 54.2199, 25.0] |
| nodes.shape_326 | 1 | 6 | compactBody | [1081.6381, 139.8287, 54.2199, 25.0] |
| nodes.shape_328 | 1 | 15 | diagramCompact | [256.991, 203.4675, 97.3088, 17.5] |
| nodes.shape_329 | 1 | 15 | diagramCompact | [256.991, 253.0305, 97.3088, 17.5] |
| nodes.shape_330 | 1 | 6 | diagramCompact | [553.7603, 203.4675, 41.7053, 17.5] |
| nodes.shape_331 | 1 | 6 | diagramCompact | [553.7603, 253.0305, 41.7053, 17.5] |
| nodes.shape_332 | 1 | 11 | diagramCompact | [815.4224, 203.4675, 69.5122, 17.5] |
| nodes.shape_333 | 1 | 11 | diagramCompact | [815.4224, 253.0305, 69.5122, 17.5] |
| nodes.shape_334 | 1 | 8 | diagramCompact | [1096.445, 203.4675, 55.6036, 17.5] |
| nodes.shape_335 | 1 | 8 | diagramCompact | [1096.445, 253.0305, 55.6036, 17.5] |
| nodes.shape_336 | 1 | 22 | diagramCompact | [214.6042, 312.6198, 139.0244, 17.5] |
| nodes.shape_338 | 1 | 19 | diagramCompact | [495.5237, 312.6198, 125.1158, 17.5] |
| nodes.shape_339 | 1 | 18 | diagramCompact | [773.0563, 312.6198, 117.9911, 17.5] |
| nodes.shape_350 | 1 | 17 | diagramCompact | [1050.4236, 312.6198, 111.2175, 17.5] |
| nodes.shape_351 | 1 | 11 | diagramCompact | [249.35, 447.4934, 69.5122, 17.5] |
| nodes.shape_352 | 1 | 8 | diagramCompact | [530.2798, 447.4934, 55.6036, 17.5] |
| nodes.shape_353 | 1 | 11 | diagramCompact | [797.3009, 447.4934, 69.5122, 17.5] |
| nodes.shape_354 | 1 | 8 | diagramCompact | [1078.2306, 447.4934, 55.6036, 17.5] |
| nodes.shape_355 | 1 | 16 | diagramMicro | [240.3151, 348.2991, 87.5821, 15.5814] |
| nodes.shape_356 | 1 | 16 | diagramMicro | [240.3151, 384.2943, 87.5821, 15.5814] |
| nodes.shape_357 | 1 | 9 | diagramMicro | [533.0574, 348.2991, 50.0484, 15.5814] |
| nodes.shape_358 | 1 | 9 | diagramMicro | [533.0574, 384.2943, 50.0484, 15.5814] |
| nodes.shape_359 | 1 | 18 | diagramMicro | [782.0086, 348.2991, 100.0968, 15.5814] |
| nodes.shape_360 | 1 | 13 | diagramMicro | [794.5233, 384.2943, 75.0674, 15.5814] |
| nodes.shape_361 | 1 | 16 | diagramMicro | [1062.2362, 348.2991, 87.5821, 15.5814] |
| nodes.shape_362 | 1 | 13 | diagramMicro | [1068.4935, 384.2943, 75.0674, 15.5814] |
| nodes.shape_363 | 1 | 11 | diagramMicro | [252.8298, 483.9057, 62.5631, 15.5814] |
| nodes.shape_364 | 1 | 11 | diagramMicro | [252.8298, 521.0781, 62.5631, 15.5814] |
| nodes.shape_365 | 1 | 13 | diagramMicro | [520.553, 483.9057, 75.0674, 15.695] |
| nodes.shape_366 | 1 | 13 | diagramMicro | [520.553, 521.0781, 75.0674, 15.5814] |
| nodes.shape_367 | 1 | 23 | diagramMicro | [769.4939, 483.9057, 125.1158, 15.5814] |
| nodes.shape_368 | 1 | 13 | diagramMicro | [794.5233, 521.0781, 75.0674, 15.5814] |
| nodes.shape_369 | 1 | 20 | diagramMicro | [1049.7318, 483.9057, 112.6011, 15.5814] |
| nodes.shape_370 | 1 | 20 | diagramMicro | [1049.7318, 521.0781, 112.6011, 15.5814] |
| nodes.shape_372 | 1 | 34 | heading | [174.2826, 559.1074, 219.647, 83.4105] |
| nodes.shape_373 | 1 | 30 | heading | [459.5801, 559.1074, 197.9322, 83.4105] |
| nodes.shape_374 | 1 | 26 | heading | [746.9943, 559.1074, 170.1253, 83.4105] |
| nodes.shape_375 | 1 | 16 | heading | [1052.685, 559.1074, 106.6949, 83.4105] |
### page-14

顶层规划；园区/企业2模型入口；2能力平台与保障右栏；信息汇聚、云设施、接入设备3层

Layout为`source-architecture-14`，原型为`templates/prototypes/source-architecture-14.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_289 | 1 | 24 | compactBody | [528.6535, 134.006, 222.6824, 25.0] |
| nodes.shape_290 | 1 | 16 | compactBody | [125.0728, 197.8005, 74.2275, 51.4959] |
| nodes.shape_291 | 1 | 8 | compactBody | [125.0728, 336.5121, 74.2275, 25.0] |
| nodes.shape_292 | 1 | 10 | compactBody | [115.7957, 442.5362, 92.7817, 25.0] |
| nodes.shape_293 | 1 | 34 | compactBody | [484.8549, 497.6687, 310.2901, 25.0] |
| nodes.shape_294 | 1 | 36 | compactBody | [475.8429, 613.5848, 328.3142, 25.0] |
| nodes.shape_296 | 1 | 8 | compactBody | [1074.3383, 211.0431, 74.2275, 25.0] |
| nodes.shape_299 | 1 | 15 | diagramCompact | [226.7287, 559.2366, 99.9171, 17.7696] |
| nodes.shape_307 | 1 | 15 | diagramCompact | [590.0415, 559.2366, 99.9171, 17.7696] |
| nodes.shape_308 | 1 | 18 | diagramCompact | [946.2082, 559.2366, 114.1986, 17.7696] |
| nodes.shape_309 | 1 | 15 | diagramCompact | [738.4752, 199.4651, 99.9171, 17.7696] |
| nodes.shape_310 | 1 | 13 | diagramCompact | [340.5986, 199.4651, 85.6463, 17.7696] |
| nodes.shape_317 | 1 | 18 | diagramCompact | [731.3398, 283.1287, 114.1986, 17.7696] |
| nodes.shape_318 | 1 | 18 | diagramCompact | [326.3277, 283.1287, 114.1986, 17.7696] |
| nodes.shape_319 | 1 | 7 | diagramMicro | [296.641, 233.3622, 39.9711, 15.0] |
| nodes.shape_320 | 1 | 7 | diagramMicro | [430.6766, 233.1439, 39.0805, 15.0] |
| nodes.shape_321 | 1 | 7 | diagramMicro | [701.653, 233.3622, 39.9711, 15.0] |
| nodes.shape_322 | 1 | 7 | diagramMicro | [835.6887, 233.1439, 39.0805, 15.0] |
| nodes.shape_323 | 1 | 7 | diagramMicro | [673.0265, 317.1094, 39.9711, 25.626] |
| nodes.shape_327 | 1 | 3 | diagramMicro | [587.6029, 317.1094, 19.9855, 25.626] |
| nodes.shape_337 | 1 | 3 | diagramMicro | [778.4463, 317.1094, 19.9855, 25.626] |
| nodes.shape_340 | 1 | 3 | diagramMicro | [873.868, 317.1094, 19.9855, 25.626] |
| nodes.shape_341 | 1 | 3 | diagramMicro | [969.6077, 317.1094, 19.9855, 25.626] |
| nodes.shape_342 | 1 | 3 | diagramMicro | [683.0246, 363.76, 19.9855, 25.626] |
| nodes.shape_343 | 1 | 3 | diagramMicro | [587.6029, 363.76, 19.9855, 25.626] |
| nodes.shape_344 | 1 | 3 | diagramMicro | [778.4463, 363.76, 19.9855, 25.626] |
| nodes.shape_345 | 1 | 3 | diagramMicro | [873.868, 363.76, 19.9855, 25.626] |
| nodes.shape_346 | 1 | 3 | diagramMicro | [969.6077, 363.76, 19.9855, 25.626] |
| nodes.shape_347 | 1 | 5 | diagramMicro | [368.4299, 317.1094, 29.973, 25.626] |
| nodes.shape_348 | 1 | 5 | diagramMicro | [273.0082, 317.1094, 29.973, 25.626] |
| nodes.shape_349 | 1 | 5 | diagramMicro | [463.8516, 317.1094, 29.973, 25.626] |
| nodes.shape_376 | 1 | 5 | diagramMicro | [368.4299, 363.76, 29.973, 25.626] |
| nodes.shape_377 | 1 | 5 | diagramMicro | [273.0082, 363.76, 29.973, 25.626] |
| nodes.shape_378 | 1 | 12 | diagramMicro | [309.9258, 447.3125, 69.9441, 15.0] |
| nodes.shape_379 | 1 | 12 | diagramMicro | [503.6, 447.3125, 69.9441, 15.0] |
| nodes.shape_380 | 1 | 12 | diagramMicro | [693.733, 447.3125, 69.9441, 15.0] |
| nodes.shape_381 | 1 | 12 | diagramMicro | [887.4072, 447.3125, 69.9441, 15.0] |
| nodes.shape_382 | 1 | 7 | diagramMicro | [1091.4718, 270.1207, 39.9711, 15.0] |
| nodes.shape_383 | 1 | 7 | diagramMicro | [1091.4718, 305.4586, 39.9711, 15.0] |
| nodes.shape_384 | 1 | 7 | diagramMicro | [1091.4718, 340.7964, 39.9711, 15.0] |
| nodes.shape_385 | 1 | 7 | diagramMicro | [1091.4718, 376.1448, 39.9711, 15.0] |
| nodes.shape_386 | 1 | 7 | diagramMicro | [1091.4718, 411.4827, 39.9711, 15.0] |
| nodes.shape_387 | 1 | 7 | diagramMicro | [1091.4718, 446.8205, 39.9711, 15.0] |
### page-15

传统组织→多种环境变化→节能/增效两翼→新组织能力底座；中心改造项目

Layout为`source-architecture-15`，原型为`templates/prototypes/source-architecture-15.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_192 | 1 | 14 | compactBody | [573.2619, 134.7356, 133.4762, 25.0] |
| nodes.shape_194 | 1 | 4 | compactBody | [167.7349, 281.0778, 38.1407, 25.0] |
| nodes.shape_195 | 1 | 4 | compactBody | [1083.5696, 281.0778, 38.1407, 25.0] |
| nodes.shape_196 | 1 | 12 | diagramCompact | [793.5869, 256.5028, 79.2011, 17.5] |
| nodes.shape_198 | 1 | 12 | diagramCompact | [612.0236, 256.5028, 79.2011, 17.5] |
| nodes.shape_199 | 1 | 12 | diagramCompact | [430.4494, 256.5028, 79.2011, 17.5] |
| nodes.shape_204 | 1 | 12 | diagramCompact | [793.5869, 318.9595, 79.2011, 17.5] |
| nodes.shape_206 | 1 | 12 | diagramCompact | [612.0236, 318.9595, 79.2011, 17.5] |
| nodes.shape_207 | 1 | 12 | diagramCompact | [430.4494, 318.9595, 79.2011, 17.5] |
| nodes.shape_210 | 1 | 10 | diagramCompact | [1069.6359, 474.1934, 66.0082, 33.8702] |
| nodes.shape_211 | 1 | 8 | diagramCompact | [1076.2378, 405.9192, 52.8044, 33.8702] |
| nodes.shape_213 | 1 | 12 | diagramCompact | [147.1993, 474.1934, 79.2011, 33.8702] |
| nodes.shape_214 | 1 | 14 | diagramCompact | [140.5974, 405.9192, 92.4049, 33.8702] |
| nodes.shape_215 | 1 | 18 | diagramCompact | [410.6437, 448.2414, 118.8016, 17.5] |
| nodes.shape_217 | 1 | 14 | diagramCompact | [605.4217, 448.2414, 92.4049, 17.5] |
| nodes.shape_218 | 1 | 16 | diagramCompact | [780.3831, 448.2414, 105.6087, 17.5] |
| nodes.shape_219 | 1 | 19 | compactBody | [554.5565, 546.1673, 171.606, 25.0] |
| nodes.shape_220 | 1 | 14 | caption | [503.6695, 614.2061, 105.6087, 21.1239] |
| nodes.shape_221 | 1 | 14 | caption | [675.7984, 614.2061, 105.6087, 21.1239] |
| nodes.shape_223 | 1 | 14 | caption | [852.6554, 614.2061, 105.6087, 21.1239] |
| nodes.shape_224 | 1 | 14 | caption | [1024.7843, 614.2061, 105.6087, 21.1239] |
| nodes.shape_225 | 1 | 14 | caption | [326.4639, 614.2061, 105.6087, 21.1239] |
| nodes.shape_226 | 1 | 14 | caption | [149.6069, 614.2061, 105.6087, 21.1239] |
### page-16

上方用户旅程；下方公域入口、创意生产/转化、教务教学/学员服务、持续运营4区；内部向下与横向流

Layout为`source-architecture-16`，原型为`templates/prototypes/source-architecture-16.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_294 | 1 | 8 | caption | [196.3852, 147.8427, 62.2809, 20.0] |
| nodes.shape_295 | 1 | 8 | caption | [445.8978, 147.8427, 62.2809, 20.0] |
| nodes.shape_296 | 1 | 8 | caption | [742.3735, 147.8427, 62.2809, 20.0] |
| nodes.shape_297 | 1 | 8 | caption | [1021.3339, 147.8427, 62.2809, 20.0] |
| nodes.shape_298 | 1 | 8 | diagramCompact | [136.1649, 340.4404, 50.9581, 17.5] |
| nodes.shape_299 | 1 | 10 | diagramCompact | [129.7938, 389.5061, 63.7002, 17.5] |
| nodes.shape_300 | 1 | 8 | diagramCompact | [136.1649, 438.5612, 50.9581, 17.5] |
| nodes.shape_301 | 1 | 10 | diagramCompact | [129.7938, 487.6269, 63.7002, 17.5] |
| nodes.shape_302 | 1 | 8 | diagramCompact | [1090.7744, 340.4404, 50.9581, 17.5] |
| nodes.shape_303 | 1 | 8 | diagramCompact | [1090.7744, 389.5061, 50.9581, 17.5] |
| nodes.shape_304 | 1 | 8 | diagramCompact | [1090.7744, 438.5612, 50.9581, 17.5] |
| nodes.shape_305 | 1 | 10 | diagramCompact | [1084.4033, 487.6269, 63.7002, 17.5] |
| nodes.shape_306 | 1 | 10 | diagramMicro | [77.1253, 387.522, 13.44, 74.7392] |
| nodes.shape_307 | 1 | 18 | diagramMicro | [1189.4347, 359.4934, 13.44, 130.7857] |
| nodes.shape_308 | 1 | 10 | diagramMicro | [338.087, 387.522, 13.44, 74.7392] |
| nodes.shape_309 | 1 | 10 | diagramMicro | [624.0493, 387.522, 13.44, 74.7392] |
| nodes.shape_310 | 1 | 10 | diagramMicro | [913.071, 387.522, 13.44, 74.7392] |
| nodes.shape_311 | 1 | 8 | caption | [125.7672, 198.3066, 62.2809, 20.0] |
| nodes.shape_312 | 1 | 8 | caption | [262.6191, 198.3066, 62.2809, 20.0] |
| nodes.shape_313 | 1 | 12 | caption | [430.685, 198.3066, 93.4214, 20.0] |
| nodes.shape_314 | 1 | 8 | caption | [744.8336, 198.3066, 62.2809, 20.0] |
| nodes.shape_315 | 1 | 8 | caption | [1093.6761, 198.3066, 62.2809, 20.0] |
| nodes.shape_316 | 1 | 8 | diagramMicro | [253.2412, 301.745, 45.2914, 15.0] |
| nodes.shape_317 | 1 | 8 | diagramMicro | [253.2412, 368.3141, 45.2914, 29.0483] |
| nodes.shape_318 | 1 | 8 | diagramMicro | [253.2412, 441.9074, 45.2914, 29.0483] |
| nodes.shape_319 | 1 | 8 | diagramMicro | [253.2412, 515.5006, 45.2914, 29.0483] |
| nodes.shape_320 | 1 | 8 | diagramMicro | [972.3524, 325.5564, 45.2914, 29.0483] |
| nodes.shape_321 | 1 | 8 | diagramMicro | [972.3524, 392.8417, 45.2914, 29.0483] |
| nodes.shape_322 | 1 | 8 | diagramMicro | [972.3524, 460.127, 45.2914, 29.0483] |
| nodes.shape_323 | 1 | 8 | diagramMicro | [972.3524, 527.4122, 45.2914, 29.0483] |
| nodes.shape_324 | 1 | 16 | caption | [162.1223, 627.6147, 118.8951, 20.3853] |
| nodes.shape_325 | 1 | 14 | caption | [434.4909, 627.6147, 101.9161, 20.3853] |
| nodes.shape_326 | 1 | 14 | caption | [724.6585, 627.6147, 101.9161, 20.3853] |
| nodes.shape_327 | 1 | 14 | caption | [998.9616, 627.6147, 104.9229, 20.3853] |
| nodes.shape_328 | 1 | 8 | diagramCompact | [457.1471, 266.8471, 56.6142, 17.5] |
| nodes.shape_329 | 1 | 21 | diagramCompact | [708.7413, 266.8471, 133.761, 17.5] |
| nodes.shape_330 | 1 | 15 | diagramCompact | [435.9102, 417.5451, 99.0775, 17.5] |
| nodes.shape_331 | 1 | 8 | diagramCompact | [457.1471, 566.1299, 56.6142, 17.5] |
| nodes.shape_332 | 1 | 13 | diagramCompact | [733.1533, 454.6887, 84.9266, 17.5] |
| nodes.shape_335 | 1 | 8 | diagramMicro | [397.0319, 306.8427, 22.6457, 31.4243] |
| nodes.shape_344 | 1 | 16 | diagramMicro | [462.8032, 306.8427, 45.2914, 31.4243] |
| nodes.shape_345 | 1 | 16 | diagramMicro | [539.8974, 306.8427, 45.2914, 31.4243] |
| nodes.shape_349 | 1 | 12 | diagramMicro | [391.3652, 457.5407, 33.9685, 31.4243] |
| nodes.shape_350 | 1 | 18 | diagramMicro | [460.238, 457.5407, 50.4219, 31.4243] |
| nodes.shape_351 | 1 | 18 | diagramMicro | [537.3322, 457.5407, 50.4219, 31.4243] |
| nodes.shape_358 | 1 | 20 | diagramMicro | [669.821, 305.9491, 56.9717, 31.4243] |
| nodes.shape_359 | 1 | 16 | diagramMicro | [752.7606, 305.9491, 45.2914, 31.4243] |
| nodes.shape_360 | 1 | 16 | diagramMicro | [829.8548, 305.9491, 45.2914, 31.4243] |
| nodes.shape_363 | 1 | 16 | diagramMicro | [675.6664, 364.1193, 45.2914, 31.4243] |
| nodes.shape_364 | 1 | 16 | diagramMicro | [752.7606, 364.1193, 45.2914, 31.4243] |
| nodes.shape_365 | 1 | 16 | diagramMicro | [829.8548, 364.1193, 45.2914, 31.4243] |
| nodes.shape_368 | 1 | 16 | diagramMicro | [675.6664, 493.9798, 45.2914, 31.4243] |
| nodes.shape_369 | 1 | 16 | diagramMicro | [752.7606, 493.9798, 45.2914, 31.4243] |
| nodes.shape_370 | 1 | 16 | diagramMicro | [829.8548, 493.9798, 45.2914, 31.4243] |
| nodes.shape_374 | 1 | 16 | diagramMicro | [675.6664, 552.1606, 45.2914, 31.4243] |
| nodes.shape_375 | 1 | 16 | diagramMicro | [752.7606, 552.1606, 45.2914, 31.4243] |
| nodes.shape_376 | 1 | 16 | diagramMicro | [829.8548, 552.1606, 45.2914, 31.4243] |
| nodes.shape_377 | 1 | 13 | diagramCompact | [952.8817, 266.8471, 84.9266, 17.5] |
### page-17

左全面/开放/隐私3原则；右联邦学习、多模态/图学习、图像/文本/语音视频3能力、应用模型、算法底座

Layout为`source-architecture-17`，原型为`templates/prototypes/source-architecture-17.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_256 | 1 | 4 | body | [112.3503, 217.5966, 44.5424, 30.0] |
| nodes.shape_258 | 1 | 30 | caption | [112.3503, 256.9521, 220.0754, 20.0] |
| nodes.shape_259 | 1 | 4 | body | [112.3503, 359.6401, 44.5424, 30.0] |
| nodes.shape_261 | 1 | 82 | caption | [112.3503, 399.5626, 298.6717, 43.6278] |
| nodes.shape_262 | 1 | 8 | body | [112.3503, 529.4812, 89.0751, 30.0] |
| nodes.shape_264 | 1 | 30 | caption | [112.3503, 568.8367, 220.0754, 20.0] |
| nodes.shape_265 | 1 | 12 | caption | [515.6354, 336.8452, 24.3047, 94.3194] |
| nodes.shape_267 | 1 | 8 | caption | [854.3933, 150.8695, 62.8731, 20.0] |
| nodes.shape_268 | 1 | 10 | diagramCompact | [851.202, 270.1647, 69.2655, 17.5] |
| nodes.shape_269 | 1 | 13 | diagramCompact | [1054.0851, 270.1647, 82.5271, 17.5] |
| nodes.shape_270 | 1 | 10 | diagramCompact | [641.693, 270.1647, 69.2655, 17.5] |
| nodes.shape_271 | 1 | 8 | diagramCompact | [626.7579, 522.494, 55.0213, 17.5] |
| nodes.shape_272 | 1 | 8 | diagramCompact | [626.7579, 591.8957, 55.0213, 17.5] |
| nodes.shape_274 | 1 | 10 | caption | [701.2386, 209.8994, 78.5963, 20.0] |
| nodes.shape_275 | 1 | 6 | caption | [1007.5578, 209.8994, 47.1597, 20.0] |
| nodes.shape_277 | 1 | 8 | diagramMicro | [653.067, 325.2587, 47.1597, 15.0] |
| nodes.shape_279 | 1 | 8 | diagramMicro | [653.067, 366.7752, 47.1597, 15.0] |
| nodes.shape_282 | 1 | 8 | diagramMicro | [653.067, 408.282, 47.1597, 15.0] |
| nodes.shape_283 | 1 | 13 | diagramMicro | [639.8054, 449.7985, 73.6828, 15.0] |
| nodes.shape_333 | 1 | 8 | diagramMicro | [812.9644, 325.2587, 47.1597, 15.0] |
| nodes.shape_334 | 1 | 8 | diagramMicro | [812.9644, 366.7752, 47.1597, 15.0] |
| nodes.shape_336 | 1 | 8 | diagramMicro | [812.9644, 408.282, 47.1597, 15.0] |
| nodes.shape_337 | 1 | 8 | diagramMicro | [812.9644, 449.7985, 47.1597, 15.0] |
| nodes.shape_338 | 1 | 8 | diagramMicro | [912.207, 325.2587, 47.1597, 15.0] |
| nodes.shape_339 | 1 | 8 | diagramMicro | [912.207, 366.7752, 47.1597, 15.0] |
| nodes.shape_340 | 1 | 8 | diagramMicro | [912.207, 408.282, 47.1597, 15.0] |
| nodes.shape_341 | 1 | 4 | diagramMicro | [923.4156, 449.7985, 24.7231, 15.0] |
| nodes.shape_342 | 1 | 8 | diagramMicro | [1072.0947, 325.2587, 47.1597, 15.0] |
| nodes.shape_343 | 1 | 8 | diagramMicro | [1072.0947, 366.7752, 47.1597, 15.0] |
| nodes.shape_346 | 1 | 8 | diagramMicro | [1072.0947, 408.282, 47.1597, 15.0] |
| nodes.shape_352 | 1 | 7 | diagramMicro | [714.0623, 523.7488, 41.9154, 15.0] |
| nodes.shape_353 | 1 | 9 | diagramMicro | [796.0737, 523.7488, 52.3943, 15.0] |
| nodes.shape_354 | 1 | 9 | diagramMicro | [905.046, 523.7488, 52.3943, 15.0] |
| nodes.shape_355 | 1 | 7 | diagramMicro | [1018.601, 523.7488, 41.9154, 15.0] |
| nodes.shape_356 | 1 | 12 | diagramMicro | [992.7881, 593.1506, 66.3174, 15.0] |
| nodes.shape_357 | 1 | 7 | diagramMicro | [1078.9249, 593.1506, 41.9154, 15.0] |
| nodes.shape_378 | 1 | 4 | diagramMicro | [937.7766, 593.1506, 23.9058, 15.0] |
| nodes.shape_379 | 1 | 4 | diagramMicro | [874.3197, 593.1506, 23.9058, 15.0] |
| nodes.shape_380 | 1 | 7 | diagramMicro | [788.6597, 593.1506, 41.9154, 15.0] |
| nodes.shape_381 | 1 | 4 | diagramMicro | [722.6633, 593.1506, 24.7231, 15.0] |
### page-18

创意→定向→投放→转化→线索5阶段；底部全域数据/跨方资源/转化链3块向左回流；外部总回路

Layout为`source-architecture-18`，原型为`templates/prototypes/source-architecture-18.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_280 | 1 | 98 | caption | [286.2567, 120, 707.4866, 26.0869] |
| nodes.shape_303 | 1 | 8 | diagramCompact | [213.9345, 240.0474, 53.1427, 17.5] |
| nodes.shape_304 | 1 | 8 | diagramCompact | [411.883, 240.0474, 53.1427, 17.5] |
| nodes.shape_305 | 1 | 8 | diagramCompact | [609.8403, 240.0474, 53.1427, 17.5] |
| nodes.shape_306 | 1 | 8 | diagramCompact | [807.7977, 240.0474, 53.1427, 17.5] |
| nodes.shape_307 | 1 | 8 | diagramCompact | [1005.7461, 240.0474, 53.1427, 17.5] |
| nodes.shape_308 | 1 | 8 | diagramMicro | [416.7182, 291.2421, 43.4812, 15.0] |
| nodes.shape_309 | 1 | 8 | diagramMicro | [816.8133, 291.2421, 43.4812, 15.0] |
| nodes.shape_310 | 1 | 8 | diagramMicro | [416.7182, 409.0548, 43.4812, 15.0] |
| nodes.shape_311 | 1 | 8 | diagramMicro | [816.8133, 409.0548, 43.4812, 15.0] |
| nodes.shape_312 | 1 | 94 | diagramCompact | [341.6689, 619.2138, 597.8552, 17.5] |
| nodes.shape_314 | 1 | 8 | diagramMicro | [219.3618, 334.8982, 43.4812, 15.0] |
| nodes.shape_315 | 1 | 8 | diagramMicro | [219.3618, 416.2269, 43.4812, 15.0] |
| nodes.shape_316 | 1 | 8 | diagramMicro | [617.0618, 309.7801, 43.4812, 15.0] |
| nodes.shape_317 | 1 | 8 | diagramMicro | [617.0618, 381.546, 43.4812, 15.0] |
| nodes.shape_318 | 1 | 8 | diagramMicro | [617.0618, 455.6982, 43.4812, 15.0] |
| nodes.shape_319 | 1 | 8 | diagramMicro | [1018.9511, 461.0807, 43.4812, 15.0] |
| nodes.shape_320 | 1 | 8 | diagramMicro | [1018.9511, 414.4328, 43.4812, 15.0] |
| nodes.shape_321 | 1 | 8 | diagramMicro | [1018.9511, 367.7849, 43.4812, 15.0] |
| nodes.shape_322 | 1 | 8 | diagramMicro | [1018.9511, 321.1371, 43.4812, 15.0] |
| nodes.shape_325 | 1 | 52 | diagramMicro | [239.2051, 538.7722, 144.9313, 36.0534] |
| nodes.shape_326 | 1 | 30 | diagramMicro | [602.5112, 538.7722, 84.5403, 36.0534] |
| nodes.shape_329 | 1 | 44 | diagramMicro | [917.5099, 538.7722, 120.7821, 36.0534] |
| nodes.shape_330 | 1 | 6 | diagramMicro | [379.687, 327.7171, 32.6087, 15.0] |
| nodes.shape_331 | 1 | 4 | diagramMicro | [470.0493, 327.7171, 21.7361, 15.0] |
| nodes.shape_332 | 1 | 4 | diagramMicro | [385.1232, 360.6128, 21.7361, 15.0] |
| nodes.shape_335 | 1 | 4 | diagramMicro | [470.0493, 360.6128, 21.7361, 15.0] |
| nodes.shape_344 | 1 | 8 | diagramMicro | [416.7182, 445.5388, 43.4812, 15.0] |
| nodes.shape_345 | 1 | 10 | diagramMicro | [411.2819, 480.2197, 54.3537, 15.0] |
| nodes.shape_347 | 1 | 20 | diagramMicro | [186.4482, 368.5699, 108.6985, 15.0] |
| nodes.shape_348 | 1 | 24 | diagramMicro | [572.0915, 338.9754, 130.4436, 15.0] |
| nodes.shape_350 | 1 | 24 | diagramMicro | [572.0915, 412.6431, 130.4436, 15.0] |
| nodes.shape_358 | 1 | 8 | diagramMicro | [773.5923, 327.7171, 44.9883, 15.0] |
| nodes.shape_359 | 1 | 8 | diagramMicro | [773.5923, 360.6128, 44.9883, 15.0] |
| nodes.shape_360 | 1 | 8 | diagramMicro | [859.2719, 327.7171, 43.4812, 15.0] |
| nodes.shape_361 | 1 | 4 | diagramMicro | [870.1444, 360.6128, 21.7361, 15.0] |
| nodes.shape_362 | 1 | 4 | diagramMicro | [785.2184, 480.2197, 21.7361, 15.0] |
| nodes.shape_363 | 1 | 6 | diagramMicro | [864.7081, 480.2197, 32.6087, 15.0] |
| nodes.shape_364 | 1 | 3 | diagramMicro | [885.3498, 445.5388, 19.628, 15.0] |
| nodes.shape_365 | 1 | 4 | diagramMicro | [827.6859, 445.5388, 21.7361, 15.0] |
| nodes.shape_366 | 1 | 4 | diagramMicro | [771.0625, 445.5388, 21.7361, 15.0] |
### page-19

上方3业务域；中间数据平台/APIs/数据治理与右安全标准竖栏；底部数据及行业赋能2块

Layout为`source-architecture-19`，原型为`templates/prototypes/source-architecture-19.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_226 | 1 | 318 | caption | [64.6448, 120, 1150.7001, 45.6415] |
| nodes.shape_227 | 1 | 8 | compactBody | [204.6767, 191.577, 72.2769, 25.0] |
| nodes.shape_228 | 1 | 8 | compactBody | [603.8564, 191.577, 72.2769, 25.0] |
| nodes.shape_229 | 1 | 8 | compactBody | [1003.0465, 191.577, 72.2769, 25.0] |
| nodes.shape_230 | 1 | 9 | diagramMicro | [83.6509, 476.687, 50.0394, 15.0108] |
| nodes.shape_231 | 1 | 9 | diagramMicro | [83.6509, 590.5997, 50.0394, 15.0108] |
| nodes.shape_233 | 1 | 9 | diagramMicro | [682.4308, 590.5997, 50.0394, 15.0108] |
| nodes.shape_234 | 1 | 9 | diagramMicro | [1162.6213, 457.5054, 17.4059, 53.374] |
| nodes.shape_235 | 1 | 9 | diagramMicro | [1205.2999, 457.5054, 17.4059, 53.374] |
| nodes.shape_236 | 1 | 16 | diagramMicro | [155.7316, 262.3548, 87.5664, 15.5786] |
| nodes.shape_237 | 1 | 13 | diagramMicro | [444.1783, 262.3548, 75.054, 15.5786] |
| nodes.shape_238 | 1 | 9 | diagramMicro | [773.2802, 262.3548, 50.0394, 15.5786] |
| nodes.shape_239 | 1 | 13 | diagramMicro | [1042.9583, 262.3548, 75.054, 15.5786] |
| nodes.shape_241 | 1 | 22 | diagramMicro | [281.1863, 302.5659, 118.8372, 15.0108] |
| nodes.shape_242 | 1 | 26 | diagramMicro | [866.6795, 302.5659, 145.4209, 15.0108] |
| nodes.shape_244 | 1 | 23 | diagramMicro | [89.9381, 341.6312, 125.0934, 16.7039] |
| nodes.shape_245 | 1 | 9 | diagramMicro | [315.5955, 341.6312, 50.0394, 16.7039] |
| nodes.shape_246 | 1 | 13 | diagramMicro | [491.2032, 341.6312, 75.054, 16.7039] |
| nodes.shape_247 | 1 | 11 | diagramMicro | [98.2178, 381.5533, 62.5519, 16.7039] |
| nodes.shape_248 | 1 | 9 | diagramMicro | [245.2182, 381.5533, 50.0394, 16.7039] |
| nodes.shape_250 | 1 | 9 | diagramMicro | [385.9625, 381.5533, 50.0394, 16.7039] |
| nodes.shape_251 | 1 | 13 | diagramMicro | [514.2046, 381.5533, 75.054, 16.7039] |
| nodes.shape_252 | 1 | 9 | diagramMicro | [688.6251, 361.5974, 50.0394, 16.7039] |
| nodes.shape_253 | 1 | 9 | diagramMicro | [801.4951, 361.5974, 50.0394, 16.7039] |
| nodes.shape_254 | 1 | 9 | diagramMicro | [914.3754, 361.5974, 50.0394, 16.7039] |
| nodes.shape_255 | 1 | 9 | diagramMicro | [1027.2454, 361.5974, 50.0394, 16.7039] |
| nodes.shape_256 | 1 | 2 | diagramMicro | [1158.4152, 361.5974, 13.44, 16.7039] |
| nodes.shape_257 | 1 | 8 | diagramMicro | [270.8729, 455.8846, 45.3421, 16.7039] |
| nodes.shape_258 | 1 | 9 | diagramMicro | [508.9085, 455.8846, 50.0394, 16.7039] |
| nodes.shape_259 | 1 | 9 | diagramMicro | [749.2774, 455.8846, 50.0394, 16.7039] |
| nodes.shape_261 | 1 | 9 | diagramMicro | [989.6462, 455.8846, 50.0394, 16.7039] |
| nodes.shape_262 | 1 | 9 | diagramMicro | [308.1314, 495.8067, 50.0394, 16.7039] |
| nodes.shape_263 | 1 | 11 | diagramMicro | [622.8316, 495.8067, 62.5519, 16.7039] |
| nodes.shape_264 | 1 | 9 | diagramMicro | [950.0441, 495.8067, 50.0394, 16.7039] |
| nodes.shape_265 | 1 | 23 | diagramMicro | [176.1211, 564.2534, 125.0934, 16.7039] |
| nodes.shape_266 | 1 | 18 | diagramMicro | [176.1211, 589.7532, 100.0788, 16.7039] |
| nodes.shape_267 | 1 | 34 | diagramMicro | [176.1211, 615.2426, 187.6452, 16.7039] |
| nodes.shape_268 | 1 | 54 | diagramMicro | [774.2919, 564.2534, 296.7574, 16.7039] |
| nodes.shape_269 | 1 | 60 | diagramMicro | [774.2919, 589.7532, 325.2511, 16.7039] |
| nodes.shape_270 | 1 | 20 | diagramMicro | [774.2919, 615.2426, 112.5809, 16.7039] |
### page-20

左个人成长4项、中央3个个体目标串联、右企业成长4项；数据设施支撑；底部反馈/协同标签

Layout为`source-architecture-20`，原型为`templates/prototypes/source-architecture-20.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_284 | 1 | 8 | compactBody | [97.269, 135.6435, 76.0936, 25.0] |
| nodes.shape_285 | 1 | 29 | compactBody | [506.8334, 135.6435, 266.3331, 25.0] |
| nodes.shape_287 | 1 | 8 | compactBody | [1106.6373, 135.6435, 76.0936, 25.0] |
| nodes.shape_288 | 1 | 29 | compactBody | [506.8334, 607.3566, 266.3331, 25.0] |
| nodes.shape_289 | 1 | 33 | compactBody | [487.8127, 463.5221, 304.3745, 25.0] |
| nodes.shape_290 | 1 | 8 | caption | [105.6925, 205.8897, 58.5294, 20.0] |
| nodes.shape_291 | 1 | 8 | caption | [105.6925, 262.4083, 58.5294, 20.0] |
| nodes.shape_292 | 1 | 8 | caption | [105.6925, 318.927, 58.5294, 20.0] |
| nodes.shape_293 | 1 | 8 | caption | [105.6925, 375.4456, 58.5294, 20.0] |
| nodes.shape_294 | 1 | 6 | caption | [1122.3646, 205.8897, 43.8998, 20.0] |
| nodes.shape_295 | 1 | 8 | caption | [1115.0498, 262.4083, 58.5294, 20.0] |
| nodes.shape_296 | 1 | 8 | caption | [1115.0498, 318.927, 58.5294, 20.0] |
| nodes.shape_297 | 1 | 8 | caption | [1115.0498, 375.4456, 58.5294, 20.0] |
| nodes.shape_298 | 1 | 8 | diagramCompact | [102.0948, 539.7301, 52.6819, 17.5] |
| nodes.shape_299 | 1 | 8 | diagramCompact | [272.3789, 539.7301, 52.6819, 17.5] |
| nodes.shape_300 | 1 | 8 | diagramCompact | [442.6521, 539.7301, 52.6819, 17.5] |
| nodes.shape_301 | 1 | 8 | diagramCompact | [612.9362, 539.7301, 52.6819, 17.5] |
| nodes.shape_302 | 1 | 8 | diagramCompact | [783.2203, 539.7301, 52.6819, 17.5] |
| nodes.shape_303 | 1 | 8 | diagramCompact | [953.4935, 539.7301, 52.6819, 17.5] |
| nodes.shape_304 | 1 | 8 | diagramCompact | [1123.7776, 539.7301, 52.6819, 17.5] |
| nodes.shape_305 | 1 | 12 | caption | [277.2808, 211.3242, 87.7995, 20.0] |
| nodes.shape_306 | 1 | 12 | caption | [914.9196, 211.3242, 87.7995, 20.0] |
| nodes.shape_307 | 1 | 12 | caption | [596.1002, 211.3242, 87.7995, 20.0] |
| nodes.shape_308 | 1 | 7 | diagramMicro | [301.0513, 249.3277, 40.976, 15.0] |
| nodes.shape_309 | 1 | 7 | diagramMicro | [301.0513, 284.1084, 40.976, 15.0] |
| nodes.shape_310 | 1 | 7 | diagramMicro | [301.0513, 318.8891, 40.976, 15.0] |
| nodes.shape_311 | 1 | 7 | diagramMicro | [301.0513, 353.6697, 40.976, 15.0] |
| nodes.shape_312 | 1 | 7 | diagramMicro | [301.0513, 388.4504, 40.976, 15.0] |
| nodes.shape_313 | 1 | 11 | diagramMicro | [609.6321, 249.3277, 61.464, 15.0] |
| nodes.shape_314 | 1 | 11 | diagramMicro | [609.6321, 284.1084, 61.464, 15.0] |
| nodes.shape_315 | 1 | 11 | diagramMicro | [609.6321, 318.8891, 61.464, 15.0] |
| nodes.shape_316 | 1 | 11 | diagramMicro | [609.6321, 353.6697, 61.464, 15.0] |
| nodes.shape_317 | 1 | 11 | diagramMicro | [609.6321, 388.4504, 61.464, 15.0] |
| nodes.shape_318 | 1 | 7 | diagramMicro | [938.7009, 249.3277, 40.976, 15.0] |
| nodes.shape_319 | 1 | 7 | diagramMicro | [938.7009, 284.1084, 40.976, 15.0] |
| nodes.shape_320 | 1 | 7 | diagramMicro | [938.7009, 318.8891, 40.976, 15.0] |
| nodes.shape_321 | 1 | 7 | diagramMicro | [938.7009, 353.6697, 40.976, 15.0] |
| nodes.shape_322 | 1 | 7 | diagramMicro | [938.7009, 388.4504, 40.976, 15.0] |
| nodes.shape_324 | 1 | 4 | caption | [465.7704, 286.4184, 29.6288, 38.6283] |
| nodes.shape_325 | 1 | 4 | caption | [784.5898, 286.4184, 29.6288, 38.6283] |
### page-21

上方组织/流程/能力3条件；中部生成→探索分析→输出；下方10类业务数据2行

Layout为`source-architecture-21`，原型为`templates/prototypes/source-architecture-21.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_199 | 1 | 38 | caption | [501.222, 191.0328, 276.8935, 20.764] |
| nodes.shape_203 | 1 | 38 | caption | [501.222, 384.1681, 276.8935, 20.764] |
| nodes.shape_204 | 1 | 14 | diagramCompact | [202.5164, 257.597, 93.1811, 17.5] |
| nodes.shape_208 | 1 | 19 | diagramCompact | [579.7596, 257.597, 119.8085, 17.5] |
| nodes.shape_209 | 1 | 19 | diagramCompact | [970.3213, 257.597, 119.8085, 17.5] |
| nodes.shape_211 | 1 | 11 | diagramMicro | [210.2584, 452.6348, 59.9092, 15.0] |
| nodes.shape_213 | 1 | 15 | diagramMicro | [598.0616, 452.6348, 83.867, 15.0] |
| nodes.shape_215 | 1 | 13 | diagramMicro | [1003.8503, 452.6348, 71.8831, 15.0] |
| nodes.shape_216 | 1 | 21 | diagramMicro | [183.2948, 508.0056, 113.8166, 15.0] |
| nodes.shape_217 | 1 | 8 | diagramMicro | [616.0373, 508.0056, 47.9254, 15.0] |
| nodes.shape_218 | 1 | 15 | diagramMicro | [997.8584, 508.0056, 83.867, 15.0] |
| nodes.shape_220 | 1 | 8 | diagramMicro | [143.7344, 302.3476, 47.9254, 15.0] |
| nodes.shape_221 | 1 | 8 | diagramMicro | [308.2054, 302.3476, 47.9254, 15.0] |
| nodes.shape_222 | 1 | 19 | diagramMicro | [586.0876, 302.3476, 107.8247, 15.0] |
| nodes.shape_223 | 1 | 13 | diagramMicro | [913.5366, 302.3476, 71.8831, 15.0] |
| nodes.shape_224 | 1 | 13 | diagramMicro | [1078.0076, 302.3476, 71.8831, 15.0] |
| nodes.shape_225 | 1 | 8 | diagramMicro | [156.262, 566.6739, 47.9254, 15.0] |
| nodes.shape_226 | 1 | 8 | diagramMicro | [386.3178, 566.6739, 47.9254, 15.0] |
| nodes.shape_228 | 1 | 8 | diagramMicro | [616.3636, 566.6739, 47.9254, 15.0] |
| nodes.shape_229 | 1 | 8 | diagramMicro | [846.4193, 566.6739, 47.9254, 15.0] |
| nodes.shape_230 | 1 | 8 | diagramMicro | [1076.475, 566.6739, 47.9254, 15.0] |
| nodes.shape_231 | 1 | 8 | diagramMicro | [156.262, 622.7072, 47.9254, 15.0] |
| nodes.shape_232 | 1 | 8 | diagramMicro | [386.3178, 622.7072, 47.9254, 15.0] |
| nodes.shape_233 | 1 | 8 | diagramMicro | [616.3636, 622.7072, 47.9254, 15.0] |
| nodes.shape_234 | 1 | 8 | diagramMicro | [846.4193, 622.7072, 47.9254, 15.0] |
| nodes.shape_236 | 1 | 8 | diagramMicro | [1076.475, 622.7072, 47.9254, 15.0] |
### page-22

左汇集→集成→应用3层；中部数据/应用模块2列；右开放共享贯穿；底部仓库

Layout为`source-architecture-22`，原型为`templates/prototypes/source-architecture-22.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_197 | 1 | 28 | compactBody | [514.2343, 146.3877, 253.424, 25.0] |
| nodes.shape_200 | 1 | 4 | compactBody | [61.9516, 253.9113, 36.2079, 46.4259] |
| nodes.shape_201 | 1 | 4 | compactBody | [61.9516, 430.4207, 36.2079, 46.4259] |
| nodes.shape_202 | 1 | 4 | compactBody | [61.9516, 569.3468, 36.2079, 46.4259] |
| nodes.shape_206 | 1 | 8 | compactBody | [1188.7445, 360.7974, 22.4, 118.1073] |
| nodes.shape_210 | 1 | 6 | diagramMicro | [303.1821, 218.5929, 37.7695, 15.0375] |
| nodes.shape_212 | 1 | 9 | diagramMicro | [296.9975, 320.6285, 50.1284, 15.0375] |
| nodes.shape_214 | 1 | 6 | diagramMicro | [305.1782, 395.092, 33.7671, 15.0375] |
| nodes.shape_219 | 1 | 7 | diagramMicro | [303.0891, 446.1201, 37.9453, 15.0375] |
| nodes.shape_227 | 1 | 4 | diagramMicro | [309.5322, 497.1379, 25.059, 15.0375] |
| nodes.shape_235 | 1 | 9 | diagramMicro | [296.9975, 585.0462, 50.1284, 15.0375] |
| nodes.shape_237 | 1 | 85 | diagramMicro | [562.5218, 585.0462, 463.6798, 15.0375] |
| nodes.shape_238 | 1 | 9 | diagramMicro | [515.9098, 267.5423, 50.1284, 15.0375] |
| nodes.shape_239 | 1 | 11 | diagramCompact | [584.7574, 220.6401, 69.6233, 17.5] |
| nodes.shape_240 | 1 | 11 | diagramCompact | [934.322, 220.6401, 69.6233, 17.5] |
| nodes.shape_241 | 1 | 9 | diagramMicro | [673.1104, 267.5423, 50.1284, 15.0375] |
| nodes.shape_242 | 1 | 13 | diagramMicro | [503.3751, 329.9364, 75.1874, 15.0375] |
| nodes.shape_243 | 1 | 9 | diagramMicro | [673.1104, 329.9364, 50.1284, 15.0375] |
| nodes.shape_244 | 1 | 96 | diagramMicro | [487.986, 393.4372, 263.1663, 32.1537] |
| nodes.shape_245 | 1 | 18 | diagramMicro | [840.405, 267.5423, 100.2568, 15.0375] |
| nodes.shape_246 | 1 | 18 | diagramMicro | [997.6056, 267.5423, 100.2568, 15.0375] |
| nodes.shape_247 | 1 | 30 | diagramMicro | [888.3718, 329.9364, 162.9095, 15.0375] |
| nodes.shape_248 | 1 | 18 | diagramMicro | [840.405, 391.648, 100.2568, 15.0375] |
| nodes.shape_249 | 1 | 13 | diagramMicro | [1010.1403, 391.648, 75.1874, 15.0375] |
| nodes.shape_250 | 1 | 13 | diagramMicro | [852.9396, 453.7009, 75.1874, 15.0375] |
| nodes.shape_251 | 1 | 13 | diagramMicro | [1010.1403, 453.7009, 75.1874, 15.0375] |
### page-23

顶部7行业应用；中部HR/采购供应链/物流3流程；底部签约平台与企业系统双向连接；基础部署4方式

Layout为`source-architecture-23`，原型为`templates/prototypes/source-architecture-23.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_322 | 1 | 15 | caption | [57.9539, 143.9598, 23.4599, 100.0968] |
| nodes.shape_323 | 1 | 12 | caption | [57.9539, 300.5895, 23.4599, 80.0754] |
| nodes.shape_324 | 1 | 21 | caption | [57.6028, 460.5543, 23.4599, 140.1293] |
| nodes.shape_325 | 1 | 6 | diagramMicro | [160.7044, 130.743, 37.5337, 15.0135] |
| nodes.shape_326 | 1 | 6 | diagramMicro | [323.168, 130.743, 37.5337, 15.0135] |
| nodes.shape_327 | 1 | 4 | diagramMicro | [491.8787, 130.712, 25.019, 15.0135] |
| nodes.shape_328 | 1 | 4 | diagramMicro | [654.332, 130.743, 25.019, 15.0135] |
| nodes.shape_329 | 1 | 9 | diagramMicro | [804.281, 130.743, 50.0484, 15.0135] |
| nodes.shape_330 | 1 | 4 | diagramMicro | [979.249, 130.743, 25.019, 15.0135] |
| nodes.shape_331 | 1 | 6 | diagramMicro | [1135.445, 130.743, 37.5337, 15.0135] |
| nodes.shape_337 | 1 | 13 | diagramMicro | [249.3294, 306.2789, 75.0674, 15.0135] |
| nodes.shape_338 | 1 | 16 | diagramMicro | [623.7475, 306.2789, 87.5821, 15.0135] |
| nodes.shape_339 | 1 | 9 | diagramMicro | [1034.2021, 306.2789, 50.0484, 15.0135] |
| nodes.shape_340 | 1 | 8 | diagramMicro | [125.5662, 360.6656, 44.4829, 15.0] |
| nodes.shape_341 | 1 | 8 | diagramMicro | [218.497, 360.6656, 44.4829, 15.0] |
| nodes.shape_342 | 1 | 8 | diagramMicro | [311.4278, 360.6656, 44.4829, 15.0] |
| nodes.shape_343 | 1 | 8 | diagramMicro | [404.3586, 360.6656, 44.4829, 15.0] |
| nodes.shape_344 | 1 | 8 | diagramMicro | [500.7278, 360.6656, 44.4829, 15.0] |
| nodes.shape_345 | 1 | 8 | diagramMicro | [592.2853, 360.6656, 44.4829, 15.0] |
| nodes.shape_346 | 1 | 8 | diagramMicro | [686.5997, 360.6656, 44.4829, 15.0] |
| nodes.shape_347 | 1 | 10 | diagramMicro | [779.4685, 360.6656, 55.6036, 15.0] |
| nodes.shape_348 | 1 | 8 | diagramMicro | [892.4207, 360.6656, 44.4829, 15.0] |
| nodes.shape_349 | 1 | 8 | diagramMicro | [985.3515, 360.6656, 44.4829, 15.0] |
| nodes.shape_350 | 1 | 6 | diagramMicro | [1078.3339, 360.6656, 33.3622, 15.0] |
| nodes.shape_351 | 1 | 8 | diagramMicro | [1160.1956, 360.6656, 44.4829, 15.0] |
| nodes.shape_352 | 1 | 9 | diagramMicro | [139.6504, 452.903, 50.0484, 15.0135] |
| nodes.shape_353 | 1 | 9 | diagramMicro | [255.69, 452.903, 50.0484, 15.0135] |
| nodes.shape_354 | 1 | 9 | diagramMicro | [368.1982, 452.903, 50.0484, 15.0135] |
| nodes.shape_355 | 1 | 9 | diagramMicro | [483.8454, 452.903, 50.0484, 15.0135] |
| nodes.shape_356 | 1 | 9 | diagramMicro | [599.4926, 452.903, 50.0484, 15.0135] |
| nodes.shape_357 | 1 | 9 | diagramMicro | [715.1397, 452.903, 50.0484, 15.0135] |
| nodes.shape_358 | 1 | 23 | diagramMicro | [389.8614, 508.6615, 125.1158, 15.0135] |
| nodes.shape_359 | 1 | 9 | diagramMicro | [907.5374, 471.4892, 50.0484, 15.0135] |
| nodes.shape_360 | 1 | 8 | diagramMicro | [1031.8169, 471.4892, 43.791, 15.0135] |
| nodes.shape_361 | 1 | 9 | diagramMicro | [1146.6483, 471.4892, 52.3097, 15.0135] |
| nodes.shape_362 | 1 | 7 | diagramMicro | [911.2753, 525.1825, 42.5726, 15.0135] |
| nodes.shape_363 | 1 | 9 | diagramMicro | [1026.9535, 525.1825, 53.5178, 15.0135] |
| nodes.shape_364 | 1 | 9 | diagramMicro | [1147.7842, 525.1825, 50.0484, 15.0135] |
| nodes.shape_365 | 1 | 13 | diagramCompact | [1011.3205, 432.072, 83.4105, 17.5] |
| nodes.shape_366 | 1 | 25 | diagramMicro | [744.3097, 602.9656, 137.6305, 15.0135] |
| nodes.shape_367 | 1 | 18 | diagramMicro | [470.515, 602.9656, 100.0968, 15.0135] |
| nodes.shape_368 | 1 | 6 | diagramMicro | [225.4255, 602.9656, 35.4479, 15.0135] |
| nodes.shape_369 | 1 | 11 | diagramMicro | [1064.0845, 602.9656, 62.5631, 15.0135] |
| nodes.shape_370 | 1 | 8 | diagramMicro | [1131.9756, 164.7469, 44.4829, 15.0] |
| nodes.shape_371 | 1 | 8 | diagramMicro | [1131.7175, 189.1257, 45.0095, 15.0] |
| nodes.shape_375 | 1 | 8 | diagramMicro | [969.5223, 164.7469, 44.4829, 15.0] |
| nodes.shape_376 | 1 | 8 | diagramMicro | [969.5223, 189.1257, 44.4829, 15.0] |
| nodes.shape_377 | 1 | 6 | diagramMicro | [975.0775, 213.4943, 33.3622, 15.0] |
| nodes.shape_378 | 1 | 10 | diagramMicro | [963.9567, 237.8731, 55.6036, 15.0] |
| nodes.shape_379 | 1 | 6 | diagramMicro | [812.6241, 164.7469, 33.3622, 15.0] |
| nodes.shape_380 | 1 | 10 | diagramMicro | [801.5034, 189.1257, 55.6036, 15.0] |
| nodes.shape_381 | 1 | 8 | diagramMicro | [807.0586, 213.4943, 44.4829, 15.0] |
| nodes.shape_382 | 1 | 8 | diagramMicro | [807.0586, 237.8731, 44.4829, 15.0] |
| nodes.shape_383 | 1 | 8 | diagramMicro | [644.6053, 164.7469, 44.4829, 15.0] |
| nodes.shape_384 | 1 | 8 | diagramMicro | [644.6053, 189.1257, 44.4829, 15.0] |
| nodes.shape_385 | 1 | 8 | diagramMicro | [644.6053, 213.4943, 44.4829, 15.0] |
| nodes.shape_386 | 1 | 8 | diagramMicro | [644.6053, 237.8731, 44.4829, 15.0] |
| nodes.shape_387 | 1 | 8 | diagramMicro | [482.152, 164.7469, 44.4829, 15.0] |
| nodes.shape_388 | 1 | 6 | diagramMicro | [487.7072, 189.1257, 33.3622, 15.0] |
| nodes.shape_389 | 1 | 8 | diagramMicro | [482.152, 213.4943, 44.4829, 15.0] |
| nodes.shape_390 | 1 | 8 | diagramMicro | [482.152, 237.8731, 44.4829, 15.0] |
| nodes.shape_391 | 1 | 8 | diagramMicro | [319.6883, 164.7469, 44.4829, 15.0] |
| nodes.shape_392 | 1 | 8 | diagramMicro | [319.6883, 189.1257, 44.4829, 15.0] |
| nodes.shape_393 | 1 | 8 | diagramMicro | [319.6883, 213.4943, 44.4829, 15.0] |
| nodes.shape_394 | 1 | 8 | diagramMicro | [319.6883, 237.8731, 44.4829, 15.0] |
| nodes.shape_395 | 1 | 8 | diagramMicro | [157.235, 164.7469, 44.4829, 15.0] |
| nodes.shape_396 | 1 | 8 | diagramMicro | [157.235, 189.1257, 44.4829, 15.0] |
| nodes.shape_397 | 1 | 8 | diagramMicro | [157.235, 213.4943, 44.4829, 15.0] |
| nodes.shape_398 | 1 | 8 | diagramMicro | [157.235, 237.8731, 44.4829, 15.0] |
### page-24

左开发平台、中央多端门户、右BI；流程运营横梁；下方ESB及8系统；上下双向箭头

Layout为`source-architecture-24`，原型为`templates/prototypes/source-architecture-24.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_91 | 1 | 20 | caption | [66.0909, 159.6197, 144.9266, 28.876] |
| nodes.shape_92 | 1 | 17 | caption | [567.0742, 159.6197, 129.3586, 28.876] |
| nodes.shape_93 | 1 | 26 | caption | [1032.4224, 159.6197, 190.7372, 28.876] |
| nodes.shape_94 | 1 | 20 | caption | [674.2108, 402.6848, 144.9266, 28.876] |
| nodes.shape_95 | 1 | 11 | caption | [97.2269, 227.0741, 82.6545, 28.876] |
| nodes.shape_96 | 1 | 13 | caption | [89.4481, 290.3448, 98.2225, 28.876] |
| nodes.shape_97 | 1 | 30 | caption | [81.0282, 352.3541, 114.7577, 53.9467] |
| nodes.shape_98 | 1 | 11 | caption | [97.2269, 440.2015, 82.6545, 28.876] |
| nodes.shape_99 | 1 | 15 | caption | [81.6589, 502.8415, 113.7906, 28.876] |
| nodes.shape_100 | 1 | 6 | caption | [304.2364, 570.0226, 49.9207, 28.876] |
| nodes.shape_101 | 1 | 11 | caption | [391.411, 570.0226, 82.6545, 28.876] |
| nodes.shape_102 | 1 | 11 | caption | [494.6056, 570.0226, 82.6545, 28.876] |
| nodes.shape_103 | 1 | 7 | caption | [610.9716, 570.0226, 54.8718, 28.876] |
| nodes.shape_104 | 1 | 11 | caption | [700.154, 570.0226, 82.6545, 28.876] |
| nodes.shape_105 | 1 | 11 | caption | [803.0543, 570.0226, 82.6545, 28.876] |
| nodes.shape_106 | 1 | 11 | caption | [906.291, 570.0226, 82.6545, 28.876] |
| nodes.shape_107 | 1 | 7 | caption | [1024.3178, 570.0226, 52.7589, 28.876] |
| nodes.shape_108 | 1 | 9 | caption | [1119.3342, 570.0226, 68.8525, 28.876] |
| nodes.shape_109 | 1 | 11 | caption | [1086.4637, 298.9015, 82.6545, 28.876] |
| nodes.shape_110 | 1 | 11 | caption | [1086.4637, 249.5274, 82.6545, 28.876] |
| nodes.shape_111 | 1 | 11 | caption | [1086.4637, 200.3636, 82.6545, 28.876] |
| nodes.shape_112 | 1 | 50 | caption | [447.3655, 282.2822, 362.8789, 28.876] |
| nodes.shape_113 | 1 | 28 | caption | [638.9015, 507.0462, 205.7796, 28.876] |
| nodes.shape_114 | 1 | 9 | caption | [355.6813, 213.4508, 67.0865, 28.876] |
| nodes.shape_115 | 1 | 12 | caption | [535.339, 212.9462, 87.6056, 28.876] |
| nodes.shape_116 | 1 | 11 | caption | [739.3631, 213.4508, 82.6545, 28.876] |
| nodes.shape_117 | 1 | 7 | caption | [921.0916, 213.4508, 51.5185, 28.876] |

## 使用步骤

1. 先确认材料确有本页型所表达的关系，选择`family=source-architecture`及兼容variant。
2. 提供完整content，按schema控制config。可选内容可留空，正文含义由实际汇报任务确定。
3. 执行validate和build，处理具体字段的长度、容量或字体测量错误。
4. 对生成项目执行check、export、inspect，并查看最终页面和所需编辑操作。

## 配置与tokens

本页型的config类型、可选值与默认值如下。

```json
{
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
  }
}
```

允许字段来自page-catalog.json与pages.schema.json。tokens控制全局几何、字阶、颜色、间距和线条。字号通过body_role选择已登记字阶。切换variant后重新校验输入容量。

## 来源与检查

来源为蓝色逻辑架构图.pptx，逐页结构见variants与来源索引。原始文件指纹及资产处理见asset-provenance.json。当前原型完成结构生成与文本测量，实际渲染和原生编辑范围以交付检查记录为准。

catalog指纹为`498fe133ea2d00699bb4c4ea5bc798e78130623b21eea5d3cc8cb10e125af78b`，tokens指纹为`2bb967b3a61bf7a4072665f712f39ac49458d22ebe9407f269236c21adc366f3`，参数schema指纹为`6981096e740f47c827294403dd132d6609fd537f46b15e8164c4b630b9822a61`。
