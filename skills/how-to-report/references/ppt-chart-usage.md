# 数据图表与使用场景

先明确要让听众读出的关系，再选择图表。材料、统计口径与必要派生按[业务数据分析](business-data-analysis.md)处理，实际成图按[模板与数据表达审核](ppt-visual-review.md)复验。统一发现、推荐组合及profile调用见[组件系统手册](ppt-component-system.md)。

## 当前注册资产入口（2026-11-16）

FT九类的68个图样现有独立数据合同和算法入口，详见[注册图表手册与逐项限制](../assets/design-system/chart-assets/README.md)。先运行`report_engine.py chart-assets <chart-id>`取得当前schema、示例和使用边界，再用`chart-build --request <request.json> --output <new-project> --pptx <new.pptx>`。输入为asset/data/options，位置与几何由engine计算，浏览和取用见[PPT Storybook](ppt-storybook.md)。

这68项输出为可编辑形状和文字，修改数据需引擎重建；它们不等同于下述5种Excel链接原生Chart入口，也不能仅凭注册状态宣布所有Office环境和业务输入都已验收。新算法包含明确限定的分箱、KDE、ECDF、网络与区域地理绘制；回归、预测和缺失业务事实不因此自动产生。

下面保留的是原有Chart/模板入口的兼容手册和扩展前能力快照。其FT表格中的“底层/规划”描述旧接口，不是新`chart-assets`入口状态；新制作优先查实时注册合同，不能据旧表退回手画SVG。

## 既有原生Chart入口的数量与兼容边界

公共作者入口有5种原生图表，另有3种量化语义组件。模板variant、同图的多系列和布局变化分别计数。

| 图种 | 正常入口 | 当前子类型与边界 | 常见使用问题 |
| --- | --- | --- | --- |
| 柱状图 column | scene chart、chart模板 | 单系列或多系列并列柱。同一category轴和主value轴，条长含零点 | 各业务类别的规模差多少，几期离散总量如何比较 |
| 横向条形图 bar | scene chart | 单系列或多系列并列横条，同轴、含零点，可调类别顺序 | 长名称类别的排名、规模或正负差额比较 |
| 折线图 line | scene chart、chart模板 | 单线或多线、同轴、等距有序类别。null留缺口并断线 | 同口径、等间隔观测的变化方向及拐点 |
| 饼图 pie | scene chart、chart/pie模板 | 一个非负数列，合计大于零，无null，组成项互斥 | 同一个整体由哪些部分组成，少量主要部分占多少 |
| 环形图 doughnut | scene chart、chart/doughnut模板 | 与pie同数据条件，孔径10–90，默认75，起点12点并顺时针 | 组成关系与一个核心总量或占比共同展示 |

scene图表的categories和series没有统一硬数量上限，仍要满足文字、轴、图例和数据标签的实际容量。当前chart模板接受1–6个类别、1–2个系列，pie/doughnut收窄为1个系列。模板有side、wide、pie、doughnut四种版式，详细字段见[chart家族](../assets/templates/business-blue-v1/docs/families/chart.md)。

| 量化组件 | 正常入口 | 必要输入与不变量 | 适用场景及编辑能力 |
| --- | --- | --- | --- |
| partition 比例分解 | scene component | 正总量，2–4个非负分项，分项合计等于总量 | 同一整体的结构和余量。按值生成原生分段条、文字与组，数据变化后由引擎重算 |
| comparison 基准比较 | scene component | 2–5个非负数值，至少一个为正，可指定其中一项作baseline | 同单位、同口径的规模与基准差额。原生条形和文字共用零点，差额由相同输入计算 |
| progress-ring 比例环 | scene component | total大于零，0≤value≤total，各比例有自己的分母 | 完成率、激活率、渗透率。原生doughnut及Excel加独立可编辑标签、中心百分比与分母 |

paragraph-flow和evidence-map分别组织段落及证据到行动，另有流程、辐射和树等关系模板。这些属于表达或拓扑结构，图种数量单独统计。

折线柱状组合combo已存在于底层原生后端，公共scene及chart模板仍待接通。当前普通scene中的series保持同图型，series.type不会建立混合图。stacked、100% stacked、secondary axis等也不能由当前普通scene字段直接启用。需要双指标时可使用明确分离的小图，并核对单位与尺度。

## 选图前的数据条件

每张图先说明业务问题、值/单位、期间或时点、人群与筛选范围、维度和粒度、必要分母、缺值、约值及来源。可见读数与图形都引用同源facts，派生结果保存公式和输入。

- 比较规模时确认可比口径。柱条从零开始，多图并置比较时显式声明共同尺度。负值需要保留零点和正负方向，comparison组件的输入域仍限非负。
- 排序需要按实际数值排列categories与每个series的对应值，图表不会自动替作者完成业务排序。排名折线等专用图样保留各自状态。
- 时间变化需要真实序列。当前line按等距类别排布，只适合等间隔观测或明确的顺序比较。不等时间间隔不能靠日期标签让本入口变为连续时间轴，line显式date轴当前会拒绝。
- 部分与整体需要同一分母、互斥且穷尽的集合。重叠的功能用户、不同人群比例、不同期间累计和不能合成一个饼。比例差显示百分点，相对增幅显示百分比，文字说明其计算基准。
- 缺值与零分别保留。柱/条/线接受null，所有系列各须至少一个有限数值。pie/doughnut及三个量化组件要求其数值完整。缺值的补齐、平均或外推需要明确方法和来源。
- 分布、相关、流量和空间数据各需要专门输入。均值不能代替原始分布，两个总量不能推导相关性，节点数量不能代替流量，地区名称与总量还需要可靠地理匹配。

facts目前直接支持sum、product、difference、ratio。注册图表的分箱、密度和区域投影按各自schema执行；回归、预测及统计置信区间不能靠模型手画后声称为确定性统计结果，fan-chart仅显示调用方提供的区间。

## FT九类关系目录与旧接口状态快照

目录及英文名称参考Financial Times Visual Journalism Team的Visual Vocabulary。分类沿用户指定海报，9类共有74个分类条目，跨类重复去重为66种图样。交互网站另有两个扩展项，下方独立列出。5个公共chart_type可承载其中10种表达，包括作者预先排序和多系列并列，不能将其理解为新增10种自动recipe。[FT海报与项目说明](https://github.com/Financial-Times/chart-doctor/tree/main/visual-vocabulary)、[英文海报](https://raw.githubusercontent.com/Financial-Times/chart-doctor/main/visual-vocabulary/Visual-vocabulary-en.pdf)

表中“可调用”表示现有公共chart可表达，需要满足该列的数据条件。“底层”表示已有原生后端，公共作者合同或完整预览仍待接。“规划”表示命名图样的专用数据、算法或布局仍待实现。以下场景与限制为本项目整理，不能由候选primitive推定完整图样可用。

### 偏差 Deviation

回答相对零点、目标或基准偏离多少。非零基准先以同源公式求偏差，并保留原值及基准。

| 图样 | 状态 | 适用问题与关键条件 |
| --- | --- | --- |
| 发散条 Diverging bar | 可调用bar | 各项盈亏、净增减或目标差额，正负方向围绕共同零点 |
| 发散堆积条 Diverging stacked bar | 底层bar | 正向/中性/负向调查分布，需规定中性项摆放与总样本 |
| 脊柱图 Spine | 规划 | 两项相对构成及类别规模，明确宽、高分别编码什么 |
| 盈余/赤字填充线 Surplus/deficit filled line | 规划 | 时序相对基线或两序列之间的差，交点、分段与填色域需计算 |

### 相关性 Correlation

回答观测对象的几个变量怎样共同变化。每个点需要成对或成组观测，相关关系不能直接推断因果。

| 图样 | 状态 | 适用问题与关键条件 |
| --- | --- | --- |
| 散点 Scatterplot | 底层scatter | 两个连续变量的关系，需真实X/Y坐标、单位及观测粒度 |
| 柱线组合 Column + line timeline | 底层combo | 同期数量与比率并看，明确主/次轴、单位和缩放，不凭曲线贴近判断相关 |
| 连线散点 Connected scatterplot | 底层scatter | 两变量关系随顺序变化，每点有X/Y及顺序，连线方向需要可辨 |
| 气泡 Bubble | 底层bubble | X/Y之外增加第三个量，以面积编码，负size和面积尺度需明确 |
| XY热力图 XY heatmap | 规划 | 两维交叉强弱，需单元格聚合规则、统一色阶和缺值表示 |

### 排序 Ranking

回答位置和名次。排序必须同步重排类别、系列与对应注释，保留并列名次规则。

| 图样 | 状态 | 适用问题与关键条件 |
| --- | --- | --- |
| 有序横条 Ordered bar | 可调用bar | 长名称类别排行，作者按值预排序，保留同一零点 |
| 有序柱 Ordered column | 可调用column | 少量短名称排行，作者预排序，类别标签仍可读 |
| 有序比例符号 Ordered proportional symbol | 规划 | 重量级差异较大的排行，以面积表示量，不能按半径直接映射值 |
| 条带点 Dot strip plot | 规划 | 多组紧凑位置比较，点重叠、共同数轴和排列规则需处理 |
| 坡度图 Slope | 规划 | 两端名次或值的变化，需要实体一对一匹配、同尺度及防碰撞标签 |
| 棒棒糖 Lollipop | 规划 | 用位置强调类别值，需细杆零点、端点及读数空间 |
| 排名变化 Bump | 规划 | 多期间名次升降，需秩变换、同名实体和并列规则 |

### 分布 Distribution

回答样本怎样散布、集中、偏斜或分化。需原始观测或可追溯的频数/分位统计，不能只用总量和均值构造分布。

| 图样 | 状态 | 适用问题与关键条件 |
| --- | --- | --- |
| 直方 Histogram | 底层histogram | 连续量频数分布，需样本及明确分箱边界、宽度和极端值策略 |
| 点图 Dot plot | 规划 | 类别的点估计、范围或变化，需明确每个点/线代表的统计量 |
| 条带点 Dot strip plot | 规划 | 展示个体观测，需处理同值重叠且不制造虚假数值偏移 |
| 条码 Barcode plot | 规划 | 高密度个体位置分布，需真实位置和可辨识的高亮策略 |
| 箱线 Boxplot | 底层box_whisker | 多组中位数、四分位和离群点比较，需统一分位数/须线定义 |
| 小提琴 Violin plot | 规划 | 分布形状和多峰，需密度估计算法、带宽及样本量 |
| 人口金字塔 Population pyramid | 规划 | 两人群按同年龄段/分组对称比较，镜像轴仍保留真实非负人数 |
| 累积曲线 Cumulative curve | 规划 | 随阈值累积的数量/比例，需排序、累计及分母，不混同累计占比与原始量 |
| 频率多边形 Frequency polygons | 规划 | 多组分布形状比较，需共同分箱及频数/密度归一化 |
| 蜂群 Beeswarm | 规划 | 保留每个观测并减少重叠，需碰撞算法，偏移方向不能代表额外变量 |

### 时间变化 Change over Time

回答何时、怎样变化。明确时间粒度、观测间隔、缺口和累计/期间值。当前普通line的等距限制继续适用。

| 图样 | 状态 | 适用问题与关键条件 |
| --- | --- | --- |
| 折线 Line | 可调用line | 等间隔同口径序列，保留null断口和必要的期间标签 |
| 柱 Column | 可调用column | 各期离散总量，时间顺序固定，柱从零开始 |
| 柱线组合 Column + line timeline | 底层combo | 同期两项有关指标，轴、单位及日期映射分别声明 |
| 坡度 Slope | 规划 | 少量实体的两期变化，实体匹配和标签碰撞需处理 |
| 面积 Area chart | 底层area | 强调随时间的量，零基线及标准/堆积含义需明确 |
| 蜡烛 Candlestick | 底层stock | 各期OHLC价格，需同标的和日期；当前底层合同为4条OHLC数列 |
| 扇形预测 Fan chart | 规划 | 预测区间随时间扩展，需预测方法、各区间概率及嵌套顺序 |
| 连线散点 Connected scatterplot | 底层scatter | 两变量轨迹随时间变化，数值坐标和先后标记保持可读 |
| 日历热力 Calendar heatmap | 规划 | 每日规律与异常，需日历、缺日、时区和统一色域 |
| 区间时间轴 Priestley timeline | 规划 | 事件起止、重叠和持续，需真实起止点及时间映射 |
| 圆点时间轴 Circle timeline | 规划 | 事件时点和规模，位置代表时间、面积代表量，重叠需处理 |
| 纵向时间轴 Vertical timeline | 规划 | 沿纵向展开事件，明确真实时间尺度与纯顺序叙述的区别 |
| 震波 Seismogram | 规划 | 高频正负波动，需共同基线、观测间隔和合理采样 |
| 流图 Streamgraph | 规划 | 多组成序列的体量变化，需共同粒度、堆积顺序和中轴算法 |

### 量级 Magnitude

回答规模有多大及差多少，标签同时保留单位和比较范围。

| 图样 | 状态 | 适用问题与关键条件 |
| --- | --- | --- |
| 柱 Column | 可调用column | 短名称类别规模，零基线及实际数值 |
| 横条 Bar | 可调用bar | 长名称类别规模，零基线及足够标签区 |
| 成对柱 Paired column | 可调用column | 相同类别下两组同单位量，多系列默认并列，图例可辨 |
| 成对横条 Paired bar | 可调用bar | 相同类别下两组量，标签较长时使用并列横条 |
| 马赛克 Marimekko | 规划 | 组规模及组内比例共同编码，宽度、分段高度和整体面积需同源计算 |
| 比例符号 Proportional symbol | 规划 | 强调大幅规模差异，面积与值成比例，图例有明确参考量 |
| 象形 Isotype | 规划 | 用重复图标表达量，需每图标代表的单位及部分图标规则 |
| 棒棒糖 Lollipop | 规划 | 类别值的位置强调，明确杆起点及标签位置 |
| 雷达 Radar | 底层radar | 同对象多维度概貌，各维度需归一化或可比尺度，轴顺序影响轮廓 |
| 平行坐标 Parallel coordinates | 规划 | 多变量的个体模式，各轴单位、归一化和遮挡需明确 |
| 子弹 Bullet | 规划 | 当前值、目标与分区比较，需每个阈值的业务依据及共同尺度 |
| 分组符号 Grouped symbol | 规划 | 类别组中的符号数量/规模，需明确计数单位、面积编码和组间对应 |

### 部分与整体 Part-to-whole

回答整体怎样构成。层级图需树关系，包含与重叠需集合依据，变化桥接需起终值与分项可加总。

| 图样 | 状态 | 适用问题与关键条件 |
| --- | --- | --- |
| 堆积柱/条 Stacked column/bar | 底层bar/column | 组内构成及组间总量，需非负可加量及一致分项顺序 |
| 马赛克 Marimekko | 规划 | 不同规模组的组成，宽高两种编码都需清楚解释 |
| 饼 Pie | 可调用pie | 单个整体的少量互斥部分，无负值、null和重叠集合 |
| 环 Donut | 可调用doughnut | 与pie同条件，中心强调内容与分母一致 |
| 矩形树 Treemap | 底层treemap | 层级构成按面积分配，树关系及子级合计需一致 |
| Voronoi | 规划 | 不规则区域的面积构成，需面积守恒布局及可辨边界 |
| 弧形 Arc | 规划 | 弧长等编码表达比例，需确定比例映射及角度范围 |
| 网格比例 Gridplot | 规划 | 单位格子表达部分与整体，需总格数、舍入及余量规则 |
| 韦恩 Venn | 规划 | 集合交并关系，需交集原数与完整集合条件，面积正确需专用算法 |
| 瀑布 Waterfall | 底层waterfall | 起点经增减变为终点，需分项符号、累计及小计/总计身份 |

### 空间 Spatial

回答哪里、距离及区域格局。需要地理位置/边界数据、可靠匹配、投影和地理粒度，现有hub/tree不能代替地理管线。

| 图样 | 状态 | 适用问题与关键条件 |
| --- | --- | --- |
| 分级设色 Basic choropleth | 规划 | 各地区率/比例，需地区边界、可比率值及分级方案，避免人口总量冒充风险率 |
| 地理比例符号 Proportional symbol | 规划 | 地点计数或规模，需坐标、面积尺度和重叠处理 |
| 流向地图 Flow map | 规划 | 区域间流动，需起终地、方向、权重及空间路由 |
| 等值线 Contour map | 规划 | 连续空间量的等值区域，需采样、插值、等值等级和投影 |
| 等面积变形 Equalised cartogram | 规划 | 等权区域的格局，需拓扑保留、邻接及位置说明 |
| 数值变形 Scaled cartogram | 规划 | 地区面积随值变化，需变形算法及可识别的地理锚点 |
| 点密度 Dot density | 规划 | 区域计数的密度，需每点代表量及点位生成规则，随机点不能当精确地址 |
| 空间热力 Heat map | 规划 | 连续空间热点，需核密度/栅格化、带宽、权重及色域 |

### 流动 Flow

回答从哪里到哪里、转移多少、如何连接。加权流与定性流程分开，守恒、循环和方向按实际数据声明。

| 图样 | 状态 | 适用问题与关键条件 |
| --- | --- | --- |
| 桑基 Sankey | 规划 | 来源到去向的加权流，需节点、边、权重、守恒和节点顺序 |
| 瀑布 Waterfall | 底层waterfall | 从起点到终点的增减桥接，累计与总计同源 |
| 弦图 Chord | 规划 | 组间双向流量，需矩阵、方向/对称规则及弧段布局 |
| 网络 Network | 规划 | 多实体连接与结构，需节点/边/权重/方向和布局算法，定性辐射模板仅覆盖其声明拓扑 |

### 官网版本的两个补充图样

| 图样 | 状态 | 适用问题与关键条件 |
| --- | --- | --- |
| 比例堆积条 Proportional stacked bar | 规划 | 等宽组的100%结构对照，需每组单独归一化和分母。底层percentStacked可作接通基础 |
| 旭日 Sunburst | 底层sunburst | 多层级构成，需父子路径、层级顺序和父级合计规则 |

官网CSV有72个分类行，归并后62种，与上述海报并集为68种。这是版本清点，当前实现状态按每条记录核对。目录名称和分类参考FT Visual Vocabulary，按其[CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)要求保留Financial Times署名与来源，项目自己的编译器及其他资产来源分别登记。[交互版](https://ft-interactive.github.io/visual-vocabulary/)、[官网数据表](https://ft-interactive.github.io/visual-vocabulary/chartTypes.csv)

## 当前图表的可复制作者示例

以下全部为合成数据，与用户业务材料无关。保存为chart-example.json，使用当前安装Skill的正常入口。示例只引用语义文字角色，具体字体、字号和文字颜色沿所选profile。scene及组件示例将图例、关键读数和分母映射为正文角色，来源说明采用caption或项目具名的注释角色。模板示例沿其family规定的文字角色。

```json
{
  "schema_version": "0.1",
  "project_id": "synthetic-chart-example",
  "revision": 1,
  "brief": {"audience": "演示团队", "reading_mode": "meeting"},
  "sources": [],
  "facts": {
    "a": {"value": 12, "unit": "件"},
    "b": {"value": 18, "unit": "件"},
    "c": {"value": 10, "unit": "件"},
    "total": {"derived": {"op": "sum", "args": ["a", "b", "c"]}},
    "share_b": {"derived": {"op": "ratio", "args": ["b", "total"]}}
  },
  "pages": [{
    "id": "example-page",
    "kind": "scene",
    "job": "比较同周三个互斥类别的工单量",
    "elements": [
      {
        "id": "page-title",
        "type": "text",
        "role": "title",
        "frame": [60, 36, 1160, 70],
        "text": "三类工单量（件）"
      },
      {
        "id": "main-chart",
        "type": "chart",
        "frame": [120, 160, 1020, 400],
        "chart_type": "column",
        "categories": ["类别甲", "类别乙", "类别丙"],
        "series": [{"name": "工单量", "values": [{"ref": "a"}, {"ref": "b"}, {"ref": "c"}]}],
        "text_roles": {"base": "body", "axis": "body", "legend": "body", "data_label": "body"},
        "data_labels": {"show_value": true},
        "show_legend": false
      }
    ]
  }]
}
```

```text
python <Skill>/scripts/report_engine.py capabilities
python <Skill>/scripts/report_engine.py typography --tokens <profile.json>
python <Skill>/scripts/report_engine.py validate --input <chart-example.json>
python <Skill>/scripts/report_engine.py facts --input <chart-example.json>
python <Skill>/scripts/report_engine.py build --input <chart-example.json> --tokens <profile.json> --output <new-project> --pptx <new.pptx>
python <Skill>/scripts/report_engine.py query --variants --task "数据比较与结论" --limit 5
python <Skill>/scripts/report_engine.py describe chart --variant wide
python <Skill>/scripts/report_engine.py components progress-ring --tokens <profile.json>
```

普通作者示例需要14pt规范时，--tokens传入包内assets/design-profiles/report-14pt.json，用typography核其实际角色。通过compose生成的作者已声明brief.design_profile，后续build自动核对并应用。每次构建使用新的输出位置，当前作者修改沿[版本化patch](ppt-engine.md#修改与版本)。

| 从主图示例改为 | 元素改动 | 同步调整的内容与含义 |
| --- | --- | --- |
| bar | chart_type设bar | 保留真实类别，长名称给左侧标签区足够空间。多系列默认并列横条 |
| 多系列column/bar | series加入另一个完整数列，show_legend设true | 各系列同单位、同类别对应，每个values长度与categories一致。当前为并列比较 |
| line | chart_type设line，categories换真实等间隔时间标签 | facts也换为对应时点的数值，保留null，不凭类别替换制造趋势。多个系列为多条同轴线 |
| pie | chart_type设pie，data_labels设false，show_legend设true | 确认类别为同整体的互斥部分。scene原生数值标签关闭，图例为类别；需要值/占比可用chart/pie模板的外部说明 |
| doughnut | 沿pie设置并改chart_type为doughnut，可加hole_size为75 | 需要中心比例及分母时优先progress-ring，避免独立手写百分数 |

下面三个JSON分别替换elements中的main-chart对象，保留上面的facts、标题和页面外层。可根据问题改标题。frame用于演示实际容量，并非所有页面固定几何。

```json
{
  "id": "composition",
  "type": "component",
  "component": "partition",
  "frame": [100, 150, 1080, 380],
  "total": {"ref": "total"},
  "total_label": "同周工单总量",
  "unit": "件",
  "text_roles": {"label": "body", "value": "metric", "detail": "body", "percent": "body", "note": "caption"},
  "segments": [
    {"id": "a", "label": "类别甲", "value": {"ref": "a"}},
    {"id": "b", "label": "类别乙", "value": {"ref": "b"}},
    {"id": "c", "label": "类别丙", "value": {"ref": "c"}}
  ]
}
```

```json
{
  "id": "baseline-comparison",
  "type": "component",
  "component": "comparison",
  "frame": [100, 150, 1080, 300],
  "baseline_id": "reference",
  "delta_label": "差额",
  "unit": "件",
  "text_roles": {"label": "body", "value": "metric", "detail": "body", "percent": "body", "note": "caption"},
  "rows": [
    {"id": "reference", "label": "同口径参考量", "value": {"ref": "a"}},
    {"id": "actual", "label": "当前量", "value": {"ref": "b"}}
  ]
}
```

```json
{
  "id": "share-ring",
  "type": "component",
  "component": "progress-ring",
  "frame": [420, 160, 360, 340],
  "value": {"ref": "a"},
  "total": {"ref": "total"},
  "label": "类别甲占同周总量",
  "unit": "件",
  "value_format": ",.0f",
  "percent_decimals": 1,
  "text_roles": {"label": "body", "value": "metric", "detail": "body", "percent": "body", "note": "caption"}
}
```

模板页可沿相同facts，使用下面的page替换pages[0]。pie/doughnut的外部图例能显示类别、数值和占比，side/wide沿config.chart_type切column或line。content.conclusions应为当前数据支持的解释。

```json
{
  "id": "template-composition",
  "kind": "template",
  "job": "说明同周工单结构及主要类别",
  "template": {
    "family": "chart",
    "variant": "pie",
    "content": {
      "title": {"parts": ["类别乙占同周工单的", {"ref": "share_b", "format": "percent"}]},
      "categories": ["类别甲", "类别乙", "类别丙"],
      "series": [{"name": "工单量", "values": [{"ref": "a"}, {"ref": "b"}, {"ref": "c"}]}],
      "unit": "件",
      "conclusions": {"parts": ["三个类别合计", {"ref": "total", "format": ",.0f"}, "件，类别乙", {"ref": "b", "format": ",.0f"}, "件。该示例用于说明互斥构成。"]},
      "source": "合成数据，仅作接口演示"
    },
    "config": {"show_legend": true, "show_data_labels": true}
  }
}
```

## 标签、颜色、编辑及常见误用

主图应直接交代读者需要的标签、单位、分母/基准和约值。axis、legend及data_label通过text_roles消费全局规范，避免逐图写散字号和颜色。数值强调可用有语义的主题色；分类色由主题调色板及明确分组决定，相同类别跨图保持对应。

chart模板在profile定义dataCaption时，将重要图例、数据标签及饼环外部类别/读数映射到该角色。report-14pt的dataCaption继承caption字号并采用正文色，source等来源说明继续采用caption注释色。未定义dataCaption的profile沿原caption角色，具体显示仍按当前profile及实际成图核对。

pie/doughnut scene的原生data_labels省略或设false，axes省略。chart/pie和chart/doughnut模板使用独立的外部类别、数值与占比文字，show_data_labels=true要求show_legend=true，两个同时false可隐藏全部外部说明。progress-ring自动提供value/total及百分比，0和100%有对应边界处理。

普通Chart保留原生对象与嵌入Excel；partition和comparison为程序生成的原生形状及文字。progress-ring是原生doughnut与独立文字的组合。Office仅改工作簿后，独立中心百分比、分母、图例及差额文字需要同步，且数据缓存可能需要显式刷新。通过作者facts重建可保持同源联动。更长的Office文字修改需要重新检查容量，等长编辑探针不能证明任意长文都能容纳。

普通scene Chart默认白底，放在非白区域需要style.chart_area_fill及plot_area_fill设none或transparent。progress-ring默认透明，环孔沿所在区域底色。真实PowerPoint图表内部排版与SVG fallback的标签几何各有实现，字体属性同源及原生完整段落格式分别核对，最终显示按目标成图检查。

常见失败包括把+20%相对增长当成整体占比画环、把重叠用户相加画饼、对不同分母的比例用扇区大小表达总人数、为两组小图分别自动缩轴后比较条长、把长时间缺测连成连续趋势，以及为塞进页面而缩小到全局最低字号以下。应回到关系、数据条件、受支持版式与容量解决。

## 底层能力与扩展状态

底层原生运行时可识别19个canonical type。它们需要其专用payload、SVG载体、check及export，公共作者入口另有范围。

| 底层组 | type逐项 | 当前高层状态 |
| --- | --- | --- |
| 类别轴8项 | area、bar、column、doughnut、line、of_pie、pie、radar | bar/column/line/pie/doughnut已接scene；area/of_pie/radar待接公共作者合同 |
| XY 2项 | scatter、bubble | 待接公共作者合同、数值坐标和相应预览 |
| ChartEx 7项 | box_whisker、funnel、histogram、pareto、sunburst、treemap、waterfall | 底层存在专用路径，公共作者、统计/层级输入、预览及目标兼容验证分别待接 |
| 组合与股价2项 | combo、stock | 底层有独立合同，公共scene/chart模板待接。combo的多个plot和secondary axes不能由普通scene series.type替代 |

19项包含已接的5项，额外14项不能加到当前公共图种数。stacked等底层配置不单独计为高层成熟图种，3D和surface当前未实现。FT目录还包含大量没有对应Office原生type的表达，需要可计算几何、专用统计/地理算法及明确目标能力。

柱线双轴combo已有一页合成探针经过正常底层check/export、缓存及工作簿回读，并由主代理在PowerPoint16.0实际查看。该证据覆盖这一页的双轴显示，不包括编辑保存重开，也不扩展为其余底层图种的视觉验收。其公共作者入口状态继续为待接通。

每个新图样的完成条件包括数据schema、语义与算法、受控布局、公开入口、对应预览、原生或降级输出等级、同源更新、手册及实际验证。只有图样名称、底层枚举或一张示意图时，保留planned/backend-only身份。导入SVG或位图的缩放与替换、可编辑形状、原生Chart数据编辑分别说明，不能混为同一种可编辑能力。
