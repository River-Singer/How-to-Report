"""Discover the current template catalog without duplicating its metadata."""
from __future__ import annotations

import json
import re

from report_ppt import fingerprint, load_template


SEMANTIC_FIELDS = ("label", "purpose", "description", "scenarios", "relations",
                   "preservation", "page_type", "type", "usage_notes")


def _preview(root, variant):
    prototype = variant.get("prototype")
    return str(root / "templates" / "prototypes" / prototype) if prototype else None


def asset_summary(root, catalog, family_id, family):
    """Keep the existing family-result shape for callers of query and describe."""
    return {
        "id": family_id,
        "label": family.get("label", family_id),
        "purpose": family.get("purpose", ""),
        "scenarios": family.get("scenarios", []),
        "relations": family.get("relations", []),
        "variants": [{"id": name, "capacity": item.get("capacity"),
                      "preview": _preview(root, item)}
                     for name, item in family.get("variants", {}).items()],
        "template_id": catalog["template_id"],
    }


def variant_summary(root, catalog, family_id, family, variant_id, variant):
    """Expose selection metadata while leaving source geometry to describe."""
    array_key = family.get("array_key")
    array_schema = family.get("content_schema", {}).get("properties", {}).get(array_key, {})
    source_fields = variant.get("fields", {})
    return {
        "id": family_id + "/" + variant_id,
        "family": family_id,
        "variant": variant_id,
        "family_label": family.get("label", family_id),
        "label": variant.get("label", family.get("label", family_id) + " · " + variant_id),
        "purpose": family.get("purpose", ""),
        "description": variant.get("description", ""),
        "scenarios": variant.get("scenarios", family.get("scenarios", [])),
        "relations": variant.get("relations", family.get("relations", [])),
        "preservation": variant.get("preservation"),
        "capacity": variant.get("capacity"),
        "content_limits": {
            "array_key": array_key,
            "array_min_items": variant.get("min_items", array_schema.get("minItems")),
            "array_max_items": array_schema.get("maxItems"),
            "item_text_limits": variant.get("item_text_limits"),
            "fixed_text_fields": len(source_fields),
            "image_slots": len(variant.get("image_slots", {})),
            "chart_slots": len(variant.get("chart_slots", {})),
        },
        "adaptation": {
            "geometry_use": variant.get("geometry_use"),
            "renderer": variant.get("renderer"),
            "auto_variant_by_items": family.get("auto_variant_by_items", {}),
            "fixed_source_topology": variant.get("renderer") == "source-diagram",
            "dynamic_count": variant.get("dynamic_count", False),
            "supported_changes": variant.get("adaptation"),
            "fit_check": "declared content limits and measured fit at validate/build",
        },
        "preview": _preview(root, variant),
        "detail_command": "describe " + family_id + " --variant " + variant_id,
        "template_id": catalog["template_id"],
    }


def _catalog_identity(catalog):
    families = catalog["families"]
    return {
        "template_id": catalog["template_id"],
        "catalog_revision": catalog.get("revision"),
        "catalog_sha256": fingerprint(catalog),
        "counts": {"families": len(families),
                   "variants": sum(len(family.get("variants", {})) for family in families.values())},
    }


def _page_parameters(offset, limit, maximum):
    if isinstance(offset, bool) or not isinstance(offset, int) or offset < 0:
        raise ValueError("offset must be a nonnegative integer")
    if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= maximum:
        raise ValueError(f"limit must be between 1 and {maximum}")


def inventory_assets(template, *, family=None, variants=False, offset=0, limit=20):
    """Enumerate every registered entry with explicit, versioned pagination."""
    _page_parameters(offset, limit, 100)
    root, catalog, _ = load_template(template)
    families = catalog["families"]
    if family is not None:
        if family not in families:
            raise ValueError(f"unknown template family {family!r}")
        families = {family: families[family]}
    items = []
    for family_id, definition in sorted(families.items()):
        if variants:
            for variant_id, variant in sorted(definition.get("variants", {}).items()):
                items.append(variant_summary(root, catalog, family_id, definition, variant_id, variant))
        else:
            summary = {key: value for key, value in asset_summary(root, catalog, family_id, definition).items()
                       if key != "variants"}
            summary["variant_count"] = len(definition.get("variants", {}))
            summary["variants_command"] = "inventory --variants --family " + family_id
            items.append(summary)
    end = min(offset + limit, len(items))
    return {**_catalog_identity(catalog), "view": "variants" if variants else "families",
            "family_filter": family, "total": len(items), "offset": offset, "limit": limit,
            "next_offset": end if end < len(items) else None, "items": items[offset:end]}


def _query_terms(task):
    """Use word and Chinese-bigram overlap, with no semantic-model inference."""
    if not isinstance(task, str):
        raise ValueError("task must be text")
    terms = {}
    for token in re.findall(r"[a-z0-9_.-]+|[\u3400-\u9fff]+", task.casefold()):
        terms[token] = max(terms.get(token, 0), 4)
        if len(token) > 2 and re.fullmatch(r"[\u3400-\u9fff]+", token):
            for index in range(len(token) - 1):
                terms.setdefault(token[index:index + 2], 1)
    return terms


def _text(value):
    return value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)


def _semantic_fields(family_id, family, variant_id=None, variant=None):
    fields = {"family.id": family_id}
    fields.update({"family." + key: _text(family[key]) for key in SEMANTIC_FIELDS if key in family})
    if variant is not None:
        fields["variant.id"] = variant_id
        fields.update({"variant." + key: _text(variant[key]) for key in SEMANTIC_FIELDS if key in variant})
        roles = [field["role"] for field in variant.get("fields", {}).values() if field.get("role")]
        if roles:
            fields["variant.field_roles"] = " ".join(roles)
    return fields


def _match(fields, terms):
    evidence = []
    score = 0
    matched = set()
    for field, original in fields.items():
        normalized = original.casefold()
        hits = [term for term in terms if term in normalized]
        if not hits:
            continue
        weight = 3 if field.endswith((".label", ".id")) else 1
        score += sum(terms[term] * weight for term in hits)
        score += sum(terms[term] * 4 for term in hits if normalized == term)
        matched.update(hits)
        first_match = min(normalized.index(term) for term in hits)
        normalized_position = 0
        source_position = 0
        # Case folding can expand characters, so preserve source-text offsets.
        for source_position, character in enumerate(original):
            normalized_position += len(character.casefold())
            if normalized_position > first_match:
                break
        excerpt_start = max(0, source_position - 40)
        excerpt_end = min(len(original), excerpt_start + 180)
        evidence.append({"field": field, "terms": hits,
                         "text_excerpt": original[excerpt_start:excerpt_end],
                         "excerpt_start": excerpt_start,
                         "excerpt_truncated": excerpt_start > 0 or excerpt_end < len(original)})
    return score, len(matched), evidence


def query_assets(template, task="", limit=5, *, variants=False):
    """Rank declared catalog metadata and expose the exact lexical evidence."""
    _page_parameters(0, limit, 50)
    root, catalog, _ = load_template(template)
    terms = _query_terms(task)
    candidates = []
    for family_id, family in catalog["families"].items():
        matches = []
        for variant_id, variant in family.get("variants", {}).items():
            fields = _semantic_fields(family_id, family, variant_id, variant)
            score, count, evidence = _match(fields, terms)
            if terms and not score:
                continue
            matches.append((score, count, evidence, variant_id, variant))
        matches.sort(key=lambda item: (-item[0], item[3]))
        if variants:
            for score, count, evidence, variant_id, variant in matches:
                candidate = variant_summary(root, catalog, family_id, family, variant_id, variant)
                candidate.update(match_score=score, match_count=count, match_evidence=evidence)
                candidates.append(candidate)
        else:
            family_score, family_count, family_evidence = _match(_semantic_fields(family_id, family), terms)
            if terms and not family_score and not matches:
                continue
            best = matches[0] if matches else (family_score, family_count, family_evidence, None, None)
            candidate = asset_summary(root, catalog, family_id, family)
            candidate.update(match_score=best[0], match_count=best[1], match_evidence=best[2],
                             best_matching_variant=best[3])
            candidates.append(candidate)
    candidates.sort(key=lambda item: (-item["match_score"], item["id"]))
    return {**_catalog_identity(catalog), "query": task, "result_level": "variants" if variants else "families",
            "match_method": "declared metadata word and Chinese-bigram overlap",
            "matching_scope": "family and variant metadata including field roles",
            "selection_boundary": "Lexical candidates require prototype review and actual content-fit checks.",
            "total_matches": len(candidates), "limit": limit, "candidates": candidates[:limit]}
