# 0.6.0 独立审查入口

更新：2026-10-30。当前审查对象是内容思考、Markdown成稿与保留的可靠性工具。HTML、SVG、PPTX和视觉验收已退出，旧0.5.x页面证据仅供历史核对。

建议按以下顺序检查：

1. [当前范围](content-scope.md)：目标探索与直接正文是交付中心，简单任务不套模板，默认不建立全套Graph。
2. [架构](architecture.md)与两个入口：[生成](../skills/how-to-report/SKILL.md)、[审计](../skills/report-audit/SKILL.md)。区分目标确认、事实支持、工作完成和实际沟通效果。
3. 生成方法与共享目标/探索/叙事/成稿方法：看实际动作是否帮助当前任务，是否仍将制作旁白、字段或布局要求交给用户。
4. 非视觉脚本：Run、版本、计算、画像、经验及排期校验。核路径、来源身份、无覆盖、显式选择与初始未执行状态，不能把记录合法当语义真实。
5. [当前四项内容设计](../evaluation/content-0.6.0/README.md)：检查分阶段释放、可比条件与实质结果。目录校验不是模型执行；不得用预设隐藏动机作为唯一答案。
6. [本版工程记录](../verification/0.6.0/README.md)：核对实际运行范围、最终包身份和跳过项；旧[0.5.3记录](../verification/0.5.3/README.md)不冒充新结果。

```text
python -B tools/package_skills.py check
python -B tools/vendor_knowledge_sources.py check
python -B evaluation/tools/validate_content_cases.py
python -B evaluation/tools/validate_content_cases.py --root evaluation
python -B -m unittest discover -s tests -v
```

前一个评测命令只验证当前4项输入，后一个核对历史67项。都不调用模型，不认证内容质量。真实用户输入与私有案例不在公开仓库；使用公开合成案例可以完成独立代码/方法审查，不需要父目录材料。
