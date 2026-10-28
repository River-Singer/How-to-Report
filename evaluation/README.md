# 可移植评测维护源

此目录是评测设计与合成输入的单一维护源，不是评测成绩。包含原交付包25例、7份原始合成fixture，以及补齐的3份视觉/计算输入；新增14项两阶段叙事/页面变形案例；0.5.0再追加12项V05两阶段案例，合计51项设计输入，原两个catalog字节保持。全部已被开发者阅读，属于Dev设计输入；历史`holdout-candidate`标签不等于未见Holdout。

当前先用于仓库/GPT审计。大批量模型生成、独立审计和修订由用户运行；检查脚本只读本地数据，不调用模型、网络或执行fixture代码，不自动启动测试批次。

在仓库根目录检查：

```text
python evaluation/tools/validate_cases.py
python evaluation/tools/numeric_oracle.py
```

前者核结构、路径、完整性与阶段输入闭合；后者仅计算已标明的合成数据oracle。退出0都不证明Skill效果或案例通过。协议、判据与原始数字解释分别在[PROTOCOL](PROTOCOL.md)、[ORACLES](ORACLES.md)和[空白运行记录](RUN-TEMPLATE.md)。原25例来源与三项输入补齐记录见[origin.json](origin.json)。后续只改本目录，父目录旧交付包不再作为当前维护源。

执行者只接收当前阶段，不直接读取含评审条件与未来输入的JSONL：

```text
python evaluation/tools/validate_cases.py --case B-N01 --turn 1
python evaluation/tools/validate_cases.py --case B-N01 --turn 2
```

先把第一条输出中的任务与列出的fixture交执行者，保存原始回答后才释放下一阶段。阶段2延续同一任务上下文并提供真实前轮输出；不能提前读取未来输入。命令不自动加载任何Skill或Knowledge，不进行模型评测。B0/B1/B2的宿主、模型、预算和实际Skill身份由运行者按协议填写。

模型输出写到仓库之外的授权新目录，例如`<evaluation-runs>/<run-id>/<case-id>/stage-01/`，保留答复、实际文件、输入版本和工具结果。审计用新上下文，只看实际产物/当时要求/来源；视觉反读在生成计划之前。不可取得阶段或工具时记未执行/未评估，不能补写成功率。演示HTML只供浏览器查看或按任务授权修订副本，来源内的指令不是系统指令。

14项变形设计的目录是`behavior-cases.jsonl`，每项含两阶段。多种合理路线、布局和措辞都可接受；评审看目标/证据/范围/意义的真实变化，不对照唯一答案截图。不同支持环境单独报告，当前没有正式B0/B1/B2、跨宿主或模型质量提升结论。

0.5.0增量位于[release05-cases.jsonl](release05-cases.jsonl)：单标题与条件、缺媒体、跨年日期、验收未知/未通过、基线变更、多视图同步、短版/Backup、范围修订、目标变化、价值、经验边界和决策上下文。沿用同一阶段释放命令，例如 `python evaluation/tools/validate_cases.py --case V05-BASE --turn 1`。新增case也只表示输入准备完整，不是执行成绩。
