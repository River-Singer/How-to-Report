#!/usr/bin/env python3
"""Read-only evaluation input checks and staged prompt display; no agent execution."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = {"id", "family", "entry", "environment", "turns", "fixtures", "must",
            "must_not", "scored_dimensions", "tags"}
ENTRIES = {"create", "revise", "audit", "analyze"}
ENVIRONMENTS = {"any", "local", "cloud", "minimal"}


def strings(value: object, *, empty: bool = False) -> bool:
    return (isinstance(value, list) and (empty or bool(value))
            and all(isinstance(item, str) and item.strip() for item in value))


def local_file(root: Path, value: object) -> Path:
    if not isinstance(value, str) or not value or "\\" in value:
        raise ValueError("path must be a nonempty relative POSIX string")
    relative = Path(value)
    if relative.is_absolute() or ".." in relative.parts or ":" in value:
        raise ValueError("absolute or parent-escaping path")
    candidate = root / relative
    cursor = root
    for part in relative.parts:
        cursor /= part
        if cursor.is_symlink() or (cursor.exists() and getattr(cursor.lstat(), "st_file_attributes", 0) & 0x400):
            raise ValueError("linked/reparse input is not allowed")
    resolved = candidate.resolve()
    if not resolved.is_relative_to(root.resolve()) or not resolved.is_file():
        raise ValueError("missing or out-of-root input")
    return resolved


def unique_object(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key: " + key)
        result[key] = value
    return result


def read_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_object)


def validate(root: Path) -> tuple[list[dict], list[str]]:
    root = root.resolve()
    issues: list[str] = []
    cases: list[dict] = []
    seen: set[str] = set()
    try:
        metadata = read_json(local_file(root, "dataset.json"))
        if not isinstance(metadata, dict) or metadata.get("status") != "prepared_not_run":
            raise ValueError("dataset status must identify prepared inputs, not model results")
        catalogs = metadata.get("catalogs")
        hashes = metadata.get("files")
        if not isinstance(catalogs, list) or not catalogs or not isinstance(hashes, dict):
            raise ValueError("catalogs/files inventory missing")
        for relative, expected in hashes.items():
            path = local_file(root, relative)
            if not isinstance(expected, str) or not re.fullmatch(r"[0-9a-f]{64}", expected):
                raise ValueError("invalid SHA-256 for " + relative)
            if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
                issues.append("changed input: " + relative)
        expected_data = {p.relative_to(root).as_posix() for p in (root / "fixtures").rglob("*") if p.is_file()}
        if not expected_data.issubset(hashes):
            issues.append("unregistered fixture files")
    except (OSError, ValueError, TypeError) as error:
        return cases, ["dataset: " + str(error)]

    for catalog in catalogs:
        if not isinstance(catalog, dict) or not isinstance(catalog.get("count"), int) or isinstance(catalog.get("count"), bool):
            issues.append("invalid catalog declaration")
            continue
        try:
            relative = catalog.get("path")
            path = local_file(root, relative)
            if relative not in hashes:
                issues.append("catalog is not fingerprinted: " + str(relative))
            lines = path.read_text(encoding="utf-8").splitlines()
        except (OSError, ValueError, TypeError) as error:
            issues.append("catalog: " + str(error))
            continue
        count = 0
        for number, line in enumerate(lines, 1):
            if not line.strip():
                continue
            count += 1
            label = f"{relative}:{number}"
            try:
                case = json.loads(line, object_pairs_hook=unique_object)
                if not isinstance(case, dict) or REQUIRED - case.keys():
                    raise ValueError("case must contain all required fields")
                if case.keys() - REQUIRED - {"turn_fixtures"}:
                    raise ValueError("unknown case field")
                identity = case["id"]
                if not isinstance(identity, str) or not re.fullmatch(r"[A-Z][A-Z0-9-]{1,31}", identity):
                    raise ValueError("invalid case id")
                if identity in seen:
                    raise ValueError("duplicate case id: " + identity)
                seen.add(identity)
                if not isinstance(case["family"], str) or not case["family"].strip():
                    raise ValueError("invalid family")
                if not isinstance(case["entry"], str) or case["entry"] not in ENTRIES:
                    raise ValueError("invalid entry")
                if not isinstance(case["environment"], str) or case["environment"] not in ENVIRONMENTS:
                    raise ValueError("invalid environment")
                for field in ("turns", "must", "must_not", "scored_dimensions", "tags"):
                    if not strings(case[field]):
                        raise ValueError(field + " must be a nonempty string list")
                if not set(case["scored_dimensions"]).issubset({f"Q{i}" for i in range(1, 9)}):
                    raise ValueError("invalid scoring dimension")
                if not strings(case["fixtures"], empty=True):
                    raise ValueError("fixtures must be a string list")
                for fixture in case["fixtures"]:
                    local_file(root, fixture)
                    if fixture not in hashes:
                        raise ValueError("fixture is not fingerprinted: " + fixture)
                stages = case.get("turn_fixtures")
                if stages is not None:
                    if not isinstance(stages, list) or len(stages) != len(case["turns"]):
                        raise ValueError("turn_fixtures must match the turn count")
                    for stage in stages:
                        if not strings(stage, empty=True) or not set(stage).issubset(case["fixtures"]):
                            raise ValueError("stage fixture is outside declared inputs")
                cases.append(case)
            except (ValueError, TypeError, OSError) as error:
                issues.append(label + ": " + str(error))
        if count != catalog["count"]:
            issues.append(str(relative) + ": count differs from dataset declaration")
    return cases, issues


def visible_turn(case: dict, turn: int) -> dict:
    if turn < 1 or turn > len(case["turns"]):
        raise ValueError("requested turn is outside this case")
    fixtures = case.get("turn_fixtures", [case["fixtures"]] * len(case["turns"]))[turn - 1]
    return {"case_id": case["id"], "entry": case["entry"], "environment": case["environment"],
            "turn": turn, "prompt": case["turns"][turn - 1], "fixtures": fixtures,
            "instructions": "Use only this stage and its listed inputs; preserve actual prior output. Do not read catalogs, oracle or future turns. No model is executed by this command."}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--case")
    parser.add_argument("--turn", type=int)
    args = parser.parse_args()
    if (args.case is None) != (args.turn is None):
        parser.error("--case and --turn must be supplied together")
    cases, issues = validate(args.root)
    if issues:
        print(json.dumps({"valid": False, "scope": "evaluation_input_integrity_only", "errors": issues}, ensure_ascii=False, indent=2))
        return 1
    if args.case is not None:
        case = next((item for item in cases if item["id"] == args.case), None)
        if case is None:
            parser.error("unknown case id")
        try:
            output = visible_turn(case, args.turn)
            output["fixture_root"] = str(args.root.resolve())
        except ValueError as error:
            parser.error(str(error))
    else:
        output = {"valid": True, "scope": "evaluation_input_integrity_only", "cases": len(cases),
                  "model_execution": False, "quality": "not_assessed", "writes": "none"}
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
