#!/usr/bin/env python3
"""Explicit private experience snapshots; no network, inferred consent or rule learning."""
from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from write_boundary import require_external_write
from validate_run import unique_keys

PACKAGE = Path(__file__).resolve().parent.parent
MAX_BYTES = 2 * 1024 * 1024
FIELDS = {"id", "revision", "kind", "status", "context", "question", "action",
          "observations", "mechanism_hypothesis", "applicability", "exclusions",
          "tags", "source_refs", "confirmation_ref"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def nonempty(value):
    return isinstance(value, str) and bool(value.strip()) and len(value) <= 16000


def identity(value):
    return isinstance(value, str) and bool(re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]{0,63}", value))


def sha(data):
    return hashlib.sha256(data).hexdigest()


def private_path(path, new=False):
    path = require_external_write(path, (PACKAGE,))
    require(not any((p / "run.json").exists() for p in path.parents), "experience must be outside Run directories")
    if new:
        require(not os.path.lexists(path) and path.parent.is_dir(), "output must be a new file with an existing private parent")
    else:
        require(path.is_file(), "experience input must be an ordinary local file")
    return path


def references(value, allow_empty=False):
    require(isinstance(value, list) and len(value) <= 100 and (allow_empty or bool(value)), "source_refs require a bounded list of exact references")
    keys = []
    for ref in value:
        require(isinstance(ref, dict) and set(ref) == {"id", "revision", "locator"}, "source reference requires id/revision/locator")
        require(identity(ref["id"]) and type(ref["revision"]) is int and ref["revision"] > 0 and nonempty(ref["locator"]), "invalid exact source reference")
        keys.append((ref["id"], ref["revision"], ref["locator"]))
    require(len(keys) == len(set(keys)), "duplicate source reference")
    return set(keys)


def validate_entry(entry):
    require(isinstance(entry, dict) and set(entry) == FIELDS, "experience entry has missing or unknown fields")
    require(identity(entry["id"]) and type(entry["revision"]) is int and entry["revision"] > 0, "invalid experience identity/revision")
    require(isinstance(entry["kind"], str) and entry["kind"] in {"task_case", "method_candidate"}
            and isinstance(entry["status"], str) and entry["status"] in {"active", "withdrawn"}, "kind/status must identify a case or candidate, never a preference or core rule")
    for key in ("context", "question", "action", "mechanism_hypothesis", "applicability", "exclusions", "confirmation_ref"):
        require(nonempty(entry[key]), f"{key} must be explicitly stated; unknown must not be fabricated")
    tags = entry["tags"]
    require(isinstance(tags, list) and len(tags) <= 30 and all(nonempty(v) and len(v) <= 80 for v in tags), "invalid tags")
    require(len(set(tags)) == len(tags), "duplicate tags")
    refs = references(entry["source_refs"])
    observations = entry["observations"]
    require(isinstance(observations, list) and 1 <= len(observations) <= 50, "state observed or not_observed explicitly")
    for item in observations:
        require(isinstance(item, dict) and set(item) == {"status", "text", "source_refs"}, "observation requires status/text/source_refs")
        require(isinstance(item["status"], str) and item["status"] in {"observed", "not_observed"}
                and nonempty(item["text"]), "invalid observation state")
        linked = references(item["source_refs"], allow_empty=item["status"] == "not_observed")
        require(linked <= refs, "observation source must appear in entry source_refs")


def validate(data):
    require(isinstance(data, dict) and {"experience_version", "store_id", "entries"} <= set(data)
            and not set(data) - {"experience_version", "store_id", "entries", "parent_snapshot_sha256"}, "invalid experience store shape")
    require(data["experience_version"] == "0.1" and identity(data["store_id"]), "unsupported experience version or identity")
    require(isinstance(data["entries"], list) and len(data["entries"]) <= 1000, "at most 1000 historical entries")
    if "parent_snapshot_sha256" in data:
        require(isinstance(data["parent_snapshot_sha256"], str) and bool(re.fullmatch(r"[0-9a-f]{64}", data["parent_snapshot_sha256"])), "invalid parent fingerprint")
    current = {}
    for entry in data["entries"]:
        validate_entry(entry)
        previous = current.get(entry["id"])
        require(entry["revision"] == (previous["revision"] + 1 if previous else 1), "history must append consecutive revisions starting at 1")
        require(not previous or previous["kind"] == entry["kind"], "entry kind cannot change; create a separately linked candidate")
        current[entry["id"]] = entry
    return current


def read(path):
    path = private_path(path)
    require(path.stat().st_size <= MAX_BYTES, "experience exceeds 2 MiB")
    raw = path.read_bytes()
    require(len(raw) <= MAX_BYTES, "experience exceeds 2 MiB")
    data = json.loads(raw.decode("utf-8-sig"), object_pairs_hook=unique_keys)
    current = validate(data)
    require(path.read_bytes() == raw, "experience changed during read")
    return path, raw, data, current


def result(path, raw, data, entries, show=False):
    return {"valid": True, "path": str(path), "sha256": sha(raw), "store_id": data["store_id"],
            "history_entry_count": len(data["entries"]), "entries": entries if show else
            [{k: e[k] for k in ("id", "revision", "kind", "status")} for e in entries],
            "values_disclosed": show, "scope": "explicit_snapshot_structure_only",
            "source_and_confirmation_authenticity": "not_assessed", "semantic_applicability": "not_assessed",
            "automatic_learning": False, "currentness": "caller_selected_snapshot_not_global_latest"}


def write_new(path, data):
    path = private_path(path, new=True)
    current = validate(data)
    raw = (json.dumps(data, ensure_ascii=False, allow_nan=False, indent=2) + "\n").encode("utf-8")
    require(len(raw) <= MAX_BYTES, "experience exceeds 2 MiB")
    with path.open("xb") as stream:
        stream.write(raw)
    return result(path, raw, data, list(current.values()))


def initialize(path, store_id):
    return write_new(path, {"experience_version": "0.1", "store_id": store_id, "entries": []})


def revise(path, entry_path, expected, output):
    path, raw, data, current = read(path)
    require(sha(raw) == expected, "snapshot fingerprint changed; inspect the intended snapshot")
    entry_path = private_path(entry_path)
    require(entry_path.stat().st_size <= 128 * 1024, "entry request exceeds 128 KiB")
    entry_raw = entry_path.read_bytes()
    require(len(entry_raw) <= 128 * 1024, "entry request exceeds 128 KiB")
    change = json.loads(entry_raw.decode("utf-8-sig"), object_pairs_hook=unique_keys)
    require(isinstance(change, dict) and set(change) == FIELDS - {"revision"}, "entry request must omit revision and state all other fields")
    require(identity(change["id"]), "invalid entry id")
    previous = current.get(change["id"])
    entry = {**change, "revision": previous["revision"] + 1 if previous else 1}
    validate_entry(entry)
    revised = deepcopy(data)
    revised["entries"].append(entry)
    revised["parent_snapshot_sha256"] = sha(raw)
    require(path.read_bytes() == raw and entry_path.read_bytes() == entry_raw, "input changed during revision")
    return write_new(output, revised)


def inspect(path, show=False, query=None, tags=(), kind=None, include_withdrawn=False):
    path, raw, data, current = read(path)
    entries = list(current.values())
    if query is not None:
        require(nonempty(query), "query must be nonempty")
        entries = [e for e in entries if query.casefold() in "\n".join(e[k] for k in
                   ("context", "question", "action", "applicability", "exclusions")).casefold()]
    if tags:
        entries = [e for e in entries if set(tags) <= set(e["tags"])]
    if kind:
        entries = [e for e in entries if e["kind"] == kind]
    if not include_withdrawn:
        entries = [e for e in entries if e["status"] == "active"]
    output = result(path, raw, data, entries, show)
    output["retrieval"] = "literal_substring_and_exact_tags_not_semantic_ranking"
    return output


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    init = sub.add_parser("init")
    init.add_argument("path", type=Path); init.add_argument("--store-id", required=True)
    for name in ("inspect", "search"):
        view = sub.add_parser(name)
        view.add_argument("path", type=Path); view.add_argument("--show-values", action="store_true")
        view.add_argument("--include-withdrawn", action="store_true")
        if name == "search":
            view.add_argument("--query"); view.add_argument("--tag", action="append", default=[])
            view.add_argument("--kind", choices=("task_case", "method_candidate"))
    update = sub.add_parser("revise")
    update.add_argument("path", type=Path); update.add_argument("--entry", type=Path, required=True)
    update.add_argument("--expected-sha256", required=True); update.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "init":
            output = initialize(args.path, args.store_id)
        elif args.command == "revise":
            output = revise(args.path, args.entry, args.expected_sha256, args.output)
        else:
            if args.command == "search":
                require(args.query is not None or args.tag or args.kind, "search requires a query, tag or kind")
            output = inspect(args.path, args.show_values, getattr(args, "query", None),
                             getattr(args, "tag", ()), getattr(args, "kind", None), args.include_withdrawn)
    except (OSError, ValueError, UnicodeError, RecursionError) as exc:
        print(json.dumps({"valid": False, "error": str(exc), "partial_output": "if_created_preserved"}, ensure_ascii=True))
        return 2
    print(json.dumps(output, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
