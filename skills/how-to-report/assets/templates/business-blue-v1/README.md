# 自有参数化白底模板

包含20类页型与165个结构变体。原37个入口继续可用，新增四套用户模板的128页各有独立参数入口。统一纯白16∶9画布，标题、页眉页脚与正文区由tokens控制。

四套源模板按原文件名及逐页关系列在[源模板索引](docs/SOURCE-COLLECTIONS.md)，包含可见预览、完整调用、使用场景和逐框字段合同。

中文标题与正文采用Microsoft YaHei，字重按角色登记为400或700，拉丁文字采用Arial。此组合由原方案的已登记备选字族中选定，浏览器已核实实际命中常规体和粗体。字体文件由运行环境提供。SVG几何和字号采用px，原生PPTX按1px=9525EMU、字号1px=0.75pt转换。

[AI使用说明](docs/AI-USAGE.md)提供页型选择、参数与调用规则。唯一编辑源为templates/tokens.json和templates/page-catalog.json，SVG原型、字段绑定与文档由包内report_ppt.py生成。
