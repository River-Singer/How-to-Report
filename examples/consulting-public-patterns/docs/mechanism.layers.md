# 输入处理输出分层

`mechanism.layers` · 独立样例索引，不是引擎 `library query` 注册项。

- 栅格：左顺序关系图+右三层说明，比例1:4
- 关系：input_processing_output
- 读序：上方输入→中部处理→下方输出→共同约束
- 适用：机制、系统边界、材料如何形成输出
- 不适用：无依赖的分类；多向反馈网络
- 容量：3层各3个模块，2条边界
- 溢出：先去冗余，保留对象、条件和范围；换栅格或在语义边界拆页。拒绝缩正文、隐藏内容、以留白指标强行凑满。
- 支持边界：沿现有down拓扑改为从上往下；不宣称实现候选bottom-up布局或带边标签的路由。

## 使用

查看[预览](../previews/mechanism.layers.png)、[作者](../authors/mechanism.layers.json)和[槽位](../slots/mechanism.layers.json)。运行 `python instantiate.py --template mechanism.layers --output instance.json`；替换内容可增加 `--values values.json`，值文件仅接受 `text`、`charts`、`images`。然后从project根目录使用 `python skills/how-to-report/scripts/report_engine.py build --input examples/consulting-public-patterns/instance.json --output /absolute/new-build --pptx /absolute/new.pptx --geometry-policy computed`。

每次替换重新测排。正文14pt、最小9pt，统一语义颜色、纯色。表用于查阅核对，图用于解释比较判断；选型以任务为准。示例文字和数据均为原创合成。来源文件、客户正文、截图和品牌没有包含在这个发布目录中。

原生文字/形状可编辑；注册图形由程序计算并输出原生形状，改数应重建。真实图片替换后其内部不具备文字编辑能力。此目录提供默认实例，不是任意长文自动续排系统；稀疏方法样例不等于完成的高密度业务汇报。

公开作者移除了私有来源metadata，因此具有新的author SHA；预览若只是沿用相同可见内容，catalog显式记录原作者SHA与关系，不将旧验收冒充新输入receipt。

## 结构来源

- [公开结构参考](https://www.bcg.com/assets/2024/executive-perspectives-ai-and-genai-in-customer-engagement-4dec.pdf)，PDF第9页
- [公开结构参考](https://kpmg.com/content/dam/kpmgsites/th/pdf/2025/05/future-of-corporate-services-presentation.pdf.coredownload.inline.pdf)，PDF第9页
