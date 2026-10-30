# How-to-Report

**0.6.0：把这次汇报想清楚，交付可直接使用的 Markdown 内容。**

帮助用户确认希望取得的沟通结果，发现值得讲的重要区别，整理事实与论证，选择适合听众和场合的叙事，再以实际汇报者的立场成稿。目标已经明确、只要一句短更新或局部修改时直接处理，不要求走完一套图、表单或分析流程。

两个入口独立安装和使用：

- [how-to-report](skills/how-to-report/SKILL.md)：创建、修订或先讨论思路；默认交付《汇报方案.md》。方案说明写给汇报者，正式正文写给听众。
- [report-audit](skills/report-audit/SKILL.md)：独立审查目标、事实、推理、重要遗漏与表达。接受外来稿件，不要求先使用生成 Skill；仅审计时不改原件。

HTML、SVG、PPTX、页面组件与浏览器验收已退出当前产品范围。需要幻灯片时可建议页数与逐页内容；口头更新或书面简报按任务组织。下游自由决定视觉形式，数字、状态、重要条件和归因须保真。旧视觉工具见[历史归档](legacy/visual-0.5.3/README.md)，旧结果不作为新版内容能力的通过证据。

## 开始使用

整体复制 `skills/how-to-report` 或 `skills/report-audit` 到宿主支持的 Skill 目录，也可指向其 `SKILL.md` 使用。两包不依赖彼此位置；不要安装尚未合并共享资源的 `skill-src` 叶目录。原生自动发现与跨宿主兼容性以实际验证范围为准。

告诉 Skill 已知的场景、对象、材料与需求即可，不必先填模板：

> 我明天要向领导说明项目延期。材料在这里。我还不确定这次该重点讲什么，请先帮我判断主线；需要澄清时，只问会影响方向的问题。

目标明确时直接给出，局部修改时注明范围。详细用法见[使用说明](docs/usage.md)。核心方法和选用的知识资料均可离线读取；来源链接用于溯源。领域知识按已有授权使用，不能代替项目事实。

## 当前范围和验证

- [范围与交付](docs/content-scope.md)
- [架构与方法](docs/architecture.md)
- [开发与验证计划](docs/development-plan.md)
- [独立审查入口](docs/audit-start-here.md)
- [当前状态](docs/v1-progress.md)
- [四项内容评测设计](evaluation/content-0.6.0/README.md)
- [离线资料说明](docs/offline-knowledge.md)

模型生成、独立审计与批量修订由用户运行。工程检查只证明相应的文件、数值和结构规则；方法写入 Skill 不等于模型已经稳定掌握它，也不证明比普通任务提示更有效。

## 维护与工程检查

Python 3.10+，运行工具只用标准库。普通 Markdown 任务不要求 Python、浏览器、Run 初始化或额外 JSON；工具按实际计算、版本或记录需求使用。

```text
python tools/package_skills.py build
python tools/package_skills.py check
python tools/vendor_knowledge_sources.py check
python evaluation/tools/validate_content_cases.py
python -m unittest discover -s tests -v
```

| 目录 | 用途 |
|---|---|
| `skill-src/how-to-report/`、`skill-src/report-audit/` | 两个入口及专属方法、助手脚本 |
| `skill-src/shared/` | 方法、离线资料与契约的唯一共享源 |
| `skills/` | 构建生成的两个完整独立安装包，勿手改 |
| `evaluation/content-0.6.0/` | 当前四项合成内容设计，尚未执行模型 |
| `evaluation/` 中旧 catalog 与 fixtures | 保留原67项输入身份，作为历史开发资料 |
| `legacy/visual-0.5.3/` | 退出默认包的视觉工具历史归档 |
| `verification/` | 各版本实际执行的工程证据，不互相替换 |

构建只替换 `skills/` 下两个受管目录，先校验输入，失败保留可恢复旧内容；拒绝链接、包外依赖和冲突路径。`check` 只读比较预期字节与清单。写入工具保护安装包与原件，但不构成通用系统沙箱。Run、输出、画像与真实用户资料保存在安装目录之外；只保存显式确认的偏好与经历，不后台采集。
