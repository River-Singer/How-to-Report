# GPT审计入口

更新（2026-10-30）：当前整改候选为0.5.2，范围见[观众成稿与视觉整改](visual-refinement-release.md)，新执行的检查及包身份见[0.5.2复核](../verification/0.5.2/README.md)。[0.5.1工程验证](../verification/0.5.1/README.md)仅说明已核对字节相同的运行代码/资源的历史覆盖，不代表新增成稿方法已经过模型验证；0.5.0完整A/B交付及[历史验证](../verification/0.5.0/README.md)也保留对应版本范围。

这次重点审查具体事实与分工是否被抽象措辞写空、自然表达是否保真，以及纯文字到页面的含义、源引用详情、关键限定、并行/反馈布局和实际图形尺寸；工具通过不代表正式V1准出或模型质量提升。克隆仓库即可读要求、方法、实现和合成评测，不依赖父目录私有资料。

建议依次核对：

1. [冻结需求](requirements-freeze.md)：逐项FR/NFR、最新认知及页面行为要求、范围边界。以该清单核对实际实现，不能用版本号或测试数量替代需求满足。
2. [架构](architecture.md)与两个独立入口：[生成](../skills/how-to-report/SKILL.md)、[审计](../skills/report-audit/SKILL.md)。检查Graph各自职责、核心/Knowledge许可、目标确认与证据验证、创建/修改/审计边界是否一致。
3. [叙事与页面行为](narrative-page-behavior.md)及生成侧核心方法：检查触发是否进入真实操作、失败是否回到相应层，是否只剩填表；检查候选结果、解释方向和成品反读是否尊重未知与用户取舍。
4. 当前工具：`report_run.py`、`report_versions.py`、`report_html.py`、`report_calculate.py`、`report_profile.py`、`report_experience.py`、`report_schedule.py`及独立`audit_run.py`。实现维护在`skill-src/`，发布包在`skills/`。重点审输入/路径/类型/哈希、不可覆盖、版本/接纳语义、递归布局与图表缺失、计算口径及画像声明边界。
5. [评测目录](../evaluation/README.md)与[oracle说明](../evaluation/ORACLES.md)：25个原案例、7份原fixture及必要补件，14项既有分阶段变形和12项V05新增两阶段输入，加16项V051观众成稿/视觉输入，共67项设计。检查缺件、指标口径、阶段泄露和把已读Dev伪装Holdout的风险；不要把设计判据当模型输出。
6. [本轮版本边界](visual-refinement-release.md)及[0.5.2验证记录](../verification/0.5.2/README.md)：核对当前源码/包指纹、新38项局部测试及64项运行文件字节一致性。0.5.1的279项全量测试与12页浏览器回归是历史执行，不改标为0.5.2新跑；本轮未运行模型。合成工程HTML和截图只演示机制，不代表MASTer或真实模型内容质量。

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
