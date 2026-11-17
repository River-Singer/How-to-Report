# PPT计算排版与拓扑

先完成页面的业务问题、证据与关系，再选择布局。`kind=layout`保留作者布局树，每次正常build按当前facts、profile和文字重新计算空间。AI填写容器、顺序、间距、尺寸约束及内容，叶元素不用填写frame。既有scene及template继续使用自己的合同。[作者工程](ppt-engine.md)、[组件系统](ppt-component-system.md)

新制作的一切排版和布局依靠算法和数学。正常CLI build默认`--geometry-policy computed`，接受layout树、可信参数模板及可重新执行的recipe_source。手写scene坐标会被拒绝并给出迁移建议。复现历史产物时显式使用`--geometry-policy legacy-replay`；收据会记录该身份。底层Python SDK为旧调用保留legacy-replay默认，调用者必须显式传`geometry_policy="computed"`才能声明计算制作。

## 从正常入口发现和调用

```text
python <Skill>/scripts/report_engine.py layouts
python <Skill>/scripts/report_engine.py layouts grid
python <Skill>/scripts/report_engine.py components topology
python <Skill>/scripts/report_engine.py library component.topology
python <Skill>/scripts/report_engine.py validate --input <author.json>
python <Skill>/scripts/report_engine.py build --input <author.json> --output <new-project> --pptx <new.pptx>
```

`layouts [row|column|grid|leaf]`直接读取求解器的字段、默认值、限制和示例；`components topology`直接读取拓扑实现的输入合同。两者与实际编译共用Python合同，不维护另一份可漂移的JSON Schema。[可运行合成样例](../assets/design-system/examples/computed-layout.json)包含文档流、Grid及节点拓扑，用于接口教学。

作者页使用`kind: "layout"`、`layout_version: "0.1"`、`layout: {根节点}`。节点有全稿唯一id。叶为`type: "leaf"`，其`element`保存text、shape、image、chart或component参数；element没有另一个id、frame或坐标。生成对象继承叶id，稳定ID可继续用于关系、patch和对象映射。非文字需要声明height、aspect_ratio或由容器明确分配尺寸。

```json
{
  "id": "overview", "kind": "layout", "layout_version": "0.1",
  "layout": {
    "id": "content", "type": "column", "padding": [48, 36, 48, 30], "gap": 20,
    "children": [
      {"id": "headline", "type": "leaf", "element": {"type": "text", "role": "title", "text": "本页判断"}},
      {"id": "evidence", "type": "leaf", "element": {"type": "text", "text": {"ref": "evidence-copy"}}},
      {"id": "comparison", "type": "leaf", "height": 260,
       "element": {"type": "chart", "chart_type": "column", "categories": ["甲", "乙"],
                   "series": [{"name": "数量", "values": [12, 18]}]}}
    ]
  }
}
```

事实引用使用现有同源facts。`evidence-copy`必须在作者facts中声明。使用report-14pt profile可获得14pt正文、最低9pt、正文#333333及注释#A6A6A6；样例已声明该profile的原始字节身份，更新profile后按现有版本方法更新作者身份。默认自动样式使用纯色，渐变为最低设计偏好；当前布局surface不接受渐变。该偏好适用于当前自动默认，尚无通用设计评分搜索器。

## 实际计算范围

| 类型 | 顺序与计算 |
| --- | --- |
| column | 已知宽度下测量文字及子容器高度，再按输入顺序放置；正文变长会推动后续节点 |
| row | 先分配宽度，再按实际宽度重测文字高度；grow、shrink经有界freeze/clamp分配，遵守min/max及文字最小高度 |
| grid | 先列宽后行高，按输入顺序行优先放置；支持正数px、auto及`{"fr": 正数}`轨道，缺省行按内容测高 |

尺寸和间距使用SVG px，PPT字号沿px×0.75转换。padding按left/top/right/bottom排列，也支持单个非负数。width/height及basis默认为auto，grow/shrink默认0，align默认stretch，justify默认start。需要分配剩余空间时显式设置grow或fr；需要收缩时显式设置shrink。auto宽按内容偏好处理，不能假定其等同浏览器CSS行为。

容器支持gap、padding、align、justify，以及可选surface背景，背景生成稳定的`节点id--surface`形状。容器本身主要承担空间计算，叶对象默认同scope平铺，局部组件保留自己的原生group。文字复用同一字体角色、行高、内边距和DrawingML估算器；超容量会返回诊断，不自动缩字、删文或拆页。节点、深度及轨道上限以layouts返回的limits为准。当前不支持百分比、span、wrap、subgrid、绝对定位及语义自动拆页。

底部对齐的layout文字会按同一运行时可见下降部计算最小底部安全内边距。作者已留足空间时保留原值，空间不足时只在求解场景写入有效insets，原作者树保留原值。布局报告的computed_text_insets记录请求值、有效值和计算原因，实际字号与行距保持作者样式。

### 组件内在尺寸与自动小多图

`leaf.sizing="intrinsic"` 当前仅支持 `progress-ring`。作者省略 `height`，程序按实际格式化比例、字体角色、完整标题、分母与 detail 测量自然高度。环内数字的包围矩形必须落入圆孔，由矩形对角线及 hole_size 计算最小直径。文字变长增加文字槽及整体高度，不单独缩小该环或字号。没有启用 intrinsic 的现有显式高度/长宽比继续沿旧合同；其他组件尚无内在尺寸适配器，不能据此宣称所有图表都会自动测高。

```json
{
  "id": "ratios", "type": "grid",
  "columns": {"auto_fit": "content", "max_columns": 5},
  "uniform_components": true, "column_gap": 16, "row_gap": 12,
  "children": [
    {"id": "ratio", "type": "leaf", "sizing": "intrinsic",
     "element": {"type": "component", "component": "progress-ring",
       "value": 25, "total": 100, "label": "样本／总体",
       "text_roles": {"label": "body", "value": "heading", "detail": "body"}}}
  ]
}
```

自动列数从 max_columns（默认 12，且不超过子项数）向下枚举。各候选都在真实列宽重测内容，选择所需总高度最少的可行方案，高度相同选较多列；确定的父容器高度仍是容量上限。可断行中文的整行偏好宽度不是硬下限，不可断词和环内数字必须可读。`auto_fit` 也可以是正数，表示最小轨道宽度；此模式可用于已有非 intrinsic 叶对象。自动列数不能同时指定 rows，末行空位不拉伸成更大的图。

`uniform_components=true` 要求直接子项都是 intrinsic 环，且 hole_size 相同。算法取同组最大环径及各类文字槽高度，使所有行的实际环径、标题、分母与 detail 位置一致。`row_gap`/`column_gap` 默认为 `gap`，管理组件之间的间距；文字行距及段距仍由字体规范的 `line_height`/`paragraph_gap` 管理，两者不能互换。

内在高度还包含末行文字的可见下降部安全留白 `bottom_padding`，复用现有运行时包络并扣除已有底部 inset；同组取最大值。它由测量器计算，不是作者填写的固定补偿值，也不改变旧显式 frame 组件的行为。DrawingML 行进高度与保守可见包络的口径分别保留，不降低质量检查阈值。

固定尺寸对应显式 width/height；hug 对应省略高度后的实测自然高度；fill 沿已有 grow/fr 分配外部空间。填充外框不会放大 intrinsic 环或缩小文字。若内容在一列或父级高度仍放不下，返回节点路径和容量错误，不自动删项、缩字或分页。

`layouts`、`components progress-ring` 可发现上述字段和支持范围。求解报告记录 `component_intrinsic` 和 `grid_selection`，求解场景中的 `computed_layout_metrics` 由算法写入，作者输入不可指定。测量采用当前 DrawingML 估算器，不等于 PowerPoint 实际成图；仍需目标软件走查。[可直接 build 的内在尺寸样例](../assets/design-system/examples/intrinsic-small-multiples.json)支持事实和 detail 变更后重排。

## 计算拓扑

使用`type: "component", component: "topology"`，在scene中声明frame，或放进layout叶让求解器提供frame。`layout`选择tree、layered、radial、cycle或arch，nodes和edges保存参数化节点及关系。拓扑根据文字及可用空间计算原生形状、标签和同group连接器，继承当前tokens。树核父子关系，layered计算有向层级，radial/cycle按圆周分配，arch按椭圆弧计算。

arch的可选interior接受同一种布局树，在弧内安全矩形中调用相同求解器，可继续放Grid、文字及普通组件。interior首版禁止递归topology。可选实色弧带及标记能力以components topology返回的合同为准。首版连接器为原生直线，可声明箭头；不声称实现任意折线路由，穿过非端点节点或不能安全容纳时明确失败。

## 单图标发现与使用

```text
python <Skill>/scripts/report_engine.py icons --offset 0 --limit 20
python <Skill>/scripts/report_engine.py icons <key>
python <Skill>/scripts/report_engine.py library --kind icon --limit 20
python <Skill>/scripts/report_engine.py library icon.<key>
```

返回独立SVG、预览、源页及shape ID。847个源图标按原PPT逐项保留，另有24个兼容别名；列表分别计数，不把别名当作新增源图标。未核语义的图标保留原页和shape ID键，通过预览选择，不能凭图形编号猜业务含义。template中已有icon_key槽可直接使用这些键，并继承主题色；后端将内联矢量路径转为原生几何。自由layout中可以用普通image叶引用返回的包根相对asset_ref，按library详情中的usage传`--assets <Skill目录>`，该方式属于SVG图片对象。两种输出的编辑能力分别披露。

## 修改、收据与检查

正常JSON Pointer patch可以修改facts、text或布局参数，生成新revision。新作者仍保留布局树，随后build会重新求解。新compose结果保存recipe_source；计算模式每次按当前facts和tokens重新执行该请求的有限算法，忽略缓存elements。修改recipe内容时patch recipe_source下的slot，修改自由布局时patch layout树。早期只保存scene的compose作者可从原请求重新compose，或以明确历史身份复现。recipe仍使用其有限slot分配，不声称具有通用文档流。

项目保留`inputs/presentation.project.json`原树，并逐layout页输出`layout/*.report.json`与`layout/*.scene.json`。报告记录节点frame、测量范围、实际算法版本及bounds；scene记录当前展开后的原生对象。两者携带source_page_id、作者/facts/tokens哈希、revision和编译源身份，文件哈希进入engine-receipt及object-map。topology的计算报告保留在生成group的metadata中。

CLI容量或语法失败返回`valid: false`、`error`及实际可用的diagnostic，包括node_id、path、axis、available、required、overflow_px及建议。所有页成立后再暂存发布，失败不会发布残缺项目。实际PPT成图、文字编辑、图表工作簿和整组移动继续按目标操作复核；工程计算通过不等于用户质量验收通过。
