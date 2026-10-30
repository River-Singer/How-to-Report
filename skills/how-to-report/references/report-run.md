# 生成 Run 的建立与续接

用于需要持久追溯、续接或机器版本管理并选择Run的 `create`、`revise`、`analyze-first` 工作。仅保存一份Markdown方案不要求初始化Run。助手负责建立真实输入快照、只读检查登记状态；内容判断仍按 [生成与修订方法](reporting-method.md) 进行。短对话可直接交付必要内容，不必调用脚本或建立全套图。

## 建立新 Run

有 Python 3.10+ 时使用本包 [Run 助手](../scripts/report_run.py)。先选安装目录之外的新目录，其父目录须已存在；给实际路径加引号：

```text
python "<本Skill目录>/scripts/report_run.py" init "<新Run目录>" --run-id report-001 --mode create --source "<材料文件>"
python "<本Skill目录>/scripts/report_run.py" init "<另一新Run目录>" --run-id revision-001 --mode revise --target "<待修订报告>" --source "<补充材料>"
python "<本Skill目录>/scripts/report_run.py" init "<分析新Run目录>" --run-id analysis-001 --mode analyze-first
```

`--source` 可重复，每项必须是明确提供且实际存在的本地普通文件；也可暂不提供材料。`revise` 必须给 `--target`，其他两种模式不能给。目录、网址及重复解析到同一路径的输入会被拒绝；输入和 Run 均不接受 UNC/设备路径。不会扫描目录、联网获取资料或执行输入内容。需要用户材料时说明缺口，不用空文件充数。

成功后创建 `run.json`、`run.md` 和实际输入的 `inputs/` 快照。来源按参数顺序登记为 `source-001` 等，`role` 为 `supporting_material`；修订目标为 `revision-target`，`role` 为 `revision_target`。快照文件用对象 ID 命名，安全扩展名会保留，否则使用 `.bin`；原始名称和解析后的绝对路径保存在 `origin.filename/path`。`ref` 指向快照，SHA-256 来自实际复制的字节。

初始化的 `work_status` 是 `in_progress`，`artifacts`、`checks` 为空。各输入的 `revision=1` 仅表示本 Run 第一次登记，不是发现了原材料的业务版本，更不是确认其当前有效、已阅读或真实。修订目标仍是来源，实际修订完成后才登记新产物。不预写目标、检查通过、完整分析、许可事件或画像。

已有目录、文件或悬空链接不能作为新目标，自身及其它已识别 Skill 安装包均不能写入。目标及祖先按 [共享写入边界](workspace-contract.md) 在创建前预检，拒绝安装标记和链接/reparse；不全盘扫描。无效输入应在创建前处理；若发生中途 I/O 失败，保留不完整目录供核查，不把它称为初始化成功，也不覆盖重试。核对后另选新目录。

## 检查已有 Run

```text
python "<本Skill目录>/scripts/report_run.py" inspect "<已有Run目录>"
```

输出包含 `valid/errors/affected/scope`、目录及 Run ID、登记的 `mode/work_status`、当前 `run.json` 的 `run_record_sha256`，以及来源、产物、检查状态和 `record_refs` 摘要。它复用本包校验器并拒绝 `audit` 模式；审计 Run 应由实际可用的审计能力处理。已有可选 `version_state` 时，还展示 [版本选择与结果接纳](version-lifecycle.md) 的检查结果和派生状态；旧 Run 不强制添加此扩展。

退出 `0` 表示结构接受，`1` 表示记录无效，`2` 表示调用或实际 I/O 失败。`valid=true` 仍可能伴随未开始、失败或不可评估的内容检查。输出中的 `content_work=not_performed_by_this_command` 和 `origin_currentness=not_assessed` 明确界定本次动作：命令不读输入正文供模型分析，不回读原始位置判断更新，不自动续作或改变状态。

检查是只读的，不刷新哈希、不修复记录、不选择最大 `revision` 为当前业务版本。若快照字节不再匹配、引用失效或检查期间 `run.json` 改变，应按错误核查；不要改写历史哈希来伪装原快照未变。原位置后来改变而快照未变时，结构仍可能通过，这不证明原业务材料没有更新。

## 续接与新版本

1. 先检查既有 Run；有错误时定位受影响记录，保留真实状态，不覆盖初始化。
2. 读取当前请求所需的 `run.md`、已登记来源、实际产物与检查详情，确认目标、范围、用户新要求及未决项。已启用 `decision_context` 时，须读取绑定的精确 Source 快照；普通日志不能代替决策上下文。可按 [版本操作](version-lifecycle.md) 将实质范围与普通进度分开保存，实质变化仍需新版本和复核。指针存在不等于正文已读；没有必要不全量加载历史。
3. 对新增材料、替代版本或目标变化明确记录来源与采用理由。新来源快照使用新文件路径，按 [工作区契约](workspace-contract.md) 登记对象及精确版本，保留旧版和旧检查。需要安全追加及记录选版时，使用 [版本操作](version-lifecycle.md) 的 `register` 和 `select`；登记和选择是不同动作。没有执行能力时由宿主按契约实际保存，明确自动检查未运行，不把口头描述当成已保存。
4. 用显式依赖查询适用性发生变化的旧版本，再判断应重查的内容。例如 `source-001@1` 被新版替代时：

```text
python "<本Skill目录>/scripts/validate_run.py" "<已有Run目录>" --changed source-001@1
```

`affected` 只覆盖已声明的 `uses` 和 Task `input_refs`；不会标记状态或执行任务。依赖不全时应扩大必要复核并披露限制，不能由空结果断言全部无影响。目标变化可能改变内容取舍而不改变原始事实，须结合本次请求判断。

真正完成分析或修订后，再登记实际产物、所用精确版本与真实检查详情；新产物不继承旧版通过标签。当前摘要、工作状态和检查记录应反映实际结果，历史判断另行明确保留。涉及数字时按 [数值声明与复算](numeric-evidence.md) 保存必要定义和实际执行依据；交付与审计按 [最小证据交接](evidence-handoff.md) 选择附件，不默认把所有旧审计意见带入新审查。最后再次检查本 Run，结构与内容结论分别说明。

## 没有 Python 或文件能力

可在外置的新目录手动复制 [run.json 模板](../assets/report-run/run.json) 和 [run.md 模板](../assets/report-run/run.md)，替换 Run ID、模式与实际范围。只有实际复制了文件，才能登记快照；只登记真实计算的哈希，未计算则省略可选 `content_hash`。模板没有执行证明，不自动带来输入、许可或检查结果。修订时手工登记真实目标来源，完成后按工作区契约核对并说明自动校验未运行。

无写入能力时提供可复制记录和内容，明确未持久保存。画像、许可与可用工具按宿主实际能力和已有授权处理，助手不会隐式读取 Knowledge、画像或事件并生成授权。此能力只覆盖本地文件 Run 的建立与检查，不等于已验证宿主自动发现、原生安装、跨会话自动恢复或云端生命周期。
