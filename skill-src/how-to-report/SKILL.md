---
name: how-to-report
description: 从真实处境和材料澄清目标、形成有依据的判断并交付明确页数与逐页内容的 Markdown 汇报方案，支持先分析、多轮局部修订，以及内容确认后使用自有参数模板与包内 PPT 制作技术继续制作。
---

# How to Report

帮助用户把事情想清楚，再形成听众能够使用的汇报材料。默认完整内容交付为《汇报方案.md》，包含简短安排、具体页数和页序、每页可直接使用的标题与内容。用户要求 PPT 时，按内容确认及有效制作授权沿 [PPT 交接](references/ppt-handoff.md) 连续使用自有模板、tokens和包内制作技术完成参数绑定、页面制作、检查与导出。

## 先进入生成与修订主线

以[生成与修订方法](references/reporting-method.md)作为唯一主工作流：明确沟通结果，让候选判断、证据和遗漏区别相互校正；沿用用户确定的话题与页面约束，形成回答、理由与论据的支持关系，先组织与页数无关的理解顺序及关键承接，再映射每页必讲内容；多议题不硬造单一总论点，不按每条发现拆页。在叙事成立、可读且信息完整的约束下，授权内尝试合并相关内容，用最少篇幅呈现最多有用内容。合页、改序或压缩解释后重新连读当前全稿，不能因数字未丢继承旧叙事结论。概要先让人抓住意思，解释补足必要关系；深浅由任务和听众已有理解决定。已有目录、事实标题或问题树不替代论证；已经解决的部分沿用，不要求局部修改重走全流程或读取全部专题。

- `create`：利用已给目标、情境和资料，从尚未解决的问题开始，交付可制作的完整材料方案。
- `analyze-first`：解决当前目标、解释或方案取舍，达到可讨论程度即可；不强行成稿。
- `revise`：继承当前版本和仍适用的约定，仅调整受影响内容。只改一句话或一个标题时，直接交一个替换结果；用户要备选时才增加。

委托者、实际汇报者和听众可能不同。新完整任务须先讲清目的、场合、真实参与职责与受托利益、决定/评价和否决范围及影响关系；只有职位名单不够。已有确认沿用，局部修改不全量重问。目标歧义、事实缺口和专业知识不足分别处理；用户明示的认可与贡献诉求积极采用，已否认的诉求停止沿用。正文由实际汇报者向听众表达，作者安排与正文分开。

## 难点出现时再读专题

PPT在内容路线明确后先完成[制作前设计评估](references/ppt-design-preflight.md)，以页任务、关系、素材和必要数据分析决定表达，通过[组件库与Storybook](references/ppt-storybook.md)查询真实规格与预览，确定栅格读序、文字角色与容量预算。所有新增绘图与布局由engine负责；先测排，再成图并读取实际内容占用诊断。按[数据表示选择](references/ppt-data-display.md)先判听众任务：解释变化、差异、分布或状态用适配图表；名单和明细供查阅核对时用表格，不要求先穷尽图库。混合任务用主图解释加必要明细，不重复堆数，也不为孤立数字强造单值柱。AI不临时生成自由SVG、手填形状坐标或编写PPT绘制脚本补缺。按[制作方法](references/ppt-production.md)可将实际查看的源图放入computed容器，或在授权下为缺图设置明显矩形占位并说明建议图片；确需新原生能力时才扩展engine并验证后调用。

| 当前难点 | 资源 |
|---|---|
| 合理目标解释会改变主线，或材料出现新机会 | [目标发现](references/goal-discovery.md) |
| 新完整汇报须确认真实角色及本场判断，或相关角色/权限变化 | [职责索引](references/stakeholder-roles.md)，帮助确认，不自动补评委 |
| 重要判断须面对本场相关反对或回答不了有效问题 | [定向挑战](references/directed-challenge.md)；真实委派、先读算后具体求助 |
| 零散记录难以归并，换主体或润色后可能改义 | [材料提炼与含义保真](references/semantic-structuring.md)；需要具体改句时看[来源对读示范](references/content-decisions.md#来源不足时停在已知范围) |
| 构思完整判断类材料，需主动检验遗漏区别或展开新线索 | [解释探索](references/insight-discovery.md)；具体概念、前提、条件、论证问题用[思维方法](references/reasoning-methods.md) |
| 听众、媒介、路线、详略或时间需要调整 | [叙事与会议表达](references/meeting-expression.md) |
| 句子抽象生硬、角色混乱或混入制作旁白 | [观众成稿编辑](references/audience-copy.md) |
| 有了判断却仍平均介绍全部主题，或新回复替掉原余项 | 定向用[内容删合示范](references/content-decisions.md#读者仍需自己拼接)或[部分更新示范](references/content-decisions.md#新回复只完成部分请求)，实际重写受影响内容；交付形式看[完整材料示例](assets/examples/report-proposal.md) |
| 标题有要点，正文却只重复标签；复杂评审仍讲不清一件事 | 用[关系展开](references/semantic-structuring.md#把概括展开为可理解的关系)补本场必要解释，定向参考[同源短稿与完整评审](assets/examples/report-depth-proposals.md)；不照搬页数或逐层句式 |
| 派生数字、日期、基准或计算影响判断 | [数值方法](references/numeric-evidence.md)、[进度事实](references/project-progress.md)；适用运算实际调用[Python计算工具](references/report-calculation.md)，结果还要对到正文比较与推荐 |
| 数字、看板或调研结果仍停留在罗列，需要解释差异与业务含义 | [业务数据分析](references/business-data-analysis.md)，实际展开问题、比较、拆解和计算，形成有据解释及适用建议，缺数按影响收窄相关判断 |
| 材料交接、续接或版本追溯 | [最小证据](references/evidence-handoff.md)、[生成Run](references/report-run.md)、[版本操作](references/version-lifecycle.md) |
| 请求制作 PPT、确认内容后继续制作，或制作中需要回改内容 | [PPT 交接](references/ppt-handoff.md)，承接当前稿、来源、属性级确认及实际制作状态 |
| PPT需要模板、组件及推荐组合发现、跨页数字联动或持续局部修改 | [组件系统](references/ppt-component-system.md)通过library发现、compose调用3个受约束组合，查看slot、profile及样例。自由编排与版本化修改沿[作者工程](references/ppt-engine.md) |
| PPT需要判断图表或明细表、比较图种或查数据表达条件 | 先读[听众任务与表示选择](references/ppt-data-display.md)，再读[图表使用场景手册](references/ppt-chart-usage.md)及[68种注册图表](assets/design-system/chart-assets/README.md)：先用chart-assets读取当前数据合同、算法限制及可编辑等级，再由chart-build计算；既有5种原生Chart入口按兼容合同使用 |
| PPT需要选择主次比例、双栏/三栏、重复小图或统一对齐线 | [栅格设计选择](references/ppt-grid-design.md)及[16种模式详解](references/ppt-grid-patterns.md)：先按内容关系选择结构，再映射现有布局容器；12/24列是设计参照，不是新增span/subgrid能力或已注册模板 |
| 资讯、介绍或技术说明文字多，需要短语、解释段与图形分工 | [长文本结构化](references/ppt-explanatory-content.md)，保留关系与必要条件后选栅格，不把全部说明压成标签 |
| PPT需要自动测高、Grid/Flex、文档流或计算拓扑 | [计算排版与拓扑](references/ppt-layout.md)：layouts发现持久布局树，components topology发现节点、连线及弧形结构。每次正常build重新计算坐标 |
| 用户给出真实PPTX，要求读取对象配置并原样重建或保留式修改 | [原生配置读取与重建](references/ppt-native-roundtrip.md)：native-import读取全包配置，native-inspect核配置与依赖，native-build从配置重建。用同台PowerPoint对照原件并验证实际编辑操作 |
| 已有PPT或成图需要审核模板选择和数据表达 | [模板适配与数据可视化审核](references/ppt-visual-review.md)，对读任务、实际原型与备选、源数据和图面，记录具体修法及复验 |
| 明确复用或保存已确认偏好/经验 | [画像](references/report-profile.md)、[私有经验](references/report-experience.md) |
| 专业关系需要领域知识 | [知识目录元信息](knowledge/index.md)，正文按已有授权范围读取 |

新制作的一切排版和布局依靠算法和数学。正常build默认computed，只接受计算树、参数模板或可重放recipe_source；手写scene仅以显式legacy-replay身份复现历史产物。实际字段与限制沿[计算排版合同](references/ppt-layout.md)。

原样重建沿原生配置路径保留源坐标、样式及继承关系，源渐变也保留。该路径的可编辑配置与重建验收按其实际证据说明，不代表已经从任意原稿推导出可增删节点的动态布局规则。

核心方法和本地来源离线可用，网址只供溯源。可选领域正文遵守实际授权，已有同范围许可不重复申请，拒绝、未回应或撤销的正文不读。知识不能替代项目事实，摘要不冒充完整原文。

## 交付与可靠性边界

完整材料必须有具体总页数和全部逐页内容，不能只交长讲稿或空页纲。用户明确只要口头稿、阅读稿、分析或局部修改时按其范围交付。下游可自由选择图形、插画和布局，事实、关系与重要条件仍应保留。

PPT 请求的协调者沿用当前内容的有效确认、制作授权和限制。用户已授权自主制作或缺数先出草稿时，在该范围内直接接续。通过总入口调用时将当前稿、实际分析与授权范围交回该协调者，独立调用本 Skill 时由当前主 Agent 接续。实际文件、工具与外部入口能力按 [宿主边界](references/host-capabilities.md#外部制作-skill) 核对，制作未完成时交代当前产物与具体续接点。

普通任务不要求建Run、Graph或Blueprint。复杂关系和留存按需使用[多图视图](references/graph-model.md)、[工作区契约](references/workspace-contract.md)与[宿主能力](references/host-capabilities.md)；记录可审阅的决定，不输出私有推理过程。普通分析可按[可选并行协作](references/host-capabilities.md#可选并行协作)拆分独立问题。审计与定向挑战必须按[委派契约](references/agent-delegation.md)由真实子Agent执行，失败或无能力时明确未完成，不由主Agent串行假扮或私调模型服务。文件能力不要求每次初始化目录。

重要成稿需要独立审计或用户请求审计时，真实委派 `report-audit` 审计执行者；干净上下文先只读正文，返回初读后才提供目标、角色、原资料与必要作者说明，不能一次注入创作历史再称盲读。生成自查、结构检查、真实委派和独立审计分别说明。未做不写通过，无法完成独立审计时交代工作稿的实际边界，继续可完成的内容工作；主Agent维护唯一当前稿。
