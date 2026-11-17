# 0.11.4 工程检查

2026-11-17。本次发布包含自0.11.0之后尚未发布的计算排版、组件/图表/原生资产工具，以及本轮的叙事、设计前评估、栅格、长文本和数据表示方法。下面是工程验证，不是模型生成质量或整套业务报告的独立审计。

| 检查 | 实际结果 |
|---|---|
| 正常打包与只读闭包检查 | 两个0.11.4包通过，Run contract保持0.1 |
| 两个Skill的quick_validate | 均通过 |
| 全套常规unittest | 637项，636通过、1跳过，489.383秒；跳过是Windows缺创建符号链接权限（WinError1314） |
| 最后文档修订后的定向回归 | 4项包装/搬迁测试通过：manifest与共享字节、无checkout/兄弟包运行、真实audit初始化检查、真实report初始化检查 |
| Python语法检查 | 229个源码、tools和tests的Python文件通过AST解析 |
| 静态类型检查 | 本项目没有配置独立type-check命令；不声称该项通过 |
| 开发工具浏览器可移植性 | `verify_template_assets.py`去除个人安装路径；help、缺路径/目录拒绝、默认Chromium与显式浏览器路径的只读SVG bbox smoke均通过，未运行资产修改流程 |
| 公开样例闭包 | 2套31样例的author/slots/guide/preview存在，作者哈希匹配、sources无私有原件；37个入口/说明文件中160个本地链接存在 |

全套unittest结束后仅补充Report Audit入口一句任务选择摘要及公开研究来源链接；引擎代码未变。随后再次正常打包、只读包检查、两包validator和上述4项定向回归，绑定以下最终manifest：

发布前另修开发工具`verify_template_assets.py`的个人浏览器路径：默认使用Playwright已安装的Chromium，支持`--browser-executable`且要求路径为现有文件。它位于Skill包之外，针对该修改执行上述参数与无资产写入smoke，Chromium版本145.0.7632.6；未据此重跑全套，也未改变包身份。

| 包 | bundle-manifest.json SHA-256 |
|---|---|
| how-to-report | `6198052e64ad2209d06dbd038880eec6d220e9b522600c91909ee0b1e02a7798` |
| report-audit | `17f99c129712a76421abf9be6c8e79b7abbaf24351e96a14bfc85df772f59942` |

Windows执行测试时设置`PYTHONDONTWRITEBYTECODE=1`，使子进程不向完整Skill包写入`__pycache__`。最初未设置时，包闭包检查正确发现运行缓存；该轮测试中止后通过正常打包重建，再执行上述完整回归。不要把缓存失败归为模型或布局缺陷。

公开样例是独立索引和合成作者输入，未自动注册到`library`；各自的默认实例、迁移检查与视觉限制见[结构样例](../../examples/consulting-explanatory/README.md)和[公开研究样例](../../examples/consulting-public-patterns/README.md)。取用新内容后仍需computed重测及目标PowerPoint成图检查。不能把PDF结构内化说成源PDF原样保真，也不能把这些检查说成已证明全部模型执行或审美质量。
