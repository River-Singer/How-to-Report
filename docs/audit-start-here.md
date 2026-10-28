# GPT审计入口

更新（2026-10-28）：当前候选为0.5.0，完整A/B增量与边界见[本版交付](complete-plan-release.md)，最终实际检查见[0.5.0验证](../verification/0.5.0/README.md)。下列0.4.0及更早数字/结果保持为对应版本历史证据，不转为新版通过。

这是0.5.0完整计划审核候选，不是正式V1准出或模型质量提升声明。克隆此仓库即可读取要求、方法、实现与合成评测，不需要父目录的私有记录、历史用户输出或联网搜索。

建议依次核对：

1. [冻结需求](requirements-freeze.md)：逐项FR/NFR、最新认知及页面行为要求、范围边界。以该清单核对实际实现，不能用版本号或测试数量替代需求满足。
2. [架构](architecture.md)与两个独立入口：[生成](../skills/how-to-report/SKILL.md)、[审计](../skills/report-audit/SKILL.md)。检查Graph各自职责、核心/Knowledge许可、目标确认与证据验证、创建/修改/审计边界是否一致。
3. [叙事与页面行为](narrative-page-behavior.md)及生成侧核心方法：检查触发是否进入真实操作、失败是否回到相应层，是否只剩填表；检查候选结果、解释方向和成品反读是否尊重未知与用户取舍。
4. 当前工具：`report_run.py`、`report_versions.py`、`report_html.py`、`report_calculate.py`、`report_profile.py`、`report_experience.py`、`report_schedule.py`及独立`audit_run.py`。实现维护在`skill-src/`，发布包在`skills/`。重点审输入/路径/类型/哈希、不可覆盖、版本/接纳语义、递归布局与图表缺失、计算口径及画像声明边界。
5. [评测目录](../evaluation/README.md)与[oracle说明](../evaluation/ORACLES.md)：25个原案例、7份原fixture及必要补件，14项既有分阶段变形和12项V05新增两阶段输入，共51项设计。检查缺件、指标口径、阶段泄露和把已读Dev伪装Holdout的风险；不要把设计判据当模型输出。
6. [实际验证记录](../verification/0.5.0/README.md)与[版本边界](complete-plan-release.md)：看最终源码/包指纹、真实命令与浏览器范围、跳过项及未做的模型检查。合成工程HTML和截图只演示机制，不代表MASTer或真实模型内容质量。

可先做本地只读工程检查（仓库根目录）：

```text
python -B tools/package_skills.py check
python -B tools/vendor_knowledge_sources.py check
python -B evaluation/tools/validate_cases.py
python -B evaluation/tools/numeric_oracle.py
python -B -m unittest discover -s tests -v
```

实际浏览器探针另需已有Python Playwright和Chromium，可用`tools/check_report_html_browser.py --help`查看CLI，输出必须是安装包之外的新目录。无浏览器时不能把源码检查算作视觉通过。这里不要求或授权自动运行大批量模型案例、联网/上传、安装插件、读私有画像或修改历史用户结果。

请按问题给出**文件/位置、实际观察、所违反的具体要求、可复核依据、影响/严重度与建议修复层**；区分确定缺陷、必要证据缺口和可选建议。也请指出“声明超过证据”的地方，以及遗漏但已确认的范围。不要按建议数量、个人审美或单一标准截图判分；没有证据时标未评估，不编造运行过程或通过结论。

这轮可先完成代码与文档审计。模型行为、独立语义反读质量、跨宿主实际使用和正式B0/B1/B2由后续用户安排并提交真实结果。
