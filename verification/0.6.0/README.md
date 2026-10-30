# 0.6.0 内容思考与 Markdown 工程复核

日期：2026-10-30。当前版本停止生成 HTML/SVG/PPTX，默认交付可使用的 Markdown 内容。此次检查没有运行浏览器或模型，不能据此宣称成稿质量、用户理解或相对普通提示词的收益已经通过。

## 实际执行

| 检查 | 结果与边界 |
|---|---|
| 全量单元测试 | 220项运行，219通过、1跳过，unittest计时83.730秒；见[完整日志](engineering-suite.log)及[执行记录](engineering-suite.json) |
| 跳过项 | Windows真实符号链接创建缺少权限（WinError1314）；相关模拟分支仍执行 |
| 双包构建与一致性 | how-to-report、report-audit均为0.6.0；独立包包含121/108个payload文件，另各有manifest |
| 默认安装范围 | 无HTML/CSS/JS/SVG/图片载荷，无renderer、diagram layout、page audit、visual editing；保留按需数值、日期、来源、版本、画像与记录工具 |
| 离线来源与Skill格式 | 来源清单及两个Skill格式检查通过，检查未联网；本地引用闭包由package check核验 |
| 评测输入 | 当前4项分阶段内容设计和历史67项均通过输入完整性检查；未运行模型，也未判内容质量 |
| Python语法/编译 | 当前源码、工具、评测工具及测试共28个文件通过Python3.10语法解析与内存编译；实际解释器Python3.14.4 |
| 历史保真 | 27个视觉归档文件与原提交逐字节相同；原提交的67个evaluation文件、560个verification文件全部未变 |

各命令原始输出见[checks.json](checks.json)，归档、包身份、Python及历史字节检查见[static-receipt.json](static-receipt.json)。项目没有配置通用linter或静态类型检查器；不把语法/编译检查说成lint或type-check通过。

## 独立人工复核及修复

复核了两个入口、可选Run触发、目标与叙事方法、实际发言身份、自然语言组织、独立审计、日期校验及独立包迁移路径。新语义组织方法区分顺序、依赖、因果和影响，要求按需还原重要事实与关系；来源明确声称不等于独立证实，缺少因果支持不自动获得相关关系。局部组织不强迫全局叙事，也不引入固定步骤、维度数量或必填图。

发现并修复三份历史发布说明中的10个视觉资源断链：`docs/html-runtime-release.md`、`docs/requirements-freeze.md`、`docs/visual-refinement-release.md`。链接指向0.5.3同字节归档，并注明历史身份；没有改写原执行结论或旧验证记录。Markdown文件链接和项目CRLF口径的whitespace检查见[最终收口记录](release-receipt.json)。

四项当前内容案例涵盖目标歧义、局部修改、新证据改变价值判断、说话身份及真实关系保留。它们包含分阶段输入，检查器验证文件和引用完整性；是否能改善模型行为仍由用户运行后审查。新增方法及合成示例可离线阅读；没有将用户研究输入中的所有外部引用说成本轮已逐篇核验。

## 复现与身份

从项目根目录可运行：

```text
python -X utf8 -B tools/package_skills.py build
python -X utf8 -B tools/package_skills.py check
python -X utf8 -B tools/vendor_knowledge_sources.py check
python -X utf8 -B evaluation/tools/validate_content_cases.py
python -X utf8 -B evaluation/tools/validate_cases.py
python -X utf8 -B -m unittest discover -s tests -v
git -c core.whitespace=cr-at-eol diff --check
```

构建生成两份安装包。manifest SHA256如下；该身份用于后续冻结测试包，不将历史案例结果移植为当前通过。

| 包 | bundle-manifest.json SHA256 |
|---|---|
| how-to-report | `413fbd7ee9715006c5d384b7453305a633a1f621894c4e3d490ad5708ffbde05` |
| report-audit | `6c5dc6fcdf0dabd94f214b46ce4ea36c78ab11b54a12248bffb7f51325951058` |

归档对照提交为`071592ad59ea2bbe62ef9ea9e728d3dea4e38181`。历史浏览器工具只能按归档说明在原版本环境复现；当前内容交付不以旧页面测量作为门槛。公开证据只含合成工程输入及执行记录，未复制私有汇报资料。
