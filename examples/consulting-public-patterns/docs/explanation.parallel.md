# 并列概念解释

`explanation.parallel` · 独立样例索引，不是引擎 `library query` 注册项。

- 栅格：等宽3列，列内定义/机制/例子/边界
- 关系：parallel_taxonomy
- 读序：从左到右，每列由定义读到限制
- 适用：2–3个同层概念或控制机制的对照说明
- 不适用：三个互不相干主题；跨列因果链；长条款
- 容量：当前3列，每列4段
- 溢出：先去冗余，保留对象、条件和范围；换栅格或在语义边界拆页。拒绝缩正文、隐藏内容、以留白指标强行凑满。
- 支持边界：等高栅格保持同层对齐；复杂条款应语义拆分，不能只缩字号。

## 使用

查看[预览](../previews/explanation.parallel.png)、[作者](../authors/explanation.parallel.json)和[槽位](../slots/explanation.parallel.json)。运行 `python instantiate.py --template explanation.parallel --output instance.json`；替换内容可增加 `--values values.json`，值文件仅接受 `text`、`charts`、`images`。然后从project根目录使用 `python skills/how-to-report/scripts/report_engine.py build --input examples/consulting-public-patterns/instance.json --output /absolute/new-build --pptx /absolute/new.pptx --geometry-policy computed`。

每次替换重新测排。正文14pt、最小9pt，统一语义颜色、纯色。表用于查阅核对，图用于解释比较判断；选型以任务为准。示例文字和数据均为原创合成。来源文件、客户正文、截图和品牌没有包含在这个发布目录中。

原生文字/形状可编辑；注册图形由程序计算并输出原生形状，改数应重建。真实图片替换后其内部不具备文字编辑能力。此目录提供默认实例，不是任意长文自动续排系统；稀疏方法样例不等于完成的高密度业务汇报。

公开作者移除了私有来源metadata，因此具有新的author SHA；预览若只是沿用相同可见内容，catalog显式记录原作者SHA与关系，不将旧验收冒充新输入receipt。

## 结构来源

- [公开结构参考](https://www.bcg.com/assets/2024/executive-perspectives-ai-and-genai-in-customer-engagement-4dec.pdf)，PDF第7页
- [公开结构参考](https://www.ey.com/content/dam/ey-unified-site/ey-com/en-us/noindex/documents/ey-frontier-ai-in-action-rethinking-cybersecurity-and-resilience.pdf)，PDF第15页
