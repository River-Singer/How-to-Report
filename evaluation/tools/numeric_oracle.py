#!/usr/bin/env python3
"""Independent Decimal arithmetic over synthetic fixtures; read-only, no model grading."""
from __future__ import annotations

import csv
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]


def cost_decomposition(path: Path) -> dict:
    groups: dict[str, dict[str, tuple[Decimal, Decimal]]] = {}
    versions, currencies = set(), set()
    with path.open(encoding="utf-8", newline="") as stream:
        for row in csv.DictReader(stream):
            key, period = row["part"], row["period"]
            if period not in ("base", "current") or period in groups.setdefault(key, {}):
                raise ValueError("duplicate part/period or unsupported period")
            price, quantity = Decimal(row["unit_price"]), Decimal(row["quantity"])
            if not price.is_finite() or not quantity.is_finite():
                raise ValueError("non-finite input")
            groups[key][period] = price, quantity
            versions.add(row["bom_version"]); currencies.add(row["currency"])
    if not groups or len(versions) != 1 or len(currencies) != 1:
        raise ValueError("empty data or mixed version/currency; comparability unresolved")
    if any(set(pair) != {"base", "current"} for pair in groups.values()):
        raise ValueError("unpaired part data")
    base = current = price_base = quantity_base = interaction = Decimal(0)
    for pair in groups.values():
        p0, q0 = pair["base"]; p1, q1 = pair["current"]
        base += p0 * q0; current += p1 * q1
        price_base += (p1 - p0) * q0
        quantity_base += p0 * (q1 - q0)
        interaction += (p1 - p0) * (q1 - q0)
    return {"base": base, "current": current, "delta": current - base,
            "base_weighted": {"price": price_base, "quantity": quantity_base, "interaction": interaction},
            "price_then_quantity": {"price": price_base, "quantity": quantity_base + interaction},
            "quantity_then_price": {"price": price_base + interaction, "quantity": quantity_base},
            "symmetric": {"price": price_base + interaction / 2, "quantity": quantity_base + interaction / 2}}


def main() -> int:
    fixture = ROOT / "fixtures/data-cost.csv"
    try:
        result = cost_decomposition(fixture)
        expected = {"base": Decimal(350), "current": Decimal(440), "delta": Decimal(90)}
        if any(result[key] != value for key, value in expected.items()):
            raise ValueError("synthetic fixture no longer matches the documented oracle")
        for key in ("base_weighted", "price_then_quantity", "quantity_then_price", "symmetric"):
            if sum(result[key].values()) != result["delta"]:
                raise ValueError("decomposition does not reconcile")
        try:
            cost_decomposition(ROOT / "fixtures/data-conflicted.csv")
        except ValueError as conflict:
            conflict_status = str(conflict)
        else:
            raise ValueError("conflicted fixture unexpectedly accepted")
    except (ValueError, OSError, ArithmeticError, KeyError, TypeError, csv.Error) as error:
        print(json.dumps({"valid": False, "error": str(error)}))
        return 1
    print(json.dumps({"valid": True, "scope": "synthetic_arithmetic_only", "model_execution": False,
                      "input_sha256": hashlib.sha256(fixture.read_bytes()).hexdigest(),
                      "cost": result, "conflicted_input": {"accepted": False, "reason": conflict_status},
                      "marketing_cost_per_application": {"A": Decimal(12000) / 600, "B": Decimal(18000) / 720},
                      "causal_attribution": "not_established", "writes": "none"}, default=str, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
