# 离线 Knowledge 资料

离线资料自包0.2.1提供，当前0.4.0沿用相同内容。12张知识卡、目录和来源归档版本为0.1.1；卡片指向包内文字，原网址只用于来源核对和日后维护。

当前知识卡直接引用的18个来源均有本地文字表示：17份为对应网页的主要可读正文，1份为明确标记的原创摘要。来源文字合计535,833字节；不含图片像素、网页布局、附件，也不递归收集文章引用的其他作品。归档完成不代表已经研究或验证每份材料的全部方法。

- [知识卡目录](../skills/how-to-report/knowledge/index.md)
- [本地来源说明](../skills/how-to-report/knowledge/sources/README.md)
- [来源清单与校验值](../skills/how-to-report/knowledge/sources/manifest.json)
- [逐项获取、许可与范围记录](research/offline-knowledge-sources.md)

SPACE是明确例外：本地文件是基于已读取作者摘要的原创中文整理，没有取得或复制论文全文，不提供仅凭摘要无法支持的完整实施框架。Google SRE两章保留CC BY-NC-ND 4.0许可与归属；其他来源也保留各自适用通知。原资料可在对应本地文字文件中阅读。

两个独立包各自含有完整的本地来源副本，不依赖另一个Skill或开发仓库。按授权卡片读取与当前问题有关的来源段落；共享一个来源不意味着自动获准读取其他领域卡。缺少用户项目证据时，保留缺口或请求用户提供材料，不依赖搜索补齐，也不能把通用文献当成业务事实。

## 维护与检查

以下命令供开发维护使用，不是运行Skill的前提。在project目录内，离线检查为：

```text
python tools/vendor_knowledge_sources.py check
python tools/vendor_knowledge_sources.py check --root <独立安装包的knowledge目录>
```

检查读取本地清单、文字和引用，不联网。它验证完整性与声明的一致性，不认证原文的全部含义或方法的实际效果。

需要更新可直接下载的来源时，维护者可显式运行：

```text
python tools/vendor_knowledge_sources.py fetch --source-id <来源ID> --output <新的候选文件>
```

此命令需要联网且只产生新候选，不能覆盖已归档资料；公开读取器取得的正文和原创摘要不能靠此命令自动重建。候选须核对许可、正文范围和内容后，再更新版本与清单、重建两包。不要把重新下载等同于完成研究。
