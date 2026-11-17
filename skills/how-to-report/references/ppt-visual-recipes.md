# 可重放的成稿设计组合

在确定页面任务、关系和可用材料后，从 `library` 查询相应关系，并实际查看预览。参数库的 `structural-template` 表示结构基础；本页三种 `designed-composition` 是语义和容量匹配时的成稿设计候选。身份是用途说明，不是自动审美评分，也不意味着基础模板不能直接用于适合它的精确查阅或简洁比较任务。

| 可调用 ID | 适用关系与容量 | 构形如何承担意义 | 不适用 |
| --- | --- | --- | --- |
| `recipe.editorial-pillars` | 3–4 个同级能力、解释或支柱，1 个共同说明 | 同一标题基线和等宽列表示同级；标题色分组，正文去外框，共同说明跨列归组 | 时间先后、上下级或输入输出关系 |
| `recipe.stage-ribbon` | 3–5 个有序阶段，1 个结果说明 | 连续方向带表达顺序；说明与阶段逐列对应，阶段出口统一收束 | 无顺序的并列项目；需按真实时间间隔定位的日期轴 |
| `recipe.capability-platform` | 2–4 类输入、1 个共享平台、2–3 类输出 | 平台横跨所有列，显式表达共同支撑范围；轻输入输出层和方向连接区分层级 | 无依赖的能力清单；复杂接口网、双向或多跳依赖 |

这三种组合共用测量式行、列、栅格和角色样式。AI只提供语义槽位和事实引用，不能给子项坐标或字号。正常 `compose` 保存 `recipe_source`；`build --geometry-policy computed` 每次重放该来源，重新测量文字并计算 frame，忽略缓存 `elements`。修改事实、文本或条目数量后必须重建，保留新的布局报告和对象图。超出声明容量或物理页面容量时明确报错，不自动缩字、隐藏或省略内容。

主示例在 `assets/design-system/examples/presentation-ui.json`。从 CLI 的 `library recipe.stage-ribbon` 可取得其完整 schema、真实 SVG/PowerPoint PNG 预览和 request；再用 `compose --input REQUEST --output NEW_AUTHOR` 与 `build --input NEW_AUTHOR --output NEW_PROJECT --pptx NEW_PPTX --geometry-policy computed`。具体子命令参数以 `report_engine.py --help` 为准。

颜色通过 `brief.palette_id` 全局选择，默认 `report-default`；`consulting-spectrum` 为可选六色色卡。分类色只分组，不表达数值大小；语义状态同时用标签。色块内前景经过对比度选择，普通正文14pt/80%黑、注释最低9pt/35%黑不因换色卡改变。

这是新增的三类共享设计能力，未改动170个历史参数模板的默认图样，也没有宣称全部图样已通过审美审阅。31个公开咨询样例和23个参数代表的盘点用于选择优先问题；查阅表、甘特、对比图及文字分栏的低装饰可能正是其功能需要。真实业务仍需论证、来源、密度与全稿减页检查，技术样例的留白不能作为业务成稿通过依据。
