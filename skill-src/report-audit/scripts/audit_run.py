#!/usr/bin/env python3
"""Initialize a fresh audit Run or check its declared structure, offline.

Initialization fingerprints the local target bytes, not their meaning. Checking
never performs the content audit, changes status, or writes validation results.
Run this helper from the built, self-contained report-audit package.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
from urllib.parse import quote

# Importing the shared helper must not write caches into the installed package.
sys.dont_write_bytecode = True
# Python -I omits the script directory; select only this package's sibling.
SCRIPT_DIRECTORY = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIRECTORY))
from write_boundary import require_external_write
from validate_run import CONTRACT_VERSION, unique_keys, validate_run


PACKAGE = SCRIPT_DIRECTORY.parent
TEMPLATES = PACKAGE / "assets" / "audit-run"
SCOPE = "structure_and_declared_references_only"


def nonempty(value):
    if not value.strip():
        raise argparse.ArgumentTypeError("expected a nonempty value")
    return value


def positive_integer(value):
    try:
        number = int(value)
        if number < 1:
            raise ValueError
        return number
    except ValueError as exc:
        raise argparse.ArgumentTypeError("expected a positive integer revision") from exc


def check_audit(directory):
    """Validate this audit directory without changing any Run or target bytes."""
    directory = Path(directory).resolve()
    path = directory / "run.json"
    original = path.read_bytes()
    try:
        record = json.loads(original.decode("utf-8-sig"), object_pairs_hook=unique_keys)
    except (ValueError, UnicodeError):
        record = {}  # The shared validator reports the exact JSON error.
    if not isinstance(record, dict):
        record = {}
    result = validate_run(directory, changed=())
    if record.get("mode") != "audit":
        result["errors"].append("run.json.mode: audit self-check requires mode audit")
    if path.read_bytes() != original:
        result["errors"].append("run.json changed during validation; rerun on a stable record")
    result.update({
        "valid": not result["errors"],
        "audit_directory": str(directory),
        "run_id": record.get("run_id"),
        "mode": record.get("mode"),
        "run_record_sha256": hashlib.sha256(original).hexdigest(),
        "content_audit": "not_performed_by_this_command",
    })
    return result


def initialize(directory, target, run_id, target_id="audit-target", target_revision=1):
    """Create only a new workspace; retain partial files on an I/O failure."""
    requested_directory = require_external_write(directory, (PACKAGE,))
    if os.path.lexists(requested_directory):
        raise FileExistsError(f"refusing to overwrite existing audit workspace: {requested_directory}")
    directory = requested_directory.resolve()
    if str(target).startswith(("\\\\", "//")):
        raise ValueError("target must be a local file, not UNC or device path")
    target = Path(target).resolve(strict=True)
    if directory.is_relative_to(PACKAGE):
        raise ValueError("audit workspace must be outside the installed Skill directory")
    if not target.is_file():
        raise ValueError("--target must name an existing local report file")
    # Read templates and the actual source before creating anything. Ref escaping
    # preserves literal percent signs and '#' in filenames under Run 0.1 parsing.
    record = json.loads((TEMPLATES / "run.json").read_text(encoding="utf-8"),
                        object_pairs_hook=unique_keys)
    notes = (TEMPLATES / "run.md").read_text(encoding="utf-8")
    audit = (TEMPLATES / "audit.md").read_text(encoding="utf-8")
    digest = hashlib.sha256(target.read_bytes()).hexdigest()
    exact_target = {"id": target_id, "revision": target_revision}
    record["run_id"] = run_id
    record["sources"][0].update({
        **exact_target,
        "ref": quote(target.as_posix(), safe="/:"),
        "content_hash": digest,
    })
    artifact = record["artifacts"][0]
    if artifact["id"] == target_id:
        artifact["id"] = "audit-report-output"
    artifact["uses"] = [exact_target.copy()]
    record["checks"][0]["target"] = exact_target.copy()

    # The parent must already exist. Exclusive creation protects old work even
    # if another writer creates the destination after the check above.
    directory.mkdir(exist_ok=False)
    for name, content in (("run.md", notes), ("audit.md", audit),
                          ("run.json", json.dumps(record, ensure_ascii=False, indent=2) + "\n")):
        with (directory / name).open("x", encoding="utf-8", newline="\n") as output:
            output.write(content)
    return check_audit(directory)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    create = commands.add_parser("init", help="create a new audit workspace outside the installed Skill")
    create.add_argument("audit_directory", type=Path)
    create.add_argument("--target", required=True, type=Path, help="existing local report file; never modified")
    create.add_argument("--run-id", required=True, type=nonempty)
    create.add_argument("--target-id", default="audit-target", type=nonempty,
                        help="target's identity in this audit Run (default: audit-target)")
    create.add_argument("--target-revision", default=1, type=positive_integer,
                        help="exact Run-local revision; default 1 does not infer an external version")
    check = commands.add_parser("check", help="read-only validation of the audit's own directory")
    check.add_argument("audit_directory", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "init":
            result = initialize(args.audit_directory, args.target, args.run_id,
                                args.target_id, args.target_revision)
        else:
            result = check_audit(args.audit_directory)
    except (OSError, ValueError) as exc:
        result = {
            "contract_version": CONTRACT_VERSION, "valid": False,
            "errors": [f"Invocation/I/O failure: {exc}"], "affected": [], "scope": SCOPE,
            "audit_directory": str(args.audit_directory.resolve()),
            "content_audit": "not_performed_by_this_command",
        }
        print(json.dumps(result, ensure_ascii=True, indent=2))
        return 2
    result["command"] = args.command
    print(json.dumps(result, ensure_ascii=True, indent=2))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
