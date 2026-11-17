# 产品界面与关键操作说明

`interface-showcase` · 独立样例索引，不是引擎 `library query` 注册项。

- 栅格：主图+窄说明栏（4:1）
- 关系：可视界面—解释或操作重点
- 读序：标题→主结构（自上而下/自左向右）→解释或适用边界
- 适用：真实产品截图、难以原生重绘的界面
- 不适用：纯数字比较应重绘图表；整页截图冒充可编辑
- 容量：中；1图+3观察
- 溢出：先压缩冗余短语并保留限定条件；超出槽位实测容量则调整分组或分续页。拒绝缩小正文、遮盖、删证据。
- 支持边界：样例为明确图片占位；替换真实图片后内部不可编辑，外部说明可编辑。

## 使用

查看[预览](../previews/interface-showcase.png)、[作者](../authors/interface-showcase.json)和[槽位](../slots/interface-showcase.json)。运行 `python instantiate.py --template interface-showcase --output instance.json`；替换内容可增加 `--values values.json`，值文件仅接受 `text`、`charts`、`images`。然后从project根目录使用 `python skills/how-to-report/scripts/report_engine.py build --input examples/consulting-explanatory/instance.json --output /absolute/new-build --pptx /absolute/new.pptx --geometry-policy computed`。

每次替换重新测排。正文14pt、最小9pt，统一语义颜色、纯色。表用于查阅核对，图用于解释比较判断；选型以任务为准。示例文字和数据均为原创合成。来源文件、客户正文、截图和品牌没有包含在这个发布目录中。

原生文字/形状可编辑；注册图形由程序计算并输出原生形状，改数应重建。真实图片替换后其内部不具备文字编辑能力。此目录提供默认实例，不是任意长文自动续排系统；稀疏方法样例不等于完成的高密度业务汇报。

公开作者移除了私有来源metadata，因此具有新的author SHA；预览若只是沿用相同可见内容，catalog显式记录原作者SHA与关系，不将旧验收冒充新输入receipt。

## 结构来源

- 用户提供的结构参考，组1，第26页
- 用户提供的结构参考，组1，第27页
