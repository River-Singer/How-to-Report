# 0.7.0 统一工作流工程复核

日期：2026-11-02。生成与独立审计主工作流、专题职责、逐页材料交付和多轮修订已完成实现及工程复核。模型案例尚未执行；以下结果不证明汇报质量、真人理解或相对旧版的效果提升。

## 实际结果

| 检查 | 结果与边界 |
|---|---|
| 全量单元测试 | 224项运行：223通过、1跳过；unittest计时85.980秒，包含包搬迁和既有工具边界检查 |
| 跳过项 | Windows无法创建真实符号链接（WinError1314）；相关模拟路径/写边界测试仍执行，不将跳过记为通过 |
| 两包构建和一致性 | how-to-report、report-audit均为0.7.0，Run契约仍为0.1；生成包与规范源一致 |
| Skill格式和离线来源 | 两包quick_validate通过；本地来源完整性通过，无联网 |
| 评测输入 | 当前4案、历史0.6.1六案、0.6.0四案及原67案的结构/哈希校验通过；没有调用模型 |
| 独立文档链接检查 | 59份变更公共/安装包文档、324个本地链接无缺失；规范源的物化依赖另由包检查覆盖 |
| 历史保护 | 开始时登记的4857个既有历史归档、验证、评测与私有交接/结果文件，哈希无变化、无缺失；不发布私有文件清单或内容 |
| 私有交接准备器 | 12项独立临时合成工程测试，11通过、1因符号链接权限跳过；覆盖重复准备/冻结、修改与多余文件、输入隔离及冻结后新增输出，不执行模型 |

命令与包身份见[检查摘要](checks.json)。这是对真实检查结果的整理，不是原始stdout；不包含本机私有路径。项目没有配置通用lint/type-check，本轮不虚报这两项通过。

## 复现公开工程检查

在仓库根目录运行：

```text
python -X utf8 -B tools/package_skills.py build
python -X utf8 -B tools/package_skills.py check
python -X utf8 -B tools/vendor_knowledge_sources.py check
python -X utf8 -B evaluation/tools/validate_content_cases.py
python -X utf8 -B evaluation/tools/validate_content_cases.py --root evaluation/content-0.6.1
python -X utf8 -B evaluation/tools/validate_content_cases.py --root evaluation/content-0.6.0
python -X utf8 -B evaluation/tools/validate_cases.py
python -X utf8 -B -m unittest discover -s tests -v
```

Skill格式检查使用宿主提供的skill-creator验证器，不属于仓库依赖。私有交接材料与开始时的历史指纹在用户工作区，不是公开仓库的复现前提；公开四案足以审查输入协议。

## 版本身份与未验证部分

| 包 | bundle-manifest.json SHA-256 |
|---|---|
| how-to-report | `f4885c828023edaec42e612b3646baeeb7d98e43484d9039bf02d5955e524167` |
| report-audit | `b900db5be25e6a85b4d5758830a1bfa7f8ecb2fe6aa9511a42909a7c6ed3e023` |

旧narrative-page-behavior已从当前源和新包退役，叙事职责并入meeting-expression，生成/审计主方法各自承担唯一流程；旧冻结文件没有被改写为新方法。此记录没有进行浏览器/视觉验收，当前产品也不承担该阶段。

下一步由用户运行[四个基础案例](../../evaluation/content-0.7.0/README.md)：前两案0.6.1/0.7.0对照，后两案仅新版，共六组。实际结果将检验材料取舍、逐页可用性、多轮保真与审计精度。工程通过、方法文献和自评都不替代这些证据。
