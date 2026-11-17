# 从汇报逻辑到可计算页面

当前方法版本0.11.4。先把听众要理解或核对的内容组织清楚，再选择表示与栅格，最后让引擎测量、计算和导出。方法已进入正常Skill入口；它不等于模型每次都能自动做出正确设计，也不是一个自动语义评分器。

## 制作前先决定什么

正常路线为：内容分析B → 理解路线与页任务C → [制作前设计评估](../skills/how-to-report/references/ppt-design-preflight.md) → 真实资产查询与computed测排 → PowerPoint成图 → 最终叙事、模板适配和视觉审核。

前置评估确认页任务、分析就绪范围、可用素材、表达关系、实际组件及必要备选、栅格读序、文字角色和容量预算。已有brief和作者工程足够，不增加重复规划文件或审批流程。日期事件形成推进关系时先评估时间线；只是名单中的日期则不强制。原图可用于界面或复杂结构证据，缺图占位必须明确身份及用途。

合页、拆页或改序会改变听众取得前提和问题的顺序，必须从最终正文及口播重审。保留全部数字与测排通过，均不能证明叙事成立。控制器的`content_review`只登记实际审核证据；没有执行的判断不能因字段齐全而写通过。

## 可直接使用的方法资源

| 需要解决的问题 | 入口与内容 |
|---|---|
| 图表还是表格 | [表示选择](../skills/how-to-report/references/ppt-data-display.md)：解释增长、差异、分布或状态用图；名单与明细查询用表；混合任务各有分工。无需先穷尽图种才允许表格，也不为孤立数字强造柱图 |
| 栅格如何选 | [基本原则](../skills/how-to-report/references/ppt-grid-design.md)与[16种模式详解](../skills/how-to-report/references/ppt-grid-patterns.md)：场景、读序、对齐、容量风险、改选信号和现有容器映射 |
| 长文本怎样结构化 | [说明页方法](../skills/how-to-report/references/ppt-explanatory-content.md)：意思单元、短语导航、机制与条件保留、图文分工，避免把长句删成无意义标签 |
| 字体与全局颜色 | [文字标准](../skills/how-to-report/references/ppt-text-standard.md)、[颜色标准](../skills/how-to-report/references/ppt-color-standard.md)：14pt正文、最小角色9pt、统一段距/行距与语义色；新设计纯色优先 |
| 图种与拓扑能力 | [图表使用场景](../skills/how-to-report/references/ppt-chart-usage.md)、[计算排版合同](../skills/how-to-report/references/ppt-layout.md)和[Storybook](../skills/how-to-report/references/ppt-storybook.md)：先查真实输入、数量域及编辑等级再调用 |
| 是否还可减少一页 | [全稿减页审核](../skills/report-audit/references/ppt-visual-review.md#全稿减页挑战)：先保理解关系，再用真实测排证明容量，不把删内容或藏入不可用备注当合页 |

16种模式包含通栏、等宽双栏、2:1和1:2主次、三栏、2×2、上总下分、标签解释行、图证解释、横向条带、中心外围/循环、时间线、流程附注、分层架构、连续正文多栏和同维度对照行。它们并非16个独立算法；显式列Grid直接子项支持有限column_span，当前没有完整CSS、自动跨栏续排、通用keep/孤行控制、row_span/subgrid或任意连线避障。

## 中性结构样例如何取用

完整仓库提供[21个咨询结构样例](../examples/consulting-explanatory/README.md)和[公开材料研究派生样例](../examples/consulting-public-patterns/README.md)。样例采用本项目tokens和合成内容，提供实际作者工程、槽位合同和预览。具体状态以各目录manifest与说明为准。

这些目录是**独立样例索引**，当前不会自动出现在`report_engine.py library`中，也不是`catalog-build`接收的原生PPT资产catalog。查本地索引、读取guide与slots后，使用该目录的`instantiate.py`绑定内容，再把产生的作者JSON送入正常`build --geometry-policy computed`。绑定脚本不计算最终几何，新增内容仍要重测和看目标成图。

方法资源随两个独立Skill包按职责分发；这些仓库级样例需保留完整目录，不表示仅安装Skill即自动包含它们。源PDF、用户业务材料与真实汇报不随公开样例发布。源结构的语义内化不等于PDF原样保真，原生对象、图表和截图各按实际编辑等级说明。

## 研究范围

本轮有界研究实际查看7家机构共22个公开PDF页，另有用户提供的截图及本地材料研究。来源与可迁移方法见[说明页研究依据](../skills/how-to-report/references/ppt-explanatory-content.md#研究如何影响方法)。这不是全网穷尽，也不认证任何机构的统一模板规范、整册论证或未读页面。

吸收的是分类—展开—机制—案例的承接、图表与说明的分工、同级角色与读序。样例排除封面和装饰副标题；帮助对象识别、范围和理解的功能标题保留。密集阅读PDF的微小字号、品牌、渐变、无作用的大装饰不会直接变成默认样式。
