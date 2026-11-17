# 双维度四情景

`scenario.quadrants` · 独立样例索引，不是引擎 `library query` 注册项。

- 栅格：2×2语义矩阵+独立行列维度标签
- 关系：independent_dimensions
- 读序：先读两个维度，再定位所属交叉情景
- 适用：用两个独立条件确定四类管理方式
- 不适用：任意四项并列；没有独立维度却硬凑象限
- 容量：2个维度×2档，4单元各2条
- 溢出：先去冗余，保留对象、条件和范围；换栅格或在语义边界拆页。拒绝缩正文、隐藏内容、以留白指标强行凑满。
- 支持边界：分类档位由业务定义；面积与位置不编码数量，不是散点坐标或风险评分。

## 使用

查看[预览](../previews/scenario.quadrants.png)、[作者](../authors/scenario.quadrants.json)和[槽位](../slots/scenario.quadrants.json)。运行 `python instantiate.py --template scenario.quadrants --output instance.json`；替换内容可增加 `--values values.json`，值文件仅接受 `text`、`charts`、`images`。然后从project根目录使用 `python skills/how-to-report/scripts/report_engine.py build --input examples/consulting-public-patterns/instance.json --output /absolute/new-build --pptx /absolute/new.pptx --geometry-policy computed`。

每次替换重新测排。正文14pt、最小9pt，统一语义颜色、纯色。表用于查阅核对，图用于解释比较判断；选型以任务为准。示例文字和数据均为原创合成。来源文件、客户正文、截图和品牌没有包含在这个发布目录中。

原生文字/形状可编辑；注册图形由程序计算并输出原生形状，改数应重建。真实图片替换后其内部不具备文字编辑能力。此目录提供默认实例，不是任意长文自动续排系统；稀疏方法样例不等于完成的高密度业务汇报。

公开作者移除了私有来源metadata，因此具有新的author SHA；预览若只是沿用相同可见内容，catalog显式记录原作者SHA与关系，不将旧验收冒充新输入receipt。

## 结构来源

- [公开结构参考](https://www.pwc.com/gx/en/issues/artificial-intelligence/wef-leveraging-generative-ai-for-job-augmentation-and-workforce-productivity-2024.pdf)，PDF第12页
