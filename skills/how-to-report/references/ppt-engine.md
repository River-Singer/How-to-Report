# 可持续改稿的PPT作者工程

新稿先沿[PPT Storybook](ppt-storybook.md)发现注册资产并填参数，使用`build --geometry-policy computed`或`chart-build/catalog-build`。下文含frame的scene示例保留作既有工程兼容与引擎接口说明，不是AI新稿手算坐标的入口。当前注册图表入口与能力以`chart-assets`为准。

需要跨页数据绑定、自由组合页面或持续局部修改时，使用`scripts/report_engine.py`。既有整页参数模板继续沿`scripts/report_ppt.py`使用。作者工程由内容、页面任务、对象、关系和版本组成，布局与PPTX从工程编译。

需要让AI发现对象、局部组件、完整模板及推荐组合，并在约束内拼装时，使用library和compose。三个recipe、可用child、全局profile及样例见[组件系统调用手册](ppt-component-system.md)。

需要程序计算Grid、Flex、文档流或可变节点拓扑时，使用[计算排版与拓扑](ppt-layout.md)。layout作者保留树和稳定ID，每次正常build重新测量；layouts与components topology公开实际字段和算法范围。

## 制作顺序

先沿[生成主线](reporting-method.md)形成当前内容，继承真实来源、重要图像、听众、阅读方式和有效约定。页面任务决定主证据、关系及表达。模板发现、绑定、构建、实际看图与修改围绕这些任务执行，方案选择沿当前授权。

```text
python <Skill>/scripts/report_engine.py capabilities
python <Skill>/scripts/report_engine.py library --executable true --limit 20
python <Skill>/scripts/report_engine.py library recipe.kpi-chart-explanation
python <Skill>/scripts/report_engine.py inventory
python <Skill>/scripts/report_engine.py inventory --variants --family source-house --offset 0 --limit 10
python <Skill>/scripts/report_engine.py query --variants --task "运营方法体系" --limit 3
python <Skill>/scripts/report_engine.py query --task "strategy" --limit 3
python <Skill>/scripts/report_engine.py describe strategy
python <Skill>/scripts/report_engine.py validate --input <author.json>
python <Skill>/scripts/report_engine.py facts --input <author.json>
python <Skill>/scripts/report_engine.py build --input <author.json> --output <new-project> --pptx <new.pptx>
```

资产查询按已登记元数据匹配，候选详情和原型用于确认关系、容量和来源。真实内容进入候选后再测量和查看目标页面。制作技术与检查边界沿[PPT制作](ppt-production.md)，图种、数据条件、FT九类图样及可复制调用见[图表使用场景手册](ppt-chart-usage.md)。

compose将recipe请求编译为普通作者scene，并写入brief.design_profile的id、原始字节sha256及hash_method。后续正常build自动解析并核此profile，显式tokens需要与声明一致。原请求、slot规则与调用例子沿组件手册，普通scene仍可按当前工程直接编排。

## 模板发现与适配范围

`inventory`读取当前page-catalog，默认列family摘要。`--variants`逐页列具体原型，`--family`限定一类。结果提供全库family/variant计数、当前过滤总数、offset、limit和next_offset。沿next_offset继续读取，直到其为null，即可完整遍历所选范围。catalog_revision与catalog_sha256用于核对连续读取的库身份，元数据直接来自当前catalog。

`query --variants`搜索family及variant的名称、用途、场景、关系、保留条件和字段角色。匹配采用英文词和连续中文片段的二元字符重合，返回命中字段、词项和有明确截取标记的原文摘录。结果给出total_matches与当前limit。旧的query继续返回family候选，同时记录最佳命中variant。

具体候选带family/variant身份、容量、数组数量域、文字字段数、图片及图表槽数、真实SVG原型路径与describe命令。源几何页会显示qualitative-fixed和固定源拓扑，常规数量变体会显示已登记的auto_variant_by_items。候选排序只说明词法命中程度，选型继续根据实际页面任务、关系、阅读方式、原型和内容试排判断。

`describe FAMILY --variant ID`取得完整槽位和几何合同。源页字段数与数组项目数分别按其含义使用，容量不能跨页型直接比较。固定源拓扑的文字替换沿既有字段和真实测量，改变节点数、连接和分组需要选合适原型或另行设计并核对结构合同。当前发现入口提供可检查的候选与边界，自动模板规划和通用拓扑重排继续按实际接入能力说明。

## 作者文档

顶层包含`schema_version="0.1"`、`project_id`、正整数`revision`、`brief`、`sources`、`facts`和`pages`。按任务保存`relations`、`locks`及`output_contract`。数字与跨页引用使用稳定事实ID。

以下为虚构数据示例。

```json
{
  "schema_version": "0.1",
  "project_id": "example",
  "revision": 1,
  "brief": {"audience": "项目团队", "reading_mode": "meeting"},
  "sources": [],
  "facts": {
    "total": {"value": 100, "unit": "人"},
    "enabled": {"value": 40, "unit": "人"},
    "rate": {"derived": {"op": "ratio", "args": ["enabled", "total"]}}
  },
  "pages": [{
    "id": "overview",
    "kind": "scene",
    "job": "说明启用比例",
    "notes": "本示例用于说明绑定方式。",
    "elements": [{
      "id": "overview-title",
      "type": "text",
      "frame": [56, 42, 1168, 80],
      "text": ["已启用比例 ", {"ref": "rate", "format": "percent"}],
      "style": {"font_size": 36, "weight": 700, "color": "#17334D"}
    }]
  }]
}
```

事实声明`value`或`derived`，保留单位、期间、来源和限定。受控计算支持`sum/product/difference/ratio`，参数引用事实ID。`{"ref":"id"}`保留原始值，带`format`时用于展示，`percent`将比例显示为百分数。正文可由字面文字与事实引用组成parts，图表数值引用相同事实。

模板的字符串槽可以使用明确的`{"parts":["已分配",{"ref":"allocated","format":",.0f"},"席。"]}`，在原有schema和字体测量前解析成完整文字。parts支持文字、数值、精确事实引用及嵌套parts，wrapper仅包含parts键。它生成普通文本，字体与样式沿模板槽位应用。items、series、values等结构数组按原类型保留，数字值继续直接引用事实。源页nodes及已登记图片/图表中的字符串槽使用相同规则，长度、行数和测量边界继续检查，作者副本保留原始引用。

## 页面与原生对象

`kind="template"`页通过`template={family,variant,content,config}`消费自有参数模板。`kind="scene"`页使用1280×720画布和显式elements，标题、脚注及区域由本次设计声明。

| 元素 | 主要字段 |
| --- | --- |
| text | `frame`、`text`或`runs`、`style`、`max_lines`，同一段落保留完整文字框 |
| shape | `shape`、`frame`、`fill`、`stroke`、`stroke_width`，路径使用`d` |
| chart | `frame`、`chart_type`、`categories`、`series`，支持bar、column、line、pie、doughnut，数据条件与能力状态见[图表手册](ppt-chart-usage.md) |
| image | `frame`、本地`path`、`fit`和`position`，资源复制到项目 |
| connector | `from/to`、`from_port/to_port`、线条样式及可选箭头 |
| group | `children`，用于原生组合，子对象采用页坐标 |
| component | `component`、`frame`及语义数据，自动布局后生成原生组 |

frame格式为`[x,y,width,height]`。文字style包括`font_size/font_family/weight/color/align/line_height`。形状、段落、图表数据、图片裁剪与端点按实际适配能力编译，目标编辑操作需要真实验证。

## 局部语义组件

页面任务已经确定比例分解、共同尺度比较或证据与行动对应时，可以在scene的elements中使用`type="component"`。父页面指定组件区域，组件根据事实和文字自动计算内部位置、条长、行高与连接。原生组保留组件及子项的稳定ID，数据变化后重建会重新计算布局。

```text
python <Skill>/scripts/report_engine.py components
python <Skill>/scripts/report_engine.py components partition
python <Skill>/scripts/report_engine.py components comparison
python <Skill>/scripts/report_engine.py components evidence-map
```

发现结果包含用途、字段、容量、不变量、全部样式默认值和可绑定的作者示例。数值字段接受原数值或不带format的事实引用，`value_format`控制数字展示，`unit`明确单位。文字字段支持普通文本和现有引用parts。各个segment或row使用作者指定的局部稳定`id`，子对象身份由组件ID、子项ID与用途组成，重排后继续保留身份。

| 组件 | 输入与表达 |
| --- | --- |
| partition | `total`和2–4个`segments`，每段包含`id/label/value`，可带`color/detail`。共享条形按数值比例分段，下方保留标签、数值、占比与说明。要求正总量、非负分段且分段和等于总量。可声明`total_label/unit/value_format/note/style` |
| comparison | 2–5个`rows`，每行包含`id/label/value`，可带`color/detail`。各行采用共同零起点与相同尺度。可用`baseline_id`指定基准行，以同源数值计算其他行差额，就近显示于同行。可声明`delta_label/unit/value_format/note/style` |
| evidence-map | 2–4个`rows`，每行包含`id/evidence/meaning/action`。三列分别保留证据、判断和建议动作，同行通过原生连接器相连。`columns`可明确三个标题，另支持`note/style`。实际文字测量决定各行高度 |

以下为虚构的比例分解示例，`remaining`由作者facts中的difference派生。

```json
{
  "id": "activation",
  "type": "component",
  "component": "partition",
  "frame": [60, 160, 1100, 320],
  "total": {"ref": "total"},
  "total_label": "已分配席位",
  "unit": "人",
  "segments": [
    {"id": "enabled", "label": "已激活", "value": {"ref": "enabled"}},
    {"id": "remaining", "label": "待激活", "value": {"ref": "remaining"}}
  ]
}
```

style支持`font_family/font_size/value_size/color/muted/accent/background/line/difference`。缺省字体来自当前主题`font.families.body`，字阶来自`font.sizes.body/metric`。文字、次级文字、主色、浅底和边线分别消费`text/textMuted/secondary/surfaceMuted/border`角色，差额使用`accent5`槽，分项调色板依次采用`accent1`至`accent6`。组件style和逐项color作为显式覆盖，保留其当前指定值。

`components [name] --tokens <tokens.json>`与build消费相同主题，发现结果的`style_defaults/palette/style_sources`说明当前生效值和来源。缺省使用所选模板工作区的tokens。替换主题会影响沿用默认值或角色的内容，已明确写入作者工程的颜色、字体和字号继续按其覆盖值生成。

组件区域需要容纳实际文字、数值和说明，超出数量、非法数值、未知字段、总量不符或测量溢出均定位报错，构建失败保留原产物。零值保留对应文字和占比，条形长度为零时省略该条形。主题字阶变化后按新字体重新测量，容量不足会返回具体错误。

顶层`density`支持`comfortable`和`compact`，默认comfortable。compact按字号收紧间距，并将比例分解的数值与占比放在同一行，继续使用作者指定的字号。适用场景为双栏模块分析、多状态分解和多行证据对应。区域能否容纳内容取决于实际文字测量，发现结果给出该布局差异，构建仍执行完整溢出检查。

编译收据包含组合布局模块的实际哈希，对象映射在组件根登记组件类型、合同版本和区域。输入作者副本保留原始数据与引用。生成的比较条和比例段为可编辑原生形状，数据修改通过作者工程重建。原生Chart继续沿chart元素使用其数据工作簿。跨组件端点和通用Office保存回导继续沿具体适配能力验证，组件内部连接已按相同原生组作用域输出。

编译收据与对象映射逐页记录实际`kind`，template页记录标准化后的`family/variant`，scene页记录实际组件实例数。顶层`asset_usage`汇总scene/template页数及family、variant、component使用次数。加载库身份与实际调用模板分别按这两类记录核对，发现入口的候选不会自动计为已使用。

## 逐页选型与适配

制作时先按页面问题完成[数据加工审核](ppt-visual-review.md#数据加工先于版式判断)，核口径与必要派生，确定比较基准、业务含义及主次。再用inventory了解当前结构集合，按页面任务、主要关系和真实内容检索具体variant。查看候选的用途、槽位、数量域、预览与几何边界后，将加工后的指标、文字、图表或图片映射到区域。主题决定默认身份和字阶，逐页结构沿内容需要选择。

在作者工程的`brief.layout_plan`中可以保留逐页候选、选中family/variant、原型身份、采用原因、内容映射和适配动作。该字段保存制作计划，编译器按实际page.kind和元素执行。选择自由scene时说明构图来源及采用原因，编译后的asset_usage用于核对实际模板与组件使用。

固定结构源页在已声明槽位和容量内替换内容。数量或连接关系超出其合同后，选择其他合适原型，或在案例中建立具有新身份的结构并重新测量。局部组件承担其声明范围内的自动布局。逐页原型的选择、复用范围和结构变化需要AI规划，当前发现入口给出候选及证据，完整的模板适配规划器仍需继续实现。

同一套稿可以沿用统一主题并使用多种页面原型。重复原型时核对业务关系和阅读节奏，结构差异由页面任务承担。实际成图检查覆盖内容完整、关系表达和容量适配，模板数量按实际使用记录。

## 修改与版本

patch使用JSON Pointer的`add/replace/remove`操作，并携带预期工程revision和操作ID。相同请求可以幂等续接，冲突返回错误。修改形成新文件，旧作者工程和成品保留。

```text
python <Skill>/scripts/report_engine.py patch --input <author-v1.json> --patch <operations.json> --expected-revision 1 --operation-id <stable-id> --output <author-v2.json>
```

源数字变化需要同步派生值、文案、图表和相关判断。重建受影响页后核对本版图像。手工改PPT的结果保存为新的来源版本，按实际支持的对象定位和导入能力续接。

## 有限运行与检查

作者工程实例化前先执行[制作前设计评估](ppt-design-preflight.md)，在已有brief/page.job延续采用的表达和容量约束；先正常validate和不导出PPTX的computed build，再进行目标成图。这里的`content_review`等controller检查用于绑定实际执行证据，不会自动替作者完成制作前理解、选型或美学判断，也不是生成前已自动强制的设计门禁。前置评估不能用一个事后`pass`补填冒充已执行。

```text
python <Skill>/scripts/report_engine.py control-init --input <author.json> --output <control.json>
python <Skill>/scripts/report_engine.py control --state <control.json> --expected-sha256 <current-hash> --action <action.json>
python <Skill>/scripts/report_engine.py status --state <control.json> --input <author.json>
```

控制动作包括`reserve_call/record_call/start_repair/sync_document/bind_artifact/record_check/record_finding/resolve_finding`。检查保存实际非空详情和对应产物，模型判断保留其实际方法与范围。绑定产物后，文档或PPTX变化使相应检查失效。控制记录通过预期hash、协作锁、历史和原子替换更新。

新状态的默认清单包含`build/target_render/content_review/visual_review/template-and-dataviz/editability`。其中`template-and-dataviz`沿[模板适配与数据可视化审核](ppt-visual-review.md)实际逐页检查当前方案、库内备选和数据表达，使用本版报告登记。显式配置required_checks时沿本次制作合同保留该层，已有状态继续使用其已保存清单。缺少当前必要check时控制器保持draft，AI判断及其实际证据分别按范围保存。

默认检查一次完整成图，最多两轮针对性修订与复验，具体预算沿本次任务配置。内核控制已登记作业，宿主额外模型调用按实际接入范围计量。已有Run继续承担来源、版本和接纳，控制侧车保留本次制作预算与局部状态。

ready需要当前版本必需检查齐全、已登记检查通过且阻断关闭。草稿列明具体未满足条目，失败保留可恢复工程和证据。独立评分、用户评分和工程检查分别保留身份，画面评分依据实际任务与认可样页校准。

## 内容深度与参考校准

原始表格和截图参与内容分析。除总量外，查看其中的参与人数、产出人数、产出量、资源构成和业务条件，核对期间与分母后再选择页面证据。删去这些信息会改变听众能够作出的判断。制作方案记录关键信息的去向，保留必要细节和追溯入口。不同期间或范围的数据在适用范围内表达。

每页围绕一个具体业务问题组织主回答、主要证据和解释。集合分解使用同一总量的比例结构，基准比较使用共同尺度并就近标出差额，双向共享保留两个方向及各自条件，行动建议关联其证据和观察项。形状、箭头和分组表达实际存在的关系。页面关系成立之后再调整字号、颜色和留白。

选择参考时实际查看样页，识别其信息层次、关系组织、容量和阅读方式。将真实内容代入后再验证适配。战略屋的参考价值来自各层业务内容之间的分工，使用该结构需要能够说明目标、支撑和基础的联系。缩减内容之后放大文字，会同时损失分析厚度和页面层次。

实际成图检查同时覆盖单页阅读和整稿承接。检查标题是否有页内证据，数字是否说明了范围，图形能否直接回答比较或关系问题，正文细节是否足以支持判断，结尾是否回收前面的事实。文字大小与信息密度沿阅读场景选择，必要限定放在对应数据附近，详细口径进入备查页或备注。

工程检查分别证明结构、来源、渲染和编辑操作。表达质量另行对照用户认可的参考，逐项记录可见的优劣和具体缺口。用户反馈低于模型暂评时，记录两个结果及对应版本，撤回失效的质量达标结论，重新比较参考。用户给出的局部样页分数沿该样页范围使用。

每轮修订合并同一根因的问题，优先处理影响理解、证据或主要版面的缺陷，再检查受影响页和整稿承接。停止依据为约定检查已完成、具体缺陷已处理和可供用户评价的改进成品。模型暂评分保留其评价身份，用户验收结果取得后再登记。

## 饼图、环形图与比例环

scene的chart元素支持`chart_type=pie|doughnut`，沿用`categories`和`series`。这两类图要求一个非负、无null的系列且合计大于零。每个分类代表同一整体的一个组成部分，`series[0].point_colors`可逐分类指定主题角色或颜色，缺省使用主题accent序列。环形图的`hole_size`为10至90的整数百分比，默认75。图表保留可编辑原生Chart及嵌入的Excel工作簿，起点位于12点并顺时针展开。axes和原生data_labels需要省略或关闭，分类说明可使用独立可编辑文字，`show_legend=true`可显示分类图例。

模板`chart/pie`与`chart/doughnut`通过外部图例区域显示独立的数值和占比文字。`config.show_data_labels=true`要求`config.show_legend=true`，不兼容的组合在validate阶段明确报错。隐藏全部外部说明时，将这两个开关同时设为false。

`progress-ring`从同源的value和total生成完成值、剩余值两个图表数据点，同时生成标签、中心百分比和value/total分母行。value必须有限且满足`0 <= value <= total`，total必须有限且大于零。数量可使用原始numeric ref，label和detail沿用混合文本parts。不同人群的比例各自提供对应分母，近似值通过label、detail或value_prefix显式注明。

```json
{
  "id": "activation-ring",
  "type": "component",
  "component": "progress-ring",
  "frame": [60, 160, 200, 135],
  "value": {"ref": "enabled"},
  "total": {"ref": "allocated"},
  "label": "组织激活",
  "unit": "人",
  "value_format": ",.0f",
  "percent_decimals": 1,
  "hole_size": 75,
  "style": {"font_size": 12, "value_size": 20}
}
```

percent_decimals为0至4的整数，默认1。0与全量的中心文字分别显示`0%`和`100%`。value_format沿用数量格式，unit位于分母行末尾。可选value_prefix为字符串，设置`"约"`后在分子前显示近似身份，图形和计算继续消费原数值。detail位于分母行下方，实际文字测量决定可用圆径，容量不足返回溢出错误。style沿现有主题tokens和显式字号覆盖，style.accent控制完成段，style.background控制剩余段。

比例环的chart与plot默认透明，环孔和外框显示所在页面区域的底色。可选chart_background可使用主题角色、hex或`none`显式覆盖。普通scene图表沿既有白底默认，需透明时设置style.chart_area_fill和style.plot_area_fill为`none`或`transparent`，这两个字段也支持主题角色。SVG与原生图表使用相同数据、颜色和背景。

比例环的标签、中心百分比和分母行为独立可编辑文字。作者facts变化后重建会同步图表和文字，在Office内仅修改图表工作簿时，需要同步修改这些独立文字。发现入口`components progress-ring`返回当前完整字段和示例。

## 全局文字规范与段落流

`report_engine.py typography [--tokens PATH]`公开当前所有文字角色、完整解析样式、单位和覆盖顺序。文字沿既有font.sizes、weights、lineHeight及families取得基础值，font.textStyles可补充具名角色。新增角色通过base_role继承已有角色，未知base和继承循环拒绝。以下为项目可采用的角色定义，具体数值继续来自所选profile。

```json
{
  "bodyStrong": {"base_role": "compactBody", "weight": 700},
  "metricCompact": {"base_role": "heading", "weight": 700}
}
```

优先级依次为基础font tokens、base_role、当前角色textStyles、元素显式style及run的weight/color。style支持font_family、font_size、weight、line_height、paragraph_gap、insets、align、vertical_anchor和color。font_size、paragraph_gap及四边insets使用SVG px，原生字号pt按px×0.75换算。line_height是字号倍数。insets按left/top/right/bottom排列，vertical_anchor为top、middle或bottom。PowerPoint原生字重沿400与700两档承载，100至500归为常规、600至900归为粗体。默认角色使用同一中文字体的Latin和EA字形，显式字体栈继续沿现有解析规则。

scene文字用role引用规范，缺省body。旧作者的开放语义role若未登记文字样式，会沿body显示并保留原语义标记。新明确text_roles及base_role保持严格校验。SVG记录data-htr-text-role、data-htr-semantic-role、data-htr-resolved-style和显式覆盖，供全稿属性核对。原生主题引用需要解析其major/minor字体后核对实际字体。

普通text中的换行保留，缺省paragraph_gap为0。显式在其role或style配置paragraph_gap时，相邻换行段之间增加该间距。需要明确逻辑段落时使用paragraph-flow，数组中的每项为独立语义段，段内仍可正常折行。

```json
{
  "id": "decision-copy",
  "type": "component",
  "component": "paragraph-flow",
  "frame": [60, 180, 350, 300],
  "role": "compactBody",
  "style": {"paragraph_gap": 12, "insets": [16, 16, 16, 16], "vertical_anchor": "top"},
  "paragraphs": [
    {"id": "observation", "text": "当前观察"},
    {"id": "judgment", "role": "bodyStrong", "text": "后续判断"}
  ]
}
```

paragraph-flow支持1至20段，每段具有稳定id、可选role和style，text与runs二选一。runs沿文字run的text/weight/color合同。共用insets和paragraph_gap放在flow的style中，各段按同一顶端锚点自动堆叠，首段前和末段后各保留声明内边距。paragraph_gap仅作用于数组项之间，段内普通换行与自动折行均按line_height推进，子文字的paragraph_gap固定为0。各段的独立字号、行高和字重参与相同测量函数，超高返回容量错误。导出为一个原生组内的可编辑文字框。

数据组件通过text_roles按用途选择label、value、detail、percent和note，默认分别为body、metric、caption、caption和caption。比例环的中心使用value，分母使用detail。比较数字使用value，差额使用detail，比例分解的百分比使用percent。各用途沿角色取得完整样式，显式style.font_size继续覆盖文字，value_size覆盖value。图表通过text_roles选择base、axis、legend和data_label，默认body及caption，已存在的显式字体与字号参数继续作为覆盖。

模板图表在font.textStyles声明dataCaption时，图例与数据标签沿该角色，饼环外部的分类、数值和占比说明也沿该角色。SVG和原生输出使用相应的角色颜色，重要读数可以与注释caption保持独立用途。省略dataCaption的profile沿既有caption默认及轴图预览文字角色处理。

测量、scene文字和模板carrier使用同一角色解析与文本测量。原生文字保留相同行距、段前间隔、四边内边距、水平及垂直对齐。段间距通过下一段的space-before承载，完整框与原生noAutofit继续保留。实际目标成图仍需要查看，角色和属性检查记录各自覆盖范围。

图表的SVG预览与原生Chart共用文字的字体、字号、字重和颜色。图表预览中的轴、图例及数据标签位置沿各自绘图几何安排，预览文字的段落和框体布局依该图表实现。原生Chart的文字样式实际下发行距、段距、四边内边距、水平及垂直锚点，各属性按原生图表结构核验。
# 页用途与内容观察

正常build会在作者工程写入`content-diagnostics.json`，收据的`content_diagnostics`记录文件摘要与是否需要审阅。该文件面向作者与审核者，内容不会插入PPT。每页可选`intent`与既有`job`共同说明页型和具体任务；支持值为cover、section、summary、analysis、comparison、process、architecture、decision、appendix、demo。recipe请求同样保留intent，旧稿不要求补齐才能构建。

程序观察文字测量矩形并集占画布比例、真实输入的数据记录数、拓扑节点/边及重复标签；装饰容器不算内容。30%画布以上而只有最多3个节点/2条边的无内部布局拓扑，以及分析/比较/决策页只剩最多一个正文块且无图表、图像、图关系，会产生可追溯审阅提示。这些阈值仅用于定位可能问题，不判断业务价值，不自动补写或改版，不产生质量分数。封面/章节过渡/demo免于稀疏警示。模板未提供展开scene时不伪造密度估计。实际内容质量继续执行独立内容及模板/数据可视化审核。

