# Knowledge 离线来源归档：0.2.1

日期：2026-10-26。落实用户要求：Skill 使用者可能没有联网或搜索能力，当前 Knowledge 的外部引用须有随包可读文字。范围为当前 12 张卡及目录实际引用的 18 个独立来源，不是历史研究索引中的 171 个链接，也不递归归档这些文章的全部参考文献。

## 实际交付与范围

`project/skill-src/shared/knowledge/sources/` 已保存 18 份 UTF-8 纯文本、一个清单和离线说明。总计 535,833 字节的来源文字文件；17 份 `source_text`，0 份 `partial_source_text`，1 份 `original_summary`。这里的 source_text 指所引用网页的可读主要文字，明确不含图像像素、版式、附件和另行链接的作品，也不声称已在语义上研读/验证整本材料的全部方法。

每份来源文件保留出处、日期、来源类型、范围、归属、复用限制和不可信参考材料边界。清单额外记录获取方法、正文选择器或完整行覆盖、SHA-256、卡片映射。18 个原网址均保留为溯源信息；12 张卡和目录只链接本地来源。目录保持元信息功能，正文仍由原卡片许可控制，共享一篇来源不授权读取其他卡片或无关领域内容。

| 来源 ID / 本地文件名 | 卡片 | 获取方式 | 可用文字范围 / 复用依据 |
|---|---|---|---|
| teal-19.txt | BUS-01、FIN-01 | 公开网页读取器；窗口按行合并 | Chapter 19 Benefits management；OGL 3.0 |
| green-book-2026.txt | BUS-02、FIN-02 | HTTPS HTML；gem-c-govspeak | Green Book 2026 网页正文；OGL 3.0 |
| cdc-use.txt | COM-01 | 公开网页读取器；完整行覆盖 | How to Use the Clear Communication Index；CDC 政府材料条款 |
| cdc-uncertainty.txt | COM-01 | 公开网页读取器；完整行覆盖 | Clear Communication Index item 11；CDC 政府材料条款 |
| gov-data-quality.txt | DATA-01 | HTTPS HTML；gem-c-govspeak | Government Data Quality Framework guidance；OGL 3.0 |
| gov-completion-rate.txt | DATA-01 | HTTPS HTML；gem-c-govspeak | Measuring completion rate；OGL 3.0 |
| nist-experimental-design.txt | DATA-02 | HTTPS HTML；body | Experiments and Experimental Design；NIST non-SRD 复用条款 |
| nist-mean-confidence.txt | DATA-02 | HTTPS HTML；body | Confidence Limits for the Mean；NIST non-SRD 复用条款 |
| teal-18.txt | PM-01 | 公开网页读取器；完整行覆盖 | Chapter 18 Reporting；OGL 3.0 |
| teal-30.txt | PM-01 | 公开网页读取器；完整行覆盖 | Chapter 30 Quality management；OGL 3.0 |
| teal-16.txt | PM-02 | 公开网页读取器；窗口按行合并 | Chapter 16 Planning；OGL 3.0 |
| teal-20.txt | PM-02 | 公开网页读取器；窗口按行合并 | Chapter 20 Risk management；OGL 3.0 |
| dora-metrics.txt | SWE-01 | HTTPS HTML；guides-article | DORA software delivery performance metrics；CC BY 4.0 |
| space-abstract-summary.txt | SWE-01 | 已读取作者机构摘要/书目页后原创整理 | **只提供有限原创中文摘要；未归档论文全文** |
| sre-service-objectives.txt | SWE-02 | HTTPS HTML；id=content | SRE Chapter 4；**CC BY-NC-ND 4.0** |
| sre-testing-reliability.txt | SWE-02 | HTTPS HTML；id=content | SRE Chapter 17；**CC BY-NC-ND 4.0** |
| gov-user-needs.txt | MKT-01 | HTTPS HTML；gem-c-govspeak | Start by learning user needs；OGL 3.0 |
| gov-digital-takeup.txt | MKT-01 | HTTPS HTML；gem-c-govspeak | Measuring digital take-up；OGL 3.0 |

所有精确原网址、正文 SHA-256 和来源级日期见 `project/skill-src/shared/knowledge/sources/manifest.json`，避免在两处手工维护同一份机器清单。

## 获取核对与例外

- 10 份正文直接经 HTTPS 获取，选择明确正文节点，保留文字顺序；删除网页导航、脚本、表单和布局代码。每次获取记录响应字节数/哈希、最终 URL、UTC 和正文选择器。不下载或执行源站脚本。
- 5 份 Teal 页面直接 HTTP 返回 403；没有登录或绕过访问控制，改用可访问的公开网页读取器。2 份 CDC 页面也采用公开读取器。读取器第一次返回的窗口没有冒充完整文档：Teal 16/19/20 补取缺失头部，与其余窗口按原行号合并，核对重叠一致、总行覆盖无缺口，再裁出章节正文。7 份分别覆盖读取器总行数 Teal 18=325、30=254、16=349、20=416、19=369，CDC use=106、uncertainty=85。原窗口保存在本 research 目录的 `offline-source-captures/`，不随 Skill 发布。
- SPACE 是唯一没有原文全文的来源。Microsoft Research 页面仅支持作者摘要和书目范围，未确认完整页面/论文的无条件再分发许可。随包文件是本项目原创中文摘要，没有逐字复制摘要全文，也不凭摘要发明五维框架的完整实施步骤、定义、阈值或效果量。Skill 可据此完成已声明的边界审查；超出范围需用户提供材料，运行时没有联网补齐前提。
- Google SRE 两章保留原有非商业、禁止演绎条款和作者/机构归属，只做文字格式转换；不能把它们视为本项目可任意商业再分发的原创内容。不得把格式转换或摘取章节误说成获得无条件再许可。
- 已归档的 OGL/CC/政府材料均保留归属和相应限制；未捆绑机构徽标或第三方图像。原文可能未来更新，因此保留日期与哈希。

已核查的复用依据：

- Government Project Delivery [Crown copyright](https://projectdelivery.gov.uk/crown-copyright/) 与 [OGL 3.0](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/)。GOV.UK 原页面页脚同样声明 OGL，并保留第三方例外。
- [CDC agency materials](https://www.cdc.gov/other/agencymaterials.html)：政府文字一般可复用，保留归属、非背书、免费原站和内容更新说明，排除第三方材料。
- [NIST reuse statement](https://www.nist.gov/open/copyright-fair-use-and-licensing-statements-srd-software-and-technical-series-publications)：非 SRD 的 NIST 员工政府作品在美国不受版权保护，页面同时给出海外复用许可与 AS IS 等条件。
- DORA 来源页页脚声明 Google LLC / [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)；SRE 来源页声明 Google / O'Reilly / [CC BY-NC-ND 4.0](https://creativecommons.org/licenses/by-nc-nd/4.0/)。随包保留对应通知。
- [Microsoft terms](https://www.microsoft.com/en-us/legal/terms-of-use) 不提供这里所需的无条件全文再分发许可，因此明确使用原创摘要例外。

## 运行与维护边界

两个 SKILL 入口及宿主能力说明已明确：核心方法、卡片和来源文字均在包内；原网址只作溯源；按授权卡片读取相关段落，不默认灌入整本长文。用户项目证据缺失仍然是事实缺口，需要询问或接受用户资料，不能假称下载或检索过。

维护脚本 `project/tools/vendor_knowledge_sources.py` 使用 Python 3.10+ 标准库，不进入运行 Skill 包，不依赖第三方库。实际 CLI：

```text
python tools/vendor_knowledge_sources.py check
python tools/vendor_knowledge_sources.py check --root PATH_TO_KNOWLEDGE
python tools/vendor_knowledge_sources.py fetch --source-id SOURCE_ID --output NEW_CANDIDATE_FILE
python tools/vendor_knowledge_sources.py fetch --root PATH_TO_KNOWLEDGE --source-id SOURCE_ID --output NEW_CANDIDATE_FILE
```

以上从 `project/` 运行。`check` 完全离线，核对正文存量/路径、哈希、UTF-8、来源与许可元信息、卡片映射、本地链接和未注册文本。`fetch` 只支持已登记的直接 HTTPS HTML 来源，独占创建更新候选文件，不更新正文或清单；读取器来源及原创摘要禁止自动替换为全文。刷新后需维护者复核正文范围、许可和卡片结论，再明确更新来源及哈希。维护下载能力不变成运行时联网授权。

包版本设为 0.2.1；Knowledge 目录/卡片/归档版本 0.1.1；Run contract 仍为 0.1。未修改冻结的 0.2.0 试跑包。

## 验证与交接

- `python tools/vendor_knowledge_sources.py check`：valid=true，network_used=false。
- `python -X utf8 -m unittest discover -s tests -v`：48 项通过。其中新增 9 项验证真实归档在网络被禁止时可检查、损坏/缺失/未登记来源可被检测、卡片远程链接和映射丢失可被检测、路径越界/重复身份可被拒绝、摘要不被抓取成全文、正文选择器不会默默拿错区域。打包测试只使用临时目录。
- Python 3.10 AST grammar：来源脚本、新测试及版本涉及的两个 Python 文件通过。
- 来源文字无网页读取器的 `L123:` 行号、工具引用标记或工具输出封套残留。
- 本工作者未运行正式 build。由主任务统一构建 0.2.1、执行生成物与可搬迁离线包验证；冻结的 0.2.0 历史测评继续保留。
