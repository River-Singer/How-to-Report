# Research: Public sources for semantic visuals, multiple views, fixed canvas and mirror audit

- Query: 定向研读共享对话引用的一手视觉资料，形成“语义关系 → 内容/页面 → 多拓扑 → 固定画布 → 独立审计”的可复用约束、适用边界和可测试建议；明确 M0/M1 接口与 M4 后置范围。
- Scope: mixed；公开原作者/官方资料与已完成的本地原型研究交叉。只研究，不实现、不安装依赖、不修改产品代码。
- Date: 2026-10-26（本轮会话日期）。
- Registry: 本任务 `research/public-sources.md` / `.json` 的 PS 编号。本文不修改共享注册表；末尾提供合并状态。
- Status: 完成 8 组重点来源研究；7 组完成与本任务有关的章节阅读，IBCS 完成官方版本说明核验但未取得 2.0 详细条文，明确限制。技术库已使用 Context7 查证，并与官方网页交叉核对；未声称安装或运行这些库。

## Findings

### 研究结论

现有 PRD 的方向成立：必须在渲染库之前保留“本页要让听众完成什么判断、哪些关系必须共同看见、数据是否可比、视觉不得改变什么含义”。公开资料不支持把业务图谱直接套成固定模板，也不支持用 DOM 不溢出证明汇报正确。应把图表选择、跨图一致性、容器运行和语义审计分层验证；模型仍可自主选择表达方式。

这是一组根据多源资料与本项目需求形成的**研究建议**，不是资料原作者为本项目给出的规格，也不是用户已冻结的新增工程范围。主要依据为 [Munzner 的分层设计/验证模型](https://www.cs.ubc.ca/labs/imager/tr/2009/NestedModel/)、[Vega-Lite 的组合边界](https://vega.github.io/vega-lite/docs/composition.html) 与 [Qu / Hullman 的多视图一致性研究](https://volitionalai.uw.edu/paper/2018-Consistency-InfoVis.pdf)。

### 1. FT Visual Vocabulary：关系先于图形名称

- **PS150，关联 PS159**。逐类阅读官方 README 的 Deviation、Correlation、Ranking、Distribution、Change over Time、Part-to-whole、Magnitude、Spatial、Flow 及限制。它是提高图表判断能力的学习资源，并非整套可直接调用的图表 API。量级比较、名次比较、分布与趋势是不同任务；相关关系易被观众误读成因果，热力图不擅长精确比较小差异。应据问题/数据选择图，不能因有地图或桑基图就强行使用。[FT 分类与说明](https://github.com/Financial-Times/chart-doctor/blob/main/visual-vocabulary/README.md)
- **对项目的约束推导**：Chart Intent 保留“比较什么/看什么关系”及关键前提；适配器可有多个候选。FT 不能替代证据审计或确定页数。
- **复用边界**：另一个 PS159 仓库定位为供进一步编辑的静态图起点，软件采用 MIT，但该授权排除 FT 内容/品牌。可借鉴代码机制并遵守许可，不能把海报/品牌与软件许可混同。[FT 示例仓库与许可](https://github.com/ft-interactive/visual-vocabulary)

### 2. Munzner Nested Model：验证方式必须对应设计决策

- **PS153**。阅读作者页、论文第 1–3 节，及第 6 节建议、第 7 节局限中的相关文本。四层分别处理领域问题、数据/操作抽象、视觉/交互、算法；上层误解会传到下层。作者明确不要求严格按时间串行；下层性能测试不能验证上层问题是否选对，模型也简化了复杂认知任务。[作者原论文](https://www.cs.ubc.ca/labs/imager/tr/2009/NestedModel/NestedModel.pdf)
- **对项目的约束推导**：若页面“能打开但讲错问题”，返修 Content Blueprint / Page Plan；若关系正确却难读，返修视觉编码/排版；若容器为空，返修 runtime。审计缺陷必须标记归属层，不统一通过“再美化一下”处理。
- **限制**：这是设计/验证框架，不是完整生成算法、固定四阶段任务图，也未证明某个 LLM 自动审计方案有效。

### 3. Qu / Hullman：跨图一致性既有规则，也有有理由的例外

- **PS176 → 补充查证作者机构 PDF**。重点读第 3 节约束、第 4 节研究设计、第 5 节 xy/颜色一致性与例外、第 6 节实现启示/局限。尺度包含数据域、视觉范围、映射函数；同字段跨图的颜色/顺序/尺度应有一致规则。研究故意提出严格约束以探索作者为何接受或拒绝，不能照抄成无例外硬规则。[原作者版本](https://volitionalai.uw.edu/paper/2018-Consistency-InfoVis.pdf)
- **证据边界**：研究为 10 名具有可视化经验的 Tableau 使用者的定性观察；未直接研究观众理解效果。范围主要是定量/名义数据的 xy 和颜色，不覆盖所有交互一致性。
- **对项目的约束推导**：同屏比较可明确共享尺度；不同单位或有意放大局部差异可以独立尺度，但需可见标注、理由和误读检查。审计报告指出具体图对和差异，不能只判“所有轴不一致即失败”。

### 4. ECharts：图表尺寸是生命周期契约

- **PS182，关联 PS158**。官方 Chart Container 全文与 Context7 `/apache/echarts-handbook` 对照：初始化前容器应有有效宽高，或显式指定尺寸；CSS/JS 改容器不一定触发窗口 resize，应考虑 ResizeObserver；DOM 被移除后应释放实例，重新挂载时重建。[官方尺寸文档](https://echarts.apache.org/handbook/en/concepts/chart-size/)
- **对项目的约束推导**：HTML Deck 应向图表适配器提供挂载、页面显现、尺寸变化、销毁事件；隐藏页初次进入需实际检查图表非空且尺寸正确。不能仅因为页面舞台缩放正确就宣称图库尺寸已正确。
- **限制**：这证明官方 API 所需条件，不证明本项目已兼容；本轮未安装 ECharts、未测试图种或导出。库的精确版本和集成边界应在采用时固定，避免把 Context7 的索引版本当项目依赖版本。

### 5. Vega-Lite：组合语法不保证组合后的语义合理

- **PS183，关联 PS161/PS162**。读官方 Composition、Resolve 全文和 Context7 `/vega/vega-lite` 中 layer/facet/concat/repeat 的尺度默认值。可分层、分面、拼接和重复；编译器能合并尺度域/图例，但官方明确不能保证域合并在语义上合理。`shared` / `independent` 应按比较任务选择，独立尺度意味着独立坐标/图例。[组合](https://vega.github.io/vega-lite/docs/composition.html)、[尺度与图例解析](https://vega.github.io/vega-lite/docs/resolve.html)
- **对项目的约束推导**：Chart Adapter 输出除图形外，应能回报实际字段、转换、尺度/图例选择及数据引用，供跨图审计；从两个成功编译的 Spec 不能推得“可联合论证”。
- **限制**：Vega-Lite 的多视图语法适合数据图，不能替代包含文字论证、视频、拓扑的整页内容规划；不得把其默认推断当业务口径验证。

### 6. AntV Infographic：可以复用表达语法，不能把模板名称当语义证明

- **PS156/PS157 → 补充查证官方语法页**。读 README、语法正文与 Context7 `/antvis/infographic`。官方将 template/design/data/theme 分开，数据区分无序列表、有序序列、层级、对比、数值、节点/关系；关系默认有向，重复节点 id 后者覆盖，部分 Mermaid 风格修饰会归一化/忽略。[官方语法](https://infographic.antv.vision/learn/infographic-syntax)、[官方仓库](https://github.com/antvis/Infographic)
- **对项目的约束推导**：适配前检查唯一 ID、关系类型和方向；禁止用列表自动生成因果箭头。若上游需要保留不确定/反驳/支持等关系，而目标语法不能表达，应显式标注、换组件或拒绝该映射，不能静默降成普通箭头。
- **限制**：可编辑 SVG、流式生成和模板数量不是专业质量证明；本轮不引入它的现成 Skill，不把它的字段模型覆盖本项目语义核心。

### 7. MDN aspect-ratio：比例约束不能证明内容放得下

- **PS179**。定向读属性工作机制、非替换元素、溢出/网格相关章节。`aspect-ratio` 是首选比例；显式同时给定宽高会覆盖它，内容的内在尺寸、最小尺寸和溢出仍需处理。[MDN 原文](https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Box_sizing/Aspect_ratios)
- **对项目的约束推导**：舞台几何、内容边界、实际字形可读性是三项不同检查。`overflow:hidden` 可能掩盖缺失的限制/来源；页面容器仍是 16:9 不代表页面合格。应分别记录设计坐标和缩放后的显示尺寸，再截图核查，必要时回到页面计划拆分内容。
- **限制**：网页允许滚动/裁剪的示例不自动适用于演讲页面；禁止把 CSS 的可行技术方案误当本产品允许隐藏关键内容的规则。

### 8. IBCS：先处理当前版本漂移，再决定采用哪些规则

- **PS141/PS142/PS154 关联，补充查证现行官方页**。当前官方说明 IBCS 2.0 于 2026-06-11 发布，与 ISO 24896 对齐，改为 Notation / Composition 两部分；旧 1.2 被明确标为旧版。[IBCS 2.0 官方说明](https://www.ibcs.com/ibcs-version-2-0/)
- **访问层级**：已读版本说明和公开页面文字；页面在线阅读组件的详细条文未被文本工具返回，未取得完整 2.0 标准。没有以会员身份访问 PDF，也没有核验 ISO 全文。因此不声称已逐条验证 SUCCESS、统一符号、尺度、压缩等旧条文在 2.0 的确切位置或强度。
- **对项目的约束推导**：Reference 要标所依据版本和实际读过的条款；M0/M1 无需等待 IBCS 全量卡。不能把“符合 ISO/IBCS”作为未验证产品宣传。

## 语义到页面的可测试约束（本项目建议）

以下为结合来源、PRD `:649`–`:758` 和已确认用户需求形成的验收候选，不是新写入产品代码的测试，也未被宣称已经通过。

| 层 | 应保留的含义/决定 | 可观察失败 | 建议核查方式 |
|---|---|---|---|
| 内容 → 页面 | 问题、完整主张、证据/限制、核心认知任务 | 页面漂亮但无法说清回答什么 | 从页面独立重建主张，再对照 Blueprint |
| 关系 → 拓扑 | 支持/限定/时间/因果/包含等区分 | 无序项画成时间链；支持关系画成因果 | 在图外保留关系引用；独立检查箭头/分组暗示 |
| 数据 → 图表 | 对象、粒度、单位、时间、来源、缺失策略 | 空值画成 0；总量和比率混合 | 对输入与生成规格做确定性检查 |
| 图表 → 多视图 | 共同认知任务及可比范围 | 不同车型/期间/筛选状态暗示同一对象 | 对图对核对元数据；差异需可见解释 |
| 编码一致性 | 同字段的颜色、排序和尺度规则 | 同一颜色在不同页表示不同业务对象 | 按本次报告范围比较编码；例外记录理由 |
| 表达 → 画布 | 关键来源/限制和共同比较关系 | 为塞入 16:9 删证据、截标签 | DOM 边界 + 截图 + 关键文本/对象追溯 |
| 翻页/缩放 | 图表可见时有有效尺寸 | 首次进入空白、二次进入失效 | 实际浏览器覆盖进入、离开、缩放、再进入 |
| 镜像审计 | 原材料与页面可独立取得 | 只读生成侧总结而确认合理 | 记录独立性和输入来源；先看页面后核对计划 |

建议优先保留六个有实际判别力的反例：① `null` 与 0 的热力格不同；② 中文/英文长标签不会变成同一对象；③ 双图同色不同义；④ 相邻两图的日期/筛选不一致；⑤ 无因果证据的箭头连接；⑥ 为解决溢出删除限定或来源。它们能检测真实信息损失，不是镜像实现细节的形式测试。

## 现原型差距与代码依据

本节复用已完成的 `research/supporting-docs.md`；未重跑研究、未改原型。以下路径均在 `doc/How-to-Report-Visual-Lab/`。

| 原型事实 | 代码依据 | 对正式系统的影响 |
|---|---|---|
| JSON 已将 canvas/charts/slides 分开，但未实现 Source/Claim/Obligation/QUD | `presentation.json:3`、`:11`、`:601` | 可复用渲染输入边界，不能直接作为上游语义契约 |
| 无效/缺失数值可能被转换为 0 | `chart-engine.js:7`、`:21`–`:22`、`:28`–`:29` | 先建立缺失/非法输入契约，再换成熟图库；换库本身不修正数据语义 |
| 英文排名标签被截成相同文本 | `chart-engine.js:19`；`make_example.py:37` | “几何不越界”不足；必须检查标签可辨识与对象对应 |
| `canvas` 配置与 CSS/runtime 固定 1600×900 不一致 | `deck-runtime.js:40`；`styles.css:3`；`audit.py:22` | 主题/runtime 应统一提供画布和安全区，图表只消费区域尺寸 |
| build 不强制运行 audit，runtime 未调用 validate | `build.py:25`–`:28`；`deck-runtime.js:32` | 有校验函数不等于用户流程受保护，需要真实入口与审计结果关联 |
| 静态 audit 只验证部分结构/来源字段 | `audit.py:18`–`:54` | 无法替代跨图口径、事实推理、页面语义往返与真实渲染核查 |

最有价值的复用是现有配置/renderer/runtime 分离和离线样例；最紧急的缺口是来源追溯、主张强度、缺失语义及真实验证状态。无需在 M0/M1 为覆盖 FT 图谱而大规模重写 renderer。

## M0 / M1 应保留的最小接口语义

这里描述应能表达的信息，不冻结 JSON 字段名称，也不要求每项独立文件。与 PRD `:414`–`:438`、`:649`–`:656` 相容。

1. **Blueprint → Page Plan**：可引用原主张/内容单元；声明认知任务、必须同屏/允许分步的关系、证据和不可删除的限定。M1 可用简洁 Markdown 表达，并接受审计挑战。
2. **Page Plan → Visual Intent**：保留关系类型、强调理由及候选表现方式；支持“此时不用图”。图的数量、左右比例、模板名称不成为业务语义。
3. **数据/计算 → Chart Adapter**：引用数据版本/计算凭证，明确量纲、粒度、缺失与变换；适配器回报实际编码/尺度/过滤决定。M1 留引用接口，不预建全部图库驱动。
4. **Renderer → Runtime**：区域宽高、安全区、显现/尺寸改变/销毁生命周期，实际渲染状态。可先明确能力边界；实现丰富浏览器生命周期在 M4。
5. **产物 → Audit**：稳定对象引用、来源可用性、未验证状态、缺陷所属层及修复位置。M1 双 Skill 可审 Blueprint 与证据缺口；无浏览器就不能报告页面验收通过。
6. **可选标准/方法引用**：方法名、来源、所读版本、适用条件和例外；FT 分类与 IBCS 是可选方法资源，不凌驾于用户任务和实际事实。

## M4 及后续才需要的实现工作

- 先选能覆盖真实评测的少量图形和一个主要定量图库；ECharts / Vega-Lite 是适配候选，不必同时引入。AntV 也只在语义拓扑确有收益时作为可选适配器。
- 固定实际采用的库版本，建立语法/属性兼容验证；若上游语义无法映射，明确降级，不依赖容错吞掉关系。
- 实现声明支持的画布预设、图表实例生命周期、浏览器测量与截图；维护设计坐标、实际屏幕缩放和字体可读性之间的区别。
- 将跨视图编码/单位/口径检查与页面语义重建结合；尺度例外应可解释，模型发现的语义问题要有位置/影响/修复路径。
- 富运行机制（双语、视频、自动播放、编辑/保存、导出）按最终范围逐项实现和验收；本研究不以原型具备某按钮推出正式产品已承诺全部功能。
- 完整多图自动优化器、覆盖全部 FT 图形、IBCS/ISO 认证、跨任务学习用户所有设计偏好均不是 M0/M1 启动条件。

## Files Found / Related Specs

- `research/conversation-rounds-14-26.md`：用户原始视觉诉求和“先内容后视觉”的明确纠偏。
- `research/public-sources.md` / `.json`：本次实际引用的公开来源注册表。
- `research/supporting-docs.md`：Visual Lab 全代码阅读和内存反例核查；本次只引用结论。
- `doc/How-to-Report V1.0 · Codex 开发交付包/How-to-Report_PRD_V1.0.md:647`：页面语义到固定画布要求；`:716` 独立审计；`:839` M0–M5 路线。
- `.trellis/workflow.md`、`.trellis/spec/frontend/index.md`、`.trellis/spec/backend/index.md`、`.trellis/spec/guides/index.md`：已在当前任务读过；本轮不修改其内容。

## 来源状态合并表

状态仅限本文实际行为。`read_relevant_sections` 不等于整站、整仓库或整篇所有附件均精读。

| PS 编号 / 补充链接 | 建议状态 | 阅读层级与访问情况 |
|---|---|---|
| PS150 | `read_relevant_sections` | 官方 README 分类正文全部及许可读完；未逐一打开所有外链，也未把海报像素算作已读 |
| PS159 | `read_relevant_sections` | 官方仓库 README 定位、使用说明、许可全文；未逐个审查 D3 组件 |
| PS153 | `read_relevant_sections` | 原作者页面 + PDF 第 1–3 节、6/7 的相关段落；读取文本与图注，未声称完整图像检查 |
| PS176 | `abstract_read_primary_followed` | PubMed 初次 429，搜索返回摘要；随后访问原作者机构 PDF 见下一行 |
| 补充：`https://volitionalai.uw.edu/paper/2018-Consistency-InfoVis.pdf` | `read_relevant_sections` | 原论文约束、研究方法、关键 xy/颜色案例、设计启示、局限；Northwestern 同作者副本超时，UW 副本成功 |
| PS182 | `read_full_page` | 官方 Chart Container 全文 + Context7 对照；未运行库 |
| PS158 | `reference_only` | 关联官方仓库，技术阅读实际使用 PS182；不要升级成整仓库已读 |
| PS183 | `read_full_page` | 官方 Composition 全文；Context7 核对相关组合默认值 |
| 补充：`https://vega.github.io/vega-lite/docs/resolve.html` | `read_full_page` | 官方 Resolve 全文；补充精读来源 |
| PS161/PS162 | `docs_via_context7` | Context7 返回官方 repo 文档片段；未读完整仓库/完整 spec.md |
| PS156/PS157 | `read_relevant_sections` | 大小写 URL 指向同一官方仓库；README 完整正文 + Context7 语法/模板片段 |
| 补充：`https://infographic.antv.vision/learn/infographic-syntax` | `read_full_article` | 官方语法正文全部（含数据/关系/主题/流式示例）；页面后半为重复代码展示，不当新内容 |
| PS179 | `read_relevant_sections` | 属性机制、非替换元素/溢出/网格章节；未遍历全站或验证浏览器实现 |
| PS141/PS142/PS154 | `version_followup_only` | 未声称旧链接具体条文已读；使用当前官方说明校正版本，见下一行 |
| 补充：`https://www.ibcs.com/ibcs-version-2-0/` | `read_version_page_detail_unavailable` | 官方版本介绍全文；在线阅读组件详细标准未提取，PDF 提示会员获取；未宣称 2.0 逐条规范核验 |

## Caveats / Not Found

- 本轮是研究而非验证库集成。没有安装、构建、截图测试本项目 ECharts/Vega/AntV，也没有修改产品代码；任何运行能力都仍需实现期证明。
- Web 的论文截图调用只返回引用信息，没有可供本研究直接检查的像素；因此阅读范围按文本/图注记录，不谎称做过图像审阅。
- 技术文档读取于本轮；未固定 commit/package version。实施选择版本后，语法、导出、无障碍和生命周期细节需在该版本验证。
- PS176 研究不能支持“自动一致性检查已证明让所有听众理解更好”；PS153 不能证明特定 LLM 审计有效。本文将这类产品推导显式列为建议。
- IBCS 2.0 细节未取得；只采官方版本事实。没有将旧 SUCCESS 细节冒充已核验的新标准，也没有宣称符合 ISO。
- 未重复研究原 Report Takt 仓库；当前问题可由现有本地原型与上述一手来源回答。若后续决定复用其模块，再针对具体文件/许可研究。
