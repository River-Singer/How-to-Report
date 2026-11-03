# 0.8.1：13场景、25轮输入

状态：**输入已准备，模型未运行**。由用户执行，公开素材全为合成，私有项目原话与交付留在用户工作区。情境覆盖扩展不等于全部能力已通过。

| 组 | Case ID | 场合 | 轮数 |
|---|---|---|---|
| 01-internal-competition | `C081-INTERNAL` | 内部AI实践比赛 | 2 |
| 02-external-competition | `C081-EXTERNAL` | 外部创新比赛 | 1 |
| 03-business-direct | `C081-BUSINESS-DIRECT` | 业务一级领导 | 2 |
| 04-business-department | `C081-BUSINESS-DEPARTMENT` | 业务二级领导 | 1 |
| 05-technical-direct | `C081-TECHNICAL-DIRECT` | 技术一级领导 | 2 |
| 06-technical-department | `C081-TECHNICAL-DEPARTMENT` | 技术二级领导 | 2 |
| 07-general-manager | `C081-GENERAL-MANAGER` | 总负责人评议 | 3 |
| 08-external-peer | `C081-EXTERNAL-PEER` | 外部同行 | 1 |
| 09-project-progress | `C081-MATERIAL` | 项目进度 | 3 |
| 10-weekly-report | `C081-WEEKLY` | 书面周报 | 2 |
| 11-monthly-report | `C081-MONTHLY` | 月度评议 | 1 |
| 12-comparison-transfer | `C081-TRANSFER` | 培训迁移 | 2 |
| 13-audit-regression | `C081-AUDIT` | 独立审计 | 3 |

详见[运行与评审协议](PROTOCOL.md)、[场景责任与编辑参照](coverage.md)。这些文件仅给操作者和评审，不整体发给模型。

```text
python evaluation/tools/validate_content_cases.py
python evaluation/tools/validate_content_cases.py --case C081-INTERNAL --turn 1
```

05最后一轮交单条标题；09第一轮保存真实目标探索回复；10交书面周报；13交初读/审计；其余完整材料给逐页方案。单次检查不执行模型，不自动创建报告输出。
