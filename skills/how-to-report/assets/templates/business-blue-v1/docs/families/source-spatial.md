# 立体结构逻辑图1122.pptx

立体层次与结构关系

类型为定性关系图，语义入口为`source-spatial`。

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

蓝色几何装饰封面，中央叠片标题框

Layout为`source-spatial-01`，原型为`templates/prototypes/source-spatial-01.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_38 | 1 | 172 | heading | [363.2913, 299.3587, 553.4247, 163.504] |
### page-02

立体漏斗/圆台上下椭圆；顶消费者与7业务触点；中供应链/金融；底技术与5能力；中上行、两侧下行箭头

Layout为`source-spatial-02`，原型为`templates/prototypes/source-spatial-02.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_202 | 1 | 11 | diagramMicro | [332.853, 444.6799, 62.8629, 23.5039] |
| nodes.shape_203 | 1 | 11 | diagramMicro | [332.853, 467.9412, 62.8629, 21.2723] |
| nodes.shape_204 | 1 | 11 | diagramMicro | [332.853, 509.0467, 62.8629, 21.2723] |
| nodes.shape_206 | 1 | 11 | diagramMicro | [332.853, 488.4939, 62.8629, 21.2723] |
| nodes.shape_28 | 1 | 14 | caption | [589.4631, 335.3186, 102.7637, 28.735] |
| nodes.shape_29 | 1 | 22 | diagramMicro | [579.4616, 355.1033, 122.7666, 18.2889] |
| nodes.shape_31 | 1 | 11 | caption | [596.8045, 440.516, 85.3399, 28.735] |
| nodes.shape_32 | 1 | 15 | diagramMicro | [598.6398, 460.3087, 81.6692, 18.2889] |
| nodes.shape_35 | 1 | 20 | caption | [561.8357, 548.333, 150.7902, 28.735] |
| nodes.shape_36 | 1 | 30 | diagramMicro | [555.1735, 568.1176, 164.1308, 18.2889] |
| nodes.shape_42 | 1 | 8 | diagramCompact | [610.9699, 146.4873, 54.8666, 23.5119] |
| nodes.shape_43 | 1 | 11 | diagramMicro | [605.1161, 162.0919, 60.5748, 18.2889] |
| nodes.shape_83 | 1 | 30 | caption | [217.7674, 436.918, 75.201, 62.7012] |
| nodes.shape_2 | 1 | 14 | caption | [181.222, 206.4395, 102.7637, 28.735] |
| nodes.shape_4 | 1 | 17 | diagramMicro | [191.1103, 227.3157, 95.2767, 19.5906] |
| nodes.shape_10 | 1 | 14 | caption | [348.2958, 166.1588, 102.7637, 28.735] |
| nodes.shape_11 | 1 | 21 | diagramMicro | [347.0345, 186.8328, 117.9963, 19.5906] |
| nodes.shape_13 | 1 | 11 | caption | [447.7688, 242.2249, 85.3399, 28.735] |
| nodes.shape_14 | 1 | 10 | diagramMicro | [460.9802, 260.8534, 56.3624, 19.5906] |
| nodes.shape_16 | 1 | 11 | caption | [732.8229, 245.4348, 85.3399, 28.735] |
| nodes.shape_17 | 1 | 15 | diagramMicro | [728.6509, 263.8368, 85.7523, 19.5906] |
| nodes.shape_19 | 1 | 11 | caption | [817.1117, 167.1775, 85.3399, 28.735] |
| nodes.shape_20 | 1 | 23 | diagramMicro | [795.5402, 188.0294, 128.4748, 19.5906] |
| nodes.shape_22 | 1 | 11 | caption | [889.5395, 229.24, 85.3399, 28.735] |
| nodes.shape_23 | 1 | 21 | diagramMicro | [875.3903, 247.6986, 113.6465, 19.5906] |
| nodes.shape_25 | 1 | 11 | caption | [990.387, 187.7626, 85.3399, 28.735] |
| nodes.shape_26 | 1 | 19 | diagramMicro | [981.1374, 207.4179, 103.8471, 19.5906] |
| nodes.shape_85 | 1 | 10 | diagramMicro | [230.8251, 329.0202, 56.233, 19.5906] |
| nodes.shape_88 | 1 | 10 | diagramMicro | [230.8251, 357.0437, 56.233, 19.5906] |
| nodes.shape_91 | 1 | 10 | diagramMicro | [230.8251, 385.0592, 56.233, 19.5906] |
| nodes.shape_94 | 1 | 10 | diagramMicro | [230.8251, 413.0827, 56.233, 19.5906] |
| nodes.shape_97 | 1 | 33 | diagramCompact | [980.6442, 436.2955, 75.201, 62.7012] |
| nodes.shape_99 | 1 | 10 | diagramMicro | [989.8049, 329.0202, 56.233, 19.5906] |
| nodes.shape_102 | 1 | 10 | diagramMicro | [989.8049, 357.0437, 56.233, 19.5906] |
| nodes.shape_105 | 1 | 10 | diagramMicro | [989.8049, 385.0592, 56.233, 19.5906] |
| nodes.shape_108 | 1 | 10 | diagramMicro | [989.8049, 413.0827, 56.233, 19.5906] |
| nodes.shape_130 | 1 | 24 | diagramCompact | [288.7641, 570.3734, 55.8045, 53.8964] |
| nodes.shape_131 | 1 | 24 | diagramCompact | [448.4399, 590.1419, 55.0283, 53.1525] |
| nodes.shape_132 | 1 | 24 | diagramCompact | [607.3477, 594.8475, 55.0283, 53.1525] |
| nodes.shape_133 | 1 | 24 | diagramCompact | [766.2554, 590.1419, 55.0283, 53.1525] |
| nodes.shape_134 | 1 | 24 | diagramCompact | [925.1632, 571.3275, 55.0283, 53.1525] |
| nodes.shape_167 | 1 | 11 | diagramMicro | [890.9302, 443.3297, 62.8629, 23.5119] |
| nodes.shape_168 | 1 | 11 | diagramMicro | [890.9302, 466.591, 62.8629, 21.2723] |
| nodes.shape_169 | 1 | 11 | diagramMicro | [890.9302, 507.6884, 62.8629, 21.2723] |
| nodes.shape_171 | 1 | 11 | diagramMicro | [890.9302, 487.1437, 62.8629, 21.2723] |
| nodes.shape_188 | 1 | 11 | diagramMicro | [818.6318, 435.2444, 62.8629, 23.5039] |
| nodes.shape_189 | 1 | 11 | diagramMicro | [818.6318, 458.5057, 62.8629, 21.2723] |
| nodes.shape_190 | 1 | 22 | diagramMicro | [818.6318, 499.6031, 62.8629, 35.3811] |
| nodes.shape_192 | 1 | 11 | diagramMicro | [818.6318, 479.0584, 62.8629, 21.2723] |
| nodes.shape_195 | 1 | 11 | diagramMicro | [404.4237, 438.2117, 62.8629, 23.5039] |
| nodes.shape_196 | 1 | 11 | diagramMicro | [404.4237, 461.473, 62.8629, 21.2723] |
| nodes.shape_197 | 1 | 11 | diagramMicro | [404.4237, 502.5785, 62.8629, 21.2723] |
| nodes.shape_199 | 1 | 11 | diagramMicro | [404.4237, 482.0257, 62.8629, 21.2723] |
| nodes.shape_236 | 1 | 10 | diagramCompact | [362.0327, 348.4976, 67.9243, 23.5119] |
| nodes.shape_239 | 1 | 10 | diagramCompact | [851.9996, 348.4976, 67.9243, 23.5119] |
| nodes.shape_242 | 1 | 10 | diagramCompact | [864.9361, 382.4557, 67.9243, 23.5119] |
| nodes.shape_245 | 1 | 10 | diagramCompact | [347.4792, 382.4557, 67.9243, 23.5119] |
### page-03

上生产力环，中人/货/实体空间，底商业生态多层椭圆；倒锥与竖向连接

Layout为`source-spatial-03`，原型为`templates/prototypes/source-spatial-03.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_66 | 1 | 87 | diagramMicro | [872.2419, 200.2784, 161.1542, 44.4856] |
| nodes.shape_67 | 1 | 84 | diagramMicro | [246.6039, 200.2784, 154.0545, 44.4856] |
| nodes.shape_69 | 1 | 19 | diagramCompact | [575.8994, 265.076, 120.3483, 25.048] |
| nodes.shape_97 | 1 | 19 | diagramCompact | [575.8994, 369.5192, 120.3483, 25.048] |
| nodes.shape_98 | 1 | 16 | caption | [289.7215, 333.7265, 120.3483, 27.8792] |
| nodes.shape_99 | 1 | 16 | caption | [866.4669, 333.7265, 120.3483, 27.8792] |
| nodes.shape_100 | 1 | 17 | diagramMicro | [389.5154, 319.7609, 95.3522, 19.5847] |
| nodes.shape_101 | 1 | 17 | diagramMicro | [415.3167, 338.6962, 95.3522, 19.5847] |
| nodes.shape_102 | 1 | 17 | diagramMicro | [446.9535, 319.7609, 95.3522, 19.5847] |
| nodes.shape_103 | 1 | 17 | diagramMicro | [446.9535, 353.7614, 95.3522, 19.5847] |
| nodes.shape_104 | 1 | 17 | diagramMicro | [389.5154, 353.7614, 95.3522, 19.5847] |
| nodes.shape_105 | 1 | 17 | diagramMicro | [768.1709, 363.9174, 95.3522, 19.5847] |
| nodes.shape_106 | 1 | 17 | diagramMicro | [799.3403, 334.0208, 95.3522, 19.5847] |
| nodes.shape_107 | 1 | 17 | diagramMicro | [733.5903, 347.1812, 95.3522, 19.5847] |
| nodes.shape_108 | 1 | 17 | diagramMicro | [756.1015, 331.8823, 95.3522, 19.5847] |
| nodes.shape_109 | 1 | 17 | diagramMicro | [726.9581, 319.7609, 95.3522, 19.5847] |
| nodes.shape_110 | 1 | 17 | diagramMicro | [752.2919, 306.1416, 95.3522, 19.5847] |
| nodes.shape_111 | 1 | 17 | diagramMicro | [781.617, 317.9686, 95.3522, 19.5847] |
| nodes.shape_112 | 1 | 17 | diagramMicro | [822.3104, 317.9686, 95.3522, 19.5847] |
| nodes.shape_113 | 1 | 17 | diagramMicro | [812.1543, 349.6055, 95.3522, 19.5847] |
| nodes.shape_115 | 1 | 50 | diagramCompact | [555.9856, 509.6081, 160.1758, 42.3816] |
| nodes.shape_117 | 1 | 22 | diagramMicro | [721.4689, 528.8292, 119.7162, 19.5847] |
| nodes.shape_118 | 1 | 22 | diagramMicro | [812.1543, 509.6081, 119.7162, 19.5847] |
| nodes.shape_119 | 1 | 22 | diagramMicro | [832.7001, 570.5009, 119.7162, 19.5847] |
| nodes.shape_120 | 1 | 22 | diagramMicro | [731.7461, 597.5749, 119.7162, 19.5847] |
| nodes.shape_121 | 1 | 22 | diagramMicro | [516.0456, 597.5749, 119.7162, 19.5847] |
| nodes.shape_122 | 1 | 22 | diagramMicro | [617.9174, 597.5749, 119.7162, 19.5847] |
| nodes.shape_123 | 1 | 22 | diagramMicro | [409.4291, 580.605, 119.7162, 19.5847] |
| nodes.shape_124 | 1 | 22 | diagramMicro | [309.8084, 565.1328, 119.7162, 19.5847] |
| nodes.shape_125 | 1 | 22 | diagramMicro | [356.675, 499.5041, 119.7162, 19.5847] |
| nodes.shape_126 | 1 | 19 | diagramCompact | [434.7715, 531.8249, 119.7162, 25.048] |
| nodes.shape_129 | 1 | 19 | diagramCompact | [271.8338, 454.4211, 120.3483, 25.048] |
| nodes.shape_130 | 1 | 30 | diagramMicro | [271.8338, 475.7807, 162.3144, 20.8921] |
| nodes.shape_131 | 1 | 19 | diagramCompact | [872.2419, 454.4211, 120.3483, 25.048] |
| nodes.shape_132 | 1 | 27 | diagramMicro | [844.2414, 476.6465, 148.8076, 20.8921] |
| nodes.shape_137 | 1 | 30 | diagramMicro | [375.8961, 200.1572, 81.2741, 33.5763] |
| nodes.shape_138 | 1 | 32 | diagramMicro | [815.8427, 200.1572, 91.6638, 33.5763] |
| nodes.shape_139 | 1 | 12 | diagramCompact | [595.4408, 193.6982, 81.2741, 25.1779] |
| nodes.shape_140 | 1 | 58 | diagramMicro | [556.3926, 160.2258, 159.3706, 33.5763] |
| nodes.shape_144 | 1 | 13 | diagramMicro | [421.0051, 426.0223, 71.2826, 20.8921] |
| nodes.shape_145 | 1 | 13 | diagramMicro | [787.6085, 424.6803, 71.2826, 20.8921] |
| nodes.shape_249 | 1 | 25 | diagramMicro | [566.8689, 566.9424, 138.4179, 22.2774] |
| nodes.shape_142 | 1 | 25 | diagramMicro | [566.8689, 623.4109, 138.4179, 22.2774] |
| nodes.shape_258 | 1 | 18 | diagramMicro | [585.8822, 450.9665, 100.7809, 20.8921] |
### page-04

顶智能生产增效上箭头；中智能/连接两椭圆；底运营降本下箭头；左右弧箭头

Layout为`source-spatial-04`，原型为`templates/prototypes/source-spatial-04.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_30 | 1 | 22 | diagramCompact | [952.0637, 289.3682, 70.0787, 47.4997] |
| nodes.shape_31 | 1 | 22 | diagramCompact | [874.1226, 298.0853, 70.0787, 47.4997] |
| nodes.shape_32 | 1 | 22 | diagramCompact | [705.421, 308.7424, 70.0787, 47.4997] |
| nodes.shape_33 | 1 | 22 | diagramCompact | [614.6606, 304.0163, 70.0787, 47.4997] |
| nodes.shape_34 | 1 | 22 | diagramCompact | [523.9002, 298.0853, 70.0787, 47.4997] |
| nodes.shape_35 | 1 | 22 | diagramCompact | [458.7783, 289.3682, 70.0787, 47.4997] |
| nodes.shape_36 | 1 | 7 | compactBody | [704.7458, 376.3683, 70.3607, 30.2535] |
| nodes.shape_37 | 1 | 7 | compactBody | [704.7458, 452.378, 70.3607, 30.2535] |
| nodes.shape_38 | 1 | 7 | caption | [711.8734, 519.8928, 52.4735, 27.5187] |
| nodes.shape_39 | 1 | 13 | caption | [809.7015, 531.7036, 99.6484, 27.5187] |
| nodes.shape_40 | 1 | 18 | diagramCompact | [967.3186, 575.1267, 61.447, 41.4233] |
| nodes.shape_41 | 1 | 18 | diagramCompact | [894.2744, 592.5011, 61.447, 41.4233] |
| nodes.shape_42 | 1 | 18 | diagramCompact | [821.6918, 600.6542, 61.447, 41.4233] |
| nodes.shape_43 | 1 | 18 | diagramCompact | [745.5709, 606.5767, 61.447, 41.4233] |
| nodes.shape_44 | 1 | 22 | diagramCompact | [648.7684, 606.5767, 71.5315, 41.4233] |
| nodes.shape_45 | 1 | 18 | diagramCompact | [574.7072, 600.6542, 61.447, 41.4233] |
| nodes.shape_46 | 1 | 18 | diagramCompact | [503.2013, 592.5011, 61.447, 41.4233] |
| nodes.shape_47 | 1 | 18 | diagramCompact | [444.9762, 575.1267, 61.447, 41.4233] |
| nodes.shape_54 | 1 | 7 | caption | [711.8734, 231.7669, 52.4735, 27.5187] |
| nodes.shape_55 | 1 | 13 | caption | [790.2675, 245.8425, 99.6484, 27.5187] |
| nodes.shape_56 | 1 | 22 | diagramCompact | [796.1814, 304.0163, 70.0787, 47.4997] |
### page-05

上技术与行业/体系支持同一大圆盘，下方法论圆柱底座，中倒锥连接

Layout为`source-spatial-05`，原型为`templates/prototypes/source-spatial-05.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_39 | 1 | 30 | heading | [455.7662, 482.5701, 382.6105, 52.031] |
| nodes.shape_40 | 1 | 53 | caption | [455.7662, 526.1385, 382.6105, 34.9707] |
| nodes.shape_51 | 1 | 30 | heading | [452.7135, 233.37, 382.6105, 52.031] |
| nodes.shape_52 | 1 | 53 | caption | [452.7135, 276.9384, 382.6105, 34.9707] |
| nodes.shape_53 | 1 | 82 | compactBody | [460.2776, 321.0286, 371.5783, 53.0647] |
| nodes.shape_54 | 1 | 33 | diagramMicro | [950.7949, 469.3256, 179.8093, 28.5659] |
| nodes.shape_55 | 1 | 39 | diagramMicro | [132.973, 469.3256, 212.6644, 28.5659] |
| nodes.shape_56 | 1 | 30 | heading | [849.3895, 416.8696, 382.6105, 52.031] |
| nodes.shape_57 | 1 | 30 | heading | [48, 418.6471, 382.6105, 52.031] |
| nodes.shape_31 | 1 | 57 | body | [335.2815, 126.6803, 618.4309, 37.4631] |
### page-06

卓越/安全/开放3层悬浮椭圆；中间环路节点；左需求到IP6步骤；右版本输出

Layout为`source-spatial-06`，原型为`templates/prototypes/source-spatial-06.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_10 | 1 | 14 | caption | [61.5466, 277.6886, 105.6494, 28.5835] |
| nodes.shape_11 | 1 | 14 | caption | [61.5466, 324.9853, 105.6494, 28.5835] |
| nodes.shape_12 | 1 | 14 | caption | [61.5466, 371.4916, 105.6494, 28.5835] |
| nodes.shape_13 | 1 | 14 | caption | [61.5466, 419.9048, 105.6494, 28.5835] |
| nodes.shape_14 | 1 | 14 | caption | [61.5466, 468.2488, 105.6494, 28.5835] |
| nodes.shape_15 | 1 | 14 | caption | [61.5466, 511.5242, 105.6494, 28.5835] |
| nodes.shape_23 | 1 | 16 | caption | [404.46, 230.2042, 116.2608, 28.5835] |
| nodes.shape_24 | 1 | 16 | caption | [392.1394, 299.6228, 116.2608, 28.5835] |
| nodes.shape_25 | 1 | 16 | caption | [283.9804, 377.3506, 116.2608, 28.5835] |
| nodes.shape_26 | 1 | 16 | caption | [383.3756, 421.8117, 116.2608, 28.5835] |
| nodes.shape_27 | 1 | 16 | caption | [383.3756, 567.97, 116.2608, 28.5835] |
| nodes.shape_28 | 1 | 16 | caption | [479.4807, 531.5515, 116.2608, 28.5835] |
| nodes.shape_29 | 1 | 16 | caption | [482.346, 591.2874, 116.2608, 28.5835] |
| nodes.shape_30 | 1 | 20 | caption | [724.5106, 576.0718, 147.344, 28.5835] |
| nodes.shape_31 | 1 | 16 | caption | [690.1966, 531.5515, 116.2608, 28.5835] |
| nodes.shape_32 | 1 | 16 | caption | [819.2918, 421.8117, 116.2608, 28.5835] |
| nodes.shape_33 | 1 | 16 | caption | [871.7954, 377.3506, 116.2608, 28.5835] |
| nodes.shape_34 | 1 | 16 | caption | [755.6037, 224.0784, 116.2608, 28.5835] |
| nodes.shape_35 | 1 | 16 | caption | [805.331, 312.141, 116.2608, 28.5835] |
| nodes.shape_36 | 1 | 16 | caption | [583.8852, 334.9347, 116.2608, 28.5835] |
| nodes.shape_37 | 1 | 30 | heading | [545.3522, 209.8509, 195.5003, 81.2847] |
| nodes.shape_38 | 1 | 30 | heading | [545.3522, 379.2575, 195.5003, 81.2847] |
| nodes.shape_39 | 1 | 30 | heading | [545.3522, 534.0413, 195.5003, 81.2847] |
| nodes.shape_50 | 1 | 10 | heading | [1081.1873, 383.2787, 137.2662, 41.3686] |
| nodes.shape_51 | 1 | 58 | body | [319.2825, 120, 632.5033, 38.3156] |
### page-07

6指标2×3卡置于立体环上；下方4项能力收益

Layout为`source-spatial-07`，原型为`templates/prototypes/source-spatial-07.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_90 | 1 | 42 | compactBody | [447.6535, 179.4348, 384.6844, 32.7537] |
| nodes.shape_91 | 1 | 11 | compactBody | [301.098, 550.5014, 103.3633, 32.7537] |
| nodes.shape_92 | 1 | 52 | diagramCompact | [268.1711, 581.1933, 169.2084, 46.6486] |
| nodes.shape_95 | 1 | 11 | compactBody | [492.5782, 550.5014, 103.3633, 32.7537] |
| nodes.shape_96 | 1 | 52 | diagramCompact | [459.6513, 581.1933, 169.2084, 46.6486] |
| nodes.shape_97 | 1 | 11 | compactBody | [684.0585, 550.5014, 103.3633, 32.7537] |
| nodes.shape_98 | 1 | 52 | diagramCompact | [651.1316, 581.1933, 169.2084, 46.6486] |
| nodes.shape_101 | 1 | 11 | compactBody | [875.5387, 550.5014, 103.3633, 32.7537] |
| nodes.shape_102 | 1 | 78 | diagramCompact | [842.6205, 581.1933, 169.2084, 66.8067] |
| nodes.shape_119 | 1 | 11 | caption | [423.1034, 280.4505, 85.1456, 29.4792] |
| nodes.shape_120 | 1 | 7 | heading | [406.8089, 244.5176, 77.2312, 49.1262] |
| nodes.shape_122 | 1 | 4 | caption | [490.0401, 261.5051, 35.1012, 27.8419] |
| nodes.shape_123 | 1 | 11 | caption | [597.8733, 280.4505, 84.9637, 29.4792] |
| nodes.shape_124 | 1 | 4 | heading | [599.8744, 244.5176, 38.7255, 49.1262] |
| nodes.shape_125 | 1 | 4 | caption | [644.5999, 261.5051, 35.1012, 27.8419] |
| nodes.shape_126 | 1 | 11 | caption | [772.8338, 280.4505, 84.9637, 29.4792] |
| nodes.shape_127 | 1 | 5 | heading | [766.5273, 244.5176, 55.6005, 49.1262] |
| nodes.shape_129 | 1 | 4 | caption | [828.1278, 261.5051, 35.1012, 27.8419] |
| nodes.shape_130 | 1 | 11 | caption | [422.7482, 369.425, 84.9637, 29.4792] |
| nodes.shape_131 | 1 | 5 | heading | [419.1792, 333.4922, 53.2355, 49.1262] |
| nodes.shape_132 | 1 | 4 | caption | [478.4147, 350.4797, 35.1012, 27.8419] |
| nodes.shape_133 | 1 | 9 | caption | [605.6784, 369.425, 68.6345, 29.4792] |
| nodes.shape_134 | 1 | 4 | heading | [597.6134, 333.4922, 42.4245, 49.1262] |
| nodes.shape_136 | 1 | 4 | caption | [646.0379, 350.4797, 35.1012, 27.8419] |
| nodes.shape_137 | 1 | 11 | caption | [772.288, 369.425, 84.9637, 29.4792] |
| nodes.shape_138 | 1 | 2 | heading | [776.7504, 333.4922, 18.9128, 49.1262] |
| nodes.shape_139 | 1 | 4 | caption | [801.6632, 350.4797, 50.5555, 27.8419] |
### page-08

标准模型底部环→机制中间环循环→测试工具顶部盘；中间任务/测评/分析闭环

Layout为`source-spatial-08`，原型为`templates/prototypes/source-spatial-08.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_5 | 1 | 21 | heading | [295.8584, 120, 265.8328, 35.0] |
| nodes.shape_8 | 1 | 57 | caption | [136.9197, 174.0717, 410.9407, 20.0] |
| nodes.shape_110 | 1 | 23 | compactBody | [590.7361, 544.816, 209.4455, 25.0] |
| nodes.shape_111 | 1 | 12 | diagramCompact | [652.3075, 630.5, 79.8707, 17.5] |
| nodes.shape_120 | 1 | 17 | diagramCompact | [956.0059, 545.384, 111.6333, 17.5] |
| nodes.shape_121 | 1 | 8 | diagramCompact | [380.4007, 550.5875, 50.4004, 17.5] |
| nodes.shape_122 | 1 | 8 | diagramCompact | [223.2029, 540.2095, 50.4004, 17.5] |
| nodes.shape_47 | 1 | 23 | compactBody | [581.451, 401.3911, 209.4455, 25.0] |
| nodes.shape_48 | 1 | 30 | diagramCompact | [586.6835, 426.3033, 191.7943, 17.5] |
| nodes.shape_51 | 1 | 11 | diagramCompact | [853.4642, 350.7752, 71.6786, 17.5] |
| nodes.shape_52 | 1 | 11 | diagramCompact | [650.3345, 336.8089, 71.6786, 17.5] |
| nodes.shape_56 | 1 | 12 | diagramCompact | [465.3009, 350.7752, 79.8707, 17.5] |
| nodes.shape_91 | 1 | 12 | diagramCompact | [429.0312, 439.5635, 79.8707, 17.5] |
| nodes.shape_95 | 1 | 12 | diagramCompact | [652.5783, 457.1857, 79.8707, 17.5] |
| nodes.shape_99 | 1 | 12 | diagramCompact | [884.2016, 437.3486, 79.8707, 17.5] |
| nodes.shape_118 | 1 | 17 | diagramCompact | [1034.8321, 456.2057, 111.6333, 31.25] |
| nodes.shape_124 | 1 | 8 | diagramCompact | [223.2029, 402.0074, 50.4004, 17.5] |
| nodes.shape_43 | 1 | 14 | compactBody | [623.1757, 268.9051, 131.0933, 25.0] |
| nodes.shape_126 | 1 | 8 | diagramCompact | [223.2029, 261.6581, 50.4004, 17.5] |
| nodes.shape_132 | 1 | 8 | diagramCompact | [380.4007, 272.0264, 50.4004, 17.5] |
### page-09

上GMV=人群×商品公式；左右生命周期环；中倒锥穿一环；下3驱动块

Layout为`source-spatial-09`，原型为`templates/prototypes/source-spatial-09.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_12 | 1 | 59 | body | [321.0494, 120, 640.0609, 38.7734] |
| nodes.shape_1080 | 1 | 66 | diagramCompact | [218.3469, 367.6678, 138.9763, 64.2391] |
| nodes.shape_1081 | 1 | 12 | diagramMicro | [164.1961, 390.8238, 67.4985, 22.6161] |
| nodes.shape_1082 | 1 | 12 | diagramMicro | [181.1032, 341.4922, 67.4985, 22.6161] |
| nodes.shape_1083 | 1 | 12 | diagramMicro | [251.5912, 303.1088, 67.4985, 22.6161] |
| nodes.shape_1084 | 1 | 12 | diagramMicro | [179.5435, 440.5454, 67.4985, 22.6161] |
| nodes.shape_1085 | 1 | 12 | diagramMicro | [251.5912, 476.3193, 67.4985, 22.6161] |
| nodes.shape_1086 | 1 | 12 | diagramMicro | [337.7765, 391.2138, 67.4985, 22.6161] |
| nodes.shape_1087 | 1 | 12 | diagramMicro | [326.0785, 341.8922, 67.4985, 22.6161] |
| nodes.shape_1088 | 1 | 12 | diagramMicro | [322.1092, 440.9453, 67.4985, 22.6161] |
| nodes.shape_1091 | 1 | 51 | diagramCompact | [944.1732, 370.8472, 112.8608, 64.2391] |
| nodes.shape_1092 | 1 | 18 | diagramMicro | [887.3529, 416.4195, 52.841, 35.5339] |
| nodes.shape_1093 | 1 | 12 | diagramMicro | [895.7314, 341.4922, 67.4985, 22.6161] |
| nodes.shape_1096 | 1 | 24 | diagramMicro | [966.2294, 476.3193, 67.4985, 35.5339] |
| nodes.shape_1098 | 1 | 24 | diagramMicro | [1040.7167, 341.4922, 67.4985, 35.5339] |
| nodes.shape_1099 | 1 | 20 | diagramMicro | [1052.5547, 416.4195, 59.0999, 35.5339] |
| nodes.shape_1139 | 1 | 44 | diagramCompact | [230.3748, 194.7673, 138.9763, 45.8222] |
| nodes.shape_1146 | 1 | 44 | diagramCompact | [610.0401, 194.5073, 138.9763, 45.8222] |
| nodes.shape_1149 | 1 | 44 | diagramCompact | [931.9953, 194.5073, 138.9763, 45.8222] |
| nodes.shape_1155 | 1 | 11 | body | [439.9491, 197.9567, 120.6094, 38.7734] |
| nodes.shape_1156 | 1 | 11 | body | [784.0605, 197.9567, 120.6094, 38.7734] |
| nodes.shape_1166 | 1 | 56 | caption | [183.5728, 582.4912, 203.3553, 47.6619] |
| nodes.shape_1174 | 1 | 56 | caption | [901.7204, 590.6098, 203.3553, 47.6619] |
| nodes.shape_1182 | 1 | 84 | caption | [484.8015, 583.471, 309.0673, 47.6619] |
### page-10

倒锥漏斗，顶流量入口；左右获取/激活/留存/推荐/盈利；底价值；向上回流曲线

Layout为`source-spatial-10`，原型为`templates/prototypes/source-spatial-10.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_102 | 1 | 5 | body | [926.2186, 293.7464, 62.0398, 35.7099] |
| nodes.shape_103 | 1 | 40 | caption | [926.2186, 324.5053, 148.0777, 53.3995] |
| nodes.shape_106 | 1 | 5 | body | [869.9564, 414.363, 62.0398, 35.7099] |
| nodes.shape_108 | 1 | 20 | caption | [869.9564, 445.1219, 148.0777, 30.0802] |
| nodes.shape_109 | 1 | 5 | body | [385.2973, 199.4423, 62.0398, 35.7099] |
| nodes.shape_110 | 1 | 20 | caption | [299.2681, 230.2099, 148.0777, 30.0802] |
| nodes.shape_111 | 1 | 11 | heading | [628.2098, 532.7608, 141.7084, 41.3309] |
| nodes.shape_112 | 1 | 5 | body | [441.7335, 359.2667, 62.0398, 35.7099] |
| nodes.shape_113 | 1 | 20 | caption | [355.7043, 390.0343, 148.0777, 30.0802] |
| nodes.shape_114 | 1 | 5 | body | [490.2168, 476.5943, 62.0398, 35.7099] |
| nodes.shape_115 | 1 | 30 | caption | [330.462, 507.3532, 221.7946, 30.0802] |
| nodes.shape_118 | 1 | 12 | body | [633.2652, 611.1068, 139.8028, 35.7099] |
| nodes.shape_10 | 1 | 10 | body | [644.6117, 204.7675, 108.9047, 35.7099] |
### page-11

战略规划至营销活动5层倒锥；各层椭圆；外左右立式循环与旁注

Layout为`source-spatial-11`，原型为`templates/prototypes/source-spatial-11.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_57 | 1 | 16 | heading | [524.5697, 187.8622, 211.973, 40.4006] |
| nodes.shape_74 | 1 | 11 | diagramCompact | [594.7863, 336.2037, 72.2273, 17.5] |
| nodes.shape_75 | 1 | 11 | diagramCompact | [594.7863, 403.0345, 72.2273, 17.5] |
| nodes.shape_76 | 1 | 11 | diagramCompact | [594.7863, 466.4171, 72.2273, 17.5] |
| nodes.shape_77 | 1 | 11 | diagramCompact | [594.7863, 572.6796, 72.2273, 17.5] |
| nodes.shape_78 | 1 | 11 | diagramCompact | [757.2951, 472.3344, 72.2273, 17.5] |
| nodes.shape_79 | 1 | 11 | diagramCompact | [435.83, 472.3344, 72.2273, 17.5] |
| nodes.shape_80 | 1 | 11 | diagramCompact | [784.2879, 411.5981, 72.2273, 17.5] |
| nodes.shape_81 | 1 | 11 | diagramCompact | [816.1771, 343.1837, 72.2273, 17.5] |
| nodes.shape_82 | 1 | 11 | diagramCompact | [852.2856, 260.9136, 72.2273, 17.5] |
| nodes.shape_83 | 1 | 11 | diagramCompact | [402.5552, 411.1397, 72.2273, 17.5] |
| nodes.shape_84 | 1 | 11 | diagramCompact | [372.8955, 343.4025, 72.2273, 17.5] |
| nodes.shape_85 | 1 | 11 | diagramCompact | [336.1203, 261.6845, 72.2273, 17.5] |
| nodes.shape_94 | 1 | 22 | caption | [1061.0082, 341.5471, 165.0716, 20.2003] |
| nodes.shape_102 | 1 | 25 | diagramMicro | [1061.0082, 366.6021, 136.287, 18.398] |
| nodes.shape_104 | 1 | 22 | caption | [984.8012, 468.5413, 165.0716, 20.2003] |
| nodes.shape_105 | 1 | 25 | diagramMicro | [984.8012, 493.5963, 136.287, 18.398] |
| nodes.shape_107 | 1 | 22 | caption | [150.2649, 533.476, 165.0716, 20.2003] |
| nodes.shape_108 | 1 | 25 | diagramMicro | [179.0392, 558.5311, 136.287, 18.398] |
| nodes.shape_110 | 1 | 22 | caption | [53.9202, 284.7174, 165.0716, 20.2003] |
| nodes.shape_111 | 1 | 25 | diagramMicro | [82.6944, 309.7725, 136.287, 18.398] |
| nodes.shape_56 | 1 | 10 | heading | [561.9491, 229.2754, 137.2246, 35.0] |
| nodes.shape_4 | 1 | 58 | caption | [419.3072, 120, 423.1959, 20.2003] |
### page-12

中央水平椭圆；两端3重竖椭圆穿插；上角色边界、下探索机会3组

Layout为`source-spatial-12`，原型为`templates/prototypes/source-spatial-12.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_14 | 1 | 61 | caption | [422.2233, 120, 439.4807, 20.9776] |
| nodes.shape_26 | 1 | 14 | diagramCompact | [595.4753, 498.054, 91.7649, 17.5] |
| nodes.shape_27 | 1 | 10 | heading | [578.1436, 443.5189, 131.0912, 35.0] |
| nodes.shape_28 | 1 | 8 | heading | [589.3843, 250.079, 104.8773, 35.0] |
| nodes.shape_29 | 1 | 19 | caption | [559.9356, 286.5877, 142.386, 20.9776] |
| nodes.shape_31 | 1 | 10 | caption | [598.3747, 546.2026, 72.8321, 20.0] |
| nodes.shape_32 | 1 | 12 | caption | [591.6346, 569.9066, 87.3941, 20.0] |
| nodes.shape_34 | 1 | 14 | diagramCompact | [272.5562, 498.054, 91.7649, 17.5] |
| nodes.shape_35 | 1 | 10 | heading | [262.7436, 443.5189, 131.0912, 35.0] |
| nodes.shape_36 | 1 | 8 | heading | [258.0915, 250.079, 104.8773, 35.0] |
| nodes.shape_37 | 1 | 19 | caption | [252.2602, 286.5877, 142.386, 20.9776] |
| nodes.shape_39 | 1 | 10 | caption | [257.821, 546.9491, 72.8321, 20.0] |
| nodes.shape_41 | 1 | 12 | caption | [257.821, 570.653, 87.3941, 20.0] |
| nodes.shape_43 | 1 | 14 | diagramCompact | [933.3676, 498.054, 91.7649, 17.5] |
| nodes.shape_44 | 1 | 10 | heading | [911.8166, 443.5189, 131.0912, 35.0] |
| nodes.shape_45 | 1 | 8 | heading | [928.4451, 250.079, 104.8773, 35.0] |
| nodes.shape_46 | 1 | 19 | caption | [875.3897, 286.5877, 142.386, 20.9776] |
| nodes.shape_50 | 1 | 10 | caption | [969.0047, 546.2026, 72.8321, 20.0] |
| nodes.shape_51 | 1 | 12 | caption | [955.5137, 569.9066, 87.3941, 20.0] |
| nodes.shape_55 | 1 | 25 | heading | [480.9801, 355.8327, 321.253, 35.0] |
### page-13

上4分区椭圆盘，中3上箭头，下3扇区底座；上下两层连接

Layout为`source-spatial-13`，原型为`templates/prototypes/source-spatial-13.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_69 | 1 | 13 | diagramMicro | [1041.1592, 138.1877, 73.5629, 15.0] |
| nodes.shape_70 | 1 | 12 | caption | [604.2168, 280.4876, 92.5387, 20.0] |
| nodes.shape_71 | 1 | 12 | caption | [604.2168, 389.1135, 92.5387, 20.0] |
| nodes.shape_72 | 1 | 12 | caption | [322.4848, 328.2257, 92.5387, 20.0] |
| nodes.shape_73 | 1 | 12 | caption | [887.6345, 328.2257, 92.5387, 20.0] |
| nodes.shape_74 | 1 | 16 | compactBody | [227.7941, 533.2197, 149.8261, 25.0] |
| nodes.shape_75 | 1 | 16 | compactBody | [919.58, 533.2197, 149.8261, 25.0] |
| nodes.shape_76 | 1 | 20 | compactBody | [562.8694, 623.0, 187.2867, 25.0] |
### page-14

获客→识客→洗客→转化4层漏斗；上7渠道，底客户成长/忠诚/洞察回环；左3阶段说明

Layout为`source-spatial-14`，原型为`templates/prototypes/source-spatial-14.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_1096 | 1 | 6 | diagramMicro | [471.4066, 307.9077, 37.1507, 15.0] |
| nodes.shape_1100 | 1 | 6 | diagramMicro | [471.4066, 385.3917, 37.1507, 15.0] |
| nodes.shape_1104 | 1 | 6 | diagramMicro | [471.4066, 462.8757, 37.1507, 15.0] |
| nodes.shape_1110 | 1 | 8 | diagramCompact | [774.3613, 589.7733, 55.2933, 19.3527] |
| nodes.shape_1111 | 1 | 10 | diagramCompact | [934.2206, 564.356, 68.1267, 19.3527] |
| nodes.shape_1112 | 1 | 8 | diagramCompact | [966.48, 502.712, 55.2933, 19.3527] |
| nodes.shape_1113 | 1 | 8 | caption | [462.4746, 289.6567, 63.1913, 21.7213] |
| nodes.shape_1114 | 1 | 8 | caption | [462.4746, 368.556, 63.1913, 21.7213] |
| nodes.shape_1115 | 1 | 5 | compactBody | [783.4473, 353.6547, 45.4153, 28.8273] |
| nodes.shape_1116 | 1 | 5 | compactBody | [783.4473, 430.42, 45.4153, 28.8273] |
| nodes.shape_1117 | 1 | 8 | caption | [462.4746, 445.7027, 63.1913, 21.7213] |
| nodes.shape_1118 | 1 | 5 | compactBody | [783.4473, 497.9747, 45.4153, 28.8273] |
| nodes.shape_1119 | 1 | 10 | diagramCompact | [563.7553, 504.2887, 68.1267, 19.3527] |
| nodes.shape_1120 | 1 | 12 | diagramCompact | [611.1653, 574.3953, 80.96, 19.3527] |
| nodes.shape_1121 | 1 | 5 | diagramMicro | [717.6453, 202.9253, 27.6467, 18.1647] |
| nodes.shape_1122 | 1 | 5 | diagramMicro | [787.3266, 218.9487, 27.6467, 18.1647] |
| nodes.shape_1123 | 1 | 5 | diagramMicro | [674.386, 230.7187, 27.6467, 18.1647] |
| nodes.shape_1124 | 1 | 5 | diagramMicro | [743.752, 238.052, 29.6193, 18.1647] |
| nodes.shape_1125 | 1 | 5 | diagramMicro | [823.6706, 187.54, 27.6467, 18.1647] |
| nodes.shape_1126 | 1 | 5 | diagramMicro | [845.1206, 222.9893, 27.6467, 18.1647] |
| nodes.shape_1127 | 1 | 7 | diagramMicro | [881.6993, 246.192, 39.49, 18.1647] |
| nodes.shape_1128 | 1 | 5 | compactBody | [783.4473, 268.94, 45.4153, 28.8273] |
| nodes.shape_1131 | 1 | 21 | compactBody | [217.8786, 120, 33.9827, 187.7187] |
### page-15

中核心圆，左右扇形分层扩散，外围阶段竖线；左正反馈生命周期，右问题负反馈

Layout为`source-spatial-15`，原型为`templates/prototypes/source-spatial-15.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_22 | 1 | 9 | diagramMicro | [227.9114, 287.4104, 50.2241, 16.1007] |
| nodes.shape_23 | 1 | 9 | diagramMicro | [222.1163, 125.148, 50.2241, 16.1007] |
| nodes.shape_24 | 1 | 9 | diagramMicro | [800.3308, 125.148, 50.2241, 16.1007] |
| nodes.shape_25 | 1 | 13 | diagramMicro | [209.879, 145.7495, 74.689, 16.1007] |
| nodes.shape_26 | 1 | 13 | diagramMicro | [788.1031, 145.7495, 74.689, 16.1007] |
| nodes.shape_27 | 1 | 11 | diagramMicro | [221.4692, 339.5662, 62.4614, 16.1007] |
| nodes.shape_28 | 1 | 9 | diagramMicro | [227.9114, 391.722, 50.2241, 16.1007] |
| nodes.shape_29 | 1 | 9 | diagramMicro | [227.9114, 443.8777, 50.2241, 16.1007] |
| nodes.shape_30 | 1 | 9 | diagramMicro | [227.9114, 496.0335, 50.2241, 16.1007] |
| nodes.shape_31 | 1 | 9 | diagramMicro | [393.3901, 354.3726, 50.2241, 16.1007] |
| nodes.shape_32 | 1 | 9 | diagramMicro | [393.3901, 394.3008, 50.2241, 16.1007] |
| nodes.shape_33 | 1 | 4 | diagramMicro | [481.601, 391.722, 25.7592, 16.1007] |
| nodes.shape_34 | 1 | 4 | diagramMicro | [354.1091, 391.722, 25.7592, 16.1007] |
| nodes.shape_35 | 1 | 11 | diagramMicro | [393.3901, 429.7087, 62.4614, 16.1007] |
| nodes.shape_36 | 1 | 9 | diagramMicro | [819.6477, 358.236, 50.2241, 16.1007] |
| nodes.shape_37 | 1 | 11 | diagramMicro | [962.5932, 342.145, 62.4614, 16.1007] |
| nodes.shape_38 | 1 | 9 | diagramMicro | [968.3883, 394.3008, 50.2241, 16.1007] |
| nodes.shape_39 | 1 | 9 | diagramMicro | [968.3883, 446.4565, 50.2241, 16.1007] |
| nodes.shape_40 | 1 | 9 | diagramMicro | [819.6477, 421.3445, 50.2241, 16.1007] |
| nodes.shape_41 | 1 | 4 | diagramMicro | [743.6741, 394.3008, 25.7592, 16.1007] |
| nodes.shape_42 | 1 | 9 | caption | [593.0019, 391.722, 65.6776, 21.2487] |
| nodes.shape_43 | 1 | 6 | diagramMicro | [562.0947, 336.1345, 37.3493, 15.0] |
| nodes.shape_44 | 1 | 9 | diagramMicro | [497.0546, 244.174, 52.8029, 15.0] |
| nodes.shape_45 | 1 | 9 | diagramMicro | [698.598, 243.5269, 52.8029, 15.0] |
| nodes.shape_46 | 1 | 6 | diagramMicro | [605.8766, 336.1345, 37.3493, 15.0] |
| nodes.shape_47 | 1 | 6 | diagramMicro | [581.4117, 356.0986, 37.3493, 15.0] |
| nodes.shape_48 | 1 | 10 | diagramMicro | [593.0019, 436.5826, 55.3721, 15.0] |
| nodes.shape_49 | 1 | 10 | diagramMicro | [593.0019, 455.2525, 55.3721, 15.0] |
| nodes.shape_50 | 1 | 6 | diagramMicro | [631.6358, 356.0986, 37.3493, 15.0] |
| nodes.shape_51 | 1 | 6 | diagramMicro | [652.2373, 336.1345, 37.3493, 15.0] |
| nodes.shape_52 | 1 | 9 | diagramMicro | [496.4171, 125.148, 50.2241, 16.1007] |
| nodes.shape_53 | 1 | 9 | diagramMicro | [800.3308, 125.148, 50.2241, 16.1007] |
| nodes.shape_54 | 1 | 9 | diagramMicro | [987.7052, 125.148, 50.2241, 16.1007] |
| nodes.shape_55 | 1 | 13 | diagramMicro | [484.1798, 145.7495, 74.689, 16.1007] |
| nodes.shape_56 | 1 | 13 | diagramMicro | [788.1031, 145.7495, 74.689, 16.1007] |
| nodes.shape_57 | 1 | 13 | diagramMicro | [975.4776, 145.7495, 74.689, 16.1007] |
| nodes.shape_58 | 1 | 2 | diagramCompact | [1061.1096, 628.0359, 18.6698, 19.9641] |
| nodes.shape_59 | 1 | 2 | diagramCompact | [1100.601, 628.0359, 15.68, 19.9641] |
| nodes.shape_60 | 1 | 3 | diagramCompact | [1137.0929, 628.0359, 21.2487, 19.9641] |
| nodes.shape_101 | 1 | 6 | diagramMicro | [85.6034, 631.0368, 34.1234, 15.0] |
| nodes.shape_102 | 1 | 8 | diagramMicro | [131.3266, 631.0368, 43.7819, 15.0] |
| nodes.shape_103 | 1 | 6 | diagramMicro | [232.4123, 629.7522, 34.7705, 15.0] |
| nodes.shape_104 | 1 | 6 | diagramMicro | [292.2948, 629.7522, 36.0551, 15.0] |
| nodes.shape_105 | 1 | 4 | diagramMicro | [350.2457, 629.7522, 25.7592, 15.0] |
### page-16

沙漏状双锥；公司→聚焦特征→用户多样性；上下两条抽象/具体路径

Layout为`source-spatial-16`，原型为`templates/prototypes/source-spatial-16.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_21 | 1 | 5 | compactBody | [246.3092, 169.5003, 50.817, 48.837] |
| nodes.shape_22 | 1 | 5 | compactBody | [102.4316, 399.5568, 50.817, 25.0] |
| nodes.shape_23 | 1 | 5 | compactBody | [1126.7514, 399.5568, 50.817, 25.0] |
| nodes.shape_24 | 1 | 16 | caption | [383.5933, 186.2255, 122.0975, 20.0] |
| nodes.shape_25 | 1 | 16 | caption | [383.5933, 613.2548, 122.0975, 20.0] |
| nodes.shape_26 | 1 | 10 | caption | [765.0724, 186.2255, 76.5572, 20.0] |
| nodes.shape_27 | 1 | 16 | caption | [742.629, 613.2548, 122.0975, 20.0] |
| nodes.shape_28 | 1 | 5 | compactBody | [246.3092, 599.163, 50.817, 48.837] |
| nodes.shape_29 | 1 | 5 | compactBody | [954.4903, 169.5003, 50.817, 48.837] |
| nodes.shape_30 | 1 | 5 | compactBody | [954.4903, 599.163, 50.817, 48.837] |
| nodes.shape_31 | 1 | 5 | compactBody | [606.0081, 169.5003, 50.817, 48.837] |
| nodes.shape_32 | 1 | 5 | compactBody | [606.0081, 599.163, 50.817, 48.837] |
### page-17

沙漏环面，上经营指标/企业，下体验指标/客户，中胜任力与体验团队；曲线联结

Layout为`source-spatial-17`，原型为`templates/prototypes/source-spatial-17.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_40 | 1 | 16 | diagramCompact | [80.8217, 120, 105.863, 17.5] |
| nodes.shape_41 | 1 | 12 | heading | [141.8729, 260.3194, 156.5199, 35.0701] |
| nodes.shape_42 | 1 | 20 | heading | [141.2202, 302.6666, 256.5281, 48.7085] |
| nodes.shape_43 | 1 | 135 | caption | [139.9246, 466.1712, 326.2592, 64.3537] |
| nodes.shape_44 | 1 | 12 | heading | [136.0279, 354.0833, 157.8155, 51.3095] |
| nodes.shape_45 | 1 | 8 | diagramCompact | [520.5035, 191.1271, 53.2579, 17.5] |
| nodes.shape_46 | 1 | 6 | diagramCompact | [630.2534, 387.9093, 40.2624, 17.5] |
| nodes.shape_47 | 1 | 12 | diagramCompact | [1003.039, 387.9093, 79.2292, 17.5] |
| nodes.shape_48 | 1 | 4 | diagramCompact | [1096.5593, 191.7797, 27.2768, 17.5] |
| nodes.shape_49 | 1 | 4 | diagramCompact | [1097.212, 585.9873, 27.2768, 17.5] |
| nodes.shape_50 | 1 | 8 | diagramCompact | [521.7991, 587.9356, 53.2579, 17.5] |
| nodes.shape_51 | 1 | 10 | diagramMicro | [519.1981, 207.4709, 54.5535, 15.0] |
| nodes.shape_52 | 1 | 9 | diagramMicro | [616.6151, 404.2532, 53.9008, 15.0] |
| nodes.shape_53 | 1 | 21 | diagramMicro | [1003.039, 404.2532, 118.196, 15.0] |
| nodes.shape_54 | 1 | 12 | diagramMicro | [1096.5593, 208.1236, 67.5392, 15.0] |
| nodes.shape_55 | 1 | 18 | diagramMicro | [1097.212, 602.3312, 101.9664, 15.0] |
| nodes.shape_56 | 1 | 10 | diagramMicro | [520.5035, 604.2795, 54.5535, 15.0] |
### page-18

3层圆锥台，上字体/图形/色彩，中复古/插画/3D，下运营策略；右3层引线；左说明

Layout为`source-spatial-18`，原型为`templates/prototypes/source-spatial-18.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_16 | 1 | 5 | caption | [636.8229, 263.9744, 37.4157, 23.2987] |
| nodes.shape_17 | 1 | 7 | caption | [1154.341, 236.4395, 55.7793, 23.2987] |
| nodes.shape_18 | 1 | 7 | caption | [1154.341, 370.5873, 55.7793, 23.2987] |
| nodes.shape_19 | 1 | 7 | caption | [1152.223, 525.2063, 55.7793, 23.2987] |
| nodes.shape_20 | 1 | 14 | diagramMicro | [1153.6315, 262.1296, 78.3685, 15.0] |
| nodes.shape_21 | 1 | 4 | diagramMicro | [1153.6315, 396.2669, 26.8253, 15.0] |
| nodes.shape_22 | 1 | 8 | diagramMicro | [1151.5134, 550.8858, 45.189, 15.0] |
| nodes.shape_23 | 1 | 5 | caption | [605.7614, 378.35, 37.4157, 23.2987] |
| nodes.shape_24 | 1 | 5 | caption | [692.6022, 263.9744, 37.4157, 23.2987] |
| nodes.shape_25 | 1 | 5 | caption | [692.6022, 378.35, 37.4157, 23.2987] |
| nodes.shape_26 | 1 | 10 | caption | [675.6577, 547.0965, 74.1324, 23.2987] |
| nodes.shape_27 | 1 | 12 | caption | [791.4419, 547.0965, 92.4854, 23.2987] |
| nodes.shape_28 | 1 | 12 | caption | [519.6196, 547.0965, 91.7865, 23.2987] |
| nodes.shape_29 | 1 | 5 | caption | [748.3709, 263.9744, 37.4157, 23.2987] |
| nodes.shape_30 | 1 | 3 | caption | [784.3781, 378.35, 26.8253, 23.2987] |
| nodes.shape_31 | 1 | 11 | heading | [48, 360.7065, 141.9106, 40.2433] |
| nodes.shape_32 | 1 | 17 | diagramCompact | [204.0275, 374.8235, 109.43, 21.8902] |
| nodes.shape_33 | 1 | 72 | body | [50.8276, 413.51, 263.53, 127.0841] |
### page-19

左5级服务分层；右倒锥4椭圆层，顶盘分4域，底项目实施；两侧价值尺度

Layout为`source-spatial-19`，原型为`templates/prototypes/source-spatial-19.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_84 | 1 | 9 | diagramMicro | [810.0793, 120, 51.8625, 19.0771] |
| nodes.shape_85 | 1 | 12 | diagramMicro | [802.7482, 287.3063, 66.5337, 23.483] |
| nodes.shape_86 | 1 | 19 | body | [722.1247, 259.6899, 212.3828, 35.2291] |
| nodes.shape_2 | 1 | 12 | diagramMicro | [529.673, 187.424, 64.8531, 22.0114] |
| nodes.shape_9 | 1 | 21 | diagramMicro | [529.673, 287.9604, 114.8442, 22.0114] |
| nodes.shape_4 | 1 | 9 | diagramMicro | [529.673, 202.3677, 51.8625, 19.0771] |
| nodes.shape_10 | 1 | 20 | diagramMicro | [529.673, 411.7981, 108.4216, 22.0114] |
| nodes.shape_11 | 1 | 8 | diagramMicro | [529.673, 426.7418, 43.296, 19.0771] |
| nodes.shape_12 | 1 | 10 | diagramMicro | [529.673, 303.2947, 57.6674, 19.0771] |
| nodes.shape_13 | 1 | 30 | diagramMicro | [529.673, 508.2011, 164.2267, 22.0114] |
| nodes.shape_14 | 1 | 9 | diagramMicro | [529.673, 523.1448, 51.8625, 19.0771] |
| nodes.shape_15 | 1 | 14 | diagramMicro | [1057.7729, 445.828, 78.9157, 22.0114] |
| nodes.shape_16 | 1 | 15 | diagramMicro | [1059.5988, 461.117, 81.214, 19.0771] |
| nodes.shape_17 | 1 | 15 | diagramMicro | [1053.6304, 586.9351, 82.5857, 22.0114] |
| nodes.shape_18 | 1 | 15 | diagramMicro | [1059.5988, 602.2331, 81.214, 19.0771] |
| nodes.shape_19 | 1 | 14 | diagramMicro | [1057.4731, 176.4138, 78.7703, 22.0114] |
| nodes.shape_20 | 1 | 15 | diagramMicro | [1059.29, 191.7118, 81.214, 19.0771] |
| nodes.shape_21 | 1 | 24 | diagramMicro | [762.5409, 225.2875, 134.8752, 19.0771] |
| nodes.shape_22 | 1 | 10 | diagramMicro | [807.6538, 240.5219, 57.6674, 19.0771] |
| nodes.shape_23 | 1 | 9 | diagramMicro | [810.7879, 192.0752, 51.8625, 19.0771] |
| nodes.shape_24 | 1 | 9 | diagramMicro | [751.0311, 168.038, 51.8625, 19.0771] |
| nodes.shape_25 | 1 | 9 | diagramMicro | [869.1275, 168.038, 51.8625, 19.0771] |
| nodes.shape_26 | 1 | 8 | compactBody | [796.7798, 169.0464, 74.9458, 30.8232] |
| nodes.shape_27 | 1 | 10 | diagramMicro | [644.5354, 273.489, 56.5954, 19.0771] |
| nodes.shape_28 | 1 | 6 | diagramMicro | [657.2262, 286.9429, 34.7385, 19.0771] |
| nodes.shape_29 | 1 | 10 | diagramMicro | [977.7399, 273.489, 56.5954, 19.0771] |
| nodes.shape_30 | 1 | 6 | diagramMicro | [990.4307, 286.9429, 34.7385, 19.0771] |
| nodes.shape_31 | 1 | 19 | diagramMicro | [780.8186, 316.9394, 103.5342, 19.0771] |
| nodes.shape_32 | 1 | 10 | diagramMicro | [807.3449, 330.3933, 57.6674, 19.0771] |
| nodes.shape_33 | 1 | 20 | diagramMicro | [683.4981, 396.7908, 111.483, 19.0771] |
| nodes.shape_34 | 1 | 9 | diagramMicro | [717.7461, 407.9191, 51.8625, 19.0771] |
| nodes.shape_35 | 1 | 18 | diagramMicro | [875.2413, 397.0269, 100.7817, 19.0771] |
| nodes.shape_36 | 1 | 9 | diagramMicro | [903.1393, 408.1462, 51.8625, 19.0771] |
| nodes.shape_37 | 1 | 10 | diagramMicro | [767.0195, 465.4502, 58.5849, 19.0771] |
| nodes.shape_38 | 1 | 8 | diagramMicro | [776.7307, 476.5785, 43.296, 19.0771] |
| nodes.shape_39 | 1 | 12 | diagramMicro | [850.9497, 499.2894, 69.2863, 19.0771] |
| nodes.shape_40 | 1 | 8 | diagramMicro | [866.0116, 510.4086, 43.296, 19.0771] |
| nodes.shape_41 | 1 | 10 | diagramMicro | [840.3029, 572.3365, 55.0693, 19.0771] |
| nodes.shape_42 | 1 | 6 | diagramMicro | [852.0762, 583.4558, 34.7385, 19.0771] |
| nodes.shape_43 | 1 | 11 | diagramMicro | [766.4654, 586.3082, 61.3375, 19.0771] |
| nodes.shape_44 | 1 | 6 | diagramMicro | [781.6816, 597.4366, 34.7385, 19.0771] |
| nodes.shape_45 | 1 | 6 | diagramMicro | [819.4271, 405.3664, 34.7385, 19.0771] |
| nodes.shape_46 | 1 | 12 | caption | [259.9135, 266.1579, 87.782, 26.4173] |
| nodes.shape_47 | 1 | 8 | diagramMicro | [259.9135, 289.0686, 43.296, 19.0771] |
| nodes.shape_48 | 1 | 8 | caption | [259.9953, 320.0553, 63.0181, 26.4173] |
| nodes.shape_49 | 1 | 8 | diagramMicro | [259.9953, 342.966, 43.296, 19.0771] |
| nodes.shape_50 | 1 | 13 | caption | [259.9135, 373.9527, 98.6378, 26.4173] |
| nodes.shape_51 | 1 | 8 | diagramMicro | [259.9135, 396.8634, 43.296, 19.0771] |
| nodes.shape_52 | 1 | 9 | caption | [259.9135, 427.8592, 65.3164, 26.4173] |
| nodes.shape_53 | 1 | 8 | diagramMicro | [259.9135, 450.7699, 43.296, 19.0771] |
| nodes.shape_55 | 1 | 19 | caption | [259.9135, 481.7838, 139.6172, 26.4173] |
| nodes.shape_56 | 1 | 8 | diagramMicro | [259.9135, 504.6945, 43.296, 19.0771] |
| nodes.shape_57 | 1 | 10 | diagramMicro | [139.1872, 303.2993, 58.8938, 19.0771] |
| nodes.shape_58 | 1 | 10 | diagramMicro | [423.9312, 301.8321, 55.8324, 19.0771] |
| nodes.shape_59 | 1 | 11 | diagramMicro | [438.0029, 498.6535, 61.0286, 19.0771] |
| nodes.shape_60 | 1 | 11 | diagramMicro | [155.4799, 498.6625, 61.0286, 19.0771] |
| nodes.shape_61 | 1 | 23 | heading | [156.3793, 561.8169, 295.8588, 46.966] |
| nodes.shape_62 | 1 | 34 | caption | [157.3059, 605.6851, 246.7852, 26.4173] |
### page-20

左5层倒锥操作/状态/数据/信息/逻辑；右上升锥箭头+强/可/无感知3环；中转换箭头

Layout为`source-spatial-20`，原型为`templates/prototypes/source-spatial-20.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_11 | 1 | 16 | compactBody | [67.3314, 227.6675, 39.1536, 105.4813] |
| nodes.shape_12 | 1 | 16 | compactBody | [67.3314, 459.117, 39.1536, 105.4813] |
| nodes.shape_14 | 1 | 8 | compactBody | [317.5861, 348.9369, 75.112, 31.9619] |
| nodes.shape_15 | 1 | 8 | compactBody | [317.5861, 409.2599, 75.112, 31.9619] |
| nodes.shape_16 | 1 | 8 | compactBody | [317.5861, 472.7782, 75.112, 31.9619] |
| nodes.shape_17 | 1 | 8 | compactBody | [317.5861, 527.9672, 75.112, 31.9619] |
| nodes.shape_18 | 1 | 8 | compactBody | [317.5861, 584.4323, 75.112, 31.9619] |
| nodes.shape_19 | 1 | 20 | compactBody | [466.4465, 435.5736, 37.828, 143.8435] |
| nodes.shape_20 | 1 | 9 | compactBody | [930.3728, 286.0616, 83.105, 35.1571] |
| nodes.shape_21 | 1 | 9 | compactBody | [930.3728, 423.9598, 83.105, 35.1571] |
| nodes.shape_22 | 1 | 9 | compactBody | [930.3728, 543.9531, 83.105, 35.1571] |
| nodes.shape_23 | 1 | 11 | diagramCompact | [178.8074, 223.8293, 72.451, 25.5715] |
| nodes.shape_24 | 1 | 11 | diagramCompact | [170.8936, 276.9211, 72.451, 25.5715] |
| nodes.shape_25 | 1 | 11 | diagramCompact | [318.9117, 206.3496, 72.451, 25.5715] |
| nodes.shape_26 | 1 | 11 | diagramCompact | [318.9117, 298.328, 72.451, 25.5715] |
| nodes.shape_27 | 1 | 11 | diagramCompact | [464.6941, 223.8293, 72.451, 25.5715] |
| nodes.shape_28 | 1 | 11 | diagramCompact | [461.7264, 276.9211, 72.451, 25.5715] |
| nodes.shape_29 | 1 | 11 | diagramMicro | [822.2898, 254.5448, 61.797, 22.3763] |
| nodes.shape_30 | 1 | 15 | diagramMicro | [776.1226, 295.1031, 83.105, 22.3763] |
| nodes.shape_31 | 1 | 13 | diagramMicro | [838.4439, 330.7153, 72.451, 22.3763] |
| nodes.shape_32 | 1 | 15 | diagramMicro | [928.2855, 343.9017, 84.2723, 22.3763] |
| nodes.shape_33 | 1 | 15 | diagramMicro | [1029.9385, 330.7153, 83.105, 22.3763] |
| nodes.shape_34 | 1 | 11 | diagramMicro | [1058.6261, 257.9972, 61.797, 22.3763] |
| nodes.shape_35 | 1 | 11 | diagramMicro | [1098.5216, 295.1031, 61.797, 22.3763] |
| nodes.shape_50 | 1 | 11 | diagramMicro | [795.185, 387.1408, 61.797, 22.3763] |
| nodes.shape_51 | 1 | 11 | diagramMicro | [758.5836, 427.7387, 61.797, 22.3763] |
| nodes.shape_52 | 1 | 11 | diagramMicro | [824.2683, 467.2484, 61.797, 22.3763] |
| nodes.shape_53 | 1 | 11 | diagramMicro | [938.6922, 488.685, 61.797, 22.3763] |
| nodes.shape_54 | 1 | 11 | diagramMicro | [1078.4304, 387.1408, 61.797, 22.3763] |
| nodes.shape_55 | 1 | 11 | diagramMicro | [1116.5157, 428.6883, 61.797, 22.3763] |
| nodes.shape_56 | 1 | 11 | diagramMicro | [1051.9884, 467.2484, 61.797, 22.3763] |
| nodes.shape_57 | 1 | 11 | diagramMicro | [1150.8715, 554.8346, 61.797, 22.3763] |
| nodes.shape_58 | 1 | 11 | diagramMicro | [1088.3227, 596.491, 61.797, 22.3763] |
| nodes.shape_59 | 1 | 11 | diagramMicro | [938.1283, 619.8466, 61.797, 22.3763] |
| nodes.shape_60 | 1 | 11 | diagramMicro | [733.3781, 554.8346, 61.797, 22.3763] |
| nodes.shape_61 | 1 | 11 | diagramMicro | [803.0988, 596.491, 61.797, 22.3763] |
### page-21

中心倒锥全场景/内容/链路/数据；外大椭圆回路从品牌心智到交易转化；两翼资产沉淀

Layout为`source-spatial-21`，原型为`templates/prototypes/source-spatial-21.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_7 | 1 | 25 | caption | [542.9197, 120, 180.1426, 26.1313] |
| nodes.shape_10 | 1 | 19 | caption | [567.9547, 228.8655, 143.246, 27.5871] |
| nodes.shape_17 | 1 | 11 | diagramMicro | [863.7113, 290.5095, 60.9791, 21.7731] |
| nodes.shape_19 | 1 | 11 | diagramMicro | [939.3555, 254.4846, 60.9791, 21.7731] |
| nodes.shape_24 | 1 | 11 | diagramMicro | [286.0635, 254.4846, 60.9791, 21.7731] |
| nodes.shape_26 | 1 | 11 | diagramMicro | [356.0017, 290.5095, 60.9791, 21.7731] |
| nodes.shape_4 | 1 | 13 | diagramMicro | [188.3137, 518.3409, 71.8611, 21.7731] |
| nodes.shape_27 | 1 | 13 | diagramMicro | [273.9774, 563.5674, 71.8611, 21.7731] |
| nodes.shape_28 | 1 | 13 | diagramMicro | [372.8235, 591.7206, 71.8611, 21.7731] |
| nodes.shape_29 | 1 | 12 | caption | [290.1612, 502.1571, 90.0129, 26.1313] |
| nodes.shape_32 | 1 | 11 | caption | [156.9436, 401.5677, 80.3349, 27.5871] |
| nodes.shape_34 | 1 | 11 | caption | [1042.7216, 401.5677, 80.3349, 27.5871] |
| nodes.shape_35 | 1 | 13 | diagramMicro | [835.1268, 590.4805, 71.8611, 21.7731] |
| nodes.shape_36 | 1 | 13 | diagramMicro | [935.7701, 563.5674, 71.8611, 21.7731] |
| nodes.shape_37 | 1 | 13 | diagramMicro | [1019.9959, 518.3409, 71.8611, 21.7731] |
| nodes.shape_38 | 1 | 12 | caption | [909.3871, 501.8425, 90.0129, 26.1313] |
| nodes.shape_44 | 1 | 8 | caption | [471.418, 350.7787, 60.9791, 26.1313] |
| nodes.shape_45 | 1 | 8 | caption | [752.0331, 350.7787, 60.9791, 26.1313] |
| nodes.shape_46 | 1 | 8 | caption | [608.7871, 402.0978, 60.9791, 26.1313] |
| nodes.shape_47 | 1 | 8 | caption | [608.194, 309.5419, 60.9791, 26.1313] |
| nodes.shape_48 | 1 | 81 | diagramMicro | [565.3577, 336.3112, 150.5067, 49.9083] |
| nodes.shape_57 | 1 | 11 | caption | [673.073, 588.7103, 80.3349, 27.5871] |
| nodes.shape_58 | 1 | 11 | caption | [526.2955, 588.7103, 80.3349, 27.5871] |
| nodes.shape_64 | 1 | 12 | caption | [583.7521, 483.8705, 48.8749, 46.4577] |
| nodes.shape_65 | 1 | 12 | caption | [644.6323, 483.8705, 48.8749, 46.4577] |
| nodes.shape_12 | 1 | 14 | caption | [753.399, 494.0337, 104.5343, 26.1313] |
| nodes.shape_14 | 1 | 14 | caption | [427.8628, 494.0337, 104.5343, 26.1313] |
### page-22

上下双漏斗以成交客户为腰；上商机→目标→线索，下活跃→忠诚→NPS；左右相反旅程箭头

Layout为`source-spatial-22`，原型为`templates/prototypes/source-spatial-22.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_10 | 1 | 4 | diagramMicro | [218.5753, 588.8087, 25.9087, 15.0] |
| nodes.shape_11 | 1 | 6 | diagramMicro | [253.2913, 588.8087, 33.242, 15.0] |
| nodes.shape_12 | 1 | 4 | diagramMicro | [330.042, 587.8333, 26.4, 15.0] |
| nodes.shape_13 | 1 | 5 | diagramMicro | [375.5087, 587.8333, 27.3753, 15.0] |
| nodes.shape_14 | 1 | 3 | diagramMicro | [419.5087, 587.8333, 19.558, 15.0] |
| nodes.shape_15 | 1 | 48 | compactBody | [219.558, 310.1753, 216.0913, 61.6] |
| nodes.shape_16 | 1 | 10 | diagramMicro | [545.038, 284.758, 13.44, 80.1753] |
| nodes.shape_17 | 1 | 16 | diagramMicro | [1005.5713, 407.958, 13.44, 120.2667] |
| nodes.shape_18 | 1 | 9 | diagramCompact | [833.1087, 379.6, 57.2, 20.042] |
| nodes.shape_19 | 1 | 252 | diagramCompact | [219.558, 378.1333, 269.8667, 109.5087] |
| nodes.shape_20 | 1 | 147 | diagramMicro | [218.5753, 168.8913, 269.8667, 48.4] |
| nodes.shape_21 | 1 | 4 | diagramMicro | [770.5333, 201.642, 24.9333, 17.1087] |
| nodes.shape_22 | 1 | 9 | diagramMicro | [758.8, 263.242, 48.8913, 17.1087] |
| nodes.shape_23 | 1 | 4 | diagramMicro | [771.0247, 328.758, 24.9333, 17.1087] |
| nodes.shape_24 | 1 | 13 | diagramMicro | [747.0667, 424.5753, 72.842, 17.1087] |
| nodes.shape_25 | 1 | 18 | diagramMicro | [734.842, 491.558, 97.2913, 17.1087] |
| nodes.shape_26 | 1 | 22 | diagramMicro | [721.642, 548.2667, 123.2, 17.1087] |
| nodes.shape_27 | 1 | 18 | diagramMicro | [732.8913, 219.079, 100.2247, 15.0] |
| nodes.shape_28 | 1 | 3 | diagramMicro | [772.4913, 346.1877, 21.5087, 15.0] |
| nodes.shape_29 | 1 | 15 | diagramMicro | [741.6913, 280.679, 83.1087, 15.0] |
| nodes.shape_30 | 1 | 15 | diagramMicro | [742.1753, 442.0123, 82.6247, 15.0] |
| nodes.shape_31 | 1 | 15 | diagramMicro | [742.1753, 508.9877, 82.1333, 15.0] |
| nodes.shape_32 | 1 | 17 | diagramMicro | [735.3333, 565.7037, 96.3087, 15.0] |
### page-23

3个悬浮环盘，吸引/沉淀/转化3阶段；每环多个触点；中段连接箭头

Layout为`source-spatial-23`，原型为`templates/prototypes/source-spatial-23.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_49 | 1 | 8 | diagramMicro | [335.0121, 248.5404, 44.6885, 15.0] |
| nodes.shape_50 | 1 | 8 | diagramMicro | [450.9685, 237.6694, 44.6885, 15.0] |
| nodes.shape_51 | 1 | 8 | diagramMicro | [561.4894, 234.0458, 44.6885, 15.0] |
| nodes.shape_52 | 1 | 8 | diagramMicro | [689.5215, 235.8576, 44.6885, 15.0] |
| nodes.shape_53 | 1 | 8 | diagramMicro | [816.3488, 246.7285, 44.6885, 15.0] |
| nodes.shape_54 | 1 | 31 | diagramMicro | [997.8386, 311.0019, 171.5158, 15.6994] |
| nodes.shape_55 | 1 | 8 | diagramMicro | [833.2621, 294.4428, 44.6885, 15.0] |
| nodes.shape_56 | 1 | 8 | diagramMicro | [698.5806, 305.3137, 44.6885, 15.0] |
| nodes.shape_57 | 1 | 8 | diagramMicro | [581.4194, 309.5443, 44.6885, 15.0] |
| nodes.shape_58 | 1 | 8 | diagramMicro | [441.3024, 305.9206, 44.6885, 15.0] |
| nodes.shape_59 | 1 | 8 | diagramMicro | [302.9973, 295.0497, 44.6885, 15.0] |
| nodes.shape_60 | 1 | 7 | diagramMicro | [338.0288, 471.702, 39.86, 15.0] |
| nodes.shape_61 | 1 | 6 | diagramMicro | [427.4149, 538.3979, 35.0315, 15.0] |
| nodes.shape_62 | 1 | 8 | diagramMicro | [385.1361, 569.1988, 43.4836, 15.0] |
| nodes.shape_63 | 1 | 6 | diagramMicro | [445.533, 585.5051, 35.0315, 15.0] |
| nodes.shape_64 | 1 | 6 | diagramMicro | [492.6403, 562.5494, 35.0315, 15.0] |
| nodes.shape_65 | 1 | 11 | diagramMicro | [568.1297, 535.0603, 61.6018, 15.6994] |
| nodes.shape_66 | 1 | 13 | diagramMicro | [562.0873, 391.9267, 73.6776, 15.6994] |
| nodes.shape_70 | 1 | 8 | caption | [123.0294, 296.1688, 59.183, 20.0] |
| nodes.shape_71 | 1 | 8 | caption | [123.0294, 422.3891, 59.183, 20.0] |
| nodes.shape_72 | 1 | 8 | caption | [123.0294, 556.4637, 59.183, 20.0] |
| nodes.shape_73 | 1 | 8 | diagramMicro | [132.6864, 317.3561, 46.5003, 15.0] |
| nodes.shape_74 | 1 | 12 | diagramMicro | [132.6864, 443.5764, 68.8491, 15.0] |
| nodes.shape_75 | 1 | 15 | diagramMicro | [132.6864, 577.6509, 85.1554, 15.0] |
| nodes.shape_76 | 1 | 6 | diagramMicro | [530.0815, 592.7524, 35.0315, 15.0] |
| nodes.shape_77 | 1 | 6 | diagramMicro | [597.1188, 595.7691, 35.0315, 15.0] |
| nodes.shape_78 | 1 | 9 | diagramMicro | [668.9846, 561.3446, 51.9358, 15.0] |
| nodes.shape_79 | 1 | 6 | diagramMicro | [697.9736, 589.7267, 35.0315, 15.0] |
| nodes.shape_80 | 1 | 6 | diagramMicro | [772.2582, 567.387, 35.0315, 15.0] |
| nodes.shape_81 | 1 | 7 | diagramMicro | [708.2467, 534.7742, 41.0649, 15.0] |
| nodes.shape_82 | 1 | 7 | diagramMicro | [397.8188, 386.5465, 39.86, 15.0] |
| nodes.shape_83 | 1 | 7 | diagramMicro | [455.797, 454.7887, 39.86, 15.0] |
| nodes.shape_84 | 1 | 7 | diagramMicro | [579.6076, 460.8311, 39.86, 15.0] |
| nodes.shape_85 | 1 | 7 | diagramMicro | [726.3648, 452.3699, 39.86, 15.0] |
| nodes.shape_86 | 1 | 7 | diagramMicro | [769.8485, 393.1868, 39.86, 15.0] |
| nodes.shape_87 | 1 | 7 | diagramMicro | [815.7418, 470.4881, 39.86, 15.0] |
| nodes.shape_121 | 1 | 5 | diagramMicro | [1020.4773, 122.9225, 30.8009, 15.0] |
| nodes.shape_122 | 1 | 5 | diagramMicro | [1057.9275, 122.9225, 28.9891, 15.0] |
### page-24

顶3问题卡，下消费核心盘与外圈8策略节点

Layout为`source-spatial-24`，原型为`templates/prototypes/source-spatial-24.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_68 | 1 | 11 | compactBody | [279.9283, 349.5716, 105.0538, 25.2122] |
| nodes.shape_69 | 1 | 19 | diagramMicro | [279.9283, 378.2253, 105.0538, 15.0] |
| nodes.shape_70 | 1 | 52 | diagramMicro | [262.1375, 402.2849, 140.6439, 31.7233] |
| nodes.shape_83 | 1 | 9 | compactBody | [590.6073, 343.6587, 84.0465, 25.2122] |
| nodes.shape_84 | 1 | 19 | diagramMicro | [580.108, 372.3124, 105.0538, 15.0] |
| nodes.shape_85 | 1 | 84 | diagramMicro | [556.5257, 396.3807, 152.2097, 48.1182] |
| nodes.shape_89 | 1 | 9 | compactBody | [888.2467, 343.6587, 84.0465, 25.2122] |
| nodes.shape_90 | 1 | 19 | diagramMicro | [877.7387, 372.3124, 105.0538, 15.0] |
| nodes.shape_91 | 1 | 90 | diagramMicro | [847.8967, 396.3807, 164.7464, 48.1182] |
| nodes.shape_92 | 1 | 14 | compactBody | [583.576, 516.8821, 126.0698, 25.0] |
| nodes.shape_93 | 1 | 26 | diagramMicro | [575.695, 542.5382, 141.8231, 15.0] |
| nodes.shape_94 | 1 | 19 | diagramMicro | [261.0451, 506.8527, 105.0538, 15.0] |
| nodes.shape_95 | 1 | 19 | diagramMicro | [145.4487, 542.5382, 105.0538, 15.0] |
| nodes.shape_96 | 1 | 19 | diagramMicro | [296.8867, 585.0297, 105.0538, 15.0] |
| nodes.shape_97 | 1 | 19 | diagramMicro | [592.4713, 611.343, 105.0538, 15.0] |
| nodes.shape_98 | 1 | 19 | diagramMicro | [873.8372, 586.7203, 105.0538, 15.0] |
| nodes.shape_99 | 1 | 19 | diagramMicro | [1025.8562, 542.4342, 105.0538, 15.0] |
| nodes.shape_100 | 1 | 19 | diagramMicro | [910.3724, 510.8409, 105.0538, 15.0] |
### page-25

上业务中台分8云域，外智能/数据中台环，底技术平台；两翼应用基础设施/共创平台

Layout为`source-spatial-25`，原型为`templates/prototypes/source-spatial-25.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_6 | 1 | 39 | diagramCompact | [368.4332, 126.3635, 251.834, 24.9059] |
| nodes.shape_94 | 1 | 17 | compactBody | [574.9089, 577.0679, 154.1631, 32.5455] |
| nodes.shape_95 | 1 | 15 | compactBody | [413.0291, 438.5438, 45.1955, 96.8572] |
| nodes.shape_96 | 1 | 15 | compactBody | [853.7129, 438.5438, 45.1955, 96.8572] |
| nodes.shape_97 | 1 | 12 | compactBody | [598.4445, 375.2427, 109.6613, 30.4386] |
| nodes.shape_98 | 1 | 17 | diagramCompact | [523.5127, 623.0941, 109.6613, 24.9059] |
| nodes.shape_99 | 1 | 17 | diagramCompact | [657.0779, 622.5897, 109.6613, 24.9059] |
| nodes.shape_100 | 1 | 17 | diagramCompact | [794.9339, 586.2748, 109.6613, 24.9059] |
| nodes.shape_101 | 1 | 22 | diagramCompact | [380.2009, 581.5814, 143.1661, 24.9059] |
| nodes.shape_110 | 1 | 36 | caption | [236.0756, 459.116, 136.3915, 47.0454] |
| nodes.shape_111 | 1 | 36 | caption | [934.7598, 459.116, 136.3915, 47.0454] |
| nodes.shape_102 | 1 | 12 | diagramCompact | [560.1178, 451.3564, 78.6403, 24.1094] |
| nodes.shape_103 | 1 | 17 | diagramCompact | [665.4883, 448.8641, 109.6613, 23.527] |
| nodes.shape_104 | 1 | 17 | diagramCompact | [750.1324, 410.8287, 109.6613, 23.527] |
| nodes.shape_105 | 1 | 17 | diagramCompact | [452.1009, 410.8287, 109.6613, 23.527] |
| nodes.shape_106 | 1 | 17 | diagramCompact | [750.1324, 353.814, 109.6613, 23.527] |
| nodes.shape_107 | 1 | 17 | diagramCompact | [452.1009, 353.814, 109.6613, 23.527] |
| nodes.shape_108 | 1 | 15 | diagramCompact | [551.399, 310.8196, 96.0779, 23.527] |
| nodes.shape_109 | 1 | 15 | diagramCompact | [666.1649, 310.8196, 96.5318, 23.527] |
| nodes.shape_137_segment_1 | 1 | 23 | diagramCompact | [431.0234, 239.622, 145.5985, 27.4068] |
| nodes.shape_137_segment_2 | 1 | 23 | diagramCompact | [529.5165, 189.9472, 145.5985, 27.4068] |
| nodes.shape_137_segment_3 | 1 | 23 | diagramCompact | [648.5646, 189.9472, 145.5985, 27.4068] |
| nodes.shape_137_segment_4 | 1 | 23 | diagramCompact | [744.4883, 239.622, 145.5985, 27.4068] |
### page-26

顶虚拟人场景7节点虚线环；中应用交付盘+环形箭头；底智能设计6节点环

Layout为`source-spatial-26`，原型为`templates/prototypes/source-spatial-26.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_17 | 1 | 10 | diagramMicro | [771.1515, 290.9126, 56.6389, 24.6208] |
| nodes.shape_19 | 1 | 10 | diagramMicro | [539.4745, 290.9126, 56.6389, 24.6208] |
| nodes.shape_21 | 1 | 10 | diagramMicro | [354.9154, 249.353, 56.6389, 24.6208] |
| nodes.shape_23 | 1 | 10 | diagramMicro | [443.0339, 186.79, 56.6389, 24.6208] |
| nodes.shape_25 | 1 | 10 | diagramMicro | [864.8181, 186.79, 56.6389, 24.6208] |
| nodes.shape_27 | 1 | 10 | diagramMicro | [964.0328, 249.4241, 56.6389, 24.6208] |
| nodes.shape_29 | 1 | 15 | diagramMicro | [646.7572, 174.5965, 81.2597, 24.6208] |
| nodes.shape_37 | 1 | 31 | diagramMicro | [603.5312, 221.7651, 170.0184, 24.6208] |
| nodes.shape_38 | 1 | 11 | compactBody | [638.1506, 239.3035, 101.7855, 34.4772] |
| nodes.shape_39 | 1 | 31 | diagramMicro | [603.5312, 545.8792, 170.0184, 24.6208] |
| nodes.shape_40 | 1 | 11 | compactBody | [638.1506, 563.4176, 101.7855, 34.4772] |
| nodes.shape_41 | 1 | 31 | diagramMicro | [603.5312, 392.4745, 170.0184, 24.6208] |
| nodes.shape_42 | 1 | 10 | body | [629.9505, 410.0129, 118.2061, 39.4054] |
| nodes.shape_43 | 1 | 12 | diagramMicro | [529.6892, 355.9142, 68.9544, 24.6208] |
| nodes.shape_44 | 1 | 12 | diagramMicro | [529.6892, 457.3949, 68.9544, 24.6208] |
| nodes.shape_45 | 1 | 12 | diagramMicro | [801.0866, 356.6967, 68.9544, 24.6208] |
| nodes.shape_46 | 1 | 12 | diagramMicro | [801.0866, 456.6023, 68.9544, 24.6208] |
| nodes.shape_47 | 1 | 12 | diagramMicro | [856.9431, 508.5264, 68.9544, 24.6208] |
| nodes.shape_48 | 1 | 12 | diagramMicro | [856.9431, 598.2098, 68.9544, 24.6208] |
| nodes.shape_49 | 1 | 12 | diagramMicro | [654.7643, 623.3792, 68.9544, 24.6208] |
| nodes.shape_50 | 1 | 12 | diagramMicro | [459.6679, 599.7848, 68.9544, 24.6208] |
| nodes.shape_51 | 1 | 12 | diagramMicro | [459.6679, 508.5264, 68.9544, 24.6208] |
### page-27

顶成果句与2指标；底单椭圆11检测节点；中空背景

Layout为`source-spatial-27`，原型为`templates/prototypes/source-spatial-27.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_29 | 1 | 25 | caption | [561.8813, 166.5111, 186.4119, 26.9991] |
| nodes.shape_30 | 1 | 35 | heading | [425.3982, 194.5882, 450.9049, 51.2992] |
| nodes.shape_32 | 1 | 11 | caption | [522.2809, 349.1794, 79.2008, 26.9991] |
| nodes.shape_33 | 1 | 4 | heading | [531.5647, 287.9947, 60.6415, 51.2992] |
| nodes.shape_35 | 1 | 11 | caption | [675.7189, 349.1794, 79.2008, 26.9991] |
| nodes.shape_36 | 1 | 5 | heading | [677.6827, 287.9947, 75.265, 51.2992] |
| nodes.shape_37 | 1 | 11 | diagramCompact | [618.6455, 623.6999, 70.2011, 24.3001] |
| nodes.shape_38 | 1 | 11 | diagramCompact | [275.1689, 530.6862, 70.2011, 24.3001] |
| nodes.shape_39 | 1 | 11 | diagramCompact | [938.2064, 530.6862, 70.2011, 24.3001] |
| nodes.shape_40 | 1 | 7 | diagramMicro | [999.1655, 338.6755, 40.9541, 22.9547] |
| nodes.shape_41 | 1 | 12 | diagramMicro | [1045.5178, 394.8632, 65.7054, 22.9547] |
| nodes.shape_42 | 1 | 12 | diagramMicro | [946.287, 480.7657, 65.7054, 22.9547] |
| nodes.shape_43 | 1 | 12 | diagramMicro | [783.2141, 519.8063, 65.7054, 22.9547] |
| nodes.shape_44 | 1 | 12 | diagramMicro | [624.052, 536.5523, 65.7054, 22.9547] |
| nodes.shape_45 | 1 | 12 | diagramMicro | [458.0963, 517.9345, 65.7054, 22.9547] |
| nodes.shape_46 | 1 | 12 | diagramMicro | [264.8823, 480.3061, 65.7054, 22.9547] |
| nodes.shape_47 | 1 | 12 | diagramMicro | [168.7768, 394.8632, 65.7054, 22.9547] |
| nodes.shape_48 | 1 | 7 | diagramMicro | [230.3208, 338.2577, 40.9541, 22.9547] |
### page-28

上民生/公共管理/城市治理3圆；中服务触点环；下业务/数据双中台；底云/大数据/移动/物联

Layout为`source-spatial-28`，原型为`templates/prototypes/source-spatial-28.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_26 | 1 | 13 | caption | [444.9185, 251.8146, 95.8944, 25.9841] |
| nodes.shape_27 | 1 | 25 | diagramMicro | [423.1162, 268.3361, 139.5079, 25.1441] |
| nodes.shape_28 | 1 | 13 | caption | [591.5658, 251.8146, 95.8944, 25.9841] |
| nodes.shape_29 | 1 | 25 | diagramMicro | [569.7635, 268.3361, 139.5079, 25.0548] |
| nodes.shape_30 | 1 | 13 | caption | [738.2042, 251.8146, 95.8944, 25.9841] |
| nodes.shape_31 | 1 | 25 | diagramMicro | [716.4019, 268.3361, 139.5079, 25.1441] |
| nodes.shape_32 | 1 | 13 | caption | [948.3194, 287.8867, 95.8944, 25.9841] |
| nodes.shape_33 | 1 | 38 | diagramMicro | [948.3194, 304.3993, 208.1137, 25.1441] |
| nodes.shape_34 | 1 | 13 | caption | [1006.1134, 330.2403, 95.8944, 25.9841] |
| nodes.shape_35 | 1 | 25 | diagramMicro | [1006.1134, 346.7529, 139.5079, 25.1441] |
| nodes.shape_37 | 1 | 13 | caption | [818.4885, 351.0061, 95.8944, 25.9841] |
| nodes.shape_38 | 1 | 25 | diagramMicro | [818.4885, 367.5276, 139.5079, 25.1441] |
| nodes.shape_39 | 1 | 13 | caption | [671.1442, 358.5119, 95.8944, 25.9841] |
| nodes.shape_40 | 1 | 28 | diagramMicro | [671.1442, 375.0244, 152.0621, 25.0548] |
| nodes.shape_41 | 1 | 13 | caption | [465.318, 362.8008, 95.8944, 25.9841] |
| nodes.shape_42 | 1 | 25 | diagramMicro | [421.7134, 379.3223, 139.5079, 25.1441] |
| nodes.shape_43 | 1 | 13 | caption | [311.9334, 345.7164, 95.8944, 25.9841] |
| nodes.shape_44 | 1 | 25 | diagramMicro | [268.3288, 362.229, 139.5079, 25.1441] |
| nodes.shape_45 | 1 | 13 | caption | [185.8553, 329.043, 95.8944, 25.9841] |
| nodes.shape_46 | 1 | 25 | diagramMicro | [142.2507, 345.5645, 139.5079, 25.1441] |
| nodes.shape_47 | 1 | 13 | caption | [267.6497, 285.2776, 95.8944, 25.9841] |
| nodes.shape_48 | 1 | 25 | diagramMicro | [224.0361, 301.7901, 139.5079, 25.1441] |
| nodes.shape_49 | 1 | 13 | caption | [459.6976, 458.4272, 95.8944, 25.9841] |
| nodes.shape_50 | 1 | 31 | diagramMicro | [423.7327, 474.9397, 167.8241, 25.1441] |
| nodes.shape_51 | 1 | 13 | caption | [716.0177, 458.4272, 95.8944, 25.9841] |
| nodes.shape_52 | 1 | 25 | diagramMicro | [694.2154, 474.9397, 139.5079, 25.1441] |
| nodes.shape_53 | 1 | 13 | caption | [586.8301, 550.9619, 95.8944, 25.9841] |
| nodes.shape_54 | 1 | 25 | diagramMicro | [565.0278, 567.4744, 139.5079, 25.1441] |
| nodes.shape_55 | 1 | 19 | caption | [565.0278, 594.9596, 139.5079, 25.9841] |
| nodes.shape_56 | 1 | 40 | diagramMicro | [525.5334, 611.4722, 218.4877, 25.1441] |
| nodes.shape_57 | 1 | 13 | caption | [429.639, 571.5043, 95.8944, 25.9841] |
| nodes.shape_58 | 1 | 30 | diagramMicro | [360.4256, 588.0258, 165.1167, 25.0548] |
| nodes.shape_59 | 1 | 13 | caption | [747.8365, 567.4119, 95.8944, 25.9841] |
| nodes.shape_60 | 1 | 25 | diagramMicro | [747.8365, 583.9245, 139.5079, 25.0548] |
### page-29

上机构/医疗2圈和两侧各5权益条；中用户权益匹配圆盘与上箭头；底4技术球体与平台圆盘

Layout为`source-spatial-29`，原型为`templates/prototypes/source-spatial-29.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_273 | 1 | 90 | caption | [492.6485, 323.0051, 330.401, 54.0487] |
| nodes.shape_311 | 1 | 10 | diagramCompact | [302.7135, 568.733, 67.8675, 23.1614] |
| nodes.shape_221 | 1 | 12 | diagramMicro | [392.8663, 411.8995, 66.4418, 21.234] |
| nodes.shape_312 | 1 | 12 | diagramMicro | [849.6278, 411.8995, 66.4418, 21.234] |
| nodes.shape_324 | 1 | 10 | diagramCompact | [342.5531, 499.2965, 67.8675, 23.934] |
| nodes.shape_325 | 1 | 10 | diagramCompact | [944.9895, 568.733, 67.8675, 23.1614] |
| nodes.shape_326 | 1 | 10 | diagramCompact | [887.2611, 499.2965, 67.8675, 23.934] |
| nodes.shape_327 | 1 | 12 | diagramMicro | [542.8104, 367.1855, 66.4418, 21.234] |
| nodes.shape_328 | 1 | 12 | diagramMicro | [625.4684, 367.1855, 66.4418, 21.234] |
| nodes.shape_329 | 1 | 12 | diagramMicro | [709.106, 367.1855, 66.4418, 21.234] |
| nodes.shape_330 | 1 | 12 | diagramMicro | [262.7306, 231.3151, 66.4418, 21.234] |
| nodes.shape_331 | 1 | 12 | diagramMicro | [262.7306, 269.944, 66.4418, 21.234] |
| nodes.shape_332 | 1 | 12 | diagramMicro | [262.7306, 306.6376, 66.4418, 21.234] |
| nodes.shape_333 | 1 | 12 | diagramMicro | [262.7306, 344.486, 66.4418, 21.234] |
| nodes.shape_334 | 1 | 12 | diagramMicro | [262.7306, 381.8167, 66.4418, 21.234] |
| nodes.shape_342 | 1 | 12 | diagramMicro | [986.4221, 231.3151, 66.4418, 21.234] |
| nodes.shape_343 | 1 | 12 | diagramMicro | [986.4221, 269.944, 66.4418, 21.234] |
| nodes.shape_344 | 1 | 12 | diagramMicro | [986.4221, 306.6376, 66.4418, 21.234] |
| nodes.shape_345 | 1 | 12 | diagramMicro | [986.4221, 344.486, 66.4418, 21.234] |
| nodes.shape_346 | 1 | 12 | diagramMicro | [986.4221, 381.8167, 66.4418, 21.234] |
| nodes.shape_347 | 1 | 19 | diagramCompact | [388.9317, 320.9582, 124.5604, 23.1614] |
| nodes.shape_348 | 1 | 19 | diagramCompact | [796.6305, 320.9582, 124.5604, 23.1614] |
| nodes.shape_246 | 1 | 90 | caption | [492.6485, 592.2847, 330.401, 54.0487] |
| nodes.shape_261 | 1 | 34 | diagramCompact | [547.868, 624.3029, 218.385, 23.1614] |
### page-30

底平台层4球体/环；能力层多共性模块；应用层4列应用；顶多端入口；左右PaaS/运营立式上箭头；中总上箭头

Layout为`source-spatial-30`，原型为`templates/prototypes/source-spatial-30.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_452 | 1 | 9 | diagramMicro | [406.9533, 514.657, 52.5435, 19.9628] |
| nodes.shape_459 | 1 | 9 | diagramMicro | [363.1885, 508.0255, 52.5435, 19.9628] |
| nodes.shape_460 | 1 | 9 | diagramMicro | [331.4196, 515.9165, 52.5435, 19.9628] |
| nodes.shape_36 | 1 | 9 | diagramMicro | [573.1654, 540.2193, 52.5435, 19.9628] |
| nodes.shape_39 | 1 | 9 | diagramMicro | [536.9881, 529.5437, 52.5435, 19.9628] |
| nodes.shape_40 | 1 | 13 | diagramMicro | [488.3977, 541.4789, 71.0267, 19.9628] |
| nodes.shape_213 | 1 | 9 | diagramMicro | [755.5465, 540.2193, 52.5435, 19.9628] |
| nodes.shape_216 | 1 | 9 | diagramMicro | [719.3692, 529.5437, 52.5435, 19.9628] |
| nodes.shape_217 | 1 | 18 | diagramMicro | [677.6151, 537.541, 52.5435, 32.9222] |
| nodes.shape_484 | 1 | 9 | diagramMicro | [905.5896, 514.657, 52.5435, 19.9628] |
| nodes.shape_487 | 1 | 9 | diagramMicro | [869.4123, 508.0255, 52.5435, 19.9628] |
| nodes.shape_488 | 1 | 9 | diagramMicro | [830.0635, 515.9165, 52.5435, 19.9628] |
| nodes.shape_495 | 1 | 18 | diagramMicro | [369.0233, 542.5715, 52.5435, 32.9222] |
| nodes.shape_496 | 1 | 18 | diagramMicro | [534.6739, 568.6194, 52.5435, 32.9222] |
| nodes.shape_497 | 1 | 18 | diagramMicro | [717.1688, 568.6194, 52.5435, 32.9222] |
| nodes.shape_498 | 1 | 18 | diagramMicro | [868.517, 542.5715, 52.5435, 32.9222] |
| nodes.shape_502 | 1 | 9 | diagramMicro | [535.4706, 430.944, 52.5435, 19.9628] |
| nodes.shape_506 | 1 | 9 | diagramMicro | [463.7155, 430.944, 52.5435, 19.9628] |
| nodes.shape_509 | 1 | 9 | diagramMicro | [392.317, 430.944, 52.5435, 19.9628] |
| nodes.shape_512 | 1 | 9 | diagramMicro | [520.3639, 456.7339, 52.5435, 19.9628] |
| nodes.shape_515 | 1 | 9 | diagramMicro | [448.6087, 456.7339, 52.5435, 19.9628] |
| nodes.shape_518 | 1 | 9 | diagramMicro | [377.2102, 456.7339, 52.5435, 19.9628] |
| nodes.shape_521 | 1 | 9 | diagramMicro | [866.9691, 430.1245, 52.5435, 19.9628] |
| nodes.shape_524 | 1 | 9 | diagramMicro | [795.2216, 430.1245, 52.5435, 19.9628] |
| nodes.shape_527 | 1 | 9 | diagramMicro | [723.8231, 430.1245, 52.5435, 19.9628] |
| nodes.shape_530 | 1 | 9 | diagramMicro | [877.0605, 455.9145, 52.5435, 19.9628] |
| nodes.shape_533 | 1 | 9 | diagramMicro | [805.3054, 455.9145, 52.5435, 19.9628] |
| nodes.shape_536 | 1 | 9 | diagramMicro | [733.9145, 455.9145, 52.5435, 19.9628] |
| nodes.shape_500 | 1 | 8 | caption | [621.1564, 424.4946, 64.6305, 29.7734] |
| nodes.shape_539 | 1 | 9 | caption | [619.6237, 317.0629, 70.5715, 29.7734] |
| nodes.shape_549 | 1 | 12 | diagramMicro | [817.4151, 267.8427, 68.5608, 22.0645] |
| nodes.shape_550 | 1 | 12 | diagramMicro | [817.4151, 292.3125, 68.5608, 19.9628] |
| nodes.shape_552 | 1 | 12 | diagramMicro | [817.4151, 335.5537, 68.5608, 19.9628] |
| nodes.shape_553 | 1 | 12 | diagramMicro | [817.4151, 357.1705, 68.5608, 19.9628] |
| nodes.shape_554 | 1 | 12 | diagramMicro | [817.4151, 313.9293, 68.5608, 19.9628] |
| nodes.shape_566 | 1 | 12 | diagramMicro | [731.3196, 278.9281, 68.5608, 22.0645] |
| nodes.shape_567 | 1 | 12 | diagramMicro | [731.3196, 303.3978, 68.5608, 19.9628] |
| nodes.shape_568 | 1 | 12 | diagramMicro | [731.3196, 346.6391, 68.5608, 19.9628] |
| nodes.shape_569 | 1 | 12 | diagramMicro | [731.3196, 368.2635, 68.5608, 19.9628] |
| nodes.shape_570 | 1 | 12 | diagramMicro | [731.3196, 325.0222, 68.5608, 19.9628] |
| nodes.shape_575 | 1 | 12 | diagramMicro | [509.8324, 278.9281, 68.5608, 22.0645] |
| nodes.shape_576 | 1 | 12 | diagramMicro | [509.8324, 303.3978, 68.5608, 19.9628] |
| nodes.shape_577 | 1 | 12 | diagramMicro | [509.8324, 346.6391, 68.5608, 19.9628] |
| nodes.shape_578 | 1 | 12 | diagramMicro | [509.8324, 368.2635, 68.5608, 19.9628] |
| nodes.shape_579 | 1 | 12 | diagramMicro | [509.8324, 325.0222, 68.5608, 19.9628] |
| nodes.shape_584 | 1 | 12 | diagramMicro | [423.3347, 267.8427, 68.5608, 22.0645] |
| nodes.shape_585 | 1 | 12 | diagramMicro | [423.3347, 292.3125, 68.5608, 19.9628] |
| nodes.shape_586 | 1 | 12 | diagramMicro | [423.3347, 335.5537, 68.5608, 19.9628] |
| nodes.shape_587 | 1 | 12 | diagramMicro | [423.3347, 357.1705, 68.5608, 19.9628] |
| nodes.shape_588 | 1 | 12 | diagramMicro | [423.3347, 313.9293, 68.5608, 19.9628] |
| nodes.shape_593 | 1 | 12 | diagramMicro | [335.441, 218.2583, 68.5608, 19.9628] |
| nodes.shape_594 | 1 | 9 | caption | [619.9879, 213.0533, 68.5608, 29.7734] |
| nodes.shape_596 | 1 | 12 | diagramMicro | [406.5815, 218.2583, 68.5608, 19.9628] |
| nodes.shape_597 | 1 | 12 | diagramMicro | [477.7145, 218.2583, 68.5608, 19.9628] |
| nodes.shape_598 | 1 | 12 | diagramMicro | [548.8474, 218.2583, 68.5608, 19.9628] |
| nodes.shape_599 | 1 | 12 | diagramMicro | [691.1209, 218.2583, 68.5608, 19.9628] |
| nodes.shape_600 | 1 | 12 | diagramMicro | [762.2614, 218.2583, 68.5608, 19.9628] |
| nodes.shape_601 | 1 | 12 | diagramMicro | [833.3944, 218.2583, 68.5608, 19.9628] |
| nodes.shape_602 | 1 | 12 | diagramMicro | [904.5273, 218.2583, 68.5608, 19.9628] |
| nodes.shape_604 | 1 | 22 | diagramCompact | [276.2887, 326.5701, 70.5715, 41.6782] |
| nodes.shape_606 | 1 | 9 | diagramMicro | [274.0276, 372.5201, 52.5435, 19.9628] |
| nodes.shape_608 | 1 | 9 | diagramMicro | [267.4872, 399.4027, 52.5435, 19.9628] |
| nodes.shape_613 | 1 | 9 | diagramMicro | [260.9467, 426.2776, 52.5435, 19.9628] |
| nodes.shape_616 | 1 | 9 | diagramMicro | [254.4063, 453.1602, 52.5435, 19.9628] |
| nodes.shape_620 | 1 | 39 | diagramMicro | [953.8083, 318.7094, 70.5715, 47.1185] |
| nodes.shape_631 | 1 | 9 | diagramMicro | [973.5737, 372.5201, 52.5435, 19.9628] |
| nodes.shape_629 | 1 | 9 | diagramMicro | [980.1142, 399.4027, 52.5435, 19.9628] |
| nodes.shape_627 | 1 | 9 | diagramMicro | [986.6546, 426.2776, 52.5435, 19.9628] |
| nodes.shape_625 | 1 | 9 | diagramMicro | [993.1951, 453.1602, 52.5435, 19.9628] |
| nodes.shape_633 | 1 | 28 | diagramMicro | [577.2247, 625.2375, 154.0873, 22.7625] |
| nodes.shape_635 | 1 | 8 | caption | [621.1564, 568.1035, 64.6305, 29.7734] |
### page-31

立体梯形3层平台，源/总线/应用；中层多系统与上箭头，上层标准和资产2组模块；左右生命周期/安全

Layout为`source-spatial-31`，原型为`templates/prototypes/source-spatial-31.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_46 | 1 | 13 | compactBody | [562.6617, 284.1363, 123.7685, 34.2373] |
| nodes.shape_47 | 1 | 13 | compactBody | [562.6617, 470.1637, 123.7685, 34.2373] |
| nodes.shape_48 | 1 | 13 | compactBody | [562.6617, 607.9813, 123.7685, 34.2373] |
| nodes.shape_203 | 1 | 19 | diagramCompact | [384.6381, 310.3273, 123.7685, 27.7406] |
| nodes.shape_204 | 1 | 19 | diagramCompact | [742.9247, 310.3273, 123.7685, 27.7406] |
| nodes.shape_483 | 1 | 55 | diagramCompact | [192.94, 337.4974, 35.9913, 192.3963] |
| nodes.shape_484 | 1 | 30 | diagramCompact | [1012.2857, 373.3342, 40.9298, 89.2247] |
| nodes.shape_515 | 1 | 13 | diagramMicro | [416.8744, 514.0395, 73.7451, 22.0103] |
| nodes.shape_516 | 1 | 13 | diagramMicro | [489.8277, 514.0395, 73.7451, 22.0103] |
| nodes.shape_517 | 1 | 13 | diagramMicro | [416.8744, 538.8171, 73.7451, 22.0103] |
| nodes.shape_518 | 1 | 13 | diagramMicro | [489.8277, 538.8171, 73.7451, 22.0103] |
| nodes.shape_519 | 1 | 13 | diagramMicro | [702.8975, 514.0395, 73.7451, 22.0103] |
| nodes.shape_520 | 1 | 13 | diagramMicro | [775.8508, 514.0395, 73.7451, 22.0103] |
| nodes.shape_521 | 1 | 17 | diagramMicro | [692.1435, 538.8171, 95.253, 22.0103] |
| nodes.shape_522 | 1 | 13 | diagramMicro | [775.8508, 538.8171, 73.7451, 22.0103] |
| nodes.shape_523 | 1 | 17 | compactBody | [546.9267, 169.4614, 155.23, 34.2373] |
| nodes.shape_524 | 1 | 20 | diagramMicro | [319.2203, 232.41, 112.725, 22.0103] |
| nodes.shape_525 | 1 | 17 | diagramMicro | [451.9717, 229.7023, 95.3893, 22.0103] |
| nodes.shape_526 | 1 | 17 | diagramMicro | [577.5708, 229.7023, 95.3893, 22.0103] |
| nodes.shape_527 | 1 | 17 | diagramMicro | [702.6676, 229.7023, 95.3893, 22.0103] |
| nodes.shape_528 | 1 | 17 | diagramMicro | [827.7559, 232.41, 95.3893, 22.0103] |
| nodes.shape_534 | 1 | 19 | diagramCompact | [563.956, 435.0068, 123.7685, 27.7406] |
| nodes.shape_535 | 1 | 13 | diagramMicro | [489.8277, 440.2433, 73.7451, 22.0103] |
| nodes.shape_536 | 1 | 13 | diagramMicro | [392.1139, 442.5082, 73.7451, 22.0103] |
| nodes.shape_537 | 1 | 13 | diagramMicro | [792.9566, 442.5082, 73.7451, 22.0103] |
| nodes.shape_538 | 1 | 18 | diagramMicro | [682.8882, 440.2433, 98.429, 22.0103] |
| nodes.shape_539 | 1 | 13 | diagramMicro | [311.6423, 527.9269, 73.7451, 22.0103] |
| nodes.shape_540 | 1 | 13 | diagramMicro | [889.5379, 527.9269, 73.7451, 22.0103] |
| nodes.shape_546 | 1 | 19 | diagramMicro | [314.0604, 362.3516, 107.2842, 22.0103] |
| nodes.shape_547 | 1 | 17 | diagramMicro | [475.9318, 362.3516, 96.7431, 22.0103] |
| nodes.shape_548 | 1 | 17 | diagramMicro | [319.3225, 399.9011, 96.7431, 22.0103] |
| nodes.shape_549 | 1 | 17 | diagramMicro | [475.9318, 399.9011, 96.7431, 22.0103] |
| nodes.shape_550 | 1 | 17 | diagramMicro | [681.2704, 362.3516, 96.7431, 22.0103] |
| nodes.shape_551 | 1 | 17 | diagramMicro | [837.8712, 362.3516, 96.7431, 22.0103] |
| nodes.shape_552 | 1 | 17 | diagramMicro | [681.2704, 399.9011, 96.7431, 22.0103] |
| nodes.shape_553 | 1 | 17 | diagramMicro | [837.8712, 399.9011, 96.7431, 22.0103] |
| nodes.shape_569 | 1 | 20 | diagramMicro | [362.0744, 580.113, 111.3542, 22.0103] |
| nodes.shape_570 | 1 | 18 | diagramMicro | [577.5027, 577.5586, 98.429, 22.0103] |
| nodes.shape_573 | 1 | 18 | diagramMicro | [758.8811, 580.113, 98.429, 22.0103] |
### page-32

底5云球体环，中6技术能力环，顶4价值球体斜环；中央大上箭头；左右8行业

Layout为`source-spatial-32`，原型为`templates/prototypes/source-spatial-32.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_14 | 1 | 10 | diagramCompact | [347.6035, 557.1571, 69.1136, 23.5867] |
| nodes.shape_22 | 1 | 10 | diagramCompact | [474.7755, 576.6721, 69.1136, 23.5867] |
| nodes.shape_26 | 1 | 10 | diagramCompact | [601.9474, 580.6059, 69.1136, 23.5867] |
| nodes.shape_31 | 1 | 10 | diagramCompact | [731.723, 577.3372, 69.1136, 24.3735] |
| nodes.shape_452 | 1 | 10 | diagramCompact | [860.4928, 557.1571, 69.1136, 24.3735] |
| nodes.shape_478 | 1 | 13 | diagramMicro | [223.1001, 242.4189, 70.2167, 21.2264] |
| nodes.shape_35 | 1 | 7 | diagramMicro | [213.2371, 317.5752, 38.2757, 21.2264] |
| nodes.shape_38 | 1 | 16 | diagramMicro | [186.6169, 392.7314, 91.5161, 21.2264] |
| nodes.shape_41 | 1 | 11 | diagramMicro | [228.4209, 467.8796, 59.5751, 21.2264] |
| nodes.shape_44 | 1 | 11 | diagramMicro | [990.8036, 242.4189, 59.5751, 21.2264] |
| nodes.shape_47 | 1 | 7 | diagramMicro | [1023.9451, 317.5752, 38.2757, 21.2264] |
| nodes.shape_50 | 1 | 11 | diagramMicro | [1013.2954, 392.7314, 59.5751, 21.2264] |
| nodes.shape_53 | 1 | 11 | diagramMicro | [990.8036, 467.8796, 59.5751, 21.2264] |
| nodes.shape_59 | 1 | 10 | diagramCompact | [602.2069, 287.3537, 69.1136, 23.5867] |
| nodes.shape_60 | 1 | 14 | diagramMicro | [597.4134, 309.4642, 78.9522, 21.2021] |
| nodes.shape_54 | 1 | 12 | diagramMicro | [404.5507, 320.0734, 69.1136, 22.2808] |
| nodes.shape_55 | 1 | 12 | diagramMicro | [494.3229, 359.3224, 69.1136, 22.2808] |
| nodes.shape_56 | 1 | 12 | diagramMicro | [731.723, 269.542, 69.1136, 22.2808] |
| nodes.shape_57 | 1 | 12 | diagramMicro | [820.9031, 305.5061, 69.1136, 22.2808] |
| nodes.shape_196 | 1 | 15 | diagramMicro | [399.384, 435.8899, 81.4179, 21.6239] |
| nodes.shape_201 | 1 | 15 | diagramMicro | [447.8308, 464.1567, 81.4179, 21.6239] |
| nodes.shape_202 | 1 | 15 | diagramMicro | [532.7527, 474.4982, 81.4179, 21.6239] |
| nodes.shape_203 | 1 | 15 | diagramMicro | [638.0331, 474.4982, 81.4179, 22.2808] |
| nodes.shape_204 | 1 | 15 | diagramMicro | [735.673, 464.1567, 81.4179, 21.6239] |
| nodes.shape_205 | 1 | 15 | diagramMicro | [783.5683, 435.8899, 81.4179, 22.2808] |
### page-33

底4源系统球体，中源头倒锥汇聚到总线环，上效益与应用3球；左右弧箭头；右3段说明

Layout为`source-spatial-33`，原型为`templates/prototypes/source-spatial-33.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_456 | 1 | 16 | caption | [443.1031, 510.2242, 120.1097, 33.2252] |
| nodes.shape_15 | 1 | 13 | diagramMicro | [162.8252, 572.1713, 73.8043, 23.2684] |
| nodes.shape_16 | 1 | 13 | diagramMicro | [299.6342, 610.1641, 73.8043, 23.2684] |
| nodes.shape_18 | 1 | 13 | diagramMicro | [629.3822, 610.1641, 73.8043, 23.2684] |
| nodes.shape_20 | 1 | 13 | diagramMicro | [774.3797, 572.1713, 73.8043, 23.2684] |
| nodes.shape_458 | 1 | 13 | diagramMicro | [169.766, 359.6161, 73.8043, 23.3427] |
| nodes.shape_459 | 1 | 13 | diagramMicro | [745.9471, 359.6161, 73.8043, 23.3427] |
| nodes.shape_460 | 1 | 13 | diagramMicro | [653.1959, 396.981, 73.8043, 23.3427] |
| nodes.shape_461 | 1 | 13 | diagramMicro | [289.4873, 396.981, 73.8043, 23.3427] |
| nodes.shape_33 | 1 | 13 | diagramMicro | [245.6195, 269.0546, 73.8043, 23.3427] |
| nodes.shape_35 | 1 | 13 | diagramMicro | [690.9078, 269.0546, 73.8043, 23.3427] |
| nodes.shape_42 | 1 | 13 | diagramMicro | [594.6036, 285.2252, 73.8043, 23.3427] |
| nodes.shape_43 | 1 | 13 | diagramMicro | [346.7163, 285.2252, 73.8043, 23.3427] |
| nodes.shape_44 | 1 | 13 | diagramMicro | [465.9831, 290.8439, 73.8043, 23.3427] |
| nodes.shape_536 | 1 | 11 | diagramMicro | [903.7852, 194.1514, 60.0053, 20.7647] |
| nodes.shape_540 | 1 | 68 | diagramMicro | [885.2432, 226.4841, 186.3782, 40.1412] |
| nodes.shape_205 | 1 | 11 | diagramMicro | [916.4935, 346.2054, 60.0053, 20.7647] |
| nodes.shape_213 | 1 | 11 | diagramMicro | [932.9863, 517.6195, 60.0053, 20.7647] |
| nodes.shape_218 | 1 | 111 | diagramMicro | [897.9516, 377.4392, 205.0772, 56.8323] |
| nodes.shape_219 | 1 | 68 | diagramMicro | [914.4443, 550.3407, 186.3782, 40.1412] |
| nodes.shape_552 | 1 | 21 | diagramMicro | [280.0346, 627.3262, 113.7224, 20.6738] |
| nodes.shape_553 | 1 | 21 | diagramMicro | [608.7001, 627.3262, 113.7224, 20.6738] |
| nodes.shape_554 | 1 | 21 | diagramMicro | [713.416, 591.8618, 113.7224, 20.6738] |
| nodes.shape_555 | 1 | 21 | diagramMicro | [182.5157, 591.0438, 113.7224, 20.6738] |
| nodes.shape_522 | 1 | 9 | diagramMicro | [593.8847, 224.1953, 50.7673, 21.8058] |
| nodes.shape_566 | 1 | 10 | diagramMicro | [632.4642, 169.5031, 58.4518, 20.2689] |
| nodes.shape_573 | 1 | 10 | diagramMicro | [592.2239, 157.621, 58.4518, 20.2689] |
| nodes.shape_574 | 1 | 10 | diagramMicro | [548.447, 170.8995, 58.4518, 20.2689] |
| nodes.shape_525 | 1 | 9 | diagramMicro | [365.754, 224.1953, 50.7673, 21.8058] |
| nodes.shape_578 | 1 | 10 | diagramMicro | [403.3255, 169.5031, 58.4518, 20.2689] |
| nodes.shape_585 | 1 | 10 | diagramMicro | [363.0851, 157.621, 58.4518, 20.2689] |
| nodes.shape_586 | 1 | 10 | diagramMicro | [319.3082, 170.8995, 58.4518, 20.2689] |
| nodes.shape_524 | 1 | 9 | diagramMicro | [478.6336, 247.7033, 50.7673, 21.8058] |
| nodes.shape_590 | 1 | 10 | diagramMicro | [514.7591, 195.7213, 58.4518, 20.2689] |
| nodes.shape_597 | 1 | 10 | diagramMicro | [474.5187, 183.8475, 58.4518, 20.2689] |
| nodes.shape_598 | 1 | 10 | diagramMicro | [430.7418, 197.1177, 58.4518, 20.2689] |
| nodes.shape_604 | 1 | 13 | diagramMicro | [291.7349, 339.2233, 73.8043, 23.3427] |
| nodes.shape_606 | 1 | 13 | diagramMicro | [637.926, 339.2233, 73.8043, 23.3427] |
| nodes.shape_48 | 1 | 16 | caption | [443.1031, 333.6706, 120.1097, 33.2252] |
| nodes.shape_49 | 1 | 84 | diagramMicro | [386.874, 359.046, 228.8413, 35.8858] |
### page-34

巨大上升箭头，3层环分别第一/二/三步；左右每层4项动作；顶营业额目标

Layout为`source-spatial-34`，原型为`templates/prototypes/source-spatial-34.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_3 | 1 | 69 | caption | [550.1615, 137.0714, 169.1944, 63.2873] |
| nodes.shape_19 | 1 | 13 | caption | [584.6569, 498.0707, 97.0619, 21.1767] |
| nodes.shape_20 | 1 | 50 | diagramMicro | [565.243, 527.3405, 135.882, 33.7981] |
| nodes.shape_22 | 1 | 13 | caption | [584.6569, 383.4046, 97.0619, 21.1767] |
| nodes.shape_23 | 1 | 64 | diagramMicro | [546.3774, 412.6744, 173.6131, 34.8558] |
| nodes.shape_24 | 1 | 13 | caption | [584.6569, 287.8625, 97.0619, 21.1767] |
| nodes.shape_25 | 1 | 32 | diagramMicro | [546.3774, 317.1402, 173.6131, 17.0009] |
| nodes.shape_558 | 1 | 18 | diagramCompact | [750.3963, 283.0521, 116.4524, 22.7828] |
| nodes.shape_566 | 1 | 18 | diagramCompact | [797.6307, 331.5557, 116.4524, 22.7828] |
| nodes.shape_605 | 1 | 22 | diagramCompact | [844.1442, 385.1203, 143.6147, 22.7828] |
| nodes.shape_609 | 1 | 18 | diagramCompact | [879.3918, 435.9429, 114.7366, 22.7828] |
| nodes.shape_618 | 1 | 18 | diagramCompact | [924.7302, 491.7012, 118.2935, 22.7828] |
| nodes.shape_622 | 1 | 17 | diagramCompact | [963.9263, 540.2048, 111.0466, 22.7828] |
| nodes.shape_13 | 1 | 20 | diagramCompact | [411.7019, 283.0521, 129.1051, 22.7828] |
| nodes.shape_16 | 1 | 18 | diagramCompact | [364.4676, 331.5557, 116.4524, 22.7828] |
| nodes.shape_26 | 1 | 22 | diagramCompact | [317.954, 385.1203, 142.8234, 22.7828] |
| nodes.shape_29 | 1 | 16 | diagramCompact | [282.7065, 435.9429, 105.3744, 22.7828] |
| nodes.shape_450 | 1 | 14 | diagramCompact | [237.3681, 491.7012, 91.139, 22.7828] |
| nodes.shape_453 | 1 | 18 | diagramCompact | [181.6489, 540.2048, 116.4524, 22.7828] |

## 使用步骤

1. 先确认材料确有本页型所表达的关系，选择`family=source-spatial`及兼容variant。
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

来源为立体结构逻辑图1122.pptx，逐页结构见variants与来源索引。原始文件指纹及资产处理见asset-provenance.json。当前原型完成结构生成与文本测量，实际渲染和原生编辑范围以交付检查记录为准。

catalog指纹为`498fe133ea2d00699bb4c4ea5bc798e78130623b21eea5d3cc8cb10e125af78b`，tokens指纹为`2bb967b3a61bf7a4072665f712f39ac49458d22ebe9407f269236c21adc366f3`，参数schema指纹为`6981096e740f47c827294403dd132d6609fd537f46b15e8164c4b630b9822a61`。
