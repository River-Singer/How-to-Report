# Knowledge 0.1.0：首批来源与实现记录

日期：2026-10-26（客户端 UTC）。用于 package 0.2.0 的第一批可选知识卡。实现范围仅 `project/skill-src/shared/knowledge/**`；未修改研究总索引、生成包、入口或行为探针。

## 交付与方法

已编写 metadata-only 目录和12张卡，覆盖 PM、BUS、FIN、SWE、DATA 各两张，MKT、COM 各一张。卡片自身版本0.1.0，与发布包版本和 Run 契约版本分开。

每卡含实际判断输入、动作、输出、独立审计问题、停止/降级边界和出处。正文为原创中文综合，不搬入第三方全文、长引文、图像或框架评分表。来源负责支撑特定概念，汇报/Graph 操作是本项目设计；没有文献证明这些卡已提高模型表现。

目录只列 ID、版本、名称、适用问题、来源与加载范围。查目录不意味着已读正文；跟随正文或外部来源仍须在对应实际授权范围。未回答/拒绝/撤销不读卡，已有同范围许可不重复申请。卡片的同源副本不成为独立项目事实，领域不成为固定正交轴或章节。

## 实际原文核对范围

本轮使用 `web.run` 搜索、打开、页内定位读取以下官方/作者一手页面。行号仅用于当前网页文本定位，不保证未来网页不变。没有取得完整 PDF、执行源站示例、查看全部图片或审查全部关联研究。

| 来源 | 实际读取范围 | 使用卡片 / 边界 |
|---|---|---|
| [Teal Book 18: Reporting](https://projectdelivery.gov.uk/teal-book/home/part-e-planning-and-control/chapter-18-reporting/) | §18.1–18.4、18.5、18.6.1.1–18.6.1.2及相关段落；页面2026-07-01更新 | PM-01；不采用其管理层级刻板映射，实际受众优先 |
| [Teal Book 30: Quality management](https://projectdelivery.gov.uk/teal-book/home/part-f-solution-delivery/chapter-30-quality-management/) | §30.6.2正文，尤其30.6.2.4质量记录；相关工具段落 | PM-01；验收标准与记录，非代组织验收 |
| [Teal Book 16: Planning](https://projectdelivery.gov.uk/teal-book/home/part-e-planning-and-control/chapter-16-planning/) | §16.6.3.4–16.6.3.7相关段落：范围、活动依赖、计划整合；不是全章阅读 | PM-02；不据局部清单认证关键路径 |
| [Teal Book 20: Risk management](https://projectdelivery.gov.uk/teal-book/home/part-e-planning-and-control/chapter-20-risk-management/) | §20.6.2.5、20.6.3.3–20.6.3.7相关正文；风险/问题及剩余风险 | PM-02；不引入固定风险矩阵或概率数值 |
| [Teal Book 19: Benefits management](https://projectdelivery.gov.uk/teal-book/home/part-e-planning-and-control/chapter-19-benefits-management/) | 复核§19.1–19.6.1.3及19.6.2，另看到时间/变更/评价相关段落；沿用前轮已读范围；页面2026-07-01更新 | BUS-01、FIN-01；只支撑收益实现及现金/非现金区别，非企业会计规则 |
| [HM Treasury, Green Book 2026](https://www.gov.uk/government/publications/the-green-book--2/the-green-book-2026) | 定向读第2/4章 BAU、选项相关段，第6章 time horizon、成本/沉没成本及 sensitivity/switching values，第8章机会成本定义；网页2026-02-05更新。首次搜索结果落到旧发布路径，规范页面重定向如本链接 | BUS-02、FIN-02；借鉴有限比较与假设检验原则，不复制公共部门贴现率、固定年限、财务核算或政府价值优先级 |
| [DORA software delivery metrics](https://dora.dev/guides/dora-metrics/) | 官方正文，包括五指标定义、情境及常见误用；页面2026-01-05更新；未逐篇复核关联研究 | SWE-01；五指标是当前资料定义，不是个人生产率评分 |
| [SPACE 作者机构页](https://www.microsoft.com/en-us/research/publication/the-space-of-developer-productivity-theres-more-to-it-than-you-think/) | 书目和摘要；本轮重新成功读取，仍未读论文全文；前轮正文403记录保持 | SWE-01；只使用“不能用单一指标/活动量替代开发生产率”的明确原则 |
| [Google SRE Chapter 4](https://sre.google/sre-book/service-level-objectives/) | Service Level Terminology、Indicators in Practice、Aggregation、Standardize Indicators及Objectives相关正文；未取页面示例具体服务目标作为现行规格 | SWE-02；SLI/SLO/SLA、代理测量与聚合限制，非服务承诺模板 |
| [Google SRE Chapter 17](https://sre.google/sre-book/testing-reliability/) | 导论、传统/生产测试、配置版本与相关测试段落（文本约59–129行）；未跑源站示例 | SWE-02；测试证据覆盖边界，不是全套可靠性工程卡 |
| [Government Data Quality Framework: guidance](https://www.gov.uk/government/publications/the-government-data-quality-framework/the-government-data-quality-framework-guidance) | 定向读 action planning 中适用性段落、metadata、communicating data quality，尤其定义变化、完整/唯一/一致/及时/有效/准确；未全读maturity models | DATA-01；数据是否适合当前判断，避免把完整性当准确性 |
| [GOV.UK measuring completion rate](https://www.gov.uk/service-manual/measuring-success/measuring-completion-rate) | 计算、交易起止、save-and-return及跨线上线下相关正文；页面2021-02-19更新 | DATA-01；用于分母及跨期匹配的具体依据，政府交易与公开频率不通用化 |
| [NIST Experiments and Experimental Design](https://www.itl.nist.gov/div898/handbook/ppc/section1/ppc136.htm) | 短网页正文，相关与因果、潜在第三因素及实验设计用途；未追读其整个设计方法目录 | DATA-02；不能据观察关联作因果认证 |
| [NIST Confidence Limits for the Mean](https://www.itl.nist.gov/div898/handbook/eda/section3/eda352.htm) | 定义、解释和检验相关文字；看到了示例但未下载/执行示例数据或查看图像像素 | DATA-02；未把均值 t 区间公式推广为任意分布或任意依赖数据的算法 |
| [GOV.UK learning user needs](https://www.gov.uk/service-manual/user-research/start-by-learning-user-needs) | writing / validating user needs及与user stories关联的相关正文 | MKT-01；用户问题与证据，未宣称通用市场分析框架 |
| [GOV.UK measuring digital take-up](https://www.gov.uk/service-manual/measuring-success/measuring-digital-take-up) | 计算、discovery/alpha/beta相关正文，页面2021-02-19更新 | MKT-01；数字渠道采用口径，不照搬推广指标目标或机构义务 |
| [CDC Clear Communication Index: How to Use](https://www.cdc.gov/ccindex/tool/how-to-use.html) | 正文，尤其受众/目标/消息、独立审阅与实际受众测试；未下载评分附件 | COM-01；不采用分数阈值、人数、固定版式，不把清晰度等同真实性 |
| [CDC uncertainty item](https://www.cdc.gov/ccindex/tool/page-11.html) | 开头原则段；网页医学案例只作来源上下文，不转入卡片 | COM-01；未知披露，非健康咨询或完整危机传播标准 |

## 本次新增的实质边界

- PM 首版采用公开 Teal Book 的明确段落，不冒称已研读 PMI/PMBOK 完整体系。
- 财务首版是汇报主张与模型输入审查，未覆盖税务、会计确认、金融产品估值、完整 NPV 算法；不提供统一 ROI 公式或默认贴现率。
- 数据首版覆盖比较/聚合/结论强度与必要证据，不实现自动因果识别或统计模型选择。
- 产品/营销与沟通/公关为轻量范围，不含广告归因、品牌战略、市场规模或完整危机处理工作流。
- 同域来源和相同机构材料不能证明“多方独立验证”；全部卡片都需要实际任务材料。源站实践适用范围和本项目迁移分别标注。

## 验证记录

本实现者没有读取 `validation/cognitive-v1` 下的新案例或判定协议，也没有把旧研究案例答案写进卡片。只执行本目录的文件/本地链接检查；包构建、独立质量检查和真实前向使用由根代理在源冻结后执行。无全局安装、提交或推送。

本目录静态复查已通过：13个 UTF-8 Markdown 文件、12个正文入口链接可解析，无替换字符或缺失文件。此检查不证明方法有效、专业内容已全面覆盖或许可行为已执行。
