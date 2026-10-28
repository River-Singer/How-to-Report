# 合成计算示例

`synthetic-cost.csv` 全部为虚构工程数据，与任何用户项目无关。[spec.json](spec.json) 显式定义每行 part 粒度，两期单价/数量，CNY 总金额，全部输入行，无隐式筛选或换算，half_even 保留 2 位，仅最终聚合值舍入。

本示例定义：采用单列交互项的价量代数分解。手算 oracle：基期 `100×2+50×3=350`；现期 `110×3+55×2=440`；差额 `90`。价格项 `10×2+5×3=35`；数量项 `100×1+50×(−1)=50`；交互项 `10×1+5×(−1)=5`；三项和 `90`。这是算式核对，不是成本原因或实际业务收益。

```text
python <installed-how-to-report>/scripts/report_calculate.py run <installed-how-to-report>/assets/report-calculation/spec.json --output <new-external-directory>
```

输出需新建在安装包外且父目录存在。缺数/重复键/哈希改变应失败；请在临时副本构造这些输入，不编辑安装包。实际使用需按真实资料重新确认定义、单位、范围和版本。完整合同见[计算说明](../../references/report-calculation.md)。
