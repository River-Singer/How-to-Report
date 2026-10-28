# How-to-Report

面向报告创建、修订和独立审计的 Skill。当前候选为 **0.5.0**：在原有多Graph方法、离线计算、画像、Run与版本能力上，补齐写入/检查冲突修复、四类按需思考动作、单标题与胶囊导航、主线/Backup、本地媒体与关系表达、项目进度五类视图以及显式经验记录。两个独立入口是 `how-to-report` 与 `report-audit`；基础Run0.1保持，PagePlan0.2兼容0.1。

本版承接完整A/B开发计划，范围、限制与验证见[0.5.0说明](docs/complete-plan-release.md)。模型生成、独立审计与修订仍由用户运行；工程通过不等于语义质量已改善，也不代表正式V1准出。旧冻结包、用户结果和0.4.0验证记录保留原样。进度按[范围状态](docs/v1-progress.md)报告，不以新增文件或测试数换成完成百分比。

## 当前能力与历史试用

先从[GPT审计入口](docs/audit-start-here.md)查看冻结需求、实现和真实验证范围；评测设计与输入已放在[仓库内](evaluation/README.md)，尚未执行模型。

- [0.5.0完整计划候选](docs/complete-plan-release.md)：五类进度视图、单标题导航/Backup、受控媒体与关系、四法和经验分层。
- [0.4.0历史候选](docs/html-runtime-release.md)：递归主辅组合、文本/层级/指标与条形/折线/矩阵、离线运行、页面映射及审计交接。
- [实际结果与示例](docs/first-version-results.md)：四组模拟案例、目标变化后的修订及独立审计。
- [试用方法](docs/first-version-guide.md)：用自己的材料调用两个入口。
- [0.3.1 版本选择与结果接纳](docs/version-lifecycle-release.md)：材料换版后的待复核状态、真实新稿与检查绑定；工具不执行语义复核。
- [0.3.0 Run 创建与续接](docs/report-run-release.md)：显式输入快照、修订目标和只读检查；[完整 V1 进度](docs/v1-progress.md)区分已落地能力与剩余准出条件。
- [0.2.4 方法与验证范围](docs/audit-evidence-release.md)：发现分类、计算证据身份和来源定位；[0.2.3记录](docs/audit-precision-release.md)保留上一版范围与试用结果。
- [审计 Run 操作](skills/report-audit/references/audit-run.md)：创建记录、校验审计自己的目录及无 Python 时的模板路径。
- [离线资料](docs/offline-knowledge.md)：本地来源正文与明确标记的原创摘要，版本/数量按来源清单核对，原网址仅溯源。

## 开发与生成

需要 Python 3.10+，工具只使用标准库。在本仓库目录执行：

```powershell
python tools/package_skills.py build
python tools/package_skills.py check
python tools/vendor_knowledge_sources.py check
python -m unittest discover -s tests -v
```

也可以从任意工作目录用脚本的绝对路径执行 `build` 或 `check`。工具始终以脚本所在仓库定位输入与输出。

| 目录 | 用途 |
| --- | --- |
| `skill-src/how-to-report/`、`skill-src/report-audit/` | 人工维护的入口与各自方法 |
| `skill-src/shared/` | 两包共有认知方法、契约、知识卡/本地来源、结构校验器和合成示例的唯一维护源 |
| `skills/how-to-report/`、`skills/report-audit/` | 已物化共有文件的独立安装目录；生成结果纳入版本管理 |
| `docs/` | 产品研究、架构与开发计划，不是运行依赖 |
| `tests/` | 打包行为、Run契约、生成/审计记录工具与离线来源完整性的隔离测试 |
| `examples/first-version/` | 明确标记的模拟请求、材料和实际主要产物，不随运行包加载 |

编辑 `skill-src/` 后重新 `build`；不要手动修改 `skills/`。共享资源复制到两个生成包，路径碰撞会失败；源码目录中的 `__pycache__/`、`.pyc`、`.pyo` 解释器缓存不参与分发。`check` 从源码重新计算预期内容并只读比较，能够发现手改、缺失、遗留文件及 manifest 漂移。每包 `bundle-manifest.json` 包含包版本、支持的契约版本与所有 payload 文件的 SHA-256（不包含自身）。

构建先验证全部输入，再在 `skills/` 内暂存并替换两个受管包。没有本工具生成标记的同名目录不会被覆盖。源校验失败保留已有包；普通替换错误会尝试回滚，若回滚失败则保留临时备份。Windows在尚未替换任何包时拒绝首次备份目录重命名（WinError5/32），可走受限后备路径：完整备份旧内容后保留外层目录逐项更新，失败恢复原内容，恢复失败保留备份。它不跳过受管目录、路径或链接检查。构建不提供并发写入锁、读者原子快照或进程崩溃后的自动恢复，不应与其他构建或手工编辑生成目录同时运行。

包检查拒绝符号链接、Windows junction/reparse point、大小写碰撞、包外本地资源链接和缺失的核心 Reference。静态资源扫描覆盖 Markdown 正文中的行内链接及引用定义，忽略代码块、锚点和普通外部网页链接；包内链接使用精确大小写和 `/`，相对当前 Markdown 文件。脚本动态读取和宿主能力仍需要独立运行验证，静态检查不能证明它们全部可用。

## 独立使用

任一生成目录都可作为独立安装单元，整体复制到宿主支持的 Skill 目录；`skill-src/` 叶目录不完整，不能直接安装。包不依赖另一个包的相对位置。此仓库的构建命令不安装到全局目录，也不修改宿主设置。当前验证覆盖格式、独立搬迁与按路径调用；宿主原生安装、自动发现及跨宿主兼容性尚未验证。

有 Python 执行能力时，可从任意当前目录运行已安装包的只读结构校验器：

```powershell
python <installed-skill>/scripts/validate_run.py <run-directory>
python <installed-skill>/scripts/validate_run.py <run-directory> --changed <id>@<revision>
```

命令中的尖括号表示需要替换的实际路径/标识。`--changed` 可重复。校验成功只说明结构与声明引用一致，不意味着主张已被证明、计算已执行或审计已独立完成。共享示例均为合成资料，不是用户事实。

生成任务可用 `how-to-report` 包内工具建立新记录，并在后续会话只读检查已有记录：

```powershell
python "<installed-how-to-report>/scripts/report_run.py" init "<new-run-directory>" --run-id "<run-id>" --mode create --source "<local-material-file>"
python "<installed-how-to-report>/scripts/report_run.py" init "<new-revision-directory>" --run-id "<revision-run-id>" --mode revise --target "<local-report-file>" --source "<local-material-file>"
python "<installed-how-to-report>/scripts/report_run.py" inspect "<run-directory>"
```

`--mode` 也支持 `analyze-first`，`--source` 可重复；`revise` 必须提供 `--target`，其他模式不接受目标参数。`init` 只复制显式指定的本地文件，保存快照与哈希，不覆盖既有目录；新 Run 为 `in_progress`，产物和检查为空。`inspect` 核对本地快照并返回已登记状态，不读取原路径来判断最新业务版本，不自动执行续接任务。无 Python 时按[随包说明](skills/how-to-report/references/report-run.md)使用模板，披露自动检查未运行。

继续已有工作时，可按[版本操作](skills/how-to-report/references/version-lifecycle.md)使用 `report_versions.py register/select/accept/inspect`。登记材料、选择采用版本和记录接纳是三个不同动作。写入需要最新记录哈希；实际复核先完成，再保存真实 Check，最后接纳。基础校验不检查可选 `version_state`；接纳仍匹配也不等于语义正确。

审计任务可用 `report-audit` 包内工具建立新记录，完成内容审查后校验自己的目录：

```powershell
python "<installed-report-audit>/scripts/audit_run.py" init "<new-audit-directory>" --target "<local-report-file>" --run-id "<audit-run-id>"
python "<installed-report-audit>/scripts/audit_run.py" check "<audit-directory>"
```

`init` 不覆盖既有目录，初始内容检查保持 `not_run`；目标登记版本可用 `--target-revision` 明确指定。`check` 只读输出审计目录、Run ID、记录哈希和结构结果，不自动完成内容检查；验证被审生成目录不能替代审计自身自检。无 Python 执行能力时按[随包说明](skills/report-audit/references/audit-run.md)使用模板并人工核对，披露自动自检未运行。

Run、原始资料、输出和个人画像保存在安装目录之外；画像也不混入 Run。仓库忽略本地 `.runs/`、`.profiles/` 和 Python 缓存，避免把工作数据当 Skill 资源提交。V1 画像只保存用户确认的偏好与经历，支持查看和修正；跨任务自动更新后置。

当前已实现专门认知方法和可离线读取的来源，完成有界模拟试用；包含有界页面与CSV计算适配；尚无通用任务调度、全部业务引擎或相对基线质量提升的实验证据。知识卡、来源正文和项目事实保持区分；按明确许可读取相关领域与来源段落，缺少项目证据时如实保留缺口。
