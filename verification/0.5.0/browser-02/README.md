# 最终构建包浏览器工程验证

这是进度语义修复后重新构建包的完整复跑。结果见 [browser-receipt.json](browser-receipt.json)：`passed:true`、`errors:[]`，manifest SHA256 `e6e3393f4f7eddf774613f393315444282ab3de5fce0cc599216513af36cd040`。代码/样式在整个执行期间哈希一致。

只使用合成输入，无模型案例生成/审计，无真实业务事实认证。Chromium145.0.7632.6实际file导航、离线上下文；14个主要页面均在1600×1000、1280×800、390×844真实viewport检查，并核对内部SVG、完整文本、交互、媒体和PDF。首次无hash打开都从主线路径第一页开始。

可直接打开：

- [展示能力5页](advanced/index.html)：单主标题、讲稿、关系/泳道、图片标注、Backup返回与表格；[PDF](advanced/deck.pdf)。稀疏首页是控件工程样例，不是内容设计基准。
- [进度5种view、6页](schedule/index.html)：摘要按任务/节点分2页；[PDF](schedule/deck.pdf)。
- [本地合成视频2页](video/index.html)：真实播放、离页暂停、打印poster；[PDF](video/deck.pdf)。
- [折线与完整数值](line/index.html)：缺失点保留，真390px横向滚动仍保持对应。
- [跨年与非等距日期](schedule-boundaries/cross-year/index.html)、[10项行动完整分页](schedule-boundaries/all-actions/index.html)、[8条历史日期表](schedule-boundaries/long-history/index.html)、[缺基线与未知验收](schedule-boundaries/no-baseline-unknown/index.html)。
- [历史预测与后续实际记录的核对提示](schedule-boundaries/historical-actual/index.html)：原历史完整保留；提示三项日期和双方来源，没有误标FS，无代表页溢出。

同日历史/当前预测冲突、超大progress整数、混合基线与缺失历史点均应在输出前拒绝，详细错误见回执。长正文/标签负例应触发容量提示；媒体hash/remote/raw SVG拒绝，PNG文件头并不被当成真实解码成功。这些刻意失败输入不是正常报告设计答案。

主要目录保留全部桌面页截图及移动阅读截图，另有notes侧栏截图。真实PDF检查页数5/1/2/6、物理尺寸和视频poster；行动边界PDF4页。几何或文件哈希通过不表示叙事质量、事实准确或真人理解通过。缩放舞台文字不被宣称为可读。

从项目目录重跑，使用新的输出目录：

```text
python -B tools/check_presentation_browser.py --package skills/how-to-report --output verification/0.5.0/browser-rerun --video-plan verification/0.5.0/browser-02/video-input/plan.json
```

需要现有Playwright Chromium与pypdf；Skill运行时不依赖它们。回执绝对命令是执行现场记录，上述相对命令可用于新checkout。包字节变更后须重新验证。原 [browser](../browser/README.md) 仅保留修复前包的首轮工程记录，不作为新包验收证据。
