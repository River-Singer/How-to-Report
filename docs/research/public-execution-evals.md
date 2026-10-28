# Research: Skills执行、评测与可复现计算

- Query: 针对共享对话第33–38轮所引用的Skills与计算资料，核验渐进加载、宿主边界、独立审计、基线公平性以及真实计算凭证。
- Scope: mixed；8份一手来源的定向章节阅读，结合已确认项目需求提出研究建议；不修改产品代码或冻结接口。
- Date: 2026-10-26（本轮日期由主代理确认）
- Status: 8份来源成功访问；阅读深度逐项列明。没有运行产品、安装计算库或执行B0/B1/B2评测。

## Findings

### 结论与来源身份

本项目适合把可变的专业判断放在按需读取的方法Reference中，把数值执行、格式校验和渲染检查交给可观察的工具。独立评测、文件持久化、上下文保护和子代理隔离是宿主能力；Skill说明能够要求并检查这些能力，但不能单靠文字实现它们。这是下列来源与第33–38轮需求的综合判断，不是某个框架的强制架构。

| 本研究编号 | 注册表关联 | 官方来源、实际版本/访问状态 | 实际阅读层级 |
|---|---|---|---|
| E1 | PS126；PS121为同规范源码路径 | [Agent Skills specification](https://agentskills.io/specification)，2026-10-26公开现行页，200 | 格式、目录、渐进加载、引用、校验章节；主体规范已读 |
| E2 | PS119 | [Adding skills support](https://github.com/agentskills/agentskills/blob/main/docs/client-implementation/adding-skills-support.mdx)，main公开源码，200 | 生命周期/本地云端差异、激活、资源枚举、压缩与委派章节；非逐行读全文件 |
| E3 | PS128；不自动替PS127旧路径背书 | [OpenAI skill-creator](https://github.com/openai/skills/blob/main/skills/.system/skill-creator/SKILL.md)，main公开源码，200 | 核心原则、自由度、文件职责与渐进加载；创建命令和全部模板未逐行核验 |
| E4 | PS133 | [Testing Agent Skills Systematically with Evals](https://developers.openai.com/blog/eval-skills)，官方文章，Markdown通过普通GET成功 | 成功定义、触发/反例、trace校验、结构化rubric、扩展原则；未逐行审计示例runner代码 |
| E5 | 补充查证；对话方向的原作者实现 | [Anthropic skill-creator](https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md)，main公开源码，200 | 渐进加载、with/without基线、评分/汇总、迭代、盲比、宿主降级；非全部脚本实现 |
| E6 | PS129；PS130已为别名 | [Anthropic authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)，官方现行文档，200 | 渐进加载、引用深度、evaluation-first、读取行为观察、可验证中间产物、执行依赖章节 |
| E7 | PS039 DuckDB仓库的定向官方补充 | [DuckDB non-deterministic behavior](https://duckdb.org/docs/2.0/operations_manual/non-deterministic_behavior)，stable跳转到2.0 LTS，200 | 全文96行已读，含示例及限制 |
| E8 | PS039的定向官方补充 | [DuckDB numeric types](https://duckdb.org/docs/2.0/sql/data_types/numeric)，stable跳转到2.0 LTS，200 | 整数/DECIMAL/浮点/舍入章节已读；UUID章节不属本题 |

PS121、PS127、PS039仅提供关联来源，不能因读了等价规范或子文档就把这些不同URL自动标为“全文已读”。E5/E7/E8需作为补充查证记录；不伪造它们在历史对话中的引用ID。

### 1. 渐进加载的边界

E1定义最小载体为有frontmatter的SKILL.md；name/description用于发现，完整主体在激活时进入上下文，资源按需读。小于500行、主体约5000 tokens是建议，不能把建议当格式校验的强制上限。`allowed-tools`仍是实验字段，支持依实现而异。[规范](https://agentskills.io/specification)

E3强调已有模型能力不必重复教学；易错且重复的操作适合脚本，条件变化大的判断保留自由度；Reference承担细节、assets承担输出资源。[OpenAI指导](https://github.com/openai/skills/blob/main/skills/.system/skill-creator/SKILL.md)

**项目推导：**双Skill主体应交代目标、关键质量约束、方法路由和退出/回退条件；具体方法、图表策略、数据口径与宿主差异分文件。入口必须给出“何时读/能解决什么/边界”，不能只给方法名。用户反对预置答案与僵化流程，因此Reference应教认知动作，不应藏入MASTer结论或固定页面比例。能被发现不等于已被正确调用，需查看执行记录中实际读取了哪些资源。

### 2. 宿主适配不是再造Runtime

E2允许文件读取或专门激活工具；本地目录发现与云端分发方式不同。资源枚举不等于预读全部文件，子代理委派仅部分客户端支持。技能上下文的保留和去重也由宿主实现。[接入指南](https://github.com/agentskills/agentskills/blob/main/docs/client-implementation/adding-skills-support.mdx)

**项目推导：**先探测当前可用的持久文件、执行、渲染、子代理隔离、联网与产物展示能力，再选择路径；同一语义产物可有不同宿主执行方式。最小可用路径是本地/云端用户可见工作区与明确阶段产物，不需要为V1附带调度平台。无执行环境时计算必须标未验证；无渲染器时只能做结构检查；无隔离上下文时审计应披露独立性不足。

**不能据此宣称：**所有平台的文件权限、脚本语言、网络、子代理和压缩策略相同；某厂商当前产品说明也不能成为跨宿主永恒假设。应按能力检测而非品牌名称硬编码。

### 3. 基线与独立审计各验证什么

E4把评测对象分为产物、过程、风格和效率；要求记录trace与artifact，确定性检查补充结构化rubric，而不是让文件存在性承担全部质量证明。文章包含显式、隐式、语境与不应触发的反例。[OpenAI评测文章](https://developers.openai.com/blog/eval-skills)

E5的新Skill基线为相同任务但无Skill，修改Skill时可以使用旧版快照；可程序验证的断言交给脚本。盲比较给独立评审者两份匿名产物。其无子代理宿主降级明确承认同上下文试做更弱，不能形成同等基准证明。[Anthropic实现](https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md)

**项目推导：**B0/B1/B2应固定输入材料、题目、模型/参数、可用工具、预算和评价标准，仅改变待比较的方法条件；保存版本、输出、trace与失败。此处是公平比较设计建议，不是已跑结果。小样本先找缺陷，不能由一次胜出宣布普遍增益；现有25条eval定义只表示有检查入口。

镜像审计至少区分三层：

1. **结构证据**：引用有效、口径字段可定位、计算/渲染确已执行；可由脚本检查。
2. **内容判断**：来源能否支持主张，反证/限制是否保留，视觉有没有新增因果或确定性；需要专业rubric和可定位证据。
3. **独立性证据**：评审从原始来源与最终产物重建含义，不先接受生成者的自评解释；记录独立上下文是否真实可用。

独立进程/代理只减少特定的上下文污染，不保证判断正确；重新运行同一计算也不等于独立复核公式。同一模型可以做受控的隔离评审，但不能因此声称消除了模型共有偏差。此为项目审计设计推论，来源没有证明“第二个Agent自动保证真实性”。

### 4. 可复现计算应留下什么

E7表明SQL未要求排序时结果顺序可变，多线程浮点聚合也可能有细小差异；限制线程、显式排序能缓解相应情况。E8说明DECIMAL加减乘可保持定点结果，但除法仍产生近似浮点；类型范围、舍入以及异常值语义都须考虑。[非确定性](https://duckdb.org/docs/2.0/operations_manual/non-deterministic_behavior)、[数值类型](https://duckdb.org/docs/2.0/sql/data_types/numeric)

**项目推导的最小计算凭证**（字段建议，尚未冻结schema）：

| 凭证内容 | 验证的问题 |
|---|---|
| 输入来源ID、文件版本/hash、时间范围、粒度、过滤/缺失/去重口径 | 到底算了哪批数据，分母与总体是否一致 |
| 原始SQL/脚本、参数、公式出处和假设 | 数字是否来自真实执行，公式是否适合业务问题 |
| 实际运行库/引擎版本、关键配置、随机性与精度/舍入规则 | 别人能否在可说明的条件下重算 |
| 实际输出、日志、执行成功或错误状态、输出版本 | 禁止把拟运行代码或LLM口算当已执行结果 |
| 校验方式、误差容忍值、独立复核差异及结论 | 复跑一致、实现正确、业务口径正确分别是否有证据 |

对常规汇总，固定输入与SQL、显式输出顺序以及明确舍入通常比引入复杂计算框架更有价值。关键数字可用不同实现路径、手工小样本或守恒/范围检查复核；适用性由问题决定。`threads=1`不是所有任务的强制设置；固定版本/hash也不会使错公式变对。算出相关性、工时差或可释放容量仍不能自动升级为因果效果、已实现成本节省或业务价值。

### 5. Reference与评测如何共同迭代

E6建议先观察无Skill任务缺口，建立代表性评测，再写最小指令；同时观察模型实际阅读路径、漏读引用和反复读取。深层Reference链可能导致遗漏；可验证中间产物有助提前发现执行问题。[官方最佳实践](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)

**项目推导：**先选少数有区分力的案例：同素材不同受众、缺证仍被要求强结论、数字有口径冲突、图形偷偷升级因果、工具缺失降级、用户中途改目标、长期偏好与本次要求冲突。每次失败说明缺的是方法知识、调用时机、语义约束还是工具能力，再改相应层；不能通过不断加MUST、固定观点数或背熟案例答案提高测试分数。

## Files Found / Code Patterns / Related Specs

- `public-sources.json` / `public-sources.md`：历史可见引用注册表；当前清理后171个资料链接，4别名、9缓存图排除。主代理接管后续阅读状态同步。
- `public-source-snapshots/manifest.json`：8份官方材料的读取URL、获取状态、访问日期、SHA256和保存路径；保存不代表每行已读。
- `public-source-snapshots/agent-skills-spec.md`：规范主体；例如渐进加载、引用深度与validation章节。
- `public-source-snapshots/adding-skills-support.md:234`：激活机制；`:304`资源按需读取；`:314`上下文管理；`:331`可选子代理。
- `public-source-snapshots/openai-skill-creator.md:28`：简洁与自由度；`:127`渐进加载；不把该文当当前执行Skill调用。
- `public-source-snapshots/openai-eval-skills.md:21`：成功定义；`:153`触发测试；`:189`行为trace；`:279`rubric。
- `public-source-snapshots/anthropic-skill-creator.md:169`：基线；`:221`评分；`:325`盲比；`:420`宿主降级。
- `public-source-snapshots/anthropic-best-practices.md:251`：分层加载；`:746`先评测；`:837`观察读取；`:1012`中间产物验证。
- `public-source-snapshots/duckdb-nondeterminism.md:46`：多线程浮点差异；`:65`缓解方式。
- `public-source-snapshots/duckdb-numeric.md`：当前2.0数值类型文档；准确原文与hash在manifest，不能把Context7旧路径视作安装版本。
- 需求上下文：`shared-conversation-turns/round-33.md`至`round-38.md`；`.trellis/workflow.md`及前后端spec索引已读。本研究没有生成实现；现有产品规范仍需主代理收敛。

## Caveats / Not Found

- Context7已先用于DuckDB/Claude资料定位：`/duckdb/duckdb-web`、`/websites/platform_claude_en`。DuckDB返回的`docs/current/...`源码路径实际404，随后沿官方stable页跳转，确认2.0 LTS版正文并保存；这是明确的路径更新，不能隐藏。
- E4的`.md`链接在web工具因text/markdown类型返回错误；普通HTTP GET成功获取19246字符，并完成上述章节阅读。
- GitHub main及滚动文档未固定commit；snapshot hash提供本次读取证据，不代替实现阶段锁版本。未验证所有嵌套脚本、附件或例子。
- 没有确认E5所列特定宿主限制在全部产品版本成立；仅采纳按实际能力降级的原则，不引用其产品品牌作为永久约束。
- 没有任何官方来源证明本项目已经改善汇报效果、保证审计无误或必须选择DuckDB。以上计算凭证、评测设计和职责划分是本项目研究建议，待实现与真实评测验证。
