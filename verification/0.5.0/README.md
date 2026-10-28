# 0.5.0 工程验证与模型测试边界

日期：2026-10-28。本目录记录完整 A/B 开发候选的实际工程检查；对应需求与限制见[本版交付说明](../../docs/complete-plan-release.md)。这些检查不代表模型已经学会方法、不代表真实 MASTer 项目成果，也不是正式 V1 准出结论。

## 已执行的工程检查

| 检查 | 实际结果与范围 |
|---|---|
| 全量单元回归 | 260 项运行，259 项通过，1 项跳过；99.019 秒，Python 3.14.4 |
| 跳过原因 | Windows 当前账户不能创建实际符号链接（WinError 1314）；对应 dangling-link 实物分支未执行。模拟 reparse/link 分支仍有覆盖，不能替代实物分支 |
| 两包构建及一致性 | `how-to-report`、`report-audit` 0.5.0；源码计算结果与发布文件逐字节一致 |
| 离线来源 | 领域与核心方法两份来源清单校验通过，校验过程未联网 |
| 评测输入 | 51 项有效：原 25 项、14 项分阶段变形、12 项 V05 变形；仅完整性检查，没有执行模型 |
| 合成算术 oracle | 通过；不将算术对账解释为因果归因 |
| Skill 格式 | 两包通过 skill-creator 的 `quick_validate.py`，使用 Python UTF-8 模式 |
| Python 静态检查 | 19 个源码/开发工具文件可编译，并通过 Python 3.10 语法解析；实际运行环境为 3.14.4，没有执行真实 3.10 解释器 |
| 格式与独立包 | 源码/测试/文档 whitespace 检查通过；原始 PDF 转写保留的 3 处尾空格单独列为来源字节例外。全量回归包含移走 checkout 后实际运行独立包的检查 |

测试日志见 [engineering-suite.log](engineering-suite.log)。原日志中跳过项的本机临时路径已替换为说明文字；测试名称、结果和最终计数保留。项目没有配置通用 linter 或静态类型检查命令，因此没有把编译检查称作这两项检查。

最终暂存区全量 whitespace 检查在 `gantt-task-taxonomy.txt` 的 255、258、260 行发现原始 PDF 转写的尾空格，两份生成包保留相同字节，共 9 条提示。为保留取得的来源文字和已测哈希，没有清洗这些行；仅排除这 3 份同源归档文件后的其余暂存内容检查通过，不声称未排除的全量命令为零提示。

最初整合检查出现过 7 个失败：6 个独立搬迁测试夹具漏带新增共享依赖，另 1 个仍使用旧评测数量。修复夹具与断言后完成上述全量运行；没有关闭或绕过独立搬迁检查。独立复核另发现同日当前/历史预测冲突和超大百分比异常，已修复，并加入历史预测与实际事件的可见核查警告；随后重新构建、完成 260 项全量测试及最终浏览器检查。Skill 格式检查首次受到 Windows 默认 GBK 解码影响，随后以 `-X utf8` 对同一文件成功执行。

## 浏览器与视觉证据

最终安装包的实际浏览器结果见 [browser-02/browser-receipt.json](browser-02/browser-receipt.json)：Chromium 145.0.7632.6，14 个常规页面分别进入 1600×1000、1280×800、390×844 视口；四稿实际 PDF 分别为 5、1、2、6 页。导航、讲稿、全屏、非首页进入 Backup 后返回原位、媒体解码/播放/离页暂停与打印 poster 均有实际检查。额外覆盖跨年及非等距日期、10 项行动分页、长历史分页、密集日期降级表格、无基线及未知验收、长标签警告和非法历史拒绝。检查前后实现文件哈希相同。新增预测冲突与巨整数拒绝、历史已发生日期警告、无 hash 初次打开落在主线首页的检查也已通过。此前 `browser/` 保留最后语义修复前的实际记录，最终包以 `browser-02/` 为准。

可打开[演示组件](browser-02/advanced/index.html)、[五类进度视图](browser-02/schedule/index.html)、[视频及打印替代](browser-02/video/index.html)查看。页面与截图均是合成工程输入，只证明声明的交互、数据映射及布局行为，不作为优秀汇报内容范本。界面采用近白浅蓝、轻薄磨砂控件、柔和阴影和单主标题；大背景字等装饰仅为按内容选择的方法建议，不自动强加到正文或数据图中。

复核时应分别看数值与几何、实际截图、内容语义；DOM 无溢出或截图稳定都不能替代语义反读与真实听众试读。负例目录故意包含超长内容、非法素材声明或不能解码的文件；它们触发拒绝或警告才是预期结果。

## 可复现命令

在仓库根目录运行只读检查：

```text
python -B tools/package_skills.py check
python -B tools/vendor_knowledge_sources.py check
python -B evaluation/tools/validate_cases.py
python -B evaluation/tools/numeric_oracle.py
python -B -m unittest discover -s tests -v
```

浏览器检查依赖开发环境已有的 Playwright、Chromium 与 pypdf，不随 Skill 运行包安装。可查看 `python -B tools/check_presentation_browser.py --help`；给 `--package skills/how-to-report`、一个包外新目录作为 `--output`，并以本目录 `browser-02/video-input/plan.json` 作为 `--video-plan`，复核图片、视频、关系、主线/Backup和进度视图。没有浏览器时必须保持“未做实际渲染检查”。

## 待用户执行

MASTer v5 的 8 个案例、16 份生成/独立审计提示、冻结包及空输出目录位于工作区外置 `case-handoff/master-v5/`。未运行批量模型生成、独立审计或修订。51 项公开设计输入也属于已读 Dev 材料，不是未见 Holdout。

离线共有 43 份来源文字表示：领域 19 份取得的文字与 4 份原创摘要，核心方法另 20 份原创摘要；不能称为 43 份原作全文。GAO 全文直接下载被自动审批以 `blocked by policy` 拦截，现以标明覆盖范围的离线原创摘要保存。其他来源也按实际读取范围与许可标注。

源文件、最终包和工程证据的指纹由 [release-receipt.json](release-receipt.json) 记录。旧 master-v1–v4 的 1,219 个文件已与开发前 SHA-256 基线比对，全部保持不变。
