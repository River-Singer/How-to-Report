# 分类解释行

`explanation.rows` · 独立样例索引，不是引擎 `library query` 注册项。

- 栅格：纵向行组；标签/解释为1:4共享显式比例
- 关系：classification
- 读序：按行：分类名→解释→例子与边界
- 适用：解释同一分类维度下的3–5类概念
- 不适用：有先后依赖的流程；大量精确记录的查找清单
- 容量：当前3行，每行1解释+例子+边界
- 溢出：先去冗余，保留对象、条件和范围；换栅格或在语义边界拆页。拒绝缩正文、隐藏内容、以留白指标强行凑满。
- 支持边界：标签列宽由fr约束统一，未实现自动取最长标签作为共享track。

## 使用

查看[预览](../previews/explanation.rows.png)、[作者](../authors/explanation.rows.json)和[槽位](../slots/explanation.rows.json)。运行 `python instantiate.py --template explanation.rows --output instance.json`；替换内容可增加 `--values values.json`，值文件仅接受 `text`、`charts`、`images`。然后从project根目录使用 `python skills/how-to-report/scripts/report_engine.py build --input examples/consulting-public-patterns/instance.json --output /absolute/new-build --pptx /absolute/new.pptx --geometry-policy computed`。

每次替换重新测排。正文14pt、最小9pt，统一语义颜色、纯色。表用于查阅核对，图用于解释比较判断；选型以任务为准。示例文字和数据均为原创合成。来源文件、客户正文、截图和品牌没有包含在这个发布目录中。

原生文字/形状可编辑；注册图形由程序计算并输出原生形状，改数应重建。真实图片替换后其内部不具备文字编辑能力。此目录提供默认实例，不是任意长文自动续排系统；稀疏方法样例不等于完成的高密度业务汇报。

公开作者移除了私有来源metadata，因此具有新的author SHA；预览若只是沿用相同可见内容，catalog显式记录原作者SHA与关系，不将旧验收冒充新输入receipt。

## 结构来源

- [公开结构参考](https://www.bcg.com/assets/2024/executive-perspectives-ai-and-genai-in-customer-engagement-4dec.pdf)，PDF第8页
- [公开结构参考](https://www2.deloitte.com/content/dam/Deloitte/se/Documents/audit/AI%20presentation%20for%20the%20Audit%20Committee%20-%20Second%20draft.pdf)，PDF第4页
