# 长文本说明页：先保关系，再形成短语与层次

用于资讯、介绍、技术机制和方案评审。沿B/C已经成立的内容路线与[制作前设计评估](ppt-design-preflight.md)执行；数据表示先按[听众任务](ppt-data-display.md)决定，不能因为文字多就一律转图或删成标签。

## 从完整解释变成可读页面

1. **确定本页要解释的对象和问题**：定义是什么、分哪些类、怎样工作、与前文有什么关系、什么条件会改变理解。每段只承担明确作用，先保留听众需要的前提与限定。
2. **提取意思单元**：将对象/动作/产物或条件/结果作为完整单元。类别名做导航，必要机制保留一句解释，来源、例子和例外靠近所支持的意思。不是按字符数截句，也不把标题当成论据。
3. **只压缩重复表达**：重复主语可由组标题承担；并列项统一语法；删除空泛导语和重复总结。不能删掉谁做、作用于什么、先后、条件、范围及尚未证实的状态。
4. **映射可见关系**：真实同维度并列用同构列/解释行；先后用时间线或流程；包含用层级；机制以输入—处理—产物展开；同一连续论证可用正文分栏。先选择关系，再选择栅格比例。
5. **测量而非猜字数**：按14 pt正文、统一字阶和段距测量真实中英文内容。窄栏导致频繁断句时改解释行或两栏；必要内容不因无法塞进三卡而降级成小字。

例如合成原句：“需求提交后，业务负责人先确认范围；范围未确认时不能进入技术评估。技术评估通过后，才把成本影响交给委员会。”可结构为“范围确认 → 技术评估 → 成本评审”，并在对应节点保留“业务负责人”“范围确认后才进入”“技术通过后提交”。只留下三个名词会丢失责任与准入条件。该例是方法示范，不是用户项目事实。

## 可选结构与失败分支

| 内容任务 | 首选候选 | 需要保留的关系 | 常见失败与改法 |
|---|---|---|---|
| 三类能力，各有定义和例子 | 三栏同构；长文改解释行 | 类别相同层级、各栏对应槽 | 一栏过长不机械等高，改两栏或逐行 |
| 生命周期及各阶段职责 | 时间/循环骨架＋局部解释 | 循环与线性顺序分清；解释归属于阶段 | 中间大图、四周小字不可读时缩骨架并扩说明 |
| 分层系统、接口与数据来源 | 分层架构＋侧注 | 包含、依赖、输入/输出 | 无依据箭头删除；复杂线先用原图或已有受支持结构 |
| 总背景→共同能力→具体案例 | 多层条带 | 上下层为什么关联 | 不把无关三题拼成一页；必要转场保留 |
| 连续研究论证 | 通栏限行宽、连续双栏 | 同一段内前提与结论，合法断点 | 当前没有通用跨栏续排，声明段落组并测排 |
| 范围/供应商/人天供逐项核对 | 明细表 | 对象与属性的交叉定位 | 不强造图；另有分布问题再增加承担解释的主图 |

详细排布见[16种栅格与内容模式](ppt-grid-patterns.md)。它们是设计候选，不全是不同算法或已注册recipe。当前row/column/grid、参数模板和topology各按真实合同调用；没有通用keep-with-next、孤行控制、跨栏流动及任意连线避障。新增需求先查现有可用结构和源图，不能由AI补手写最终坐标。

## 研究如何影响方法

有界研究实际查看7家机构共22个公开PDF页，另看用户3张截图和两份本地PDF的16个表格相关页。不是全网穷尽，也没有把整册内容或作者私有方法认证为事实。

- Deloitte公开AI审计材料：从工具用途进入可信使用框架；局部示例说明“能力介绍”和“使用条件”需要不同层次。[官方PDF](https://www2.deloitte.com/content/dam/Deloitte/se/Documents/audit/AI%20presentation%20for%20the%20Audit%20Committee%20-%20Second%20draft.pdf)
- KPMG企业服务方案：主题条带内对齐解释与图示，再区分概览、任务与职能；研究看PDF页8、9，不沿用五窄栏小字。[官方PDF](https://kpmg.com/content/dam/kpmgsites/th/pdf/2025/05/future-of-corporate-services-presentation.pdf.coredownload.inline.pdf)
- EY网络安全说明：概览中的类别在后页展开关系；研究看PDF页8、9、15，不复制纹理、渐变与六窄栏。[官方PDF](https://www.ey.com/content/dam/ey-unified-site/ey-com/en-us/noindex/documents/ey-frontier-ai-in-action-rethinking-cybersecurity-and-resilience.pdf)
- BCG客户互动方案：从三类方案概览到能力说明、分层机制和案例；研究看PDF页7–10，提炼概览—展开承接及同构说明槽。[官方PDF](https://www.bcg.com/assets/2024/executive-perspectives-ai-and-genai-in-customer-engagement-4dec.pdf)
- Accenture技术趋势报告：研究看PDF页8–11，观察连续正文、章节入口和时间线；阅读型跨栏续句需要重新组织成投屏可读单元。[官方PDF](https://www.accenture.com/content/dam/accenture/final/accenture-com/document-3/Accenture-Tech-Vision-2025.pdf)
- PwC/WEF研究：先定义分析维度，再给双轴情景概览，随后逐项解释影响。二维矩阵需要两个实际维度，不能把任意四段装成四象限。[官方PDF](https://www.pwc.com/gx/en/issues/artificial-intelligence/wef-leveraging-generative-ai-for-job-augmentation-and-workforce-productivity-2024.pdf)
- Bain技术报告：比较证据、时间变化和带类别导航的说明段可围绕一个问题逐步展开，不必给每段套大形状。[官方PDF](https://www.bain.com/globalassets/noindex/2025/bain_report_technology_report_2025.pdf)

阅读型报告可放大的密集小字和跨页续句，不直接迁移到投屏PPT。样例采用本项目tokens、原创合成内容，不复制品牌、装饰副标题或封面；承担对象识别、范围和读序的功能标题继续保留。局部结构的可借鉴性不代表原PDF已被原样重建。
