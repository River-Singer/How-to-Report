# 0.7.2 工程检查记录

日期：2026-11-02。本版调整按需示范调用、连续改稿教学与审计对自身解释、影响和建议的核对。以下是实际工程检查；未运行本版模型案例，不证明内容已经改善。

| 检查 | 实际结果 |
|---|---|
| 全量单元 | 224项，223通过、1跳过；unittest计时85.279秒，外层运行器85.740秒 |
| 跳过项 | Windows真实符号链接创建缺少权限，WinError1314；不算通过 |
| 两包与离线来源 | 0.7.2构建、一致性、两包Skill格式与本地来源检查通过；Run仍为0.1 |
| 输入 | 当前四案及历史0.7.1/0.7.0/0.6.1/0.6.0与原67案校验通过；未执行模型 |
| 引用 | 122份当前文档、532本地链接、32片段检查通过；规范源物化闭包另由打包检查验证 |
| 历史保护 | 登记5698个旧文件，无缺失或字节变化 |
| 新交接工程 | 10项临时合成测试通过，4.612秒；保留无覆盖、半冻结保护及后续输出追加 |

[检查摘要与包身份](checks.json)来自真实检查结果，非模型成绩。项目未配置通用lint/type-check；仅记录实际完成的差异空白检查。公开摘要不含私有资料清单。

## 复现公开检查

在仓库根目录运行：

```text
python -X utf8 -B tools/package_skills.py check
python -X utf8 -B tools/vendor_knowledge_sources.py check
python -X utf8 -B evaluation/tools/validate_content_cases.py
python -X utf8 -B evaluation/tools/validate_content_cases.py --root evaluation/content-0.7.1
python -X utf8 -B evaluation/tools/validate_content_cases.py --root evaluation/content-0.7.0
python -X utf8 -B evaluation/tools/validate_content_cases.py --root evaluation/content-0.6.1
python -X utf8 -B evaluation/tools/validate_content_cases.py --root evaluation/content-0.6.0
python -X utf8 -B evaluation/tools/validate_cases.py
python -X utf8 -B -m unittest discover -s tests -v
```

源码变更后先用package_skills.py build重建，Skill格式检查使用宿主skill-creator验证器。私有交接在独立工程检查后冻结并通过只读复核：4组12轮、287个冻结文件，冻结时outputs为空，未运行模型。具体项目输入及冻结凭据留在用户工作区，公开摘要只记录数量和身份边界。

[四组12轮](../../evaluation/content-0.7.2/README.md)待用户执行；已见回归与开发侧设计的迁移试测分开，组内持续会话，审计逐阶段开放。方法读取日志可得则记录，否则未知。没有匹配基线、独立保留集或真人试读支持整体效果声明。[旧0.7.1记录](../0.7.1/README.md)保持原有身份。
