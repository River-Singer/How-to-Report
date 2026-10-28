#!/usr/bin/env python3
"""Validate explicit project dates or render selected views through the shared Deck."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
import tempfile

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate_run import unique_keys
from report_run import local_path
from write_boundary import require_external_write
from schedule_core import VERSION, VIEWS, validate, to_plan, warnings

PACKAGE = Path(__file__).resolve().parent.parent


def digest(data):
    return hashlib.sha256(data).hexdigest()


def encode(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode("utf-8")


def load(path):
    source = local_path(Path(path))
    if source.stat().st_size > 8 * 1024 * 1024:
        raise ValueError("schedule input exceeds 8 MiB")
    raw = source.read_bytes()
    obj = json.loads(raw.decode("utf-8-sig"), object_pairs_hook=unique_keys,
                     parse_constant=lambda _: (_ for _ in ()).throw(ValueError("nonfinite JSON constant")))
    return raw, validate(obj)


def render(source, directory, views, canvas=None):
    import report_html
    raw, spec = load(source)
    destination = require_external_write(Path(directory), known_roots=(PACKAGE,))
    # All validation/known capability errors precede destination creation.
    plan = report_html.validate(to_plan(spec, views, canvas))
    report_html.output_path(destination)
    with tempfile.TemporaryDirectory(prefix="how-to-report-schedule-") as tmp:
        plan_path = Path(tmp) / "plan.json"
        require_external_write(plan_path, known_roots=(PACKAGE,))
        plan_path.write_bytes(encode(plan))
        result = report_html.render(plan_path, destination)
    with (destination / "schedule-input.json").open("xb") as out:
        out.write(raw)
    files = {p.name: digest(p.read_bytes()) for p in destination.iterdir() if p.is_file()}
    methods = {name: digest((Path(__file__).parent / name).read_bytes()) for name in ("report_schedule.py", "schedule_core.py", "schedule_render.py")}
    receipt = {"schedule_version": VERSION, "input_sha256": digest(raw), "views": views, "files": files,
               "method_sha256": methods, "calendar": "natural_days_inclusive_finish_end_of_day",
               "source_refs": spec["refs"], "warnings": warnings(spec), "scope": "declared_dates_and_deterministic_graphics_not_project_truth",
               "browser_validation": "not_run", "semantic_validation": "not_run", "run_mutation": "not_performed"}
    with (destination / "schedule-receipt.json").open("xb") as out:
        out.write(encode(receipt))
    return {"valid": True, "output_directory": str(destination), "page_count": result["page_count"], **receipt}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    check = sub.add_parser("validate"); check.add_argument("input", type=Path)
    build = sub.add_parser("render"); build.add_argument("input", type=Path)
    build.add_argument("--views", required=True, help=",".join(VIEWS))
    build.add_argument("--output", required=True, type=Path)
    build.add_argument("--width", type=int, default=1600); build.add_argument("--height", type=int, default=900)
    args = parser.parse_args(argv)
    try:
        if args.command == "validate":
            raw, spec = load(args.input)
            result = {"valid": True, "schedule_version": VERSION, "input_sha256": digest(raw),
                      "scope": "declared_schedule_constraints_only", "warnings": warnings(spec), "semantic_validation": "not_run"}
        else:
            result = render(args.input, args.output, args.views.split(","), {"width": args.width, "height": args.height})
    except (ValueError, OSError, UnicodeError, RecursionError, TypeError) as exc:
        print(json.dumps({"valid": False, "error": str(exc), "partial_output": "if_created_preserved", "semantic_validation": "not_run"}))
        return 2
    print(json.dumps(result, ensure_ascii=True, indent=2)); return 0


if __name__ == "__main__":
    sys.exit(main())
