"""Optional offline date/state validation; no presentation or scheduling engine.

Collection limits bound local processing resources, not report length or layout.
"""
from __future__ import annotations

from datetime import date
import math
import re

VERSION = "0.1"
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
    need(isinstance(value, list) and len(value) <= maximum, where + ": list exceeds local validation resource limit")


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
    text(spec["title"], "title", 10000)
    as_of = day(spec["as_of"], "as_of")
    need(spec["calendar"] == "calendar_days", "only natural days / end-of-day snapshots are supported")
    refs(spec["refs"], "refs")
    if "limits" in spec:
        collection(spec["limits"], 20, "limits")
        for limit in spec["limits"]:
            text(limit, "limit", 10000)
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
        text(task["label"], "task.label", 10000)
        need(isinstance(task["state"], str) and task["state"] in STATES, "invalid execution state")
        refs(task["refs"], "task.refs")
        for key in ("owner", "condition"):
            if key in task:
                text(task[key], key, 10000)
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
            text(progress["basis"], "progress.basis", 10000); refs(progress["refs"], "progress.refs")
        if "acceptance" in task:
            acc = task["acceptance"]
            fields(acc, ("status",), ("criteria", "result", "scope", "refs"), "acceptance")
            need(isinstance(acc["status"], str) and acc["status"] in ACCEPTANCE, "invalid acceptance state")
            for key in ("criteria", "result", "scope"):
                if key in acc:
                    text(acc[key], "acceptance." + key, 10000)
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
        text(mark["label"], "milestone.label", 10000); refs(mark["refs"], "milestone.refs")
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
            text(mark["condition"], "milestone.condition", 10000)
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
             "mixed/historical baseline not supported in one comparison group; split by baseline")
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
        text(spec["summary"]["reason"], "summary.reason", 10000)
        if spec["summary"].get("milestone_ids"):
            selected(spec["summary"]["milestone_ids"], marks, "summary milestone_ids")
        else:
            need(isinstance(spec["summary"].get("milestone_ids", []), list), "summary milestone_ids must be a list")
    actions = spec.get("actions", []); collection(actions, 200, "actions")
    for action in actions:
        fields(action, ("id", "text", "refs"), ("owner", "due"), "action")
        ident(action["id"], "action.id"); need(action["id"] not in ids, "duplicate business object ID"); ids.add(action["id"])
        text(action["text"], "action.text", 10000); refs(action["refs"], "action.refs")
        if "owner" in action: text(action["owner"], "action.owner", 10000)
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
