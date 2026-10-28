#!/usr/bin/env python3
"""Read-only validation of the How-to-Report 0.1 declared workspace contract.

This checks structure, local references, declared checks and consent sequences.
It does not certify facts, authorization, completeness, freshness or visual quality.
"""

from __future__ import annotations

import argparse
from collections import defaultdict, deque
import hashlib
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit

CONTRACT_VERSION = "0.1"
MODES = {"create", "revise", "audit", "analyze-first"}
WORK_STATES = {"in_progress", "completed", "blocked"}
EVIDENCE_STATES = {"proposed", "needs_evidence", "verified", "disputed", "stale", "invalidated"}
CHECK_STATES = {"not_run", "pass", "fail", "not_assessable"}
TASK_STATES = {"planned", "blocked", "ready", "running", "completed", "failed", "cancelled", "stale"}
REMOTE_SCHEMES = {"http", "https", "workspace", "page"}


def unique_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key {key!r}")
        result[key] = value
    return result


class Validator:
    def __init__(self, directory):
        self.directory = Path(directory).resolve()
        self.errors = []
        self.objects = {}
        self.kinds = {}
        self.pending_refs = []
        self.dependencies = defaultdict(set)
        self.nodes = []
        self.tasks = {}
        self.prerequisites = {}
        self.checks = {}
        self.run_id = None

    def error(self, where, message):
        self.errors.append(f"{where}: {message}")

    def string(self, value, where):
        if not isinstance(value, str) or not value.strip():
            self.error(where, "expected a nonempty string")
            return False
        return True

    def integer(self, value, where):
        if type(value) is not int or value < 1:
            self.error(where, "expected a positive integer, not a boolean")
            return False
        return True

    def mapping(self, value, where):
        if not isinstance(value, dict):
            self.error(where, "expected an object")
            return {}
        return value

    def array(self, value, where):
        if not isinstance(value, list):
            self.error(where, "expected an array")
            return []
        return value

    def enum(self, value, choices, where):
        if not isinstance(value, str) or value not in choices:
            self.error(where, "expected one of " + ", ".join(sorted(choices)))

    def load(self, path, where):
        try:
            return json.loads(path.read_text(encoding="utf-8-sig"), object_pairs_hook=unique_keys)
        except (ValueError, UnicodeError) as exc:
            self.error(where, f"invalid JSON: {exc}")
            return {}

    def file_ref(self, value, where, owned=True):
        if not self.string(value, where):
            return None
        # A drive letter is a filesystem path, not a URL scheme.
        is_drive = bool(re.match(r"^[A-Za-z]:[\\/]", value))
        try:
            parsed = urlsplit(value) if not is_drive else None
        except ValueError as exc:
            self.error(where, f"invalid resource locator: {exc}")
            return None
        if parsed and parsed.scheme:
            if not owned and parsed.scheme.lower() in REMOTE_SCHEMES:
                return None  # Locator only; deliberately no network access.
            self.error(where, "expected a local owned file" if owned else "unsupported resource scheme")
            return None
        path_text = unquote(value.split("#", 1)[0])
        path = Path(path_text)
        if owned and (path.is_absolute() or is_drive):
            self.error(where, "owned resources must use Run-relative paths")
            return None
        path = path.resolve() if path.is_absolute() else (self.directory / path).resolve()
        if owned and not path.is_relative_to(self.directory):
            self.error(where, "owned resource escapes the Run directory")
            return None
        if not path.is_file():
            self.error(where, f"local file does not exist: {value}")
            return None
        return path

    def versioned(self, record, where):
        record = self.mapping(record, where)
        good_id = self.string(record.get("id"), where + ".id")
        good_revision = self.integer(record.get("revision"), where + ".revision")
        return (record["id"], record["revision"]) if good_id and good_revision else None

    def reference(self, value, where, consumer=None):
        key = self.versioned(value, where)
        if isinstance(value, dict) and "locator" in value:
            self.string(value["locator"], where + ".locator")
        if key:
            self.pending_refs.append((key, where))
            if consumer:
                self.dependencies[key].add(consumer)
        return key

    def refs(self, record, field, where, consumer=None, required=False):
        values = record.get(field, None if required else [])
        return [self.reference(v, f"{where}.{field}[{i}]", consumer)
                for i, v in enumerate(self.array(values, where + "." + field))]

    def register(self, record, kind, where):
        key = self.versioned(record, where)
        if not key:
            return None
        if key in self.objects:
            self.error(where, f"duplicate object version {key[0]}@{key[1]}")
        else:
            self.objects[key] = (record, where)
        if key[0] in self.kinds and self.kinds[key[0]] != kind:
            self.error(where, f"object {key[0]} changes kind across records")
        self.kinds.setdefault(key[0], kind)
        return key

    def header(self, record, where):
        if record.get("contract_version") != CONTRACT_VERSION:
            self.error(where + ".contract_version", f"unsupported version; expected {CONTRACT_VERSION}")
        if self.string(record.get("run_id"), where + ".run_id") and record["run_id"] != self.run_id:
            self.error(where + ".run_id", "does not match run.json")

    def read_assets(self, run, field):
        for i, value in enumerate(self.array(run.get(field), "run.json." + field)):
            where = f"run.json.{field}[{i}]"
            record = self.mapping(value, where)
            key = self.register(record, "source" if field == "sources" else "artifact", where)
            path = self.file_ref(record.get("ref"), where + ".ref", owned=False)
            self.refs(record, "uses", where, key)
            digest = record.get("content_hash")
            if digest is not None:
                if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-fA-F]{64}", digest):
                    self.error(where + ".content_hash", "expected a SHA-256 hex digest")
                elif path:
                    actual = hashlib.sha256(path.read_bytes()).hexdigest()
                    if actual != digest.lower():
                        self.error(where + ".content_hash", "local file bytes differ from declared hash")

    def read_semantic(self, data):
        data = self.mapping(data, "semantic.json")
        self.header(data, "semantic.json")
        for i, value in enumerate(self.array(data.get("nodes"), "semantic.json.nodes")):
            where = f"semantic.json.nodes[{i}]"
            node = self.mapping(value, where)
            kind = node.get("kind")
            self.string(kind, where + ".kind")
            key = self.register(node, "semantic:" + kind if isinstance(kind, str) else "invalid", where)
            if ("text" in node) == ("text_ref" in node):
                self.error(where, "provide exactly one of text or text_ref")
            if "text" in node:
                self.string(node["text"], where + ".text")
            if "text_ref" in node:
                self.file_ref(node["text_ref"], where + ".text_ref")
            if "status" in node:
                self.enum(node["status"], EVIDENCE_STATES, where + ".status")
            self.refs(node, "uses", where, key)
            for j, value in enumerate(self.array(node.get("links", []), where + ".links")):
                loc = f"{where}.links[{j}]"
                link = self.mapping(value, loc)
                self.string(link.get("type"), loc + ".type")
                self.reference(link.get("target"), loc + ".target")
            verification = self.array(node.get("verification_refs", []), where + ".verification_refs")
            seen_checks = set()
            for j, check_id in enumerate(verification):
                if self.string(check_id, f"{where}.verification_refs[{j}]"):
                    if check_id in seen_checks:
                        self.error(where + ".verification_refs", f"duplicate check ID {check_id}")
                    seen_checks.add(check_id)
            self.nodes.append((key, node, where))

    def read_tasks(self, data):
        data = self.mapping(data, "tasks.json")
        self.header(data, "tasks.json")
        for i, value in enumerate(self.array(data.get("tasks"), "tasks.json.tasks")):
            where = f"tasks.json.tasks[{i}]"
            task = self.mapping(value, where)
            key = self.register(task, "task", where)
            self.string(task.get("objective"), where + ".objective")
            self.string(task.get("completion"), where + ".completion")
            self.enum(task.get("status"), TASK_STATES, where + ".status")
            self.refs(task, "input_refs", where, key, required=True)
            prerequisites = self.refs(task, "prerequisites", where, required=True)
            self.refs(task, "result_refs", where, required=True)
            if key:
                self.tasks[key] = where
                self.prerequisites[key] = {p for p in prerequisites if p}

    def read_checks(self, run):
        for i, value in enumerate(self.array(run.get("checks"), "run.json.checks")):
            where = f"run.json.checks[{i}]"
            check = self.mapping(value, where)
            check_id = check.get("id")
            if self.string(check_id, where + ".id"):
                if check_id in self.checks:
                    self.error(where, f"duplicate check ID {check_id}")
                else:
                    self.checks[check_id] = check
            self.reference(check.get("target"), where + ".target")
            self.enum(check.get("status"), CHECK_STATES, where + ".status")
            detail = self.file_ref(check.get("detail_ref"), where + ".detail_ref")
            if check.get("status") == "pass":
                self.string(check.get("method"), where + ".method")
                self.string(check.get("scope"), where + ".scope")
                if detail and detail.stat().st_size == 0:
                    self.error(where + ".detail_ref", "pass needs nonempty supporting detail")

    def check_verifications(self):
        for key, node, where in self.nodes:
            refs = node.get("verification_refs", [])
            if not isinstance(refs, list):
                continue
            matched = False
            for check_id in refs:
                if not isinstance(check_id, str):
                    continue
                check = self.checks.get(check_id)
                if check is None:
                    self.error(where + ".verification_refs", f"unknown check {check_id}")
                    continue
                target = check.get("target")
                same_target = isinstance(target, dict) and key and target.get("id") == key[0] and type(target.get("revision")) is int and target["revision"] == key[1]
                if same_target and check.get("status") == "pass":
                    matched = True
            if node.get("status") == "verified" and not matched:
                self.error(where + ".status", "verified needs a matching pass check for this exact object version")

    def check_tasks(self):
        degree = {key: 0 for key in self.tasks}
        children = defaultdict(set)
        for key, parents in self.prerequisites.items():
            for parent in parents:
                if parent not in self.tasks:
                    self.error(self.tasks[key] + ".prerequisites", f"not a task version: {parent[0]}@{parent[1]}")
                    continue
                degree[key] += 1
                children[parent].add(key)
        ready = deque(key for key, n in degree.items() if n == 0)
        visited = 0
        while ready:
            key = ready.popleft()
            visited += 1
            for child in children[key]:
                degree[child] -= 1
                if degree[child] == 0:
                    ready.append(child)
        if visited != len(degree):
            self.error("tasks.json.prerequisites", "execution prerequisite cycle detected")

    def read_events(self, path):
        seen = set()
        previous = 0
        grants = {}
        try:
            lines = path.read_text(encoding="utf-8-sig").splitlines()
        except UnicodeError as exc:
            self.error("events.jsonl", f"invalid UTF-8: {exc}")
            return
        for line_no, line in enumerate(lines, 1):
            if not line.strip():
                continue
            where = f"events.jsonl:{line_no}"
            try:
                event = self.mapping(json.loads(line, object_pairs_hook=unique_keys), where)
            except ValueError as exc:
                self.error(where, f"invalid JSON: {exc}")
                continue
            event_id = event.get("event_id")
            if self.string(event_id, where + ".event_id"):
                if event_id in seen:
                    self.error(where, f"duplicate event ID {event_id}")
                seen.add(event_id)
            sequence = event.get("sequence")
            if self.integer(sequence, where + ".sequence"):
                if sequence <= previous:
                    self.error(where + ".sequence", "must strictly increase in file order")
                previous = max(previous, sequence)
            event_type = event.get("type")
            if not self.string(event_type, where + ".type") or event_type not in {"consent_decision", "resource_read"}:
                continue
            scope = event.get("scope_id")
            if not self.string(scope, where + ".scope_id"):
                continue
            if event_type == "consent_decision":
                decision = event.get("decision")
                self.enum(decision, {"grant", "deny", "revoke"}, where + ".decision")
                user_ref_valid = self.string(event.get("user_message_ref"), where + ".user_message_ref")
                if decision == "grant":
                    scope_valid = self.string(event.get("scope"), where + ".scope")
                    if user_ref_valid and scope_valid and isinstance(event_id, str):
                        grants[scope] = event_id
                elif isinstance(decision, str) and decision in {"deny", "revoke"}:
                    grants.pop(scope, None)
            else:
                self.string(event.get("resource_ref"), where + ".resource_ref")
                consent_id = event.get("consent_event_id")
                self.string(consent_id, where + ".consent_event_id")
                if scope not in grants or consent_id != grants.get(scope):
                    self.error(where, "resource_read requires the current active grant for this scope")

    def run(self, changed=()):
        run = self.mapping(self.load(self.directory / "run.json", "run.json"), "run.json")
        self.run_id = run.get("run_id")
        self.header(run, "run.json")
        self.enum(run.get("mode"), MODES, "run.json.mode")
        self.enum(run.get("work_status"), WORK_STATES, "run.json.work_status")
        self.read_assets(run, "sources")
        self.read_assets(run, "artifacts")
        for field, reader in [("semantic_ref", self.read_semantic), ("tasks_ref", self.read_tasks)]:
            if field in run:
                path = self.file_ref(run[field], "run.json." + field)
                if path:
                    reader(self.load(path, field))
        if "notes_ref" in run:
            self.file_ref(run["notes_ref"], "run.json.notes_ref")
        self.read_checks(run)
        if "events_ref" in run:
            path = self.file_ref(run["events_ref"], "run.json.events_ref")
            if path:
                self.read_events(path)
        for key, where in self.pending_refs:
            if key not in self.objects:
                self.error(where, f"unknown exact object version {key[0]}@{key[1]}")
        self.check_verifications()
        self.check_tasks()
        roots = set(changed)
        for key in roots:
            if key not in self.objects:
                self.error("--changed", f"unknown exact object version {key[0]}@{key[1]}")
        seen = set(roots)
        queue = deque(roots)
        while queue:
            for consumer in self.dependencies.get(queue.popleft(), ()):
                if consumer not in seen:
                    seen.add(consumer)
                    queue.append(consumer)
        return {"contract_version": CONTRACT_VERSION, "valid": not self.errors,
                "errors": self.errors,
                "affected": [{"id": key[0], "revision": key[1]} for key in sorted(seen - roots)],
                "scope": "structure_and_declared_references_only"}


def parse_changed(value):
    try:
        identity, revision = value.rsplit("@", 1)
        if not identity.strip() or not re.fullmatch(r"[1-9][0-9]*", revision):
            raise ValueError
        return identity, int(revision)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("expected <id>@<positive-integer-revision>") from exc


def validate_run(directory, changed=()):
    """Return declared consistency and impact; never modify any input."""
    return Validator(directory).run(changed)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_directory", type=Path)
    parser.add_argument("--changed", action="append", default=[], type=parse_changed,
                        help="repeatable old exact version that changed, e.g. s1@1 when replaced by s1@2; an empty result for s1@2 does not validate old consumers")
    args = parser.parse_args(argv)
    try:
        result = validate_run(args.run_directory, args.changed)
    except OSError as exc:
        result = {"contract_version": CONTRACT_VERSION, "valid": False,
                  "errors": [f"I/O failure: {exc}"], "affected": [],
                  "scope": "structure_and_declared_references_only"}
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
