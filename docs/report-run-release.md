# 0.3.0：生成 Run 的创建、输入快照与续接检查

更新：2026-10-28。包版本0.3.0，Run契约0.1，知识卡、目录与来源归档0.1.1。本版补充生成侧 Run 工具，推进持续使用与版本登记；0.2.4的认知和审计方法继续保留。

本文保留0.3.0的实现范围。后续0.3.1增加显式版本选择与已有检查绑定的接纳，见[新版本说明](version-lifecycle-release.md)；下列链接指向仓库当前包，不替代历史冻结字节。

## 本版交付什么

[how-to-report](../skills/how-to-report/SKILL.md)新增[Run 操作说明](../skills/how-to-report/references/report-run.md)、初始化模板及[本地工具](../skills/how-to-report/scripts/report_run.py)。工具只需 Python 3.10+ 标准库，资源随同一个包分发。

| 操作 | 实际行为 | 结果边界 |
|---|---|---|
| `init --mode create` | 在新目录创建 `run.json`、`run.md`，按需复制显式输入 | 初始状态为 `in_progress`，产物和检查为空；没有生成报告 |
| `init --mode analyze-first` | 建立分析优先的同类记录 | 不预填结论、图节点、计算或已完成任务 |
| `init --mode revise --target FILE` | 把待修订原件登记为修订目标，并保存其快照 | 目标初始登记版本为1，不代表它在业务上的第一个或最新版本 |
| `inspect RUN` | 只读核对记录、快照哈希及显式引用，返回模式、状态、登记对象和记录位置 | 为 Agent 续接提供可核对的上下文；不执行续接、不选择现行业务版本、不自动接纳结果 |

命令示例中的占位路径需要替换为真实本地路径。父目录须已存在，目标 Run 目录须不存在。

```powershell
python "<installed-how-to-report>/scripts/report_run.py" init "<new-run-directory>" --run-id "report-001" --mode create --source "<local-material-file>"
python "<installed-how-to-report>/scripts/report_run.py" init "<new-analysis-directory>" --run-id "analysis-001" --mode analyze-first
python "<installed-how-to-report>/scripts/report_run.py" init "<new-revision-directory>" --run-id "revision-001" --mode revise --target "<local-report-file>" --source "<local-material-file>"
python "<installed-how-to-report>/scripts/report_run.py" inspect "<run-directory>"
```

`--source` 可重复，仅接受显式指定的普通本地文件；同一实际文件重复登记会被拒绝。`revise` 必须有 `--target`，另两种模式不接受该参数。不扫描文件夹、不下载链接，也不扩大画像或可选 Knowledge 的读取许可。输入内容只按字节复制，不作为代码执行。

快照位于 Run 的 `inputs/`，记录保存实际字节的 SHA-256 和原文件路径/名称。原件随后变更或移走，不会改写已保存的输入；检查基于快照，原路径只用于溯源。哈希一致说明字节与登记相符，不能证明来源真实、业务版本最新、内容已精读或结论成立。修改快照后不能靠刷新哈希掩盖已使用版本的变化。

初始化拒绝已有目标及包内工作区；无效输入在写入前拒绝。写入时若发生 I/O 错误，保留已经创建的目录供检查，不清空或覆盖重试。`inspect` 对审计模式不适用，审计仍使用原有 `audit_run.py check`。退出码0表示结构检查接受，1表示记录无效，2表示调用或 I/O 错误；它们不是内容工作完成状态。

## 怎样续接

先读 `inspect` 返回的登记状态和记录位置，再按当前任务读取必要材料；`run.json` 是机器状态的权威记录，`run.md` 解释目标、判断与缺口。用户的新目标、来源版本和结果接纳需要明确登记，随后复核实际受影响的对象；本工具没有自动推进这一流程。

无 Python 执行能力时可依随包模板用宿主文件工具建立记录，保留真实输入、范围和状态，并注明自动检查未运行。简短任务不因此强制创建全套图、任务或页面文件。

## 验证范围与剩余工作

本版的确定性验收包括：初始化边界、三种模式、快照与原件变化、只读检查、独立包搬迁及 `python -I` 调用。实际执行结果以任务工作区 `validation/report-run-*` 的记录为准；开发记录不作为安装包的运行依赖。

本轮不启动模型案例，不修改冻结 master-v1/v2/v3 或用户输出。0.2.1认知/修订试用、0.2.2审计流程和0.2.3定向审计分别保留原版本归属；0.2.4和0.3.0尚无新的模型行为结果。测试通过也不能证明方法效果提高。

在0.3.0交付时，现行版本决定和变更后结果接纳尚未实现，0.3.1补充其有界工具路径。原生宿主安装/自动发现、跨宿主兼容、完整执行与恢复闭环、正式 B0/B1/B2 对照仍未完成；后续0.4.0的有界HTML实现见[说明](html-runtime-release.md)。完整范围与推进顺序见[开发计划](development-plan.md)和[V1进度](v1-progress.md)。
