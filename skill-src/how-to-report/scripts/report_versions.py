#!/usr/bin/env python3
"""Explicit local versions and recorded acceptance; never perform content review."""
from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys
import uuid

sys.dont_write_bytecode = True
SCRIPT_DIRECTORY = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIRECTORY))
from write_boundary import require_external_write
from validate_run import Validator, unique_keys, parse_changed, CONTRACT_VERSION
from report_run import MODES, PACKAGE, resolve_path, local_path, nonempty

STATE_VERSION = "0.1"
LOCK = ".report-versions.lock"
HEX = re.compile(r"[0-9a-f]{64}")


def sha(data):
    return hashlib.sha256(data).hexdigest()


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def ref(key):
    return {"id": key[0], "revision": key[1]}


def key(value):
    if (not isinstance(value, dict) or set(value) != {"id", "revision"}
            or not isinstance(value["id"], str) or not value["id"].strip()
            or type(value["revision"]) is not int or value["revision"] < 1):
        raise ValueError("expected exact id/revision reference")
    return value["id"], value["revision"]


def text(value):
    return isinstance(value, str) and bool(value.strip())


def no_links(path):
    """Reject existing reparse/link components before writes, not an OS sandbox."""
    path = Path(os.path.abspath(path))
    for part in reversed((path, *path.parents)):
        if os.path.lexists(part):
            info = part.lstat()
            if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
                raise ValueError(f"write path contains a link/reparse point: {part}")
    return path


class ObservedValidator(Validator):
    """Use the base contract while pinning the files actually observed."""
    def __init__(self, directory):
        super().__init__(directory)
        self.observed = {}

    def capture(self, path):
        path = resolve_path(path, strict=True)
        data = path.read_bytes()
        if path in self.observed and self.observed[path] != data:
            raise ValueError(f"referenced file changed while reading: {path}")
        self.observed[path] = data
        return data

    def load(self, path, where):
        try:
            return json.loads(self.capture(path).decode("utf-8-sig"), object_pairs_hook=unique_keys)
        except (ValueError, UnicodeError) as exc:
            self.error(where, f"invalid or unstable JSON: {exc}")
            return {}

    def file_ref(self, value, where, owned=True):
        path = super().file_ref(value, where, owned)
        if path:
            self.capture(path)
        return path

    def stable(self):
        for path, data in self.observed.items():
            if path.read_bytes() != data:
                raise ValueError(f"observed file changed; inspect and retry: {path}")


class View:
    def __init__(self, directory):
        self.directory = resolve_path(directory, strict=True)
        self.validator = ObservedValidator(self.directory)
        self.base = self.validator.run()
        self.raw = self.validator.observed.get(self.directory / "run.json", b"")
        try:
            self.record = json.loads(self.raw.decode("utf-8-sig"), object_pairs_hook=unique_keys)
        except (ValueError, UnicodeError):
            self.record = {}
        if not isinstance(self.record, dict):
            self.record = {}
        self.errors = []
        if not isinstance(self.record.get("mode"), str) or self.record.get("mode") not in MODES:
            self.errors.append("report_versions supports reporting modes only; audit remains read-only")
        self.state = self.record.get("version_state", {"version": STATE_VERSION, "selections": [], "acceptances": []})
        self.selected = {}
        self.validate_state()
        self.forward = {}
        # Reverse the exact base-validator dependency index; no new edge semantics.
        for dependency, consumers in self.validator.dependencies.items():
            for consumer in consumers:
                self.forward.setdefault(consumer, set()).add(dependency)

    def validate_state(self):
        try:
            state = self.state
            if (not isinstance(state, dict) or set(state) != {"version", "selections", "acceptances"}
                    or state["version"] != STATE_VERSION
                    or not isinstance(state["selections"], list) or not isinstance(state["acceptances"], list)):
                raise ValueError("unsupported version_state shape/version")
            decisions = set()
            for selection in state["selections"]:
                if (not isinstance(selection, dict) or set(selection) != {"decision_id", "target", "reason"}
                        or not text(selection["decision_id"]) or not text(selection["reason"])):
                    raise ValueError("malformed selection decision")
                target = key(selection["target"])
                if target not in self.validator.objects or selection["decision_id"] in decisions:
                    raise ValueError("selection must identify an existing version and unique decision_id")
                decisions.add(selection["decision_id"])
                self.selected[target[0]] = selection
            identities = set()
            for acceptance in state["acceptances"]:
                required = {"id", "target", "check_ids", "reason", "context_sha256", "evidence_sha256"}
                if (not isinstance(acceptance, dict) or not required <= acceptance.keys()
                        or acceptance.keys() - required - {"context_mode"}
                        or ("context_mode" in acceptance and acceptance["context_mode"] != "decision_context_v1")):
                    raise ValueError("malformed acceptance record")
                target = key(acceptance["target"])
                checks = acceptance["check_ids"]
                if (not text(acceptance["id"]) or acceptance["id"] in identities
                        or not text(acceptance["reason"]) or target not in self.validator.objects
                        or self.validator.kinds.get(target[0]) != "artifact"
                        or not isinstance(checks, list) or not checks
                        or any(not text(c) for c in checks) or len(set(checks)) != len(checks)
                        or any(c not in self.validator.checks for c in checks)
                        or any(not isinstance(acceptance[h], str) or not HEX.fullmatch(acceptance[h])
                               for h in ("context_sha256", "evidence_sha256"))):
                    raise ValueError("invalid acceptance identity/target/checks/fingerprint")
                identities.add(acceptance["id"])
        except (ValueError, TypeError, KeyError) as exc:
            self.errors.append("version_state: " + str(exc))

    def context_mode(self):
        return "decision_context_v1" if "decision_context" in self.record else "legacy_notes"

    def closure(self, target, context_mode=None):
        visited, pending = set(), [target]
        if (context_mode or self.context_mode()) == "decision_context_v1" and "decision_context" in self.record:
            pending.append(key(self.record["decision_context"]["target"]))
        while pending:
            item = pending.pop()
            if item not in visited:
                visited.add(item)
                pending.extend(self.forward.get(item, ()))
        return sorted(visited)

    def currentness(self, target, context_mode=None):
        reasons = []
        for item in self.closure(target, context_mode):
            choice = self.selected.get(item[0])
            if choice is None:
                reasons.append({"target": ref(item), "reason": "unselected"})
            elif key(choice["target"]) != item:
                reasons.append({"target": ref(item), "reason": "selected_version_mismatch"})
            obj = self.validator.objects[item][0]
            kind = self.validator.kinds[item[0]]
            if kind.startswith("semantic:") and obj.get("status") in {"stale", "invalidated"}:
                reasons.append({"target": ref(item), "reason": "evidence_" + obj["status"]})
            if kind == "task" and obj["status"] != "completed":
                reasons.append({"target": ref(item), "reason": "task_" + obj["status"]})
        return {"state": "pending" if reasons else "current", "reasons": reasons}

    def file_fingerprint(self, locator, owned=False):
        path = self.validator.file_ref(locator, "acceptance evidence", owned)
        if path is None:
            raise ValueError("acceptance requires accessible local evidence; remote locators are not assessed")
        data = self.validator.capture(path)
        if not data:
            raise ValueError("acceptance evidence must be nonempty")
        return sha(data)

    def evidence(self, target, check_ids, context_mode=None):
        context_mode = context_mode or self.context_mode()
        if context_mode == "decision_context_v1" and "decision_context" not in self.record:
            raise ValueError("acceptance decision context is missing")
        if self.currentness(target, context_mode)["state"] != "current":
            raise ValueError("target or declared dependencies are pending; inspect version selections")
        if self.validator.kinds[target[0]] != "artifact":
            raise ValueError("only an Artifact can be accepted")
        objects = []
        for item in self.closure(target, context_mode):
            obj = self.validator.objects[item][0]
            entry = {"target": ref(item), "object": obj, "selection": self.selected[item[0]]}
            kind = self.validator.kinds[item[0]]
            if kind in {"source", "artifact"}:
                entry["file_sha256"] = self.file_fingerprint(obj["ref"])
            elif "text_ref" in obj:
                entry["file_sha256"] = self.file_fingerprint(obj["text_ref"], True)
            if kind.startswith("semantic:") and obj.get("verification_refs"):
                entry["verification_evidence"] = [
                    {"check": self.validator.checks[check_id],
                     "detail_sha256": self.file_fingerprint(self.validator.checks[check_id]["detail_ref"], True)}
                    for check_id in sorted(obj["verification_refs"])
                ]
            if kind.startswith("semantic:") and (obj.get("verification_dispositions") or any(
                    c.get("status") != "pass" and (c["target"].get("id"), c["target"].get("revision")) == item
                    for c in self.validator.checks.values())):
                # Include unreferenced conflicts and resolution detail, not only selected pass IDs.
                entry["target_checks"] = [
                    {"check": c, "detail_sha256": self.file_fingerprint(c["detail_ref"], True)}
                    for c in sorted(self.validator.checks.values(), key=lambda c: c["id"])
                    if (c["target"].get("id"), c["target"].get("revision")) == item]
                entry["disposition_details"] = [
                    {"disposition": d, "detail_sha256": self.file_fingerprint(d["detail_ref"], True)}
                    for d in obj.get("verification_dispositions", [])]
            objects.append(entry)
        context = {"run_id": self.record["run_id"], "mode": self.record["mode"], "objects": objects}
        if context_mode == "decision_context_v1":
            context["decision_context"] = self.record["decision_context"]
        elif "notes_ref" in self.record:
            context["notes"] = {"ref": self.record["notes_ref"],
                                "sha256": self.file_fingerprint(self.record["notes_ref"], True)}
        matching = [c for c in self.validator.checks.values()
                    if (c["target"].get("id"), c["target"].get("revision")) == target]
        if not matching or any(c["status"] != "pass" for c in matching):
            raise ValueError("all registered checks on the exact target must pass; no silent exclusions")
        matches = {c["id"] for c in matching}
        if not check_ids or len(set(check_ids)) != len(check_ids) or not set(check_ids) <= matches:
            raise ValueError("provide unique existing pass Check IDs for this exact target")
        details = [{"check": c, "detail_sha256": self.file_fingerprint(c["detail_ref"], True)}
                   for c in sorted(matching, key=lambda c: c["id"])]
        context_hash = sha(encoded(context))
        return context_hash, sha(encoded({"context_sha256": context_hash, "checks": details,
                                          "selected_check_ids": sorted(check_ids)}))

    def summary(self):
        result = {"contract_version": CONTRACT_VERSION, "run_directory": str(self.directory),
                  "run_id": self.record.get("run_id") if isinstance(self.record.get("run_id"), str) else None,
                  "mode": self.record.get("mode") if isinstance(self.record.get("mode"), str) else None,
                  "work_status": self.record.get("work_status") if isinstance(self.record.get("work_status"), str) else None, "run_record_sha256": sha(self.raw),
                  "structure_valid": self.base["valid"], "lifecycle_valid": not self.errors,
                  "valid": self.base["valid"] and not self.errors,
                  "errors": self.base["errors"] + self.errors,
                  "scope": "declared_version_choices_and_recorded_acceptance_only",
                  "content_review": "not_performed_by_this_command", "dependency_completeness": "not_assessed",
                  "historical_check_timing": "not_independently_verified",
                  "new_acceptance_context_mode": self.context_mode(),
                  "selections": [], "artifacts": [], "acceptances": []}
        if result["valid"]:
            result["selections"] = [deepcopy(self.selected[i]) for i in sorted(self.selected)]
            states = {}
            for acceptance in self.state["acceptances"]:
                target = key(acceptance["target"])
                try:
                    context, evidence = self.evidence(target, acceptance["check_ids"], acceptance.get("context_mode", "legacy_notes"))
                    current = (context == acceptance["context_sha256"] and evidence == acceptance["evidence_sha256"])
                    reason = None if current else "relevant_evidence_or_choice_changed"
                except ValueError as exc:
                    current, reason = False, str(exc)
                status = "current" if current else "stale"
                result["acceptances"].append({"id": acceptance["id"], "target": ref(target),
                                               "status": status, "reason": reason,
                                               "context_mode": acceptance.get("context_mode", "legacy_notes")})
                states.setdefault(target, []).append(status)
            for artifact in self.record["artifacts"]:
                target = (artifact["id"], artifact["revision"])
                statuses = states.get(target, [])
                result["artifacts"].append({"target": ref(target), "currentness": self.currentness(target),
                    "acceptance_status": "current" if "current" in statuses else "stale" if statuses else "absent"})
        self.validator.stable()
        return result


def inspect(directory):
    return View(directory).summary()


def exclusive(path, data):
    with path.open("xb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())


def mutate(directory, expected, command, *, reason, identity=None, revision=None, kind=None,
           file=None, uses=(), no_dependencies=False, target=None, acceptance_id=None, check_ids=()):
    if not text(reason) or not isinstance(expected, str) or not HEX.fullmatch(expected):
        raise ValueError("reason and expected lowercase run.json SHA-256 are required")
    directory = require_external_write(directory, (PACKAGE,))
    no_links(directory)
    directory = resolve_path(directory, strict=True)
    if directory.is_relative_to(PACKAGE):
        raise ValueError("mutations must be outside the installed Skill")
    no_links(directory / "run.json")
    # Existing managed descendants may themselves be another installed Skill.
    # Preflight every directory we will write before creating even the lock.
    parents = [require_external_write(directory / relative, (PACKAGE,))
               for relative in ("versions", "versions/files", "versions/history")]
    if sha((directory / "run.json").read_bytes()) != expected:
        raise ValueError("stale expected run.json SHA-256; inspect before retry")
    lock_path = no_links(directory / LOCK)
    # Ownership is acquired exclusively; never remove another writer's lock.
    lock = lock_path.open("xb")
    committed = False
    temporary = None
    try:
        with lock:
            lock.write(b"cooperating report_versions writer; do not remove while active\n")
        view = View(directory)
        summary = view.summary()
        if not summary["valid"]:
            raise ValueError("invalid Run or lifecycle: " + "; ".join(summary["errors"]))
        if sha(view.raw) != expected:
            raise ValueError("stale expected run.json SHA-256; inspect before retry")
        record = deepcopy(view.record)
        state = deepcopy(view.state)
        snapshot = None
        operation_id = uuid.uuid4().hex
        if command == "register":
            item = key({"id": identity, "revision": revision})
            if kind not in {"source", "artifact"}:
                raise ValueError("registration kind must be source or artifact")
            if item in view.validator.objects or (identity in view.validator.kinds and view.validator.kinds[identity] != kind):
                raise ValueError("duplicate version or cross-kind object identity")
            uses = list(uses)
            if (no_dependencies and uses) or (kind == "artifact" and not uses and not no_dependencies):
                raise ValueError("Artifact requires explicit --uses or --no-dependencies, never both")
            if len(set(uses)) != len(uses) or any(u == item or u not in view.validator.objects for u in uses):
                raise ValueError("uses must name unique existing versions and cannot refer to self")
            origin = local_path(file)
            captured = view.validator.capture(origin)
            suffix = origin.suffix if re.fullmatch(r"\.[A-Za-z0-9]{1,16}", origin.suffix) else ".bin"
            name = f"versions/files/{operation_id}{suffix}"
            entry = {"id": identity, "revision": revision, "ref": name, "uses": [ref(u) for u in uses],
                     "content_hash": sha(captured), "origin": {"path": str(origin), "filename": origin.name},
                     "version_note": reason, "dependency_declaration": "explicit_none" if no_dependencies else "explicit_uses"}
            record["sources" if kind == "source" else "artifacts"].append(entry)
            snapshot = (name, captured)
            record["work_status"] = "in_progress"
        elif command == "select":
            if target not in view.validator.objects:
                raise ValueError("selection target must be an existing exact object version")
            previous = view.selected.get(target[0])
            if previous is not None and key(previous["target"]) == target:
                raise ValueError("version already selected; no new decision recorded")
            state["selections"].append({"decision_id": operation_id, "target": ref(target), "reason": reason})
            record["work_status"] = "in_progress"
        elif command == "set-context":
            if target not in view.validator.objects or view.validator.kinds.get(target[0]) != "source":
                raise ValueError("decision context must be a registered Source version")
            if view.selected.get(target[0], {}).get("target") != ref(target):
                raise ValueError("select the decision context Source version before binding it")
            obj = view.validator.objects[target][0]
            if not isinstance(obj.get("content_hash"), str) or not HEX.fullmatch(obj["content_hash"]):
                raise ValueError("decision context Source must have its actual content_hash")
            view.file_fingerprint(obj["ref"])
            if record.get("decision_context", {}).get("target") == ref(target):
                raise ValueError("decision context version already bound; register a new revision for changes")
            record["decision_context"] = {"version": "0.1", "target": ref(target),
                                          "decision_id": operation_id, "reason": reason}
            record["work_status"] = "in_progress"
        elif command == "accept":
            if target not in view.validator.objects or not text(acceptance_id):
                raise ValueError("acceptance needs an existing Artifact target and nonempty ID")
            if any(a["id"] == acceptance_id for a in state["acceptances"]):
                raise ValueError("acceptance ID already exists")
            context, evidence = view.evidence(target, check_ids)
            for previous in state["acceptances"]:
                if set(previous["check_ids"]) & set(check_ids) and (
                        previous["context_sha256"] != context or previous["evidence_sha256"] != evidence):
                    raise ValueError("changed acceptance evidence requires fresh actual Check IDs; old pass cannot be reused")
            state["acceptances"].append({"id": acceptance_id, "target": ref(target), "check_ids": list(check_ids),
                                         "reason": reason, "context_sha256": context, "evidence_sha256": evidence})
            if view.context_mode() == "decision_context_v1":
                state["acceptances"][-1]["context_mode"] = "decision_context_v1"
        else:
            raise ValueError("unknown mutation")
        record["version_state"] = state
        # All predictable state errors are rejected before immutable files are written.
        view.validator.stable()
        parents = [no_links(parent) for parent in parents]
        for parent in parents:
            if parent.exists() and not parent.is_dir():
                raise ValueError("managed version path is not a directory")
        for parent in parents:
            parent.mkdir(exist_ok=True)
        if snapshot:
            exclusive(no_links(directory / snapshot[0]), snapshot[1])
        exclusive(no_links(directory / "versions/history" / f"{operation_id}.json"), view.raw)
        temporary = no_links(directory / f".run-{operation_id}.tmp")
        exclusive(temporary, encoded(record))
        view.validator.stable()
        # Cooperative writers are serialized. Arbitrary external writers are unsupported.
        no_links(directory / "run.json")
        os.replace(temporary, directory / "run.json")
        temporary = None
        committed = True
        result = inspect(directory)
        result.update(command=command, committed=True)
        return result
    except (OSError, ValueError) as exc:
        suffix = "state was committed; inspect current record" if committed else "no state commit; any orphan files are retained"
        raise ValueError(f"{exc}; {suffix}") from exc
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()
        lock_path.unlink()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("inspect", "register", "select", "accept", "set-context"):
        sub = commands.add_parser(name)
        sub.add_argument("run_directory", type=Path)
        if name == "inspect":
            continue
        sub.add_argument("--reason", required=True, type=nonempty)
        sub.add_argument("--expect-run-sha256", required=True)
        if name == "register":
            sub.add_argument("--kind", required=True, choices=("source", "artifact"))
            sub.add_argument("--id", required=True, dest="identity", type=nonempty)
            sub.add_argument("--revision", required=True, type=int)
            sub.add_argument("--file", required=True, type=Path)
            group = sub.add_mutually_exclusive_group()
            group.add_argument("--uses", action="append", type=parse_changed, default=[])
            group.add_argument("--no-dependencies", action="store_true")
        else:
            sub.add_argument("--target", required=True, type=parse_changed)
            if name == "accept":
                sub.add_argument("--acceptance-id", required=True, type=nonempty)
                sub.add_argument("--check", action="append", dest="check_ids", required=True, type=nonempty)
    args = vars(parser.parse_args(argv))
    directory, command = args.pop("run_directory"), args.pop("command")
    try:
        if command == "inspect":
            result = inspect(directory)
        else:
            expected = args.pop("expect_run_sha256")
            result = mutate(directory, expected, command, **args)
    except (OSError, ValueError) as exc:
        result = {"valid": False, "errors": [str(exc)], "command": command,
                  "run_directory": str(directory), "content_review": "not_performed_by_this_command"}
        print(json.dumps(result, ensure_ascii=True, indent=2))
        return 2
    print(json.dumps(result, ensure_ascii=True, indent=2))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
