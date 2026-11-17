# 判断与图形证据

`judgment.evidence` · 独立样例索引，不是引擎 `library query` 注册项。

- 栅格：证据图/解释栏非对称双栏，比例3:2
- 关系：claim_supported_by_evidence
- 读序：标题判断→排序条形图→原因边界与优先级
- 适用：同单位分类数据支持重点判断或排序
- 不适用：只供核对的供应商名单/工作人天明细；无数据的观点
- 容量：1排序图4类+2层解释
- 溢出：先去冗余，保留对象、条件和范围；换栅格或在语义边界拆页。拒绝缩正文、隐藏内容、以留白指标强行凑满。
- 支持边界：合成反馈样本，不代表真实业务；解释型任务用图，精确查阅任务改表。

## 使用

查看[预览](../previews/judgment.evidence.png)、[作者](../authors/judgment.evidence.json)和[槽位](../slots/judgment.evidence.json)。运行 `python instantiate.py --template judgment.evidence --output instance.json`；替换内容可增加 `--values values.json`，值文件仅接受 `text`、`charts`、`images`。然后从project根目录使用 `python skills/how-to-report/scripts/report_engine.py build --input examples/consulting-public-patterns/instance.json --output /absolute/new-build --pptx /absolute/new.pptx --geometry-policy computed`。

每次替换重新测排。正文14pt、最小9pt，统一语义颜色、纯色。表用于查阅核对，图用于解释比较判断；选型以任务为准。示例文字和数据均为原创合成。来源文件、客户正文、截图和品牌没有包含在这个发布目录中。

原生文字/形状可编辑；注册图形由程序计算并输出原生形状，改数应重建。真实图片替换后其内部不具备文字编辑能力。此目录提供默认实例，不是任意长文自动续排系统；稀疏方法样例不等于完成的高密度业务汇报。

公开作者移除了私有来源metadata，因此具有新的author SHA；预览若只是沿用相同可见内容，catalog显式记录原作者SHA与关系，不将旧验收冒充新输入receipt。

## 结构来源

- [公开结构参考](https://www.bain.com/globalassets/noindex/2025/bain_report_technology_report_2025.pdf)，PDF第7页
