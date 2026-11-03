---
name: how-to-report
description: 从真实处境和材料澄清汇报目标、提炼信息、形成有依据的判断，组织叙事并交付明确页数与逐页内容的 Markdown 汇报方案；支持先分析和多轮局部修订。
---

# How to Report

帮助用户把事情想清楚，再形成听众能够使用的汇报材料。默认完整交付是《汇报方案.md》：简短安排、具体页数和页序、每页可直接使用的标题与内容。到内容交付即停止，不生成 HTML、SVG、PPTX、固定版式或视觉验收记录。

## 先进入生成与修订主线

以[生成与修订方法](references/reporting-method.md)作为唯一主工作流：明确沟通结果，让候选价值判断、证据和遗漏区别相互校正，作出有依据的取舍，再组织逐页内容并核对实际成稿。已经解决的部分沿用，不要求每次走完全部工作或读取全部专题。

- `create`：利用已给目标、情境和资料，从尚未解决的问题开始，交付可制作的完整材料方案。
- `analyze-first`：解决当前目标、解释或方案取舍，达到可讨论程度即可；不强行成稿。
- `revise`：继承当前版本和仍适用的约定，仅调整受影响内容。只改一句话或一个标题时，直接交一个替换结果；用户要备选时才增加。

委托者、实际汇报者和听众可能不同。材料已经回答、目标已经确认就沿用；目标歧义、事实缺口和专业知识不足分别处理。用户已明确的认可与贡献诉求积极采用，已否认的诉求停止沿用。正文由实际汇报者向听众表达，作者安排与正文分开。

## 难点出现时再读专题

| 当前难点 | 资源 |
|---|---|
| 合理目标解释会改变主线，或材料出现新机会 | [目标发现](references/goal-discovery.md) |
| 零散记录难以归并，概括或关系可能失真 | [材料提炼与含义保真](references/semantic-structuring.md) |
| 构思完整判断类材料，需主动检验遗漏区别或展开新线索 | [解释探索](references/insight-discovery.md)；具体概念、前提、条件、论证问题用[思维方法](references/reasoning-methods.md) |
| 听众、媒介、路线、详略或时间需要调整 | [叙事与会议表达](references/meeting-expression.md) |
| 句子抽象生硬、角色混乱或混入制作旁白 | [观众成稿编辑](references/audience-copy.md) |
| 改了措辞仍只剩分类，或新回复使旧请求被整句替换 | 定向用[内容重组示范](references/content-decisions.md#读者仍需自己拼接)或[部分更新示范](references/content-decisions.md#新回复只完成部分请求)，再改当前片段；交付形式看[完整材料示例](assets/examples/report-proposal.md) |
| 数字、日期、基准或计算影响判断 | [数值方法](references/numeric-evidence.md)、[进度事实](references/project-progress.md)；定义明确的CSV用[显式计算](references/report-calculation.md) |
| 材料交接、续接或版本追溯 | [最小证据](references/evidence-handoff.md)、[生成Run](references/report-run.md)、[版本操作](references/version-lifecycle.md) |
| 明确复用或保存已确认偏好/经验 | [画像](references/report-profile.md)、[私有经验](references/report-experience.md) |
| 专业关系需要领域知识 | [知识目录元信息](knowledge/index.md)，正文按已有授权范围读取 |

核心方法和本地来源离线可用，网址只供溯源。可选领域正文遵守实际授权，已有同范围许可不重复申请，拒绝、未回应或撤销的正文不读。知识不能替代项目事实，摘要不冒充完整原文。

## 交付与可靠性边界

完整材料必须有具体总页数和全部逐页内容，不能只交长讲稿或空页纲。用户明确只要口头稿、阅读稿、分析或局部修改时按其范围交付。下游可自由选择图形、插画和布局，事实、关系与重要条件仍应保留。

普通任务不要求建Run、Graph或Blueprint。复杂关系和留存按需使用[多图视图](references/graph-model.md)、[工作区契约](references/workspace-contract.md)与[宿主能力](references/host-capabilities.md)；记录可审阅的决定，不输出私有推理过程。复杂材料可按[可选并行协作](references/host-capabilities.md#可选并行协作)把独立问题交真实子代理，主代理统一取舍；无能力则串行，不新增必需平台。文件能力存在不等于每次都要初始化目录。

重要成稿交实际可用的 `report-audit` 或独立上下文审查，提供原要求、原资料和实际产物，不能只交生成者自评。生成自查、结构检查和独立审计分别说明；未做的检查不写通过，已知重要错误不能因任务结束而通过。无法独立审查时如实交代工作稿的核验范围，不阻断可完成的内容工作。
