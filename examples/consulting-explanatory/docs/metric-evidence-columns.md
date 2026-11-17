# 服务资源与范围索引

`metric-evidence-columns` · 独立样例索引，不是引擎 `library query` 注册项。

- 栅格：通栏四列查阅索引：维度、数量、单位、范围说明
- 关系：查阅五项服务资源和范围，核对维度—数量—说明的对应
- 读序：标题→主结构（自上而下/自左向右）→解释或适用边界
- 适用：资源、服务范围、不同单位指标的精确查阅和核对
- 不适用：解释增长、差异、分布或排名；没有比较基准的独立单值柱
- 容量：五项资源，每项数量、单位和范围就近对应
- 溢出：先压缩冗余短语并保留限定条件；超出槽位实测容量则调整分组或分续页。拒绝缩小正文、遮盖、删证据。
- 支持边界：这是呈现精确记录的索引表。保留原五个合成值200人、12区域、80项目、4环节、3类型；不把查阅记录包装成量级比较或能力结论。需要解释数据时，先明确同口径比较关系和基准再选图。

本次为表示选择修复：原来五个不同单位的独立单值柱均呈满高，缺少可解释的共同关系。现移除这些柱形，不发明新基准。对应作者、槽位与预览均已正常 computed 重建，并由 PowerPoint 实际成图后查看。这项修复不是同内容仅换样式的受控对照。

## 使用

查看[预览](../previews/metric-evidence-columns.png)、[作者](../authors/metric-evidence-columns.json)和[槽位](../slots/metric-evidence-columns.json)。运行 `python instantiate.py --template metric-evidence-columns --output instance.json`；替换内容可增加 `--values values.json`，值文件仅接受 `text`、`charts`、`images`。然后从project根目录使用 `python skills/how-to-report/scripts/report_engine.py build --input examples/consulting-explanatory/instance.json --output /absolute/new-build --pptx /absolute/new.pptx --geometry-policy computed`。

每次替换重新测排。正文14pt、最小9pt，统一语义颜色、纯色。表用于查阅核对，图用于解释比较判断；选型以任务为准。示例文字和数据均为原创合成。来源文件、客户正文、截图和品牌没有包含在这个发布目录中。

原生文字/形状可编辑；注册图形由程序计算并输出原生形状，改数应重建。真实图片替换后其内部不具备文字编辑能力。此目录提供默认实例，不是任意长文自动续排系统；稀疏方法样例不等于完成的高密度业务汇报。

本页 catalog 记录修正后的作者及真实预览身份；它不同于目录中只移除私有来源 metadata、沿用既有预览的其他页面。此次未批量重做其余20页。

## 结构来源

- 用户提供的结构参考，组1，第4页
- 用户提供的结构参考，组1，第5页
