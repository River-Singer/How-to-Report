#!/usr/bin/env python3
"""Initialize or inspect a local reporting Run; never generate or approve content."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True
SCRIPT_DIRECTORY = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIRECTORY))
from validate_run import CONTRACT_VERSION, unique_keys, validate_run

PACKAGE = SCRIPT_DIRECTORY.parent
TEMPLATES = PACKAGE / "assets" / "report-run"
MODES = {"create", "revise", "analyze-first"}
SCOPE = "structure_and_declared_references_only"
RECORD_REFS = ("notes_ref", "semantic_ref", "tasks_ref", "events_ref")
ASSET_FIELDS = ("id", "revision", "ref", "role", "status", "content_hash")


def nonempty(value):
    if not value.strip():
        raise argparse.ArgumentTypeError("expected a nonempty value")
    return value


def metadata(record, fields):
    """Project metadata only; malformed values do not become summary claims."""
    if not isinstance(record, dict):
        return None
    return {field: value if isinstance(value, str) or type(value) is int else None
            for field in fields if field in record for value in [record[field]]}


def summarize(record, field):
    values = record.get(field)
    if not isinstance(values, list):
        return None
    if field != "checks":
        return [metadata(value, ASSET_FIELDS) for value in values]
    result = []
    for value in values:
        item = metadata(value, ("id", "status", "detail_ref"))
        if item is not None and "target" in value:
            item["target"] = metadata(value["target"], ("id", "revision"))
        result.append(item)
    return result


def inspect_run(directory):
    directory = resolve_path(directory, strict=True)
    record_path = directory / "run.json"
    original_bytes = record_path.read_bytes()
    try:
        record = json.loads(original_bytes.decode("utf-8-sig"), object_pairs_hook=unique_keys)
    except (ValueError, UnicodeError):
        record = {}  # The shared validator provides the precise parse error.
    if not isinstance(record, dict):
        record = {}
    result = validate_run(directory, changed=())
    mode = record.get("mode")
    if not isinstance(mode, str) or mode not in MODES:
        result["errors"].append("run.json.mode: report_run supports create, revise or analyze-first; use audit_run for audit")
    if record_path.read_bytes() != original_bytes:
        result["errors"].append("run.json changed during inspection; retry against a stable record")
    result.update({
        "valid": not result["errors"],
        "run_directory": str(directory),
        "run_id": metadata(record, ("run_id",)).get("run_id"),
        "mode": metadata(record, ("mode",)).get("mode"),
        "work_status": metadata(record, ("work_status",)).get("work_status"),
        "run_record_sha256": hashlib.sha256(original_bytes).hexdigest(),
        "sources": summarize(record, "sources"),
        "artifacts": summarize(record, "artifacts"),
        "checks": summarize(record, "checks"),
        "record_refs": metadata(record, RECORD_REFS),
        "content_work": "not_performed_by_this_command",
        "origin_currentness": "not_assessed",
    })
    if "version_state" in record:
        from report_versions import inspect as inspect_versions
        lifecycle = inspect_versions(directory)
        result["version_lifecycle"] = lifecycle
        result["structure_valid"] = result["valid"]
        result["lifecycle_valid"] = lifecycle["lifecycle_valid"]
        result["errors"].extend(lifecycle["errors"])
        if lifecycle["run_record_sha256"] != result["run_record_sha256"]:
            result["errors"].append("run.json changed between structure and lifecycle inspections")
        result["valid"] = not result["errors"]
    return result


def require_local(path):
    # UNC/device paths can perform network or device I/O, not local file capture.
    if str(path).startswith(("\\\\", "//")):
        raise ValueError("expected a local filesystem path, not a UNC or device path")


def resolve_path(path, strict=False):
    require_local(path)
    try:
        resolved = path.resolve(strict=strict)
    except RuntimeError as exc:  # Python 3.10-3.12 report symlink loops this way.
        raise ValueError(f"cannot resolve path: {path}") from exc
    require_local(resolved)
    return resolved


def local_path(path):
    resolved = resolve_path(path, strict=True)
    if not resolved.is_file():
        raise ValueError(f"input is not a regular file: {path}")
    return resolved


def initialize(directory, run_id, mode, sources=(), target=None):
    if mode not in MODES:
        raise ValueError("unsupported reporting mode")
    if not run_id.strip():
        raise ValueError("run_id must be nonempty")
    if mode == "revise" and target is None:
        raise ValueError("revise requires --target")
    if mode != "revise" and target is not None:
        raise ValueError("--target is only valid for revise")
    require_local(directory)
    if os.path.lexists(directory):
        raise ValueError("Run destination already exists; inspect it or choose a new directory")
    directory = resolve_path(directory)
    if directory.is_relative_to(PACKAGE):
        raise ValueError("Run destination must be outside the installed Skill")
    if not directory.parent.is_dir():
        raise ValueError("Run destination parent must be an existing directory")

    supplied = [(f"source-{index:03d}", "supporting_material", path)
                for index, path in enumerate(sources, 1)]
    if target is not None:
        supplied.insert(0, ("revision-target", "revision_target", target))
    resolved_inputs = []
    seen = set()
    for identity, role, path in supplied:
        origin = local_path(path)
        if origin in seen:
            raise ValueError(f"duplicate resolved input path: {path}")
        seen.add(origin)
        resolved_inputs.append((identity, role, origin))

    record = json.loads((TEMPLATES / "run.json").read_text(encoding="utf-8-sig"), object_pairs_hook=unique_keys)
    expected_keys = {"contract_version", "run_id", "mode", "work_status", "notes_ref", "sources", "artifacts", "checks"}
    if not isinstance(record, dict) or set(record) != expected_keys or record.get("contract_version") != CONTRACT_VERSION:
        raise ValueError("report-run template has an unsupported structure or contract")
    notes = (TEMPLATES / "run.md").read_bytes()
    record.update(run_id=run_id, mode=mode, work_status="in_progress", notes_ref="run.md", sources=[], artifacts=[], checks=[])
    snapshots = []
    for identity, role, origin in resolved_inputs:
        suffix = origin.suffix
        if not re.fullmatch(r"\.[A-Za-z0-9]{1,16}", suffix):
            suffix = ".bin"
        ref = f"inputs/{identity}{suffix}"
        captured = origin.read_bytes()
        snapshots.append((ref, captured))
        record["sources"].append({
            "id": identity, "revision": 1, "ref": ref, "role": role,
            "content_hash": hashlib.sha256(captured).hexdigest(),
            "origin": {"path": str(origin), "filename": origin.name},
            "scope": "Explicit local input snapshot; registration does not establish reading, authenticity or content verification.",
            "version_note": "revision=1 is this Run's local registration, not an inferred external or current business version.",
        })
    encoded_record = (json.dumps(record, ensure_ascii=False, indent=2) + "\n").encode("utf-8")

    # All predictable input/template errors are checked before the first write.
    # Exclusive creation never overwrites; an I/O failure leaves partial work intact.
    directory.mkdir(exist_ok=False)
    if snapshots:
        (directory / "inputs").mkdir(exist_ok=False)
    for ref, captured in snapshots:
        with (directory / ref).open("xb") as output:
            output.write(captured)
    for name, captured in (("run.md", notes), ("run.json", encoded_record)):
        with (directory / name).open("xb") as output:
            output.write(captured)
    return inspect_run(directory)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    init = commands.add_parser("init", help="create a new Run with explicit local input snapshots")
    init.add_argument("run_directory", type=Path)
    init.add_argument("--run-id", required=True, type=nonempty)
    init.add_argument("--mode", required=True, choices=sorted(MODES))
    init.add_argument("--source", action="append", default=[], type=Path)
    init.add_argument("--target", type=Path)
    inspect = commands.add_parser("inspect", help="read recorded metadata and validate declared references")
    inspect.add_argument("run_directory", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "init":
            result = initialize(args.run_directory, args.run_id, args.mode, args.source, args.target)
        else:
            result = inspect_run(args.run_directory)
    except (OSError, ValueError) as exc:
        result = {"contract_version": CONTRACT_VERSION, "valid": False,
                  "errors": [f"Invocation or I/O failure: {exc}"], "affected": [], "scope": SCOPE,
                  "run_directory": str(args.run_directory), "command": args.command,
                  "content_work": "not_performed_by_this_command", "origin_currentness": "not_assessed"}
        print(json.dumps(result, ensure_ascii=True, indent=2))
        return 2
    result["command"] = args.command
    print(json.dumps(result, ensure_ascii=True, indent=2))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
