# 私有、已确认画像的显式操作

仅在用户启用画像、明确指定私有位置并实际确认长期条目时使用。画像与安装包、Run、Agent Memory 分离；当前用户要求优先，不把一次性选择或模型推测写成长期事实。旧版宿主文件手动保存/修正路径仍可用；此工具提供同一 0.1 契约的可复核快照。

```text
python <installed-how-to-report>/scripts/report_profile.py init <new-private.json> --profile-id <id>
python <installed-how-to-report>/scripts/report_profile.py inspect <private.json>
python <installed-how-to-report>/scripts/report_profile.py inspect <private.json> --show-values
python <installed-how-to-report>/scripts/report_profile.py revise <private.json> --entry <confirmed-entry.json> --expected-sha256 <inspection-hash> --output <new-private-revision.json>
```

Python 3.10+ 标准库、离线、支持独立搬迁和 `-I`。init 创建空画像，不假造确认或偏好。inspect 默认只显示 profile ID、指纹、历史数量及当前条目 id/revision/type；用户明确查看正文时使用 `--show-values`，此时包含 value、scope、confirmation_ref。查看不写文件、不读其他画像、不自动决定全局最新快照。

revise 的 entry 文件精确包含 `id, type, value, scope, confirmation_ref`，全部非空；type 仅 `preference | experience`。示例见[合成条目](../assets/report-profile/confirmed-entry.json)，不可把其假设确认用于真人画像。`confirmation_ref` 指向本次实际用户确认消息/记录，工具只检查非空，**不能认证该消息存在、用户同意或内容属实**，宿主执行者须核对。对未确认/否定诉求不调用写入。

新条目 revision 从 1 开始；修订同 ID 自动加 1，保持原类型，保留旧条目的完整历史。工具要求输入画像的真实当前字节指纹；不符失败。该指纹只绑定显式选择的快照，不证明它是其他会话的最新决定。输出为新的不可覆盖文件，旧画像保持原字节，新文件的 `parent_snapshot_sha256` 标明前一个快照；交付明确指出本次采用哪份新快照。没有后台观察、自动跨任务更新、并发合并或原位替换。

用户修改请求到来时：先查看指定快照，找相关已确认条目；把修订值及适用范围与当前指令对齐；经已有会话确认后写新快照并返回真实位置；后续只引用所用条目版本，不将完整画像复制到 Run。临时不同要求直接在本次生效，无需为了覆盖旧偏好写永久修订。

文件必须在安装包和 Run 外，父目录已存在；拒绝 UNC/device、链接/reparse、已有输出及具有 run.json/SKILL.md/bundle-manifest.json 的祖先目录。路径检查不能替代操作系统访问权限或保密设置，不会加密、上传、共享或设置全局配置。最大 1 MiB、1000 条含历史条目；历史修订必须连续，类型/结构错误退出 2，不刷新指纹。I/O 失败保留可能的部分新文件并换新路径重试。退出 0 只表示结构/本次文件操作成功，不证明画像真实或适用。

无 Python 时按[工作区契约](workspace-contract.md)使用宿主文件工具在明确私有位置保存、查看与修正；保持旧版本、实际确认来源和当前要求优先，自动校核未运行需披露。无法持久保存时只交付可复制条目，不声称下次已记住。
