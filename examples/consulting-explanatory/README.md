# 咨询结构样例：21种

打开[离线索引](index.html)按预览选结构；[catalog.json](catalog.json)逐项列出栅格、关系、读序、场景、容量、限制和来源。每种结构都有authors、slots、docs和previews。

这是**独立样例目录**，未注册为`library query`资产。所有文字、数值为原创合成；私有源PDF、真实业务材料、截图、品牌和原题不发布。公开作者移除私有来源metadata后重新计算SHA，catalog保留预览与原作者可见内容的关系；旧本地build receipt没有复制过来。

## 正常重放

从本目录运行：

```powershell
python instantiate.py --template team-profiles --output instance.json
```

从project根目录运行（输出路径必须不存在）：

```powershell
python skills/how-to-report/scripts/report_engine.py validate --input examples/consulting-explanatory/instance.json
python skills/how-to-report/scripts/report_engine.py build --input examples/consulting-explanatory/instance.json --output C:/Temp/example-build --pptx C:/Temp/example.pptx --geometry-policy computed
```

`instantiate.py --values values.json`支持text、charts、images三个映射；具体ID见slots。图表值须满足已注册图表合同，图片需在构建时用`--assets`提供素材根目录。增减结构应编辑语义children/nodes/edges，并重算，不能补写final frame。正文14pt、最小9pt；使用全局palette，不逐对象手改。

解释、比较、判断数据用图；仅查阅或核对精确记录用表；混合任务各司其职。这里只展示方法与默认实例：没有任意文字自动跨栏续排、自动分页或任意PDF保真还原保证。图位是明确矩形占位，待用户绑定真实证据。所有重新构建都应实际查看渲染结果。

## 已执行的工程检查

当前公开作者已全部通过正常validate；代表性迁移作者从无关临时工作目录正常computed构建。具体范围和新author哈希见[verification-summary.json](verification-summary.json)。未把本地旧来源metadata的receipt冒充公开输入验收。
