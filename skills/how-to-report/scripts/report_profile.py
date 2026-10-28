#!/usr/bin/env python3
"""Explicit private profile snapshots; never infer preferences or authenticate consent."""
from __future__ import annotations

import argparse
from copy import deepcopy
import json
import os
from pathlib import Path
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from report_run import PACKAGE, resolve_path, require_local, local_path, nonempty
from report_versions import sha, encoded, no_links, text
from write_boundary import require_external_write
from validate_run import unique_keys

ENTRY_FIELDS = {"id", "revision", "type", "value", "scope", "confirmation_ref"}


def private_path(path, new=False):
    path = require_external_write(path, (PACKAGE,))
    no_links(path)
    path = resolve_path(path, strict=not new)
    if path.is_relative_to(PACKAGE):
        raise ValueError("profile must be outside the installed Skill")
    if any((parent / "run.json").exists() or (parent / "bundle-manifest.json").exists()
           or (parent / "SKILL.md").exists() for parent in path.parents):
        raise ValueError("profile must be outside Run and installed Skill directories")
    if new and (os.path.lexists(path) or not path.parent.is_dir()):
        raise ValueError("profile output must be a new file with an existing private parent")
    if not new and not path.is_file():
        raise ValueError("profile must be an ordinary local file")
    return path


def validate_entry(entry):
    if not isinstance(entry, dict) or set(entry) != ENTRY_FIELDS:
        raise ValueError("entry requires id/revision/type/value/scope/confirmation_ref")
    if not all(text(entry[x]) for x in ENTRY_FIELDS - {"revision"}):
        raise ValueError("entry fields, including confirmation_ref and scope, must be nonempty")
    if entry["type"] not in {"preference", "experience"} or type(entry["revision"]) is not int or entry["revision"] < 1:
        raise ValueError("entry requires preference/experience and positive integer revision")


def validate_profile(profile):
    if (not isinstance(profile, dict) or not {"contract_version", "profile_id", "entries"}.issubset(profile)
            or set(profile) - {"contract_version", "profile_id", "entries", "parent_snapshot_sha256"}
            or profile["contract_version"] != "0.1" or not text(profile["profile_id"])
            or not isinstance(profile["entries"], list) or len(profile["entries"]) > 1000):
        raise ValueError("unsupported profile contract/shape or more than 1000 historical entries")
    if "parent_snapshot_sha256" in profile:
        import re
        if not isinstance(profile["parent_snapshot_sha256"], str) or not re.fullmatch(r"[0-9a-f]{64}", profile["parent_snapshot_sha256"]):
            raise ValueError("invalid parent snapshot fingerprint")
    current = {}
    for entry in profile["entries"]:
        validate_entry(entry)
        previous = current.get(entry["id"])
        if entry["revision"] != (previous["revision"] + 1 if previous else 1):
            raise ValueError("entry history must start at 1 and append consecutive revisions")
        if previous and previous["type"] != entry["type"]:
            raise ValueError("entry identity cannot change type")
        current[entry["id"]] = entry
    return current


def read_profile(path):
    path = private_path(path)
    data = path.read_bytes()
    if len(data) > 1024 * 1024:
        raise ValueError("profile exceeds 1 MiB")
    profile = json.loads(data.decode("utf-8-sig"), object_pairs_hook=unique_keys)
    current = validate_profile(profile)
    if path.read_bytes() != data:
        raise ValueError("profile changed during reading; inspect again")
    return path, data, profile, current


def summary(path, data, profile, current, show_values=False):
    return {"valid": True, "profile_path": str(path), "profile_sha256": sha(data),
            "profile_id": profile["profile_id"], "history_entry_count": len(profile["entries"]),
            "current_entries": list(current.values()) if show_values else
                [{k: entry[k] for k in ("id", "revision", "type")} for entry in current.values()],
            "values_disclosed": show_values, "confirmation_authenticity": "not_assessed",
            "scope": "explicit_snapshot_structure_only",
            "current_task_instruction_priority": "current instructions override stored entries; no automatic profile update",
            "snapshot_currentness": "caller-selected snapshot; no global latest-version discovery"}


def inspect(path, show_values=False):
    return summary(*read_profile(path), show_values=show_values)


def write_new(path, profile):
    path = private_path(path, new=True)
    current = validate_profile(profile)
    data = encoded(profile)
    if len(data) > 1024 * 1024:
        raise ValueError("profile exceeds 1 MiB")
    with path.open("xb") as handle:
        handle.write(data)
    return summary(path, data, profile, current)


def initialize(path, identity):
    if not text(identity):
        raise ValueError("profile_id must be nonempty")
    return write_new(path, {"contract_version": "0.1", "profile_id": identity, "entries": []})


def revise(path, entry_file, expected, output):
    path, raw, profile, current = read_profile(path)
    if sha(raw) != expected:
        raise ValueError("profile hash changed; inspect and confirm applicable snapshot before retry")
    entry_file = local_path(entry_file)
    change_raw = entry_file.read_bytes()
    if len(change_raw) > 65536:
        raise ValueError("entry request exceeds 64 KiB")
    change = json.loads(change_raw.decode("utf-8-sig"), object_pairs_hook=unique_keys)
    if not isinstance(change, dict) or set(change) != ENTRY_FIELDS - {"revision"}:
        raise ValueError("entry request requires id/type/value/scope/confirmation_ref, no inferred revision")
    if not text(change["id"]):
        raise ValueError("entry id must be nonempty")
    previous = current.get(change["id"])
    entry = {**change, "revision": previous["revision"] + 1 if previous else 1}
    validate_entry(entry)
    revised = deepcopy(profile)
    revised["entries"].append(entry)
    revised["parent_snapshot_sha256"] = sha(raw)
    if path.read_bytes() != raw or entry_file.read_bytes() != change_raw:
        raise ValueError("profile or change request changed during revision")
    return write_new(output, revised)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    init = sub.add_parser("init")
    init.add_argument("profile", type=Path)
    init.add_argument("--profile-id", required=True, type=nonempty)
    view = sub.add_parser("inspect")
    view.add_argument("profile", type=Path)
    view.add_argument("--show-values", action="store_true")
    update = sub.add_parser("revise")
    update.add_argument("profile", type=Path)
    update.add_argument("--entry", required=True, type=Path)
    update.add_argument("--expected-sha256", required=True)
    update.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "init":
            result = initialize(args.profile, args.profile_id)
        elif args.command == "inspect":
            result = inspect(args.profile, args.show_values)
        else:
            result = revise(args.profile, args.entry, args.expected_sha256, args.output)
    except (OSError, ValueError) as exc:
        print(json.dumps({"valid": False, "scope": "profile_structure_only", "error": str(exc)}, ensure_ascii=True))
        return 2
    print(json.dumps(result, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
