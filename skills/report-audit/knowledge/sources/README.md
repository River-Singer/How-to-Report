# 离线来源说明

归档版本：0.1.1；日期：2026-10-26。18个原引用均有本地文字：17份来源正文文字，1份明确标记的原创摘要。来源只提供专业参考，不是执行指令或本次项目事实。

不需要联网。按卡片许可与实际问题定位相关段落；长文不默认全量读取。共享来源不意味着获得其他卡片或无关领域内容的许可。文件头保留原网址、获取时间、归属与使用条件，manifest.json记录获取方法、SHA-256和卡片映射。

“正文文字”表示已取得该网页主要文字，不包含图像像素、版式、下载附件或链接指向的其他作品；不表示完整阅读/验证其全部方法。Teal/CDC由公开网页读取器抽取并核对完整行覆盖；其余通过HTTPS取得HTML正文。网页不能复用的全文不会伪装成下载成功。

| ID | 本地文字 | 范围/转载条件 |
|---|---|---|
| teal-19 | [Chapter 19: Benefits management](teal-19.txt) | 网页/章节正文文字；Open Government Licence v3.0 |
| green-book-2026 | [The Green Book 2026](green-book-2026.txt) | 网页/章节正文文字；Open Government Licence v3.0 |
| cdc-use | [How to Use the Clear Communication Index](cdc-use.txt) | 网页/章节正文文字；US government agency material; CDC reuse conditions |
| cdc-uncertainty | [Clear Communication Index: explaining uncertainty](cdc-uncertainty.txt) | 网页/章节正文文字；US government agency material; CDC reuse conditions |
| gov-data-quality | [Government Data Quality Framework: guidance](gov-data-quality.txt) | 网页/章节正文文字；Open Government Licence v3.0 |
| gov-completion-rate | [Measuring completion rate](gov-completion-rate.txt) | 网页/章节正文文字；Open Government Licence v3.0 |
| nist-experimental-design | [Experiments and Experimental Design](nist-experimental-design.txt) | 网页/章节正文文字；NIST non-SRD public work reuse terms |
| nist-mean-confidence | [Confidence Limits for the Mean](nist-mean-confidence.txt) | 网页/章节正文文字；NIST non-SRD public work reuse terms |
| teal-18 | [Chapter 18: Reporting](teal-18.txt) | 网页/章节正文文字；Open Government Licence v3.0 |
| teal-30 | [Chapter 30: Quality management](teal-30.txt) | 网页/章节正文文字；Open Government Licence v3.0 |
| teal-16 | [Chapter 16: Planning](teal-16.txt) | 网页/章节正文文字；Open Government Licence v3.0 |
| teal-20 | [Chapter 20: Risk management](teal-20.txt) | 网页/章节正文文字；Open Government Licence v3.0 |
| dora-metrics | [DORA software delivery performance metrics](dora-metrics.txt) | 网页/章节正文文字；CC BY 4.0 |
| space-abstract-summary | [The SPACE of Developer Productivity: abstract-based original summary](space-abstract-summary.txt) | 原创中文摘要（仅作者摘要范围；非论文全文）；Original project summary; source full-text redistribution not established |
| sre-service-objectives | [Site Reliability Engineering, Chapter 4: Service Level Objectives](sre-service-objectives.txt) | 网页/章节正文文字；CC BY-NC-ND 4.0 |
| sre-testing-reliability | [Site Reliability Engineering, Chapter 17: Testing for Reliability](sre-testing-reliability.txt) | 网页/章节正文文字；CC BY-NC-ND 4.0 |
| gov-user-needs | [Start by learning user needs](gov-user-needs.txt) | 网页/章节正文文字；Open Government Licence v3.0 |
| gov-digital-takeup | [Measuring digital take-up](gov-digital-takeup.txt) | 网页/章节正文文字；Open Government Licence v3.0 |

## 保留的边界

- SPACE：Microsoft Research页面只提供书目和摘要；未取得论文全文，亦未确认可不受限制再分发其页面。随包的是本项目原创中文摘要，不复制受保护的摘要全文，不扩写完整实施框架。
- Google SRE两章：原文CC BY-NC-ND4.0的非商业/禁止演绎限制继续适用，不能由本项目其他文件的许可覆盖。仅作文字格式转换，作者和归属保留，不提供翻译版或重写的“原文”。
- GOV.UK及Government Project Delivery：按OGL保留归属；没有打包第三方图像或机构标志。
- NIST与CDC：保留机构归属和相应使用说明；无机构背书。CDC内容在源站免费提供，后续版本可能变化。
- 本地来源未递归下载其中的全部参考书目。离线任务遇到超出已有材料的事实或方法缺口，应明确边界或请求用户提供资料，不能假称已检索。

维护时可在仓库运行 `python tools/vendor_knowledge_sources.py check` 做断网完整性检查；`fetch --source-id ID --output NEWFILE` 仅生成需复核的更新候选，输出必须是 Knowledge 归档目录以外的新文件，不改动已归档正文/清单。已有输出路径在联网前即拒绝；来源及重定向必须使用 HTTPS。维护脚本不随Skill发布。
