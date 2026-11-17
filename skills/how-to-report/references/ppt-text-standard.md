# PPT全局文字规范

文字规范复用已有`report-14pt`设计profile。它和全局配色共同控制computed作者工程；没有再建立一套字号或段落参数。Storybook中的“全局文字规范”可查看实际角色、单位、能力边界和三页真实可编辑示例。

## 查询和取用

```text
python <Skill>/scripts/report_engine.py typography --profile report-14pt
python <Skill>/scripts/report_engine.py typography --profile report-14pt --example
python <Skill>/scripts/report_engine.py typography --tokens <已有tokens.json>
```

第一条返回完整规范及原始tokens，第二条返回可保存为JSON、经正常`build --geometry-policy computed`构建的作者工程。第三条沿原接口查询指定tokens的解析结果。`--profile`与`--tokens`不能同时传入；`--example`必须指定profile。

作者及recipe的全局字段是`brief.design_profile`，值为查询结果`global_binding.value`中的`id`、`sha256`、`hash_method`三项。编译器验证profile身份后加载其tokens，字体、测量与导出共享该配置。不要手填过期摘要，也不要使用不存在的`typography_profile`字段。颜色仍由`brief.palette_id`及[色彩标准](ppt-color-standard.md)控制。

## 字体和语义字阶

当前profile的标题、正文、latin和fallback声明均为Microsoft YaHei。每个文字角色实际解析一个`font_family`，用于Latin、East Asian、Complex Script。当前没有独立中西文或逐字字体回退链，也不自动嵌入字体；缺失字体交由目标环境替代，必须检查实际PowerPoint成图。

| 角色 | 原生pt | 字重 | 行距倍数 | 用途 |
|---|---:|---:|---:|---|
| hero / metric | 33.6 | 700 | 1.1 | 主视觉或主指标 |
| chapter / title | 22.4 | 700 | 1.1 | 章节或页标题 |
| heading | 16.8 | 700 | 1.2 | 区块标题 |
| metricCompact | 16.8 | 700 | 1.1 | 紧凑指标 |
| body / compactBody | 14 | 400 | 1.3 | 正文 |
| bodyStrong | 14 | 700 | 1.3 | 强调正文 |
| diagramCompact / label | 11.2 | 400 | 1.25 | 图表或结构标签 |
| labelStrong | 11.2 | 700 | 1.25 | 强调标签 |
| caption / diagramMicro / dataCaption | 9 | 400 | 1.25 | 次要注释或小标签 |
| captionStrong | 9 | 700 | 1.25 | 强调注释 |

字号以SVG px保存，原生pt=px×0.75。正文14pt的行距是18.2pt。当前规范角色最低9pt。绑定`report-14pt`且使用`computed`的新稿还会在发布前检查实际生成文字，显式局部覆盖也不能降到9pt以下；不满足时以`typography_minimum_font`拒绝构建，不发布项目。`caption`和`captionStrong`使用注释灰；`dataCaption`和`diagramMicro`使用正文色，重要分母和数据不可为了节省空间降为低对比度注释。

字重输入100–500解析为普通400，600–900解析为加粗700；没有九档原生字重的保证。

## 段落、内距与对齐

当前profile统一默认：`paragraph_gap=0`、四边`insets=[0,0,0,0]`、左对齐、顶部定位。实际卡片的留白可以由外层布局容器padding/gap承担，不能把容器间距与文字段前后混为一谈。

文本style支持`font_family`、`font_size`、`weight`、`line_height`、`paragraph_gap`、`insets`、`align`、`vertical_anchor`、`color`。原生文本框支持左/中/右对齐、上/中/下定位和四边内距；不支持两端对齐。

单文本中的显式换行开始新的逻辑段，自动折行只增加行距。`paragraph_gap`加在后续段之前，不额外添加首段前或末段后的空白。当前没有分别设置“段前”和“段后”的独立字段。`paragraph-flow`组件的gap负责独立子段之间的距离，子段内部换行继续使用自身行距。

全局profile先给出字阶和角色继承；元素显式style可覆盖，富文本run最后覆盖字重和颜色。新稿应优先引用语义角色。Storybook段距/对齐页中的局部参数仅是能力示范，不会修改全局标准。

## 富文本支持范围

实际run格式：

```json
[
  {"text": "合成示例："},
  {"text": "本周完成率", "weight": 700},
  {"text": "82%", "weight": 700, "color": "secondary"}
]
```

支持同一文本框内普通/加粗与局部颜色，统一字号、字体、行距。内容按真实run拼接后测量，自动折行保留文字和样式片段；混合字重时采用较粗字重测量，可能保守留白。

尚不支持的高层作者功能：逐run字号或字体、斜体、下划线、删除线、上下标、富文本超链接、原生项目符号/编号、首行/悬挂缩进、分栏、竖排、直接把Markdown/HTML解释为富文本。正常构建遇到未支持的run/style字段会拒绝，不会静默丢弃格式。源PPT保真重放可能含这些原生格式，不代表新的computed作者接口已支持生成它们。

## 真实覆盖边界

该profile通过正常作者绑定控制引用主题角色的computed文字和参数模板。9pt闸门覆盖layout/recipe新生成文字、展开的组件和图表的文字及原生图表JSON字号；参数模板仅检查有语义角色标记的新生成字段。原生源资产、图片内部文字及固定源几何文字保留原件，`legacy-replay`和未绑定profile的兼容入口保持原行为。套用profile不能自动使任意原始PPT变成14pt，也不代表内容变化后自动重排完成。字体回退、实际行距显示和可编辑性仍以目标PowerPoint成图及对象检查为证据。
