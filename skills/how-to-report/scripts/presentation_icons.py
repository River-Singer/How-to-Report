"""Bounded discovery of independently extracted user PPT vector icons."""
from __future__ import annotations

import copy
import json
from pathlib import Path

from report_ppt import TemplateInputError


ICON_ROOT = Path(__file__).resolve().parents[1] / "assets" / "templates" / "business-blue-v1" / "icons"


def icon_catalog(key=None, tokens=None, *, offset=0, limit=20, query="", name=None):
    """Describe one icon or page through real source assets; aliases count separately."""
    if name is not None:
        if key is not None:
            raise TemplateInputError("icons: provide key or name, not both")
        key = name
    if isinstance(offset, bool) or not isinstance(offset, int) or offset < 0:
        raise TemplateInputError("icons.offset: expected a nonnegative integer")
    if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 100:
        raise TemplateInputError("icons.limit: expected an integer from 1 to 100")
    if not isinstance(query, str) or len(query) > 200:
        raise TemplateInputError("icons.query: expected a string of at most 200 characters")
    registry = json.loads((ICON_ROOT / "catalog.json").read_text(encoding="utf-8"))
    items = []
    for identifier, record in registry.items():
        item = copy.deepcopy(record)
        item.update(key=identifier, name=identifier)
        item.setdefault("title", identifier)
        item.setdefault("tags", [identifier] if not identifier.startswith("ppt-icons-") else [])
        item["asset"] = "assets/templates/business-blue-v1/icons/" + record["file"]
        item["preview"] = item["asset"]
        item.setdefault("source", {"slide": record["source_slide"], "shape_id": record["source_shape_id"], "sha256": record["source_sha256"]})
        item["editability"] = "inline SVG vector paths; native PPT freeform geometry after export; no editable text"
        item["usage"] = {"template_field": "content.items[].icon_key (or the family-specific node/step field)", "value": identifier, "color": "theme primary", "fit": "contain"}
        items.append(item)
    if key is not None:
        if not isinstance(key, str) or key not in registry:
            raise TemplateInputError(f"icons: unknown key {key!r}")
        return next(item for item in items if item["key"] == key)
    terms = query.casefold().split()
    matches = [item for item in items if all(term in json.dumps(item, ensure_ascii=False).casefold() for term in terms)]
    source_count = sum(identifier.startswith("ppt-icons-") for identifier in registry)
    return {"contract_version": "0.1", "source_asset_count": source_count,
            "legacy_alias_count": len(registry) - source_count, "total": len(matches),
            "offset": offset, "limit": limit, "items": matches[offset:offset + limit],
            "gallery": "assets/templates/business-blue-v1/icons/gallery.html",
            "capabilities": {"independent_vector_assets": True, "theme_color": "primary",
                             "semantic_names": "24 established aliases; remaining keys retain source page and shape ID",
                             "arbitrary_scene_icon_leaf": False}}
