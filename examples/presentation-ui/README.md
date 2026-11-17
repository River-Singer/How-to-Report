# 可重放的 PPT 设计组合

三种共享设计 recipe 已接入正常 `library → compose → build computed → PowerPoint` 链路。示例是原创合成内容，主展示沿用户最新选择使用 `report-default`。`consulting-spectrum` 保留为第六套可选色卡，草绿、青蓝、深蓝、灰、橘、红按角色使用。

| Recipe | 适用情况 | 真实预览 |
| --- | --- | --- |
| `editorial-pillars` | 3–4个同级支柱/解释；共享标题基线、分类标题带、跨列共同说明 | [并列解释](previews/editorial-pillars.png) |
| `stage-ribbon` | 3–5个有序阶段；连续方向带、阶段说明逐列对应、出口收束 | [阶段带](previews/stage-ribbon.png) |
| `capability-platform` | 多类输入经共享平台形成多类输出；平台跨列表达支撑范围 | [共享平台](previews/capability-platform.png) |

查看 [PPTX](presentation-ui.pptx)、[请求](request.json)、[作者工程](author.json)与[成图身份](preview-manifest.json)。这些是组件能力示例，不是已完成的业务报告；样例较少的文字不能代替真实材料的密度和减页审查。

从 `project` 根目录可运行（输出须是新路径）：

```powershell
python skills/how-to-report/scripts/report_engine.py library recipe.stage-ribbon
python skills/how-to-report/scripts/report_engine.py compose --input examples/presentation-ui/request.json --output D:/new-ui-author.json
python skills/how-to-report/scripts/report_engine.py build --input D:/new-ui-author.json --output D:/new-ui-build --pptx D:/new-ui.pptx --geometry-policy computed
```

修改请求槽位后重新 compose；作者工程绑定事实后，也可更新事实及 `recipe_source` 再正常 build。构建忽略缓存 frame，由行列/栅格布局重新测量。禁止子项坐标/字号覆盖，正文14pt、最小9pt，超过容量报错而不缩字。形状和文字原生可编辑；手动编辑输出后若需要再次由引擎生成，应同步修改作者来源。

新增能力覆盖并列解释、过程、共享平台三类关系。170个历史参数模板在库中标记为 `structural-template`，默认图样没有批量换皮；本次三种组合为 `designed-composition`。原生保真源资产是另一类，保留原稿配置与颜色。身份用于提示选型，不是美观评分。制作时应查看实际预览并比较适合本页语义和容量的候选；精确查阅表、甘特图和简洁分栏无需强加装饰。
