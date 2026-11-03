# 0.8.3 独立审查入口

更新：2026-11-03。当前审查对象是内容思考、Markdown成稿与保留的可靠性工具。HTML、SVG、PPTX和视觉验收已退出，旧0.5.x页面证据仅供历史核对。

建议按以下顺序检查：

1. [当前范围](content-scope.md)：目标到逐页材料是交付中心，简单任务不套模板，默认不建立全套Graph。
2. [架构](architecture.md)与两个入口：[生成](../skills/how-to-report/SKILL.md)、[审计](../skills/report-audit/SKILL.md)。区分目标确认、事实支持、工作完成和实际沟通效果。
3. 生成方法与共享目标/探索/叙事/成稿方法：看重要新断言是否对回真实对象与来源，部分回复是否保留有效余项；主张仍须有必要解释，概要与正文保持同一含义。可对照[短长教学](../skills/how-to-report/assets/examples/report-depth-proposals.md)；不按字数、页数或标题数判断厚度，也不把制作旁白、字段或布局要求交给用户。
4. 非视觉脚本：Run、版本、计算、画像、经验及排期校验。核路径、来源身份、无覆盖、显式选择与初始未执行状态，不能把记录合法当语义真实。
5. [当前十三场景与回归设计](../evaluation/content-0.8.3/README.md)：检查自然输入、分阶段释放和实质结果，本版继承全部自然请求和分阶段来源，检查归属、版本、条件及实际改稿，同时保留充分解释与有据推荐。审计先看正文、再对照来源、最后开放作者说明；目录校验不是模型执行，不得用预设隐藏动机作为唯一答案。
6. [0.8.3工程记录](../verification/0.8.3/README.md)供核对本轮实际检查与包身份；[0.8.2工程记录](../verification/0.8.2/README.md)独立保留。V10的0.8.2产物已复核，V11的0.8.3待用户运行，不能混用两版效果证据。

```text
python -B tools/package_skills.py check
python -B tools/vendor_knowledge_sources.py check
python -B evaluation/tools/validate_content_cases.py
python -B evaluation/tools/validate_content_cases.py --root evaluation
python -B -m unittest discover -s tests -v
```

前一个评测命令只验证当前13场景25轮输入，后一个核对历史67项；旧4案可另用 `--root evaluation/content-0.6.0` 检查。都不调用模型，不认证内容质量。真实用户输入与私有案例不在公开仓库；使用公开合成案例可以完成独立代码/方法审查，不需要父目录材料。
