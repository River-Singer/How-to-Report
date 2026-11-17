# PPT全局色彩标准

配色是作者工程的全局变量。AI选择已注册的`palette_id`，继续提供内容、数据和关系；engine解析语义颜色、计算几何并输出。色卡不承担听众分析、数据解释或汇报结论判断。

## 查询与调用

```text
python <Skill>/scripts/report_engine.py palettes
python <Skill>/scripts/report_engine.py palettes ant-business
```

正常作者工程及recipe请求写`brief.palette_id`。`chart-build`请求写顶层`palette_id`，随后自动转入作者工程。值为注册ID；未知ID、非字符串与路径均拒绝，不能悄悄回落到默认主题。通过正常`build --geometry-policy computed`生成。项目保存实际`tokens.json`、请求、主题ID、主题资源摘要和编译收据，修改配色必须重新构建。

Storybook可以选择全局主题并下载参数请求；预览是先前真实生成的实例，修改选择不会把静态图片伪称为已重新成图。

## 五组注册配色

| ID | 色卡 | 主色 | 辅助色 | 强调色 | 来源 |
|---|---|---|---|---|---|
| report-default | 报告蓝 | #153653 | #0756B8 | #BC681A | 当前report-14pt保持不变 |
| ant-business | 商务蓝青 | #0050B3 | #08979C | #D48806 | [Ant Design色彩](https://4x.ant.design/docs/spec/colors) |
| carbon-teal | 青绿琥珀 | #005D5D | #1192E8 | #B28600 | [Carbon数据可视化色卡](https://www.carbondesignsystem.com/building-blocks/data-visualization/color-palettes) |
| carbon-indigo | 靛紫科技 | #6929C4 | #002D9C | #B28600 | [Carbon数据可视化色卡](https://www.carbondesignsystem.com/building-blocks/data-visualization/color-palettes) |
| nord-report | 北欧蓝金 | #2E3440 | #5E81AC | #EBCB8B | [Nord色彩体系](https://www.nordtheme.com/docs/colors-and-palettes/) |

以上名称、语义分配、色序和浅色衍生均由本项目定义，不是来源网站发布的官方PPT主题。资源内逐组保留出处及派生关系。

## 颜色角色与优先级

| 角色 | 规则 |
|---|---|
| body / text | #333333，80%黑；正文、关键数据和图表轴标签 |
| muted / textMuted | #A6A6A6，约35%黑；允许的设计范围是#999999至#B3B3B3，限次要注释 |
| primary / secondary / tertiary | 标题、结构分组和主要图形；随全局配色变化 |
| accent / accentSurface | 重点色块、线和浅底；浅金等强调色不直接承担小字号正文 |
| surface / surfaceMuted / border | 白色主底、按主题派生的浅底与边界 |
| success / warning / danger | 固定#198038 / #B28600 / #C21E2B，不因选漂亮色卡而改变风险含义 |
| positive / negative / neutral | 定量正负方向及中性；它们不自动代表业务好坏 |
| categorical | 六个分类色，按系列索引稳定分配；还应提供标签，不能仅靠色差辨别 |
| sequential | 数量顺序色阶；每一个数据图元使用独立实色填充 |
| diverging | 相对零点的负向—中性—正向色阶；零点位于中性，正负范围分别计算 |

顺序为：先验证基础profile，再应用全局配色，最后解析对象语义角色。遗留对象显式指定的HEX固定色保留；新内容应引用角色而非随处散落HEX。未选配色和明确选择`report-default`都保持已有tokens及SVG视觉结果。选配色不会修改字号、字体、段落和布局约束。

分类图使用`categorical`；矩阵、地图数量和等值线使用主题色阶。空间热力图按实际阈值区间取色，图例和图块共享同一色表；跨零数据用发散色阶。瀑布、偏差填充及蜡烛涨跌使用方向颜色。所有填充保持实色，不生成渐变对象。

## 对比度与边界

每个色卡返回按sRGB相对亮度计算的白底、白字及正文色对比度。白底#333333约12.63:1，#999999约2.85:1，#A6A6A6约2.43:1，#B3B3B3约2.10:1。注释灰按用户偏好保留，因此不能声称整个主题达到统一无障碍标准，关键信息不得降为注释灰。

选主题后，彩色图块内的小标签根据实际对比度选择：优先#333333，必要时反白；两者仍不足4.5:1时使用100%黑作为数据内嵌标签例外。普通白底正文仍为80%黑。这只验证颜色对比，不替代字号、密度、色觉差异和实际投影检查。

全局主题覆盖engine的语义颜色。原生PPT保真提取、嵌入图片、原始固定锚点素材内部固定填色不自动重着色；如需改色，应先增加明确的语义适配器及来源差异记录。不能通过强行全图替色破坏原样还原证据。
