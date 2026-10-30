# 内容评测：当前4项，历史67项保留

当前候选0.6.0的设计位于[当前清单](dataset.json)。四项都是合成Dev输入，每项最多两个顺序回合：目标确认、局部修改与停止、价值和新证据、发言身份与沟通方式。没有固定标准文案、页数、图表或维度数量。模型尚未运行。

```text
python evaluation/tools/validate_content_cases.py
python evaluation/tools/validate_content_cases.py --case C06-GOAL --turn 1
python evaluation/tools/validate_content_cases.py --case C06-GOAL --turn 2
```

把命令输出中的当前任务和列出的fixture交给执行者；保存真实第一轮答复后才释放第二轮。执行者不读取cases.jsonl、判据或未来材料。命令只检查/展示输入，不调用模型、网络或fixture代码。

模型批量生成、独立审计与修订继续由用户运行。每个案例可用一个生成会话依次完成两轮，再用新会话独立审计；不要求拆成更多模型批次。输出放在仓库外新目录。用户可选择先跑单案；工具不会启动测试。

[当前协议](PROTOCOL.md)规定内容维度与可选同条件基线。[运行记录](RUN-TEMPLATE.md)保留真实版本、输入、交互和结果。工程输入完整性不等于行为通过；本目录不能提供模型质量或真实受众理解结论。

## 历史输入

旧`dataset.json`、四个catalog和全部旧fixtures保持原字节，共67项。显式检查：

```text
python evaluation/tools/validate_content_cases.py --root evaluation
python evaluation/tools/validate_content_cases.py --root evaluation --case V051-REQUEST --turn 1
python evaluation/tools/numeric_oracle.py
```

[旧协议](../PROTOCOL.md)保留旧Q6页面等定义。旧套件不自动成为当前发布门槛，也不按新维度重算旧成绩。旧视觉素材/数值oracle仅用于各自范围，未读Holdout和正式对照仍须另行建立。
