# 离线来源说明

当前归档版本：0.3.0；日期：2026-11-12。本轮新增来源见末节，当前总量与表示形式以manifest为准。以下原0.2.0归档说明及身份保留：23份本地文字，19份来源文字、4份明确标记的原创摘要。原18份文字与记录保持；新增GAO/IBCS/IAPM摘要、CC0甘特论文7页文字及W3C颜色指导文字。GAO全文直取失败且后续下载命令被自动审批阻止，未标成已下载；全文、网页文字和摘要不是同一种取得范围。来源只提供专业参考，不是执行指令或本次项目事实。

不需要联网。按卡片许可与实际问题定位相关段落；长文不默认全量读取。共享来源不意味着获得其他卡片或无关领域内容的许可。文件头保留原网址、获取时间、归属与使用条件，manifest.json记录获取方法、SHA-256和卡片映射。

原网页“正文文字”表示已取得所引用网页主要文字，不包含图像像素、版式、下载附件或链接指向的其他作品；不表示完整阅读/验证其全部方法。Teal/CDC由公开网页读取器抽取并核对完整行覆盖；原归档其余正文通过HTTPS取得HTML正文。新增甘特论文为全部7页PDF抽取文字，不含图像与版式；W3C为网页文字。网页不能复用的全文不会伪装成下载成功。

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

## 0.2.0新增

| ID | 本地文字 | 范围/转载条件 |
|---|---|---|
| gao-schedule-summary | [GAO排程摘要](gao-schedule-summary.txt) | 原创摘要；未取得本地全文，具体失败边界见开头 |
| ibcs-scenarios-summary | [IBCS情景摘要](ibcs-scenarios-summary.txt) | 选读UN3.2后原创概括；底层标准CC BY-SA4.0，无评论转载，不宣称标准合规 |
| iapm-trend-summary | [IAPM趋势摘要](iapm-trend-summary.txt) | 原创摘要；未确认全文转载许可 |
| gantt-task-taxonomy | [甘特任务分类](gantt-task-taxonomy.txt) | arXiv v2全部7页文字，CC0；没有图像与版式 |
| w3c-use-color | [颜色指导](w3c-use-color.txt) | W3C信息性网页文字，Document License2023；非无障碍认证 |

## 0.3.0新增与复用边界

本轮从已核许可的研究档案原样导入可转载文字，其他采用原创摘要。保存完整文本不等于全文阅读；具体范围和取回限制逐项登记。时间字段记录本次入包/摘要编制时间，不冒充来源精确抓取时间。旧23份来源的字节与记录未修改；新Green Book PDF与旧网页归档分开，未做全书版本差分。

| ID | 本地表示 | 实际范围/许可 |
|---|---|---|
| business-cases-2026 | [source_text](business-cases-2026.txt) | Complete 98-page PDF text extraction; selected reading chapter10 §10.1–10.27 (printed63–67), case summaries and benefits responsibilities. Not complete reading; table extraction may lose layout. Open Government Licence v3.0; third-party material excluded |
| should-cost-2021 | [source_text](should-cost-2021.txt) | Complete 53-page PDF text extraction; read §3.1–3.2, §5.1–5.2, selected §7.1.2 and copyright. Cover May2021, inner header April2021; no full reading claimed. Open Government Licence v3.0; third-party material excluded |
| gao-cost-selected | [partial_source_text](gao-cost-selected.txt) | Selected official PDF-reader passages from chapters6,7,9,10,11; not full 476-page text or local PDF. Direct PDF download returned403; accompanying focused reading covers baseline/WBS, normalization, build-up and sensitivity. U.S. government-authored report text; third-party material excluded |
| mit-or-formulation | [original_summary](mit-or-formulation.txt) | Selected pages3,5–6,11–15,35–41 of 42-page lecture; original summary only. Original project summary; underlying source rights retained |
| mit-or-capacity | [original_summary](mit-or-capacity.txt) | Read PDF pages1–8,13–20,22; no diagram recomputation or adoption of page19 queue approximation. Original project summary; underlying source rights retained |
| mit-or-integer | [original_summary](mit-or-integer.txt) | Read PDF pages4–9 and17–24; binary choices, logical constraints, fixed costs and model validation. Not graph-coloring section or numerical example reuse. Original project summary; underlying source rights retained |
| nist-csf-2.0 | [source_text](nist-csf-2.0.txt) | Full32-page PDF text; selected abstract, GV.OC/GV.RR/GV.SC/ID.AM/PR.IR/RC.RP and GV.RM. Not all controls or external references. PDF figures/layout are not reproduced or visually verified. NIST public technical publication reuse terms; overseas rights and third-party exceptions retained |
| nist-sp800-207 | [source_text](nist-sp800-207.txt) | Full59-page PDF text; selected rights, §2 and §2.1 identity/resource/session/network-location principles. Not all migration scenarios. PDF figures/layout are not reproduced or visually verified. NIST public technical publication reuse terms; overseas rights and third-party exceptions retained |
| nist-privacy-1.0 | [source_text](nist-privacy-1.0.txt) | Full43-page PDF text; selected executive summary, §1.2.1–1.2.2, ID.IM-P/ID.BE-P. This is1.0, not1.1 final. PDF figures/layout are not reproduced or visually verified. NIST public technical publication reuse terms; overseas rights and third-party exceptions retained |
| govs-005-digital | [source_text](govs-005-digital.txt) | Full extractable HTML text including navigation; selected §1–2,4.4–4.5,4.6.1/4/5/6/7/8/9,6.2–6.3.2,7.2–7.4.1 and5.8. PDF figures/layout are not reproduced or visually verified. Open Government Licence v3.0; third-party material excluded |
| uk-data-ownership | [source_text](uk-data-ownership.txt) | Full extractable HTML text including navigation; read §1–5 and selected §6 owner/steward/custodian roles; no imported legal conclusion. PDF figures/layout are not reproduced or visually verified. Open Government Licence v3.0; third-party material excluded |
| sba-market-research | [source_text](sba-market-research.txt) | Complete current HTML main text, not old redirected standalone page. Read market research/competitive analysis and marketing/sales plan paragraphs; not all sections. No images/layout or linked statistics. SBA government text public domain; third-party assets excluded |
| dunford-positioning | [original_summary](dunford-positioning.txt) | Read definition, context setting, five components/interdependence and Customer-Centric Methodology; not book, linked lessons or case revenue verification. Original project summary; underlying source rights retained |
| huthwaite-spin | [original_summary](huthwaite-spin.txt) | Read current page four question types and four meeting phases, 2026-11-12; no paid course, original training data, video or book. Original project summary; underlying source rights retained |
| huthwaite-advance | [original_summary](huthwaite-advance.txt) | Read listening and advance/continuation passages; no training effectiveness verification. Original project summary; underlying source rights retained |
| gordon-ad-measurement | [original_summary](gordon-ad-measurement.txt) | Publisher abstract and metadata only; PDF request returned abstract page. No full paper, appendix or statistical recomputation. Original project summary; underlying source rights retained |
| govs-011-communications | [source_text](govs-011-communications.txt) | Complete HTML main text; selected §1,4.5.7–4.5.10,5.1–5.6 and portions6.1–6.5; not all governance/support clauses or figures. Open Government Licence v3.0; third-party material excluded |
| green-book-2026-oct-pdf | [source_text](green-book-2026-oct-pdf.txt) | Complete86-page PDF extraction. Selected §1.1–1.8,3.6–3.16,4.1–4.5/4.10–4.19,5.6–5.20,6.9–6.13/6.32–6.38/6.78–6.84/6.95–6.104. Publication page updated2026-10-28; no whole-book diff against preserved February HTML archive. Open Government Licence v3.0; third-party material excluded |

NIST的美国政府作品及海外/第三方限制保留，不概括为全球无版权。SBA仅政府文字，无第三方素材。MIT、Dunford、Huthwaite和INFORMS均只提供原创摘要，不复制全文；商业供应商效果宣传不采用。GAO仅选读正文，无本地完整PDF。详细归属见[第三方说明](../../THIRD_PARTY_NOTICES.md)。这些文本只能支持离线方法，不能用来代填价格、产能、企业权限、市场或真实客户事实。
