#!/usr/bin/env python3
"""Read-only validation of declared project dates, states and date differences."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate_run import unique_keys
from report_run import local_path
from schedule_core import VERSION, delta, finish, validate, warnings


def digest(data):
    return hashlib.sha256(data).hexdigest()


def load(path):
    source = local_path(Path(path))
    if source.stat().st_size > 8 * 1024 * 1024:
        raise ValueError("schedule input exceeds 8 MiB")
    raw = source.read_bytes()
    obj = json.loads(raw.decode("utf-8-sig"), object_pairs_hook=unique_keys,
                     parse_constant=lambda _: (_ for _ in ()).throw(ValueError("nonfinite JSON constant")))
    return raw, validate(obj)


def comparisons(spec):
    """Return declared dates without filling missing endpoints or rescheduling."""
    rows = []
    for milestone, items in ((False, spec["tasks"]), (True, spec.get("milestones", []))):
        for item in items:
            actual = item.get("actual_date") if milestone else item.get("actual", {}).get("finish")
            current = (actual or item.get("forecast_date")) if milestone else finish(item)
            baseline = item.get("baseline_date") if milestone else item.get("baseline", {}).get("finish")
            rows.append({"id": item["id"], "kind": "milestone" if milestone else "task",
                         "baseline_date": baseline, "current_finish": current,
                         "current_finish_type": "actual" if actual else "forecast" if current else "unknown",
                         "deviation_calendar_days": delta(item, milestone), "refs": item["refs"]})
    return rows


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    check = sub.add_parser("validate")
    check.add_argument("input", type=Path)
    args = parser.parse_args(argv)
    try:
        raw, spec = load(args.input)
        methods = {name: digest((Path(__file__).parent / name).read_bytes())
                   for name in ("report_schedule.py", "schedule_core.py")}
        result = {"valid": True, "schedule_version": VERSION, "input_sha256": digest(raw),
                  "method_sha256": methods, "as_of": spec["as_of"],
                  "scope": "declared_constraints_and_calendar_day_differences_not_project_truth",
                  "date_comparisons": comparisons(spec), "warnings": warnings(spec),
                  "semantic_validation": "not_run", "run_mutation": "not_performed"}
    except (ValueError, OSError, UnicodeError, RecursionError, TypeError) as exc:
        print(json.dumps({"valid": False, "error": str(exc), "semantic_validation": "not_run"}))
        return 2
    print(json.dumps(result, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
