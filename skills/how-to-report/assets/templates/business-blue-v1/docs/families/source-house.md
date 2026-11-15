# 房子图战略图.pptx

战略屋与目标支撑

类型为定性关系图，语义入口为`source-house`。

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

屋顶总方法；3列数据分析/用户画像/精细化营销；问题-解法-工具纵向3层；底部总价值

Layout为`source-house-01`，原型为`templates/prototypes/source-house-01.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_44 | 1 | 19 | compactBody | [564.2774, 135.8949, 177.3785, 32.8815] |
| nodes.shape_170 | 1 | 143 | caption | [140.917, 614.3599, 1036.5246, 33.6401] |
| nodes.shape_63 | 1 | 24 | caption | [140.917, 223.844, 60.184, 68.7513] |
| nodes.shape_76 | 1 | 20 | diagramCompact | [85.544, 300.9405, 33.8067, 74.0434] |
| nodes.shape_77 | 1 | 25 | diagramCompact | [85.544, 381.9044, 33.8067, 96.8958] |
| nodes.shape_78 | 1 | 35 | diagramCompact | [85.544, 487.8116, 33.8067, 118.9432] |
| nodes.shape_113 | 1 | 12 | caption | [549.4835, 313.6342, 87.6901, 29.8931] |
| nodes.shape_114 | 1 | 45 | diagramCompact | [549.4835, 336.3015, 285.0528, 26.4328] |
| nodes.shape_123 | 1 | 37 | diagramMicro | [606.4108, 392.5719, 202.9602, 20.9187] |
| nodes.shape_129 | 1 | 37 | diagramMicro | [606.4108, 419.5692, 202.9602, 20.9187] |
| nodes.shape_120 | 1 | 17 | diagramMicro | [508.9784, 392.5719, 92.0847, 20.9187] |
| nodes.shape_128 | 1 | 17 | diagramMicro | [508.9784, 419.5692, 92.0847, 20.9187] |
| nodes.shape_131 | 1 | 17 | diagramMicro | [508.9784, 446.5756, 92.0847, 20.9187] |
| nodes.shape_132 | 1 | 37 | diagramMicro | [606.4108, 446.5756, 202.9602, 20.9187] |
| nodes.shape_239 | 1 | 17 | diagramMicro | [160.5867, 392.5719, 96.2759, 20.9187] |
| nodes.shape_240 | 1 | 17 | diagramMicro | [160.5867, 419.5692, 96.2759, 20.9187] |
| nodes.shape_241 | 1 | 17 | diagramMicro | [160.5867, 446.5756, 96.2759, 20.9187] |
| nodes.shape_236 | 1 | 17 | diagramMicro | [262.4137, 392.5719, 96.2759, 20.9187] |
| nodes.shape_237 | 1 | 17 | diagramMicro | [262.4137, 419.5692, 96.2759, 20.9187] |
| nodes.shape_238 | 1 | 17 | diagramMicro | [262.4137, 446.5756, 96.2759, 20.9187] |
| nodes.shape_233 | 1 | 17 | diagramMicro | [364.2315, 392.5719, 96.2759, 20.9187] |
| nodes.shape_234 | 1 | 17 | diagramMicro | [364.2315, 419.5692, 96.2759, 20.9187] |
| nodes.shape_235 | 1 | 17 | diagramMicro | [364.2315, 446.5756, 96.2759, 20.9187] |
| nodes.shape_275 | 1 | 26 | diagramMicro | [857.6014, 392.5719, 145.7646, 20.9187] |
| nodes.shape_276 | 1 | 26 | diagramMicro | [857.6014, 419.5692, 145.7646, 20.9187] |
| nodes.shape_281 | 1 | 26 | diagramMicro | [857.6014, 446.5756, 145.7646, 20.9187] |
| nodes.shape_266 | 1 | 26 | diagramMicro | [1011.7576, 392.5719, 145.7646, 20.9187] |
| nodes.shape_267 | 1 | 26 | diagramMicro | [1011.7576, 419.5692, 145.7646, 20.9187] |
| nodes.shape_274 | 1 | 26 | diagramMicro | [1011.7576, 446.5756, 145.7646, 20.9187] |
| nodes.shape_296 | 1 | 12 | caption | [201.101, 313.6342, 87.6901, 29.8931] |
| nodes.shape_298 | 1 | 45 | diagramCompact | [201.101, 336.3015, 288.1985, 26.4328] |
| nodes.shape_307 | 1 | 12 | caption | [897.8752, 313.6342, 87.6901, 29.8931] |
| nodes.shape_308 | 1 | 47 | diagramCompact | [897.8752, 336.3015, 296.5808, 26.4328] |
| nodes.shape_332 | 1 | 27 | diagramMicro | [508.9784, 499.8114, 145.9959, 26.5069] |
| nodes.shape_329 | 1 | 27 | diagramMicro | [660.5995, 499.8114, 145.9959, 26.5069] |
| nodes.shape_333 | 1 | 27 | diagramMicro | [508.9784, 534.0344, 145.9959, 26.5069] |
| nodes.shape_330 | 1 | 27 | diagramMicro | [660.5995, 534.0344, 145.9959, 26.5069] |
| nodes.shape_364 | 1 | 35 | diagramMicro | [965.6643, 499.8114, 189.3136, 26.5069] |
| nodes.shape_365 | 1 | 18 | diagramMicro | [857.3609, 499.8114, 99.6621, 26.5069] |
| nodes.shape_362 | 1 | 35 | diagramMicro | [965.6643, 534.0344, 189.3136, 26.5069] |
| nodes.shape_363 | 1 | 18 | diagramMicro | [857.3609, 534.0344, 99.6621, 26.5069] |
| nodes.shape_369 | 1 | 35 | diagramMicro | [965.6643, 568.2481, 189.3136, 26.5069] |
| nodes.shape_370 | 1 | 18 | diagramMicro | [857.3609, 568.2481, 99.6621, 26.5069] |
| nodes.shape_378 | 1 | 26 | diagramMicro | [161.9837, 499.8114, 144.9319, 26.5069] |
| nodes.shape_386 | 1 | 26 | diagramMicro | [315.5755, 499.8114, 144.9319, 26.5069] |
| nodes.shape_389 | 1 | 26 | diagramMicro | [161.9837, 534.0344, 144.9319, 26.5069] |
| nodes.shape_390 | 1 | 26 | diagramMicro | [315.5755, 534.0344, 144.9319, 26.5069] |
| nodes.shape_392 | 1 | 26 | diagramMicro | [161.9837, 568.2481, 144.9319, 26.5069] |
| nodes.shape_393 | 1 | 26 | diagramMicro | [315.5755, 568.2481, 144.9319, 26.5069] |
| nodes.shape_403 | 1 | 24 | caption | [489.2995, 223.844, 60.184, 68.7513] |
| nodes.shape_406 | 1 | 24 | caption | [837.6912, 223.844, 60.184, 68.7513] |
| nodes.shape_409 | 1 | 47 | caption | [140.917, 183.4499, 339.7504, 32.0488] |
| nodes.shape_410 | 1 | 47 | caption | [489.2995, 183.4499, 339.7504, 32.0488] |
| nodes.shape_411 | 1 | 47 | caption | [837.6912, 183.4499, 339.7504, 32.0488] |
| nodes.shape_423 | 1 | 86 | diagramCompact | [208.1695, 235.5847, 272.4979, 45.2698] |
| nodes.shape_427 | 1 | 129 | diagramCompact | [556.552, 226.1662, 272.4979, 64.0976] |
| nodes.shape_430 | 1 | 129 | diagramCompact | [904.9437, 226.1662, 272.4979, 64.0976] |
| nodes.shape_334 | 1 | 17 | diagramMicro | [508.9784, 568.2481, 95.1749, 26.5069] |
| nodes.shape_442 | 1 | 17 | diagramMicro | [610.1948, 568.2481, 95.1749, 26.5069] |
| nodes.shape_443 | 1 | 17 | diagramMicro | [711.4112, 568.2481, 95.1749, 26.5069] |
### page-02

屋顶使命；3根能力支柱；每列分理解业务、方法/项目工具、底层行为规范；多级子模块

Layout为`source-house-02`，原型为`templates/prototypes/source-house-02.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_20 | 1 | 39 | caption | [498.948, 149.1332, 282.3973, 29.6098] |
| nodes.shape_21 | 1 | 19 | caption | [241.835, 199.5093, 141.8264, 31.9467] |
| nodes.shape_22 | 1 | 19 | caption | [576.322, 199.5093, 141.8264, 31.9467] |
| nodes.shape_23 | 1 | 19 | caption | [915.1987, 198.9869, 141.8264, 31.9467] |
| nodes.shape_24 | 1 | 168 | diagramMicro | [229.1241, 255.1365, 229.4552, 60.9333] |
| nodes.shape_25 | 1 | 172 | diagramMicro | [558.3142, 255.1365, 237.1074, 60.6767] |
| nodes.shape_26 | 1 | 164 | diagramMicro | [902.2679, 255.1365, 224.5982, 60.9333] |
| nodes.shape_31 | 1 | 16 | diagramMicro | [149.4132, 423.9975, 91.7711, 21.5636] |
| nodes.shape_34 | 1 | 16 | diagramMicro | [149.4132, 456.2924, 91.7711, 21.5636] |
| nodes.shape_37 | 1 | 17 | diagramMicro | [149.2757, 488.5873, 93.1916, 21.5636] |
| nodes.shape_39 | 1 | 38 | diagramMicro | [247.8101, 424.9689, 207.0394, 21.4902] |
| nodes.shape_40 | 1 | 38 | diagramMicro | [247.1961, 457.2547, 207.855, 21.4902] |
| nodes.shape_41 | 1 | 39 | diagramMicro | [246.8845, 487.3868, 210.9526, 21.4902] |
| nodes.shape_42 | 1 | 55 | diagramMicro | [488.2075, 429.2211, 301.0924, 21.4902] |
| nodes.shape_43 | 1 | 55 | diagramMicro | [488.2075, 459.5182, 301.0924, 21.4902] |
| nodes.shape_44 | 1 | 55 | diagramMicro | [488.2075, 489.8153, 301.0924, 21.4902] |
| nodes.shape_45 | 1 | 54 | diagramMicro | [826.5802, 427.7457, 145.987, 37.4269] |
| nodes.shape_46 | 1 | 52 | diagramMicro | [980.9433, 428.1214, 142.9169, 37.4269] |
| nodes.shape_47 | 1 | 54 | diagramMicro | [826.5802, 473.2463, 145.987, 37.9401] |
| nodes.shape_48 | 1 | 52 | diagramMicro | [980.9433, 473.6221, 142.9169, 37.9401] |
| nodes.shape_49 | 1 | 20 | diagramMicro | [149.2757, 541.9784, 108.0744, 21.4902] |
| nodes.shape_50 | 1 | 35 | diagramMicro | [265.2863, 541.9784, 192.5507, 21.4902] |
| nodes.shape_51 | 1 | 57 | diagramMicro | [149.2757, 610.5731, 308.5613, 21.4902] |
| nodes.shape_52 | 1 | 35 | diagramMicro | [265.5888, 575.3914, 192.5507, 21.4902] |
| nodes.shape_53 | 1 | 20 | diagramMicro | [149.5782, 575.3914, 108.0744, 21.4902] |
| nodes.shape_54 | 1 | 55 | diagramMicro | [488.2075, 542.3633, 301.0924, 21.4902] |
| nodes.shape_55 | 1 | 55 | diagramMicro | [488.2075, 575.6113, 301.0924, 21.4902] |
| nodes.shape_56 | 1 | 55 | diagramMicro | [488.2075, 608.9876, 301.0924, 21.4902] |
| nodes.shape_57 | 1 | 108 | diagramMicro | [827.0017, 535.5451, 296.8585, 38.7832] |
| nodes.shape_58 | 1 | 54 | diagramMicro | [827.0017, 578.1865, 296.8585, 21.4902] |
| nodes.shape_59 | 1 | 26 | diagramMicro | [828.6971, 602.6093, 70.8674, 38.7832] |
| nodes.shape_60 | 1 | 26 | diagramMicro | [903.4685, 602.6093, 70.8674, 38.7832] |
| nodes.shape_61 | 1 | 26 | diagramMicro | [978.2307, 602.6093, 70.8674, 38.7832] |
| nodes.shape_62 | 1 | 26 | diagramMicro | [1052.9929, 602.6093, 70.8674, 38.7832] |
| nodes.shape_64 | 1 | 30 | diagramCompact | [488.3083, 255.9246, 65.6896, 60.6584] |
| nodes.shape_65 | 1 | 30 | diagramCompact | [828.7888, 255.9246, 65.6896, 60.6584] |
| nodes.shape_66 | 1 | 21 | diagramMicro | [155.6541, 344.14, 114.581, 25.1834] |
| nodes.shape_67 | 1 | 33 | diagramMicro | [275.2296, 343.8559, 179.6199, 25.1834] |
| nodes.shape_68 | 1 | 21 | diagramMicro | [156.2131, 374.1988, 114.0128, 25.1834] |
| nodes.shape_69 | 1 | 33 | diagramMicro | [275.2296, 373.9055, 179.6199, 25.1834] |
| nodes.shape_70 | 1 | 55 | diagramMicro | [488.2075, 343.7367, 301.0924, 25.1834] |
| nodes.shape_71 | 1 | 55 | diagramMicro | [488.2075, 374.1438, 301.0924, 25.1834] |
| nodes.shape_72 | 1 | 55 | diagramMicro | [826.5802, 343.4068, 301.0924, 25.1834] |
| nodes.shape_73 | 1 | 55 | diagramMicro | [826.5802, 373.8231, 301.0924, 25.1834] |
| nodes.shape_3 | 1 | 30 | diagramCompact | [156.3872, 255.4114, 65.6896, 60.6584] |
### page-03

上方背景；中部3种达人策略+6个案例；下方项目成果指标与长尾效果

Layout为`source-house-03`，原型为`templates/prototypes/source-house-03.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| charts.chart_130.title | 1 | 24 | diagramMicro | [206.5577, 533.6392, 284.621755, 20] |
| charts.chart_130.axis_caption | 0 | 28 | diagramMicro | [544.0518, 533.6392, 180, 20] |
| charts.chart_130.chart_ticks.0 | 1 | 16 | diagramMicro | [206.5577, 616.0, 36, 20] |
| charts.chart_130.chart_ticks.1 | 1 | 16 | diagramMicro | [206.5577, 549.6392, 36, 20] |
| charts.chart_130.categories.0 | 1 | 24 | diagramMicro | [252.5577, 628.0, 145.83136666666667, 20] |
| charts.chart_130.categories.1 | 1 | 24 | diagramMicro | [406.3890666666667, 628.0, 145.83136666666667, 20] |
| charts.chart_130.categories.2 | 1 | 24 | diagramMicro | [560.2204333333334, 628.0, 145.83136666666667, 20] |
| charts.chart_130.series.0.name | 0 | 16 | diagramMicro | [248.5577, 553.6392, 140.74705, 20] |
| nodes.shape_7 | 1 | 608 | diagramCompact | [201.2214, 122.6033, 961.9843, 71.3363] |
| nodes.shape_11 | 1 | 66 | compactBody | [388.2986, 206.4837, 595.4267, 32.9259] |
| nodes.shape_16 | 1 | 96 | compactBody | [115.6826, 205.0477, 79.5724, 334.6508] |
| nodes.shape_17 | 1 | 24 | compactBody | [114.8674, 545.3313, 79.5724, 98.4905] |
| nodes.shape_20 | 1 | 31 | caption | [271.0476, 265.0258, 228.2299, 29.9335] |
| nodes.shape_48 | 1 | 168 | diagramCompact | [252.2407, 322.2617, 265.8436, 68.5107] |
| nodes.shape_22 | 1 | 31 | caption | [595.3685, 265.9986, 228.2299, 29.9335] |
| nodes.shape_49 | 1 | 196 | diagramCompact | [554.8643, 323.2344, 309.2291, 68.5107] |
| nodes.shape_24 | 1 | 62 | caption | [911.6571, 255.502, 228.2299, 50.8897] |
| nodes.shape_50 | 1 | 156 | diagramCompact | [900.8825, 323.2159, 249.7883, 68.5107] |
| nodes.shape_55 | 1 | 24 | caption | [223.2708, 399.3327, 34.5842, 125.728] |
| nodes.shape_101 | 1 | 34 | diagramCompact | [329.7009, 420.7984, 112.137, 41.9124] |
| nodes.shape_102 | 1 | 17 | diagramCompact | [329.7009, 478.6272, 112.137, 25.4495] |
| nodes.shape_107 | 1 | 17 | diagramCompact | [644.0069, 421.2431, 112.137, 25.4495] |
| nodes.shape_108 | 1 | 17 | diagramCompact | [644.0069, 480.1929, 112.137, 25.4495] |
| nodes.shape_109 | 1 | 17 | diagramCompact | [967.707, 420.7984, 112.137, 25.4495] |
| nodes.shape_110 | 1 | 17 | diagramCompact | [967.707, 478.6272, 112.137, 25.4495] |
| nodes.shape_131 | 1 | 18 | diagramMicro | [266.6284, 591.4868, 50.5654, 32.9259] |
| nodes.shape_132 | 1 | 22 | diagramMicro | [605.9207, 591.4868, 59.8484, 32.9259] |
| nodes.shape_134 | 1 | 116 | diagramCompact | [733.5386, 562.0073, 183.2973, 68.5107] |
| nodes.shape_135 | 1 | 17 | diagramCompact | [953.1618, 567.3344, 112.137, 25.4495] |
| nodes.shape_137 | 1 | 8 | caption | [1047.1498, 556.8563, 60.08, 35.9276] |
| nodes.shape_136 | 1 | 20 | diagramCompact | [953.1618, 605.0685, 127.5901, 25.4495] |
| nodes.shape_138 | 1 | 11 | caption | [1065.2896, 594.5904, 79.5724, 35.9276] |
### page-04

背景双栏含树状筛选与维度表；中段私域矩阵和双向信息模型；底部3类收益与指标

Layout为`source-house-04`，原型为`templates/prototypes/source-house-04.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_6 | 1 | 56 | compactBody | [115.8823, 334.8782, 79.2983, 203.5037] |
| nodes.shape_7 | 1 | 24 | compactBody | [115.9192, 544.8632, 79.2983, 102.6382] |
| nodes.shape_11 | 1 | 36 | caption | [776.7663, 122.4097, 265.8973, 29.8304] |
| nodes.shape_15 | 1 | 41 | caption | [272.6047, 123.3699, 298.5528, 29.8304] |
| nodes.shape_18 | 1 | 18 | diagramCompact | [220.3762, 220.6901, 59.0883, 41.768] |
| nodes.shape_19 | 1 | 16 | diagramMicro | [333.798, 175.2291, 90.5713, 23.2198] |
| nodes.shape_20 | 1 | 16 | diagramMicro | [333.798, 229.9596, 90.5713, 23.2198] |
| nodes.shape_21 | 1 | 16 | diagramMicro | [335.4045, 285.2164, 90.5713, 23.2198] |
| nodes.shape_22 | 1 | 18 | diagramMicro | [521.9019, 160.9186, 98.9913, 23.2198] |
| nodes.shape_23 | 1 | 18 | diagramMicro | [521.9019, 188.4686, 98.9913, 23.2198] |
| nodes.shape_24 | 1 | 18 | diagramMicro | [521.9019, 216.0277, 98.9913, 23.2198] |
| nodes.shape_25 | 1 | 18 | diagramMicro | [521.9019, 243.5868, 98.9913, 23.2198] |
| nodes.shape_26 | 1 | 18 | diagramMicro | [521.9019, 271.1368, 98.9913, 23.2198] |
| nodes.shape_27 | 1 | 18 | diagramMicro | [521.9019, 298.6959, 98.9913, 23.2198] |
| nodes.shape_70_cell_0_0 | 1 | 30 | diagramMicro | [654.2153, 161.6692, 162.7227, 22.3732] |
| nodes.shape_70_cell_0_1 | 1 | 60 | diagramMicro | [828.0171, 161.6692, 329.143, 22.3732] |
| nodes.shape_70_cell_1_0 | 1 | 30 | diagramMicro | [654.2153, 189.582, 162.7227, 22.3732] |
| nodes.shape_70_cell_1_1 | 1 | 60 | diagramMicro | [828.0171, 189.582, 329.143, 22.3732] |
| nodes.shape_70_cell_2_0 | 1 | 30 | diagramMicro | [654.2153, 217.4947, 162.7227, 22.3732] |
| nodes.shape_70_cell_2_1 | 1 | 60 | diagramMicro | [828.0171, 217.4947, 329.143, 22.3732] |
| nodes.shape_70_cell_3_0 | 1 | 30 | diagramMicro | [654.2153, 245.4075, 162.7227, 22.3732] |
| nodes.shape_70_cell_3_1 | 1 | 60 | diagramMicro | [828.0171, 245.4075, 329.143, 22.3732] |
| nodes.shape_70_cell_4_0 | 1 | 30 | diagramMicro | [654.2153, 273.3203, 162.7227, 22.3732] |
| nodes.shape_70_cell_4_1 | 1 | 60 | diagramMicro | [828.0171, 273.3203, 329.143, 22.3732] |
| nodes.shape_70_cell_5_0 | 1 | 30 | diagramMicro | [654.2153, 301.233, 162.7227, 22.3732] |
| nodes.shape_70_cell_5_1 | 1 | 60 | diagramMicro | [828.0171, 301.233, 329.143, 22.3732] |
| nodes.shape_73 | 1 | 53 | caption | [278.7167, 337.6757, 384.397, 29.8304] |
| nodes.shape_77 | 1 | 20 | diagramMicro | [192.734, 410.9267, 58.1558, 32.8125] |
| nodes.shape_74 | 1 | 23 | diagramCompact | [253.7888, 378.9821, 145.2279, 25.0848] |
| nodes.shape_79 | 1 | 9 | diagramMicro | [263.4553, 412.8379, 51.5453, 22.3705] |
| nodes.shape_81 | 1 | 9 | diagramMicro | [339.3653, 412.8379, 51.5453, 22.3705] |
| nodes.shape_85 | 1 | 11 | diagramMicro | [257.2418, 441.8742, 63.6769, 22.3705] |
| nodes.shape_86 | 1 | 11 | diagramMicro | [333.558, 442.1604, 63.1506, 22.3705] |
| nodes.shape_75 | 1 | 23 | diagramCompact | [409.3941, 379.6192, 147.5638, 25.0848] |
| nodes.shape_89 | 1 | 21 | diagramMicro | [424.277, 413.4749, 117.8073, 22.3705] |
| nodes.shape_91 | 1 | 24 | diagramMicro | [415.94, 443.019, 131.7299, 22.3705] |
| nodes.shape_76 | 1 | 27 | diagramCompact | [567.7877, 383.9215, 175.4368, 25.0848] |
| nodes.shape_93 | 1 | 12 | diagramMicro | [576.2539, 417.7773, 66.6774, 22.3705] |
| nodes.shape_95 | 1 | 13 | diagramMicro | [664.1939, 417.7773, 73.5465, 22.3705] |
| nodes.shape_97 | 1 | 15 | diagramMicro | [567.3445, 447.3214, 84.5055, 22.3705] |
| nodes.shape_99 | 1 | 12 | diagramMicro | [667.6284, 447.3214, 66.6774, 22.3705] |
| nodes.shape_115 | 1 | 22 | diagramMicro | [191.9308, 491.5915, 60.1777, 32.8125] |
| nodes.shape_117 | 1 | 8 | diagramMicro | [249.1633, 496.8078, 44.7963, 22.3705] |
| nodes.shape_119 | 1 | 24 | diagramMicro | [294.1073, 490.0958, 67.2037, 35.8038] |
| nodes.shape_121 | 1 | 24 | diagramMicro | [376.914, 490.0958, 65.3018, 35.8038] |
| nodes.shape_123 | 1 | 12 | diagramMicro | [459.7853, 496.8078, 66.8713, 22.3705] |
| nodes.shape_125 | 1 | 11 | diagramMicro | [544.0877, 496.8078, 62.8829, 22.3705] |
| nodes.shape_127 | 1 | 12 | diagramMicro | [624.9833, 496.8078, 64.8032, 22.3705] |
| nodes.shape_133 | 1 | 16 | diagramMicro | [696.3139, 490.0958, 44.7963, 35.8038] |
| nodes.shape_141 | 1 | 41 | caption | [809.2833, 337.6665, 297.2695, 29.8304] |
| nodes.shape_146 | 1 | 8 | diagramMicro | [758.6243, 451.236, 44.547, 19.3883] |
| nodes.shape_150 | 1 | 8 | diagramMicro | [1113.4033, 449.7773, 44.547, 19.3883] |
| nodes.shape_164 | 1 | 10 | diagramMicro | [914.0819, 405.8918, 55.7553, 15.0] |
| nodes.shape_165 | 1 | 10 | diagramMicro | [914.4974, 496.9062, 55.7553, 15.0] |
| nodes.shape_172 | 1 | 8 | diagramMicro | [816.854, 397.1887, 44.7963, 19.3883] |
| nodes.shape_173 | 1 | 8 | diagramMicro | [1034.5297, 397.6319, 44.7963, 19.3883] |
| nodes.shape_174 | 1 | 8 | diagramMicro | [1034.3912, 501.8211, 44.7963, 19.3883] |
| nodes.shape_175 | 1 | 8 | diagramMicro | [814.7121, 503.7507, 44.7963, 19.3883] |
| nodes.shape_176 | 1 | 8 | diagramMicro | [898.8852, 454.809, 44.7963, 19.3883] |
| nodes.shape_177 | 1 | 45 | diagramCompact | [203.8777, 550.5505, 289.2649, 26.2666] |
| nodes.shape_178 | 1 | 106 | diagramMicro | [203.8777, 576.8171, 289.2649, 35.1298] |
| nodes.shape_181 | 1 | 45 | diagramCompact | [551.2522, 550.5505, 289.4403, 26.2666] |
| nodes.shape_182 | 1 | 106 | diagramMicro | [551.2522, 576.8171, 289.4403, 34.4928] |
| nodes.shape_184 | 1 | 45 | diagramCompact | [874.6774, 550.5505, 289.4403, 26.2666] |
| nodes.shape_185 | 1 | 106 | diagramMicro | [874.6774, 576.8171, 289.4403, 34.4928] |
| nodes.shape_187 | 1 | 33 | diagramMicro | [218.502, 617.5326, 179.3145, 22.3705] |
| nodes.shape_188 | 1 | 8 | caption | [394.659, 610.7744, 59.8731, 35.8038] |
| nodes.shape_189 | 1 | 14 | diagramMicro | [432.3278, 627.1806, 78.7444, 19.3883] |
| nodes.shape_190 | 1 | 22 | diagramMicro | [501.7565, 610.7744, 59.8731, 35.8038] |
| nodes.shape_191 | 1 | 15 | diagramMicro | [544.3001, 627.1806, 86.3889, 19.3883] |
| nodes.shape_192 | 1 | 33 | diagramMicro | [711.723, 617.5326, 179.3145, 22.3705] |
| nodes.shape_193 | 1 | 8 | caption | [887.88, 610.719, 59.8731, 35.8038] |
| nodes.shape_194 | 1 | 14 | diagramMicro | [925.5488, 627.1252, 78.7444, 19.3883] |
| nodes.shape_195 | 1 | 22 | diagramMicro | [994.9775, 610.719, 59.8731, 35.8038] |
| nodes.shape_196 | 1 | 15 | diagramMicro | [1037.5211, 627.1252, 86.3889, 19.3883] |
### page-05

屋顶总产品；行业/场景6列；应用服务1行；平台服务4组、组内2×2模块；数据服务5模块底座

Layout为`source-house-05`，原型为`templates/prototypes/source-house-05.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_109 | 1 | 14 | diagramCompact | [1094.287, 120, 89.8914, 24.3855] |
| nodes.shape_110 | 1 | 12 | diagramCompact | [130.8197, 269.6241, 79.2505, 25.9137] |
| nodes.shape_111 | 1 | 11 | diagramCompact | [133.3573, 354.2893, 74.1753, 25.9137] |
| nodes.shape_112 | 1 | 11 | diagramCompact | [133.3573, 497.442, 74.1753, 25.9137] |
| nodes.shape_113 | 1 | 11 | diagramCompact | [133.3573, 614.4641, 74.1753, 25.9137] |
| nodes.shape_114 | 1 | 25 | diagramCompact | [264.6711, 614.832, 158.001, 25.9137] |
| nodes.shape_115 | 1 | 19 | diagramCompact | [467.6885, 614.832, 124.5028, 25.9137] |
| nodes.shape_116 | 1 | 19 | diagramCompact | [653.2351, 614.832, 125.9272, 25.9137] |
| nodes.shape_117 | 1 | 25 | diagramCompact | [823.4619, 614.832, 158.001, 25.9137] |
| nodes.shape_118 | 1 | 20 | diagramCompact | [1023.6964, 614.832, 130.0591, 25.9137] |
| nodes.shape_119 | 1 | 21 | diagramCompact | [305.7349, 406.1922, 134.3419, 25.9137] |
| nodes.shape_120 | 1 | 11 | diagramCompact | [581.456, 406.1922, 72.2697, 25.9137] |
| nodes.shape_121 | 1 | 16 | diagramCompact | [787.5204, 406.1922, 101.7964, 25.9137] |
| nodes.shape_122 | 1 | 9 | diagramCompact | [1028.8094, 406.1922, 60.2043, 25.9137] |
| nodes.shape_123 | 1 | 16 | diagramCompact | [321.5548, 461.51, 102.1172, 25.9137] |
| nodes.shape_124 | 1 | 11 | diagramCompact | [586.5689, 461.51, 74.1753, 25.9137] |
| nodes.shape_125 | 1 | 11 | diagramCompact | [801.2083, 461.51, 74.1753, 25.9137] |
| nodes.shape_126 | 1 | 15 | diagramCompact | [1010.8669, 461.51, 96.0798, 25.9137] |
| nodes.shape_127 | 1 | 10 | diagramCompact | [281.6136, 506.3284, 69.0906, 24.3855] |
| nodes.shape_128 | 1 | 10 | diagramCompact | [281.6136, 554.0522, 69.0906, 24.3855] |
| nodes.shape_129 | 1 | 10 | diagramCompact | [393.9094, 506.3284, 69.0906, 24.3855] |
| nodes.shape_130 | 1 | 10 | diagramCompact | [393.9094, 554.0522, 69.0906, 24.3855] |
| nodes.shape_131 | 1 | 10 | diagramCompact | [528.0154, 506.3284, 69.0906, 24.3855] |
| nodes.shape_132 | 1 | 14 | diagramCompact | [515.318, 554.0522, 94.4949, 24.3855] |
| nodes.shape_133 | 1 | 10 | diagramCompact | [639.6887, 506.3284, 69.0906, 24.3855] |
| nodes.shape_134 | 1 | 14 | diagramCompact | [628.8968, 554.0522, 90.6838, 24.3855] |
| nodes.shape_135 | 1 | 14 | diagramCompact | [789.8505, 506.3284, 94.4949, 24.3855] |
| nodes.shape_136 | 1 | 14 | diagramCompact | [789.8505, 554.0522, 94.4949, 24.3855] |
| nodes.shape_137 | 1 | 15 | diagramCompact | [951.6908, 506.3284, 98.7777, 24.3855] |
| nodes.shape_138 | 1 | 10 | diagramCompact | [966.5297, 554.0522, 69.0906, 24.3855] |
| nodes.shape_139 | 1 | 10 | diagramCompact | [1077.2502, 506.3284, 69.0906, 24.3855] |
| nodes.shape_140 | 1 | 14 | diagramCompact | [1064.5527, 554.0522, 94.4949, 24.3855] |
| nodes.shape_141 | 1 | 11 | diagramCompact | [307.2443, 355.8081, 74.1753, 25.9137] |
| nodes.shape_142 | 1 | 11 | diagramCompact | [505.1676, 355.8081, 74.1753, 25.9137] |
| nodes.shape_143 | 1 | 11 | diagramCompact | [701.9118, 355.8081, 74.1753, 25.9137] |
| nodes.shape_144 | 1 | 11 | diagramCompact | [897.5711, 355.8081, 74.1753, 25.9137] |
| nodes.shape_145 | 1 | 11 | diagramCompact | [1090.7777, 355.8081, 74.1753, 25.9137] |
| nodes.shape_146 | 1 | 36 | diagramMicro | [279.3401, 280.482, 97.9193, 43.6675] |
| nodes.shape_147 | 1 | 36 | diagramMicro | [432.747, 280.482, 102.1172, 43.6675] |
| nodes.shape_148 | 1 | 36 | diagramMicro | [591.1724, 280.482, 102.1172, 43.6675] |
| nodes.shape_149 | 1 | 36 | diagramMicro | [736.3911, 280.482, 102.1172, 43.6675] |
| nodes.shape_150 | 1 | 36 | diagramMicro | [892.9864, 280.482, 102.1172, 43.6675] |
| nodes.shape_151 | 1 | 36 | diagramMicro | [1060.3454, 280.482, 102.1172, 43.6675] |
| nodes.shape_152 | 1 | 7 | diagramCompact | [303.9897, 238.9276, 46.2334, 25.9137] |
| nodes.shape_153 | 1 | 7 | diagramCompact | [460.6606, 238.9276, 46.2334, 25.9137] |
| nodes.shape_154 | 1 | 7 | diagramCompact | [619.1143, 238.9276, 46.2334, 25.9137] |
| nodes.shape_155 | 1 | 7 | diagramCompact | [769.5402, 238.9276, 48.1389, 25.9137] |
| nodes.shape_156 | 1 | 11 | diagramCompact | [912.0232, 238.9276, 74.1753, 25.9137] |
| nodes.shape_157 | 1 | 7 | diagramCompact | [1081.7122, 238.9276, 46.2334, 25.9137] |
| nodes.shape_104 | 1 | 27 | body | [476.5559, 168.7521, 299.5877, 36.5829] |
### page-06

屋顶；左开发平台、中央多端接入与统一门户、右监控BI；中部流程平台；下部ESB与8系统；多向接口箭头

Layout为`source-house-06`，原型为`templates/prototypes/source-house-06.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_90 | 1 | 5 | body | [157.1721, 120, 61.7771, 35.3038] |
| nodes.shape_91 | 1 | 18 | caption | [136.5161, 243.9092, 135.316, 26.4733] |
| nodes.shape_92 | 1 | 16 | caption | [570.9947, 243.9092, 120.6046, 26.4733] |
| nodes.shape_93 | 1 | 24 | caption | [971.3166, 243.9092, 179.1316, 26.4733] |
| nodes.shape_94 | 1 | 18 | caption | [663.1596, 454.4118, 135.316, 26.4733] |
| nodes.shape_95 | 1 | 11 | diagramCompact | [168.3787, 302.327, 71.5816, 25.0076] |
| nodes.shape_96 | 1 | 13 | diagramCompact | [161.642, 357.1216, 85.0641, 25.0076] |
| nodes.shape_97 | 1 | 30 | diagramCompact | [154.35, 410.8238, 99.3841, 46.7197] |
| nodes.shape_98 | 1 | 11 | diagramCompact | [168.3787, 486.9026, 71.5816, 25.0076] |
| nodes.shape_99 | 1 | 15 | diagramCompact | [154.8962, 541.151, 98.5465, 25.0076] |
| nodes.shape_100 | 1 | 7 | diagramCompact | [347.046, 599.3321, 44.462, 25.0076] |
| nodes.shape_101 | 1 | 11 | diagramCompact | [423.1521, 599.3321, 71.5816, 25.0076] |
| nodes.shape_102 | 1 | 11 | diagramCompact | [512.5222, 599.3321, 71.5816, 25.0076] |
| nodes.shape_103 | 1 | 7 | diagramCompact | [612.6073, 599.3321, 48.9046, 25.0076] |
| nodes.shape_104 | 1 | 11 | diagramCompact | [690.5341, 599.3321, 71.5816, 25.0076] |
| nodes.shape_105 | 1 | 11 | diagramCompact | [779.6493, 599.3321, 71.5816, 25.0076] |
| nodes.shape_106 | 1 | 11 | diagramCompact | [869.0558, 599.3321, 71.5816, 25.0076] |
| nodes.shape_107 | 1 | 7 | diagramCompact | [971.4987, 599.3321, 45.2267, 25.0076] |
| nodes.shape_108 | 1 | 9 | diagramCompact | [1052.6391, 599.3321, 61.4675, 25.0076] |
| nodes.shape_109 | 1 | 11 | diagramCompact | [1025.0916, 364.5319, 71.5816, 25.0076] |
| nodes.shape_110 | 1 | 11 | diagramCompact | [1025.0916, 321.7723, 71.5816, 25.0076] |
| nodes.shape_111 | 1 | 11 | diagramCompact | [1025.0916, 279.1947, 71.5816, 25.0076] |
| nodes.shape_112 | 1 | 49 | diagramCompact | [471.6106, 350.1391, 314.2655, 25.0076] |
| nodes.shape_113 | 1 | 28 | diagramCompact | [637.4874, 544.7924, 178.2122, 25.0076] |
| nodes.shape_114 | 1 | 9 | diagramCompact | [392.209, 290.5287, 58.0992, 25.0076] |
| nodes.shape_115 | 1 | 12 | diagramCompact | [547.7987, 290.0917, 77.3988, 25.0076] |
| nodes.shape_116 | 1 | 11 | diagramCompact | [724.4906, 290.5287, 71.5816, 25.0076] |
| nodes.shape_117 | 1 | 7 | diagramCompact | [881.8737, 290.5287, 44.6168, 25.0076] |
| nodes.shape_119 | 1 | 26 | body | [492.5671, 171.6174, 289.1123, 35.3038] |
### page-07

屋顶；企业层3决策/赋能/风控中心；项目层全生命周期多角色横向流程；客户层营销/建造/透明/物业链；右侧数据回流栏

Layout为`source-house-07`，原型为`templates/prototypes/source-house-07.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_27 | 1 | 30 | compactBody | [484.4709, 133.6985, 270.9217, 32.1563] |
| nodes.shape_50 | 1 | 50 | caption | [98.2969, 178.4676, 78.4545, 112.1036] |
| nodes.shape_494 | 1 | 9 | diagramMicro | [426.4466, 183.1906, 50.6593, 19.8783] |
| nodes.shape_495 | 1 | 7 | diagramMicro | [380.0489, 183.1906, 40.797, 19.8783] |
| nodes.shape_496 | 1 | 7 | diagramMicro | [333.6512, 183.1906, 40.797, 19.8783] |
| nodes.shape_497 | 1 | 7 | diagramMicro | [287.2626, 183.1906, 40.797, 19.8783] |
| nodes.shape_498 | 1 | 7 | diagramMicro | [240.8649, 183.1906, 40.797, 19.8783] |
| nodes.shape_36 | 1 | 12 | diagramMicro | [180.2348, 181.4172, 67.1174, 23.416] |
| nodes.shape_524 | 1 | 9 | diagramMicro | [735.7405, 183.1906, 50.6593, 19.8783] |
| nodes.shape_528 | 1 | 7 | diagramMicro | [689.3518, 183.1906, 40.797, 19.8783] |
| nodes.shape_535 | 1 | 7 | diagramMicro | [642.9541, 183.1906, 40.797, 19.8783] |
| nodes.shape_536 | 1 | 7 | diagramMicro | [596.5564, 183.1906, 40.797, 19.8783] |
| nodes.shape_537 | 1 | 7 | diagramMicro | [550.1678, 183.1906, 40.797, 19.8783] |
| nodes.shape_523 | 1 | 12 | diagramMicro | [489.5377, 181.4172, 67.1174, 23.416] |
| nodes.shape_541 | 1 | 12 | diagramMicro | [798.8406, 181.4172, 67.1174, 23.416] |
| nodes.shape_548 | 1 | 25 | diagramMicro | [195.8968, 240.301, 136.0354, 19.4168] |
| nodes.shape_549 | 1 | 25 | diagramMicro | [338.8447, 240.301, 136.0354, 19.4168] |
| nodes.shape_552 | 1 | 25 | diagramMicro | [195.8968, 265.1828, 136.0354, 19.4168] |
| nodes.shape_553 | 1 | 25 | diagramMicro | [338.8447, 265.1828, 136.0354, 19.4168] |
| nodes.shape_555 | 1 | 32 | diagramMicro | [246.8546, 213.6007, 177.0677, 23.416] |
| nodes.shape_569 | 1 | 25 | diagramMicro | [505.1997, 240.301, 136.0354, 19.4168] |
| nodes.shape_570 | 1 | 25 | diagramMicro | [648.1476, 240.301, 136.0354, 19.4168] |
| nodes.shape_565 | 1 | 51 | diagramMicro | [505.1997, 265.1828, 278.9833, 19.4168] |
| nodes.shape_562 | 1 | 32 | diagramMicro | [556.1575, 213.6007, 177.0677, 23.416] |
| nodes.shape_131 | 1 | 25 | diagramMicro | [814.4935, 240.301, 136.0354, 19.4168] |
| nodes.shape_132 | 1 | 25 | diagramMicro | [957.4505, 240.301, 136.0354, 19.4168] |
| nodes.shape_129 | 1 | 51 | diagramMicro | [814.4935, 265.1828, 278.9833, 19.4168] |
| nodes.shape_574 | 1 | 32 | diagramMicro | [865.4604, 213.6007, 177.0677, 23.416] |
| nodes.shape_675 | 1 | 25 | caption | [1141.2498, 178.4676, 40.4442, 112.1036] |
| nodes.shape_58 | 1 | 80 | caption | [98.2969, 321.2618, 78.4545, 164.4549] |
| nodes.shape_676 | 1 | 40 | caption | [1141.2498, 321.2618, 40.4442, 164.4549] |
| nodes.shape_452 | 1 | 60 | caption | [98.2969, 516.4072, 78.4545, 131.5928] |
| nodes.shape_652 | 1 | 17 | diagramCompact | [597.2803, 528.2328, 108.3759, 22.5203] |
| nodes.shape_653 | 1 | 21 | diagramCompact | [202.366, 567.3559, 137.7454, 22.5203] |
| nodes.shape_654 | 1 | 21 | diagramCompact | [351.7471, 567.3559, 137.7454, 22.5203] |
| nodes.shape_655 | 1 | 21 | diagramCompact | [501.1281, 567.3559, 137.7454, 22.5203] |
| nodes.shape_656 | 1 | 21 | diagramCompact | [650.5092, 567.3559, 137.7454, 22.5203] |
| nodes.shape_657 | 1 | 21 | diagramCompact | [799.8811, 567.3559, 137.7454, 22.5203] |
| nodes.shape_658 | 1 | 21 | diagramCompact | [949.2622, 567.3559, 137.7454, 22.5203] |
| nodes.shape_628 | 1 | 25 | diagramMicro | [290.4565, 604.9319, 135.0763, 24.6284] |
| nodes.shape_632 | 1 | 25 | diagramMicro | [420.0045, 604.9319, 135.0763, 24.6284] |
| nodes.shape_633 | 1 | 25 | diagramMicro | [549.5616, 604.9319, 135.0763, 24.6284] |
| nodes.shape_634 | 1 | 25 | diagramMicro | [679.1187, 604.9319, 135.0763, 24.6284] |
| nodes.shape_635 | 1 | 25 | diagramMicro | [808.6667, 604.9319, 135.0763, 24.6284] |
| nodes.shape_636 | 1 | 25 | diagramMicro | [938.2237, 604.9319, 135.0763, 24.6284] |
| nodes.shape_662 | 1 | 16 | diagramMicro | [202.366, 605.5381, 88.0905, 23.416] |
| nodes.shape_677 | 1 | 30 | caption | [1141.2498, 516.4072, 40.4442, 131.5928] |
| nodes.shape_148 | 1 | 19 | diagramMicro | [230.6589, 406.5293, 105.4263, 24.6284] |
| nodes.shape_158 | 1 | 20 | diagramMicro | [328.3582, 406.5293, 110.9546, 24.6284] |
| nodes.shape_159 | 1 | 20 | diagramMicro | [431.5949, 406.5293, 110.9546, 24.6284] |
| nodes.shape_160 | 1 | 20 | diagramMicro | [534.8225, 406.5293, 110.9546, 24.6284] |
| nodes.shape_161 | 1 | 20 | diagramMicro | [638.0592, 406.5293, 110.9546, 24.6284] |
| nodes.shape_162 | 1 | 20 | diagramMicro | [741.2959, 406.5293, 110.9546, 24.6284] |
| nodes.shape_163 | 1 | 20 | diagramMicro | [844.5326, 406.5293, 110.9546, 24.6284] |
| nodes.shape_164 | 1 | 20 | diagramMicro | [947.7602, 406.5293, 110.9546, 24.6284] |
| nodes.shape_166 | 1 | 9 | diagramMicro | [258.1555, 433.6549, 50.4331, 23.416] |
| nodes.shape_167 | 1 | 9 | diagramMicro | [360.0621, 433.6549, 50.4331, 23.416] |
| nodes.shape_168 | 1 | 9 | diagramMicro | [463.0545, 433.6549, 50.4331, 23.416] |
| nodes.shape_169 | 1 | 9 | diagramMicro | [566.0469, 433.6549, 50.4331, 23.416] |
| nodes.shape_170 | 1 | 9 | diagramMicro | [669.0393, 433.6549, 50.4331, 23.416] |
| nodes.shape_171 | 1 | 9 | diagramMicro | [772.0407, 433.6549, 50.4331, 23.416] |
| nodes.shape_172 | 1 | 9 | diagramMicro | [875.0331, 433.6549, 50.4331, 23.416] |
| nodes.shape_174 | 1 | 9 | diagramMicro | [978.0255, 433.6549, 50.4331, 23.416] |
| nodes.shape_1045 | 1 | 13 | diagramMicro | [230.6589, 356.9286, 73.1433, 24.6284] |
| nodes.shape_1046 | 1 | 13 | diagramMicro | [314.5421, 356.9286, 73.1433, 24.6284] |
| nodes.shape_1064 | 1 | 13 | diagramMicro | [398.4162, 356.9286, 73.1433, 24.6284] |
| nodes.shape_1065 | 1 | 13 | diagramMicro | [482.2994, 356.9286, 73.1433, 24.6284] |
| nodes.shape_1067 | 1 | 13 | diagramMicro | [566.1826, 356.9286, 73.1433, 24.6284] |
| nodes.shape_1068 | 1 | 13 | diagramMicro | [650.0568, 356.9286, 73.1433, 24.6284] |
| nodes.shape_1070 | 1 | 13 | diagramMicro | [733.94, 356.9286, 73.1433, 24.6284] |
| nodes.shape_1071 | 1 | 13 | diagramMicro | [817.8232, 356.9286, 73.1433, 24.6284] |
| nodes.shape_1073 | 1 | 13 | diagramMicro | [901.6973, 356.9286, 73.1433, 24.6284] |
| nodes.shape_1074 | 1 | 13 | diagramMicro | [985.5805, 356.9286, 73.1433, 24.6284] |
| nodes.shape_1085 | 1 | 15 | diagramMicro | [194.7567, 361.8326, 21.335, 83.3041] |
| nodes.shape_576 | 1 | 15 | diagramMicro | [1073.291, 361.8326, 21.335, 83.3041] |
| nodes.shape_579 | 1 | 14 | diagramMicro | [605.7039, 331.1149, 77.9659, 17.0915] |
| nodes.shape_580 | 1 | 14 | diagramMicro | [605.7039, 460.102, 77.9659, 17.0915] |
| nodes.shape_686 | 1 | 23 | diagramMicro | [575.2758, 294.2085, 127.1775, 23.416] |
| nodes.shape_688 | 1 | 24 | diagramMicro | [572.3804, 489.3539, 132.9591, 23.416] |
| nodes.shape_692 | 1 | 14 | diagramMicro | [1101.5838, 214.9217, 42.8781, 39.2046] |
| nodes.shape_693 | 1 | 14 | diagramMicro | [1101.5838, 383.8914, 42.8781, 39.2046] |
| nodes.shape_694 | 1 | 14 | diagramMicro | [1101.5838, 562.6058, 42.8781, 39.2046] |
| nodes.shape_31 | 1 | 13 | diagramMicro | [1023.5546, 183.1906, 72.1481, 19.8783] |
| nodes.shape_32 | 1 | 13 | diagramMicro | [941.5081, 183.1906, 72.1481, 19.8783] |
| nodes.shape_33 | 1 | 13 | diagramMicro | [859.4616, 183.1906, 72.1481, 19.8783] |
| nodes.shape_53 | 1 | 11 | diagramMicro | [276.3146, 383.6109, 61.3991, 23.416] |
| nodes.shape_54 | 1 | 11 | diagramMicro | [564.9883, 383.6109, 61.3991, 23.416] |
| nodes.shape_55 | 1 | 11 | diagramMicro | [882.6876, 383.6109, 61.3991, 23.416] |
### page-08

屋顶目标；背景行；两痛点；3项产品体验优化及各6细项；一条定制营销说明；底部收获

Layout为`source-house-08`，原型为`templates/prototypes/source-house-08.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_5 | 1 | 39 | compactBody | [445.8572, 134.8335, 353.7959, 30.8835] |
| nodes.shape_49 | 1 | 16 | diagramCompact | [125.7168, 608.5657, 52.5211, 39.4342] |
| nodes.shape_71 | 1 | 24 | diagramCompact | [125.7168, 233.393, 52.5211, 58.9949] |
| nodes.shape_33 | 1 | 144 | diagramCompact | [199.7451, 239.1109, 457.6301, 47.5592] |
| nodes.shape_34 | 1 | 144 | diagramCompact | [682.7146, 239.1109, 457.6301, 47.5592] |
| nodes.shape_25 | 1 | 16 | diagramCompact | [125.7168, 174.4589, 52.5211, 47.5679] |
| nodes.shape_35 | 1 | 147 | diagramCompact | [199.7451, 185.521, 928.6164, 25.4437] |
| nodes.shape_78 | 1 | 136 | diagramCompact | [125.7168, 303.7542, 52.5211, 293.454] |
| nodes.shape_132 | 1 | 27 | caption | [197.2077, 497.5364, 69.5096, 77.6345] |
| nodes.shape_84 | 1 | 28 | caption | [320.2985, 312.5222, 204.7661, 30.4664] |
| nodes.shape_94 | 1 | 36 | caption | [582.4085, 312.5222, 264.7864, 30.4664] |
| nodes.shape_110 | 1 | 33 | caption | [885.3083, 312.5222, 243.2358, 30.4664] |
| nodes.shape_149 | 1 | 300 | diagramMicro | [326.3466, 510.6145, 815.1452, 40.1034] |
| nodes.shape_160 | 1 | 300 | diagramMicro | [326.3466, 549.2232, 812.182, 40.1034] |
| nodes.shape_50 | 1 | 132 | caption | [192.7759, 608.6092, 954.5207, 39.3473] |
| nodes.shape_103 | 1 | 21 | caption | [203.9249, 347.7158, 56.0839, 77.6345] |
| nodes.shape_98 | 1 | 22 | diagramMicro | [719.1857, 352.304, 119.4672, 28.7458] |
| nodes.shape_90 | 1 | 22 | diagramMicro | [298.826, 352.304, 119.4672, 28.7458] |
| nodes.shape_88 | 1 | 22 | diagramMicro | [427.0612, 352.304, 119.4672, 28.7458] |
| nodes.shape_102 | 1 | 22 | diagramMicro | [590.9505, 352.304, 119.4672, 28.7458] |
| nodes.shape_116 | 1 | 22 | diagramMicro | [883.075, 352.304, 119.4672, 28.7458] |
| nodes.shape_114 | 1 | 22 | diagramMicro | [1011.3101, 352.304, 119.4672, 28.7458] |
| nodes.shape_99 | 1 | 22 | diagramMicro | [719.1857, 389.0705, 119.4672, 28.7458] |
| nodes.shape_91 | 1 | 22 | diagramMicro | [298.826, 389.0705, 119.4672, 28.7458] |
| nodes.shape_89 | 1 | 22 | diagramMicro | [427.0612, 389.0705, 119.4672, 28.7458] |
| nodes.shape_104 | 1 | 22 | diagramMicro | [590.9505, 389.0705, 119.4672, 28.7458] |
| nodes.shape_118 | 1 | 22 | diagramMicro | [883.075, 389.0705, 119.4672, 28.7458] |
| nodes.shape_115 | 1 | 22 | diagramMicro | [1011.3101, 389.0705, 119.4672, 28.7458] |
| nodes.shape_216 | 1 | 22 | diagramMicro | [719.1857, 425.837, 119.4672, 28.7458] |
| nodes.shape_217 | 1 | 22 | diagramMicro | [298.826, 425.837, 119.4672, 28.7458] |
| nodes.shape_218 | 1 | 22 | diagramMicro | [427.0612, 425.837, 119.4672, 28.7458] |
| nodes.shape_219 | 1 | 22 | diagramMicro | [590.9505, 425.837, 119.4672, 28.7458] |
| nodes.shape_220 | 1 | 22 | diagramMicro | [883.075, 425.837, 119.4672, 28.7458] |
| nodes.shape_221 | 1 | 22 | diagramMicro | [1011.3101, 425.837, 119.4672, 28.7458] |
| nodes.shape_20 | 1 | 28 | caption | [612.423, 481.8774, 204.7661, 30.4664] |
### page-09

屋顶总规划；起步/运营/变革3阶段水平箭头；每阶段目标、策略、能力图、持续改进4层

Layout为`source-house-09`，原型为`templates/prototypes/source-house-09.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_184 | 1 | 35 | caption | [505.2691, 131.7381, 257.7319, 29.5449] |
| nodes.shape_55 | 1 | 11 | caption | [288.9865, 172.9879, 81.7347, 27.0094] |
| nodes.shape_56 | 1 | 11 | caption | [581.8663, 172.9879, 79.3571, 27.0094] |
| nodes.shape_57 | 1 | 11 | caption | [922.0894, 172.9879, 79.3571, 27.0094] |
| nodes.shape_13 | 1 | 86 | diagramMicro | [213.5199, 227.655, 232.6761, 30.1683] |
| nodes.shape_14 | 1 | 118 | diagramMicro | [460.1621, 227.655, 323.3557, 30.1683] |
| nodes.shape_15 | 1 | 120 | diagramMicro | [797.4839, 227.655, 328.5764, 30.1683] |
| nodes.shape_479 | 1 | 7 | diagramCompact | [158.329, 227.655, 45.2234, 30.1683] |
| nodes.shape_484 | 1 | 21 | diagramCompact | [158.329, 586.7572, 45.2234, 61.2345] |
| nodes.shape_482 | 1 | 49 | diagramCompact | [158.329, 264.2743, 45.2234, 125.3038] |
| nodes.shape_144 | 1 | 15 | diagramCompact | [220.0457, 286.4371, 96.7066, 24.1746] |
| nodes.shape_145 | 1 | 80 | diagramMicro | [220.0457, 306.8292, 217.0142, 32.9034] |
| nodes.shape_149 | 1 | 80 | diagramMicro | [220.0457, 334.4953, 220.0319, 32.9034] |
| nodes.shape_156 | 1 | 15 | diagramCompact | [465.0253, 273.3855, 96.7066, 24.1746] |
| nodes.shape_157 | 1 | 116 | diagramMicro | [465.0253, 293.4035, 316.8299, 32.9034] |
| nodes.shape_174 | 1 | 11 | diagramCompact | [465.0253, 327.1548, 69.8386, 24.1746] |
| nodes.shape_175 | 1 | 116 | diagramMicro | [465.0253, 347.1729, 316.8299, 32.9034] |
| nodes.shape_512 | 1 | 19 | diagramCompact | [802.3471, 273.3855, 123.5663, 24.1746] |
| nodes.shape_513 | 1 | 116 | diagramMicro | [802.3471, 293.4035, 316.8299, 32.9034] |
| nodes.shape_515 | 1 | 17 | diagramCompact | [802.3471, 327.1548, 110.1323, 24.1746] |
| nodes.shape_516 | 1 | 116 | diagramMicro | [802.3471, 347.1729, 316.8299, 32.9034] |
| nodes.shape_483 | 1 | 70 | diagramCompact | [158.329, 396.0208, 45.2234, 182.2736] |
| nodes.shape_461 | 1 | 19 | diagramMicro | [567.9501, 452.0596, 107.1728, 22.1129] |
| nodes.shape_465 | 1 | 12 | diagramMicro | [701.6502, 463.5234, 70.1379, 22.1379] |
| nodes.shape_467 | 1 | 12 | diagramMicro | [471.8836, 463.5234, 70.1379, 22.1379] |
| nodes.shape_468 | 1 | 12 | diagramMicro | [701.0516, 436.2896, 70.1379, 22.1379] |
| nodes.shape_469 | 1 | 12 | diagramMicro | [471.8836, 436.2896, 70.1379, 22.1379] |
| nodes.shape_473 | 1 | 12 | diagramMicro | [540.5999, 485.4784, 70.1379, 22.1379] |
| nodes.shape_474 | 1 | 12 | diagramMicro | [632.9338, 486.0437, 70.1379, 22.1379] |
| nodes.shape_475 | 1 | 12 | diagramMicro | [540.5999, 414.7087, 70.1379, 22.1379] |
| nodes.shape_476 | 1 | 12 | diagramMicro | [632.9338, 414.7087, 70.1379, 22.1379] |
| nodes.shape_481 | 1 | 39 | diagramMicro | [856.1995, 537.4604, 211.1368, 22.1379] |
| nodes.shape_485 | 1 | 12 | diagramMicro | [1041.2747, 449.9065, 70.1379, 22.1379] |
| nodes.shape_488 | 1 | 12 | diagramMicro | [812.115, 449.9065, 70.1379, 22.1379] |
| nodes.shape_489 | 1 | 12 | diagramMicro | [880.8313, 485.4784, 70.1379, 22.1379] |
| nodes.shape_490 | 1 | 12 | diagramMicro | [973.1652, 486.0437, 70.1379, 22.1379] |
| nodes.shape_491 | 1 | 12 | diagramMicro | [880.8313, 414.7087, 70.1379, 22.1379] |
| nodes.shape_492 | 1 | 12 | diagramMicro | [973.1652, 414.7087, 70.1379, 22.1379] |
| nodes.shape_498 | 1 | 28 | diagramMicro | [251.6522, 537.4604, 156.4115, 22.1379] |
| nodes.shape_503 | 1 | 14 | diagramMicro | [245.9162, 485.4784, 76.9047, 22.1379] |
| nodes.shape_504 | 1 | 14 | diagramMicro | [336.8867, 486.0437, 76.9047, 22.1379] |
| nodes.shape_505 | 1 | 14 | diagramMicro | [245.9162, 414.7087, 76.9047, 22.1379] |
| nodes.shape_506 | 1 | 14 | diagramMicro | [336.8867, 414.7087, 76.9047, 22.1379] |
| nodes.shape_130 | 1 | 19 | diagramMicro | [908.5224, 452.0596, 106.4912, 22.1129] |
| nodes.shape_132 | 1 | 19 | diagramMicro | [277.4312, 450.3887, 104.8535, 22.1129] |
| nodes.shape_523 | 1 | 36 | diagramMicro | [523.4167, 537.4604, 196.8466, 22.1379] |
| nodes.shape_486 | 1 | 174 | diagramMicro | [464.2189, 592.1192, 314.5272, 50.5189] |
| nodes.shape_535 | 1 | 177 | diagramMicro | [801.5407, 592.1192, 319.2906, 50.5189] |
| nodes.shape_541 | 1 | 123 | diagramMicro | [217.5767, 592.1192, 225.5102, 50.5189] |
### page-10

业务前台7模块；中台3列开发/标准/治理；统一查询横向总服务；基础设施行；数据源4类

Layout为`source-house-10`，原型为`templates/prototypes/source-house-10.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_259 | 1 | 11 | compactBody | [126.8615, 326.7986, 105.7744, 35.6155] |
| nodes.shape_326 | 1 | 11 | compactBody | [126.8615, 517.6835, 105.7744, 35.6155] |
| nodes.shape_343 | 1 | 99 | compactBody | [273.9636, 515.6091, 896.3313, 39.7643] |
| nodes.shape_348 | 1 | 9 | compactBody | [137.6544, 596.4606, 84.1886, 35.6155] |
| nodes.shape_365 | 1 | 23 | compactBody | [273.9636, 594.3862, 209.1637, 39.7643] |
| nodes.shape_376 | 1 | 99 | compactBody | [273.9636, 215.7832, 896.3313, 45.3161] |
| nodes.shape_260 | 1 | 10 | compactBody | [372.3122, 283.4367, 94.9815, 32.3787] |
| nodes.shape_261 | 1 | 18 | compactBody | [643.5976, 283.4367, 170.5417, 32.3787] |
| nodes.shape_262 | 1 | 14 | compactBody | [966.4926, 283.4367, 132.7616, 32.3787] |
| nodes.shape_278 | 1 | 25 | compactBody | [301.6323, 420.3972, 229.607, 36.1066] |
| nodes.shape_50 | 1 | 25 | compactBody | [607.3207, 420.3972, 229.607, 36.1066] |
| nodes.shape_65 | 1 | 25 | compactBody | [913.0191, 420.3972, 229.607, 36.1066] |
| nodes.shape_44 | 1 | 25 | compactBody | [301.6323, 372.9265, 229.607, 36.1066] |
| nodes.shape_51 | 1 | 12 | compactBody | [607.3207, 372.9265, 110.2138, 36.1066] |
| nodes.shape_53 | 1 | 12 | compactBody | [726.7139, 372.9265, 110.2138, 36.1066] |
| nodes.shape_66 | 1 | 25 | compactBody | [913.0191, 372.9265, 229.607, 36.1066] |
| nodes.shape_45 | 1 | 25 | compactBody | [301.6323, 325.4658, 229.607, 36.1066] |
| nodes.shape_52 | 1 | 25 | compactBody | [607.3207, 325.4658, 229.607, 36.1066] |
| nodes.shape_74 | 1 | 12 | compactBody | [913.0191, 325.4658, 110.2138, 36.1066] |
| nodes.shape_75 | 1 | 12 | compactBody | [1032.4024, 325.4658, 110.2138, 36.1066] |
| nodes.shape_79 | 1 | 23 | compactBody | [503.0194, 594.3862, 209.1637, 39.7643] |
| nodes.shape_82 | 1 | 23 | compactBody | [732.0753, 594.3862, 209.1637, 39.7643] |
| nodes.shape_85 | 1 | 23 | compactBody | [961.1312, 594.3862, 209.1637, 39.7643] |
| nodes.shape_103 | 1 | 10 | compactBody | [132.263, 137.5372, 94.9815, 32.3787] |
| nodes.shape_104 | 1 | 10 | compactBody | [285.6784, 137.5372, 94.9815, 32.3787] |
| nodes.shape_105 | 1 | 10 | compactBody | [439.0938, 137.5372, 94.9815, 32.3787] |
| nodes.shape_106 | 1 | 10 | compactBody | [592.5093, 137.5372, 94.9815, 32.3787] |
| nodes.shape_107 | 1 | 12 | compactBody | [736.4746, 137.5372, 113.8715, 32.3787] |
| nodes.shape_108 | 1 | 12 | compactBody | [889.8901, 137.5372, 113.8715, 32.3787] |
| nodes.shape_109 | 1 | 14 | compactBody | [1033.8655, 137.5372, 132.7616, 32.3787] |
### page-11

顶部流量=留存+智能整合；4根功能柱分别触达、投放、沉淀、智能；底部11类数据支持

Layout为`source-house-11`，原型为`templates/prototypes/source-house-11.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_35 | 1 | 6 | body | [314.7353, 131.442, 68.957, 39.4069] |
| nodes.shape_36 | 1 | 10 | body | [1025.0051, 131.442, 118.2106, 39.4069] |
| nodes.shape_46 | 1 | 6 | body | [754.2984, 131.442, 68.957, 39.4069] |
| nodes.shape_63 | 1 | 14 | body | [140.5035, 581.4513, 151.297, 39.4069] |
| nodes.shape_79 | 1 | 10 | compactBody | [152.1792, 284.3751, 96.3122, 32.8323] |
| nodes.shape_80 | 1 | 31 | caption | [88.557, 310.2975, 223.5464, 27.9141] |
| nodes.shape_81 | 1 | 18 | caption | [135.3718, 329.8282, 129.927, 27.9141] |
| nodes.shape_82 | 1 | 10 | compactBody | [152.1792, 382.7603, 96.3122, 32.8323] |
| nodes.shape_83 | 1 | 22 | caption | [118.4831, 408.6827, 163.6942, 27.9141] |
| nodes.shape_84 | 1 | 10 | compactBody | [152.1792, 457.5806, 96.3122, 32.8323] |
| nodes.shape_85 | 1 | 20 | caption | [126.0129, 483.503, 148.6448, 27.9141] |
| nodes.shape_91 | 1 | 10 | compactBody | [738.3954, 305.237, 96.3122, 32.8323] |
| nodes.shape_92 | 1 | 20 | caption | [714.4545, 329.9196, 144.2042, 27.9141] |
| nodes.shape_95 | 1 | 10 | compactBody | [738.3954, 433.7413, 96.3122, 32.8323] |
| nodes.shape_96 | 1 | 20 | caption | [714.4545, 458.424, 144.2042, 27.9141] |
| nodes.shape_99 | 1 | 11 | compactBody | [1029.6286, 285.5233, 100.0822, 32.8323] |
| nodes.shape_100 | 1 | 22 | caption | [997.8125, 309.6878, 163.6942, 27.9141] |
| nodes.shape_103 | 1 | 10 | compactBody | [1031.5086, 369.8346, 96.3122, 32.8323] |
| nodes.shape_104 | 1 | 25 | caption | [987.5594, 393.9889, 184.2208, 27.9141] |
| nodes.shape_106 | 1 | 12 | compactBody | [1021.9261, 454.2476, 115.467, 32.8323] |
| nodes.shape_107 | 1 | 20 | caption | [1007.5677, 478.412, 144.2042, 27.9141] |
| nodes.shape_112 | 1 | 14 | body | [710.9691, 210.703, 151.297, 39.4069] |
| nodes.shape_114 | 1 | 14 | body | [1004.0111, 210.703, 151.297, 39.4069] |
| nodes.shape_116 | 1 | 14 | body | [417.9372, 210.703, 151.297, 39.4069] |
| nodes.shape_16 | 1 | 10 | compactBody | [445.4245, 421.5575, 96.3122, 32.8323] |
| nodes.shape_17 | 1 | 25 | caption | [400.9672, 448.2725, 185.2471, 27.9141] |
| nodes.shape_20 | 1 | 24 | caption | [407.1455, 469.1446, 172.8804, 27.9141] |
| nodes.shape_23 | 1 | 10 | compactBody | [445.4245, 305.237, 96.3122, 32.8323] |
| nodes.shape_25 | 1 | 20 | caption | [419.2582, 329.9196, 148.6448, 27.9141] |
| nodes.shape_110 | 1 | 14 | body | [124.8951, 210.703, 151.297, 39.4069] |
| nodes.shape_167 | 1 | 16 | caption | [357.7497, 576.533, 64.0794, 49.2536] |
| nodes.shape_168 | 1 | 14 | caption | [447.5991, 576.533, 52.7085, 49.2536] |
| nodes.shape_169 | 1 | 14 | caption | [531.7681, 576.533, 52.7085, 49.2536] |
| nodes.shape_170 | 1 | 14 | caption | [615.927, 576.533, 52.7085, 49.2536] |
| nodes.shape_171 | 1 | 14 | caption | [700.0961, 576.533, 52.7085, 49.2536] |
| nodes.shape_172 | 1 | 14 | caption | [784.255, 576.533, 52.7085, 49.2536] |
| nodes.shape_173 | 1 | 14 | caption | [868.424, 576.533, 52.7085, 49.2536] |
| nodes.shape_174 | 1 | 14 | caption | [952.5829, 576.533, 52.7085, 49.2536] |
| nodes.shape_175 | 1 | 14 | caption | [1036.752, 576.533, 52.7085, 49.2536] |
| nodes.shape_176 | 1 | 14 | caption | [1120.9109, 576.533, 52.7085, 49.2536] |
### page-12

屋顶业务目标；治理门户横梁；左生命周期、右安全边柱；中部主数据/标准/质量/资产/集成/交换6域；底部元数据与实时数据两行

Layout为`source-house-12`，原型为`templates/prototypes/source-house-12.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_442 | 1 | 90 | compactBody | [420.3293, 142.6598, 412.9902, 57.0818] |
| nodes.shape_457 | 1 | 14 | caption | [128.0673, 244.8566, 103.4707, 25.8398] |
| nodes.shape_447 | 1 | 14 | caption | [123.1765, 313.4497, 106.8739, 25.8398] |
| nodes.shape_483 | 1 | 13 | caption | [280.3259, 322.4132, 100.2535, 25.8398] |
| nodes.shape_614 | 1 | 14 | caption | [1051.1863, 312.1758, 106.8739, 25.8398] |
| nodes.shape_615 | 1 | 14 | caption | [277.025, 541.684, 106.8739, 25.8398] |
| nodes.shape_616 | 1 | 17 | caption | [284.5752, 603.5266, 129.0966, 25.8398] |
| nodes.shape_617 | 1 | 14 | caption | [278.5964, 375.5805, 103.7125, 25.8398] |
| nodes.shape_618 | 1 | 16 | caption | [427.3867, 375.5805, 116.5161, 25.8398] |
| nodes.shape_619 | 1 | 13 | caption | [591.7422, 375.5805, 96.5063, 25.8398] |
| nodes.shape_620 | 1 | 14 | caption | [900.6387, 375.5805, 102.5223, 25.8398] |
| nodes.shape_621 | 1 | 14 | caption | [743.824, 375.5805, 104.2425, 25.8398] |
| nodes.shape_5 | 1 | 11 | caption | [134.1763, 371.9355, 84.8742, 27.0393] |
| nodes.shape_6 | 1 | 11 | caption | [134.1763, 578.8398, 84.8742, 27.0393] |
| nodes.shape_10 | 1 | 11 | caption | [134.1763, 423.6616, 84.8742, 27.0393] |
| nodes.shape_11 | 1 | 11 | caption | [134.1763, 475.3877, 84.8742, 27.0393] |
| nodes.shape_12 | 1 | 11 | caption | [134.1763, 527.1137, 84.8742, 27.0393] |
| nodes.shape_14 | 1 | 18 | caption | [254.1978, 235.2423, 71.9032, 45.0685] |
| nodes.shape_15 | 1 | 18 | caption | [347.5335, 235.2423, 71.9032, 45.0685] |
| nodes.shape_16 | 1 | 22 | caption | [441.176, 235.2423, 83.3772, 45.0685] |
| nodes.shape_17 | 1 | 22 | caption | [546.5993, 235.2423, 83.3772, 45.0685] |
| nodes.shape_18 | 1 | 22 | caption | [745.3676, 235.2423, 83.3772, 45.0685] |
| nodes.shape_19 | 1 | 22 | caption | [850.7909, 235.2423, 83.3772, 45.0685] |
| nodes.shape_20 | 1 | 22 | caption | [956.2142, 235.2423, 83.3772, 45.0685] |
| nodes.shape_21 | 1 | 18 | caption | [651.7158, 235.2423, 71.9032, 45.0685] |
| nodes.shape_22 | 1 | 18 | caption | [1061.3307, 235.2423, 71.9032, 45.0685] |
| nodes.shape_23 | 1 | 14 | caption | [529.0907, 321.8088, 101.1554, 27.0393] |
| nodes.shape_24 | 1 | 12 | caption | [406.0193, 321.8088, 91.7456, 27.0393] |
| nodes.shape_25 | 1 | 12 | caption | [775.2242, 321.8088, 91.7456, 27.0393] |
| nodes.shape_26 | 1 | 14 | caption | [652.1528, 321.8088, 101.1554, 27.0393] |
| nodes.shape_27 | 1 | 14 | caption | [898.2862, 321.8088, 101.1554, 27.0393] |
| nodes.shape_28 | 1 | 13 | caption | [280.986, 417.2551, 94.2469, 27.0393] |
| nodes.shape_29 | 1 | 13 | caption | [280.986, 448.9063, 94.2469, 27.0393] |
| nodes.shape_30 | 1 | 13 | caption | [280.986, 480.5575, 94.2469, 27.0393] |
| nodes.shape_31 | 1 | 13 | caption | [436.9267, 417.2551, 94.2469, 27.0393] |
| nodes.shape_32 | 1 | 13 | caption | [436.9267, 448.9063, 94.2469, 27.0393] |
| nodes.shape_33 | 1 | 13 | caption | [436.9267, 480.5575, 94.2469, 27.0393] |
| nodes.shape_35 | 1 | 13 | caption | [592.8766, 417.2551, 94.2469, 27.0393] |
| nodes.shape_36 | 1 | 13 | caption | [592.8766, 448.9063, 94.2469, 27.0393] |
| nodes.shape_37 | 1 | 13 | caption | [592.8766, 480.5575, 94.2469, 27.0393] |
| nodes.shape_38 | 1 | 13 | caption | [748.8265, 417.2551, 94.2469, 27.0393] |
| nodes.shape_39 | 1 | 13 | caption | [748.8265, 448.9063, 94.2469, 27.0393] |
| nodes.shape_40 | 1 | 13 | caption | [748.8265, 480.5575, 94.2469, 27.0393] |
| nodes.shape_43 | 1 | 13 | caption | [904.7764, 417.2551, 94.2469, 27.0393] |
| nodes.shape_44 | 1 | 13 | caption | [904.7764, 448.9063, 94.2469, 27.0393] |
| nodes.shape_46 | 1 | 13 | caption | [904.7764, 480.5575, 94.2469, 27.0393] |
| nodes.shape_49 | 1 | 13 | caption | [402.8486, 541.7119, 94.0702, 27.0393] |
| nodes.shape_51 | 1 | 13 | caption | [524.7577, 541.7119, 94.0702, 27.0393] |
| nodes.shape_52 | 1 | 13 | caption | [768.5945, 541.7119, 94.0702, 27.0393] |
| nodes.shape_54 | 1 | 13 | caption | [890.5036, 541.7119, 94.0702, 27.0393] |
| nodes.shape_55 | 1 | 13 | caption | [646.6761, 541.7119, 94.0702, 27.0393] |
| nodes.shape_58 | 1 | 30 | caption | [442.4684, 602.9315, 112.8061, 45.0685] |
| nodes.shape_59 | 1 | 15 | caption | [585.5496, 602.9315, 112.8061, 27.0393] |
| nodes.shape_61 | 1 | 15 | caption | [728.6214, 602.9315, 112.8061, 27.0393] |
| nodes.shape_62 | 1 | 15 | caption | [871.6933, 602.9315, 112.8061, 27.0393] |
| nodes.shape_449 | 1 | 11 | caption | [1058.9876, 371.9355, 84.8742, 27.0393] |
| nodes.shape_451 | 1 | 11 | caption | [1058.9876, 578.8398, 84.8742, 27.0393] |
| nodes.shape_452 | 1 | 11 | caption | [1058.9876, 423.6616, 84.8742, 27.0393] |
| nodes.shape_455 | 1 | 11 | caption | [1058.9876, 475.3877, 84.8742, 27.0393] |
| nodes.shape_458 | 1 | 11 | caption | [1058.9876, 527.1137, 84.8742, 27.0393] |
### page-13

左9触达渠道竖栏；中间支付前/买单场景/支付后/游戏/其他5阶段或功能簇；底部交易行为/分析/画像

Layout为`source-house-13`，原型为`templates/prototypes/source-house-13.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_114 | 1 | 39 | body | [428.4945, 128.1144, 423.0109, 36.9254] |
| nodes.shape_119 | 1 | 20 | body | [63.7185, 210.5368, 109.6645, 63.7831] |
| nodes.shape_95 | 1 | 15 | caption | [63.3445, 284.0448, 110.4333, 28.0733] |
| nodes.shape_97 | 1 | 15 | caption | [63.3445, 323.2767, 110.4333, 28.0733] |
| nodes.shape_99 | 1 | 15 | caption | [63.3445, 362.5191, 110.4333, 28.0733] |
| nodes.shape_101 | 1 | 15 | caption | [63.3445, 401.751, 110.4333, 28.0733] |
| nodes.shape_103 | 1 | 15 | caption | [63.3445, 440.983, 110.4333, 28.0733] |
| nodes.shape_105 | 1 | 15 | caption | [63.3445, 480.2149, 110.4333, 28.0733] |
| nodes.shape_107 | 1 | 15 | caption | [63.3445, 519.4572, 110.4333, 28.0733] |
| nodes.shape_109 | 1 | 15 | caption | [63.3445, 558.6892, 110.4333, 28.0733] |
| nodes.shape_111 | 1 | 15 | caption | [63.3445, 597.9211, 110.4333, 28.0733] |
| nodes.shape_192 | 1 | 10 | body | [317.9261, 604.955, 109.6645, 36.9254] |
| nodes.shape_196 | 1 | 10 | body | [664.6446, 604.955, 109.6645, 36.9254] |
| nodes.shape_200 | 1 | 10 | body | [1011.3736, 604.955, 109.6645, 36.9254] |
| nodes.shape_87 | 1 | 29 | compactBody | [586.7626, 267.7016, 265.4702, 33.5695] |
| nodes.shape_88 | 1 | 41 | body | [494.7296, 210.3394, 449.5361, 36.9254] |
| nodes.shape_93 | 1 | 10 | compactBody | [276.3357, 317.0844, 92.7811, 33.5695] |
| nodes.shape_91 | 1 | 21 | compactBody | [438.3752, 317.0844, 194.1025, 33.5695] |
| nodes.shape_86 | 1 | 10 | compactBody | [682.0995, 317.0844, 92.7811, 33.5695] |
| nodes.shape_84 | 1 | 12 | compactBody | [828.7414, 317.0844, 115.2438, 33.5695] |
| nodes.shape_82 | 1 | 17 | compactBody | [999.8409, 317.0844, 156.481, 33.5695] |
| nodes.shape_2 | 1 | 12 | caption | [1088.1647, 422.728, 90.3394, 31.6162] |
| nodes.shape_7 | 1 | 13 | caption | [269.3329, 377.0336, 99.389, 30.2136] |
| nodes.shape_8 | 1 | 13 | caption | [265.2186, 422.6761, 97.0409, 30.2136] |
| nodes.shape_13 | 1 | 12 | caption | [267.7017, 468.3289, 92.0745, 30.2136] |
| nodes.shape_14 | 1 | 8 | caption | [416.4735, 377.3453, 62.048, 30.2136] |
| nodes.shape_19 | 1 | 13 | caption | [472.0175, 377.3453, 99.8669, 30.2136] |
| nodes.shape_20 | 1 | 8 | caption | [558.8659, 377.3453, 62.048, 30.2136] |
| nodes.shape_28 | 1 | 13 | caption | [419.7359, 422.9982, 95.659, 30.2136] |
| nodes.shape_29 | 1 | 13 | caption | [517.8365, 422.9047, 95.659, 30.2136] |
| nodes.shape_34 | 1 | 13 | caption | [419.7359, 468.6406, 95.659, 30.2136] |
| nodes.shape_35 | 1 | 13 | caption | [517.8365, 468.5575, 95.659, 30.2136] |
| nodes.shape_36 | 1 | 10 | caption | [679.554, 377.0336, 78.7132, 30.2136] |
| nodes.shape_37 | 1 | 10 | caption | [679.554, 422.6761, 78.7132, 30.2136] |
| nodes.shape_38 | 1 | 10 | caption | [679.554, 468.3289, 78.7132, 30.2136] |
| nodes.shape_39 | 1 | 13 | caption | [827.5258, 377.0336, 96.9162, 30.2136] |
| nodes.shape_40 | 1 | 15 | caption | [819.8061, 422.7696, 115.1192, 30.2136] |
| nodes.shape_41 | 1 | 13 | caption | [827.5258, 468.5056, 96.9162, 30.2136] |
| nodes.shape_42 | 1 | 12 | caption | [983.8509, 377.0336, 87.2848, 30.2136] |
| nodes.shape_43 | 1 | 12 | caption | [1085.0166, 377.0336, 87.2848, 30.2136] |
| nodes.shape_44 | 1 | 12 | caption | [983.8509, 422.728, 87.2848, 30.2136] |
| nodes.shape_45 | 1 | 8 | caption | [997.5759, 468.4225, 59.8349, 30.2136] |
| nodes.shape_47 | 1 | 12 | caption | [1085.0166, 468.4225, 87.2848, 30.2136] |
### page-14

顶部导入→触达→转化→持续运营；4纵向分组；公域/商域输入、私域/品牌触点、内容/CRM转化；底部虚线反推反馈

Layout为`source-house-14`，原型为`templates/prototypes/source-house-14.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_341 | 1 | 9 | heading | [106.0973, 143.7782, 123.1779, 40.42] |
| nodes.shape_354 | 1 | 9 | heading | [421.4943, 143.7782, 123.1779, 40.42] |
| nodes.shape_361 | 1 | 9 | heading | [736.8913, 143.7782, 123.1779, 40.42] |
| nodes.shape_359 | 1 | 9 | heading | [1052.2883, 143.7782, 123.1779, 40.42] |
| nodes.shape_401 | 1 | 11 | caption | [627.8365, 375.8337, 84.9883, 26.9432] |
| nodes.shape_331 | 1 | 21 | compactBody | [1019.1435, 369.5903, 189.4571, 39.5549] |
| nodes.shape_334 | 1 | 21 | compactBody | [1019.1435, 427.5312, 189.4571, 39.5549] |
| nodes.shape_337 | 1 | 21 | compactBody | [1019.1435, 485.4722, 189.4571, 39.5549] |
| nodes.shape_328 | 1 | 21 | compactBody | [1019.1435, 311.6598, 189.4571, 39.5549] |
| nodes.shape_324 | 1 | 21 | compactBody | [1019.1435, 253.7189, 189.4571, 39.5549] |
| nodes.shape_32 | 1 | 15 | heading | [71.2952, 237.2299, 189.6551, 40.42] |
| nodes.shape_159 | 1 | 9 | heading | [422.4636, 237.2299, 121.2496, 40.42] |
| nodes.shape_201 | 1 | 30 | compactBody | [729.4389, 237.2299, 138.0826, 57.253] |
| nodes.shape_222 | 1 | 13 | caption | [803.2227, 298.7771, 93.754, 36.7095] |
| nodes.shape_225 | 1 | 13 | caption | [699.9838, 298.7771, 93.754, 36.7095] |
| nodes.shape_377 | 1 | 10 | compactBody | [958.8887, 330.0458, 23.5245, 131.3494] |
| nodes.shape_467 | 1 | 4 | caption | [304.7369, 384.2554, 31.1853, 25.3485] |
| nodes.shape_468 | 1 | 4 | caption | [623.9592, 264.5692, 31.1853, 25.3485] |
| nodes.shape_466 | 1 | 4 | caption | [641.5634, 443.4262, 31.1853, 25.3485] |
| nodes.shape_469 | 1 | 11 | caption | [615.8918, 491.6008, 84.9883, 30.956] |
| nodes.shape_70 | 1 | 15 | heading | [71.2952, 374.7705, 189.6551, 40.42] |
| nodes.shape_138 | 1 | 10 | compactBody | [433.6891, 445.4378, 98.7883, 33.6764] |
| nodes.shape_213 | 1 | 8 | caption | [384.6181, 500.3248, 60.2756, 36.7095] |
| nodes.shape_218 | 1 | 8 | caption | [453.3571, 500.3248, 60.2756, 36.7095] |
| nodes.shape_216 | 1 | 8 | caption | [522.0961, 500.3248, 60.2756, 36.7095] |
| nodes.shape_190 | 1 | 13 | caption | [436.8055, 389.5085, 93.754, 36.7095] |
| nodes.shape_99 | 1 | 32 | diagramCompact | [272.8324, 424.0187, 103.5411, 40.42] |
| nodes.shape_100 | 1 | 16 | diagramCompact | [272.8324, 450.4408, 103.5411, 25.2547] |
| nodes.shape_109 | 1 | 16 | diagramCompact | [272.8324, 306.3025, 103.5411, 25.2547] |
| nodes.shape_110 | 1 | 16 | diagramCompact | [272.8324, 332.7245, 103.5411, 25.2547] |
| nodes.shape_111 | 1 | 3 | caption | [154.2198, 602.9279, 23.8163, 25.3485] |
| nodes.shape_112 | 1 | 3 | caption | [471.2636, 602.9279, 23.6391, 25.3485] |
| nodes.shape_113 | 1 | 2 | compactBody | [814.198, 601.1143, 26.4429, 30.3932] |
| nodes.shape_173 | 1 | 8 | caption | [384.6181, 282.163, 60.2756, 36.7095] |
| nodes.shape_175 | 1 | 9 | caption | [450.4908, 282.163, 66.0187, 36.7095] |
| nodes.shape_177 | 1 | 8 | caption | [522.0961, 282.163, 60.2756, 36.7095] |
| nodes.shape_158 | 1 | 13 | caption | [384.6181, 327.4505, 93.754, 36.7095] |
| nodes.shape_122 | 1 | 13 | caption | [488.6178, 327.4505, 93.754, 36.7095] |
| nodes.shape_126 | 1 | 24 | caption | [818.8466, 445.2606, 44.9123, 80.8296] |
| nodes.shape_4 | 1 | 9 | caption | [64.9476, 309.0645, 65.7164, 30.3098] |
| nodes.shape_7 | 1 | 9 | caption | [133.6763, 309.0645, 65.7164, 30.3098] |
| nodes.shape_10 | 1 | 9 | caption | [202.4153, 309.0645, 65.7164, 30.3098] |
| nodes.shape_12 | 1 | 9 | caption | [64.9476, 440.1221, 65.7164, 30.3098] |
| nodes.shape_13 | 1 | 10 | caption | [133.6763, 440.1221, 75.4618, 30.3098] |
| nodes.shape_15 | 1 | 9 | caption | [202.4153, 440.1221, 65.7164, 30.3098] |
| nodes.shape_16 | 1 | 9 | caption | [64.9476, 505.0672, 65.7164, 30.3098] |
| nodes.shape_20 | 1 | 9 | caption | [202.4153, 505.0672, 65.7164, 30.3098] |
| nodes.shape_22 | 1 | 13 | caption | [719.2245, 485.8265, 97.9857, 28.6317] |
| nodes.shape_23 | 1 | 13 | caption | [719.2245, 423.9979, 97.9857, 28.6317] |
| nodes.shape_24 | 1 | 13 | caption | [719.2245, 454.9122, 97.9857, 28.6317] |
| nodes.shape_25 | 1 | 13 | caption | [719.2245, 517.7727, 97.9857, 28.6317] |
| nodes.shape_26 | 1 | 30 | caption | [863.6547, 462.0936, 75.8579, 63.1524] |
### page-15

3阶段短视频时间轴1–3/4–24/25–30秒；目标/用户视角/结构/内容/表现/效果多条泳道

Layout为`source-house-15`，原型为`templates/prototypes/source-house-15.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_140 | 1 | 18 | caption | [348.2364, 308.0608, 135.1584, 35.4888] |
| nodes.shape_152 | 1 | 90 | caption | [558.0855, 525.6138, 328.01, 40.5784] |
| nodes.shape_159 | 1 | 30 | compactBody | [278.5285, 193.6238, 274.5741, 37.7402] |
| nodes.shape_160 | 1 | 30 | compactBody | [575.1577, 193.6238, 274.5741, 37.7402] |
| nodes.shape_161 | 1 | 30 | compactBody | [872.5018, 193.6238, 274.5741, 37.7402] |
| nodes.shape_162 | 1 | 8 | compactBody | [142.986, 140.3213, 80.4527, 25.0] |
| nodes.shape_163 | 1 | 8 | compactBody | [142.986, 199.9352, 80.4527, 25.0] |
| nodes.shape_164 | 1 | 8 | compactBody | [142.986, 248.9004, 80.4527, 25.0] |
| nodes.shape_165 | 1 | 11 | compactBody | [132.9241, 315.1831, 100.5552, 25.0] |
| nodes.shape_166 | 1 | 8 | caption | [153.0373, 340.1437, 60.3395, 20.0] |
| nodes.shape_167 | 1 | 11 | compactBody | [132.9241, 418.0857, 100.5552, 25.0] |
| nodes.shape_168 | 1 | 8 | caption | [153.0373, 443.0463, 60.3395, 20.0] |
| nodes.shape_169 | 1 | 11 | compactBody | [132.9241, 525.2457, 100.5552, 25.0] |
| nodes.shape_170 | 1 | 8 | caption | [153.0373, 550.2063, 60.3395, 20.0] |
| nodes.shape_171 | 1 | 8 | compactBody | [142.986, 611.5456, 80.4527, 25.0] |
| nodes.shape_172 | 1 | 29 | compactBody | [364.583, 139.4357, 261.4605, 25.0] |
| nodes.shape_173 | 1 | 26 | compactBody | [807.8409, 139.4357, 241.3473, 25.0] |
| nodes.shape_184 | 1 | 8 | caption | [384.216, 406.2504, 63.2098, 20.0] |
| nodes.shape_185 | 1 | 4 | caption | [399.2075, 425.446, 33.2161, 20.0] |
| nodes.shape_186 | 1 | 8 | caption | [681.1973, 406.2504, 63.2098, 20.0] |
| nodes.shape_187 | 1 | 5 | caption | [691.7927, 425.446, 42.0189, 20.0] |
| nodes.shape_188 | 1 | 8 | caption | [977.1116, 406.2504, 63.2098, 20.0] |
| nodes.shape_189 | 1 | 7 | caption | [983.1296, 425.446, 51.1739, 20.0] |
| nodes.shape_196 | 1 | 18 | caption | [644.8656, 308.0608, 135.1584, 35.4888] |
| nodes.shape_199 | 1 | 18 | caption | [942.2097, 308.0608, 135.1584, 35.4888] |
| nodes.shape_8 | 1 | 76 | caption | [278.5285, 598.3199, 276.7081, 49.6801] |
| nodes.shape_9 | 1 | 76 | caption | [574.4428, 598.3199, 276.7081, 49.6801] |
| nodes.shape_10 | 1 | 76 | caption | [870.3678, 598.3199, 276.7081, 49.6801] |
| nodes.shape_156 | 1 | 30 | compactBody | [278.5285, 241.842, 274.5741, 37.7402] |
| nodes.shape_157 | 1 | 30 | compactBody | [575.1577, 241.842, 274.5741, 37.7402] |
| nodes.shape_158 | 1 | 30 | compactBody | [872.5018, 241.842, 274.5741, 37.7402] |
### page-16

屋顶总目标；多渠道入口行；4纵向能力簇；底部开放生态；4上行连接箭头

Layout为`source-house-16`，原型为`templates/prototypes/source-house-16.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_103 | 1 | 28 | heading | [451.8384, 144.5391, 358.8547, 35.0] |
| nodes.shape_104 | 1 | 8 | compactBody | [117.9462, 219.1931, 77.2965, 25.0] |
| nodes.shape_105 | 1 | 8 | compactBody | [320.4548, 221.2536, 77.2965, 25.0] |
| nodes.shape_106 | 1 | 10 | compactBody | [522.1228, 221.2536, 96.6104, 25.0] |
| nodes.shape_107 | 1 | 8 | compactBody | [745.6984, 221.2536, 77.2965, 25.0] |
| nodes.shape_108 | 1 | 12 | compactBody | [953.0765, 221.2536, 115.9345, 25.0] |
| nodes.shape_109 | 1 | 18 | caption | [316.2107, 320.8407, 132.501, 20.0] |
| nodes.shape_110 | 1 | 18 | caption | [553.1337, 320.8407, 132.501, 20.0] |
| nodes.shape_111 | 1 | 16 | caption | [799.0473, 320.8407, 115.9345, 20.0] |
| nodes.shape_112 | 1 | 16 | caption | [1038.441, 320.8407, 115.9345, 20.0] |
| nodes.shape_113 | 1 | 10 | compactBody | [98.622, 412.6086, 96.6104, 25.0] |
| nodes.shape_114 | 1 | 8 | caption | [134.5126, 607.0531, 60.73, 20.0] |
| nodes.shape_115 | 1 | 10 | compactBody | [341.9215, 381.0032, 96.6104, 25.0] |
| nodes.shape_116 | 1 | 8 | compactBody | [341.9215, 435.5208, 77.2965, 25.0] |
| nodes.shape_117 | 1 | 8 | compactBody | [341.9215, 491.1968, 77.2965, 25.0] |
| nodes.shape_118 | 1 | 8 | compactBody | [580.126, 381.0032, 77.2965, 25.0] |
| nodes.shape_119 | 1 | 10 | compactBody | [580.126, 435.5208, 96.6104, 25.0] |
| nodes.shape_120 | 1 | 13 | compactBody | [580.126, 491.1968, 123.5309, 25.0] |
| nodes.shape_121 | 1 | 8 | compactBody | [818.9558, 381.0032, 77.2965, 25.0] |
| nodes.shape_122 | 1 | 8 | compactBody | [818.9558, 435.5208, 77.2965, 25.0] |
| nodes.shape_123 | 1 | 8 | compactBody | [818.9558, 491.1968, 77.2965, 25.0] |
| nodes.shape_124 | 1 | 8 | compactBody | [1056.1659, 381.0032, 77.2965, 25.0] |
| nodes.shape_125 | 1 | 8 | compactBody | [1056.1659, 435.5208, 77.2965, 25.0] |
| nodes.shape_126 | 1 | 10 | compactBody | [1056.1659, 491.1968, 96.6104, 25.0] |
| nodes.shape_127 | 1 | 15 | compactBody | [571.6992, 604.2199, 135.2586, 25.0] |
### page-17

屋顶总计划；3列目标；4行具体行动/量化指标/公司关联/时间计划；底部时间箭头

Layout为`source-house-17`，原型为`templates/prototypes/source-house-17.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_30 | 1 | 38 | body | [424.6248, 155.1607, 419.1156, 35.913] |
| nodes.shape_6 | 1 | 24 | diagramCompact | [125.4727, 254.7527, 77.1432, 41.4354] |
| nodes.shape_7 | 1 | 18 | diagramCompact | [125.4727, 350.4636, 58.0113, 41.4354] |
| nodes.shape_15 | 1 | 17 | diagramMicro | [126.3275, 288.0754, 96.2922, 20.7134] |
| nodes.shape_16 | 1 | 17 | diagramMicro | [125.4727, 384.2821, 96.2922, 20.7134] |
| nodes.shape_24 | 1 | 28 | diagramCompact | [125.4727, 467.0247, 90.9578, 41.4354] |
| nodes.shape_25 | 1 | 17 | diagramMicro | [125.4727, 500.8347, 96.2922, 20.7134] |
| nodes.shape_27 | 1 | 11 | diagramCompact | [125.4727, 546.553, 71.8174, 24.8595] |
| nodes.shape_28 | 1 | 17 | diagramMicro | [125.4727, 564.129, 96.2922, 20.7134] |
| nodes.shape_11 | 1 | 176 | diagramCompact | [241.2046, 264.8828, 281.6701, 68.9108] |
| nodes.shape_13 | 1 | 39 | caption | [238.0672, 481.5489, 287.9534, 27.6208] |
| nodes.shape_14 | 1 | 102 | diagramCompact | [275.5531, 556.3583, 216.5634, 55.4381] |
| nodes.shape_34 | 1 | 17 | diagramCompact | [247.4622, 428.4787, 113.0903, 24.8595] |
| nodes.shape_35 | 1 | 2 | body | [289.3235, 371.7583, 26.88, 46.5646] |
| nodes.shape_38 | 1 | 17 | diagramCompact | [381.7703, 428.4787, 113.0903, 24.8595] |
| nodes.shape_39 | 1 | 8 | heading | [383.4801, 371.7583, 107.1832, 46.5646] |
| nodes.shape_40 | 1 | 24 | caption | [243.0511, 220.4212, 179.0861, 27.6208] |
| nodes.shape_545 | 1 | 176 | diagramCompact | [556.2572, 264.8828, 281.6701, 68.9108] |
| nodes.shape_546 | 1 | 39 | caption | [553.1199, 481.5489, 287.9534, 27.6208] |
| nodes.shape_547 | 1 | 136 | diagramCompact | [590.6058, 556.3583, 216.5634, 80.5456] |
| nodes.shape_548 | 1 | 17 | diagramCompact | [572.7733, 428.4787, 113.0903, 24.8595] |
| nodes.shape_549 | 1 | 8 | heading | [574.6454, 371.7583, 106.8584, 46.5646] |
| nodes.shape_551 | 1 | 17 | diagramCompact | [707.0814, 428.4787, 113.0903, 24.8595] |
| nodes.shape_552 | 1 | 8 | heading | [708.7911, 371.7583, 107.1832, 46.5646] |
| nodes.shape_553 | 1 | 24 | caption | [558.1037, 220.4212, 179.0861, 27.6208] |
| nodes.shape_564 | 1 | 176 | diagramCompact | [871.3099, 264.8828, 281.6701, 68.9108] |
| nodes.shape_565 | 1 | 39 | caption | [868.1725, 481.5489, 287.9534, 27.6208] |
| nodes.shape_566 | 1 | 136 | diagramCompact | [914.5491, 538.4916, 216.5634, 80.3062] |
| nodes.shape_568 | 1 | 2 | body | [919.4289, 371.7583, 26.88, 46.5646] |
| nodes.shape_570 | 1 | 17 | diagramCompact | [951.958, 428.4787, 113.0903, 24.8595] |
| nodes.shape_571 | 1 | 9 | heading | [944.6318, 371.7583, 116.2021, 49.6421] |
| nodes.shape_572 | 1 | 24 | caption | [873.1564, 220.4212, 179.0861, 27.6208] |
### page-18

与house08同语义的屋顶-背景-痛点-3优化列-营销-收益图；页题及排版略变

Layout为`source-house-18`，原型为`templates/prototypes/source-house-18.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_5 | 1 | 47 | body | [357.6677, 140.3408, 517.3648, 35.8288] |
| nodes.shape_49 | 1 | 16 | diagramCompact | [138.6691, 609.297, 51.5471, 38.703] |
| nodes.shape_71 | 1 | 24 | diagramCompact | [138.6691, 241.0812, 51.5471, 57.901] |
| nodes.shape_33 | 1 | 142 | diagramCompact | [211.3246, 246.6931, 449.1441, 46.6773] |
| nodes.shape_34 | 1 | 142 | diagramCompact | [685.3468, 246.6931, 449.1441, 46.6773] |
| nodes.shape_25 | 1 | 16 | diagramCompact | [138.6691, 183.2399, 51.5471, 46.6858] |
| nodes.shape_35 | 1 | 144 | diagramCompact | [211.3246, 194.0969, 911.3968, 24.9719] |
| nodes.shape_78 | 1 | 136 | diagramCompact | [138.6691, 310.1377, 51.5471, 288.0124] |
| nodes.shape_132 | 1 | 27 | caption | [208.8428, 500.3265, 68.2206, 76.1949] |
| nodes.shape_84 | 1 | 27 | caption | [329.6425, 318.7431, 200.969, 29.9014] |
| nodes.shape_94 | 1 | 36 | caption | [586.8921, 318.7431, 259.8764, 29.9014] |
| nodes.shape_110 | 1 | 33 | caption | [884.1837, 318.7431, 238.7254, 29.9014] |
| nodes.shape_149 | 1 | 296 | diagramMicro | [335.587, 513.1621, 800.0297, 39.3597] |
| nodes.shape_160 | 1 | 294 | diagramMicro | [335.587, 551.0549, 797.1214, 39.3597] |
| nodes.shape_50 | 1 | 130 | caption | [204.4846, 609.3396, 936.8207, 38.6177] |
| nodes.shape_103 | 1 | 21 | caption | [215.4269, 353.2841, 55.0439, 76.1949] |
| nodes.shape_98 | 1 | 21 | diagramMicro | [721.133, 357.7872, 117.2518, 28.2128] |
| nodes.shape_90 | 1 | 21 | diagramMicro | [308.5768, 357.7872, 117.2518, 28.2128] |
| nodes.shape_88 | 1 | 21 | diagramMicro | [434.4255, 357.7872, 117.2518, 28.2128] |
| nodes.shape_102 | 1 | 21 | diagramMicro | [595.2843, 357.7872, 117.2518, 28.2128] |
| nodes.shape_116 | 1 | 21 | diagramMicro | [881.9918, 357.7872, 117.2518, 28.2128] |
| nodes.shape_114 | 1 | 21 | diagramMicro | [1007.8405, 357.7872, 117.2518, 28.2128] |
| nodes.shape_99 | 1 | 21 | diagramMicro | [721.133, 393.8719, 117.2518, 28.2128] |
| nodes.shape_91 | 1 | 21 | diagramMicro | [308.5768, 393.8719, 117.2518, 28.2128] |
| nodes.shape_89 | 1 | 21 | diagramMicro | [434.4255, 393.8719, 117.2518, 28.2128] |
| nodes.shape_104 | 1 | 21 | diagramMicro | [595.2843, 393.8719, 117.2518, 28.2128] |
| nodes.shape_118 | 1 | 21 | diagramMicro | [881.9918, 393.8719, 117.2518, 28.2128] |
| nodes.shape_115 | 1 | 21 | diagramMicro | [1007.8405, 393.8719, 117.2518, 28.2128] |
| nodes.shape_216 | 1 | 21 | diagramMicro | [721.133, 429.9566, 117.2518, 28.2128] |
| nodes.shape_217 | 1 | 21 | diagramMicro | [308.5768, 429.9566, 117.2518, 28.2128] |
| nodes.shape_218 | 1 | 21 | diagramMicro | [434.4255, 429.9566, 117.2518, 28.2128] |
| nodes.shape_219 | 1 | 21 | diagramMicro | [595.2843, 429.9566, 117.2518, 28.2128] |
| nodes.shape_220 | 1 | 21 | diagramMicro | [881.9918, 429.9566, 117.2518, 28.2128] |
| nodes.shape_221 | 1 | 21 | diagramMicro | [1007.8405, 429.9566, 117.2518, 28.2128] |
| nodes.shape_20 | 1 | 27 | caption | [616.35, 484.9579, 200.969, 29.9014] |
### page-19

左用户圈、右品牌圈；中央线上4活动柱和线下活动带；上下曝光资源与底部3类价值；外部大环线连接双方

Layout为`source-house-19`，原型为`templates/prototypes/source-house-19.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_10 | 1 | 33 | caption | [212.7861, 613.7532, 239.9208, 34.2468] |
| nodes.shape_11 | 1 | 33 | caption | [520.0396, 613.7532, 239.9208, 34.2468] |
| nodes.shape_12 | 1 | 33 | caption | [827.293, 613.7532, 239.9208, 34.2468] |
| nodes.shape_14 | 1 | 54 | caption | [212.7861, 143.2085, 395.6856, 34.2468] |
| nodes.shape_15 | 1 | 54 | caption | [671.5283, 143.2085, 395.6856, 34.2468] |
| nodes.shape_18 | 1 | 54 | caption | [212.7861, 556.2883, 395.6856, 34.2468] |
| nodes.shape_19 | 1 | 54 | caption | [671.5283, 556.2883, 395.6856, 34.2468] |
| nodes.shape_36 | 1 | 44 | diagramCompact | [263.8467, 266.0325, 139.0767, 49.1354] |
| nodes.shape_37 | 1 | 26 | caption | [236.7685, 216.1135, 193.233, 36.288] |
| nodes.shape_42 | 1 | 46 | diagramCompact | [463.9387, 266.0325, 147.7061, 49.1354] |
| nodes.shape_43 | 1 | 26 | caption | [441.1753, 216.1135, 193.233, 36.288] |
| nodes.shape_46 | 1 | 100 | diagramCompact | [661.1866, 256.3776, 162.0336, 69.7705] |
| nodes.shape_47 | 1 | 26 | caption | [645.5917, 216.1135, 193.233, 36.288] |
| nodes.shape_50 | 1 | 42 | diagramCompact | [879.9305, 266.0325, 133.3786, 49.1354] |
| nodes.shape_51 | 1 | 26 | caption | [849.9985, 216.1135, 193.233, 36.288] |
| nodes.shape_57 | 1 | 29 | caption | [834.065, 491.4807, 209.1665, 34.2468] |
| nodes.shape_59 | 1 | 29 | diagramCompact | [647.5459, 493.9863, 186.6062, 28.5003] |
| nodes.shape_143 | 1 | 6 | compactBody | [231.1381, 342.0719, 55.2302, 29.2549] |
| nodes.shape_144 | 1 | 6 | compactBody | [231.1381, 395.3092, 55.2302, 29.2549] |
| nodes.shape_149 | 1 | 6 | compactBody | [231.1381, 448.5464, 55.2302, 29.2549] |
| nodes.shape_153 | 1 | 6 | compactBody | [993.6414, 342.0719, 55.2302, 29.2549] |
| nodes.shape_154 | 1 | 6 | compactBody | [993.6414, 395.3092, 55.2302, 29.2549] |
| nodes.shape_156 | 1 | 6 | compactBody | [993.6414, 448.5464, 55.2302, 29.2549] |
| nodes.shape_160 | 1 | 20 | compactBody | [294.2431, 389.108, 182.8719, 31.2574] |
| nodes.shape_161 | 1 | 18 | compactBody | [812.0078, 389.108, 164.636, 31.2574] |
| nodes.shape_163 | 1 | 16 | compactBody | [566.7951, 339.2857, 146.4001, 31.2574] |
| nodes.shape_54 | 1 | 42 | caption | [486.828, 404.1804, 306.3538, 32.1571] |
| nodes.shape_166 | 1 | 7 | compactBody | [605.1438, 374.3064, 69.7125, 31.2574] |
| nodes.shape_167 | 1 | 7 | compactBody | [605.1438, 436.9664, 71.8311, 31.2574] |
| nodes.shape_207 | 1 | 29 | caption | [236.7685, 491.4807, 209.1665, 34.2468] |
| nodes.shape_205 | 1 | 29 | diagramCompact | [445.8479, 493.9863, 186.6062, 28.5003] |
| nodes.shape_208 | 1 | 6 | compactBody | [103.2932, 339.8081, 55.2302, 31.2574] |
| nodes.shape_209 | 1 | 32 | diagramCompact | [78.5466, 369.479, 104.7235, 43.7662] |
| nodes.shape_220 | 1 | 6 | compactBody | [1117.4135, 339.8081, 55.2302, 31.2574] |
| nodes.shape_221 | 1 | 32 | diagramCompact | [1092.6668, 369.479, 104.7235, 43.7662] |
### page-20

左目标列表2组；右顶产品需求椭圆；弧线串联4数据/核心目标簇；底部6个指标卡

Layout为`source-house-20`，原型为`templates/prototypes/source-house-20.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_60 | 1 | 17 | diagramMicro | [141.9584, 157.7247, 94.8761, 26.2669] |
| nodes.shape_61 | 1 | 17 | diagramMicro | [243.7954, 157.7247, 94.8761, 26.2669] |
| nodes.shape_62 | 1 | 36 | diagramMicro | [141.9584, 191.3229, 196.7045, 26.2669] |
| nodes.shape_64 | 1 | 36 | diagramMicro | [141.9584, 224.9211, 196.7045, 26.2669] |
| nodes.shape_71 | 1 | 30 | diagramCompact | [142.8457, 280.5219, 194.9385, 25.5519] |
| nodes.shape_73 | 1 | 36 | diagramMicro | [141.9584, 309.916, 196.7045, 26.2669] |
| nodes.shape_75 | 1 | 36 | diagramMicro | [141.9584, 343.5142, 196.7045, 26.2669] |
| nodes.shape_77 | 1 | 36 | diagramMicro | [141.9584, 377.1124, 196.7045, 26.2669] |
| nodes.shape_84 | 1 | 36 | diagramMicro | [141.9584, 410.7106, 196.7045, 26.2669] |
| nodes.shape_87 | 1 | 36 | diagramMicro | [141.9584, 444.3088, 196.7045, 26.2669] |
| nodes.shape_137 | 1 | 104 | diagramMicro | [157.3791, 541.2094, 143.4988, 64.9996] |
| nodes.shape_194 | 1 | 6 | diagramMicro | [257.7947, 513.1582, 33.2019, 15.0] |
| nodes.shape_215 | 1 | 14 | diagramCompact | [157.3791, 508.5933, 93.2565, 23.6652] |
| nodes.shape_219 | 1 | 104 | diagramMicro | [323.3284, 541.2094, 143.4988, 64.9996] |
| nodes.shape_221 | 1 | 6 | diagramMicro | [423.7525, 513.1582, 33.2019, 15.0] |
| nodes.shape_222 | 1 | 14 | diagramCompact | [323.3284, 508.5933, 93.2565, 23.6652] |
| nodes.shape_225 | 1 | 104 | diagramMicro | [489.2862, 541.2094, 143.4988, 64.9996] |
| nodes.shape_227 | 1 | 6 | diagramMicro | [589.7018, 513.1582, 33.2019, 15.0] |
| nodes.shape_228 | 1 | 14 | diagramCompact | [489.2862, 508.5933, 93.2565, 23.6652] |
| nodes.shape_231 | 1 | 104 | diagramMicro | [655.2355, 541.2094, 143.4988, 64.9996] |
| nodes.shape_233 | 1 | 6 | diagramMicro | [755.651, 513.1582, 33.2019, 15.0] |
| nodes.shape_234 | 1 | 14 | diagramCompact | [655.2355, 508.5933, 93.2565, 23.6652] |
| nodes.shape_237 | 1 | 104 | diagramMicro | [821.1848, 541.2094, 143.4988, 64.9996] |
| nodes.shape_239 | 1 | 6 | diagramMicro | [921.6089, 513.1582, 33.2019, 15.0] |
| nodes.shape_240 | 1 | 14 | diagramCompact | [821.1848, 508.5933, 93.2565, 23.6652] |
| nodes.shape_243 | 1 | 104 | diagramMicro | [987.1426, 541.2094, 143.4988, 64.9996] |
| nodes.shape_245 | 1 | 6 | diagramMicro | [1087.5582, 513.1582, 33.2019, 15.0] |
| nodes.shape_246 | 1 | 14 | diagramCompact | [987.1426, 508.5933, 93.2565, 23.6652] |
| nodes.shape_23 | 1 | 19 | diagramMicro | [548.1262, 207.8808, 103.8357, 23.4412] |
| nodes.shape_24 | 1 | 81 | diagramMicro | [539.0805, 236.6719, 147.9182, 50.5265] |
| nodes.shape_30 | 1 | 19 | diagramMicro | [869.6782, 207.8808, 103.8357, 23.4412] |
| nodes.shape_31 | 1 | 81 | diagramMicro | [834.6413, 236.6719, 147.9182, 50.5265] |
| nodes.shape_27 | 1 | 19 | diagramMicro | [434.5556, 303.1877, 103.8357, 23.4412] |
| nodes.shape_28 | 1 | 81 | diagramMicro | [425.51, 331.9788, 147.9182, 50.5265] |
| nodes.shape_33 | 1 | 19 | diagramMicro | [983.2487, 303.1877, 103.8357, 23.4412] |
| nodes.shape_34 | 1 | 81 | diagramMicro | [948.2204, 331.9788, 147.9182, 50.5265] |
| nodes.shape_38 | 1 | 21 | diagramMicro | [699.6971, 245.976, 118.6189, 23.0708] |
| nodes.shape_39 | 1 | 21 | diagramMicro | [699.6971, 275.2495, 118.6189, 23.0708] |
| nodes.shape_40 | 1 | 21 | diagramMicro | [699.6971, 304.5144, 118.6189, 23.0708] |
| nodes.shape_41 | 1 | 21 | diagramMicro | [699.6971, 333.7879, 118.6189, 23.0708] |
| nodes.shape_42 | 1 | 21 | diagramMicro | [699.6971, 363.0614, 118.6189, 23.0708] |
| nodes.shape_22 | 1 | 104 | diagramMicro | [618.5101, 148.9461, 283.0433, 32.8573] |
| nodes.shape_55 | 1 | 18 | diagramCompact | [702.0318, 216.0392, 113.9582, 27.1025] |
| nodes.shape_57 | 1 | 16 | diagramCompact | [708.984, 411.753, 106.446, 25.0522] |
| nodes.shape_63 | 1 | 272 | diagramMicro | [392.3511, 432.0153, 739.7204, 37.3285] |
### page-21

屋顶使命；愿景横梁；5根战略支柱，每柱3–4行动；底座ESG治理/数智创新2条

Layout为`source-house-21`，原型为`templates/prototypes/source-house-21.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_36 | 1 | 21 | compactBody | [49.7693, 120, 67.1686, 94.4927] |
| nodes.shape_33 | 1 | 14 | compactBody | [49.7693, 226.408, 67.1686, 70.3889] |
| nodes.shape_25 | 1 | 21 | compactBody | [49.7693, 560.1431, 67.1686, 87.8569] |
| nodes.shape_46 | 1 | 149 | caption | [139.3827, 569.1894, 1078.8254, 31.4911] |
| nodes.shape_47 | 1 | 149 | caption | [139.3827, 607.4627, 1078.8254, 31.4911] |
| nodes.shape_27 | 1 | 63 | compactBody | [49.7693, 308.7122, 67.1686, 239.5449] |
| nodes.shape_60 | 1 | 40 | compactBody | [142.7397, 315.8165, 180.193, 60.6986] |
| nodes.shape_81 | 1 | 40 | compactBody | [365.7144, 315.8165, 180.193, 60.6986] |
| nodes.shape_89 | 1 | 40 | compactBody | [588.6989, 315.8165, 180.193, 60.6986] |
| nodes.shape_97 | 1 | 40 | compactBody | [811.6737, 315.8165, 180.193, 60.6986] |
| nodes.shape_105 | 1 | 40 | compactBody | [1034.6582, 315.8165, 180.193, 60.6986] |
| nodes.shape_49 | 1 | 27 | diagramCompact | [146.2138, 384.0878, 173.2448, 31.8619] |
| nodes.shape_50 | 1 | 27 | diagramCompact | [146.2138, 422.6832, 173.2448, 31.8619] |
| nodes.shape_61 | 1 | 27 | diagramCompact | [146.2138, 461.2785, 173.2448, 31.8619] |
| nodes.shape_83 | 1 | 27 | diagramCompact | [369.1885, 384.0878, 173.2448, 31.8619] |
| nodes.shape_84 | 1 | 27 | diagramCompact | [369.1885, 422.6832, 173.2448, 31.8619] |
| nodes.shape_85 | 1 | 27 | diagramCompact | [369.1885, 461.2785, 173.2448, 31.8619] |
| nodes.shape_86 | 1 | 27 | diagramCompact | [369.1885, 499.8739, 173.2448, 31.8619] |
| nodes.shape_91 | 1 | 27 | diagramCompact | [592.173, 384.0878, 173.2448, 31.8619] |
| nodes.shape_92 | 1 | 27 | diagramCompact | [592.173, 422.6832, 173.2448, 31.8619] |
| nodes.shape_93 | 1 | 27 | diagramCompact | [592.173, 461.2785, 173.2448, 31.8619] |
| nodes.shape_94 | 1 | 27 | diagramCompact | [592.173, 499.8739, 173.2448, 31.8619] |
| nodes.shape_99 | 1 | 27 | diagramCompact | [815.1478, 384.0878, 173.2448, 31.8619] |
| nodes.shape_100 | 1 | 27 | diagramCompact | [815.1478, 422.6832, 173.2448, 31.8619] |
| nodes.shape_101 | 1 | 27 | diagramCompact | [815.1478, 461.2785, 173.2448, 31.8619] |
| nodes.shape_102 | 1 | 27 | diagramCompact | [815.1478, 499.8739, 173.2448, 31.8619] |
| nodes.shape_107 | 1 | 27 | diagramCompact | [1038.1323, 384.0878, 173.2448, 31.8619] |
| nodes.shape_108 | 1 | 27 | diagramCompact | [1038.1323, 422.6832, 173.2448, 31.8619] |
| nodes.shape_109 | 1 | 27 | diagramCompact | [1038.1323, 461.2785, 173.2448, 31.8619] |
| nodes.shape_24 | 1 | 60 | compactBody | [543.2043, 144.094, 271.1823, 59.9082] |
| nodes.shape_30 | 1 | 57 | compactBody | [419.7284, 243.1441, 518.1243, 34.6821] |
### page-22

与house21同5柱2底座，增加左侧使命/愿景/支柱/底座标签栏

Layout为`source-house-22`，原型为`templates/prototypes/source-house-22.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_36 | 1 | 36 | caption | [49.7693, 120, 67.1686, 94.4927] |
| nodes.shape_44 | 1 | 52 | compactBody | [553.7631, 144.7186, 239.6522, 53.6041] |
| nodes.shape_33 | 1 | 27 | caption | [49.7693, 226.408, 67.1686, 70.3889] |
| nodes.shape_45 | 1 | 52 | compactBody | [558.9644, 234.8004, 239.6522, 53.6041] |
| nodes.shape_25 | 1 | 36 | caption | [49.7693, 560.1431, 67.1686, 87.8569] |
| nodes.shape_46 | 1 | 147 | caption | [146.2138, 569.1894, 1065.1633, 31.4911] |
| nodes.shape_47 | 1 | 147 | caption | [146.2138, 607.4627, 1065.1633, 31.4911] |
| nodes.shape_27 | 1 | 99 | caption | [49.7693, 308.7122, 67.1686, 239.5449] |
| nodes.shape_60 | 1 | 40 | compactBody | [142.7397, 319.5638, 180.193, 60.6986] |
| nodes.shape_49 | 1 | 27 | diagramCompact | [146.2138, 384.0878, 173.2448, 32.3791] |
| nodes.shape_50 | 1 | 27 | diagramCompact | [146.2138, 423.3077, 173.2448, 32.3791] |
| nodes.shape_61 | 1 | 27 | diagramCompact | [146.2138, 462.5374, 173.2448, 32.3791] |
| nodes.shape_81 | 1 | 40 | compactBody | [365.7144, 319.5638, 180.193, 60.6986] |
| nodes.shape_83 | 1 | 27 | diagramCompact | [369.1885, 384.0878, 173.2448, 32.3791] |
| nodes.shape_84 | 1 | 27 | diagramCompact | [369.1885, 423.3077, 173.2448, 32.3791] |
| nodes.shape_85 | 1 | 27 | diagramCompact | [369.1885, 462.5374, 173.2448, 32.3791] |
| nodes.shape_86 | 1 | 27 | diagramCompact | [369.1885, 501.767, 173.2448, 32.3791] |
| nodes.shape_89 | 1 | 40 | compactBody | [588.6989, 319.5638, 180.193, 60.6986] |
| nodes.shape_91 | 1 | 27 | diagramCompact | [592.173, 384.0878, 173.2448, 32.3791] |
| nodes.shape_92 | 1 | 27 | diagramCompact | [592.173, 423.3077, 173.2448, 32.3791] |
| nodes.shape_93 | 1 | 27 | diagramCompact | [592.173, 462.5374, 173.2448, 32.3791] |
| nodes.shape_94 | 1 | 27 | diagramCompact | [592.173, 501.767, 173.2448, 32.3791] |
| nodes.shape_97 | 1 | 40 | compactBody | [811.6737, 319.5638, 180.193, 60.6986] |
| nodes.shape_99 | 1 | 27 | diagramCompact | [815.1478, 384.0878, 173.2448, 32.3791] |
| nodes.shape_100 | 1 | 27 | diagramCompact | [815.1478, 423.3077, 173.2448, 32.3791] |
| nodes.shape_101 | 1 | 27 | diagramCompact | [815.1478, 462.5374, 173.2448, 32.3791] |
| nodes.shape_102 | 1 | 27 | diagramCompact | [815.1478, 501.767, 173.2448, 32.3791] |
| nodes.shape_105 | 1 | 40 | compactBody | [1034.6582, 319.5638, 180.193, 60.6986] |
| nodes.shape_107 | 1 | 27 | diagramCompact | [1038.1323, 384.0878, 173.2448, 32.3791] |
| nodes.shape_108 | 1 | 27 | diagramCompact | [1038.1323, 423.3077, 173.2448, 32.3791] |
| nodes.shape_109 | 1 | 27 | diagramCompact | [1038.1323, 462.5374, 173.2448, 32.3791] |
### page-23

左认识→认知→兴趣→购买→忠诚纵向旅程；右3×3模块含运营、私域、门店及各自角色/关键工作/小图

Layout为`source-house-23`，原型为`templates/prototypes/source-house-23.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_6 | 1 | 10 | caption | [82.0541, 230.3387, 75.2296, 30.8744] |
| nodes.shape_7 | 1 | 10 | caption | [82.0541, 368.5581, 75.2296, 30.8744] |
| nodes.shape_8 | 1 | 10 | caption | [82.7077, 463.4548, 75.2296, 30.8744] |
| nodes.shape_9 | 1 | 10 | caption | [82.0541, 617.1162, 75.2296, 30.8744] |
| nodes.shape_159 | 1 | 18 | caption | [180.1434, 170.6078, 50.0678, 64.2877] |
| nodes.shape_162 | 1 | 15 | diagramMicro | [370.8369, 132.1356, 82.619, 21.4292] |
| nodes.shape_166 | 1 | 42 | diagramMicro | [370.8369, 177.9025, 76.2433, 45.9184] |
| nodes.shape_167 | 1 | 18 | diagramMicro | [370.8369, 250.0437, 100.6377, 21.4292] |
| nodes.shape_240 | 1 | 12 | caption | [527.8614, 179.7972, 50.0678, 45.9184] |
| nodes.shape_290 | 1 | 12 | caption | [874.7551, 179.7972, 50.0678, 45.9184] |
| nodes.shape_305 | 1 | 16 | diagramMicro | [1064.615, 133.083, 86.6074, 21.4292] |
| nodes.shape_309 | 1 | 48 | diagramMicro | [1064.615, 179.7972, 88.521, 45.9184] |
| nodes.shape_310 | 1 | 40 | diagramMicro | [1064.615, 244.8711, 110.2061, 33.6691] |
| nodes.shape_55 | 1 | 18 | caption | [527.8614, 533.1045, 50.0678, 64.2877] |
| nodes.shape_119 | 1 | 19 | diagramMicro | [717.7307, 495.5797, 103.9819, 21.4292] |
| nodes.shape_128 | 1 | 42 | diagramMicro | [717.7307, 542.2844, 79.5875, 45.9184] |
| nodes.shape_129 | 1 | 48 | diagramMicro | [717.7307, 607.3679, 130.6121, 33.6691] |
| nodes.shape_40 | 1 | 21 | diagramCompact | [585.7638, 489.0808, 132.6395, 24.4892] |
| nodes.shape_41 | 1 | 48 | diagramMicro | [585.7638, 506.6827, 88.4547, 52.1899] |
| nodes.shape_79 | 1 | 9 | diagramMicro | [673.7923, 566.8873, 19.4777, 57.7035] |
| nodes.shape_98 | 1 | 6 | diagramMicro | [615.1698, 567.3862, 35.7154, 15.0] |
| nodes.shape_116 | 1 | 6 | diagramMicro | [615.1698, 587.0249, 35.7154, 15.0] |
| nodes.shape_117 | 1 | 6 | diagramMicro | [615.1698, 605.6594, 35.7154, 15.0] |
| nodes.shape_118 | 1 | 6 | diagramMicro | [615.1698, 624.7961, 35.7154, 15.0] |
| nodes.shape_168 | 1 | 17 | diagramCompact | [238.8701, 126.5936, 107.5061, 24.4892] |
| nodes.shape_169 | 1 | 48 | diagramMicro | [238.8701, 144.186, 88.4547, 52.1899] |
| nodes.shape_176 | 1 | 2 | diagramMicro | [259.1909, 214.7325, 14.8261, 15.0] |
| nodes.shape_189 | 1 | 2 | diagramMicro | [259.0393, 246.109, 15.1482, 15.0] |
| nodes.shape_206 | 1 | 4 | diagramMicro | [310.8598, 230.4208, 26.7818, 15.0] |
| nodes.shape_249 | 1 | 21 | diagramCompact | [585.7638, 126.5936, 132.6395, 24.4892] |
| nodes.shape_250 | 1 | 48 | diagramMicro | [585.7638, 144.186, 88.4547, 52.1899] |
| nodes.shape_262 | 1 | 6 | diagramMicro | [594.6879, 211.7421, 19.4777, 43.01] |
| nodes.shape_257 | 1 | 3 | diagramMicro | [645.9968, 204.8895, 17.8577, 15.0] |
| nodes.shape_258 | 1 | 3 | diagramMicro | [646.0063, 224.5377, 17.8577, 15.0] |
| nodes.shape_259 | 1 | 3 | diagramMicro | [645.9968, 243.1627, 17.8577, 15.0] |
| nodes.shape_260 | 1 | 3 | diagramMicro | [646.0063, 262.3088, 17.8577, 15.0] |
| nodes.shape_292 | 1 | 21 | diagramCompact | [932.6481, 126.5936, 132.6395, 24.4892] |
| nodes.shape_293 | 1 | 64 | diagramMicro | [932.6481, 144.186, 88.4547, 66.8834] |
| nodes.shape_316 | 1 | 3 | diagramMicro | [945.5227, 218.8535, 17.8577, 15.0] |
| nodes.shape_347 | 1 | 3 | diagramMicro | [982.1759, 218.8535, 17.8577, 15.0] |
| nodes.shape_350 | 1 | 3 | diagramMicro | [1018.8292, 218.8535, 17.8577, 15.0] |
| nodes.shape_366 | 1 | 3 | diagramMicro | [945.5227, 251.0732, 17.8577, 15.0] |
| nodes.shape_364 | 1 | 3 | diagramMicro | [982.1759, 251.0732, 17.8577, 15.0] |
| nodes.shape_361 | 1 | 3 | diagramMicro | [1018.8292, 251.0732, 17.8577, 15.0] |
| nodes.shape_415 | 1 | 18 | caption | [180.9771, 351.8562, 50.0678, 64.2877] |
| nodes.shape_424 | 1 | 48 | diagramMicro | [370.8369, 426.1195, 130.6121, 33.6691] |
| nodes.shape_417 | 1 | 21 | diagramCompact | [238.8701, 307.8325, 132.6395, 24.4892] |
| nodes.shape_418 | 1 | 57 | diagramMicro | [238.8701, 325.4344, 106.9377, 52.1899] |
| nodes.shape_445 | 1 | 3 | diagramMicro | [251.7447, 385.5221, 17.8577, 15.0] |
| nodes.shape_443 | 1 | 3 | diagramMicro | [288.3979, 385.5221, 17.8577, 15.0] |
| nodes.shape_429 | 1 | 3 | diagramMicro | [325.0512, 385.5221, 17.8577, 15.0] |
| nodes.shape_457 | 1 | 3 | diagramMicro | [288.3979, 415.648, 17.8577, 15.0] |
| nodes.shape_458 | 1 | 3 | diagramMicro | [266.6087, 437.8825, 17.8577, 15.0] |
| nodes.shape_459 | 1 | 3 | diagramMicro | [310.1871, 437.8825, 17.8577, 15.0] |
| nodes.shape_493 | 1 | 16 | caption | [521.0499, 361.0361, 63.7856, 45.9184] |
| nodes.shape_500 | 1 | 44 | diagramMicro | [717.7307, 426.1195, 120.4091, 33.6691] |
| nodes.shape_501 | 1 | 21 | diagramCompact | [585.7638, 307.8325, 132.6395, 24.4892] |
| nodes.shape_502 | 1 | 57 | diagramMicro | [585.7638, 325.4344, 106.9377, 52.1899] |
| nodes.shape_552 | 1 | 3 | diagramMicro | [635.9832, 388.6768, 17.8577, 15.0] |
| nodes.shape_555 | 1 | 3 | diagramMicro | [601.5279, 406.1366, 17.8577, 15.0] |
| nodes.shape_558 | 1 | 3 | diagramMicro | [619.5561, 433.2783, 17.8577, 15.0] |
| nodes.shape_561 | 1 | 3 | diagramMicro | [655.2904, 433.2783, 17.8577, 15.0] |
| nodes.shape_564 | 1 | 3 | diagramMicro | [670.4386, 406.1366, 17.8577, 15.0] |
| nodes.shape_595 | 1 | 16 | caption | [867.9436, 361.0361, 63.7856, 45.9184] |
| nodes.shape_419 | 1 | 10 | diagramMicro | [370.8369, 314.3314, 58.8593, 21.4292] |
| nodes.shape_495 | 1 | 7 | diagramMicro | [717.7307, 314.3314, 42.7637, 21.4292] |
| nodes.shape_597 | 1 | 19 | diagramMicro | [1064.615, 314.3314, 103.9819, 21.4292] |
| nodes.shape_423 | 1 | 57 | diagramMicro | [370.8369, 361.0361, 104.6166, 45.9184] |
| nodes.shape_499 | 1 | 60 | diagramMicro | [717.7307, 361.0361, 110.2061, 45.9184] |
| nodes.shape_601 | 1 | 42 | diagramMicro | [1064.615, 361.0361, 79.5875, 45.9184] |
| nodes.shape_602 | 1 | 48 | diagramMicro | [1064.615, 426.1195, 130.6121, 33.6691] |
| nodes.shape_603 | 1 | 21 | diagramCompact | [932.6481, 307.8325, 132.6395, 24.4892] |
| nodes.shape_604 | 1 | 38 | diagramMicro | [932.6481, 325.4344, 106.9377, 37.4964] |
| nodes.shape_653 | 1 | 21 | caption | [176.8656, 533.1045, 56.5572, 64.2877] |
| nodes.shape_655 | 1 | 19 | diagramMicro | [370.8369, 495.5797, 103.9819, 21.4292] |
| nodes.shape_659 | 1 | 45 | diagramMicro | [370.8369, 542.2844, 85.1674, 45.9184] |
| nodes.shape_660 | 1 | 34 | diagramMicro | [370.8369, 607.3679, 95.3704, 33.6691] |
| nodes.shape_661 | 1 | 21 | diagramCompact | [238.8701, 489.0808, 132.6395, 24.4892] |
| nodes.shape_662 | 1 | 57 | diagramMicro | [238.8701, 506.6827, 106.9377, 52.1899] |
| nodes.shape_770 | 1 | 18 | caption | [874.7551, 533.1045, 50.0678, 64.2877] |
| nodes.shape_772 | 1 | 19 | diagramMicro | [1064.615, 495.5797, 103.9819, 21.4292] |
| nodes.shape_776 | 1 | 42 | diagramMicro | [1064.615, 542.2844, 79.5875, 45.9184] |
| nodes.shape_777 | 1 | 28 | diagramMicro | [1064.615, 607.3679, 79.5875, 33.6691] |
| nodes.shape_778 | 1 | 21 | diagramCompact | [932.6481, 489.0808, 132.6395, 24.4892] |
| nodes.shape_779 | 1 | 80 | diagramMicro | [932.6481, 506.6827, 111.5418, 66.8834] |
| nodes.shape_790 | 1 | 3 | diagramMicro | [982.1759, 594.3669, 17.8577, 15.0] |
| nodes.shape_791 | 1 | 3 | diagramMicro | [960.3962, 616.6014, 17.8577, 15.0] |
| nodes.shape_792 | 1 | 3 | diagramMicro | [1003.9651, 616.6014, 17.8577, 15.0] |
| nodes.shape_826 | 1 | 10 | diagramMicro | [717.7307, 133.083, 58.8593, 21.4292] |
| nodes.shape_829 | 1 | 66 | diagramMicro | [717.7307, 179.7972, 122.3227, 45.9184] |
| nodes.shape_830 | 1 | 22 | diagramMicro | [717.7307, 250.9911, 120.4091, 21.4292] |
| nodes.shape_856 | 1 | 3 | diagramMicro | [948.4121, 406.1366, 17.8577, 15.0] |
| nodes.shape_857 | 1 | 3 | diagramMicro | [982.8675, 388.6768, 17.8577, 15.0] |
| nodes.shape_858 | 1 | 3 | diagramMicro | [966.4403, 433.2783, 17.8577, 15.0] |
| nodes.shape_859 | 1 | 3 | diagramMicro | [1002.1841, 433.2783, 17.8577, 15.0] |
| nodes.shape_860 | 1 | 3 | diagramMicro | [1017.3324, 406.1366, 17.8577, 15.0] |
### page-24

顶部总平台；左脑3能力柱、右脑2能力柱；外围4服务圈；底部技术底座；大外椭圆边界

Layout为`source-house-24`，原型为`templates/prototypes/source-house-24.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_21 | 1 | 18 | caption | [118.3206, 355.9746, 132.3152, 39.4859] |
| nodes.shape_25 | 1 | 18 | caption | [118.3206, 500.3717, 132.3152, 39.4859] |
| nodes.shape_55 | 1 | 58 | compactBody | [365.3029, 543.1688, 529.8554, 33.0411] |
| nodes.shape_56 | 1 | 9 | compactBody | [596.1465, 590.2093, 89.953, 30.2891] |
| nodes.shape_69 | 1 | 22 | diagramMicro | [299.2918, 297.6423, 120.2244, 22.8234] |
| nodes.shape_73 | 1 | 5 | heading | [322.9053, 429.8776, 72.9975, 63.3391] |
| nodes.shape_72 | 1 | 153 | diagramMicro | [313.4954, 326.9017, 91.8172, 131.0546] |
| nodes.shape_77 | 1 | 22 | diagramMicro | [431.5803, 297.6423, 120.2244, 22.8234] |
| nodes.shape_78 | 1 | 5 | heading | [455.1938, 429.8776, 72.9975, 63.3391] |
| nodes.shape_79 | 1 | 180 | diagramMicro | [435.0247, 326.9017, 113.3356, 131.0546] |
| nodes.shape_82 | 1 | 22 | diagramMicro | [562.777, 297.6423, 120.2244, 22.8234] |
| nodes.shape_83 | 1 | 5 | heading | [586.3904, 429.8776, 72.9975, 63.3391] |
| nodes.shape_84 | 1 | 90 | diagramMicro | [582.3601, 326.9017, 81.0669, 100.073] |
| nodes.shape_87 | 1 | 22 | diagramMicro | [727.7514, 297.6423, 120.2244, 22.8234] |
| nodes.shape_88 | 1 | 5 | heading | [751.3649, 429.8776, 72.9975, 63.3391] |
| nodes.shape_89 | 1 | 99 | diagramMicro | [758.0938, 326.9017, 59.5485, 131.0546] |
| nodes.shape_92 | 1 | 22 | diagramMicro | [860.5282, 297.6423, 120.2244, 22.8234] |
| nodes.shape_93 | 1 | 5 | heading | [884.1417, 429.8776, 72.9975, 63.3391] |
| nodes.shape_94 | 1 | 135 | diagramMicro | [880.1025, 326.9017, 81.0669, 131.0546] |
| nodes.shape_169 | 1 | 18 | caption | [1029.3643, 355.9746, 132.3152, 39.4859] |
| nodes.shape_172 | 1 | 18 | caption | [1029.3643, 500.3717, 132.3152, 39.4859] |
| nodes.shape_186 | 1 | 6 | compactBody | [464.3107, 236.1763, 54.7725, 31.2123] |
| nodes.shape_225 | 1 | 6 | compactBody | [832.0145, 236.1763, 54.7725, 31.2123] |
### page-25

顶6指标；中商业/自然流量2圈与协同箭头；底部购买人群资产横梁和5个研究问题

Layout为`source-house-25`，原型为`templates/prototypes/source-house-25.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_33 | 1 | 302 | caption | [94.5594, 478.6248, 1090.8812, 44.9532] |
| nodes.shape_278 | 1 | 28 | caption | [94.5594, 534.2559, 207.3925, 39.8547] |
| nodes.shape_44 | 1 | 58 | diagramCompact | [103.7943, 581.1907, 188.9225, 46.829] |
| nodes.shape_45 | 1 | 58 | diagramCompact | [322.3746, 581.1907, 188.9225, 46.829] |
| nodes.shape_47 | 1 | 28 | caption | [315.4291, 534.2559, 207.3925, 39.8547] |
| nodes.shape_48 | 1 | 28 | caption | [536.3085, 534.2559, 207.3925, 39.8547] |
| nodes.shape_49 | 1 | 28 | caption | [757.1783, 534.2559, 207.3925, 39.8547] |
| nodes.shape_50 | 1 | 28 | caption | [978.0481, 534.2559, 207.3925, 39.8547] |
| nodes.shape_53 | 1 | 58 | diagramCompact | [545.5339, 581.1907, 188.9225, 46.829] |
| nodes.shape_54 | 1 | 58 | diagramCompact | [766.4133, 581.1907, 188.9225, 46.829] |
| nodes.shape_55 | 1 | 29 | diagramCompact | [987.2831, 581.1907, 188.9225, 27.2528] |
| nodes.shape_295 | 1 | 18 | caption | [573.4216, 281.8525, 133.1568, 39.4314] |
| nodes.shape_292 | 1 | 44 | caption | [495.9248, 334.819, 84.6251, 84.6251] |
| nodes.shape_293 | 1 | 44 | caption | [699.4597, 334.819, 84.6251, 84.6251] |
| nodes.shape_61 | 1 | 45 | compactBody | [89.8553, 141.7888, 143.902, 98.6314] |
| nodes.shape_412 | 1 | 45 | compactBody | [281.1347, 141.7888, 143.902, 98.6314] |
| nodes.shape_415 | 1 | 45 | compactBody | [472.4141, 141.7888, 143.902, 98.6314] |
| nodes.shape_418 | 1 | 45 | compactBody | [663.6934, 141.7888, 143.902, 98.6314] |
| nodes.shape_421 | 1 | 45 | compactBody | [854.9728, 141.7888, 143.902, 98.6314] |
| nodes.shape_424 | 1 | 45 | compactBody | [1046.2522, 141.7888, 143.902, 98.6314] |
| nodes.shape_323 | 1 | 24 | caption | [294.3715, 293.6175, 176.7728, 38.758] |
| nodes.shape_327 | 1 | 112 | diagramCompact | [294.3715, 343.775, 176.7728, 69.3777] |
| nodes.shape_433 | 1 | 24 | caption | [97.2529, 293.6175, 176.7728, 38.758] |
| nodes.shape_434 | 1 | 112 | diagramCompact | [97.2529, 343.775, 176.7728, 69.3777] |
| nodes.shape_443 | 1 | 24 | caption | [1005.9743, 293.6175, 176.7728, 38.758] |
| nodes.shape_444 | 1 | 112 | diagramCompact | [1005.9743, 343.775, 176.7728, 69.3777] |
| nodes.shape_441 | 1 | 24 | caption | [808.8557, 293.6175, 176.7728, 38.758] |
| nodes.shape_442 | 1 | 112 | diagramCompact | [808.8557, 343.775, 176.7728, 69.3777] |
| nodes.shape_446 | 1 | 5 | compactBody | [613.3821, 353.1638, 53.2358, 30.2445] |
### page-26

左目标原则4卡与Why/What/Choose模型+SMART分支；右Task/Who/Time行动计划、团队共识、工具

Layout为`source-house-26`，原型为`templates/prototypes/source-house-26.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_5 | 1 | 28 | diagramCompact | [199.4028, 210.7188, 29.0904, 122.5706] |
| nodes.shape_7 | 1 | 72 | diagramCompact | [199.4028, 343.5768, 29.0904, 304.4232] |
| nodes.shape_8 | 1 | 75 | diagramMicro | [240.4086, 343.5768, 408.8213, 27.8852] |
| nodes.shape_9 | 1 | 16 | diagramMicro | [240.4086, 377.1444, 91.6127, 24.5013] |
| nodes.shape_10 | 1 | 28 | diagramMicro | [337.6877, 377.1444, 155.6673, 24.5013] |
| nodes.shape_11 | 1 | 27 | diagramMicro | [499.0215, 377.1444, 150.2084, 24.5013] |
| nodes.shape_12 | 1 | 16 | diagramMicro | [240.4086, 407.3281, 91.6127, 24.5013] |
| nodes.shape_13 | 1 | 28 | diagramMicro | [337.6877, 407.3281, 155.6673, 24.5013] |
| nodes.shape_14 | 1 | 27 | diagramMicro | [499.0215, 407.3281, 150.2084, 24.5013] |
| nodes.shape_15 | 1 | 16 | diagramMicro | [240.4086, 437.5119, 91.6127, 24.5013] |
| nodes.shape_16 | 1 | 28 | diagramMicro | [337.6877, 437.5119, 155.6673, 24.5013] |
| nodes.shape_17 | 1 | 27 | diagramMicro | [499.0215, 437.5119, 150.2084, 24.5013] |
| nodes.shape_18 | 1 | 28 | diagramCompact | [676.4926, 213.8394, 29.0904, 119.45] |
| nodes.shape_19 | 1 | 75 | diagramMicro | [717.4985, 213.8394, 408.8213, 28.1247] |
| nodes.shape_20 | 1 | 16 | diagramMicro | [717.4985, 247.6943, 91.6127, 24.7168] |
| nodes.shape_21 | 1 | 28 | diagramMicro | [814.7776, 247.6943, 155.6673, 24.7168] |
| nodes.shape_22 | 1 | 27 | diagramMicro | [976.1114, 247.6943, 150.2084, 24.7168] |
| nodes.shape_23 | 1 | 16 | diagramMicro | [717.4985, 278.1334, 91.6127, 24.7168] |
| nodes.shape_24 | 1 | 28 | diagramMicro | [814.7776, 278.1334, 155.6673, 24.7168] |
| nodes.shape_25 | 1 | 27 | diagramMicro | [976.1114, 278.1334, 150.2084, 24.7168] |
| nodes.shape_26 | 1 | 16 | diagramMicro | [717.4985, 308.5726, 91.6127, 24.7168] |
| nodes.shape_27 | 1 | 28 | diagramMicro | [814.7776, 308.5726, 155.6673, 24.7168] |
| nodes.shape_28 | 1 | 27 | diagramMicro | [976.1114, 308.5726, 150.2084, 24.7168] |
| nodes.shape_29 | 1 | 48 | diagramCompact | [676.4926, 343.5768, 29.0904, 210.967] |
| nodes.shape_30 | 1 | 150 | diagramMicro | [717.4985, 343.5768, 408.8213, 31.0217] |
| nodes.shape_31 | 1 | 16 | diagramMicro | [717.4985, 380.2091, 91.6127, 27.2548] |
| nodes.shape_704 | 1 | 112 | diagramMicro | [717.4985, 413.0744, 91.6127, 108.604] |
| nodes.shape_705 | 1 | 16 | diagramMicro | [717.4985, 527.281, 91.6127, 27.2548] |
| nodes.shape_706 | 1 | 57 | diagramMicro | [814.7776, 380.2091, 311.5422, 27.2548] |
| nodes.shape_708 | 1 | 57 | diagramMicro | [814.7776, 527.281, 311.5422, 27.2548] |
| nodes.shape_709 | 1 | 16 | diagramCompact | [676.4926, 564.8311, 29.0904, 83.1689] |
| nodes.shape_710 | 1 | 75 | diagramMicro | [717.4985, 624.7756, 408.8213, 23.2244] |
| nodes.shape_711 | 1 | 18 | diagramMicro | [717.4985, 564.8311, 99.1067, 23.2244] |
| nodes.shape_712 | 1 | 18 | diagramMicro | [717.4985, 594.8073, 99.1067, 23.2244] |
| nodes.shape_713 | 1 | 18 | diagramMicro | [820.7393, 564.8311, 99.1067, 23.2244] |
| nodes.shape_714 | 1 | 18 | diagramMicro | [820.7393, 594.8073, 99.1067, 23.2244] |
| nodes.shape_715 | 1 | 18 | diagramMicro | [923.9722, 564.8311, 99.1067, 23.2244] |
| nodes.shape_716 | 1 | 18 | diagramMicro | [923.9722, 594.8073, 99.1067, 23.2244] |
| nodes.shape_717 | 1 | 18 | diagramMicro | [1027.213, 564.8311, 99.1067, 23.2244] |
| nodes.shape_718 | 1 | 18 | diagramMicro | [1027.213, 594.8073, 99.1067, 23.2244] |
| nodes.shape_719 | 1 | 44 | diagramMicro | [324.2639, 621.7827, 241.1188, 21.2771] |
| nodes.shape_722 | 1 | 11 | diagramMicro | [284.4951, 216.8641, 62.7538, 21.9235] |
| nodes.shape_723 | 1 | 56 | diagramMicro | [284.4951, 232.6264, 153.0336, 34.5812] |
| nodes.shape_725 | 1 | 13 | diagramMicro | [492.0542, 216.8641, 74.5735, 21.9235] |
| nodes.shape_726 | 1 | 56 | diagramMicro | [492.0542, 232.6264, 153.0336, 34.5812] |
| nodes.shape_853 | 1 | 11 | diagramMicro | [284.4951, 280.5197, 62.7538, 21.9235] |
| nodes.shape_854 | 1 | 56 | diagramMicro | [284.4951, 296.282, 153.0336, 34.5812] |
| nodes.shape_856 | 1 | 11 | diagramMicro | [492.0542, 280.5197, 62.7538, 21.9235] |
| nodes.shape_857 | 1 | 56 | diagramMicro | [492.0542, 296.282, 153.0336, 34.5812] |
| nodes.shape_858 | 1 | 29 | diagramMicro | [434.4561, 482.3007, 158.1255, 21.7559] |
| nodes.shape_859 | 1 | 29 | diagramMicro | [434.4561, 510.154, 158.1255, 21.7559] |
| nodes.shape_860 | 1 | 29 | diagramMicro | [434.4561, 538.0153, 158.1255, 21.7559] |
| nodes.shape_861 | 1 | 29 | diagramMicro | [434.4561, 565.8686, 158.1255, 21.7559] |
| nodes.shape_862 | 1 | 29 | diagramMicro | [434.4561, 593.7219, 158.1255, 21.7559] |
| nodes.shape_863 | 1 | 19 | diagramMicro | [297.057, 538.0153, 105.3558, 21.7559] |
| nodes.shape_871 | 1 | 9 | diagramMicro | [829.5742, 425.3011, 51.4688, 20.6546] |
| nodes.shape_873 | 1 | 156 | diagramMicro | [829.5742, 442.6037, 284.1039, 48.4999] |
| nodes.shape_874 | 1 | 40 | diagramMicro | [829.5742, 488.7732, 216.809, 19.3377] |
### page-27

虚线屋顶口号；定位与价值2层；3人群；3列执行策略；立体底板

Layout为`source-house-27`，原型为`templates/prototypes/source-house-27.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_25 | 1 | 14 | caption | [595.3756, 191.051, 107.3697, 28.3711] |
| nodes.shape_27 | 1 | 20 | caption | [270.055, 348.5169, 75.2558, 44.9132] |
| nodes.shape_28 | 1 | 14 | caption | [281.8763, 417.4269, 51.6133, 44.9517] |
| nodes.shape_29 | 1 | 14 | caption | [281.8763, 489.1325, 51.6133, 44.9517] |
| nodes.shape_31 | 1 | 47 | heading | [351.826, 215.9335, 603.3406, 40.1847] |
| nodes.shape_26 | 1 | 12 | caption | [283.5937, 278.4516, 45.7065, 44.9132] |
| nodes.shape_453 | 1 | 117 | diagramCompact | [282.2768, 309.572, 740.8219, 23.6426] |
| nodes.shape_468 | 1 | 7 | diagramMicro | [546.0727, 274.8166, 37.8282, 21.2783] |
| nodes.shape_469 | 1 | 7 | diagramMicro | [633.0728, 274.9476, 37.8282, 21.2783] |
| nodes.shape_470 | 1 | 7 | diagramMicro | [722.4834, 275.2402, 37.8282, 21.2783] |
| nodes.shape_472 | 1 | 90 | diagramCompact | [376.3543, 347.8315, 285.1898, 45.5139] |
| nodes.shape_473 | 1 | 90 | diagramCompact | [720.7892, 347.8315, 285.1898, 45.5139] |
| nodes.shape_475 | 1 | 72 | diagramCompact | [345.3108, 416.988, 227.5619, 45.5524] |
| nodes.shape_476 | 1 | 72 | diagramCompact | [577.5551, 416.988, 227.5619, 45.5524] |
| nodes.shape_477 | 1 | 72 | diagramCompact | [809.4681, 416.988, 227.5619, 45.4831] |
| nodes.shape_479 | 1 | 245 | diagramMicro | [376.3543, 485.6901, 190.1804, 111.2973] |
| nodes.shape_50 | 1 | 245 | diagramMicro | [604.9327, 485.6901, 190.1804, 111.2973] |
| nodes.shape_55 | 1 | 245 | diagramMicro | [833.5112, 485.6901, 190.1804, 111.2973] |
### page-28

梯形总框；应用层3业务域多应用；技术层7技术+5圆柱设施；支撑层4轮/圈；两侧上行箭头

Layout为`source-house-28`，原型为`templates/prototypes/source-house-28.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_22 | 1 | 84 | compactBody | [276.206, 211.4736, 760.3958, 30.1133] |
| nodes.shape_24 | 1 | 14 | compactBody | [441.2856, 239.436, 134.0733, 32.241] |
| nodes.shape_25 | 1 | 14 | compactBody | [589.3673, 239.436, 134.0733, 32.241] |
| nodes.shape_26 | 1 | 14 | compactBody | [747.9319, 239.436, 134.0733, 32.241] |
| nodes.shape_34 | 1 | 48 | caption | [201.676, 285.5067, 63.5268, 131.4564] |
| nodes.shape_35 | 1 | 11 | diagramMicro | [201.676, 353.0092, 63.5268, 18.815] |
| nodes.shape_40 | 1 | 32 | caption | [201.676, 423.7576, 63.5268, 88.1346] |
| nodes.shape_45 | 1 | 11 | diagramMicro | [201.676, 474.2156, 63.5268, 18.815] |
| nodes.shape_46 | 1 | 32 | caption | [201.676, 541.6483, 63.5268, 92.2579] |
| nodes.shape_49 | 1 | 11 | diagramMicro | [201.676, 587.191, 63.5268, 18.815] |
| nodes.shape_451 | 1 | 7 | diagramMicro | [421.1894, 288.24, 40.1459, 22.5811] |
| nodes.shape_452 | 1 | 15 | diagramMicro | [302.4212, 319.9995, 82.2175, 21.5872] |
| nodes.shape_453 | 1 | 15 | diagramMicro | [400.1536, 319.9995, 82.2175, 21.5872] |
| nodes.shape_454 | 1 | 15 | diagramMicro | [497.8937, 319.9995, 82.2175, 21.5872] |
| nodes.shape_455 | 1 | 15 | diagramMicro | [302.4212, 350.7729, 82.2175, 21.5872] |
| nodes.shape_456 | 1 | 15 | diagramMicro | [400.1536, 350.7729, 82.2175, 21.5872] |
| nodes.shape_457 | 1 | 15 | diagramMicro | [497.8937, 350.7729, 82.2175, 21.5872] |
| nodes.shape_459 | 1 | 15 | diagramMicro | [302.4212, 381.5384, 82.2175, 21.5872] |
| nodes.shape_460 | 1 | 15 | diagramMicro | [400.1536, 381.5384, 82.2175, 21.5872] |
| nodes.shape_470 | 1 | 15 | diagramMicro | [497.8937, 381.5384, 82.2175, 21.5872] |
| nodes.shape_474 | 1 | 7 | diagramMicro | [749.4849, 288.24, 40.1459, 22.5811] |
| nodes.shape_475 | 1 | 15 | diagramMicro | [630.709, 319.9995, 82.2175, 21.5872] |
| nodes.shape_476 | 1 | 15 | diagramMicro | [728.4491, 319.9995, 82.2175, 21.5872] |
| nodes.shape_477 | 1 | 15 | diagramMicro | [826.1814, 319.9995, 82.2175, 21.5872] |
| nodes.shape_478 | 1 | 15 | diagramMicro | [630.709, 350.7729, 82.2175, 21.5872] |
| nodes.shape_479 | 1 | 15 | diagramMicro | [728.4491, 350.7729, 82.2175, 21.5872] |
| nodes.shape_480 | 1 | 15 | diagramMicro | [826.1814, 350.7729, 82.2175, 21.5872] |
| nodes.shape_481 | 1 | 15 | diagramMicro | [630.709, 381.5384, 82.2175, 21.5872] |
| nodes.shape_482 | 1 | 15 | diagramMicro | [728.4491, 381.5384, 82.2175, 21.5872] |
| nodes.shape_486 | 1 | 15 | diagramMicro | [977.3458, 319.9995, 82.2175, 21.5872] |
| nodes.shape_489 | 1 | 15 | diagramMicro | [977.3458, 350.7729, 82.2175, 21.5872] |
| nodes.shape_492 | 1 | 15 | diagramMicro | [977.3458, 381.5384, 82.2175, 21.5872] |
| nodes.shape_497 | 1 | 7 | diagramMicro | [998.3817, 288.24, 40.1459, 22.5811] |
| nodes.shape_498 | 1 | 12 | diagramMicro | [295.021, 433.5184, 67.3317, 22.5811] |
| nodes.shape_499 | 1 | 19 | diagramMicro | [295.021, 483.1534, 106.406, 22.5811] |
| nodes.shape_514 | 1 | 10 | diagramMicro | [474.8544, 486.8263, 58.9609, 20.7019] |
| nodes.shape_515 | 1 | 10 | diagramMicro | [642.3179, 486.8263, 58.9609, 20.7019] |
| nodes.shape_516 | 1 | 12 | diagramMicro | [812.5691, 486.8263, 69.9408, 20.7019] |
| nodes.shape_517 | 1 | 6 | diagramMicro | [1002.7146, 486.8263, 37.0088, 20.7019] |
| nodes.shape_538 | 1 | 9 | diagramMicro | [392.5748, 536.4457, 53.7737, 20.1428] |
| nodes.shape_539 | 1 | 9 | diagramMicro | [347.3504, 548.2099, 53.7737, 20.1428] |
| nodes.shape_540 | 1 | 9 | diagramMicro | [392.1865, 583.7821, 53.7737, 18.815] |
| nodes.shape_543 | 1 | 13 | diagramMicro | [429.6534, 548.2099, 74.5533, 20.1428] |
| nodes.shape_688 | 1 | 9 | diagramMicro | [557.1185, 536.4457, 53.7737, 20.1428] |
| nodes.shape_689 | 1 | 9 | diagramMicro | [511.8942, 548.2099, 53.7737, 20.1428] |
| nodes.shape_690 | 1 | 9 | diagramMicro | [556.7303, 583.7821, 53.7737, 18.815] |
| nodes.shape_692 | 1 | 9 | diagramMicro | [604.587, 548.2099, 53.7737, 20.1428] |
| nodes.shape_702 | 1 | 9 | diagramMicro | [721.6623, 536.4457, 53.7737, 20.1428] |
| nodes.shape_703 | 1 | 9 | diagramMicro | [676.438, 548.2099, 53.7737, 20.1428] |
| nodes.shape_704 | 1 | 9 | diagramMicro | [721.2741, 583.7821, 53.7737, 18.815] |
| nodes.shape_706 | 1 | 9 | diagramMicro | [769.1308, 548.2099, 53.7737, 20.1428] |
| nodes.shape_716 | 1 | 15 | diagramMicro | [871.5999, 536.4457, 82.9863, 20.1428] |
| nodes.shape_717 | 1 | 9 | diagramMicro | [840.9818, 548.2099, 53.7737, 20.1428] |
| nodes.shape_718 | 1 | 9 | diagramMicro | [885.8179, 583.7821, 53.7737, 18.815] |
| nodes.shape_720 | 1 | 9 | diagramMicro | [933.6746, 548.2099, 53.7737, 20.1428] |
| nodes.shape_733 | 1 | 5 | diagramMicro | [427.7509, 426.39, 28.3817, 20.0729] |
| nodes.shape_13 | 1 | 12 | diagramMicro | [505.1541, 426.39, 66.1514, 20.0729] |
| nodes.shape_19 | 1 | 8 | diagramMicro | [611.3116, 426.39, 46.4201, 20.0729] |
| nodes.shape_36 | 1 | 8 | diagramMicro | [707.5996, 426.39, 46.4201, 20.0729] |
| nodes.shape_48 | 1 | 8 | diagramMicro | [803.9498, 426.39, 46.2881, 20.0729] |
| nodes.shape_55 | 1 | 8 | diagramMicro | [900.1757, 426.39, 46.4201, 20.0729] |
| nodes.shape_61 | 1 | 10 | diagramMicro | [991.2377, 426.39, 56.872, 20.0729] |
### page-29

屋顶；触点11小块；应用8椭圆；业务/数据双中台；云平台基础；左层标签

Layout为`source-house-29`，原型为`templates/prototypes/source-house-29.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_11 | 1 | 16 | compactBody | [122.3109, 592.9075, 144.876, 30.9924] |
| nodes.shape_13 | 1 | 20 | diagramCompact | [122.3109, 618.1639, 129.779, 25.3574] |
| nodes.shape_53 | 1 | 16 | compactBody | [122.3109, 391.9752, 144.876, 30.9924] |
| nodes.shape_54 | 1 | 20 | diagramCompact | [122.3109, 417.2409, 129.779, 25.3574] |
| nodes.shape_55 | 1 | 16 | compactBody | [122.3109, 270.768, 144.876, 30.9924] |
| nodes.shape_56 | 1 | 20 | diagramCompact | [122.3109, 296.0245, 129.779, 25.3574] |
| nodes.shape_57 | 1 | 16 | compactBody | [122.3109, 189.4094, 144.876, 30.9924] |
| nodes.shape_58 | 1 | 20 | diagramCompact | [122.3109, 214.6659, 129.779, 25.3574] |
| nodes.shape_59 | 1 | 16 | compactBody | [290.5804, 391.9752, 144.876, 30.9924] |
| nodes.shape_60 | 1 | 20 | diagramCompact | [376.3533, 397.1881, 129.779, 25.3574] |
| nodes.shape_450 | 1 | 16 | compactBody | [740.9662, 391.9752, 144.876, 30.9924] |
| nodes.shape_451 | 1 | 20 | diagramCompact | [826.7392, 397.1881, 129.779, 25.3574] |
| nodes.shape_477 | 1 | 14 | diagramCompact | [306.3932, 436.4035, 91.3161, 25.3574] |
| nodes.shape_479 | 1 | 14 | diagramCompact | [443.2298, 436.4035, 91.3161, 25.3574] |
| nodes.shape_481 | 1 | 14 | diagramCompact | [580.0755, 436.4035, 91.3161, 25.3574] |
| nodes.shape_483 | 1 | 14 | diagramCompact | [306.3932, 481.5752, 91.3161, 25.3574] |
| nodes.shape_485 | 1 | 14 | diagramCompact | [443.2298, 481.5752, 91.3161, 25.3574] |
| nodes.shape_487 | 1 | 14 | diagramCompact | [580.0755, 481.5752, 91.3161, 25.3574] |
| nodes.shape_489 | 1 | 14 | diagramCompact | [306.3932, 526.7469, 91.3161, 25.3574] |
| nodes.shape_491 | 1 | 14 | diagramCompact | [443.2298, 526.7469, 91.3161, 25.3574] |
| nodes.shape_493 | 1 | 14 | diagramCompact | [580.0755, 526.7469, 91.3161, 25.3574] |
| nodes.shape_512 | 1 | 20 | diagramCompact | [764.0385, 447.7377, 31.2035, 101.4206] |
| nodes.shape_515 | 1 | 17 | diagramMicro | [820.7096, 443.3784, 93.1057, 23.9441] |
| nodes.shape_516 | 1 | 17 | diagramMicro | [820.7096, 485.2278, 93.1057, 23.9441] |
| nodes.shape_517 | 1 | 17 | diagramMicro | [852.9685, 527.0772, 93.1057, 23.9441] |
| nodes.shape_518 | 1 | 17 | diagramMicro | [1027.341, 527.0772, 93.1057, 23.9441] |
| nodes.shape_525 | 1 | 13 | diagramMicro | [918.0645, 443.8098, 75.0903, 21.1266] |
| nodes.shape_531 | 1 | 13 | diagramMicro | [997.5508, 443.8098, 72.181, 21.1266] |
| nodes.shape_533 | 1 | 13 | diagramMicro | [1075.5871, 443.8098, 72.181, 21.1266] |
| nodes.shape_535 | 1 | 12 | diagramMicro | [922.4238, 485.6592, 66.3717, 21.1266] |
| nodes.shape_537 | 1 | 12 | diagramMicro | [1000.4601, 485.6592, 66.3717, 21.1266] |
| nodes.shape_539 | 1 | 12 | diagramMicro | [1078.4872, 485.6592, 66.3717, 21.1266] |
| nodes.shape_540 | 1 | 21 | compactBody | [361.5316, 604.1591, 197.5549, 30.9924] |
| nodes.shape_542 | 1 | 17 | diagramMicro | [554.7915, 609.3444, 93.1057, 23.9441] |
| nodes.shape_550 | 1 | 17 | diagramMicro | [672.7866, 609.3444, 93.1057, 23.2374] |
| nodes.shape_552 | 1 | 17 | diagramMicro | [790.7725, 609.3444, 93.1057, 23.9441] |
| nodes.shape_554 | 1 | 17 | diagramMicro | [908.7677, 609.3444, 93.1057, 23.9441] |
| nodes.shape_556 | 1 | 17 | diagramMicro | [1012.1431, 609.3444, 93.1057, 23.9441] |
| nodes.shape_560 | 1 | 20 | diagramCompact | [307.6505, 265.4175, 130.2746, 25.3574] |
| nodes.shape_561 | 1 | 20 | diagramCompact | [307.6505, 281.4231, 129.779, 25.3574] |
| nodes.shape_565 | 1 | 20 | diagramCompact | [307.6505, 324.4472, 127.3378, 25.3574] |
| nodes.shape_566 | 1 | 20 | diagramCompact | [307.6505, 340.4528, 129.779, 25.3574] |
| nodes.shape_568 | 1 | 20 | diagramCompact | [532.3158, 265.4175, 127.3378, 25.3574] |
| nodes.shape_569 | 1 | 20 | diagramCompact | [532.3158, 281.4231, 129.779, 25.3574] |
| nodes.shape_571 | 1 | 23 | diagramCompact | [532.3158, 324.4472, 150.098, 25.3574] |
| nodes.shape_572 | 1 | 20 | diagramCompact | [532.3158, 340.4528, 129.779, 25.3574] |
| nodes.shape_574 | 1 | 20 | diagramCompact | [756.981, 265.4175, 127.3378, 25.3574] |
| nodes.shape_575 | 1 | 20 | diagramCompact | [756.981, 281.4231, 129.779, 25.3574] |
| nodes.shape_577 | 1 | 20 | diagramCompact | [756.981, 324.4472, 127.3378, 25.3574] |
| nodes.shape_578 | 1 | 20 | diagramCompact | [756.981, 340.4528, 129.779, 25.3574] |
| nodes.shape_580 | 1 | 20 | diagramCompact | [981.6462, 265.4175, 127.3378, 25.3574] |
| nodes.shape_581 | 1 | 20 | diagramCompact | [981.6462, 281.4231, 129.779, 25.3574] |
| nodes.shape_583 | 1 | 23 | diagramCompact | [981.6462, 324.4472, 150.8322, 25.3574] |
| nodes.shape_584 | 1 | 20 | diagramCompact | [981.6462, 340.4528, 129.779, 25.3574] |
| nodes.shape_585 | 1 | 22 | diagramCompact | [280.3933, 194.9802, 74.7783, 42.2624] |
| nodes.shape_586 | 1 | 22 | diagramCompact | [370.443, 194.9802, 74.7783, 42.2624] |
| nodes.shape_587 | 1 | 22 | diagramCompact | [460.4835, 194.9802, 74.7783, 42.2624] |
| nodes.shape_588 | 1 | 22 | diagramCompact | [550.5331, 194.9802, 74.7783, 42.2624] |
| nodes.shape_589 | 1 | 22 | diagramCompact | [640.5827, 194.9802, 74.7783, 42.2624] |
| nodes.shape_590 | 1 | 22 | diagramCompact | [730.6232, 194.9802, 74.7783, 42.2624] |
| nodes.shape_591 | 1 | 22 | diagramCompact | [820.6728, 194.9802, 74.7783, 42.2624] |
| nodes.shape_592 | 1 | 22 | diagramCompact | [910.7225, 194.9802, 74.7783, 42.2624] |
| nodes.shape_593 | 1 | 22 | diagramCompact | [1000.763, 194.9802, 74.7783, 42.2624] |
| nodes.shape_594 | 1 | 22 | diagramCompact | [1090.8126, 194.9802, 74.7783, 42.2624] |
| nodes.shape_128 | 1 | 34 | compactBody | [477.9207, 138.1806, 307.1159, 32.6168] |
### page-30

左5源系统圆柱输入；中央业务/数据双中台；右服务能力竖栏和4用户应用；双向/右向箭头；立体面板与圆柱

Layout为`source-house-30`，原型为`templates/prototypes/source-house-30.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_528 | 1 | 12 | compactBody | [323.4879, 248.4005, 30.0325, 106.7707] |
| nodes.shape_529 | 1 | 20 | compactBody | [314.0939, 492.3144, 48.8111, 106.7707] |
| nodes.shape_531 | 1 | 12 | caption | [850.3078, 379.2275, 48.8111, 45.7616] |
| nodes.shape_713 | 1 | 12 | diagramCompact | [936.9027, 195.3126, 43.7223, 39.6626] |
| nodes.shape_717 | 1 | 12 | diagramCompact | [936.9027, 275.6196, 43.7223, 39.6626] |
| nodes.shape_720 | 1 | 12 | diagramCompact | [936.9027, 355.936, 43.7223, 39.6626] |
| nodes.shape_723 | 1 | 12 | diagramCompact | [936.9027, 436.2524, 43.7223, 39.6626] |
| nodes.shape_726 | 1 | 12 | diagramCompact | [936.9027, 516.5594, 43.7223, 39.6626] |
| nodes.shape_729 | 1 | 20 | diagramCompact | [924.1948, 596.8759, 69.1475, 39.6626] |
| nodes.shape_735 | 1 | 11 | diagramCompact | [1095.6378, 257.2564, 72.6785, 26.1899] |
| nodes.shape_741 | 1 | 11 | diagramCompact | [1095.6378, 372.3543, 72.6785, 26.1899] |
| nodes.shape_748 | 1 | 15 | diagramCompact | [1084.686, 487.4427, 94.5915, 26.1899] |
| nodes.shape_755 | 1 | 16 | diagramCompact | [1079.6444, 602.5406, 104.6559, 26.1899] |
| nodes.shape_541 | 1 | 10 | caption | [94.9255, 215.7623, 78.6831, 27.4551] |
| nodes.shape_785 | 1 | 18 | diagramMicro | [83.1901, 235.4944, 102.1445, 19.8266] |
| nodes.shape_806 | 1 | 11 | caption | [94.6045, 306.87, 79.3157, 27.4551] |
| nodes.shape_807 | 1 | 18 | diagramMicro | [83.1901, 326.6021, 102.1445, 19.8266] |
| nodes.shape_810 | 1 | 15 | caption | [79.3475, 397.9777, 109.8297, 27.4551] |
| nodes.shape_811 | 1 | 18 | diagramMicro | [83.1901, 417.7099, 102.1445, 19.8266] |
| nodes.shape_814 | 1 | 6 | caption | [109.144, 489.0855, 50.2367, 27.4551] |
| nodes.shape_815 | 1 | 18 | diagramMicro | [83.1901, 508.8176, 102.1445, 19.8266] |
| nodes.shape_818 | 1 | 7 | caption | [106.2078, 580.1932, 56.1186, 27.4551] |
| nodes.shape_819 | 1 | 18 | diagramMicro | [83.1901, 599.9254, 102.1445, 19.8266] |
| nodes.shape_853 | 1 | 7 | diagramCompact | [212.8935, 374.3086, 44.9968, 25.1703] |
| nodes.shape_882 | 1 | 7 | diagramCompact | [1024.8382, 366.7556, 44.9968, 25.1703] |
| nodes.shape_884 | 1 | 13 | caption | [293.531, 120, 94.5727, 27.4551] |
| nodes.shape_885 | 1 | 11 | caption | [1021.4488, 120, 79.3157, 27.4551] |
| nodes.shape_886 | 1 | 19 | diagramCompact | [113.6947, 122.4736, 124.2747, 24.4055] |
| nodes.shape_888 | 1 | 19 | diagramCompact | [376.3587, 122.4736, 124.2747, 24.4055] |
| nodes.shape_889 | 1 | 19 | diagramCompact | [1090.3413, 122.4736, 124.2747, 24.4055] |
| nodes.shape_578 | 1 | 11 | diagramMicro | [456.9112, 210.5224, 64.0681, 22.8761] |
| nodes.shape_654 | 1 | 8 | caption | [416.2951, 512.5941, 32.0907, 45.0252] |
| nodes.shape_657 | 1 | 14 | diagramCompact | [469.0148, 434.9023, 93.1093, 23.6691] |
| nodes.shape_19 | 1 | 10 | diagramCompact | [481.7227, 478.5585, 67.6841, 23.6691] |
| nodes.shape_27 | 1 | 10 | diagramCompact | [481.7227, 522.2242, 67.6841, 23.6691] |
| nodes.shape_36 | 1 | 10 | diagramCompact | [481.7227, 565.8803, 67.6841, 23.6691] |
| nodes.shape_43 | 1 | 10 | diagramCompact | [481.7227, 609.546, 67.6841, 23.6691] |
| nodes.shape_677 | 1 | 18 | diagramMicro | [614.4379, 461.385, 51.162, 35.8766] |
| nodes.shape_689 | 1 | 12 | diagramMicro | [683.1983, 436.8756, 69.2702, 21.0445] |
| nodes.shape_691 | 1 | 12 | diagramMicro | [683.1983, 465.5391, 69.2702, 21.0445] |
| nodes.shape_693 | 1 | 12 | diagramMicro | [683.1983, 494.2026, 69.2702, 21.0445] |
| nodes.shape_697 | 1 | 18 | diagramMicro | [614.4379, 571.6961, 51.162, 35.8766] |
| nodes.shape_702 | 1 | 10 | diagramMicro | [688.4382, 547.1867, 58.7905, 21.0445] |
| nodes.shape_704 | 1 | 11 | diagramMicro | [687.9661, 575.8503, 59.744, 21.0445] |
| nodes.shape_706 | 1 | 10 | diagramMicro | [688.4382, 604.5138, 58.7905, 21.0445] |
| nodes.shape_917 | 1 | 12 | diagramCompact | [857.4926, 287.6854, 23.1215, 73.2166] |
| nodes.shape_918 | 1 | 8 | diagramCompact | [860.2692, 435.9125, 15.68, 73.2166] |
| nodes.shape_954 | 1 | 11 | diagramMicro | [456.9112, 260.5608, 64.0681, 22.8761] |
| nodes.shape_450 | 1 | 11 | diagramMicro | [456.9112, 310.5993, 64.0681, 22.8761] |
| nodes.shape_457 | 1 | 11 | diagramMicro | [456.9112, 360.6377, 64.0681, 22.8761] |
| nodes.shape_464 | 1 | 16 | diagramMicro | [581.9601, 210.5224, 91.5515, 22.8761] |
| nodes.shape_471 | 1 | 11 | diagramMicro | [595.6971, 260.5608, 64.0681, 22.8761] |
| nodes.shape_478 | 1 | 11 | diagramMicro | [595.6971, 310.5993, 64.0681, 22.8761] |
| nodes.shape_485 | 1 | 11 | diagramMicro | [595.6971, 360.6377, 64.0681, 22.8761] |
| nodes.shape_492 | 1 | 11 | diagramMicro | [734.483, 210.5224, 64.0681, 22.8761] |
| nodes.shape_499 | 1 | 11 | diagramMicro | [734.483, 260.5608, 64.0681, 22.8761] |
| nodes.shape_506 | 1 | 11 | diagramMicro | [734.483, 310.5993, 64.0681, 22.8761] |
| nodes.shape_513 | 1 | 11 | diagramMicro | [734.483, 360.6377, 64.0681, 22.8761] |

## 使用步骤

1. 先确认材料确有本页型所表达的关系，选择`family=source-house`及兼容variant。
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

来源为房子图战略图.pptx，逐页结构见variants与来源索引。原始文件指纹及资产处理见asset-provenance.json。当前原型完成结构生成与文本测量，实际渲染和原生编辑范围以交付检查记录为准。

catalog指纹为`cb0b762dd09720f0095cb5d682a87348e0608e2f8d5fdf784ec1d4ef62f73010`，tokens指纹为`2bb967b3a61bf7a4072665f712f39ac49458d22ebe9407f269236c21adc366f3`，参数schema指纹为`add0f4b9d6bc61cd5cae5ce6d6821748442ed906b6b779cc561790e85b605ff5`。
