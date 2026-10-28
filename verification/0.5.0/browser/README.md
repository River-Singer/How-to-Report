# 浏览器工程验证

此目录保留首轮构建包的真实记录。后续发现进度语义校验缺陷并重新构建；最终发布复核见 [browser-02](../browser-02/README.md)。这里的通过结果仅适用于回执所列旧字节。

本目录仅含合成输入与确定性浏览器验证，不是用户项目实绩，也不是模型生成/审计案例结果。

实际使用构建后的 `skills/how-to-report`；Chromium145.0.7632.6，file导航、离线上下文。完整测量、哈希和边界结果见 [browser-receipt.json](browser-receipt.json)。14个主要页面均在1600×1000、1280×800、390×844实际viewport检查；没有常规样例几何问题。很长正文/图标签/任务标签的负例应当被检出，不能当作正常页面的设计答案。

可打开的代表样例：

- [展示能力5页](advanced/index.html)：单主标题、讲稿、关系/泳道、图片标注、Backup/返回与表格；[PDF](advanced/deck.pdf)。第一页内容很少，仅测试控件与留白，不能作为优秀内容设计基准。
- [进度5种view、6页](schedule/index.html)：摘要任务/节点分2页；[PDF](schedule/deck.pdf)。
- [真实本地合成视频2页](video/index.html)：播放、离页暂停、打印poster；[PDF](video/deck.pdf)。
- [折线与数值对应](line/index.html)：缺失点保留，窄屏横向滚动保持对应。
- [跨年且非等距报告日](schedule-boundaries/cross-year/index.html)、[全部10项行动分页](schedule-boundaries/all-actions/index.html)、[8条历史日期表](schedule-boundaries/long-history/index.html)、[无基线与未知验收](schedule-boundaries/no-baseline-unknown/index.html)。

每个主要目录保留全部桌面页截图和实际390px阅读截图；`notes.png`记录侧栏让出主画布。PDF已核实物理页数、尺寸和视频poster。横向图在自己的滚动区可达不等于缩小舞台文字已可读。几何、字节和映射检查不认证事实、叙事效果或真人理解。

从项目目录重新执行，使用新输出目录，复用本目录内的合成视频：

```text
python -B tools/check_presentation_browser.py --package skills/how-to-report --output verification/0.5.0/browser-rerun --video-plan verification/0.5.0/browser/video-input/plan.json
```

需要现有Playwright Chromium与pypdf；Skill运行时不依赖它们。回执中的绝对命令是当时实际执行记录，上述相对命令用于新checkout复跑。代码/样式变更后要重新构建并重新验证，不能复用旧字节的通过结果。`media-boundaries/header-only`是刻意损坏的PNG负例；签名预检通过而真实decode失败被如实记录。
