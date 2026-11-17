# README截图

三张截图来自0.11.6正式生成包导出的实际离线Storybook界面，通过浏览器正常输入、筛选和全局配色控件取得。设计组合/图表视口1600×1100，色卡视口1600×1400以完整展示六项。没有修改DOM、拼贴PPT或处理图片来模拟产品功能。

| 截图 | 实际操作与内容 |
|---|---|
| `storybook-designed-compositions.png` | 搜索`designed-composition`，显示3个正常可调用的成稿设计组合 |
| `storybook-charts.png` | 按数据图表筛选，预览采用合成数据 |
| `storybook-palettes.png` | 按全局色卡筛选，显示6套注册色卡；顶部保持`report-default`，第六套为可选 |

本地目录导入了6份原生PPT素材，界面所示39,305总项、685页等数字属于该目录快照，并非公开仓库内置原始文件的数量。截图不包含业务报告、原PDF、私有文件路径或真实业务截图。详情页可能显示本机CLI位置，故未用作公开截图。

图片是捕获时的真实UI状态。选择palette只更新请求；静态预览不会自动实时重绘。实际查看状态、文件SHA与生成包manifest SHA记录在`storybook-screenshots.json`。实际输入与边界见项目的Storybook文档。
