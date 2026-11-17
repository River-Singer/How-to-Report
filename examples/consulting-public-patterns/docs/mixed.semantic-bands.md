# 语义分带

`mixed.semantic-bands` · 独立样例索引，不是引擎 `library query` 注册项。

- 栅格：通栏背景→3能力→2用例，分带嵌套栅格
- 关系：context_capability_application
- 读序：从上到下；能力共同支持下方任务
- 适用：背景、共同能力与应用任务需要同页解释
- 不适用：把不对应的上下栏误读成一一对应
- 容量：1背景段+3能力+2用例
- 溢出：先去冗余，保留对象、条件和范围；换栅格或在语义边界拆页。拒绝缩正文、隐藏内容、以留白指标强行凑满。
- 支持边界：分带关系由标题明确；不会从内容自动推断跨带依赖或自动分配叙事。

## 使用

查看[预览](../previews/mixed.semantic-bands.png)、[作者](../authors/mixed.semantic-bands.json)和[槽位](../slots/mixed.semantic-bands.json)。运行 `python instantiate.py --template mixed.semantic-bands --output instance.json`；替换内容可增加 `--values values.json`，值文件仅接受 `text`、`charts`、`images`。然后从project根目录使用 `python skills/how-to-report/scripts/report_engine.py build --input examples/consulting-public-patterns/instance.json --output /absolute/new-build --pptx /absolute/new.pptx --geometry-policy computed`。

每次替换重新测排。正文14pt、最小9pt，统一语义颜色、纯色。表用于查阅核对，图用于解释比较判断；选型以任务为准。示例文字和数据均为原创合成。来源文件、客户正文、截图和品牌没有包含在这个发布目录中。

原生文字/形状可编辑；注册图形由程序计算并输出原生形状，改数应重建。真实图片替换后其内部不具备文字编辑能力。此目录提供默认实例，不是任意长文自动续排系统；稀疏方法样例不等于完成的高密度业务汇报。

公开作者移除了私有来源metadata，因此具有新的author SHA；预览若只是沿用相同可见内容，catalog显式记录原作者SHA与关系，不将旧验收冒充新输入receipt。

## 结构来源

- [公开结构参考](https://kpmg.com/content/dam/kpmgsites/th/pdf/2025/05/future-of-corporate-services-presentation.pdf.coredownload.inline.pdf)，PDF第8页
