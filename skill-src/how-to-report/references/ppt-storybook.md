# PPT组件库与Storybook

新稿先沿How-to-Report确定内容路线，并完成[制作前设计评估](ppt-design-preflight.md)，把每页任务、数据分析和素材用途映射到真实查询的组件及容量约束后，再提交参数。AI不临时编写绘图脚本、自由SVG或对象坐标。所有图形、布局与PPTX都由已注册的engine入口生成。缺少合适原生组件时，已有可读原图可经image容器直接使用；必要且缺失的图按授权设明确占位。确需新绘图能力时才扩展engine并取得测试证据后调用。

取组件前先沿[PPT交接](ppt-handoff.md#页面视觉语法与篇幅预算)定本页视觉语法和篇幅预算。同类数据成组选型，统一图种、可比尺度/尺寸、色义与标签位置，再填入各自真实口径；不要为了多用图种而混搭，也不把无分母绝对量伪装为环形比例。主内容与侧栏、等权比较及重复小图的排布先用[栅格设计选择](ppt-grid-design.md)判断，再以现有嵌套row/column/fr-grid表达；这些设计建议不是新增注册asset，不能编造asset ID。跨列仅使用当前明确支持的column_span，不编造row_span/subgrid字段。先尝试在授权内合页，不能让单个组件预览的巨大尺寸决定页面数量。

这条制作规则不替代How-to-Report的材料分析、听众表达和叙事取舍。组件可以生成清晰的比例图，不能替用户确认数据分母、因果与动作依据。

全局配色的注册色卡、来源、语义角色、对比度与调用方式见[色彩标准](ppt-color-standard.md)。AI通过`palettes [ID]`查询并选择工程级`palette_id`，由engine统一解析；原生源保真取用保留源色。

## 浏览与取用

```text
python <Skill>/scripts/report_engine.py storybook-export --catalog <native-catalog> --output <new-site>
python <Skill>/scripts/report_engine.py catalog --catalog <native-catalog> --query <关键词>
python <Skill>/scripts/report_engine.py catalog <asset-id> --catalog <native-catalog>
python <Skill>/scripts/report_engine.py chart-assets --executable true
python <Skill>/scripts/report_engine.py chart-assets <chart-id>
python <Skill>/scripts/report_engine.py library <template-or-component-id>
```

导出目录内`index.html`可离线直接打开。列表按类型、来源、图表关系和关键词过滤，每页24项，详情按256项分片加载。图标独立展示。原生页、组合和叶对象保留父子导航、稳定身份和来源，隐藏及兼容分支默认不展示。

原生对象预览使用原PowerPoint页面的对应区域，可能包含邻近或遮叠对象，不能据此宣称已取得孤立组件的实际成图。图表预览由engine使用明确的合成示例数据编译SVG。实例导出仍应核实际PPTX，原稿685页保真证据不会自动覆盖任意新组合。

## 原生资产库

```text
python <Skill>/scripts/report_engine.py catalog-import --sources <sources.json> --output <new-catalog>
python <Skill>/scripts/report_engine.py catalog-build --catalog <catalog> --request <request.json> --pptx <new.pptx>
```

sources为列表或仅包含sources字段的对象，每项包含id、project和可选preview_dir。project指向已提取的原生工程。源依赖压缩存储，目录按页分片。保持目录完整即可搬迁；Storybook只是索引和预览，不携带生成所需的全部资产包。

请求形式如下，使用实际查询得到的asset ID和text slot ID。

```json
{
  "asset_ids": ["<registered-asset-id>"],
  "columns": 1,
  "texts": {"<registered-asset-id>": {"t0": "替换文字"}}
}
```

位置、间距、缩放及多项网格由engine计算。原生资产以原稿几何和样式为基础，长文本、增删节点、跨组连接和不支持的高级对象按该资产合同处理，不能擅自补坐标。原稿渐变保留；新设计继续优先纯色。直接可编辑的文字槽位以`capabilities.text_slots`为准。

## 图表参数

```text
python <Skill>/scripts/report_engine.py chart-build --request <request.json> --output <new-project> --pptx <new.pptx>
```

请求必须提供asset和data，可选options及palette_id。Storybook详情中的示例可编辑并下载；下载后运行显示的正常CLI命令，由engine重新校验与计算。网页当前图片是已生成的示例，修改输入不会让浏览器自行猜测图形或几何。

全部词汇按FT九类收录，可执行状态来自当前实现；待实现图种不能提交生成。说明中分别给出数据形态、场景、禁用条件、编辑能力与限制。缺地图几何、期间、分母或分布明细时不能用占位图片伪装真实数据图表。

参数模板、组件和recipe沿`library`及正常`build --geometry-policy computed`生成。底层primitive仅作为引擎实现合同展示，不能作为AI直接手填frame的新稿入口。统一报告样式沿report-14pt profile；源原生对象则明确保留原样式。

## 全局配色

色卡类型同时展示真实引擎预览、语义角色、分类/顺序/发散色列、对比度和参考来源。初始收录报告蓝、商务蓝青、青绿琥珀、靛紫科技和北欧蓝金五套；来源网站颜色由本项目分配为PPT语义角色，不称为原站官方PPT主题。

命令行通过`report_engine.py palettes [ID]`查询列表或完整合同。色卡详情同时显示预览主题与当前生成请求采用的主题；点击“应用此配色”会同步全局选项、实色色块和请求。

顶部“全局配色”默认为保留现有配色，不改变现有输出，保留请求中已有或用户手填的palette_id。选择色卡后，下载和复制的作者工程及recipe请求写入`brief.palette_id`，图表请求写入顶层`palette_id`。切回“保留现有配色”会恢复全局覆盖前的主题。正文仍为14pt/80%黑、注释35%黑，颜色不能替代数据标签或状态文字。

选择配色只同步生成请求和显示实色色块，其他静态预览仍显示已经生成的颜色；执行engine后才获得新的SVG/PPTX。原生页/组合/原子请求及多原生选择不会注入palette_id，保持源色。图片内部和显式固定色按资产实际能力处理，不假定全局token会重着色所有对象。

## 全局文字规范

现有`profile.report-14pt`作为可调用资产收录，完整规则见[文字标准](ppt-text-standard.md)。顶部固定显示正文14pt、computed生成文字最低9pt及规范入口。详情展示16个角色实际解析后的字号、字重、颜色、行距、段间距、四边内距、对齐和字体映射；三页预览由engine实际编译，可切换查看并下载正常作者请求。

最低字号闸门仅作用于`computed`且绑定`brief.design_profile.id=report-14pt`的新稿。layout、recipe、展开组件与图表生成文字及原生chart字号低于9pt时，构建以`typography_minimum_font`拒绝且不发布项目；9pt允许。参数模板检查带文字角色标记的生成字段，底层源几何内文字保持原样。`legacy-replay`、未绑定profile的兼容流程、图片内部文字和原生保真资产不因此改写。

```text
python <Skill>/scripts/report_engine.py typography --profile report-14pt
python <Skill>/scripts/report_engine.py typography --profile report-14pt --example
```

工程通过`brief.design_profile`中的id、sha256及hash_method绑定统一规范。组件、图表、recipe及Storybook下载的参数模板新稿使用这个规范。普通参数模板和source-diagram中的可替换文字确实按字体角色tokens解析；后者的源位置和图形化文字仍有固定能力边界。模板静态原型保留旧样式，不能当作新请求已完成规范重算的预览。原生catalog取用不注入文字规范，保持原稿格式。

目前只有一套注册文字标准，没有尚未接入engine的字体切换控件。当前角色统一使用Microsoft YaHei，中西文不具有独立字体映射或逐字回退链；现有富文本支持局部加粗、颜色和换行，独立段前/段后、逐run字体/字号、斜体、下划线等按实际合同列为未支持。不能将查到的规范误称为已自动整治所有历史稿件。

## 页面空间诊断

正常`build --geometry-policy computed`求解布局后读取本版`content-diagnostics.json`。逐页看诊断所用区域、组件获配面积、估计内容占用、估计空白，以及未知或不可评估的对象；正文区域可由已求解layout节点标识，不能靠AI另填一组坐标。诊断采用的阈值是可调整的审阅提示，不是80分标准或像素级墨迹测量。

将结果对回`page.job`和实际成图：少量数据的巨幅环图、疏松拓扑或相邻页分别讲同一话题，可能需要缩小组件并合并必要内容；组件框覆盖页面不等于信息充足。原生导入内部无法估计时保留未知，不能当0或通过。信息确已完整且留白服务其用途时保留，内容仍缺定义或比较时先补有据内容。重构后重新build并读新报告；不以扩大图形、字号、装饰或编造数据来抬占用率。图表承载遵守[PPT交接](ppt-handoff.md#定量内容的图形承载)的用户约束，诊断文件与补数说明留在作者工作区。
