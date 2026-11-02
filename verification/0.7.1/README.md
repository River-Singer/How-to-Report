# 0.7.1 定向优化工程复核

日期：2026-11-02。本版保留四步生成工作流和独立审计，优化材料提炼、标题分工、来源身份、新证据后的判断更新，以及审计对自己转述和修复句的核对。以下是工程检查，未运行本版模型案例，不证明内容质量已经改善。

## 实际检查

| 项目 | 结果 |
|---|---|
| 全量单元测试 | 224项，223通过、1跳过；80.702秒 |
| 跳过原因 | Windows真实符号链接创建权限不足（WinError1314）；不将跳过记为通过 |
| 两包与离线来源 | 0.7.1构建、一致性、两包Skill格式和本地来源完整性通过；Run契约仍为0.1 |
| 评测输入 | 当前0.7.1四案、历史0.7.0四案、0.6.1六案、0.6.0四案及原67案校验通过；没有调用模型 |
| 文档链接 | 独立检查30份变更文档、103个本地链接，无缺失；规范源物化依赖另由打包检查覆盖 |
| 历史保护 | 5497份登记的历史归档、旧验证/评测、私有交接及已交结果，字节未变、无缺失 |
| 新交接准备器 | 10项临时合成工程测试通过，包括重复/半冻结保留、改动检测、后续输出允许；不执行模型 |

实际命令、包身份和检查边界见[检查摘要](checks.json)。摘要来自实际检查结果，不是原始stdout，也不包含私有文件清单。项目未配置通用lint/type-check，本记录不宣称执行过。

## 复现公开检查

在仓库根目录运行：

```text
python -X utf8 -B tools/package_skills.py check
python -X utf8 -B tools/vendor_knowledge_sources.py check
python -X utf8 -B evaluation/tools/validate_content_cases.py
python -X utf8 -B evaluation/tools/validate_content_cases.py --root evaluation/content-0.7.0
python -X utf8 -B evaluation/tools/validate_content_cases.py --root evaluation/content-0.6.1
python -X utf8 -B evaluation/tools/validate_content_cases.py --root evaluation/content-0.6.0
python -X utf8 -B evaluation/tools/validate_cases.py
python -X utf8 -B -m unittest discover -s tests -v
```

修改规范源后用 `python -X utf8 -B tools/package_skills.py build` 重建两包。Skill格式检查使用宿主提供的skill-creator验证器，不属于仓库依赖。私有测试交接与历史指纹保留在用户工作区，公开四案不依赖这些私有文件。

## 下一步验证

[四案定向回归](../../evaluation/content-0.7.1/README.md)共11轮，只运行候选版，由用户执行。各组连续会话；审计分阶段开放正文、来源与作者说明。评审参照与被测输入分开，允许成立的不同表达，并记录参照自身的更正。

这些是已见材料的回归，不能冒称未见泛化，也没有匹配基线支持总体版本提升率。历史[0.7.0工程记录](../0.7.0/README.md)与其用户结果仍属于原版本；没有浏览器、视觉或真人试读验收。
