# 0.11.5 工程与样例检查

2026-11-17。本版增加显式列Grid的有限column_span、容器rail/rule/bracket和显式sequence连接，补充视觉组织方法与实际成图审美审核，并更新Storybook展示。以下检查覆盖工程和中性样例，不是外部AI业务测试成绩。

| 检查 | 实际结果 |
|---|---|
| 正常打包与只读闭包检查 | 两包0.11.5通过，Run contract仍为0.1；全套测试后再次check通过 |
| 两包quick_validate | 显式UTF-8模式下均通过 |
| 全套unittest | 654项，653通过、1跳过，489.941秒；跳过项为Windows符号链接权限WinError1314 |
| Python语法 | skill-src、tools、tests共231个Python文件通过AST解析 |
| Lint、静态类型检查 | 项目没有独立配置命令；未把AST检查称为lint或type-check通过 |
| 跨列与组合回归 | 非法span、轨道最小宽度、跨列换行、字体和内容保留、装饰内距、层序/ID、正常computed导出均覆盖 |
| 信息占用 | 新增正常build回归：加bracket和sequence后，实际content-diagnostics不虚增内容占用 |
| 原生形状与连接 | 真正CLI导出chevron，核prstGeom、正确stCxn/endCxn、无重复ID、连接先绘制且节点后绘制 |
| 真实成图 | 实际查看PowerPoint 16.0的7页最终样例；前6页为3组对照，第7页为独立综合展示 |

三组对照保留12、13、12个标题/正文信息单元；作者字体角色与原生PPT文本相同（原生换行空白忽略），另行核对原生显式字号也相同。页脚标签用于识别前后版本，不计入正文相等；第7页不冒充控制变量对照。样例的[本地核验](../../examples/visual-composition/verify.py)检查内容、原生对象和综合页三列各行相同top/height。[完整样例与限制](../../examples/visual-composition/README.md)提供可重放输入、PPTX、预览及哈希。

实际视觉观察：跨三列的共享带使平台覆盖范围可见；四阶段chevron与连接使方向可追踪；闭环、能力组与适用维度通过不同语法区分。综合页经同一行尺寸/间距约束修正后，三列重复行对齐，未见遮挡或丢字。前6页是局部能力演示，存在有意保留的大面积空白，不能据此声称完成业务稿减页或达到高信息密度，也不赋予无依据的审美总分。

最终样例PPTX SHA-256：`32f742c0b657f0b314d7c12c1a5b0d926df441f6ec306b6a49c7268bb039dab0`。

| 包 | bundle-manifest.json SHA-256 |
|---|---|
| how-to-report | `1a451b1303d4d81425a0d06683ed021bdb6c39b54ea45f6d5f449b9363975114` |
| report-audit | `8fcde74b12eda03ec1125ddd8a050b4dcccec7d90d59be9b24db01335847bd27` |

检查期间处理了两项执行环境问题：首次71项布局检查中，一项CLI在同伴仍修改运行依赖时正确拒绝依赖变化；源码稳定后的最终全套包含该项并通过。首次宿主validator按系统GBK读取UTF-8失败，显式启用UTF-8后两包通过。测试均设置PYTHONDONTWRITEBYTECODE=1，未用修改测试预期的方式绕过故障。

本次还修正了公开方法导航中的旧“span均未实现”描述，并独立补上宽度/文长变化与装饰占用的行为回归。未实现row_span/subgrid、自动跨栏续排、任意避障、通用布尔/遮罩、Canvas后端或完整Figma/Photoshop内核；独立审美仍需要看当前成图。外部AI测试由用户运行，收到结果后才比较事实、叙事、设计及执行差异。
