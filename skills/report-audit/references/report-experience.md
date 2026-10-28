# 显式私有经验：保存、检索和修正

仅在用户要求保存或使用经验、且范围明确时操作。当前任务材料和要求优先；历史成功不证明当前适用。三层分开：已确认个人偏好/经历继续用生成侧已有画像能力；任务案例记录具体场景、做法和观察；方法修订候选记录待验证建议。不能因一次喜欢、一次获奖或模型自评就修改核心 Skill。

使用本包 [经验助手](../scripts/report_experience.py)，无需联网。存储文件及变更请求都放安装包和Run以外的私有位置，不进入公开Git。工具只检查结构与声明，不鉴别用户确认、源资料真实性或实际收益。

```text
python <本Skill>/scripts/report_experience.py init <新的私有json路径> --store-id report-cases
python <本Skill>/scripts/report_experience.py inspect <私有json路径>
python <本Skill>/scripts/report_experience.py inspect <私有json路径> --show-values
python <本Skill>/scripts/report_experience.py search <私有json路径> --query "资源协调" --tag delay --show-values
python <本Skill>/scripts/report_experience.py revise <旧json> --entry <私有变更请求json> --expected-sha256 <inspect所得sha256> --output <新的私有json>
```

请求格式见[合成条目](../assets/examples/experience-entry.json)：`id/kind/status/context/question/action/observations/mechanism_hypothesis/applicability/exclusions/tags/source_refs/confirmation_ref`。`kind`只能是`task_case|method_candidate`；`status`是`active|withdrawn`。同ID修订自动追加连续revision，旧快照不变，类型不变；另建方法候选时引用原案例的精确ID/版本及位置。撤回用新revision的withdrawn状态保留历史；检索默认排除，可用`--include-withdrawn`查看。不能重用旧结论覆盖原证据。

观察必须明确`observed`或`not_observed`；真实观察带已列入条目的精确来源引用，未观察写明缺口，不能用“效果显著”占位。`source_refs`要求ID、正整数revision和locator；它们是外部资料/案例的定位声明，不是自动打开/核验文件。机制仍标候选；适用与不适用条件都要写。若用户仅确认偏好，不强迫其提供任务效果；使用画像而非伪造案例。

`search`只在指定快照做字面子串及精确标签/类型筛选，不是embedding、语义排名、自动跨任务收集或全盘搜索。默认输出ID/版本/类型/状态和哈希，不显示内容；`--show-values`才显示。调用前仍需真实授权，参数不能认证授权。读到历史案例后先比较当前问题、条件和证据；不适用则弃用，可借检验问题而不能照搬答案。

当一次反馈值得研究时，可显式保存候选，写明还需哪些场景/反例观察。候选不会成为核心规则；需要后续开发和用户案例验证。无新增反馈不自动写记录。输出只能说明保存/检索了什么、采用或舍弃的理由及当前未知，不能声称已学习出普适规律。
