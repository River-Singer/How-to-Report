"""Escaped, deterministic time graphics with complete date/text alternatives."""
from __future__ import annotations

from datetime import timedelta
from html import escape
import json

from schedule_core import day, delta, finish, validate_component, warnings


def render_component(element, language, source_ref=None):
    validate_component(element, set())
    cfg = element["schedule"]; spec = cfg["spec"]; view = cfg["view"]; eid = element["id"]
    zh = language == "zh-CN"
    e = lambda value: escape(str(value), quote=True)
    states = {"not_started": "未开始", "active": "进行中", "blocked": "受阻", "done": "已完成"} if zh else {k: k.replace("_", " ") for k in ("not_started", "active", "blocked", "done")}
    acceptance = {"not_submitted": "未提交", "pending": "待审核", "accepted": "已接受", "rejected": "未通过", "unknown": "记录缺失 / 待核"} if zh else {"not_submitted": "not submitted", "pending": "pending review", "accepted": "accepted", "rejected": "rejected", "unknown": "unknown / no record"}
    unknown = "未知" if zh else "Unknown"
    refs_used, mappings = [], []

    def reference_marks(refs):
        if source_ref is not None:
            return source_ref(refs)
        marks = []
        for ref in refs:
            if ref not in refs_used: refs_used.append(ref)
            marks.append(str(refs_used.index(ref) + 1))
        return '<sup class="schedule-source">[' + ",".join(marks) + ']</sup>' if marks else ""

    def attrs(key, value, refs):
        identity = eid + "-" + key
        selector = "#schedule-" + identity
        mappings.append({"element_id": eid, "datum_id": identity, "selector": selector, "refs": refs,
                         "displayed": value})
        return f'id="schedule-{e(identity)}" data-datum-id="{e(identity)}" data-refs="{e(json.dumps(refs, ensure_ascii=False))}"'

    def deviation(value):
        return unknown if value is None else (f"{value:+d} " + ("自然日" if zh else "days"))

    def dates_text(task):
        parts = []
        for key, label in (("baseline", "基线" if zh else "Baseline"), ("actual", "实际" if zh else "Actual"), ("forecast", "预测" if zh else "Forecast")):
            value = task.get(key, {})
            parts.append(f'{label}: {value.get("start", unknown)} → {value.get("finish", unknown)}')
        return " · ".join(parts)

    def time_domain():
        # Every page of the same spec uses the same domain, not a separately guessed range.
        values = [day(spec["as_of"]), day(spec["as_of"]) + timedelta(days=1)]
        for task in spec["tasks"]:
            for key in ("baseline", "actual", "forecast"):
                values.extend(day(v) for v in task.get(key, {}).values())
        for mark in spec.get("milestones", []):
            values.extend(day(mark[k]) for k in ("baseline_date", "actual_date", "forecast_date") if k in mark)
        start, end = min(values), max(values) + timedelta(days=1)
        span = max(1, (end - start).days)
        return start, end, lambda d: 20 + (d - start).days / span * 760

    start, end, x = time_domain()
    ticks = [start + timedelta(days=round((end-start).days*n/4)) for n in range(5)]
    axis = '<svg viewBox="0 0 800 35" preserveAspectRatio="none" aria-hidden="true">' + ''.join(
        f'<text x="{x(t):.4f}" y="22" text-anchor="{"start" if n == 0 else "end" if n == 4 else "middle"}">{t.isoformat()}</text>' for n, t in enumerate(ticks)) + '</svg>'
    status_x = x(day(spec["as_of"]) + timedelta(days=1))

    def interval_svg(task):
        parts = [f'<line class="schedule-status-line" x1="{status_x:.4f}" x2="{status_x:.4f}" y1="0" y2="46"/>']
        for key, y, height in (("baseline", 7, 4), ("actual", 20, 12), ("forecast", 34, 8)):
            dates = task.get(key, {})
            first, last = dates.get("start"), dates.get("finish")
            if key == "actual" and first and not last: last = spec["as_of"]
            if key == "forecast" and not first and task.get("actual", {}).get("start") and last:
                first = (day(spec["as_of"]) + timedelta(days=1)).isoformat()
            if first and last:
                left, right = x(day(first)), x(day(last) + timedelta(days=1))
                parts.append(f'<rect class="schedule-{key}" x="{left:.4f}" y="{y}" width="{max(0,right-left):.4f}" height="{height}"/>')
            elif first or last:
                pos = x(day(first or last))
                parts.append(f'<circle class="schedule-{key}" cx="{pos:.4f}" cy="{y+height/2}" r="4"/>')
        return '<svg class="schedule-time-plot" viewBox="0 0 800 48" preserveAspectRatio="none" role="img" aria-label="' + e(dates_text(task)) + '">' + ''.join(parts) + '</svg>'

    content = []
    context = f'{"状态日" if zh else "As of"}: {spec["as_of"]} · {"自然日，日终边界" if zh else "Natural days; end-of-day boundary"}'
    if spec.get("baseline"):
        b = spec["baseline"]; context += f' · {"批准基线" if zh else "Approved baseline"}: {b["id"]}@{b["revision"]}'
        context += reference_marks(b["refs"])
    else:
        context += ' · ' + ("无批准基线；仅呈现现状，不判断延期" if zh else "No approved baseline; current schedule only, no lateness conclusion")
    content.append('<p class="schedule-context">' + context + '</p>')
    notices = warnings(spec)
    if any(w["code"] == "same_day_fs_order_unknown" for w in notices):
        content.append('<p class="schedule-note" data-warning-code="same_day_fs_order_unknown">' + ('存在同日FS交接：日级记录不能确定日内先后，依赖关系尚需时间记录核实。' if zh else 'Same-day FS handoffs exist: dates alone do not establish within-day order; timed evidence is required.') + '</p>')
    for warning in notices:
        if warning["code"] == "historical_forecast_after_actual":
            # Keep every warning and its evidence visible; capacity checking must
            # flag long content rather than silently truncate recorded history.
            detail = (f'节点 {warning["milestone_id"]}：已记录发生日 {warning["actual_date"]}；历史报告日 {warning["reported_on"]}，当时预测 {warning["forecast_date"]}。旧记录保留，需核对当时可得信息及来源适用性。' if zh else
                      f'Milestone {warning["milestone_id"]}: recorded actual {warning["actual_date"]}; historical report {warning["reported_on"]}, forecast then {warning["forecast_date"]}. History retained; verify information available then and source applicability.')
            content.append('<p class="schedule-note" data-warning-code="historical_forecast_after_actual">' + e(detail) + reference_marks(warning["refs"]) + '</p>')
    if view == "drift":
        mark = next(m for m in spec["milestones"] if m["id"] == cfg["milestone_id"])
        points = []
        for n, snap in enumerate(spec["snapshots"]):
            prediction = next(p for p in snap["forecasts"] if p["milestone_id"] == mark["id"])
            points.append((day(snap["reported_on"]), (day(prediction["date"]) - day(mark["baseline_date"])).days, prediction, n))
        low, high = min([0] + [p[1] for p in points]), max([0] + [p[1] for p in points])
        dx = (points[-1][0] - points[0][0]).days
        # Reserve actual glyph space above the largest deviation. The label
        # baseline is ten units above the point; the 22px presentation font
        # extends above that baseline and must remain inside the viewBox.
        plot_bottom, plot_height = 160, 115
        xy = [(60 + (d-points[0][0]).days/dx*1080, plot_bottom - (v-low)/(high-low or 1)*plot_height) for d,v,_,_ in points]
        path = "M" + " L".join(f"{px:.4f},{py:.4f}" for px,py in xy)
        dots = ''.join(f'<circle cx="{px:.4f}" cy="{py:.4f}" r="4"/><text x="{px:.4f}" y="{py-10:.4f}" text-anchor="middle">{v:+d}</text><text x="{px:.4f}" y="190" text-anchor="middle">{d.isoformat()}</text>' for (px,py),(d,v,_,_) in zip(xy,points))
        content.append(f'<p>{e(mark["label"])} · {"基线日期" if zh else "Baseline date"}: {e(mark["baseline_date"])}{reference_marks(mark["refs"])}</p>')
        zero_y = plot_bottom - (0-low)/(high-low or 1)*plot_height
        readable_plot = len(points) <= 4 and all(b[0]-a[0] >= 130 for a,b in zip(xy,xy[1:]))
        if readable_plot:
            content.append(f'<svg class="schedule-drift" viewBox="0 0 1200 200" role="img" aria-label="{"横轴为实际报告日期间距，纵轴为相对基线偏移自然日" if zh else "Actual reporting-day spacing; vertical baseline deviation in natural days"}"><line class="schedule-baseline" x1="60" x2="1140" y1="{zero_y:.4f}" y2="{zero_y:.4f}"/><path d="{path}" fill="none"/>{dots}</svg>')
        else:
            content.append('<p class="schedule-note">'+('历史记录较多或报告日期间隔过密；使用精确日期表逐页完整呈现，不等距拉开日期或覆盖标签。' if zh else 'Dense dates or a longer history use complete paginated date tables; dates are not stretched equally or labels overprinted.')+'</p>')
        rows = []
        visible_indices = cfg.get("snapshot_indices", list(range(len(points))))
        for d, v, prediction, n in points:
            if n not in visible_indices:
                continue
            rows.append(f'<tr {attrs("snapshot-"+str(n), {"reported_on": d.isoformat(), "forecast": prediction["date"], "baseline": mark["baseline_date"], "deviation_days":v}, prediction["refs"])}><td>{d.isoformat()}</td><td>{e(prediction["date"])}{reference_marks(prediction["refs"])}</td><td>{deviation(v)}</td></tr>')
        content.append('<table class="schedule-data"><thead><tr><th>' + ('报告日</th><th>当时预测</th><th>相对基线' if zh else 'Reported</th><th>Forecast then</th><th>Deviation') + '</th></tr></thead><tbody>'+''.join(rows)+'</tbody></table>')
        explanation = ('横轴：实际报告日期；纵轴：相对上述基线的自然日偏差。' if zh else 'X: actual reporting dates; Y: natural-day baseline deviation. ') if readable_plot else (f'本页记录 {visible_indices[0]+1}–{visible_indices[-1]+1}/{len(points)}；偏差相对于同一批准基线。' if zh else f'Records {visible_indices[0]+1}–{visible_indices[-1]+1}/{len(points)}; deviation from the same approved baseline. ')
        content.append('<p class="schedule-note">' + explanation + ('两点仅表示一次变化，不表示完成率或日期可信度。' if zh else 'Two points show one change, not completion or forecast confidence.') + '</p>')
    elif view == "milestones":
        marks = {m["id"]: m for m in spec["milestones"]}; rows = []
        for key in cfg["item_ids"]:
            mark = marks[key]; glyphs = []
            for kind, field, y in (("baseline","baseline_date",13),("actual","actual_date",29),("forecast","forecast_date",29)):
                if field in mark:
                    px=x(day(mark[field])); glyphs.append(f'<path class="schedule-{kind}" d="M{px:.4f},{y-5} l5,5 l-5,5 l-5,-5 Z"/>')
            dates = ' · '.join(f'{label}: {mark.get(field,unknown)}' for field,label in (("baseline_date","基线" if zh else "Baseline"),("actual_date","实际" if zh else "Actual"),("forecast_date","预测" if zh else "Forecast")))
            graphic='<svg viewBox="0 0 800 45" preserveAspectRatio="none" role="img" aria-label="'+e(dates)+'">'+''.join(glyphs)+'</svg>'
            rows.append(f'<tr {attrs(key,{**mark,"deviation_days":delta(mark,True)},mark["refs"])}><th>{e(mark["label"])}{reference_marks(mark["refs"])}</th><td>{graphic}<small>{e(dates)}</small></td><td>{deviation(delta(mark,True))}<small>{e(mark.get("condition",""))}</small></td></tr>')
        content.append('<table class="schedule-data schedule-timeline"><colgroup><col class="schedule-label-col"><col class="schedule-time-col"><col></colgroup><thead><tr><th>'+('里程碑' if zh else 'Milestone')+'</th><th>'+axis+'</th><th>'+('日期偏差 / 条件' if zh else 'Deviation / condition')+'</th></tr></thead><tbody>'+''.join(rows)+'</tbody></table>')
    else:
        tasks = {t["id"]:t for t in spec["tasks"]}; rows=[]
        if view=="summary":
            content.append('<p class="schedule-selection">'+ e(f'{"摘要选取" if zh else "Selected"} {len(spec["summary"]["task_ids"])}/{len(tasks)} · {spec["summary"]["reason"]}')+'</p>')
            mids=spec["summary"].get("milestone_ids",[])
            content.append('<p class="schedule-note">'+e((f'关键节点选取 {len(mids)}/{len(spec.get("milestones",[]))}' if mids else '本摘要未选取关键节点；不代表节点无风险。') if zh else f'Milestones selected {len(mids)}/{len(spec.get("milestones",[]))}; unselected does not mean risk-free.')+'</p>')
        for key in cfg["item_ids"]:
            task=tasks[key]; task_refs=list(task["refs"])
            if view=="summary":
                rows.append(f'<tr {attrs(key,{**task,"deviation_days":delta(task)},task_refs)}><th>{e(task["label"])}{reference_marks(task_refs)}<small>{e(task.get("owner",unknown))}</small></th><td>{e(states[task["state"]])}</td><td>{e(finish(task) or unknown)}<small>{deviation(delta(task))}</small></td><td>{e(task.get("condition",unknown))}</td></tr>')
            elif view=="outcomes":
                acc=task.get("acceptance",{"status":"unknown"}); task_refs += [r for r in acc.get("refs",[]) if r not in task_refs]
                details='<strong>'+e(acc.get("result",unknown))+'</strong><small>'+e(("标准: " if zh else "Criteria: ")+acc.get("criteria",unknown))+'</small><small>'+e(("范围: " if zh else "Scope: ")+acc.get("scope",unknown))+'</small>'
                rows.append(f'<tr {attrs(key,task,task_refs)}><th>{e(task["label"])}{reference_marks(task_refs)}</th><td>{details}</td><td>{e(states[task["state"]])}</td><td>{e(acceptance[acc["status"]])}</td></tr>')
            else:
                progress=task.get("progress"); ptext=unknown if not progress else f'{progress["value"]}% · {progress["basis"]}'
                if progress: task_refs += [r for r in progress["refs"] if r not in task_refs]
                label=f'<strong>{e(task["label"])}</strong>{reference_marks(task_refs)}<small>{e(task.get("owner",unknown))} · {e(states[task["state"]])}</small><small>{e(ptext)}</small>'
                result=f'<strong>{e(finish(task) or unknown)}</strong><span>{deviation(delta(task))}</span><small>{e(task.get("condition",""))}</small>'
                rows.append(f'<tr {attrs(key,{**task,"deviation_days":delta(task)},task_refs)}><th>{label}</th><td>{interval_svg(task)}<small class="schedule-date-text">{e(dates_text(task))}</small></td><td>{result}</td></tr>')
        if view=="summary":
            for key in cfg.get("milestone_ids",[]):
                mark=next(m for m in spec["milestones"] if m["id"]==key)
                state=("已发生" if "actual_date" in mark else "当前预测" if "forecast_date" in mark else "未知") if zh else ("actual" if "actual_date" in mark else "forecast" if "forecast_date" in mark else "unknown")
                rows.append(f'<tr {attrs(key,{**mark,"deviation_days":delta(mark,True)},mark["refs"])}><th>{e(mark["label"])}{reference_marks(mark["refs"])}</th><td>{state}</td><td>{e(mark.get("actual_date") or mark.get("forecast_date") or unknown)}<small>{deviation(delta(mark,True))}</small></td><td>{e(mark.get("condition",unknown))}</td></tr>')
            content.append('<table class="schedule-data schedule-summary"><thead><tr><th>'+('事项 / 节点</th><th>状态</th><th>当前日期 / 偏差</th><th>关键条件' if zh else 'Item / milestone</th><th>State</th><th>Current date / deviation</th><th>Condition')+'</th></tr></thead><tbody>'+''.join(rows)+'</tbody></table>')
        elif view=="outcomes":
            content.append('<table class="schedule-data schedule-outcomes"><thead><tr><th>'+('事项</th><th>结果、标准与范围</th><th>执行</th><th>验收' if zh else 'Item</th><th>Result, criteria and scope</th><th>Execution</th><th>Acceptance')+'</th></tr></thead><tbody>'+''.join(rows)+'</tbody></table>')
        else:
            content.append('<table class="schedule-data schedule-timeline"><colgroup><col class="schedule-label-col"><col class="schedule-time-col"><col></colgroup><thead><tr><th>'+('事项 / 状态 / 进度口径' if zh else 'Item / state / progress basis')+'</th><th>'+axis+'</th><th>'+('当前完成日 / 偏差' if zh else 'Current finish / deviation')+'</th></tr></thead><tbody>'+''.join(rows)+'</tbody></table>')
        if cfg.get("action_ids"):
            actions={a["id"]:a for a in spec["actions"]}
            content.append('<ul class="schedule-actions">')
            for key in cfg["action_ids"]:
                action=actions[key]
                content.append(f'<li {attrs(key,action,action["refs"])}>{e(action["text"])}{reference_marks(action["refs"])} <small>{e(action.get("owner",unknown))} · {e(action.get("due",unknown))}</small></li>')
            content.append('</ul>')
    if view == "milestones":
        content.append('<p class="schedule-note">'+('灰色实心菱形：批准基线；蓝色实心菱形：已经发生；蓝色空心虚线菱形：当前预测。' if zh else 'Gray filled diamond: baseline; blue filled diamond: actual; blue hollow dashed diamond: forecast.')+'</p>')
    if view == "gantt":
        content.append('<p class="schedule-legend"><span class="legend-baseline">'+('细灰线：批准基线' if zh else 'Thin gray: baseline')+'</span><span class="legend-actual">'+('实线：实际经过' if zh else 'Solid: actual elapsed')+'</span><span class="legend-forecast">'+('虚线：预测' if zh else 'Dashed: forecast')+'</span> · '+('经过区间不等于工作量；点仅表示已知日期。' if zh else 'Elapsed time is not work completed; dots indicate a single known date.')+'</p>')
    sources=' · '.join(f'[{n+1}] {r["id"]}@{r["revision"]}'+(' · '+r["locator"] if r.get("locator") else '') for n,r in enumerate(refs_used))
    if source_ref is None:
        content.append('<p class="schedule-provenance">'+e(sources)+'</p>')
    return '<div class="schedule-content" data-schedule-view="'+view+'">'+''.join(content)+'</div>', mappings
