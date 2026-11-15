# 圆形逻辑图PPT模版.pptx

环绕扇区与循环关系

类型为定性关系图，语义入口为`source-circular`。

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

Layout为`source-circular-01`，原型为`templates/prototypes/source-circular-01.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_38 | 1 | 172 | heading | [363.2913, 299.3587, 553.4247, 163.504] |
### page-02

半圆同心3层；中心运营、内层人货场、中层6步触点与定向箭头、外层3价值；下沿有意裁圆

Layout为`source-circular-02`，原型为`templates/prototypes/source-circular-02.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_121 | 1 | 17 | body | [563.3741, 568.6105, 193.6961, 34.6042] |
| nodes.shape_123 | 1 | 34 | diagramCompact | [550.4336, 602.877, 219.5772, 23.9536] |
| nodes.shape_125 | 1 | 13 | body | [581.3805, 388.5304, 148.2683, 32.9485] |
| nodes.shape_127 | 1 | 13 | body | [400.1636, 533.5039, 148.2683, 32.9485] |
| nodes.shape_129 | 1 | 13 | body | [763.421, 534.3276, 148.2683, 32.9485] |
| nodes.shape_131 | 1 | 6 | body | [341.68, 545.0359, 74.1342, 31.3011] |
| nodes.shape_133 | 1 | 6 | body | [366.3914, 458.546, 74.1342, 31.3011] |
| nodes.shape_134 | 1 | 6 | body | [430.641, 374.5273, 74.1342, 31.3011] |
| nodes.shape_135 | 1 | 6 | body | [812.8438, 391.0016, 74.1342, 31.3011] |
| nodes.shape_136 | 1 | 6 | body | [872.9749, 468.4306, 74.1342, 31.3011] |
| nodes.shape_137 | 1 | 6 | body | [900.1574, 563.9813, 74.1342, 31.3011] |
| nodes.shape_138 | 1 | 22 | body | [534.4288, 314.3963, 247.1139, 32.9485] |
| nodes.shape_139 | 1 | 19 | body | [280.7253, 389.3541, 214.1654, 31.3011] |
| nodes.shape_140 | 1 | 25 | body | [805.4304, 389.3541, 271.8253, 31.3011] |
| nodes.shape_141 | 1 | 30 | compactBody | [869.68, 328.3994, 271.8253, 31.3011] |
| nodes.shape_142 | 1 | 30 | compactBody | [532.7814, 148.0062, 271.8253, 31.3011] |
| nodes.shape_144 | 1 | 38 | compactBody | [133.2806, 359.7005, 345.9594, 31.3011] |
### page-03

从底部中心向外3重环与4扇区，分对象/目标/传播工具；多处标签重叠、外圆延伸画布

Layout为`source-circular-03`，原型为`templates/prototypes/source-circular-03.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_4 | 1 | 10 | heading | [339.4693, 501.5951, 134.9333, 42.5333] |
| nodes.shape_31 | 1 | 10 | heading | [475.9951, 365.0693, 134.9333, 42.5333] |
| nodes.shape_32 | 1 | 10 | heading | [669.0716, 365.0693, 134.9333, 42.5333] |
| nodes.shape_33 | 1 | 10 | heading | [805.5973, 501.5951, 134.9333, 42.5333] |
| nodes.shape_34 | 1 | 15 | compactBody | [255.2904, 472.7716, 139.3333, 32.2667] |
| nodes.shape_35 | 1 | 15 | compactBody | [439.8383, 288.2237, 139.3333, 32.2667] |
| nodes.shape_37 | 1 | 15 | compactBody | [700.8284, 288.2237, 139.3333, 32.2667] |
| nodes.shape_36 | 1 | 15 | compactBody | [885.3763, 472.7716, 139.3333, 32.2667] |
| nodes.shape_39 | 1 | 18 | compactBody | [945.2359, 441.9018, 168.6667, 32.2667] |
| nodes.shape_40 | 1 | 18 | compactBody | [717.0315, 213.6975, 168.6667, 32.2667] |
| nodes.shape_41 | 1 | 18 | compactBody | [394.3018, 213.6975, 168.6667, 32.2667] |
| nodes.shape_42 | 1 | 18 | compactBody | [166.0975, 441.9018, 168.6667, 32.2667] |
| nodes.shape_7 | 1 | 36 | heading | [522.0727, 519.894, 235.8547, 82.9327] |
### page-04

底数据服务，管理会计两翼，4核心财务模块，中交换服务，顶半圆10业务触点

Layout为`source-circular-04`，原型为`templates/prototypes/source-circular-04.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_255 | 1 | 11 | caption | [594.9963, 599.7008, 84.1775, 29.315] |
| nodes.shape_257 | 1 | 39 | diagramCompact | [777.0279, 556.1042, 85.4517, 60.665] |
| nodes.shape_258 | 1 | 39 | diagramCompact | [868.4104, 556.1042, 85.4517, 60.665] |
| nodes.shape_259 | 1 | 12 | caption | [961.5621, 560.0275, 44.99, 52.8275] |
| nodes.shape_260 | 1 | 12 | caption | [263.8779, 560.0275, 44.99, 52.8275] |
| nodes.shape_261 | 1 | 26 | diagramCompact | [320.0971, 565.2525, 85.4517, 42.3775] |
| nodes.shape_262 | 1 | 39 | diagramCompact | [411.4796, 556.1042, 85.4517, 60.665] |
| nodes.shape_263 | 1 | 11 | caption | [327.8154, 391.3333, 84.1775, 29.315] |
| nodes.shape_264 | 1 | 92 | diagramMicro | [309.5829, 434.7558, 128.4433, 68.5025] |
| nodes.shape_265 | 1 | 11 | caption | [501.1296, 391.3333, 84.1775, 29.315] |
| nodes.shape_266 | 1 | 92 | diagramMicro | [482.8879, 434.7558, 128.4433, 68.5025] |
| nodes.shape_267 | 1 | 11 | caption | [678.0004, 391.3333, 84.1775, 29.315] |
| nodes.shape_268 | 1 | 92 | diagramMicro | [659.7588, 434.7558, 128.4433, 68.5025] |
| nodes.shape_269 | 1 | 11 | caption | [854.8713, 391.3333, 84.1775, 29.315] |
| nodes.shape_270 | 1 | 92 | diagramMicro | [836.6388, 434.7558, 128.4433, 68.5025] |
| nodes.shape_271 | 1 | 17 | caption | [575.3979, 244.3733, 123.365, 29.315] |
| nodes.shape_274 | 1 | 10 | diagramCompact | [509.8012, 284.5417, 66.7608, 24.09] |
| nodes.shape_275 | 1 | 13 | diagramCompact | [682.6846, 284.5417, 82.005, 24.09] |
| nodes.shape_276 | 1 | 30 | diagramMicro | [498.2421, 315.8642, 84.1775, 37.1525] |
| nodes.shape_277 | 1 | 36 | diagramMicro | [586.6821, 315.8642, 97.24, 37.1525] |
| nodes.shape_278 | 1 | 30 | diagramMicro | [688.1113, 315.8642, 84.1775, 37.1525] |
| nodes.shape_290 | 1 | 10 | diagramCompact | [74.9896, 550.0083, 66.7608, 24.09] |
| nodes.shape_291 | 1 | 10 | diagramCompact | [1136.2512, 550.0083, 68.7592, 24.09] |
| nodes.shape_292 | 1 | 10 | diagramCompact | [1102.1971, 445.2333, 66.7608, 24.09] |
| nodes.shape_293 | 1 | 5 | diagramCompact | [1043.7046, 345.5275, 36.2817, 24.09] |
| nodes.shape_294 | 1 | 11 | diagramCompact | [946.8587, 252.0183, 74.3783, 24.09] |
| nodes.shape_295 | 1 | 8 | diagramCompact | [827.0871, 189.5017, 51.5258, 24.09] |
| nodes.shape_296 | 1 | 11 | diagramCompact | [598.0213, 120, 74.3783, 24.09] |
| nodes.shape_297 | 1 | 5 | diagramCompact | [408.3538, 189.5017, 36.2817, 24.09] |
| nodes.shape_298 | 1 | 5 | diagramCompact | [288.5821, 252.0183, 36.2817, 24.09] |
| nodes.shape_299 | 1 | 11 | diagramCompact | [162.3846, 344.7392, 74.3783, 24.09] |
| nodes.shape_300 | 1 | 5 | diagramCompact | [133.9588, 443.5742, 36.2817, 24.09] |
### page-05

底中心云图组织；内半圆5定向能力；外半圆10行业；同心分层

Layout为`source-circular-05`，原型为`templates/prototypes/source-circular-05.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_96 | 1 | 65 | diagramCompact | [736.7927, 401.4533, 84.8833, 84.8833] |
| nodes.shape_105 | 1 | 65 | diagramCompact | [816.2273, 510.9987, 84.8833, 84.8833] |
| nodes.shape_109 | 1 | 65 | diagramCompact | [597.562, 354.696, 84.8833, 84.8833] |
| nodes.shape_113 | 1 | 65 | diagramCompact | [458.324, 401.4533, 84.8833, 84.8833] |
| nodes.shape_117 | 1 | 65 | diagramCompact | [378.8893, 510.9987, 84.8833, 84.8833] |
| nodes.shape_4 | 1 | 13 | heading | [552.9827, 566.952, 174.0347, 40.282] |
| nodes.shape_14 | 1 | 14 | diagramCompact | [235.508, 533.2993, 49.9473, 40.282] |
| nodes.shape_47 | 1 | 16 | diagramCompact | [990.9147, 533.2993, 51.304, 40.282] |
| nodes.shape_48 | 1 | 14 | diagramCompact | [279.6327, 420.2707, 44.506, 40.282] |
| nodes.shape_49 | 1 | 24 | diagramCompact | [934.536, 420.2707, 79.9407, 40.282] |
| nodes.shape_50 | 1 | 18 | diagramCompact | [337.9327, 331.926, 61.16, 40.282] |
| nodes.shape_51 | 1 | 14 | diagramCompact | [888.82, 331.926, 45.3347, 40.282] |
| nodes.shape_52 | 1 | 16 | diagramCompact | [792.6067, 270.6193, 52.6973, 40.282] |
| nodes.shape_53 | 1 | 16 | diagramCompact | [434.3293, 270.6193, 53.438, 40.282] |
| nodes.shape_54 | 1 | 14 | diagramCompact | [551.8093, 228.4747, 45.7527, 40.282] |
| nodes.shape_55 | 1 | 16 | diagramCompact | [679.402, 228.4747, 51.832, 40.282] |
### page-06

中心品牌；左右物理/数字触点两圈及列表；内体验闭环，外品牌印迹弧；对角分区

Layout为`source-circular-06`，原型为`templates/prototypes/source-circular-06.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_65 | 1 | 40 | diagramMicro | [217.006, 322.1653, 28.4387, 123.904] |
| nodes.shape_66 | 1 | 14 | diagramMicro | [287.362, 351.4253, 77.066, 18.9567] |
| nodes.shape_67 | 1 | 40 | diagramMicro | [1034.5553, 322.774, 28.4387, 123.904] |
| nodes.shape_68 | 1 | 14 | diagramMicro | [287.362, 375.6473, 77.066, 18.9567] |
| nodes.shape_69 | 1 | 14 | diagramMicro | [287.362, 399.8693, 77.066, 18.9567] |
| nodes.shape_70 | 1 | 14 | diagramMicro | [377.4887, 336.7293, 80.4907, 18.9567] |
| nodes.shape_71 | 1 | 14 | diagramMicro | [377.4887, 360.57, 80.4907, 18.9567] |
| nodes.shape_72 | 1 | 14 | diagramMicro | [377.4887, 384.4107, 80.4907, 18.9567] |
| nodes.shape_73 | 1 | 14 | diagramMicro | [377.4887, 408.2513, 80.4907, 18.9567] |
| nodes.shape_74 | 1 | 18 | diagramMicro | [825.02, 330.9727, 99.0587, 18.9567] |
| nodes.shape_75 | 1 | 18 | diagramMicro | [825.02, 353.7133, 99.0587, 18.9567] |
| nodes.shape_76 | 1 | 18 | diagramMicro | [825.02, 376.4613, 99.0587, 18.9567] |
| nodes.shape_77 | 1 | 18 | diagramMicro | [825.02, 399.202, 99.0587, 18.9567] |
| nodes.shape_78 | 1 | 18 | diagramMicro | [825.02, 421.9427, 99.0587, 18.9567] |
| nodes.shape_79 | 1 | 13 | diagramMicro | [927.8773, 338.7827, 71.368, 18.9567] |
| nodes.shape_80 | 1 | 13 | diagramMicro | [927.8773, 361.5307, 71.368, 18.9567] |
| nodes.shape_81 | 1 | 13 | diagramMicro | [927.8773, 384.2713, 71.368, 18.9567] |
| nodes.shape_82 | 1 | 13 | diagramMicro | [927.8773, 407.012, 71.368, 18.9567] |
| nodes.shape_84 | 1 | 13 | diagramCompact | [470.754, 379.336, 83.666, 23.694] |
| nodes.shape_85 | 1 | 15 | diagramMicro | [470.754, 367.6907, 83.666, 15.4] |
| nodes.shape_86 | 1 | 13 | diagramCompact | [734.4167, 379.336, 83.666, 23.694] |
| nodes.shape_87 | 1 | 15 | diagramMicro | [734.4167, 367.6907, 83.666, 15.4] |
| nodes.shape_88 | 1 | 13 | diagramCompact | [598.596, 363.804, 83.666, 23.694] |
| nodes.shape_89 | 1 | 15 | diagramMicro | [598.596, 382.966, 83.666, 15.4] |
| nodes.shape_90 | 1 | 13 | diagramCompact | [598.596, 218.12, 83.666, 23.694] |
| nodes.shape_91 | 1 | 20 | diagramMicro | [517.9293, 189.9967, 27.2507, 61.842] |
| nodes.shape_92 | 1 | 20 | diagramMicro | [734.358, 192.7687, 27.2507, 61.842] |
| nodes.shape_93 | 1 | 20 | diagramMicro | [490.6713, 499.4193, 27.2507, 61.842] |
| nodes.shape_94 | 1 | 20 | diagramMicro | [550.988, 533.754, 27.2507, 61.842] |
| nodes.shape_95 | 1 | 20 | diagramMicro | [626.8073, 551.9407, 27.2507, 61.842] |
| nodes.shape_96 | 1 | 20 | diagramMicro | [709.278, 535.0447, 27.2507, 61.842] |
| nodes.shape_97 | 1 | 20 | diagramMicro | [765.4953, 501.6487, 27.2507, 61.842] |
### page-07

中心球体、内外3环轨道、10个功能图标球与大小节点

Layout为`source-circular-07`，原型为`templates/prototypes/source-circular-07.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_59 | 1 | 15 | heading | [549.8843, 374.486, 193.5193, 35.0] |
| nodes.shape_60 | 1 | 18 | diagramCompact | [588.883, 351.6367, 115.5147, 17.5] |
| nodes.shape_61 | 1 | 16 | diagramMicro | [708.7537, 274.6657, 88.0, 15.0] |
| nodes.shape_62 | 1 | 16 | diagramMicro | [839.551, 367.1683, 88.0, 15.0] |
| nodes.shape_63 | 1 | 16 | diagramMicro | [937.979, 278.7063, 88.0, 15.0] |
| nodes.shape_64 | 1 | 16 | diagramMicro | [975.379, 489.6643, 88.0, 15.0] |
| nodes.shape_65 | 1 | 16 | diagramMicro | [915.979, 606.279, 88.0, 15.0] |
| nodes.shape_66 | 1 | 16 | diagramMicro | [784.7563, 573.2277, 88.0, 15.0] |
| nodes.shape_67 | 1 | 16 | diagramMicro | [425.7897, 554.447, 88.0, 15.0] |
| nodes.shape_68 | 1 | 16 | diagramMicro | [291.179, 619.479, 88.0, 15.0] |
| nodes.shape_69 | 1 | 16 | diagramMicro | [229.3883, 525.5903, 88.0, 15.0] |
| nodes.shape_70 | 1 | 16 | diagramMicro | [318.3637, 444.887, 88.0, 15.0] |
| nodes.shape_71 | 1 | 16 | diagramMicro | [248.3963, 333.6623, 88.0, 15.0] |
### page-08

扇形同心层，从职业角色→岗位领域→趋势→5推荐功能；两侧径向上箭头

Layout为`source-circular-08`，原型为`templates/prototypes/source-circular-08.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_84 | 1 | 2340 | compactBody | [53.7776, 174.2324, 1174.1486, 473.7676] |
| nodes.shape_159 | 1 | 12 | diagramCompact | [453.7226, 610.2839, 76.5453, 24.8986] |
| nodes.shape_160 | 1 | 12 | diagramCompact | [488.3821, 556.8648, 76.5453, 24.8986] |
| nodes.shape_161 | 1 | 12 | diagramCompact | [547.786, 512.4531, 76.5453, 24.8986] |
| nodes.shape_162 | 1 | 12 | diagramCompact | [655.1978, 512.085, 76.5453, 24.8986] |
| nodes.shape_163 | 1 | 12 | diagramCompact | [722.8299, 555.4178, 76.5453, 24.8986] |
| nodes.shape_164 | 1 | 12 | diagramCompact | [755.6742, 606.4737, 76.5453, 24.8986] |
| nodes.shape_165 | 1 | 12 | diagramCompact | [603.6024, 461.5514, 76.5453, 24.8986] |
| nodes.shape_166 | 1 | 12 | diagramCompact | [602.4466, 581.3268, 76.5453, 24.8986] |
| nodes.shape_167 | 1 | 12 | diagramCompact | [599.5526, 329.1554, 76.5453, 24.8986] |
| nodes.shape_168 | 1 | 6 | compactBody | [459.699, 436.7127, 55.7907, 30.4298] |
| nodes.shape_169 | 1 | 6 | compactBody | [520.7725, 395.0408, 55.7907, 30.4298] |
| nodes.shape_170 | 1 | 6 | compactBody | [608.1061, 379.629, 55.7907, 30.4298] |
| nodes.shape_171 | 1 | 6 | compactBody | [693.7273, 395.0408, 55.7907, 30.4298] |
| nodes.shape_172 | 1 | 6 | compactBody | [757.6606, 436.7127, 55.7907, 30.4298] |
| nodes.shape_173 | 1 | 12 | diagramMicro | [357.4673, 339.31, 67.3239, 22.1331] |
| nodes.shape_174 | 1 | 12 | diagramMicro | [476.1211, 279.8804, 67.3239, 22.1331] |
| nodes.shape_175 | 1 | 12 | diagramMicro | [604.3388, 253.569, 67.3239, 22.1331] |
| nodes.shape_176 | 1 | 12 | diagramMicro | [729.5169, 279.5465, 67.3239, 22.1331] |
| nodes.shape_177 | 1 | 12 | diagramMicro | [847.9395, 338.7364, 67.3239, 22.1331] |
| nodes.shape_178 | 1 | 14 | compactBody | [572.9073, 137.9034, 134.1855, 30.4298] |
### page-09

中心主题，3同心圆环上散布6重点词与约20联想词，无箭头

Layout为`source-circular-09`，原型为`templates/prototypes/source-circular-09.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_14 | 1 | 63 | diagramMicro | [339.8906, 199.6033, 340.4867, 20.1447] |
| nodes.shape_15 | 1 | 19 | caption | [575.1806, 408.112, 137.3827, 28.4387] |
| nodes.shape_16 | 1 | 25 | diagramMicro | [575.1806, 433.1553, 137.3827, 20.1447] |
| nodes.shape_22 | 1 | 9 | diagramCompact | [482.4433, 329.506, 58.234, 23.694] |
| nodes.shape_23 | 1 | 9 | diagramCompact | [444.86, 464.564, 58.234, 23.694] |
| nodes.shape_24 | 1 | 9 | diagramCompact | [553.914, 514.5993, 58.234, 23.694] |
| nodes.shape_25 | 1 | 9 | diagramCompact | [767.182, 380.7, 58.234, 23.694] |
| nodes.shape_26 | 1 | 9 | diagramCompact | [620.6693, 276.904, 58.234, 23.694] |
| nodes.shape_27 | 1 | 9 | diagramCompact | [747.162, 501.9567, 58.234, 23.694] |
| nodes.shape_28 | 1 | 10 | diagramMicro | [794.9313, 435.9567, 58.234, 21.3253] |
| nodes.shape_29 | 1 | 10 | diagramMicro | [767.182, 340.1687, 58.234, 21.3253] |
| nodes.shape_30 | 1 | 10 | diagramMicro | [694.9633, 325.8247, 58.234, 21.3253] |
| nodes.shape_31 | 1 | 10 | diagramMicro | [703.91, 274.3447, 58.234, 21.3253] |
| nodes.shape_32 | 1 | 10 | diagramMicro | [540.6773, 304.4407, 58.234, 21.3253] |
| nodes.shape_33 | 1 | 10 | diagramMicro | [415.732, 352.7527, 58.234, 21.3253] |
| nodes.shape_34 | 1 | 10 | diagramMicro | [390.982, 401.006, 58.234, 21.3253] |
| nodes.shape_35 | 1 | 10 | diagramMicro | [404.6513, 436.624, 58.234, 21.3253] |
| nodes.shape_36 | 1 | 10 | diagramMicro | [467.674, 507.1047, 58.234, 21.3253] |
| nodes.shape_37 | 1 | 10 | diagramMicro | [688.7446, 570.1273, 58.234, 21.3253] |
| nodes.shape_38 | 1 | 10 | diagramMicro | [776.752, 285.8287, 58.234, 21.3253] |
| nodes.shape_40 | 1 | 10 | diagramMicro | [827.3373, 322.686, 58.234, 21.3253] |
| nodes.shape_41 | 1 | 10 | diagramMicro | [871.8213, 435.392, 58.234, 21.3253] |
| nodes.shape_42 | 1 | 10 | diagramMicro | [818.112, 544.9593, 58.234, 21.3253] |
| nodes.shape_43 | 1 | 10 | diagramMicro | [540.6773, 562.8673, 58.234, 21.3253] |
| nodes.shape_44 | 1 | 10 | diagramMicro | [444.86, 548.3767, 58.234, 21.3253] |
| nodes.shape_45 | 1 | 10 | diagramMicro | [556.95, 266.2413, 58.234, 21.3253] |
| nodes.shape_46 | 1 | 10 | diagramMicro | [479.2166, 283.6433, 58.234, 21.3253] |
### page-10

中心系统；4扇区商品/库存/物流/设备；每区4外围小条；外围圈

Layout为`source-circular-10`，原型为`templates/prototypes/source-circular-10.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_233 | 1 | 9 | diagramMicro | [784.3045, 583.3053, 53.7387, 19.1913] |
| nodes.shape_237 | 1 | 9 | diagramMicro | [864.8099, 534.2893, 53.8633, 19.1913] |
| nodes.shape_240 | 1 | 9 | diagramMicro | [917.8152, 426.7387, 53.8633, 19.1913] |
| nodes.shape_247 | 1 | 9 | diagramMicro | [900.0832, 480.3673, 53.8633, 19.1913] |
| nodes.shape_287 | 1 | 11 | diagramCompact | [666.1572, 461.616, 70.642, 24.266] |
| nodes.shape_54 | 1 | 9 | diagramMicro | [793.5005, 202.9547, 53.7387, 19.1913] |
| nodes.shape_57 | 1 | 9 | diagramMicro | [863.2625, 250.0127, 53.8633, 19.1913] |
| nodes.shape_270 | 1 | 9 | diagramMicro | [918.2185, 359.514, 53.8633, 19.1913] |
| nodes.shape_279 | 1 | 9 | diagramMicro | [900.4865, 305.8927, 53.8633, 19.1913] |
| nodes.shape_10 | 1 | 13 | diagramMicro | [427.0465, 200.564, 73.1133, 19.1913] |
| nodes.shape_16 | 1 | 9 | diagramMicro | [356.6832, 248.3847, 53.8633, 19.1913] |
| nodes.shape_20 | 1 | 9 | diagramMicro | [299.4025, 360.8487, 53.8633, 19.1913] |
| nodes.shape_24 | 1 | 9 | diagramMicro | [319.3052, 304.6167, 53.8633, 19.1913] |
| nodes.shape_29 | 1 | 11 | diagramCompact | [539.3492, 314.5607, 70.642, 24.266] |
| nodes.shape_31 | 1 | 14 | caption | [588.3212, 383.1347, 103.0773, 29.744] |
| nodes.shape_286 | 1 | 11 | diagramCompact | [676.5119, 315.0887, 70.642, 24.266] |
| nodes.shape_297 | 1 | 37 | diagramMicro | [539.3272, 407.298, 201.0727, 20.1447] |
| nodes.shape_39 | 1 | 9 | diagramMicro | [436.9832, 585.696, 53.8633, 19.1913] |
| nodes.shape_42 | 1 | 9 | diagramMicro | [356.9985, 537.868, 53.8633, 19.1913] |
| nodes.shape_45 | 1 | 9 | diagramMicro | [299.7179, 425.4113, 53.8633, 19.1913] |
| nodes.shape_50 | 1 | 9 | diagramMicro | [319.6279, 481.6433, 53.8633, 19.1913] |
| nodes.shape_53 | 1 | 11 | diagramCompact | [539.6719, 466.6247, 70.642, 24.266] |
### page-11

两个并列环形箭头，内部/外部驱动；中双向横箭头；左右各3收益

Layout为`source-circular-11`，原型为`templates/prototypes/source-circular-11.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_7 | 1 | 16 | caption | [593.0598, 399.1926, 121.946, 29.7409] |
| nodes.shape_8 | 1 | 16 | caption | [593.0598, 473.8072, 121.946, 29.7409] |
| nodes.shape_11 | 1 | 12 | heading | [397.3737, 414.7488, 77.33, 80.3032] |
| nodes.shape_20 | 1 | 15 | compactBody | [113.5694, 348.4554, 136.821, 32.7141] |
| nodes.shape_25 | 1 | 15 | compactBody | [92.9874, 437.9727, 136.821, 32.7141] |
| nodes.shape_30 | 1 | 15 | compactBody | [113.5694, 528.613, 136.821, 32.7141] |
| nodes.shape_34 | 1 | 15 | compactBody | [1060.05, 349.5876, 136.821, 32.7141] |
| nodes.shape_35 | 1 | 15 | compactBody | [1078.2572, 437.9727, 136.821, 32.7141] |
| nodes.shape_36 | 1 | 15 | compactBody | [1057.6751, 529.7544, 136.821, 32.7141] |
| nodes.shape_55 | 1 | 12 | heading | [833.3619, 414.7488, 77.33, 80.3032] |
### page-12

中心危机球；外围8球沿椭圆按箭头循环；大背景环

Layout为`source-circular-12`，原型为`templates/prototypes/source-circular-12.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_42 | 1 | 10 | heading | [360.6923, 537.197, 138.5746, 44.3207] |
| nodes.shape_33 | 1 | 10 | body | [1070.5511, 256.735, 111.5982, 37.4948] |
| nodes.shape_36 | 1 | 10 | heading | [1090.2269, 456.3099, 126.843, 40.913] |
| nodes.shape_39 | 1 | 11 | heading | [774.3801, 535.4984, 142.0034, 44.3207] |
| nodes.shape_45 | 1 | 10 | heading | [55.5433, 456.3099, 132.3396, 40.913] |
| nodes.shape_53 | 1 | 11 | body | [309.3454, 161.8902, 129.1535, 37.4948] |
| nodes.shape_61 | 1 | 15 | metric | [459.5989, 335.5121, 353.1517, 84.4002] |
| nodes.shape_50 | 1 | 10 | body | [847.534, 161.8902, 111.5982, 37.4948] |
| nodes.shape_30 | 1 | 11 | body | [84.4398, 256.735, 129.1535, 37.4948] |
### page-13

左中心主题+6外围功能圈，右触达/激活/沉淀3说明行

Layout为`source-circular-13`，原型为`templates/prototypes/source-circular-13.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_8 | 1 | 48 | body | [122.6404, 223.4806, 139.8994, 139.8994] |
| nodes.shape_17 | 1 | 16 | heading | [296.1402, 347.6508, 106.6315, 72.6984] |
| nodes.shape_18 | 1 | 6 | body | [313.0628, 183.9034, 72.7766, 37.9338] |
| nodes.shape_19 | 1 | 12 | body | [469.9336, 260.2406, 72.7766, 66.3793] |
| nodes.shape_20 | 1 | 6 | body | [469.9336, 455.6028, 72.7766, 37.9338] |
| nodes.shape_21 | 1 | 6 | body | [156.2017, 455.6028, 72.7766, 37.9338] |
| nodes.shape_22 | 1 | 12 | body | [156.2017, 260.2406, 72.7766, 66.3793] |
| nodes.shape_23 | 1 | 9 | body | [296.1402, 546.1725, 106.6315, 37.9338] |
| nodes.shape_34 | 1 | 11 | heading | [676.9068, 139.4549, 142.4916, 44.6833] |
| nodes.shape_37 | 1 | 108 | compactBody | [676.9068, 197.1577, 491.7411, 60.7352] |
| nodes.shape_40 | 1 | 11 | heading | [676.9068, 324.7809, 142.4916, 44.6833] |
| nodes.shape_41 | 1 | 108 | compactBody | [676.9068, 382.4838, 491.7411, 60.7352] |
| nodes.shape_43 | 1 | 11 | heading | [676.9068, 510.107, 142.4916, 44.6833] |
| nodes.shape_44 | 1 | 108 | compactBody | [676.9068, 567.8099, 491.7411, 60.7352] |
| nodes.shape_45 | 1 | 20 | compactBody | [833.1418, 139.4549, 180.083, 44.6833] |
| nodes.shape_46 | 1 | 22 | compactBody | [833.1418, 324.7809, 199.7934, 44.6833] |
| nodes.shape_47 | 1 | 28 | compactBody | [833.1418, 510.107, 252.8499, 44.6833] |
### page-14

中心平台，左3营销节点，右3目标人群，左右容器，虚线多对一/一对多连接

Layout为`source-circular-14`，原型为`templates/prototypes/source-circular-14.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_7 | 1 | 75 | heading | [544.2232, 286.7749, 194.4401, 194.4401] |
| nodes.shape_8 | 1 | 48 | body | [939.4779, 491.2277, 137.1605, 137.1605] |
| nodes.shape_11 | 1 | 48 | body | [1008.0631, 313.8462, 137.1605, 137.1605] |
| nodes.shape_12 | 1 | 48 | body | [926.9094, 136.4747, 137.1605, 137.1605] |
| nodes.shape_23 | 1 | 114 | caption | [205.5867, 136.4747, 137.1605, 137.1605] |
| nodes.shape_24 | 1 | 114 | caption | [137.0115, 313.8462, 137.1605, 137.1605] |
| nodes.shape_25 | 1 | 114 | caption | [218.1551, 491.2277, 137.1605, 137.1605] |
| nodes.shape_30 | 1 | 16 | body | [1182.2674, 307.7023, 49.7326, 152.5854] |
| nodes.shape_35 | 1 | 16 | body | [48, 307.7023, 49.7326, 152.5854] |
### page-15

中心积分平台，内圈9应用图标，外圈6管理价值说明点

Layout为`source-circular-15`，原型为`templates/prototypes/source-circular-15.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_66 | 1 | 60 | caption | [220.4821, 206.0031, 217.8312, 54.2684] |
| nodes.shape_67 | 1 | 44 | caption | [202.8613, 375.1974, 165.4686, 54.2684] |
| nodes.shape_68 | 1 | 52 | caption | [228.6364, 543.3998, 192.0561, 54.2684] |
| nodes.shape_69 | 1 | 50 | caption | [854.0978, 543.3998, 180.4339, 54.2684] |
| nodes.shape_70 | 1 | 96 | caption | [902.0083, 380.2978, 178.5124, 82.6601] |
| nodes.shape_71 | 1 | 44 | caption | [835.36, 206.0031, 164.9688, 54.2684] |
| nodes.shape_72 | 1 | 9 | caption | [603.743, 542.3078, 67.3044, 20.0] |
| nodes.shape_73 | 1 | 9 | caption | [601.6419, 437.542, 71.5065, 20.1905] |
| nodes.shape_74 | 1 | 9 | diagramMicro | [709.0071, 521.1937, 50.4724, 15.0] |
| nodes.shape_75 | 1 | 7 | diagramMicro | [515.1467, 521.1937, 40.3811, 15.0] |
| nodes.shape_76 | 1 | 7 | diagramMicro | [474.6329, 450.5542, 40.3811, 15.0] |
| nodes.shape_77 | 1 | 7 | diagramMicro | [756.2303, 450.5542, 40.3811, 15.0] |
| nodes.shape_78 | 1 | 7 | diagramMicro | [756.3475, 369.4797, 40.3811, 15.0] |
| nodes.shape_79 | 1 | 7 | diagramMicro | [474.6329, 369.4797, 40.3811, 15.0] |
| nodes.shape_80 | 1 | 5 | diagramMicro | [526.191, 303.4406, 30.2897, 15.0] |
| nodes.shape_81 | 1 | 7 | diagramMicro | [707.8121, 303.4406, 40.3811, 15.0] |
| nodes.shape_82 | 1 | 7 | diagramMicro | [617.4819, 273.1509, 40.3811, 15.0] |
### page-16

中心一致性；3大卫星圈各带2小触点；外一环；形成3簇嵌套关系

Layout为`source-circular-16`，原型为`templates/prototypes/source-circular-16.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_27 | 1 | 67 | diagramCompact | [286.7268, 120, 422.7606, 25.0123] |
| nodes.shape_28 | 1 | 57 | caption | [590.6992, 334.9223, 137.9094, 60.6597] |
| nodes.shape_29 | 1 | 23 | caption | [742.394, 276.3386, 170.5793, 29.4193] |
| nodes.shape_30 | 1 | 31 | diagramMicro | [742.394, 306.7959, 170.5793, 22.0622] |
| nodes.shape_31 | 1 | 31 | diagramMicro | [742.394, 244.8432, 170.5793, 22.0622] |
| nodes.shape_32 | 1 | 23 | caption | [403.9943, 276.3386, 170.5793, 29.4193] |
| nodes.shape_33 | 1 | 31 | diagramMicro | [403.9943, 306.7959, 170.5793, 22.0622] |
| nodes.shape_34 | 1 | 62 | diagramMicro | [403.9943, 237.4497, 170.5793, 35.3105] |
| nodes.shape_35 | 1 | 23 | caption | [571.1956, 529.8492, 170.5793, 29.4193] |
| nodes.shape_36 | 1 | 31 | diagramMicro | [571.1956, 570.6866, 170.5793, 22.0622] |
| nodes.shape_46 | 1 | 31 | diagramMicro | [571.1956, 503.726, 170.5793, 22.0622] |
| nodes.shape_47 | 1 | 17 | diagramMicro | [853.561, 354.4077, 97.0264, 22.0622] |
| nodes.shape_48 | 1 | 46 | diagramMicro | [838.6647, 374.5214, 126.8373, 34.7459] |
| nodes.shape_49 | 1 | 17 | diagramMicro | [896.2468, 246.1726, 97.0264, 22.0622] |
| nodes.shape_50 | 1 | 34 | diagramMicro | [896.2468, 266.2863, 97.0264, 34.7459] |
| nodes.shape_51 | 1 | 17 | diagramMicro | [827.7747, 150.1751, 97.0264, 22.0622] |
| nodes.shape_53 | 1 | 34 | diagramMicro | [827.7747, 170.2888, 97.0264, 34.7459] |
| nodes.shape_54 | 1 | 17 | diagramMicro | [343.8809, 196.7397, 97.0264, 22.0622] |
| nodes.shape_62 | 1 | 68 | diagramMicro | [343.8809, 216.8534, 97.0264, 61.5247] |
| nodes.shape_63 | 1 | 17 | diagramMicro | [342.761, 312.2409, 97.0264, 22.0622] |
| nodes.shape_64 | 1 | 51 | diagramMicro | [342.761, 332.3546, 97.0264, 48.1308] |
| nodes.shape_65 | 1 | 17 | diagramMicro | [496.3133, 566.6257, 97.0264, 22.0622] |
| nodes.shape_66 | 1 | 34 | diagramMicro | [496.3133, 586.7393, 97.0264, 34.7459] |
| nodes.shape_67 | 1 | 17 | diagramMicro | [721.4882, 566.6257, 97.0264, 22.0622] |
| nodes.shape_68 | 1 | 42 | diagramMicro | [712.2372, 586.7393, 115.5467, 34.7459] |
| nodes.shape_69 | 1 | 34 | diagramMicro | [609.2923, 185.6768, 97.0264, 42.1486] |
| nodes.shape_70 | 1 | 34 | diagramMicro | [484.7281, 450.2218, 97.0264, 42.1486] |
| nodes.shape_71 | 1 | 34 | diagramMicro | [726.3563, 446.7917, 97.0264, 42.1486] |
### page-17

中心系统圆；6扇区功能，3段外方向箭头；左右各4扩展服务

Layout为`source-circular-17`，原型为`templates/prototypes/source-circular-17.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_44 | 1 | 13 | caption | [294.8933, 263.9387, 95.2307, 28.4387] |
| nodes.shape_45 | 1 | 13 | caption | [261.16, 359.7633, 95.2307, 28.4387] |
| nodes.shape_46 | 1 | 13 | caption | [261.16, 456.5633, 95.2307, 28.4387] |
| nodes.shape_47 | 1 | 13 | caption | [295.3847, 552.3807, 95.2307, 28.4387] |
| nodes.shape_48 | 1 | 13 | caption | [889.876, 263.9387, 95.2307, 28.4387] |
| nodes.shape_49 | 1 | 13 | caption | [924.5847, 359.7633, 95.2307, 28.4387] |
| nodes.shape_50 | 1 | 13 | caption | [924.5847, 456.5633, 95.2307, 28.4387] |
| nodes.shape_51 | 1 | 13 | caption | [889.876, 552.7253, 95.2307, 28.4387] |
| nodes.shape_52 | 1 | 30 | diagramCompact | [467.5567, 470.8193, 95.2307, 45.9507] |
| nodes.shape_53 | 1 | 30 | diagramCompact | [466.684, 330.0413, 95.2307, 45.9507] |
| nodes.shape_54 | 1 | 30 | diagramCompact | [591.094, 256.6493, 95.2307, 45.9507] |
| nodes.shape_55 | 1 | 30 | diagramCompact | [715.5847, 328.0247, 95.2307, 45.9507] |
| nodes.shape_56 | 1 | 30 | diagramCompact | [716.6407, 470.0493, 95.2307, 45.9507] |
| nodes.shape_57 | 1 | 30 | diagramCompact | [593.4407, 538.2347, 95.2307, 45.9507] |
### page-18

中心六边形；背景蜂窝；周围10行业球体，部分不同大小，无连线

Layout为`source-circular-18`，原型为`templates/prototypes/source-circular-18.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_47 | 1 | 34 | heading | [529.5465, 431.8011, 225.6151, 91.3803] |
| nodes.shape_49 | 1 | 7 | body | [204.9709, 251.2309, 82.9094, 35.247] |
| nodes.shape_50 | 1 | 7 | body | [123.0794, 402.5437, 82.9094, 61.6776] |
| nodes.shape_51 | 1 | 7 | body | [320.4188, 427.8837, 82.9094, 61.6776] |
| nodes.shape_52 | 1 | 7 | body | [406.1821, 307.1188, 82.9094, 35.247] |
| nodes.shape_53 | 1 | 10 | body | [574.2005, 225.5818, 116.0205, 61.6776] |
| nodes.shape_54 | 1 | 7 | body | [798.6795, 245.9593, 82.9094, 35.247] |
| nodes.shape_55 | 1 | 9 | body | [1030.1751, 280.8699, 104.8865, 35.247] |
| nodes.shape_56 | 1 | 7 | body | [1075.3654, 482.8356, 82.9094, 35.247] |
| nodes.shape_57 | 1 | 7 | body | [862.7566, 400.526, 82.9094, 61.6776] |
| nodes.shape_58 | 1 | 7 | body | [908.2923, 576.8608, 82.9094, 35.247] |
| nodes.shape_59 | 1 | 9 | body | [219.8404, 577.1516, 106.4498, 35.247] |
### page-19

中心社区，4卫星业务域，4条中心连接；每域外侧3服务条

Layout为`source-circular-19`，原型为`templates/prototypes/source-circular-19.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_47 | 1 | 44 | caption | [798.6493, 256.2313, 86.3867, 86.3867] |
| nodes.shape_48 | 1 | 44 | caption | [398.3593, 256.2313, 86.108, 86.108] |
| nodes.shape_49 | 1 | 44 | caption | [398.3593, 474.8967, 86.108, 86.108] |
| nodes.shape_50 | 1 | 44 | caption | [798.6493, 474.8967, 86.108, 86.108] |
| nodes.shape_37 | 1 | 18 | heading | [577.1753, 365.1313, 125.6493, 82.9327] |
| nodes.shape_61 | 1 | 44 | diagramCompact | [224.2, 219.0367, 139.4287, 37.1947] |
| nodes.shape_65 | 1 | 44 | diagramCompact | [224.2, 266.1093, 139.4287, 37.1947] |
| nodes.shape_66 | 1 | 44 | diagramCompact | [224.2, 310.7473, 139.4287, 37.1947] |
| nodes.shape_67 | 1 | 44 | diagramCompact | [917.552, 219.0367, 139.4287, 37.1947] |
| nodes.shape_68 | 1 | 44 | diagramCompact | [917.552, 266.1093, 139.4287, 37.1947] |
| nodes.shape_69 | 1 | 44 | diagramCompact | [917.552, 310.7473, 139.4287, 37.1947] |
| nodes.shape_70 | 1 | 44 | diagramCompact | [224.2, 449.4573, 139.4287, 37.1947] |
| nodes.shape_71 | 1 | 44 | diagramCompact | [224.2, 496.53, 139.4287, 37.1947] |
| nodes.shape_72 | 1 | 44 | diagramCompact | [224.2, 541.168, 139.4287, 37.1947] |
| nodes.shape_73 | 1 | 44 | diagramCompact | [917.552, 449.4573, 139.4287, 37.1947] |
| nodes.shape_74 | 1 | 44 | diagramCompact | [917.552, 496.53, 139.4287, 37.1947] |
| nodes.shape_75 | 1 | 44 | diagramCompact | [917.552, 541.168, 139.4287, 37.1947] |
### page-20

左用户分析文字，右中心支行定位+5扇区，外弧箭头

Layout为`source-circular-20`，原型为`templates/prototypes/source-circular-20.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_53 | 1 | 75 | heading | [115.3049, 179.9603, 320.5415, 109.8069] |
| nodes.shape_54 | 1 | 29 | body | [115.3049, 424.1032, 320.5415, 40.7396] |
| nodes.shape_55 | 1 | 165 | caption | [116.8718, 290.7073, 400.3967, 79.4849] |
| nodes.shape_56 | 1 | 275 | caption | [116.8718, 479.6856, 400.3967, 103.4158] |
| nodes.shape_57 | 1 | 30 | heading | [852.6149, 349.0342, 136.0454, 109.8069] |
| nodes.shape_58 | 1 | 7 | body | [753.8143, 270.9928, 85.4676, 36.0863] |
| nodes.shape_59 | 1 | 18 | body | [870.62, 236.8057, 199.4244, 36.0863] |
| nodes.shape_60 | 1 | 11 | body | [1038.7063, 401.0934, 123.4532, 36.0863] |
| nodes.shape_61 | 1 | 15 | body | [889.6128, 561.5826, 170.9352, 36.0863] |
| nodes.shape_62 | 1 | 13 | body | [698.7352, 473.2661, 142.446, 36.0863] |
| nodes.shape_50 | 1 | 14 | caption | [140.0335, 127.8342, 105.1441, 20.0] |
### page-21

底3驱动球与中心费力度；上3层环经营/现场/执行，多角色节点；总上箭头

Layout为`source-circular-21`，原型为`templates/prototypes/source-circular-21.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_10 | 1 | 7 | diagramMicro | [740.2691, 220.8523, 38.8178, 21.4527] |
| nodes.shape_30 | 1 | 14 | diagramMicro | [814.2249, 229.7198, 79.6747, 21.4527] |
| nodes.shape_31 | 1 | 14 | diagramMicro | [872.8831, 254.416, 79.6747, 21.4527] |
| nodes.shape_32 | 1 | 7 | diagramMicro | [829.1052, 286.1398, 38.8178, 21.4527] |
| nodes.shape_33 | 1 | 7 | diagramMicro | [779.1533, 295.491, 38.8178, 21.4527] |
| nodes.shape_34 | 1 | 10 | diagramMicro | [717.6024, 298.6207, 59.2462, 21.4527] |
| nodes.shape_35 | 1 | 16 | diagramMicro | [491.23, 300.9253, 89.8889, 21.4527] |
| nodes.shape_36 | 1 | 12 | diagramMicro | [496.4367, 222.2085, 69.4605, 21.4527] |
| nodes.shape_37 | 1 | 10 | diagramMicro | [465.1681, 167.7801, 59.2462, 21.4527] |
| nodes.shape_38 | 1 | 7 | diagramMicro | [413.9927, 232.5935, 38.8178, 21.4527] |
| nodes.shape_39 | 1 | 7 | diagramMicro | [374.4636, 255.0515, 38.8178, 21.4527] |
| nodes.shape_40 | 1 | 16 | diagramMicro | [405.0304, 289.8196, 89.8889, 21.4527] |
| nodes.shape_41 | 1 | 9 | diagramMicro | [337.5616, 315.4832, 49.032, 21.4527] |
| nodes.shape_42 | 1 | 7 | diagramMicro | [387.3808, 381.1311, 38.8178, 21.4527] |
| nodes.shape_43 | 1 | 7 | diagramMicro | [492.1025, 391.8574, 38.8178, 21.4527] |
| nodes.shape_44 | 1 | 11 | diagramMicro | [533.3862, 358.5972, 64.3581, 22.9796] |
| nodes.shape_45 | 1 | 14 | diagramMicro | [601.9077, 358.5972, 75.8432, 22.9796] |
| nodes.shape_46 | 1 | 11 | diagramMicro | [681.7815, 358.5972, 64.3581, 22.9796] |
| nodes.shape_47 | 1 | 11 | diagramMicro | [533.3862, 263.1508, 64.3581, 22.9796] |
| nodes.shape_48 | 1 | 18 | diagramMicro | [590.4985, 263.1508, 98.8322, 22.9796] |
| nodes.shape_49 | 1 | 9 | diagramMicro | [681.7815, 263.1508, 51.5832, 22.9796] |
| nodes.shape_50 | 1 | 11 | diagramMicro | [607.655, 189.8588, 64.3581, 22.9796] |
| nodes.shape_51 | 1 | 9 | body | [587.2266, 159.7567, 105.2149, 35.2424] |
| nodes.shape_52 | 1 | 9 | body | [587.2266, 233.7031, 105.2149, 35.2424] |
| nodes.shape_53 | 1 | 9 | body | [587.2266, 327.708, 105.2149, 35.2424] |
| nodes.shape_61 | 1 | 7 | diagramMicro | [909.5481, 323.4213, 38.8178, 21.4527] |
| nodes.shape_62 | 1 | 7 | diagramMicro | [941.1676, 346.7328, 38.8178, 21.4527] |
| nodes.shape_63 | 1 | 7 | diagramMicro | [841.9086, 382.7718, 38.8178, 21.4527] |
| nodes.shape_64 | 1 | 10 | diagramMicro | [743.0194, 391.8574, 59.2462, 21.4527] |
| nodes.shape_54 | 1 | 8 | heading | [585.0358, 459.2788, 110.3268, 45.9687] |
| nodes.shape_55 | 1 | 12 | caption | [594.8896, 563.2229, 89.8889, 30.6426] |
| nodes.shape_56 | 1 | 8 | diagramCompact | [611.4865, 584.4765, 56.6951, 24.516] |
| nodes.shape_57 | 1 | 12 | caption | [323.0796, 481.9455, 89.8889, 30.6426] |
| nodes.shape_58 | 1 | 8 | diagramCompact | [339.686, 503.199, 56.6951, 24.516] |
| nodes.shape_59 | 1 | 12 | caption | [887.6781, 481.9455, 89.8889, 30.6426] |
| nodes.shape_60 | 1 | 8 | diagramCompact | [904.275, 503.199, 56.6951, 24.516] |
### page-22

中心自动化个性营销；3不完整圆环；四象限分别渠道/行为/转化/触达模块

Layout为`source-circular-22`，原型为`templates/prototypes/source-circular-22.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_232 | 1 | 13 | diagramMicro | [984.7564, 120, 75.0262, 20.373] |
| nodes.shape_233 | 1 | 12 | diagramMicro | [1033.9778, 258.1968, 21.4577, 62.4896] |
| nodes.shape_234 | 1 | 60 | diagramMicro | [944.9226, 294.2889, 30.5637, 179.3128] |
| nodes.shape_240 | 1 | 16 | caption | [278.4693, 217.9973, 122.297, 27.1668] |
| nodes.shape_242 | 1 | 9 | diagramMicro | [249.1332, 288.9624, 50.6341, 23.0973] |
| nodes.shape_243 | 1 | 9 | diagramMicro | [314.0191, 288.9624, 50.6341, 23.0973] |
| nodes.shape_244 | 1 | 9 | diagramMicro | [378.905, 288.9624, 50.6341, 23.0973] |
| nodes.shape_245 | 1 | 16 | caption | [261.4932, 464.3401, 122.297, 27.1668] |
| nodes.shape_246 | 1 | 9 | diagramMicro | [233.8808, 497.7627, 50.6341, 23.0973] |
| nodes.shape_247 | 1 | 9 | diagramMicro | [297.7661, 497.7627, 50.6341, 23.0973] |
| nodes.shape_248 | 1 | 9 | diagramMicro | [362.2316, 497.7627, 50.6341, 23.0973] |
| nodes.shape_249 | 1 | 9 | diagramMicro | [232.4598, 533.077, 50.6341, 23.0973] |
| nodes.shape_250 | 1 | 13 | diagramMicro | [287.5333, 533.077, 74.3535, 23.0973] |
| nodes.shape_251 | 1 | 9 | diagramMicro | [363.0304, 533.077, 50.6341, 23.0973] |
| nodes.shape_252 | 1 | 16 | caption | [708.9681, 243.3312, 122.297, 27.1668] |
| nodes.shape_253 | 1 | 16 | caption | [688.4774, 452.6276, 122.297, 27.1668] |
| nodes.shape_254 | 1 | 12 | diagramMicro | [672.3421, 318.5591, 65.3988, 23.0973] |
| nodes.shape_255 | 1 | 14 | diagramMicro | [731.4852, 318.5591, 76.052, 23.0973] |
| nodes.shape_256 | 1 | 13 | diagramMicro | [797.1278, 318.5591, 74.1685, 23.0973] |
| nodes.shape_257 | 1 | 14 | diagramMicro | [679.1947, 488.7995, 78.0279, 23.0973] |
| nodes.shape_258 | 1 | 14 | diagramMicro | [679.2284, 525.434, 80.5167, 23.0973] |
| nodes.shape_259 | 1 | 9 | diagramMicro | [786.8194, 489.8926, 50.5584, 23.0973] |
| nodes.shape_260 | 1 | 14 | diagramMicro | [769.1622, 527.0988, 78.709, 23.0973] |
| nodes.shape_261 | 1 | 32 | caption | [493.601, 414.7319, 122.297, 56.0153] |
### page-23

中心用户服务；4环扇区与外弧；四周发现/决策/使用/留存4问题

Layout为`source-circular-23`，原型为`templates/prototypes/source-circular-23.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_57 | 1 | 325 | heading | [358.3229, 120, 822.7344, 201.2387] |
| nodes.shape_58 | 1 | 5 | compactBody | [158.7052, 304.7305, 53.2957, 30.3206] |
| nodes.shape_59 | 1 | 132 | diagramCompact | [159.3536, 332.722, 212.4661, 80.5023] |
| nodes.shape_60 | 1 | 5 | compactBody | [158.7052, 503.4098, 53.2957, 30.3206] |
| nodes.shape_61 | 1 | 99 | diagramCompact | [159.3536, 531.4013, 212.4661, 55.693] |
| nodes.shape_62 | 1 | 5 | compactBody | [811.9888, 313.3216, 53.2957, 30.3206] |
| nodes.shape_63 | 1 | 43 | diagramCompact | [812.6372, 341.3131, 271.1451, 30.8837] |
| nodes.shape_64 | 1 | 5 | compactBody | [811.9888, 589.1333, 53.2957, 30.3206] |
| nodes.shape_65 | 1 | 44 | diagramCompact | [812.6372, 617.1163, 278.2176, 30.8837] |
| nodes.shape_66 | 1 | 22 | diagramMicro | [504.8924, 272.7462, 119.397, 19.298] |
| nodes.shape_67 | 1 | 22 | diagramMicro | [330.549, 447.6443, 119.397, 19.298] |
| nodes.shape_68 | 1 | 22 | diagramMicro | [504.8924, 623.1992, 119.397, 19.298] |
| nodes.shape_69 | 1 | 22 | diagramMicro | [681.8295, 447.6528, 119.397, 19.298] |
| nodes.shape_70 | 1 | 22 | diagramMicro | [504.8924, 583.0846, 119.397, 19.298] |
| nodes.shape_71 | 1 | 22 | diagramMicro | [416.5339, 349.1224, 119.397, 19.298] |
| nodes.shape_72 | 1 | 22 | diagramMicro | [635.4272, 443.6601, 119.397, 19.298] |
| nodes.shape_73 | 1 | 10 | diagramMicro | [535.87, 534.6859, 57.4419, 19.298] |
| nodes.shape_74 | 1 | 22 | diagramMicro | [504.8924, 358.7684, 119.397, 19.298] |
| nodes.shape_75 | 1 | 22 | diagramMicro | [591.3881, 447.6443, 119.397, 19.298] |
| nodes.shape_78 | 1 | 22 | diagramMicro | [417.774, 445.8441, 119.397, 19.298] |
| nodes.shape_79 | 1 | 10 | diagramMicro | [469.0435, 523.4074, 57.4419, 19.298] |
| nodes.shape_80 | 1 | 10 | diagramMicro | [404.2048, 581.0455, 57.4419, 19.298] |
| nodes.shape_81 | 1 | 4 | diagramCompact | [131.0037, 311.2143, 25.5857, 24.8093] |
| nodes.shape_82 | 1 | 4 | diagramCompact | [131.0037, 503.7766, 25.5857, 24.8093] |
| nodes.shape_83 | 1 | 4 | diagramCompact | [784.5604, 316.3502, 25.5857, 24.8093] |
| nodes.shape_84 | 1 | 4 | diagramCompact | [782.0009, 592.307, 25.5857, 24.8093] |
### page-24

右雷达式同心圈；中心主播，3外围人群节点和透明辐射区；左4类画像说明

Layout为`source-circular-24`，原型为`templates/prototypes/source-circular-24.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_63 | 1 | 23 | heading | [99.7105, 120, 291.1348, 51.2204] |
| nodes.shape_65 | 1 | 10 | body | [166.0835, 164.861, 108.4739, 36.1611] |
| nodes.shape_66 | 1 | 261 | caption | [98.0973, 213.0136, 633.3781, 60.8714] |
| nodes.shape_67 | 1 | 11 | diagramMicro | [127.1716, 359.3456, 63.2772, 22.5937] |
| nodes.shape_68 | 1 | 11 | diagramMicro | [381.8936, 359.3456, 63.2772, 22.5937] |
| nodes.shape_69 | 1 | 11 | diagramMicro | [127.6845, 512.1303, 63.2772, 22.5937] |
| nodes.shape_70 | 1 | 13 | diagramMicro | [381.8936, 512.1303, 74.5694, 22.5937] |
| nodes.shape_71 | 1 | 152 | diagramMicro | [113.912, 391.7301, 209.3108, 66.5408] |
| nodes.shape_72 | 1 | 200 | diagramMicro | [370.4709, 391.7301, 217.1342, 86.1226] |
| nodes.shape_73 | 1 | 117 | diagramMicro | [113.912, 545.727, 210.9426, 46.9497] |
| nodes.shape_74 | 1 | 152 | diagramMicro | [370.4709, 545.727, 209.3108, 66.5408] |
| nodes.shape_75 | 1 | 12 | body | [862.4869, 395.5719, 137.6601, 36.1611] |
| nodes.shape_76 | 1 | 21 | caption | [729.4706, 345.4798, 53.2345, 62.1209] |
| nodes.shape_77 | 1 | 27 | caption | [1055.8899, 219.2051, 70.8022, 62.1209] |
| nodes.shape_78 | 1 | 21 | caption | [913.5768, 556.8887, 53.2345, 62.1209] |
| nodes.shape_79 | 1 | 13 | diagramMicro | [976.453, 299.2201, 75.2874, 23.7033] |
| nodes.shape_80 | 1 | 13 | diagramMicro | [965.3194, 352.5479, 75.2874, 23.7033] |
| nodes.shape_81 | 1 | 13 | diagramMicro | [925.1207, 483.2331, 75.2874, 23.7033] |
| nodes.shape_82 | 1 | 13 | diagramMicro | [884.4092, 476.0438, 75.2874, 23.7033] |
| nodes.shape_83 | 1 | 13 | diagramMicro | [1106.6153, 481.4112, 75.2874, 27.3679] |
### page-25

左精细化迭代双弧，中央3堆叠圈细节/标准/把握，右设计走查与修改反馈虚圆

Layout为`source-circular-25`，原型为`templates/prototypes/source-circular-25.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_37 | 1 | 19 | heading | [134.7589, 120, 246.6431, 53.1298] |
| nodes.shape_39 | 1 | 6 | body | [180.1702, 166.5333, 65.6361, 37.5091] |
| nodes.shape_40 | 1 | 15 | heading | [265.3056, 409.6944, 201.0673, 53.1298] |
| nodes.shape_41 | 1 | 22 | compactBody | [262.578, 465.7453, 206.271, 34.3753] |
| nodes.shape_42 | 1 | 16 | body | [381.3052, 610.4909, 182.8351, 37.5091] |
| nodes.shape_43 | 1 | 14 | body | [393.028, 270.9552, 159.3895, 37.5091] |
| nodes.shape_44 | 1 | 11 | compactBody | [486.085, 409.8588, 102.0909, 34.3753] |
| nodes.shape_45 | 1 | 11 | compactBody | [486.085, 472.274, 102.0909, 34.3753] |
| nodes.shape_46 | 1 | 17 | compactBody | [760.033, 409.8588, 153.2089, 34.3753] |
| nodes.shape_47 | 1 | 11 | compactBody | [785.5968, 472.274, 102.0909, 34.3753] |
| nodes.shape_48 | 1 | 18 | heading | [1022.3065, 419.0282, 122.9347, 82.5722] |
| nodes.shape_49 | 1 | 6 | compactBody | [940.0147, 395.7953, 55.219, 31.2511] |
| nodes.shape_50 | 1 | 6 | compactBody | [940.0147, 490.8835, 55.219, 31.2511] |
| nodes.shape_16 | 1 | 12 | caption | [642.2343, 308.9673, 43.8057, 48.5258] |
| nodes.shape_26 | 1 | 12 | caption | [642.95, 537.3685, 43.5543, 48.3227] |
| nodes.shape_27 | 1 | 9 | caption | [630.3567, 438.3437, 66.642, 21.5982] |
### page-26

两相交大圆业务诉求/用户需求，交集PC端；左右各指标组，向外箭头

Layout为`source-circular-26`，原型为`templates/prototypes/source-circular-26.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_61 | 1 | 18 | heading | [122.4288, 120, 234.8222, 50.5835] |
| nodes.shape_63 | 1 | 5 | body | [165.6638, 164.3031, 62.4903, 35.7114] |
| nodes.shape_64 | 1 | 10 | caption | [480.8688, 401.2065, 77.3624, 26.7789] |
| nodes.shape_65 | 1 | 10 | caption | [709.7145, 401.2065, 77.3624, 26.7789] |
| nodes.shape_66 | 1 | 7 | caption | [606.8624, 400.5895, 51.1728, 26.7789] |
| nodes.shape_67 | 1 | 11 | diagramMicro | [255.4948, 370.2836, 61.2472, 19.3383] |
| nodes.shape_68 | 1 | 12 | diagramMicro | [251.1575, 404.1072, 69.9218, 19.3383] |
| nodes.shape_69 | 1 | 12 | diagramMicro | [251.1575, 437.9216, 69.9218, 19.3383] |
| nodes.shape_70 | 1 | 14 | diagramMicro | [944.8959, 370.2836, 78.6056, 19.3383] |
| nodes.shape_71 | 1 | 16 | diagramMicro | [940.5586, 404.1072, 87.2802, 19.3383] |
| nodes.shape_72 | 1 | 16 | diagramMicro | [939.0115, 437.9216, 90.3835, 19.3383] |
| nodes.shape_73 | 1 | 16 | diagramMicro | [1049.7647, 370.2836, 87.2802, 19.3383] |
| nodes.shape_74 | 1 | 16 | diagramMicro | [1049.7647, 404.1072, 87.2802, 19.3383] |
| nodes.shape_75 | 1 | 12 | diagramMicro | [1058.4393, 437.9216, 69.9218, 19.3383] |
| nodes.shape_76 | 1 | 12 | diagramMicro | [702.9369, 525.2018, 67.4446, 23.8045] |
| nodes.shape_77 | 1 | 12 | diagramMicro | [702.9369, 294.5512, 67.4446, 23.8045] |
| nodes.shape_78 | 1 | 12 | diagramMicro | [482.5356, 525.2018, 67.4446, 23.8045] |
| nodes.shape_79 | 1 | 10 | diagramMicro | [488.733, 294.5512, 55.0497, 23.8045] |
| nodes.shape_80 | 1 | 45 | diagramMicro | [533.8465, 625.6873, 247.9907, 22.3127] |
### page-27

主产品目标大圆包住设计目标小圆，左右业务/用户需求圈，由虚线满足弧连到中心

Layout为`source-circular-27`，原型为`templates/prototypes/source-circular-27.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_42 | 1 | 19 | heading | [88.6727, 120, 241.9059, 52.1094] |
| nodes.shape_44 | 1 | 5 | body | [133.2118, 165.6396, 64.3754, 36.7887] |
| nodes.shape_45 | 1 | 14 | diagramCompact | [1100.9304, 120.4079, 90.3969, 24.5226] |
| nodes.shape_46 | 1 | 9 | heading | [173.9279, 365.691, 120.5735, 39.8528] |
| nodes.shape_47 | 1 | 15 | caption | [178.0735, 414.7268, 110.3565, 31.5806] |
| nodes.shape_48 | 1 | 18 | caption | [165.4565, 448.0529, 135.5812, 31.5806] |
| nodes.shape_49 | 1 | 15 | caption | [178.0735, 481.6067, 110.3565, 31.5806] |
| nodes.shape_50 | 1 | 9 | heading | [960.0463, 365.691, 120.5735, 39.8528] |
| nodes.shape_51 | 1 | 25 | caption | [926.834, 414.7268, 186.9885, 31.5806] |
| nodes.shape_52 | 1 | 19 | caption | [949.8293, 448.0529, 141.0074, 31.5806] |
| nodes.shape_53 | 1 | 17 | caption | [957.4944, 481.6067, 125.6772, 31.5806] |
| nodes.shape_54 | 1 | 10 | heading | [562.1917, 426.8506, 130.7905, 42.917] |
| nodes.shape_55 | 1 | 87 | caption | [522.5191, 475.8958, 210.1356, 63.1991] |
| nodes.shape_56 | 1 | 81 | caption | [528.9889, 540.9827, 197.2055, 63.1991] |
| nodes.shape_57 | 1 | 10 | heading | [562.1917, 254.1107, 130.7905, 42.917] |
| nodes.shape_58 | 1 | 72 | caption | [540.4012, 303.1465, 174.3715, 63.1991] |
| nodes.shape_59 | 1 | 7 | caption | [377.736, 570.8273, 54.1585, 30.6509] |
| nodes.shape_60 | 1 | 7 | caption | [822.9852, 570.8273, 54.1585, 30.6509] |
### page-28

右中心3层三角塔，外围云图/高德/API3大圈，3类行业框与循环关系，左说明

Layout为`source-circular-28`，原型为`templates/prototypes/source-circular-28.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_100 | 1 | 72 | heading | [194.286, 244.5064, 305.9374, 117.5768] |
| nodes.shape_101 | 1 | 265 | diagramMicro | [195.5312, 445.3031, 288.8034, 76.8159] |
| nodes.shape_102 | 1 | 32 | diagramCompact | [195.5312, 370.4925, 205.6482, 23.5137] |
| nodes.shape_103 | 1 | 12 | diagramMicro | [826.416, 195.8213, 67.9295, 15.6785] |
| nodes.shape_104 | 1 | 8 | diagramMicro | [838.3912, 180.159, 43.9791, 20.902] |
| nodes.shape_105 | 1 | 12 | diagramMicro | [654.8174, 491.9425, 67.9295, 15.6785] |
| nodes.shape_106 | 1 | 13 | diagramMicro | [652.6423, 476.2801, 72.2878, 20.902] |
| nodes.shape_107 | 1 | 17 | diagramMicro | [986.8479, 491.9425, 94.0631, 15.6785] |
| nodes.shape_108 | 1 | 15 | diagramMicro | [991.4003, 476.2801, 84.9422, 20.902] |
| nodes.shape_109 | 1 | 4 | diagramMicro | [652.3122, 340.4719, 26.5621, 15.0] |
| nodes.shape_110 | 1 | 9 | diagramMicro | [661.5504, 353.5376, 53.1, 15.0] |
| nodes.shape_111 | 1 | 4 | diagramMicro | [679.7568, 319.3637, 26.5621, 15.0] |
| nodes.shape_112 | 1 | 7 | diagramMicro | [690.9633, 328.4542, 38.133, 15.0] |
| nodes.shape_113 | 1 | 4 | diagramMicro | [727.3169, 246.6595, 26.5621, 15.0] |
| nodes.shape_114 | 1 | 5 | diagramMicro | [738.4158, 254.6028, 31.1872, 15.0] |
| nodes.shape_115 | 1 | 4 | diagramMicro | [730.5108, 208.8984, 26.5621, 15.0] |
| nodes.shape_116 | 1 | 8 | diagramMicro | [740.4731, 220.6371, 48.0625, 15.0] |
| nodes.shape_117 | 1 | 6 | diagramMicro | [667.4339, 263.5068, 37.4457, 20.902] |
| nodes.shape_118 | 1 | 13 | diagramMicro | [687.3125, 285.5498, 72.967, 20.902] |
| nodes.shape_119 | 1 | 5 | diagramMicro | [1036.7843, 342.1032, 32.0039, 15.0] |
| nodes.shape_120 | 1 | 8 | diagramMicro | [1007.2188, 355.4539, 44.6583, 15.0] |
| nodes.shape_123 | 1 | 4 | diagramMicro | [1008.9533, 320.6453, 26.5621, 15.0] |
| nodes.shape_124 | 1 | 5 | diagramMicro | [991.4468, 328.8262, 31.0498, 15.0] |
| nodes.shape_126 | 1 | 4 | diagramMicro | [968.264, 246.615, 26.5621, 15.0] |
| nodes.shape_127 | 1 | 5 | diagramMicro | [950.3468, 254.802, 31.8665, 15.0] |
| nodes.shape_129 | 1 | 5 | diagramMicro | [959.8714, 208.2414, 32.0039, 15.0] |
| nodes.shape_130 | 1 | 7 | diagramMicro | [932.4592, 221.9672, 42.0789, 15.0] |
| nodes.shape_133 | 1 | 6 | diagramMicro | [1022.6052, 255.9939, 37.4457, 20.902] |
| nodes.shape_134 | 1 | 14 | diagramMicro | [962.2446, 279.0002, 77.5921, 20.902] |
| nodes.shape_135 | 1 | 4 | diagramMicro | [922.7997, 527.5928, 26.5621, 15.0] |
| nodes.shape_136 | 1 | 5 | diagramMicro | [921.9466, 512.1528, 29.2871, 15.0] |
| nodes.shape_138 | 1 | 4 | diagramMicro | [889.4454, 533.6653, 26.5621, 15.0] |
| nodes.shape_139 | 1 | 6 | diagramMicro | [885.6329, 514.8131, 34.3165, 15.0] |
| nodes.shape_140 | 1 | 4 | diagramMicro | [804.5194, 527.892, 26.5621, 15.0] |
| nodes.shape_141 | 1 | 5 | diagramMicro | [803.6987, 511.6838, 28.3329, 15.0] |
| nodes.shape_142 | 1 | 4 | diagramMicro | [770.5506, 545.2604, 26.5621, 15.0] |
| nodes.shape_143 | 1 | 8 | diagramMicro | [761.8179, 520.3883, 45.6125, 15.0] |
| nodes.shape_144 | 1 | 6 | diagramMicro | [840.5743, 559.9933, 37.4457, 20.902] |
| nodes.shape_145 | 1 | 9 | diagramMicro | [834.6555, 529.0405, 48.8792, 20.902] |
| nodes.shape_147 | 1 | 14 | diagramMicro | [768.4119, 337.2055, 80.9963, 15.6785] |
| nodes.shape_148 | 1 | 10 | diagramMicro | [767.9953, 328.072, 59.221, 20.902] |
| nodes.shape_151 | 1 | 14 | diagramMicro | [868.2928, 337.9079, 80.9963, 15.6785] |
| nodes.shape_152 | 1 | 12 | diagramMicro | [885.0367, 328.7709, 70.1127, 20.902] |
| nodes.shape_154 | 1 | 17 | diagramMicro | [810.0421, 435.5192, 93.5132, 15.6785] |
| nodes.shape_155 | 1 | 10 | diagramMicro | [827.1841, 419.8568, 59.221, 20.902] |
| nodes.shape_156 | 1 | 8 | diagramMicro | [836.6931, 327.0589, 46.1623, 15.0] |
| nodes.shape_157 | 1 | 5 | diagramMicro | [844.3181, 317.2955, 30.9204, 16.9804] |
| nodes.shape_158 | 1 | 10 | diagramMicro | [832.3429, 359.8714, 54.8708, 15.0] |
| nodes.shape_159 | 1 | 5 | diagramMicro | [844.3181, 350.108, 30.9204, 16.9804] |
| nodes.shape_160 | 1 | 9 | diagramMicro | [834.518, 393.7108, 50.5125, 15.0] |
| nodes.shape_161 | 1 | 5 | diagramMicro | [844.3181, 383.9474, 30.9204, 16.9804] |
### page-29

中心Cloud；内环企业管理5域；中环12协作功能图标；外圈6收益说明

Layout为`source-circular-29`，原型为`templates/prototypes/source-circular-29.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_46 | 1 | 12 | diagramMicro | [530.009, 254.5261, 66.3422, 20.1009] |
| nodes.shape_47 | 1 | 10 | diagramMicro | [474.0118, 318.4044, 56.2959, 20.1009] |
| nodes.shape_48 | 1 | 10 | diagramMicro | [458.2496, 400.9485, 56.2959, 20.1009] |
| nodes.shape_49 | 1 | 10 | diagramMicro | [486.4556, 479.2119, 56.2959, 20.1009] |
| nodes.shape_50 | 1 | 10 | diagramMicro | [539.9641, 532.3056, 56.2959, 20.1009] |
| nodes.shape_51 | 1 | 10 | diagramMicro | [694.6823, 532.3056, 56.2959, 20.1009] |
| nodes.shape_52 | 1 | 10 | diagramMicro | [743.2133, 479.2119, 56.2959, 20.1009] |
| nodes.shape_53 | 1 | 10 | diagramMicro | [772.6637, 411.8161, 56.2959, 20.1009] |
| nodes.shape_54 | 1 | 10 | diagramMicro | [755.6571, 329.272, 56.2959, 20.1009] |
| nodes.shape_55 | 1 | 10 | diagramMicro | [694.2675, 256.2682, 56.2959, 20.1009] |
| nodes.shape_56 | 1 | 8 | caption | [612.1051, 520.4922, 62.9907, 26.804] |
| nodes.shape_57 | 1 | 10 | caption | [604.2821, 452.3996, 78.6284, 26.804] |
| nodes.shape_58 | 1 | 20 | diagramMicro | [542.4528, 354.9312, 56.2959, 32.1714] |
| nodes.shape_59 | 1 | 20 | diagramMicro | [543.6972, 423.364, 56.2959, 32.1714] |
| nodes.shape_60 | 1 | 20 | diagramMicro | [684.7853, 423.364, 56.2959, 32.1714] |
| nodes.shape_61 | 1 | 24 | diagramMicro | [679.758, 354.0933, 66.3422, 32.1714] |
| nodes.shape_62 | 1 | 12 | diagramMicro | [609.3094, 313.0287, 67.0474, 20.1009] |
| nodes.shape_63 | 1 | 66 | caption | [875.5658, 191.2036, 239.9917, 55.2838] |
| nodes.shape_64 | 1 | 60 | caption | [873.0771, 519.7207, 220.5047, 55.2838] |
| nodes.shape_65 | 1 | 48 | caption | [236.3263, 197.8403, 178.2288, 55.2838] |
| nodes.shape_66 | 1 | 52 | caption | [164.4425, 357.1213, 192.1825, 55.2838] |
| nodes.shape_67 | 1 | 56 | caption | [203.2672, 508.6623, 205.3398, 55.2838] |
| nodes.shape_2 | 1 | 7 | compactBody | [603.4608, 385.8085, 69.6937, 32.1714] |
| nodes.shape_69 | 1 | 44 | caption | [915.3778, 357.1213, 164.0014, 55.2838] |
### page-30

上4分区椭圆盘，下3扇区圆台，中上箭头

Layout为`source-circular-30`，原型为`templates/prototypes/source-circular-30.svg`。

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
### page-31

中心主题双向环箭头，周边11具象元素圈，部分在外环，连线稀疏

Layout为`source-circular-31`，原型为`templates/prototypes/source-circular-31.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_36 | 1 | 7 | caption | [754.5031, 259.6902, 52.4217, 29.668] |
| nodes.shape_37 | 1 | 5 | body | [606.6683, 140.954, 62.311, 35.6089] |
| nodes.shape_38 | 1 | 5 | body | [845.1874, 384.0459, 62.311, 35.6089] |
| nodes.shape_39 | 1 | 6 | compactBody | [993.2427, 270.2682, 57.3618, 32.6339] |
| nodes.shape_40 | 1 | 5 | compactBody | [1044.3513, 453.2253, 46.3889, 32.6339] |
| nodes.shape_41 | 1 | 8 | compactBody | [887.6004, 556.2047, 72.9808, 32.6339] |
| nodes.shape_42 | 1 | 7 | body | [755.4948, 526.1878, 81.6397, 35.6089] |
| nodes.shape_43 | 1 | 7 | body | [331.5118, 488.8067, 84.5597, 35.6089] |
| nodes.shape_44 | 1 | 7 | caption | [217.2382, 348.033, 57.2057, 29.668] |
| nodes.shape_45 | 1 | 6 | caption | [177.1116, 476.3738, 47.4724, 26.7021] |
| nodes.shape_46 | 1 | 14 | caption | [422.3614, 253.4829, 52.4217, 50.4383] |
| nodes.shape_47 | 1 | 17 | compactBody | [539.5274, 354.0566, 158.771, 32.6339] |
| nodes.shape_48 | 1 | 17 | compactBody | [539.5274, 429.7186, 158.771, 32.6339] |
| nodes.shape_49 | 1 | 12 | heading | [538.7928, 386.3782, 158.771, 44.5066] |
### page-32

左发起者→中平台→右3拼购者；中环4行为圈用/想/拼/比；外2价值回流弧

Layout为`source-circular-32`，原型为`templates/prototypes/source-circular-32.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_33 | 1 | 12 | caption | [584.627, 142.6075, 89.5798, 34.3777] |
| nodes.shape_34 | 1 | 12 | caption | [584.627, 210.051, 89.5798, 34.3777] |
| nodes.shape_35 | 1 | 12 | caption | [436.8055, 371.1303, 89.5798, 34.3777] |
| nodes.shape_36 | 1 | 12 | caption | [717.6664, 371.1303, 89.5798, 34.3777] |
| nodes.shape_37 | 1 | 12 | caption | [585.5509, 521.7235, 89.5798, 34.3777] |
| nodes.shape_38 | 1 | 12 | caption | [585.5509, 588.2432, 89.5798, 34.3777] |
| nodes.shape_39 | 1 | 12 | caption | [713.9708, 481.0726, 89.5798, 34.3777] |
| nodes.shape_40 | 1 | 12 | caption | [444.1965, 481.0726, 89.5798, 34.3777] |
| nodes.shape_41 | 1 | 12 | caption | [444.1965, 219.6132, 89.5798, 34.3777] |
| nodes.shape_42 | 1 | 12 | caption | [715.8186, 219.6132, 89.5798, 34.3777] |
| nodes.shape_43 | 1 | 12 | caption | [911.6821, 248.2537, 89.5798, 34.3777] |
| nodes.shape_44 | 1 | 12 | caption | [911.6821, 456.1277, 89.5798, 34.3777] |
| nodes.shape_45 | 1 | 12 | caption | [1027.1677, 350.8048, 89.5798, 34.3777] |
| nodes.shape_46 | 1 | 7 | heading | [580.3217, 346.8044, 89.5798, 52.5506] |
| nodes.shape_47 | 1 | 14 | heading | [163.0308, 337.5101, 179.5015, 52.5506] |
| nodes.shape_48 | 1 | 48 | caption | [164.8785, 384.6283, 179.5015, 54.038] |
| nodes.shape_49 | 1 | 24 | caption | [536.2801, 384.6283, 179.5015, 30.7561] |
| nodes.shape_50 | 1 | 11 | caption | [915.9967, 275.6099, 83.4175, 30.7561] |
| nodes.shape_51 | 1 | 11 | caption | [1031.4822, 380.0088, 83.4175, 30.7561] |
| nodes.shape_52 | 1 | 11 | caption | [912.3011, 484.7311, 83.4175, 30.7561] |
| nodes.shape_53 | 1 | 11 | caption | [447.5872, 250.665, 83.4175, 30.7561] |
| nodes.shape_54 | 1 | 11 | caption | [717.3615, 250.665, 83.4175, 30.7561] |
| nodes.shape_55 | 1 | 11 | caption | [447.5872, 508.4288, 83.4175, 30.7561] |
| nodes.shape_56 | 1 | 15 | caption | [704.4271, 508.4288, 109.2863, 30.7561] |
### page-33

实际中心百度会员+4环扇区入口；两翼卡券平台/车后服务；左右外弧

Layout为`source-circular-33`，原型为`templates/prototypes/source-circular-33.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_77 | 1 | 12 | diagramCompact | [515.1834, 542.2073, 75.9555, 17.5] |
| nodes.shape_78 | 1 | 9 | diagramMicro | [515.1834, 561.1357, 53.6055, 15.0] |
| nodes.shape_79 | 1 | 9 | diagramCompact | [760.661, 542.2073, 60.7662, 17.5] |
| nodes.shape_80 | 1 | 9 | diagramMicro | [760.661, 561.1357, 53.6055, 15.0] |
| nodes.shape_68 | 1 | 13 | compactBody | [276.8664, 406.2489, 119.1975, 25.0] |
| nodes.shape_69 | 1 | 54 | diagramMicro | [276.8664, 438.864, 148.5434, 42.2178] |
| nodes.shape_70 | 1 | 8 | compactBody | [918.0403, 406.2489, 79.4621, 25.0] |
| nodes.shape_71 | 1 | 54 | diagramMicro | [918.0403, 438.864, 148.5434, 42.2178] |
| nodes.shape_72 | 1 | 9 | diagramMicro | [642.7307, 490.6373, 51.4182, 15.0] |
| nodes.shape_73 | 1 | 9 | diagramCompact | [515.1834, 339.364, 60.7662, 17.5] |
| nodes.shape_74 | 1 | 9 | diagramMicro | [515.1834, 358.2925, 53.6055, 15.0] |
| nodes.shape_75 | 1 | 9 | diagramCompact | [760.661, 339.364, 60.7662, 17.5] |
| nodes.shape_76 | 1 | 9 | diagramMicro | [760.661, 358.2925, 53.6055, 15.0] |
### page-34

中心结果，3重背景环；左右各3带图标的效益球及说明，共6项

Layout为`source-circular-34`，原型为`templates/prototypes/source-circular-34.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_101 | 1 | 26 | heading | [543.8563, 342.53, 170.324, 82.9327] |
| nodes.shape_328 | 1 | 60 | diagramCompact | [899.7137, 251.8387, 132.242, 60.7053] |
| nodes.shape_329 | 1 | 19 | caption | [899.7137, 228.6433, 141.5553, 27.346] |
| nodes.shape_337 | 1 | 60 | diagramCompact | [930.9977, 370.8733, 132.242, 60.7053] |
| nodes.shape_338 | 1 | 19 | caption | [930.9977, 347.678, 141.5553, 27.346] |
| nodes.shape_340 | 1 | 60 | diagramCompact | [896.9563, 489.908, 132.242, 60.7053] |
| nodes.shape_341 | 1 | 19 | caption | [896.9563, 466.7127, 141.5553, 27.346] |
| nodes.shape_352 | 1 | 60 | diagramCompact | [225.4503, 250.9513, 132.242, 60.7053] |
| nodes.shape_353 | 1 | 19 | caption | [216.1443, 227.7487, 141.5553, 27.346] |
| nodes.shape_355 | 1 | 60 | diagramCompact | [225.4503, 369.986, 132.242, 60.7053] |
| nodes.shape_356 | 1 | 19 | caption | [216.1443, 346.7833, 141.5553, 27.346] |
| nodes.shape_358 | 1 | 60 | diagramCompact | [225.4503, 489.0207, 132.242, 60.7053] |
| nodes.shape_359 | 1 | 19 | caption | [207.447, 465.818, 141.5553, 27.346] |
### page-35

上中央大环主题，向下5条辐射连接5图标球；外围01–05标题说明

Layout为`source-circular-35`，原型为`templates/prototypes/source-circular-35.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_7 | 1 | 2 | heading | [238.7508, 272.3736, 57.3324, 40] |
| nodes.shape_8 | 1 | 2 | heading | [343.9398, 477.7654, 71.1518, 40] |
| nodes.shape_9 | 1 | 2 | heading | [862.795, 483.112, 54.1186, 40] |
| nodes.shape_11 | 1 | 2 | heading | [984.2284, 274.5162, 60.293, 40] |
| nodes.shape_13 | 1 | 2 | heading | [592.6304, 567.0509, 65.4644, 40] |
| nodes.shape_80 | 1 | 42 | diagramCompact | [984.2284, 316.6073, 132.5454, 40.9128] |
| nodes.shape_81 | 1 | 42 | diagramCompact | [862.795, 524.9695, 132.5454, 40.9128] |
| nodes.shape_82 | 1 | 42 | diagramCompact | [273.6352, 524.9695, 132.5454, 40.9128] |
| nodes.shape_83 | 1 | 42 | diagramCompact | [163.2262, 317.0943, 132.5454, 40.9128] |
| nodes.shape_84 | 1 | 42 | diagramCompact | [557.9017, 607.0872, 132.5454, 40.9128] |
| nodes.shape_85 | 1 | 27 | diagramMicro | [555.7105, 248.7862, 147.212, 20.4515] |
| nodes.shape_86 | 1 | 14 | caption | [577.8176, 226.718, 102.9978, 26.7525] |
### page-36

中心主题，两层圈；外环6卫星球，左右各3说明

Layout为`source-circular-36`，原型为`templates/prototypes/source-circular-36.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_144 | 1 | 18 | body | [189.0697, 224.2067, 195.8293, 35.5447] |
| nodes.shape_145 | 1 | 44 | diagramMicro | [260.9803, 256.5687, 121.1687, 35.5447] |
| nodes.shape_147 | 1 | 18 | body | [153.965, 360.4087, 195.8293, 35.5447] |
| nodes.shape_148 | 1 | 44 | diagramMicro | [225.8757, 392.7633, 121.1687, 35.5447] |
| nodes.shape_150 | 1 | 18 | body | [175.1803, 495.166, 195.8293, 35.5447] |
| nodes.shape_151 | 1 | 44 | diagramMicro | [247.091, 527.528, 121.1687, 35.5447] |
| nodes.shape_219 | 1 | 18 | body | [859.6443, 224.2067, 195.8293, 35.5447] |
| nodes.shape_220 | 1 | 44 | diagramMicro | [931.555, 256.5687, 121.1687, 35.5447] |
| nodes.shape_217 | 1 | 18 | body | [895.101, 360.4087, 195.8293, 35.5447] |
| nodes.shape_218 | 1 | 44 | diagramMicro | [967.0117, 392.7633, 121.1687, 35.5447] |
| nodes.shape_215 | 1 | 18 | body | [845.755, 495.166, 195.8293, 35.5447] |
| nodes.shape_216 | 1 | 44 | diagramMicro | [917.6657, 527.528, 121.1687, 35.5447] |
| nodes.shape_256 | 1 | 10 | body | [602.655, 404.768, 109.0027, 35.5447] |
### page-37

底部中心半圆，6产品图标沿上半圆等距；虚线外弧

Layout为`source-circular-37`，原型为`templates/prototypes/source-circular-37.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_12 | 1 | 17 | compactBody | [163.1521, 445.9798, 161.9915, 33.233] |
| nodes.shape_13 | 1 | 23 | compactBody | [239.7216, 290.6211, 211.6011, 33.233] |
| nodes.shape_14 | 1 | 23 | compactBody | [643.205, 207.8729, 209.7243, 33.233] |
| nodes.shape_15 | 1 | 15 | compactBody | [883.1972, 294.2461, 141.2188, 33.233] |
| nodes.shape_16 | 1 | 13 | compactBody | [466.4652, 210.5809, 120.4546, 33.233] |
| nodes.shape_18 | 1 | 31 | heading | [444.6212, 555.7823, 395.0595, 63.5866] |
| nodes.shape_68 | 1 | 15 | compactBody | [975.6292, 445.7998, 141.2188, 33.233] |
### page-38

中心每日练习；外周9共创大赛卫星圈；两侧技能提升输入箭头与弧线

Layout为`source-circular-38`，原型为`templates/prototypes/source-circular-38.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_53 | 1 | 18 | caption | [636.7795, 206.2524, 66.0959, 52.0299] |
| nodes.shape_54 | 1 | 18 | caption | [745.1018, 247.5032, 66.0959, 52.0299] |
| nodes.shape_55 | 1 | 18 | caption | [808.2329, 349.6023, 66.0959, 52.0299] |
| nodes.shape_56 | 1 | 18 | caption | [789.0899, 465.7201, 66.0959, 52.0299] |
| nodes.shape_57 | 1 | 18 | caption | [694.9189, 540.1893, 66.0959, 52.0299] |
| nodes.shape_58 | 1 | 18 | caption | [581.0365, 540.6818, 66.0959, 52.0299] |
| nodes.shape_59 | 1 | 18 | caption | [489.3377, 465.4359, 66.0959, 52.0299] |
| nodes.shape_60 | 1 | 18 | caption | [469.4085, 351.6577, 66.0959, 52.0299] |
| nodes.shape_61 | 1 | 18 | caption | [528.0215, 247.5032, 66.0959, 52.0299] |
| nodes.shape_62 | 1 | 27 | heading | [604.8587, 347.6889, 120.3897, 131.6046] |
| nodes.shape_63 | 1 | 23 | diagramCompact | [879.5669, 447.8463, 149.3267, 26.0197] |
| nodes.shape_64 | 1 | 11 | heading | [869.8202, 395.4754, 149.3267, 39.792] |
| nodes.shape_65 | 1 | 20 | caption | [1001.6899, 359.8037, 149.3267, 30.6042] |
| nodes.shape_66 | 1 | 20 | caption | [1060.8712, 395.4754, 149.3267, 30.6042] |
| nodes.shape_67 | 1 | 20 | caption | [982.2912, 437.8817, 149.3267, 30.6042] |
| nodes.shape_68 | 1 | 20 | caption | [1057.9065, 467.8986, 149.3267, 30.6042] |
| nodes.shape_69 | 1 | 20 | caption | [919.5768, 371.3406, 149.3267, 30.6042] |
| nodes.shape_70 | 1 | 11 | heading | [302.2554, 409.513, 149.3267, 39.792] |
| nodes.shape_71 | 1 | 20 | caption | [195.6381, 397.0383, 149.3267, 30.6042] |
| nodes.shape_72 | 1 | 20 | caption | [208.037, 432.8521, 149.3267, 30.6042] |
| nodes.shape_73 | 1 | 20 | caption | [117.4748, 435.7032, 149.3267, 30.6042] |
| nodes.shape_74 | 1 | 20 | caption | [69.802, 480.307, 149.3267, 30.6042] |
| nodes.shape_75 | 1 | 20 | caption | [101.7417, 370.5829, 149.3267, 30.6042] |
| nodes.shape_76 | 1 | 23 | diagramCompact | [328.7961, 462.8216, 149.3267, 26.0197] |
### page-39

中心2相交球市场环境/竞品分析；左右各3标签及括弧，两侧宽弧

Layout为`source-circular-39`，原型为`templates/prototypes/source-circular-39.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_16 | 1 | 17 | compactBody | [453.674, 412.1542, 160.2491, 34.9361] |
| nodes.shape_17 | 1 | 99 | diagramMicro | [446.16, 448.9262, 179.522, 45.324] |
| nodes.shape_18 | 1 | 17 | compactBody | [659.8745, 413.107, 160.2491, 34.9361] |
| nodes.shape_19 | 1 | 99 | diagramMicro | [658.7513, 446.8966, 178.7164, 45.324] |
| nodes.shape_22 | 1 | 10 | compactBody | [256.4361, 320.2048, 90.1135, 30.0404] |
| nodes.shape_23 | 1 | 10 | compactBody | [241.7954, 414.3232, 90.1135, 30.0404] |
| nodes.shape_24 | 1 | 10 | compactBody | [252.4854, 503.8014, 90.1135, 30.0404] |
| nodes.shape_25 | 1 | 10 | compactBody | [922.8094, 503.8014, 90.1135, 30.0404] |
| nodes.shape_26 | 1 | 10 | compactBody | [932.1515, 324.9843, 90.1135, 30.0404] |
| nodes.shape_27 | 1 | 10 | compactBody | [937.1789, 413.138, 90.1135, 30.0404] |
### page-40

几何装饰结束页，叠片标题框

Layout为`source-circular-40`，原型为`templates/prototypes/source-circular-40.svg`。

| 字段或派生文字 | 最短 | 最长 | 字阶 | 框体px |
|---|---:|---:|---|---|
| title | 2 | 32 | title | [48, 24, 1184, 48] |
| section_name | 0 | 24 | caption | [48, 684, 307.84000000000003, 24] |
| source | 0 | 64 | caption | [379.52000000000004, 684, 734.08, 24] |
| page_number | 0 | 12 | caption | [1137.28, 684, 94.72, 24] |
| nodes.shape_38 | 1 | 86 | heading | [368.1753, 319.562, 553.4247, 101.8893] |

## 使用步骤

1. 先确认材料确有本页型所表达的关系，选择`family=source-circular`及兼容variant。
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

来源为圆形逻辑图PPT模版.pptx，逐页结构见variants与来源索引。原始文件指纹及资产处理见asset-provenance.json。当前原型完成结构生成与文本测量，实际渲染和原生编辑范围以交付检查记录为准。

catalog指纹为`cb0b762dd09720f0095cb5d682a87348e0608e2f8d5fdf784ec1d4ef62f73010`，tokens指纹为`2bb967b3a61bf7a4072665f712f39ac49458d22ebe9407f269236c21adc366f3`，参数schema指纹为`add0f4b9d6bc61cd5cae5ce6d6821748442ed906b6b779cc561790e85b605ff5`。
