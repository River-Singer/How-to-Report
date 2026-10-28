"""Bounded natural-day schedule contract; business tasks are not Agent tasks."""
from __future__ import annotations

from datetime import date, timedelta
import math
import re

VERSION = "0.1"
VIEWS = ("summary", "gantt", "milestones", "outcomes", "drift")
ID = re.compile(r"[A-Za-z][A-Za-z0-9_-]{0,31}\Z")
STATES = {"not_started", "active", "blocked", "done"}
ACCEPTANCE = {"not_submitted", "pending", "accepted", "rejected", "unknown"}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def fields(obj, required, optional=(), where="schedule"):
    need(isinstance(obj, dict), where + ": expected object")
    need(set(required) <= obj.keys(), where + ": missing required fields")
    need(obj.keys() <= set(required) | set(optional), where + ": unknown fields")


def text(value, where, maximum=1000):
    need(isinstance(value, str) and bool(value.strip()) and len(value) <= maximum,
         where + ": expected bounded nonempty text")
    need(not any(ord(c) < 32 and c not in "\n\r\t" for c in value), where + ": control character")


def ident(value, where):
    need(isinstance(value, str) and ID.fullmatch(value), where + ": invalid identifier")


def day(value, where="date"):
    need(isinstance(value, str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", value), where + ": use YYYY-MM-DD")
    try:
        result = date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(where + ": invalid date") from exc
    need(1900 <= result.year <= 2100, where + ": supported years 1900–2100")
    return result


def refs(value, where):
    need(isinstance(value, list) and 1 <= len(value) <= 50, where + ": exact source references required")
    seen = set()
    for ref in value:
        fields(ref, ("id", "revision"), ("locator",), where)
        text(ref["id"], where, 128)
        need(type(ref["revision"]) is int and ref["revision"] > 0, where + ": positive revision required")
        if "locator" in ref:
            text(ref["locator"], where, 1000)
        key = (ref["id"], ref["revision"], ref.get("locator"))
        need(key not in seen, where + ": duplicate reference")
        seen.add(key)


def collection(value, maximum, where):
    need(isinstance(value, list) and len(value) <= maximum, where + ": list exceeds supported capacity")


def interval(value, where, actual=False, as_of=None):
    fields(value, (), ("start", "finish"), where)
    need(bool(value), where + ": empty interval; omit unknown interval")
    dates = {k: day(v, where + "." + k) for k, v in value.items()}
    if "start" in dates and "finish" in dates:
        need(dates["start"] <= dates["finish"], where + ": start after finish")
    if actual:
        need(all(v <= as_of for v in dates.values()), where + ": future actual date")
    return dates


def validate(spec):
    fields(spec, ("schedule_version", "title", "as_of", "calendar", "refs", "tasks"),
           ("baseline", "milestones", "dependencies", "snapshots", "summary", "actions", "limits"))
    need(spec["schedule_version"] == VERSION, "unsupported schedule version")
    text(spec["title"], "title", 160)
    as_of = day(spec["as_of"], "as_of")
    need(spec["calendar"] == "calendar_days", "only natural days / end-of-day snapshots are supported")
    refs(spec["refs"], "refs")
    if "limits" in spec:
        collection(spec["limits"], 20, "limits")
        for limit in spec["limits"]:
            text(limit, "limit", 300)
    baseline = spec.get("baseline")
    if baseline is not None:
        fields(baseline, ("id", "revision", "approved_on", "refs"), (), "baseline")
        ident(baseline["id"], "baseline")
        need(type(baseline["revision"]) is int and baseline["revision"] > 0, "baseline revision required")
        need(day(baseline["approved_on"]) <= as_of, "baseline approval after status date")
        refs(baseline["refs"], "baseline.refs")
    collection(spec["tasks"], 500, "tasks")
    need(bool(spec["tasks"]), "at least one task required")
    tasks, ids = {}, set()
    for task in spec["tasks"]:
        fields(task, ("id", "label", "state", "refs"),
               ("owner", "baseline", "actual", "forecast", "progress", "acceptance", "condition"), "task")
        ident(task["id"], "task.id")
        need(task["id"] not in ids, "duplicate business object ID")
        ids.add(task["id"]); tasks[task["id"]] = task
        text(task["label"], "task.label", 180)
        need(isinstance(task["state"], str) and task["state"] in STATES, "invalid execution state")
        refs(task["refs"], "task.refs")
        for key in ("owner", "condition"):
            if key in task:
                text(task[key], key, 300)
        for key in ("baseline", "actual", "forecast"):
            if key in task:
                interval(task[key], "task." + key, key == "actual", as_of)
        if "baseline" in task:
            need(baseline is not None, "task dates need approved baseline identity")
        actual, forecast = task.get("actual", {}), task.get("forecast", {})
        need(not actual.get("finish") or actual.get("start"), "actual finish requires actual start")
        if task["state"] == "done":
            need(bool(actual.get("finish")), "done requires actual finish")
            need(not forecast, "completed task must not retain remaining forecast")
        else:
            need(not actual.get("finish"), "actual finish requires done execution state")
        if task["state"] in ("active", "blocked"):
            need(bool(actual.get("start")), "active/blocked task requires actual start")
        if task["state"] == "not_started":
            need(not actual, "not_started must not have actual interval")
        if forecast:
            need(all(day(v) > as_of for v in forecast.values()), "remaining forecast must follow end-of-day status")
        if "progress" in task:
            progress = task["progress"]
            fields(progress, ("value", "basis", "refs"), (), "progress")
            v = progress["value"]
            need(type(v) in (int, float) and 0 <= v <= 100 and math.isfinite(v), "progress must be finite 0–100")
            text(progress["basis"], "progress.basis", 300); refs(progress["refs"], "progress.refs")
        if "acceptance" in task:
            acc = task["acceptance"]
            fields(acc, ("status",), ("criteria", "result", "scope", "refs"), "acceptance")
            need(isinstance(acc["status"], str) and acc["status"] in ACCEPTANCE, "invalid acceptance state")
            for key in ("criteria", "result", "scope"):
                if key in acc:
                    text(acc[key], "acceptance." + key, 600)
            if "refs" in acc:
                refs(acc["refs"], "acceptance.refs")
            if acc["status"] in ("accepted", "rejected"):
                need(all(k in acc for k in ("criteria", "result", "scope", "refs")),
                     "accepted/rejected requires criteria, result, scope and evidence references")
    milestones = spec.get("milestones", [])
    collection(milestones, 200, "milestones")
    for mark in milestones:
        fields(mark, ("id", "label", "refs"), ("baseline_date", "actual_date", "forecast_date", "condition"), "milestone")
        ident(mark["id"], "milestone.id"); need(mark["id"] not in ids, "duplicate business object ID"); ids.add(mark["id"])
        text(mark["label"], "milestone.label", 180); refs(mark["refs"], "milestone.refs")
        for key in ("baseline_date", "actual_date", "forecast_date"):
            if key in mark:
                day(mark[key], key)
        if "baseline_date" in mark:
            need(baseline is not None, "milestone baseline needs approved identity")
        if "actual_date" in mark:
            need(day(mark["actual_date"]) <= as_of and "forecast_date" not in mark, "milestone actual/forecast conflict")
        if "forecast_date" in mark:
            need(day(mark["forecast_date"]) > as_of, "milestone forecast must follow status date")
        if "condition" in mark:
            text(mark["condition"], "milestone.condition", 300)
    edges = spec.get("dependencies", [])
    collection(edges, 2000, "dependencies")
    graph, indegree, pairs = {k: [] for k in tasks}, {k: 0 for k in tasks}, set()
    for edge in edges:
        fields(edge, ("from", "to", "type", "lag", "refs"), (), "dependency")
        need(isinstance(edge["from"], str) and isinstance(edge["to"], str) and edge["from"] in tasks and edge["to"] in tasks, "unknown dependency task")
        need(edge["type"] == "FS" and type(edge["lag"]) is int and edge["lag"] == 0, "only FS with zero lag supported")
        refs(edge["refs"], "dependency.refs")
        pair = (edge["from"], edge["to"]); need(pair not in pairs, "duplicate dependency"); pairs.add(pair)
        graph[pair[0]].append(pair[1]); indegree[pair[1]] += 1
        for scenario in ("baseline", "actual", "forecast"):
            finish = tasks[pair[0]].get(scenario, {}).get("finish")
            start = tasks[pair[1]].get(scenario, {}).get("start")
            if finish and start:
                need(day(start) >= day(finish), "FS successor starts before predecessor finish")
        effective_finish = tasks[pair[0]].get("actual", {}).get("finish") or tasks[pair[0]].get("forecast", {}).get("finish")
        effective_start = tasks[pair[1]].get("actual", {}).get("start") or tasks[pair[1]].get("forecast", {}).get("start")
        if effective_finish and effective_start:
            need(day(effective_start) >= day(effective_finish), "FS current actual/forecast conflict")
    ready = [k for k, v in indegree.items() if v == 0]; visited = 0
    while ready:
        key = ready.pop(); visited += 1
        for other in graph[key]:
            indegree[other] -= 1
            if indegree[other] == 0: ready.append(other)
    need(visited == len(tasks), "cyclic business dependencies")
    marks = {v["id"]: v for v in milestones}
    snapshots = spec.get("snapshots", [])
    collection(snapshots, 100, "snapshots")
    previous = None
    for snap in snapshots:
        fields(snap, ("reported_on", "baseline_ref", "forecasts"), (), "snapshot")
        reporting = day(snap["reported_on"])
        need(reporting <= as_of and (previous is None or reporting > previous), "snapshots must be unique chronological past dates")
        previous = reporting
        fields(snap["baseline_ref"], ("id", "revision"), (), "snapshot.baseline_ref")
        ident(snap["baseline_ref"]["id"], "snapshot.baseline_ref.id")
        need(type(snap["baseline_ref"]["revision"]) is int and snap["baseline_ref"]["revision"] > 0, "snapshot baseline revision must be a positive integer")
        need(baseline is not None and snap["baseline_ref"] == {"id": baseline["id"], "revision": baseline["revision"]},
             "mixed/historical baseline not supported in one drift series; split by baseline")
        need(reporting >= day(baseline["approved_on"]), "snapshot predates baseline approval")
        collection(snap["forecasts"], 200, "forecasts"); seen_marks = set()
        for prediction in snap["forecasts"]:
            fields(prediction, ("milestone_id", "date", "refs"), (), "forecast snapshot")
            mid = prediction["milestone_id"]
            need(isinstance(mid, str) and mid in marks and mid not in seen_marks, "unknown/duplicate snapshot milestone")
            seen_marks.add(mid); need(day(prediction["date"]) >= reporting, "historical forecast precedes its report date")
            refs(prediction["refs"], "snapshot.refs")
            current_forecast = marks[mid].get("forecast_date")
            if reporting == as_of and current_forecast is not None:
                need(prediction["date"] == current_forecast,
                     "same-day current/historical forecast conflict for milestone " + mid)
    if "summary" in spec:
        fields(spec["summary"], ("task_ids", "reason"), ("milestone_ids",), "summary")
        selected(spec["summary"]["task_ids"], tasks, "summary task_ids")
        text(spec["summary"]["reason"], "summary.reason", 600)
        if spec["summary"].get("milestone_ids"):
            selected(spec["summary"]["milestone_ids"], marks, "summary milestone_ids")
        else:
            need(isinstance(spec["summary"].get("milestone_ids", []), list), "summary milestone_ids must be a list")
        need(all(t["id"] in spec["summary"]["task_ids"] for t in spec["tasks"] if t["state"] == "blocked"),
             "summary omits blocked tasks; include them and paginate")
    actions = spec.get("actions", []); collection(actions, 200, "actions")
    for action in actions:
        fields(action, ("id", "text", "refs"), ("owner", "due"), "action")
        ident(action["id"], "action.id"); need(action["id"] not in ids, "duplicate business object ID"); ids.add(action["id"])
        text(action["text"], "action.text", 600); refs(action["refs"], "action.refs")
        if "owner" in action: text(action["owner"], "action.owner", 120)
        if "due" in action: day(action["due"])
    return spec


def selected(values, available, where):
    need(isinstance(values, list) and values, where + ": explicit nonempty selection required")
    need(all(isinstance(v, str) and v in available for v in values), where + ": unknown object")
    need(len(set(values)) == len(values), where + ": duplicate object")


def finish(task):
    return task.get("actual", {}).get("finish") or task.get("forecast", {}).get("finish")


def warnings(spec):
    """A day-only input cannot establish ordering of two events on the same day."""
    result = []
    tasks = {t["id"]: t for t in spec["tasks"]}
    for edge in spec.get("dependencies", []):
        left, right = tasks[edge["from"]], tasks[edge["to"]]
        pairs = [(name, left.get(name, {}).get("finish"), right.get(name, {}).get("start"))
                 for name in ("baseline", "actual", "forecast")]
        pairs.append(("current", finish(left), right.get("actual", {}).get("start") or right.get("forecast", {}).get("start")))
        for name, end, start in pairs:
            if end and start and end == start:
                result.append({"code": "same_day_fs_order_unknown", "from": edge["from"], "to": edge["to"],
                               "scenario": name, "date": start,
                               "detail": "日级日期不能证明日内先后；需要时间记录才能核实FS关系。"})
    marks = {m["id"]: m for m in spec.get("milestones", [])}
    for snapshot in spec.get("snapshots", []):
        for prediction in snapshot["forecasts"]:
            mark = marks[prediction["milestone_id"]]
            actual = mark.get("actual_date")
            if actual and day(actual) < day(snapshot["reported_on"]):
                evidence = list(mark["refs"])
                evidence += [r for r in prediction["refs"] if r not in evidence]
                result.append({"code": "historical_forecast_after_actual", "milestone_id": mark["id"],
                               "actual_date": actual, "reported_on": snapshot["reported_on"],
                               "forecast_date": prediction["date"], "refs": evidence,
                               "detail": "旧预测保留；报告日晚于已记录发生日，需核对当时可得信息及来源适用性。"})
    return result


def delta(item, milestone=False):
    base = item.get("baseline_date") if milestone else item.get("baseline", {}).get("finish")
    current = item.get("actual_date") or item.get("forecast_date") if milestone else finish(item)
    return (day(current) - day(base)).days if current and base else None


def validate_component(element, seen):
    config = element["schedule"]
    fields(config, ("spec", "view"), ("item_ids", "action_ids", "milestone_id", "milestone_ids", "snapshot_indices"), "schedule component")
    spec = validate(config["spec"]); view = config["view"]
    need(isinstance(view, str) and view in VIEWS, "unsupported schedule view")
    used = []
    if view in ("summary", "gantt", "outcomes", "milestones"):
        available = spec.get("milestones", []) if view == "milestones" else spec["tasks"]
        if view == "summary" and config.get("milestone_ids") and config.get("item_ids") == []:
            pass
        else:
            selected(config.get("item_ids"), {v["id"] for v in available}, "component item_ids")
        need(len(config["item_ids"]) <= 8, "component capacity exceeded; paginate")
        used.extend(config["item_ids"])
        need(not {"milestone_id", "snapshot_indices"}.intersection(config), "milestone_id/snapshot_indices only for drift")
        if view == "summary":
            need("summary" in spec, "summary selection/reason required")
            need(all(k in spec["summary"]["task_ids"] for k in config["item_ids"]), "summary contains unselected item")
        if "milestone_ids" in config:
            need(view == "summary", "milestone_ids only for summary")
            selected(config["milestone_ids"], spec.get("summary", {}).get("milestone_ids", []), "summary milestone_ids")
            need(len(config["milestone_ids"]) <= 4, "summary milestone capacity exceeded")
            used.extend(config["milestone_ids"])
        if "action_ids" in config:
            need(view == "summary", "actions only in summary")
            selected(config["action_ids"], {a["id"] for a in spec.get("actions", [])}, "action_ids")
            need(len(config["action_ids"]) <= 3, "action capacity exceeded; paginate")
            used.extend(config["action_ids"])
    else:
        need(not {"item_ids", "action_ids", "milestone_ids"}.intersection(config), "drift accepts milestone_id only")
        mid = config.get("milestone_id"); marks = {m["id"]: m for m in spec.get("milestones", [])}
        need(isinstance(mid, str) and mid in marks, "drift needs known milestone")
        need("baseline_date" in marks[mid], "drift requires approved baseline date")
        need(len(spec.get("snapshots", [])) >= 2, "drift requires at least two recorded snapshots")
        need(len(spec["snapshots"]) <= 12, "drift capacity exceeded; select explicit history window")
        indices = config.get("snapshot_indices", list(range(len(spec["snapshots"]))))
        need(isinstance(indices, list) and indices and all(type(n) is int and 0 <= n < len(spec["snapshots"]) for n in indices), "invalid snapshot_indices")
        need(indices == sorted(set(indices)) and len(indices) <= 4, "drift page capacity exceeded; paginate chronological snapshots")
        for n, snapshot in enumerate(spec["snapshots"]):
            need(any(p["milestone_id"] == mid for p in snapshot["forecasts"]), "missing historical forecast; do not interpolate")
            if n in indices:
                used.append("snapshot-" + str(n))
    for key in used:
        identity = element["id"] + "-" + key
        need(identity not in seen, "duplicate schedule datum identity")
        seen.add(identity)
    return config


def to_plan(spec, views, canvas=None):
    validate(spec)
    need(isinstance(views, list) and views and len(set(views)) == len(views) and all(v in VIEWS for v in views), "choose unique supported views")
    canvas = canvas or {"width": 1600, "height": 900}
    fields(canvas, ("width", "height"), (), "canvas")
    need(type(canvas["width"]) is int and type(canvas["height"]) is int and
         1200 <= canvas["width"] <= 2400 and 675 <= canvas["height"] <= 1600 and
         1.2 <= canvas["width"] / canvas["height"] <= 2.4, "unsupported canvas")
    # Conservative initial capacity; final DOM inspection remains required.
    capacity = max(1, min(6, int((canvas["height"] - 350) / 85)))
    titles = {"summary": "项目进度与需要支持的事项", "gantt": "计划、实际与预测对照", "milestones": "里程碑日期对照", "outcomes": "交付结果与验收状态", "drift": "同一基线下的历史预测变化"}
    pages = []
    for view in views:
        if view == "drift":
            groups = [{"milestone_id": m["id"], "snapshot_indices": list(range(i, min(i+4, len(spec.get("snapshots",[])))))} for m in spec.get("milestones", []) if "baseline_date" in m for i in range(0, len(spec.get("snapshots",[])), 4)]
            need(groups, "drift requires milestones with baseline dates")
        else:
            if view == "summary":
                need("summary" in spec, "summary requires explicit task selection and reason")
                values = spec["summary"]["task_ids"]
            else:
                values = [x["id"] for x in (spec.get("milestones", []) if view == "milestones" else spec["tasks"])]
            need(values, view + ": no eligible records")
            view_capacity = min(capacity, 3) if view == "summary" and spec.get("actions") else capacity
            groups = [{"item_ids": values[i:i + view_capacity]} for i in range(0, len(values), view_capacity)]
            if view == "summary":
                mids = spec["summary"].get("milestone_ids", [])
                groups += [{"item_ids": [], "milestone_ids": mids[i:i + min(3,capacity)]} for i in range(0, len(mids), min(3,capacity))]
            if view == "summary" and spec.get("actions"):
                action_ids = [a["id"] for a in spec["actions"]]
                # Repeat selected context explicitly when action pages outnumber task pages.
                while len(groups) < math.ceil(len(action_ids) / 3):
                    groups.append({"item_ids": values[:min(2, capacity)]})
                for i, group in enumerate(groups):
                    subset = action_ids[i * 3:(i + 1) * 3]
                    if subset: group["action_ids"] = subset
        for n, group in enumerate(groups):
            pid = f"schedule-{view}-{n + 1}"
            config = {"spec": spec, "view": view, **group}
            element = {"id": pid + "-view", "type": "schedule", "role": "primary", "title": titles[view],
                       "body": "状态日 " + spec["as_of"] + " · 自然日 · 日终快照", "refs": spec["refs"], "limits": [], "schedule": config}
            validate_component(element, set())
            title = titles[view] + (f"（{n + 1}/{len(groups)}）" if len(groups) > 1 else "")
            element["title"] = title
            pages.append({"id": pid, "layout": "composed", "title": title, "question": titles[view],
                          "takeaway": "按明确来源区分已经发生、尚未发生及尚未核实的内容。", "limits": spec.get("limits", []),
                          "refs": spec["refs"], "elements": [element], "tree": {"element": element["id"]}})
    need(len(pages) <= 100, "too many pages; split the reporting scope")
    return {"page_plan_version": "0.2", "title": spec["title"], "language": "zh-CN", "canvas": canvas, "pages": pages}
