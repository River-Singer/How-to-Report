#!/usr/bin/env python3
"""Execute a bounded, explicitly defined CSV calculation offline; not causal analysis."""
from __future__ import annotations

import argparse
import csv
from decimal import Decimal, localcontext, ROUND_HALF_UP, ROUND_HALF_EVEN
import io
import json
import os
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from report_run import PACKAGE, local_path, resolve_path, require_local
from report_versions import sha, encoded, no_links, key, text
from write_boundary import require_external_write
from validate_run import unique_keys

OPERATIONS = {
    "sum": {"value"}, "product_sum": {"price", "quantity"},
    "ratio_of_sums": {"numerator", "denominator"},
    "price_quantity_decomposition": {"base_price", "base_quantity", "current_price", "current_quantity"},
}
ROUNDING = {"half_up": ROUND_HALF_UP, "half_even": ROUND_HALF_EVEN}
CONTEXT = {"measure", "unit", "grain", "period", "population", "filters", "limitations"}
NUMBER = re.compile(r"-?(?:0|[1-9][0-9]{0,11})(?:\.[0-9]{1,12})?\Z")
MAX_BYTES = 4 * 1024 * 1024


def load_json(data):
    return json.loads(data.decode("utf-8-sig"), object_pairs_hook=unique_keys)


def validate_spec(spec):
    required = {"calculation_version", "id", "operation", "source", "context", "columns", "column_units", "key_columns",
                "decimal_places", "rounding", "missing_policy", "definition_ref"}
    if not isinstance(spec, dict) or set(spec) != required or spec["calculation_version"] != "0.1":
        raise ValueError("unsupported calculation spec shape/version")
    if not text(spec["id"]) or not text(spec["definition_ref"]):
        raise ValueError("id and explicit approved definition_ref are required")
    operation = spec["operation"]
    if not isinstance(operation, str) or operation not in OPERATIONS:
        raise ValueError("unsupported operation; arbitrary expressions are not accepted")
    source = spec["source"]
    if not isinstance(source, dict) or set(source) != {"id", "revision", "ref", "sha256"}:
        raise ValueError("source requires id/revision/ref/sha256")
    key({"id": source["id"], "revision": source["revision"]})
    if not text(source["ref"]) or not isinstance(source["sha256"], str) or not re.fullmatch(r"[0-9a-f]{64}", source["sha256"]):
        raise ValueError("source requires explicit local ref and SHA-256")
    if not isinstance(spec["context"], dict) or set(spec["context"]) != CONTEXT or not all(text(v) for v in spec["context"].values()):
        raise ValueError("context requires measure/unit/grain/period/population/filters/limitations")
    columns = spec["columns"]
    if not isinstance(columns, dict) or set(columns) != OPERATIONS[operation] or not all(text(v) for v in columns.values()):
        raise ValueError("columns must explicitly map this operation's roles")
    units = spec["column_units"]
    if not isinstance(units, dict) or set(units) != set(columns) or not all(text(v) for v in units.values()):
        raise ValueError("column_units must explicitly declare each input role's unit")
    keys = spec["key_columns"]
    if not isinstance(keys, list) or not keys or not all(text(v) for v in keys) or len(set(keys)) != len(keys):
        raise ValueError("key_columns must be a nonempty distinct column list")
    if type(spec["decimal_places"]) is not int or not 0 <= spec["decimal_places"] <= 8:
        raise ValueError("decimal_places must be an integer from 0 to 8")
    if not isinstance(spec["rounding"], str) or spec["rounding"] not in ROUNDING or spec["missing_policy"] != "error":
        raise ValueError("explicit half_up/half_even rounding and missing_policy=error required")


def read_rows(data, spec):
    if len(data) > MAX_BYTES:
        raise ValueError("CSV exceeds 4 MiB bounded adapter limit")
    reader = csv.DictReader(io.StringIO(data.decode("utf-8-sig"), newline=""), strict=True)
    headers = reader.fieldnames
    if not headers or len(headers) != len(set(headers)) or not all(text(x) for x in headers):
        raise ValueError("CSV headers must be nonempty and unique")
    if not set(spec["columns"].values()).union(spec["key_columns"]).issubset(headers):
        raise ValueError("required CSV column missing")
    seen, rows = set(), []
    for number, row in enumerate(reader, 2):
        if number > 10001:
            raise ValueError("CSV exceeds 10000 rows")
        if None in row or any(v is None for v in row.values()):
            raise ValueError(f"row {number}: inconsistent CSV width")
        identity = tuple(row[k].strip() for k in spec["key_columns"])
        if not all(identity) or identity in seen:
            raise ValueError(f"row {number}: missing or duplicate declared grain key")
        seen.add(identity)
        values = {}
        for role, column in spec["columns"].items():
            value = row[column].strip()
            if not NUMBER.fullmatch(value):
                raise ValueError(f"row {number}: missing/invalid/out-of-range decimal in {role}")
            values[role] = Decimal(value)
        rows.append(values)
    if not rows:
        raise ValueError("CSV has no observations; empty is not zero")
    return rows


def compute(rows, spec):
    # 24-digit inputs, 10000 rows, and products need < 60 significant digits.
    # 80 digits preserves finite sums/products; ratios may be repeating.
    with localcontext() as ctx:
        ctx.prec = 80
        ctx.rounding = ROUNDING[spec["rounding"]]
        total = lambda role: sum((r[role] for r in rows), Decimal(0))
        operation = spec["operation"]
        if operation == "sum":
            values = {"total": total("value")}
            formula = "total = sum(value)"
        elif operation == "product_sum":
            values = {"total": sum((r["price"] * r["quantity"] for r in rows), Decimal(0))}
            formula = "total = sum(price * quantity)"
        elif operation == "ratio_of_sums":
            numerator, denominator = total("numerator"), total("denominator")
            if denominator == 0:
                raise ValueError("aggregate denominator is zero; ratio is undefined")
            values = {"numerator": numerator, "denominator": denominator, "ratio": numerator / denominator}
            formula = "ratio = sum(numerator) / sum(denominator); not mean of row ratios"
        else:
            base = sum((r["base_price"] * r["base_quantity"] for r in rows), Decimal(0))
            current = sum((r["current_price"] * r["current_quantity"] for r in rows), Decimal(0))
            price = sum(((r["current_price"] - r["base_price"]) * r["base_quantity"] for r in rows), Decimal(0))
            quantity = sum((r["base_price"] * (r["current_quantity"] - r["base_quantity"]) for r in rows), Decimal(0))
            interaction = sum(((r["current_price"] - r["base_price"]) * (r["current_quantity"] - r["base_quantity"]) for r in rows), Decimal(0))
            values = {"base_total": base, "current_total": current, "difference": current - base,
                      "price_effect": price, "quantity_effect": quantity, "interaction": interaction,
                      "reconciliation_residual": current - base - price - quantity - interaction}
            if values["reconciliation_residual"] != 0:
                raise ValueError("decomposition did not reconcile")
            formula = "delta=sum((p1-p0)*q0)+sum(p0*(q1-q0))+sum((p1-p0)*(q1-q0)); interaction remains separate"
        quantum = Decimal(1).scaleb(-spec["decimal_places"])
        return {"values": {k: {"unrounded": format(v, "f"), "rounded": format(v.quantize(quantum), "f")}
                           for k, v in values.items()}, "formula": formula,
                "rounding_layer": "each final aggregate only; no row rounding",
                "arithmetic_precision": 80, "ratio_precision_note": "ratio may be repeating and is computed to 80 significant digits",
                "row_count": len(rows)}


def run(spec_path, directory):
    spec_path = local_path(spec_path)
    raw = spec_path.read_bytes()
    if len(raw) > 65536:
        raise ValueError("spec exceeds 64 KiB")
    spec = load_json(raw)
    validate_spec(spec)
    source_path = Path(spec["source"]["ref"])
    source_path = local_path(source_path if source_path.is_absolute() else spec_path.parent / source_path)
    if source_path.stat().st_size > MAX_BYTES:
        raise ValueError("CSV exceeds 4 MiB bounded adapter limit")
    data = source_path.read_bytes()
    if sha(data) != spec["source"]["sha256"]:
        raise ValueError("source bytes differ from declared version hash; revise spec explicitly")
    rows = read_rows(data, spec)
    result = {"calculation_version": "0.1", "id": spec["id"], "operation": spec["operation"],
              "source": {"id": spec["source"]["id"], "revision": spec["source"]["revision"], "sha256": sha(data)},
              "context": spec["context"], "column_units": spec["column_units"],
              "decimal_places": spec["decimal_places"], "rounding": spec["rounding"], **compute(rows, spec)}
    directory = require_external_write(directory, (PACKAGE,))
    if directory.is_relative_to(PACKAGE) or os.path.lexists(directory) or not directory.parent.is_dir():
        raise ValueError("output must be a new external directory with an existing parent")
    if spec_path.read_bytes() != raw or source_path.read_bytes() != data:
        raise ValueError("inputs changed during calculation; retry with stable versions")
    output = encoded(result)
    replay = {**spec, "source": {**spec["source"], "ref": "input.csv"}}
    replay_bytes = encoded(replay)
    receipt = {"calculation_version": "0.1", "id": spec["id"], "execution_status": "completed",
               "scope": "declared_formula_and_captured_data_only", "definition_ref": spec["definition_ref"],
               "source": result["source"], "spec_sha256": sha(raw), "result_sha256": sha(output),
               "snapshot_ref": "input.csv", "spec_ref": "spec.json", "result_ref": "result.json",
               "replay_spec_ref": "replay-spec.json", "replay_spec_sha256": sha(replay_bytes),
               "replay_transformation": "Only source.ref changes to captured input.csv; original spec.json bytes remain intact.",
               "method": {"script": "report_calculate.py", "sha256": sha(Path(__file__).read_bytes()),
                          "python": sys.version.split()[0], "formula": result["formula"]},
               "checks": {"declared_input_hash": "pass", "unique_grain": "pass", "required_numbers": "pass",
                          "decomposition_reconciled": "pass" if spec["operation"] == "price_quantity_decomposition" else "not_applicable"},
               "independent_review": "not_run", "source_authenticity": "not_assessed",
               "caveat": "Algebraic reconciliation is not causal attribution. Business definitions, units and completeness require review. No Run acceptance or graph verification is performed."}
    directory.mkdir()
    for name, contents in (("spec.json", raw), ("replay-spec.json", replay_bytes), ("input.csv", data), ("result.json", output), ("calculation-receipt.json", encoded(receipt))):
        with (directory / name).open("xb") as handle:
            handle.write(contents)
    return {"valid": True, "execution_status": "completed", "output_directory": str(directory), "result_sha256": sha(output),
            "scope": receipt["scope"], "independent_review": "not_run"}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    execute = sub.add_parser("run")
    execute.add_argument("spec", type=Path)
    execute.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        result = run(args.spec, args.output)
    except (OSError, ValueError, csv.Error, ArithmeticError) as exc:
        print(json.dumps({"valid": False, "execution_status": "failed", "error": str(exc),
                          "output_state": "not_verified; preserve any partial directory"}, ensure_ascii=True))
        return 2
    print(json.dumps(result, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
