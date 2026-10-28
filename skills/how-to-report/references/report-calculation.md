# 显式本地计算与凭证

需要可复用的结构化数值计算时读本页。先遵守[数值证据方法](numeric-evidence.md)：确认计算对象、口径与证据责任。此工具不发现业务公式，不自动确定源版本，不读取 Knowledge，也不执行附件代码、SQL 或任意表达式。简单人工算术不必使用它。

```text
python <installed-how-to-report>/scripts/report_calculate.py run <spec.json> --output <new-directory>
```

Python 3.10+ 标准库，离线、任意工作目录及 `-I` 可用。输出父目录必须存在，目标目录必须全新且位于安装目录外；拒绝 UNC/device 路径与输出路径中的链接/reparse。失败不覆盖源文件或已有目录；实际 I/O 失败可能留下部分输出，保留检查，改用新目录。退出 0 表示指定计算已运行，2 表示调用、数据或 I/O 失败；都不是语义审计结论。

## 输入与定义

从[合成示例](../assets/report-calculation/README.md)复制 spec 后，逐项替换为真实已确认定义。spec 精确字段如下；不支持额外字段：

- `calculation_version: "0.1"`，`id`、`definition_ref` 非空。后者指向用户确认/适用业务定义的位置，不由工具验证其真实性。
- `source: {id, revision, ref, sha256}`。正整数 revision 不是自动选择的最新版本；ref 为显式本地 CSV 路径，相对 spec 文件；sha256 是实际输入字节的 SHA-256。字节不符立即失败，禁止偷偷刷新哈希。版本更新应另存 spec/输出并复核下游依赖。
- `context` 精确包含 `measure, unit, grain, period, population, filters, limitations`，均为非空文字。**filters 描述输入已采取的筛选，工具不执行筛选；所有 CSV 行都会参与计算。** 不自动换汇、换单位、关联表、补缺失、排序配对或判断业务可比性。确认输入范围后再调用。
- `columns` 显式指定运算角色对应的 CSV 列名；`column_units` 为每个相同角色声明输入单位。`context.unit` 为主结果单位。工具保留单位声明，但不执行量纲校验；不能凭字段名自动决定企业公式或混合币种。比例的分子/分母单位分别由角色给出。
- `key_columns` 为非空、无重复列名数组，代表每行唯一粒度。按去除首尾空白后的完整键检查唯一/非空；CSV 标题也必须唯一。额外列保留在快照但不参与运算。
- `missing_policy: "error"`；`decimal_places` 为 0–8 整数；`rounding: "half_up" | "half_even"`。半值向远离零方向或取偶分别明确，最终聚合值才舍入，不逐行舍入。

支持的白名单：

| operation | columns 的角色 | 确切方法 |
| --- | --- | --- |
| sum | value | 所有 value 求和 |
| product_sum | price, quantity | 所有 price × quantity 求和；角色名称不决定实际业务单位 |
| ratio_of_sums | numerator, denominator | 分子和 ÷ 分母和；不是各行比率平均；总分母为零失败 |
| price_quantity_decomposition | base_price, base_quantity, current_price, current_quantity | 两期乘积和差额，分成基期数量权重的价格项、基期价格权重的数量项，以及单列交互项 |

分解恒等式：`Δ = Σ((p1−p0)q0) + Σ(p0(q1−q0)) + Σ((p1−p0)(q1−q0))`。该方法不把交互项归到某一因素；采用其他合理分解约定时需用其他明确方法，不能为了符合本例改企业口径。对账成立不等于因果归因。

CSV 支持 UTF-8（可含 BOM）、最多 4 MiB/10,000 行。每个数字只接受可选负号、最多 12 位整数和 12 位小数的十进制；不接受空值、NaN/Infinity、科学记数法、布尔、千分符或隐式零。空表、重复粒度、缺列/错宽度失败。适配器使用 80 位十进制运算，覆盖上述有界加乘精度；比率可为循环小数，未舍入字符串仍可能是 80 位近似。更大数据或不同方法应由实际可用宿主工具执行并保留等价凭证，不宣称本工具支持。

## 真实输出与审计交接

新目录包含原字节 `spec.json`、`input.csv`、实际 `result.json`、`calculation-receipt.json`，以及可直接复跑的 `replay-spec.json`。replay 只把 `source.ref` 改为本地 `input.csv`；原 spec 不变，修改及新哈希写入凭证。它是衍生复跑输入，不能冒称原始 spec。结果以十进制字符串提供未舍入/最终舍入值、单位声明、行数、公式和精度，不让 JSON 浮点显示伪造精度。

凭证绑定真实输入/定义/结果/方法脚本哈希、实际 Python 版本、必要的数据检查。源码哈希用于和所用包比对，不自动下载旧脚本；归档实际使用的 Skill 版本。`independent_review=not_run`、`source_authenticity=not_assessed` 保留，工具不会创建 Run 的 pass、verified 或接纳记录。默认 stdout 仅状态、输出位置和结果指纹，正文数据在显式输出目录。

使用 Run 时，将 spec、输入和实际结果按需登记为 Source/Artifact，写精确 `uses`；业务/独立复核完成后才记录真实 Check。原数据变更须保留旧输出，声明新版本、运行新计算并更新受影响标题/图表/结尾；哈希匹配或同程序复跑不能代替独立算式核对。

无 Python 时提供公式、所需数据与手工可完成部分，并明确自动执行未运行。不要只复制空凭证或示例值就声称完成真实计算。
