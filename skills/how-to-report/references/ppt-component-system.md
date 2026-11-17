# PPT组件系统与AI拼装

制作前先形成页面任务、主要证据、关系和必要限定。用library发现当前可调用的对象、组件、整页模板和推荐组合，再绑定本次事实。recipe为已登记的组合分配区域，scene支持按作者工程直接组合对象。两个入口共用文字测量、主题和原生导出链。[作者工程](ppt-engine.md)、[图表使用场景](ppt-chart-usage.md)

需要内容变长后重新排布时使用[计算排版与拓扑](ppt-layout.md)的持久layout作者。layouts发现row、column和grid，正常build每次重算；components topology发现可变节点树、分层、圆周及弧形结构。默认自动样式优先纯色，渐变为最低设计偏好。

页面任务承接[内容交接](ppt-handoff.md#制作输入)中的实际分析记录，交清业务问题、事实支持的状况、建议理由和会改变判断的未决。主值加图需要有据解释，双图需要说明比较意义，evidence-action需要说明动作回应何种原因或检验何种解释。组合器承担输入、数值域、容量和排布校验，诊断与建议依据由上游分析及独立内容审阅完成。用户允许`draft-analysis`时，可先做解释页并列补数，当前结尾按已有证据与本场用途确定。

## 层级与调用位置

| 层级 | 作用 | 当前调用位置 |
| --- | --- | --- |
| Tokens与profile | 统一字体角色、文字色、图表色、字阶、间距和画布 | profile.report-14pt，compose选择后写入作者的profile身份 |
| Primitive | text、shape、image、chart、connector、group等绘图对象 | scene的elements，用library primitive.ID查询实际合同 |
| Component | 具有数据语义和局部布局算法的块 | scene的type=component，含partition、comparison、progress-ring、paragraph-flow、evidence-map |
| Pattern与recipe | 主值加主图、双图对照、证据到行动、并列解释、阶段带、共享平台 | 当前6种recipe有compose入口；后三种为可重放的成稿设计候选，schema规定输入和数量 |
| Page template | 已有完整页面结构、Master/Layout及槽位 | kind=template页，按family/variant绑定，library读取现有catalog |
| Page与deck | 当前页的业务问题、整稿叙事与页面推进 | How-to-Report形成任务与内容，作者工程保存实际页序和采用理由 |

整页template按完整页面合同使用。要在局部区域放一个比例、比较或段落块时，从component或primitive选取。当前recipe的slot只接受下表声明的use值，完整library中的可执行对象还需符合所在slot的约束。

## 发现、查看和判断状态

```text
python <Skill>/scripts/report_engine.py library --executable true --limit 20
python <Skill>/scripts/report_engine.py library --kind component --relationship part-to-whole --limit 10
python <Skill>/scripts/report_engine.py library --kind recipe --limit 10
python <Skill>/scripts/report_engine.py library component.progress-ring
python <Skill>/scripts/report_engine.py library recipe.kpi-chart-explanation
python <Skill>/scripts/report_engine.py library profile.report-14pt
python <Skill>/scripts/report_engine.py library --kind chart-vocabulary --status backend_only --executable false --limit 20
```

library不带ID时按offset、limit分页，沿next_offset读取到null。kind可为primitive、component、template、profile、chart-vocabulary、recipe或icon。relationship按登记的关系名过滤，query按文本词项过滤，status可为high_level、backend_only或planned。带完整ID取得输入合同、限制、schema、样例及已有预览，ID以返回结果为准。

先读kind、executable和compile_contract，再读status_scope与validation。primitive、component、template及recipe分别声明自己的正常入口。profile提供主题参数。chart-vocabulary的high_level表示可用当前公共图种承载该表达，全部FT词汇条目的executable仍为false。当前5种chart_type承载10种FT表达，具体条件见图表手册。

high_level、backend_only和planned描述各自kind的实现状态。validation记录实际验证范围，preview_refs记录预览来源，user_quality_acceptance记录用户评价身份。采用前查看当前图像，并确认其数据与关系适合本页。推荐样板的视觉效果证据与语义保真证据分别记录，新图样所需数据或分支条件在材料中缺失时标记data-required，补齐有来源的输入后再实例化。[注册记录](../assets/design-system/registry.json)

## 新增成稿设计组合

`recipe.editorial-pillars`、`recipe.stage-ribbon`、`recipe.capability-platform` 已接入 compose；前两种分别用于同级解释和有序过程，第三种用于输入—共享平台—输出。语义和容量、结构原型与设计组合的选型、纯色与可重放约束见[成稿设计组合](ppt-visual-recipes.md)。正常 library 返回三者的实际示例和 SVG/PowerPoint PNG 预览。

## 三种数据与行动recipe

| recipe值 | slots与数量 | 允许的child与关键约束 |
| --- | --- | --- |
| kpi-chart-explanation | metrics为1–3项，每项id、label、value、unit及可选context。main为1个主图。explanation为1–3段，每段id和text | main接受primitive.chart、component.partition、component.comparison或component.progress-ring。主值及单位各需单行容纳，必要基准或分母放context，主图和解释实测fit |
| paired-charts-conclusion | charts恰好2个panel，每项id、title、chart、semantics。conclusion为1–2段 | chart只接受primitive.chart，chart_type限bar、column或line。semantics含unit、scope、period及scale。两图unit和显式scale相同，scale从0递增，全部系列值为有限数字且在域内，当前该recipe不接null |
| evidence-action | rows为2–4项，每项id、evidence、action、verification | evidence接受primitive.chart、primitive.image、component.partition、component.comparison、component.progress-ring或component.paragraph-flow。每行的证据、动作和复核保持对应，实际文字和图表决定能否放下 |

paired的scope和period分别展示在各panel。编译器检查声明的单位和数值域，业务可比性仍由材料审核确认。不同人群或期间可以用于有目的的对照，需要解释为何可比及哪些条件影响结论。单位相同并不能单独证明业务含义相同。

child通过use指定library ID，并保留其本身的数据字段。recipe分配frame和统一文字样式，子输入的frame、rotation、transform及字体、字号、行距、内边距等度量覆盖会报错。recipe内图表的axis、legend和data_label统一采用dataCaption，省略时自动写入，冲突角色明确报错。需要另一种几何时，使用scene或新的明确组合。图表仍沿5种公共chart_type及其数据条件，FT词汇名只用于发现和规划。[完整请求schema](../assets/design-system/recipe-request.schema.json)

recipe内比例环的detail用途承载分母，比例分解的percent用途承载组成占比，省略时同样写入dataCaption，冲突角色及会覆盖该角色的style.muted/style.color会报错。图表的style.text_color与全局、系列、单点data_labels文字色覆盖也会报错，重要文字色沿profile角色取得。series/point填充及style.colors继续用于数据配色，普通scene和既有组件保留原显式覆盖合同。

## 最小调用及同源数字

以下为合成数据。保存为request.json后可以直接compose，再用普通build导出。数值通过facts引用，修改facts后重新compose可使主值和主图联动。完整包内样例同时演示三种recipe。[三页合成样例](../assets/design-system/examples/three-recipes.json)

```json
{
  "recipe_version": "0.1",
  "project_id": "synthetic-component-example",
  "profile": "report-14pt",
  "facts": {
    "a": {"value": 12, "unit": "项"},
    "b": {"value": 18, "unit": "项"},
    "total": {"derived": {"op": "sum", "args": ["a", "b"]}}
  },
  "pages": [{
    "id": "overview",
    "recipe": "kpi-chart-explanation",
    "title": "两个类别的当前规模",
    "source": "合成数据，仅作接口演示",
    "notes": "检查当前规模与类别结构。",
    "slots": {
      "metrics": [{
        "id": "total-metric",
        "label": "当前总量",
        "value": {"ref": "total"},
        "unit": "项",
        "context": "同一期间，两个互斥类别"
      }],
      "main": {
        "id": "main-chart",
        "use": "primitive.chart",
        "chart_type": "column",
        "categories": ["类别甲", "类别乙"],
        "series": [{"name": "项目量", "values": [{"ref": "a"}, {"ref": "b"}]}],
        "text_roles": {"axis": "dataCaption", "legend": "dataCaption", "data_label": "dataCaption"}
      },
      "explanation": [{
        "id": "observation",
        "text": ["类别乙为", {"ref": "b", "format": ",.0f"}, "项，两个类别使用共同零基线。"]
      }]
    }
  }]
}
```

```text
python <Skill>/scripts/report_engine.py compose --input <request.json> --output <new-author.json> --profile report-14pt
python <Skill>/scripts/report_engine.py validate --input <new-author.json>
python <Skill>/scripts/report_engine.py build --input <new-author.json> --output <new-project> --pptx <new.pptx>
```

compose先校验请求和事实，生成0.1作者文档，再实际编译测量，成功后发布新author文件。资源图片按当前包外资产目录使用--assets。请求schema中的recipe值省略recipe.前缀，library查询使用完整ID。

保留原request及作者中的recipe_source。正常computed build每次按当前facts、tokens及recipe_source重新计算scene，不消费缓存elements的手改坐标。修改slot内容可patch recipe_source；自由文档流使用layout树。旧版仅保存scene的作者需要从原request重新compose，或显式以legacy-replay复现历史结果。

facts对象为必填字段。纯文字或图片证据可以使用空对象，引用事实时仍需提供对应事实，未知ref会报错。

## 全局规范与profile身份

report-14pt提供微软雅黑、14pt正文、最低9pt、正文80%黑及注释35%黑。当前profile的标题22.4pt、区块标题16.8pt、标签11.2pt、注释9pt、主要指标33.6pt，原生字号按既有0.1pt量化。正文行高倍率为1.3，对应18.2pt行距。图例、关键读数和必要分母用正文色角色，来源用caption。dataCaption继承注释字号并采用正文色，模板重要读数在该profile中也使用此角色。[正式profile](../assets/design-profiles/report-14pt.json)

compose将profile的id、sha256和hash_method写入brief.design_profile。正常build自动解析该声明，按原始文件字节指纹校验，显式--tokens需要匹配当前声明。profile升级需先通过作者patch更新其身份，再构建和复验。沿正常schema及版本方法修改作者，CLI及Python构建消费同一身份。未声明profile的已有作者继续使用其原调用参数。[版本化修改](ppt-engine.md#修改与版本)

## 自由组合与允许变换

通过scene可以选择基础形状、文字、图片、图表和组件，明确其frame、角色及关系。组件在分配的frame内按自己的规则计算比例、条长、段落和稳定子ID。整页模板按其既有容量及拓扑使用。当前recipe是有限组合，slot数量变化、数据域及文字长度都需编译测量。

组件逻辑frame用于布局、容量、子框包含及SVG检查。Office中实际原生组的选择边框按真实子对象并集生成，空白逻辑区域可以延伸到选择框之外。嵌套组件的完整逻辑区域参与父级包含检查。

每次选择查看语义、数据、容量和目标能力。饼环需要互斥部分与有效分母，比较需要单位和基准，拓扑连接需要资料支持，图片需要明确证据或插图用途。内容变长时可有据改写、选更合适组件、重新分配scene区域或拆页。文字和数值角色沿全局规范，替换profile后重新测量。

原生Chart支持其图表与工作簿编辑，生成的原生shape及文字支持相应对象操作，SVG插图和位图保留各自缩放、替换与清晰度能力。progress-ring中心百分比及分母属于独立文字，Office内单改工作簿后需同步，作者facts重建则从同源值生成。实际编辑能力按目标操作证据记录。[图表及编辑边界](ppt-chart-usage.md#标签颜色编辑及常见误用)

## 样板与视觉层级

推荐组合同时考虑信息组织、正确编码、视觉层级和局部细节。样板记录内容变换及其来源，先核当前材料能否支持其维度与结构，再采用外观。各自拥有分母的独立完成率分别表达，组成饼和花瓣结构需要同一整体及可加总的部分。没有数值依据的起伏路径注明概念用途，有真实序列后再用趋势编码。

优先在同源主图上用局部标注指出转折、差额和关键条件，重复放置同一张图仍沿同一证据身份。版式通过容量检查后，继续在实际成图中查看读序、主次、图意及细节。样板的视觉评价、语义保真及用户80分评价按各自证据记录。[数据表达审核](ppt-visual-review.md)

## AI采用与有限走查

1. 确认每页要回答的业务问题，提取必要事实、比较、集合和条件。
2. library筛选可用对象或recipe，读取合同及预览，比较少量合适候选。
3. 绑定当前facts和内容，选择profile，保存采用理由及具体备选。
4. compose或build，按诊断处理引用、数据域、数量和容量，形成当前PPT。
5. 先独立核当前页面、备注和全稿的业务解释，再在实际PowerPoint成图中核本页关系、数据图种、分母、尺度、标签与段落。
6. 合并同根因问题，按当前预算最多两轮针对性修订复验，登记实际交付状态。

停止依据为当前必需检查完成、影响理解和交付的问题已处理，并有可供用户评价的当前成品。预算不足或必要数据仍缺时保存可恢复工程及具体缺口。工程通过、实际看图、目标编辑和用户评分各按真实范围记录，用户的80分目标继续由实际评价确认。[制作控制与审核](ppt-engine.md#有限运行与检查)
