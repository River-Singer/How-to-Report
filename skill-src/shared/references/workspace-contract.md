# 工作区契约 0.1

本契约管理可比较的身份、版本、状态和引用。它不把开放思考限制成业务字段表，也不证明主张正确。逻辑职责见 [多图模型](graph-model.md)，能力限制见 [宿主能力](host-capabilities.md)。

## 文件与权威来源

| 资产 | 何时需要 | 权威内容 |
|---|---|---|
| `run.json` | 确需持久追溯、续接或版本管理并采用Run时 | 模式、输入/产物版本、工作和检查状态、其他资产位置 |
| `run.md` | 采用Run且需要可读笔记时 | 目标、范围、确认/假设、策略图、理由摘要和缺口；不另造机器状态 |
| `semantic.json` | 关键对象需要结构化引用时 | 认知/内容对象与带语义的关系、精确版本依赖 |
| `tasks.json` | 存在值得显式管理的工作依赖时 | 实际工作、前置和输入/结果引用 |
| `events.jsonl` | 有需留痕的许可/检查/变化时 | 有序事件；不是权限拦截系统 |
| 实际输出与检查说明 | 真正产生时 | 汇报方案、分析结果、审计报告、计算凭证等 |
| 私有 `profile.json` | 用户启用画像时 | 已确认偏好/经历，独立于 Run 和安装包 |

普通内容交付可以只有一份Markdown；文件能力存在不要求初始化Run或图。采用Run后才适用以下必需字段与结构检查。不要覆盖旧 Run 或原材料。无写入能力时交付可复制等价内容，并明确未持久保存。记录公开决定、证据和理由，不记录模型私有思维链。状态展示从 `run.json` 派生或指向其记录；源清单不在每张图重复维护。

## Run 清单

必需字段：

```json
{
  "contract_version": "0.1",
  "run_id": "run-example",
  "mode": "analyze-first",
  "work_status": "in_progress",
  "sources": [],
  "artifacts": [],
  "checks": []
}
```

- `mode`：`create | revise | audit | analyze-first`。
- `work_status`：`in_progress | completed | blocked`，只描述本次工作完成情况。
- 可选 `notes_ref`、`semantic_ref`、`tasks_ref`、`events_ref` 是 Run 内相对文件路径。
- Source/Artifact：`id`、正整数 `revision`、非空 `ref`；按需加 `scope`、`content_hash`、`version_note`、`uses`。`content_hash` 可省略；若提供，须为实际计算的 SHA-256 值（64个十六进制字符），不能用“未记录”等文字占位。本地文件可由校验器检查字节，哈希不证明已阅读或内容真实。
- Source/Artifact `ref` 可为 Run 相对文件、用户明确提供的本地绝对文件或 `https`/`http`/宿主 `workspace:`/`page:` 定位；校验器不会联网读取。远程引用仅做格式检查，不能据此声称已访问。
- 其他 Run 自有文本/记录引用须留在本 Run 内；URL 或外部文件作为 Source 登记，再通过稳定ID引用。

Profile 使用引用、能力观察和审计独立性可作为附加字段记录，本版校验器不验证这些自报事实。不要将工具名称存在写成能力已实测。

## 精确引用与身份

引用形式为 `{"id":"s1","revision":1}`，可加 `locator` 指明对应版本中的页码、段落或元素。标题可改变，ID不随标题改变。`revision` 是内部正整数；外部版本号另记。布尔值不是整数版本。

所有 Source、Artifact、语义节点和 Task 共用本 Run 的对象身份域；`(id, revision)` 唯一，同一ID的历史版本保持同类对象身份。保留历史版本时，不以文件名或最大版本号自动断言哪份数据是当前业务口径。跨 Run 输入先登记为本 Run Source，保存原始位置/版本说明。

`uses` 的方向是消费者 → 使用的精确版本，用于失效影响；`links` 表达论证/叙事关系。引用存在不代表前提为真。

本次必要的计算定义、输入和补充材料按实际用途登记为 Source/Artifact，依赖仍用 `uses`。可选 [计算说明](../assets/review/calculation-note.md) 和 [证据清单](../assets/review/evidence-inventory.md) 可供公开说明；不新增必填文件或 schema。交付状态与最小附件选择见 [证据交接](evidence-handoff.md)，具体复算边界见 [数值方法](numeric-evidence.md)。

## 语义索引

可选文件包含 `contract_version`、相同 `run_id` 和 `nodes` 数组。每个节点有：

- `id`、`revision`、非空 `kind`。
- `text` 或 `text_ref` 恰好一种；后者引用 Run 内实际文件，可附 `#定位`。
- 可选 `status`、`uses`、`links`、`verification_refs`；额外字段可用于具体任务。
- `kind` 的核心含义包括 `hypothesis`、`finding`、`claim`、`obligation`、`content_unit`、`content_module`、`presentation_beat`、`page_plan`，允许额外类型，不要求每次全部出现。
- `links` 元素：`{"type":"qualifies","target":{"id":"c1","revision":1}}`；关系词开放，方向和含义需可理解。语义关系允许循环。

证据状态：`proposed` 候选、`needs_evidence` 缺证、`verified` 在指定范围校核、`disputed` 有冲突、`stale` 依赖变化待复核、`invalidated` 已证伪/不再适用。它们不是概率，也不是只向前的固定状态机。

`verification_refs` 是本 Run 内不重复的 Check ID 字符串列表，例如 `["check-1"]`，不是带 revision 的业务对象引用。`verified` 要有该列表指向本 Run `checks` 中该对象精确版本的 `pass` 记录。校验器只证明记录对应，不认可其方法或结论。任务 `completed` 不能替代这种记录。

同一精确节点版本还有任何 `fail/not_run/not_assessable` Check 时，不能只选其中的 pass 就标为 `verified`。先保留冲突并实际核对；确已解决、撤回或范围不同，可在该节点追加可选 `verification_dispositions`：

```json
{
  "verification_scope": "本次有依据的限定范围",
  "verification_dispositions": [
    {
      "check_id": "earlier-failure",
      "disposition": "resolved",
      "reason": "说明实际复核如何解决原冲突",
      "detail_ref": "checks/resolution.md",
      "resolving_check_id": "actual-new-pass"
    }
  ]
}
```

每个处置必须唯一对应这个精确版本的非 pass Check，带非空理由与实际非空详情。`resolved` 须引用本节点 `verification_refs` 中同精确版本的 pass；`withdrawn` 说明撤回依据；`different_scope` 说明为什么不属于节点声明的 `verification_scope`。后两种不带 `resolving_check_id`。不通过 scope 文本相等、Check 顺序或最新记录覆盖推断范围；不同范围也需明确说明。其他版本的失败不自动阻塞本版本。处置是可审计声明，不证明撤回正确或检查真实执行；不得删除历史失败来绕过。Artifact 接纳仍保留原有“所有精确目标 Check 都为 pass”的保守规则，不沿用语义节点的处置豁免。

## 检查记录

Check 有 `id`、精确 `target`、`status`、Run 内 `detail_ref`。状态为 `not_run | pass | fail | not_assessable`。`pass` 还需非空 `method` 和 `scope`，详情文件必须实际存在且非空。

`target` 使用已登记对象的 `id` 和 `revision`，章节可放其 `locator`。`detail_ref` 使用实际文件路径，例如 `audit.md`；可附 `#check-1`，但校验器只检查文件，不验证锚点存在。不要写成 `audit.md §2–§4` 这样的伪文件名；章节说明放在详情正文或定位字段。

详情说明实际输入、动作/方法、结果、适用范围与限制；人工核对也可以，但不能编造执行。检查旧产物通过只对旧版本有效。记录自报通过仍是审计对象，不是事实认证。

补证或重查后，当前摘要、Check 状态、方法/范围与详情应一致指向本次实际结果；历史原判可另存快照或明确标作历史，并保留旧证据和适用范围。不要同时把已撤回判断和新判断表示为同一范围的当前结果，也不能仅添加说明就默认为缺证项已通过。新材料的收到时间不能倒写成前次已经持有或检查。

## 可选 Task 快照

文件有相同 `contract_version`、`run_id` 和 `tasks`。每项有 `id`、`revision`、`objective`、`completion`、`status`、`input_refs`、`prerequisites`、`result_refs`。`completion` 是非空自然语言，描述可观察的完成标准；目标句不能替代完成标准。

- 状态：`planned | blocked | ready | running | completed | failed | cancelled | stale`。
- 输入和结果是精确对象引用；前置也是精确引用，且目标必须是本快照中的 Task。
- 只有前置关系作为执行 DAG 检查，不把语义图拓扑排序。`input_refs` 属于版本有效性依赖；`result_refs` 记录产物归属，不反向推导依赖。
- 工作完成不保证结果可接纳。核对来源、版本、口径、方法和限制后才能用作依据。

## 版本变化与只读影响分析

用 [校验器](../scripts/validate_run.py) 检查记录：

```text
python <本Skill目录>/scripts/validate_run.py <Run目录>
python <本Skill目录>/scripts/validate_run.py <Run目录> --changed s1@1
```

`--changed` 可重复。输出JSON的 `valid` 只说明结构/声明的一致性；`errors` 定位问题；`affected` 列出沿节点/产物 `uses` 与 Task `input_refs` 可达的消费者，排除变化输入自身。论证 `links`、Task 前置和结果归属不会自动成为该传播边。

传入适用性发生变化的旧精确版本：`s1@1` 被 `s1@2` 替换时，查询 `--changed s1@1`。对新版本 `s1@2` 返回空集，不证明仍依赖旧版本的结论有效。

退出0为结构接受，1为无效数据/声明，2为调用或实际读取失败。校验器不写文件、不联网、不重算、不选择业务最新版本。文件变化未被声明、来源漏记、日志漏记和错误业务公式不能由它自动发现。

出现变化时保留旧版本及检查，对影响集合做真实复核；根据实际变化修订必要对象与产物。若依赖记录不完整，应保守扩大复核并披露，不能声称已穷尽影响。

## 可选版本选择与接纳扩展

生成侧工具可在 `run.json.version_state` 保存自己的0.1扩展：有序的显式选版决定，以及精确产物、已有检查和实际证据指纹绑定的接纳声明。它不是Run契约的必填项，不改变历史 `verified/completed/pass`。选择记录的顺序表达实际决定，不按最大revision推断现行版本。

基础 `validate_run.py` 不验证该扩展；只有基础结构通过不能证明选版或接纳当前有效。生成侧 `report_versions.py inspect` 检查扩展，`report_run.py inspect` 在扩展存在时展示其结果。依赖或选版决定变化后，旧接纳可能待复核；接纳当前也只表示记录仍匹配，不证明主张真实、依赖完整或审计独立。

独立审计不依赖生成包存在：读取实际产物、来源、选版历史及所引用的Check详情，核对上下文和实际字节；可用生成侧只读结果作为待核材料，但不能照抄其接纳标签作结论。没有该扩展的外来文档仍可正常审计，audit-only不执行选版/接纳写命令。

### 可选版本化决策上下文

长期修订需要区分实质目标变化和普通进度日志时，生成侧可通过 `report_versions.py set-context` 绑定已登记、已选中、有实际哈希的 Source 快照。快照保留本次已确认目标、受众、范围、口径、关键限定和决定；内容仍为自由文本。命令在 `run.json` 保存 `decision_context={version:"0.1",target:{id,revision},decision_id,reason}`，不产生检查或新的通过结论。

启用后的新接纳记录带 `context_mode:"decision_context_v1"`，将该 Source 的精确版本、依赖、字节和绑定决定纳入接纳指纹；普通 `notes_ref` 只作进度记录，其追加不再单独使此类接纳失效。目标、范围、口径或关键条件变化必须更新决策上下文快照并重新登记、选版、绑定，旧接纳据此失效；不能仅把实质变更藏在日志里。工具不从自然语言自动识别遗漏的语义变化。

没有 `context_mode` 的旧接纳继续按原 notes 指纹解释，不因绑定新上下文而自动变成新规则接纳。迁移不能修改旧记录或借用旧 Check 伪造复核；完成真实新复核并记录新 Check 后才能新接纳。基础 `--changed` 仍仅传播显式 `uses/input_refs`，上下文的全局接纳影响须看版本助手 `inspect`，空的基础影响集合不证明上下文变更无影响。

## 本地写入边界

随包写入助手先调用共享 [路径预检](../scripts/write_boundary.py)，仅检查目标及祖先和已知安装根：拒绝自身包、任何祖先带 `SKILL.md` 或 `bundle-manifest.json` 的其它已识别包、UNC/设备路径、备用数据流、父级跳转和链接/reparse 组件。在创建输出目录、锁、快照前拒绝；仍分别执行新输出不可覆盖与受控 Run 修改规则。不会全盘搜索安装包；无标记、未显式提供的外部安装目录不能可靠识别。此预检不创建文件，不是操作系统隔离，也不防任意外部进程在预检后替换目录。

## 许可事件

`events_ref` 指向JSONL。每条有唯一 `event_id`、严格递增正整数 `sequence`、非空 `type`。已支持的特殊记录：

- `consent_decision`：`decision` 为 `grant | deny | revoke`，`scope_id` 标明稳定资源范围，`user_message_ref` 指向真实用户决定；grant另有 `scope` 说明资源/用途/动作/流向/本Run边界。
- `resource_read`：`scope_id`、`resource_ref`、`consent_event_id`；必须对应当前仍有效的同scope grant。
- `check_recorded`、`dependency_changed` 和其他公开进度事件可按需扩展，不作为自动可信状态。

拒绝或撤销后停止该范围读取；同范围再获明确grant才可恢复。不可用改ID绕过拒绝。校验器只能检查已声明scope的顺序，不能判断用户消息真实性、识别资源别名或强制拦截工具。撤销不能让已读内容从模型记忆消失；停止后续主动依赖并复核相关内容。

## 独立画像

画像位于用户指定的私有位置，示意结构见 [模拟画像](../assets/examples/profile.json)。条目为 `id/revision/type/value/scope/confirmation_ref`，type仅为 `preference | experience`，正文保持自由文本。

实际启用时先取得可访问的明确位置；只将用户确认的持久偏好/经历写入，按要求展示和修正。当前指令优先；一次性取舍不自动升级为永久偏好。Run只引用本次所用条目及版本，不复制完整画像。当前校验器不读写画像，也不证明确认来源可信；这些由实际宿主操作与审查验证。

## 审计产物

审计建立自己的 Run，可仅登记外来报告与来源。原材料/原报告保持只读，独立报告对缺陷给出 issue ID、对象版本与定位、观察、影响、依据、级别和修复建议；证据缺口与可选建议分别说明，不混入缺陷数量。不要因缺少生成图而拒绝审查。

声明上下文继承、原资料可得性、是否先看过生成计划、数值复核方式。未解决P0→blocked；无P0但必要检查不能完成→not_assessable；已评估但结论可用性仍依赖明确的修复、限定或前置条件→conditional；无上述情形且本次必要检查完成、无未解决P0/P1→pass。可选建议、P2标签或范围外历史缺件不单独限制通过；轻微真实错误仍列明，按实际使用影响处理。范围变化须明示，不能排除必要检查来取得通过。此判定由审计方法执行，不由结构校验器自动给出。

正式审计交付需检查审计自身 Run 的结构并披露结果，检查被审生成 Run 不能替代这一步。没有执行能力时人工核对本契约，明确自动校验未运行。工作状态、审计结论与结构结果分别保留，不能用一个通过声明互相替代。

## 可运行的模拟资产

- [多图 Run](../assets/examples/multi-graph/run.json)：候选、证据、义务、任务、内容、页面与独立分支。所有材料为虚构契约样例。
- [外来文档审计 Run](../assets/examples/foreign-audit/run.json)：无生成图也能记录有限审计。

这些资产只解释协议，不是通用汇报答案、真实执行记录或用户事实。真实任务应从实际材料重新形成判断，不能套用示例结论。
