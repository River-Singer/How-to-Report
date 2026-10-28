# 版本选择与结果接纳

当同一 Run 持续修订、需要说明本次采用哪份材料及哪些结果仍适用时，使用本包 [版本助手](../scripts/report_versions.py)。它保存公开决定和实际文件指纹；内容分析、计算、复核及 Check 的真实执行仍由宿主完成。简单汇报不必增加图或此扩展。

## 四个动作分开

| 操作 | 保存或检查什么 | 不代表什么 |
|---|---|---|
| `register` | 新 Source/Artifact 的真实本地快照、明确 ID/版本、依赖及理由 | 不选择现行版本，不完成复核 |
| `select` | 对一个已登记精确版本的明确选择及决定历史 | 不证明来源真实，不改旧图或旧检查 |
| `accept` | 对已选中产物，保存已有实际检查与相关材料的接纳声明和指纹 | 不执行检查，不制造 pass，不保证语义或独立性 |
| `inspect` | 基础结构、可选扩展、选版适用性与接纳是否仍匹配 | 不续作、不重算、不自动发布 |

使用 Python3.10+，从任意当前目录调用实际安装包；支持 `python -I`。Run 须位于包外。所有写操作都要传入刚检查得到的 `run_record_sha256`；每次成功写入返回新值，下一步使用新值。不要把下列占位值当真实哈希：

```text
python "<本Skill目录>/scripts/report_versions.py" inspect "<Run目录>"
python "<本Skill目录>/scripts/report_versions.py" register "<Run目录>" --kind source --id source-001 --revision 2 --file "<真实新版材料>" --reason "说明本次登记的范围与原版本关系" --expect-run-sha256 <刚检查的哈希>
python "<本Skill目录>/scripts/report_versions.py" select "<Run目录>" --target source-001@2 --reason "说明本次采用新版的实际依据" --expect-run-sha256 <上一步返回的哈希>
```

`register` 的 `--kind` 是 `source|artifact`，`--revision` 为正整数。每次用新的精确版本，不覆盖已有版本；相同 ID 不能从 Source 变为 Artifact。`--uses ID@版本` 可重复，必须引用实际已登记对象。Artifact 必须明确给出 `--uses` 或 `--no-dependencies`；后者只是“没有声明依赖”，需要理由，并不证明没有遗漏。材料只复制字节，不执行其内容，不扫描目录或获取网络资源。

## 从旧材料到新结果

假设已登记并明确选择 `source-001@1` 与依赖它的 `report@1`，且已有接纳记录：

1. 按上例登记 `source-001@2`。仅登记不会取消原选择；明确 `select source-001@2` 后，旧报告的声明依赖不再匹配，旧接纳显示待复核。保留原材料、旧报告和原 Check。
2. 读取新材料，实际判断旧结论是否受影响。必要时用基础校验器 `--changed source-001@1` 查询显式影响；空结果不能证明没有漏记依赖。目标变化可能只改变内容选择，不使原始事实变假。
3. 完成真实修订后登记新文件及实际依赖，再选择产物；不要仅修改旧版本的 `uses` 来假装它已重做：

```text
python "<本Skill目录>/scripts/report_versions.py" register "<Run目录>" --kind artifact --id report --revision 2 --file "<实际修订后的报告文件>" --uses source-001@2 --reason "说明实际修改和依赖覆盖范围" --expect-run-sha256 <当前哈希>
python "<本Skill目录>/scripts/report_versions.py" select "<Run目录>" --target report@2 --reason "本次拟交付修订稿，尚待接纳" --expect-run-sha256 <新哈希>
```

4. **先执行所需复核，再用宿主文件工具保存真实详情和 Check。** 按 [工作区契约](workspace-contract.md) 在 `run.json.checks` 登记新的唯一 ID、精确 `target={id:report, revision:2}`、实际 `status`、`method`、`scope` 及非空的本 Run `detail_ref`。检查没有通过时如实保存失败/不可评估，不运行接纳来制造通过。保存后重新 `inspect` 取得当前哈希。
5. 满足本次证据需求后记录接纳；所给 Check ID 必须实际存在并指向此精确产物：

```text
python "<本Skill目录>/scripts/report_versions.py" accept "<Run目录>" --target report@2 --acceptance-id accepted-report-2 --check <真实新Check-ID> --reason "说明实际核对、依赖覆盖与仍适用限制" --expect-run-sha256 <重新检查的哈希>
python "<本Skill目录>/scripts/report_versions.py" inspect "<Run目录>"
```

`--check` 可重复。接纳与 `work_status=completed`、独立审计结论分别记录；此命令不自动把工作或事实标为完成/verified。当前目标存在任何 `fail/not_run/not_assessable` Check 时，本版的保守策略拒绝接纳。不能删除旧失败记录来绕过：解决后的新稿采用新 revision 和真实新 Check，历史保留。

## 读取结果，保留边界

- `structure_valid` 是基础 Run 校验，`lifecycle_valid` 是可选扩展一致性；`valid` 综合二者。基础 `validate_run.py` 不检查此扩展。`report_run.py inspect` 在存在扩展时也展示生命周期结果。
- `selections` 展示每个 ID 的最新明确决定，而非最大 revision。Artifact 的 `currentness.state` 为 `current|pending`，`reasons` 说明未选择、选择不匹配或待复核状态；其 `acceptance_status` 为 `current|stale|absent`。待复核产物可以存在于结构合法的 Run 中。
- 传递范围只沿 `uses` 和 Task `input_refs`，不沿语义 `links`、Task 前置或结果归属。实际用到的节点/任务也需明确选版；`stale/invalidated` 证据、未完成或失败的任务输入不能用于此工具的接纳。其他证据标签仍须结合正文判断，程序不判断陈述真假。
- 接纳绑定实际本地材料、对象声明、相关选版决定、Check 及详情，包括依赖节点明确引用的校核依据，并绑定公开范围说明 `notes_ref`。相关内容或说明变化会使旧接纳失配；无关独立分支的选版不使它失配。选版切走再切回来也不会复活旧接纳。
- 同一个 Check ID 已用于接纳后，相关上下文或证据变化时不能再次借其旧 pass 接纳；须真实重查并使用新 Check。首次接纳不能证明检查发生时间；指纹采集不是历史执行凭证。
- 仅远程定位、空/不可读证据不能取得本地接纳。遗漏依赖、错误方法和失实检查声明仍是人工/独立审计责任。合法的旧新版对照可能同时使用同 ID 多个版本；本版自动接纳要求依赖都匹配单一现行选择，因此不支持这种混合历史闭包。这是工具限制，不是稿件缺陷，仍可用普通 Run 保存并人工审查。

## 写入失败与手工路径

写入前核对预期记录哈希，以合作锁避免本工具同时改同一 Run，独占保存实际快照和旧 `run.json`，最后原子替换记录。哈希冲突时先重新检查，不强行覆盖。失败可能留下未登记快照/历史文件；先依据错误确认是否提交，再核对现行记录和保留文件，不清空目录重试。若进程中断遗留锁，先确认没有写入者并保留证据，由宿主明确处理；不要自动强删锁或历史。

该保护不是针对任意外部编辑者的完整事务。本次已观察的本地文件在提交前会复核其字节，但不能锁住整个文件系统。禁止包内写入和写路径的链接/重解析逃逸，不覆盖旧快照。

没有 Python 时可按基础契约用宿主文件工具保存真实版本、公开选择和复核说明，保留历史并披露自动扩展检查未运行。不要手填虚构指纹或把手写 `version_state` 当已通过工具。独立审计只读原件，核对实际产物、材料和检查详情，不依赖生成包存在，也不执行 `register/select/accept` 修改被审 Run。
