# 工作空间、业务能力与共享数据

`capability-map` · 独立样例索引，不是引擎 `library query` 注册项。

- 栅格：分层主区+外部系统栏（4:1）
- 关系：工作空间—能力域—共享功能—数据，外部集成
- 读序：标题→主结构（自上而下/自左向右）→解释或适用边界
- 适用：应用架构、功能范围地图
- 不适用：用架构层级表现不相关清单
- 容量：高；4能力域×4能力+3共享/数据项
- 溢出：先压缩冗余短语并保留限定条件；超出槽位实测容量则调整分组或分续页。拒绝缩小正文、遮盖、删证据。
- 支持边界：源阶段配色改全局色角色；真实阶段含义须通过标签，不能仅靠颜色。

## 使用

查看[预览](../previews/capability-map.png)、[作者](../authors/capability-map.json)和[槽位](../slots/capability-map.json)。运行 `python instantiate.py --template capability-map --output instance.json`；替换内容可增加 `--values values.json`，值文件仅接受 `text`、`charts`、`images`。然后从project根目录使用 `python skills/how-to-report/scripts/report_engine.py build --input examples/consulting-explanatory/instance.json --output /absolute/new-build --pptx /absolute/new.pptx --geometry-policy computed`。

每次替换重新测排。正文14pt、最小9pt，统一语义颜色、纯色。表用于查阅核对，图用于解释比较判断；选型以任务为准。示例文字和数据均为原创合成。来源文件、客户正文、截图和品牌没有包含在这个发布目录中。

原生文字/形状可编辑；注册图形由程序计算并输出原生形状，改数应重建。真实图片替换后其内部不具备文字编辑能力。此目录提供默认实例，不是任意长文自动续排系统；稀疏方法样例不等于完成的高密度业务汇报。

公开作者移除了私有来源metadata，因此具有新的author SHA；预览若只是沿用相同可见内容，catalog显式记录原作者SHA与关系，不将旧验收冒充新输入receipt。

## 结构来源

- 用户提供的结构参考，组1，第29页
- 用户提供的结构参考，组1，第30页
