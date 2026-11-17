"""Immutable production state with bounded jobs and evidence-bound release checks."""
from __future__ import annotations

from copy import deepcopy
import hashlib
import math
from pathlib import Path
import time

from presentation_document import document_hash, validate_document


CHECK_STATUSES = {"not_run", "pass", "fail", "not_assessable"}
DEFAULT_CHECKS = ["build", "target_render", "content_review", "visual_review",
                  "template-and-dataviz", "editability"]


def _text(value, where):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{where}: expected nonempty text")


def _integer(value, where, minimum=0):
    if type(value) is not int or value < minimum:
        raise ValueError(f"{where}: expected integer >= {minimum}")


def _now(value):
    value = time.time() if value is None else value
    if type(value) not in (int, float) or not math.isfinite(value):
        raise ValueError("now must be a finite epoch time")
    return value


def _fingerprint(path):
    path = Path(path).resolve(strict=True)
    if not path.is_file():
        raise ValueError(f"expected a file: {path}")
    data = path.read_bytes()
    if not data:
        raise ValueError(f"evidence file is empty: {path}")
    return {"path": str(path), "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}


def _state(state):
    if not isinstance(state, dict) or state.get("control_version") != "0.1":
        raise ValueError("unsupported presentation controller state")
    _text(state.get("project_id"), "project_id")
    _integer(state.get("document_revision"), "document_revision", 1)
    _text(state.get("document_hash"), "document_hash")
    budget = state.get("budget")
    if not isinstance(budget, dict):
        raise ValueError("missing budget")
    for name in ("max_calls", "max_repairs", "calls_reserved", "calls_completed", "repairs_used"):
        _integer(budget.get(name), "budget." + name)
    if budget.get("deadline") is None or budget.get("started_at") is None:
        raise ValueError("budget requires started_at and deadline")
    _now(budget["deadline"])
    _now(budget["started_at"])
    if budget["calls_reserved"] > budget["max_calls"] or budget["repairs_used"] > budget["max_repairs"]:
        raise ValueError("budget counters exceed configured limits")
    if not isinstance(state.get("calls"), dict) or not isinstance(state.get("checks"), list):
        raise ValueError("invalid calls/checks state")
    if not isinstance(state.get("findings"), list):
        raise ValueError("findings must be an array")
    checks = state.get("required_checks")
    if not isinstance(checks, list) or not checks or not all(isinstance(x, str) and x for x in checks):
        raise ValueError("required_checks must contain check IDs")
    if len(checks) != len(set(checks)):
        raise ValueError("required_checks must be unique")
    document_hash(state)


def new_control_state(document, *, max_calls=40, max_repairs=2, max_seconds=1800,
                      required_checks=None, now=None):
    validate_document(document)
    _integer(max_calls, "max_calls", 1)
    _integer(max_repairs, "max_repairs")
    if type(max_seconds) not in (int, float) or not math.isfinite(max_seconds) or max_seconds <= 0:
        raise ValueError("max_seconds must be positive and finite")
    started = _now(now)
    state = {
        "control_version": "0.1", "project_id": document["project_id"],
        "document_revision": document["revision"], "document_hash": document_hash(document),
        "stage": "intake", "artifact": None,
        "required_checks": deepcopy(DEFAULT_CHECKS if required_checks is None else required_checks),
        "budget": {"started_at": started, "deadline": started + max_seconds,
                   "max_calls": max_calls, "max_repairs": max_repairs,
                   "calls_reserved": 0, "calls_completed": 0, "repairs_used": 0},
        "enforcement_scope": ["controller_jobs"], "calls": {}, "checks": [], "findings": [],
        "repairs": [], "document_history": [], "artifact_history": [],
    }
    _state(state)
    return state


def reserve_call(state, operation_id, kind, *, now=None):
    _state(state)
    _text(operation_id, "operation_id")
    _text(kind, "kind")
    if operation_id in state["calls"]:
        previous = state["calls"][operation_id]
        if previous["kind"] != kind:
            raise ValueError("operation_id already reserved for another kind")
        if previous.get("document_hash") != state["document_hash"]:
            raise ValueError("operation_id already reserved for another document version")
        return deepcopy(state)
    timestamp = _now(now)
    budget = state["budget"]
    if timestamp >= budget["deadline"]:
        raise ValueError("production deadline exhausted")
    if budget["calls_reserved"] >= budget["max_calls"]:
        raise ValueError("production call budget exhausted")
    result = deepcopy(state)
    result["budget"]["calls_reserved"] += 1
    result["calls"][operation_id] = {"kind": kind, "reserved_at": timestamp,
                                      "status": "reserved", "document_hash": state["document_hash"],
                                      "document_revision": state["document_revision"]}
    return result


def record_call(state, operation_id, result, *, now=None):
    _state(state)
    if operation_id not in state["calls"]:
        raise ValueError("call was not reserved")
    if not isinstance(result, dict):
        raise ValueError("call result must be a JSON object")
    result_hash = document_hash(result)
    call = state["calls"][operation_id]
    if call["status"] == "completed":
        if call["result_hash"] != result_hash:
            raise ValueError("operation_id already completed with another result")
        return deepcopy(state)
    updated = deepcopy(state)
    updated["calls"][operation_id].update(status="completed", completed_at=_now(now),
                                           result=deepcopy(result), result_hash=result_hash)
    updated["budget"]["calls_completed"] += 1
    return updated


def start_repair(state, reason, *, now=None):
    _state(state)
    _text(reason, "repair reason")
    timestamp = _now(now)
    budget = state["budget"]
    if timestamp >= budget["deadline"]:
        raise ValueError("production deadline exhausted")
    if budget["repairs_used"] >= budget["max_repairs"]:
        raise ValueError("production repair budget exhausted")
    if budget["calls_reserved"] >= budget["max_calls"]:
        raise ValueError("no call budget remains for repair verification")
    updated = deepcopy(state)
    updated["budget"]["repairs_used"] += 1
    updated["stage"] = "repair"
    updated["repairs"].append({"number": updated["budget"]["repairs_used"],
                                "reason": reason, "started_at": timestamp,
                                "document_hash": state["document_hash"]})
    return updated


def sync_document(state, document):
    """Update author identity without resetting budget, history or open findings."""
    _state(state)
    validate_document(document)
    if state["project_id"] != document["project_id"]:
        raise ValueError("controller belongs to another project")
    identity = document_hash(document)
    if identity == state["document_hash"]:
        return deepcopy(state)
    if document["revision"] <= state["document_revision"]:
        raise ValueError("changed document requires a greater revision")
    updated = deepcopy(state)
    updated["document_history"].append({"revision": state["document_revision"],
                                         "sha256": state["document_hash"]})
    updated["document_revision"] = document["revision"]
    updated["document_hash"] = identity
    if updated["artifact"]:
        updated["artifact_history"].append(updated["artifact"])
    updated["artifact"] = None
    updated["stage"] = "design"
    return updated


def bind_artifact(state, path):
    _state(state)
    artifact = _fingerprint(path)
    artifact.update(document_revision=state["document_revision"], document_hash=state["document_hash"])
    updated = deepcopy(state)
    if state["artifact"] and state["artifact"] != artifact:
        updated["artifact_history"].append(updated["artifact"])
    updated["artifact"] = artifact
    updated["stage"] = "review"
    return updated


def _current(record, state):
    artifact = state.get("artifact")
    return bool(artifact and record.get("document_revision") == state["document_revision"]
                and record.get("document_hash") == state["document_hash"]
                and record.get("artifact_hash") == artifact["sha256"])


def record_check(state, check_id, status, detail_ref, *, method=None, scope=None,
                 detail_path=None, fatal=False):
    _state(state)
    _text(check_id, "check_id")
    if status not in CHECK_STATUSES:
        raise ValueError("unsupported check status")
    _text(detail_ref, "detail_ref")
    if type(fatal) is not bool:
        raise ValueError("fatal must be boolean")
    if not state.get("artifact"):
        raise ValueError("bind actual artifact before recording checks")
    if status == "pass":
        _text(method, "pass method")
        _text(scope, "pass scope")
    evidence = _fingerprint(detail_path or detail_ref)
    check = {"id": check_id, "status": status, "detail_ref": detail_ref,
             "detail_path": evidence["path"], "detail_hash": evidence["sha256"],
             "method": method, "scope": scope, "fatal": fatal,
             "document_revision": state["document_revision"], "document_hash": state["document_hash"],
             "artifact_hash": state["artifact"]["sha256"]}
    # Retain all earlier checks. New input revisions provide distinct acceptance targets.
    for old in state["checks"]:
        if old["id"] == check_id and _current(old, state):
            if old == check:
                return deepcopy(state)
            raise ValueError("check ID already records another result for this exact artifact")
    updated = deepcopy(state)
    updated["checks"].append(check)
    return updated


def record_finding(state, finding):
    _state(state)
    if not isinstance(finding, dict):
        raise ValueError("finding must be an object")
    for field in ("id", "requirement", "evidence", "impact", "acceptance"):
        _text(finding.get(field), "finding." + field)
    if finding.get("severity", "blocker") not in ("blocker", "improvement", "preference"):
        raise ValueError("unsupported finding severity")
    if finding.get("status", "open") != "open":
        raise ValueError("new finding must be open; resolve it with a current pass check")
    if type(finding.get("fatal", False)) is not bool:
        raise ValueError("finding.fatal must be boolean")
    record = deepcopy(finding)
    record.update(status="open", severity=finding.get("severity", "blocker"),
                  observed_document_hash=state["document_hash"])
    for old in state["findings"]:
        if old["id"] == record["id"]:
            if old == record:
                return deepcopy(state)
            raise ValueError("finding ID already exists")
    updated = deepcopy(state)
    updated["findings"].append(record)
    return updated


def resolve_finding(state, finding_id, check_id, reason):
    _state(state)
    _text(reason, "resolution reason")
    checks = [check for check in state["checks"]
              if check["id"] == check_id and check["status"] == "pass" and _current(check, state)]
    if not checks:
        raise ValueError("finding resolution requires a current artifact pass check")
    if _fingerprint(checks[0]["detail_path"])["sha256"] != checks[0]["detail_hash"]:
        raise ValueError("resolution check evidence changed")
    updated = deepcopy(state)
    finding = next((item for item in updated["findings"] if item["id"] == finding_id), None)
    if finding is None:
        raise ValueError("unknown finding ID")
    finding.update(status="resolved", resolution_check_id=check_id, resolution_reason=reason,
                   resolved_document_hash=state["document_hash"],
                   resolved_artifact_hash=state["artifact"]["sha256"])
    return updated


def evaluate_release(state, document=None, *, now=None):
    """Report current evidence. Scores and previous revisions never create a pass."""
    _state(state)
    reasons = []
    fatal = False
    if document is not None:
        validate_document(document)
        if (document["project_id"] != state["project_id"]
                or document["revision"] != state["document_revision"]
                or document_hash(document) != state["document_hash"]):
            reasons.append("controller author identity is stale")
            fatal = True
    artifact = state.get("artifact")
    if not artifact:
        reasons.append("no current artifact is bound")
        fatal = True
    else:
        try:
            if _fingerprint(artifact["path"])["sha256"] != artifact["sha256"]:
                reasons.append("bound artifact bytes changed")
                fatal = True
        except (OSError, ValueError) as exc:
            reasons.append(f"bound artifact is unavailable: {exc}")
            fatal = True
    current = [check for check in state["checks"] if _current(check, state)]
    present = {check["id"] for check in current}
    for identifier in state["required_checks"]:
        if identifier not in present:
            reasons.append(f"required check not_run: {identifier}")
    for check in current:
        if check["status"] != "pass":
            reasons.append(f"check {check['id']} is {check['status']}")
            fatal = fatal or check.get("fatal", False)
        elif not check.get("method") or not check.get("scope"):
            reasons.append(f"check {check['id']} lacks method/scope")
        try:
            if _fingerprint(check["detail_path"])["sha256"] != check["detail_hash"]:
                reasons.append(f"check evidence changed: {check['id']}")
        except (OSError, ValueError, KeyError) as exc:
            reasons.append(f"check evidence unavailable: {check['id']}: {exc}")
    open_findings = []
    for finding in state["findings"]:
        resolution_current = bool(artifact and finding.get("status") == "resolved"
                                  and finding.get("resolved_document_hash") == state["document_hash"]
                                  and finding.get("resolved_artifact_hash") == artifact["sha256"])
        if finding["severity"] == "blocker" and not resolution_current:
            open_findings.append(finding["id"])
            reasons.append(f"unresolved blocker: {finding['id']}")
            fatal = fatal or finding.get("fatal", False)
    budget = state["budget"]
    exhausted = []
    if _now(now) >= budget["deadline"]:
        exhausted.append("deadline")
    if budget["calls_reserved"] >= budget["max_calls"]:
        exhausted.append("calls")
    if budget["repairs_used"] >= budget["max_repairs"]:
        exhausted.append("repairs")
    status = "failed" if fatal else "draft" if reasons else "ready"
    return {"status": status, "reasons": reasons, "budget_exhausted": exhausted,
            "document_revision": state["document_revision"], "document_hash": state["document_hash"],
            "artifact_hash": artifact["sha256"] if artifact else None,
            "check_ids": [check["id"] for check in current], "open_blockers": open_findings,
            "enforcement_scope": deepcopy(state["enforcement_scope"])}
