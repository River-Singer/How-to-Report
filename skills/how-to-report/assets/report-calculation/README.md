# 合成计算示例

`synthetic-cost.csv` 全部为虚构工程数据，与任何用户项目无关。[spec.json](spec.json) 显式定义每行 part 粒度，两期单价/数量，CNY 总金额，全部输入行，无隐式筛选或换算，half_even 保留 2 位，仅最终聚合值舍入。

本示例定义：采用单列交互项的价量代数分解。手算 oracle：基期 `100×2+50×3=350`；现期 `110×3+55×2=440`；差额 `90`。价格项 `10×2+5×3=35`；数量项 `100×1+50×(−1)=50`；交互项 `10×1+5×(−1)=5`；三项和 `90`。这是算式核对，不是成本原因或实际业务收益。

```text
python <installed-how-to-report>/scripts/report_calculate.py run <installed-how-to-report>/assets/report-calculation/spec.json --output <new-external-directory>
```

输出需新建在安装包外且父目录存在。缺数/重复键/哈希改变应失败；请在临时副本构造这些输入，不编辑安装包。实际使用需按真实资料重新确认定义、单位、范围和版本。完整合同见[计算说明](../../references/report-calculation.md)。

## 0.2：对照结果写出推荐理由

[comparison-spec.json](comparison-spec.json)与[synthetic-comparison.csv](synthetic-comparison.csv)定义两个虚构方案的相同费用项：甲3600+2400=6000元，乙4000+3200=7200元。输入本来就是合成CSV，没有另一个被工具验证的原件。对象顺序固定为乙减甲，结果+1200元；relation为minuend_greater。期望值是手算示范，下面实际执行后才会产生本次凭证：

```text
python <installed-how-to-report>/scripts/report_calculate.py run <installed-how-to-report>/assets/report-calculation/comparison-spec.json --output <new-external-comparison-directory>
```

读该目录result.json的标签、difference、unit和relation，再对读拟写正文。可写“乙比甲多1200元”；不能写“乙更省”。假如另一份真实材料支持乙有观察操作的机会，这仍是“额外费用换取机会”的取舍，不是自动全面占优；本例CSV自身没有效果证据。

[person-time-spec.json](person-time-spec.json)与[synthetic-person-time.csv](synthetic-person-time.csv)定义两组各32个名额，每名额1半天，population_basis为capacity。总计64人·半天，即32人·天；两组是否为同一批人未知，不能称64位独立参加者，不能说实际已经投入这些工时。

```text
python <installed-how-to-report>/scripts/report_calculate.py run <installed-how-to-report>/assets/report-calculation/person-time-spec.json --output <new-external-person-time-directory>
```

读两种结果的unit及population_basis，写“按全部名额计，共64人·半天（32人·天）”。小时数和员工费用需要额外定义/资料，不能由半天直接补成4小时。本例两套资料独立，不暗示某方案拥有另一例的容量。

两个输出均可用其中的replay-spec.json在另一个全新外部目录回放。回放复现同一方法，不是独立审计；示例文件没有预填实际执行结果。
