# 自有参数模板使用说明

画布为纯白16∶9，全部页型共用标题、页眉、页脚及正文区。

在安装包根目录使用下列命令，输入与生成项目保存在安装包外。

```text
python scripts/report_ppt.py catalog
python scripts/report_ppt.py describe kpi
python scripts/report_ppt.py validate --input <参数JSON>
python scripts/report_ppt.py build --input <参数JSON> --output <新项目目录> --assets <图片资源根>
python scripts/report_ppt.py copy-template --output <私有模板根>
```

通过ppt_runtime.py的check/export/inspect检查、导出与回读项目，完整命令见包内references/ppt-production.md。模板根通过report_ppt.py的全局--template参数指定，修改私有tokens后执行refresh重生成原型与使用说明。

输入顶层包含schema_version=1、template_id=business-blue-v1和pages数组。每页包含id、family、variant、content及可选config/notes。content_source可保存当前材料身份。每家族content schema和config默认值见下列说明。

字符按CRLF规范化后的Unicode码点计数，空格、标点和换行计入。每项长度检查后继续做字体与框体测量。数组空余槽及关闭的可选槽保留空carrier，有对应输入项时执行字段min/max。数值和页码通过明确派生规则生成显示文字。

原型使用语义标记及技术轴线占位，业务生成应传入实际内容。原始材料没有相应关系或数据时，记录具体缺口并选择资料能够支持的页型。

制作前先读安装包references/ppt-production.md的图表选择与图片用途，现场主画面优先清晰图形，精确查值或交叉定位需要时使用简洁表格。图片焦点与完整显示/裁剪配置见image说明。

- [封面](families/cover.md) · 交代汇报主题和发言信息
- [目录](families/toc.md) · 说明报告的组成及顺序
- [章节过渡](families/chapter.md) · 交代进入哪个内容部分
- [核心指标](families/kpi.md) · 比较同层级指标及必要解释
- [并列事项](families/parallel.md) · 展示同层级事项及各自解释
- [问题与方案](families/comparison.md) · 逐行对应问题、方案与行动
- [数据与结论](families/chart.md) · 用明确数值表达比较、趋势或互斥构成
- [时间轴](families/timeline.md) · 解释有据的时间顺序与节点
- [甘特计划](families/gantt.md) · 说明任务持续时间与重叠安排
- [流程步骤](families/process.md) · 表达真实步骤及方向
- [图文案例](families/image.md) · 展示图片证据与相应解释
- [结束与行动](families/ending.md) · 收束认识或列出实际下一步
- [战略屋](families/strategy.md) · 说明共同目标、能力支柱与基础
- [分层架构](families/architecture.md) · 解释层级与各层职责
- [能力矩阵](families/matrix.md) · 交叉两个维度定位单元格
- [中心辐射](families/hub.md) · 解释共同中心与周边对象的关系
- [房子图战略图.pptx](families/source-house.md) · 战略屋与目标支撑
- [蓝色逻辑架构图.pptx](families/source-architecture.md) · 模块接口与分层架构
- [立体结构逻辑图1122.pptx](families/source-spatial.md) · 立体层次与结构关系
- [圆形逻辑图PPT模版.pptx](families/source-circular.md) · 环绕扇区与循环关系
- [树状层级](families/hierarchy.md) · 表达根节点、分支与子项的有据归属关系

新增四套源模板的128页入口见[按原文件名索引](SOURCE-COLLECTIONS.md)。每页包含关系、场景、完整调用、逐框字段与可见预览。
