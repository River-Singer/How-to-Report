# 0.9.0 独立审查入口

当前检查内容思考、Markdown成稿、真实委派契约和保留的可靠性工具。HTML、SVG、PPTX和视觉验收不属于当前范围，旧证据保留原版本身份。

先读[当前范围](content-scope.md)、[架构](architecture.md)和两个入口：[生成](../skills/how-to-report/SKILL.md)、[审计](../skills/report-audit/SKILL.md)。实际审计由主会话协调真实独立子Agent；它先只读听众正文，获得初读后再开放目标、来源和必要作者说明。继承创作历史不能冒称独立；已被真实委派的执行者直接审计，不递归委派。

检查[委派](../skills/report-audit/references/agent-delegation.md)、[挑战](../skills/report-audit/references/directed-challenge.md)与[职责](../skills/report-audit/references/stakeholder-roles.md)接入：新完整任务不能只凭头衔推定权限；挑战者只能返回问题，主Agent自己分析和求助；审计意见仍可包括依据、影响与修法。纯问句、文件存在或Run字段均不证明真实执行。

核专业方法的输入、分析动作和能支持到哪里，而不是只出现名词。核事实、贡献、条件、版本、替代选项和必要解释；主Agent先用已有材料，真正必要缺件不能降成可选深化。反证或部分回复应改变对应判断，拒补不补造事实。

[当前18组41轮输入](../evaluation/content-0.9.0/README.md)保留13类回归并补5组专业探针。只按当前轮暴露来源，操作者参考和未来材料不可交给生成者。[本版工程记录](../verification/0.9.0/README.md)与[历史0.8.4记录](../verification/0.8.4/README.md)分开，模型效果尚未验证。

```text
python -B tools/package_skills.py check
python -B tools/vendor_knowledge_sources.py check
python -B evaluation/tools/validate_content_cases.py
python -B evaluation/tools/validate_content_cases.py --root evaluation
python -B -m unittest discover -s tests -v
```

当前入口检查18组41轮，历史根检查67项；显式`--root evaluation/content-0.8.4`保留13组29轮验证。命令都不调用模型，不认证内容质量。公开输入全合成，可独立验证，不依赖父目录私有项目。
