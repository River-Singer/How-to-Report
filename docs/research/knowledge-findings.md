# Knowledge 定向研究的进一步发现

更新：2026-10-26。先复核方法资料并推进四项领域资料阅读，随后针对用户追加问题研读表示重构和目标发现。原共享对话索引仍为171个链接；补充新文献单独登记，没有据此验证产品效果。

## 新推进的阅读

| ID | 实际读取 | 范围与限制 |
|---|---|---|
| PS033 | [DORA 指标指南](https://dora.dev/guides/dora-metrics/) | 官方页面正文；未逐篇研究关联报告 |
| PS034 | [DORA 指标演变](https://dora.dev/insights/dora-metrics-history/) | 官方页面正文；未读完历年调查 |
| PS037 | [SPACE 作者机构页](https://www.microsoft.com/en-us/research/publication/the-space-of-developer-productivity-theres-more-to-it-than-you-think/) | 书目与摘要；ACM Queue 正文返回403，未读全文 |
| PS097 | [Teal Book 第19章：收益管理](https://projectdelivery.gov.uk/teal-book/home/part-e-planning-and-control/chapter-19-benefits-management/) | §19.1–19.6.1.3、§19.6.2–19.6.3.9相关正文；未读全部附件与关联书籍 |

四项合并时，“仅收集”从143降为139；追加研究又推进PS068，当前为138。另登记PS068作者机构副本及Gentner、Keeney两篇补充原始文献，实际读取地址总数由11增至14；地址数量不等于独立论文数。阅读状态不代表卡片已写入发布包。

## 直接发现及工程含义

**DORA 需要版本和测量层级。** 当前官方指南是五项软件交付指标，并强调应用/服务语境及跨应用比较的局限。工程含义：卡片标明版本、粒度和比较条件，不能沿用一个无日期的“四指标”模板，更不能直接换算为个人效率或现金节约。[官方指南](https://dora.dev/guides/dora-metrics/)

**SPACE 反对用单一维度代表生产率。** 作者摘要明确开发生产率超出个人活动量或交付系统效率。可支持一张有限的原则卡；完整维度操作、权重与实施步骤仍须读全文，不能由摘要补写。[作者摘要](https://www.microsoft.com/en-us/research/publication/the-space-of-developer-productivity-theres-more-to-it-than-you-think/)

**交付、结果、收益及现金影响须分开。** Teal Book 要求收益有基线、测量、负责人、实现期与依赖。工程含义：将“功能交付”“预计释放工时”“已产生业务改善”“现金支出减少”作为不同证据强度的判断；公共项目指南的组织规则不直接套用企业。[相关章节](https://projectdelivery.gov.uk/teal-book/home/part-e-planning-and-control/chapter-19-benefits-management/)

**问完论证清单不等于解决真正争议。** Hernández 的理论讨论提醒固定问题可能漏掉决定性前提或重复无争议内容。工程含义：按具体主张形成有效异议和证明义务，允许增加情境问题，不由字段齐全自动判定充分。[原论文](https://link.springer.com/article/10.1007/s10503-023-09613-w)

**RST 的 Evidence 不是事实认证。** 其关系定义关注文本的沟通作用和读者信念。工程含义：帮助理解、论证支持、因果解释和真实性检查分别处理；`supports` 标签不产生 `verified`。[原项目定义](https://www.sfu.ca/rst/01intro/definitions.html)

**Assertion–Evidence 的实验不是只改标题。** 原研究的干预还包括文字密度、解释性图示与呈现方式。工程含义：不强制所有页面套“强断言标题＋大图”，应验证实际理解、内容关系与证据范围。[原论文](https://www.writing.engr.psu.edu/ae_comprehension.pdf)

以上“工程含义”是本项目推导，不是文献对 How-to-Report 的实验结论。通用方法、领域卡和解释探索须各自经过行为验证；来源读过不等于方法已正确迁移。

## 追加问题：问题表示与目标如何被发现

**关系类比与问题重构。** 新补读 [Gentner 1983](https://groups.psych.northwestern.edu/gentner/papers/Gentner83.2b.pdf)的相关正文，以及原PS068 [Dorst/Cross作者机构副本](https://oro.open.ac.uk/3278/1/Creativity_-_coevolution.pdf)的相关章节。前者支持从关系结构产生可待验证的候选，后者讨论人类设计中的问题—方案共同演化。它们启发表示变换与反馈，均不提供通用语义正交度或本产品效果保证；详见[解释探索设计](../insight-discovery-design.md)。

**目标不能只靠一次直接询问。** 再核验MIT目的/受众指导，并补读 [Keeney 2008作者上传原文](https://www.researchgate.net/publication/233717349_Applying_Value-Focused_Thinking)摘要及pp8–12相关段。其区分所求后果、手段和过程，支持从情境进一步发现遗漏目标；本项目据此设计候选、披露、取舍和操作化。不能据此猜定隐秘动机、套固定目标矩阵或保证沟通结果；详见[目标发现设计](../goal-discovery-design.md)。

更完整的读取证据、失败入口和原文/推导区分保留于父工作区当前架构任务 `research/knowledge-extra-findings.md`、`orthogonal-thinking-engineering.md`及`goal-discovery-methods.md`。首批卡片范围与缺口见[预载计划](../knowledge-plan.md)。
