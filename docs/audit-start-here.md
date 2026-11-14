# 0.10.0 独立审查入口

独立审查覆盖实际正文、真实委派及可靠性证据。PPT 成品审查取得实际可读正文与页或对象定位，再沿内容审计主线核对。页面制作、渲染与原生对象检查由完整制作工作流负责，宿主打开和编辑记录各自的实际结果。

先读[当前范围](content-scope.md)、[架构](architecture.md)和两个入口：[生成](../skills/how-to-report/SKILL.md)、[审计](../skills/report-audit/SKILL.md)。实际审计由主会话协调真实独立子Agent；它先只读听众正文，获得初读后再开放目标、来源和必要作者说明。继承创作历史不能冒称独立；已被真实委派的执行者直接审计，不递归委派。

检查[委派](../skills/report-audit/references/agent-delegation.md)、[挑战](../skills/report-audit/references/directed-challenge.md)与[职责](../skills/report-audit/references/stakeholder-roles.md)接入：新完整任务不能只凭头衔推定权限；挑战者只能返回问题，主Agent自己分析和求助；审计意见仍可包括依据、影响与修法。纯问句、文件存在或Run字段均不证明真实执行。

核专业方法的输入、分析动作和能支持到哪里，而不是只出现名词。核事实、贡献、条件、版本、替代选项和必要解释；数值既看真实计算证据，也看比较方向与最终推荐是否一致；主Agent先用已有材料，真正必要缺件不能降成可选深化。反证或部分回复应改变对应判断，拒补不补造事实。

[0.9.1 的18组41轮输入](../evaluation/content-0.9.1/README.md)沿用其上一版全部18场景，用同一事实和请求复核计算、来源、更新和正文价值。只按当前轮暴露来源，操作者参考和未来材料留在操作者范围。[0.9.1 工程记录](../verification/0.9.1/README.md)与[0.8.4 记录](../verification/0.8.4/README.md)绑定各自版本。0.10.0 的总入口 PPT 接续由独立单例交付和用户实际运行核验，具体方法见 [PPT 交接](../skills/how-to-report/references/ppt-handoff.md)。

```text
python -B tools/package_skills.py check
python -B tools/vendor_knowledge_sources.py check
python -B evaluation/tools/validate_content_cases.py
python -B evaluation/tools/validate_content_cases.py --root evaluation
python -B -m unittest discover -s tests -v
```

内容输入检查默认覆盖0.9.1的18组41轮，历史根检查67项。显式`--root evaluation/content-0.8.4`保留13组29轮验证。公开输入全合成，可独立验证。上述命令检查工程契约与输入，模型质量、实际制作和宿主使用各需对应运行证据。
