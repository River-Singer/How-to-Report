"""Bounded discovery over existing primitives, components, templates and recipes."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

from report_ppt import DEFAULT_TEMPLATE, SKILL_ROOT, fingerprint, load_template, read_json


SYSTEM = SKILL_ROOT / "assets/design-system"
KINDS = {"primitive", "component", "template", "profile", "chart-vocabulary", "recipe", "icon"}
STATUSES = {"high_level", "backend_only", "planned"}
COMPONENT_RELATIONS = {
    "partition": ["part-to-whole", "组成", "比例"],
    "comparison": ["magnitude", "comparison", "比较"],
    "progress-ring": ["part-to-whole", "比例", "占比"],
    "paragraph-flow": ["explanation", "解释"],
    "evidence-map": ["evidence-action", "证据", "行动"],
    "topology": ["relationship", "hierarchy", "结构", "拓扑", "架构"],
}


def profile_path(identifier="report-14pt"):
    if identifier != "report-14pt":
        raise ValueError(f"unknown design profile {identifier!r}")
    return SKILL_ROOT / "assets/design-profiles/report-14pt.json"


def profile_identity(identifier="report-14pt"):
    path = profile_path(identifier)
    return {"id": identifier, "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "hash_method": "sha256-file-bytes"}


def resolve_profile_tokens(document, tokens=None):
    """Pin declared built-in profiles across compose, CLI builds and Python builds."""
    declared = document.get("brief", {}).get("design_profile")
    if declared is None:
        return tokens
    if not isinstance(declared, dict) or set(declared) != {"id", "sha256", "hash_method"}:
        raise ValueError("brief.design_profile requires id/sha256/hash_method")
    actual = profile_identity(declared["id"])
    if declared != actual:
        raise ValueError("declared design profile identity changed; patch its identity before building")
    path = profile_path(declared["id"])
    if tokens is not None and hashlib.sha256(Path(tokens).read_bytes()).hexdigest() != actual["sha256"]:
        raise ValueError("explicit tokens conflict with brief.design_profile; patch the profile declaration first")
    return path if tokens is None else tokens


def _record(identifier, kind, purpose, relations=(), **extra):
    return {"id": identifier, "kind": kind, "version": "0.1", "status": "high_level",
            "purpose": purpose, "relations": list(relations), "schema_ref": None,
            "executable": kind in {"primitive", "component", "template", "recipe", "icon"},
            "compile_contract": {"primitive": "scene element", "component": "scene component",
                                 "template": "template page", "recipe": "compose request", "icon": "template icon_key or individual image asset"}.get(kind),
            "status_scope": "normal author entry availability; evidence maturity is separate",
            "schema_scope": "inline-on-describe", "preview_refs": [],
            "validation": {"scope": "implementation contract; target results require their own evidence",
                           "user_quality_acceptance": "not_established"}, **extra}


def _records(template, *, include_icons=True):
    from presentation_svg import scene_contracts
    from presentation_composition import COMPONENTS
    from presentation_assets import variant_summary
    records = []
    for name in scene_contracts():
        records.append(_record("primitive." + name, "primitive", "Editable scene " + name,
                               compiler_ref="scripts/presentation_svg.py"))
    for name, definition in COMPONENTS.items():
        records.append(_record("component." + name, "component", definition["purpose"],
                               COMPONENT_RELATIONS.get(name, []), capacity=definition.get("capacity"),
                               compiler_ref="scripts/presentation_topology.py" if name == "topology" else "scripts/presentation_composition.py"))
    if include_icons:
        from presentation_icons import icon_catalog
        icon_offset = 0
        while True:
            icon_page = icon_catalog(offset=icon_offset, limit=100)
            for icon in icon_page["items"]:
                records.append(_record("icon." + icon["key"], "icon", icon.get("title", icon.get("name", icon["key"])),
                                       icon.get("tags", []), icon_key=icon["key"],
                                       compiler_ref="scripts/presentation_icons.py", asset_ref=icon["asset"],
                                       editability=icon.get("editability"), source=icon.get("source"),
                                       preview_refs=[{"ref": icon["preview"], "scope": "package", "format": "svg"}]))
            icon_offset += len(icon_page["items"])
            if icon_offset >= icon_page["total"] or not icon_page["items"]:
                break
    root, catalog, _ = load_template(template)
    catalog_hash = fingerprint(catalog)
    for family_id, family in catalog["families"].items():
        for variant_id, variant in family["variants"].items():
            summary = variant_summary(root, catalog, family_id, family, variant_id, variant)
            preview = Path(summary.pop("preview")) if summary.get("preview") else None
            preview_refs = []
            if preview is not None:
                try:
                    reference = preview.relative_to(SKILL_ROOT).as_posix()
                    scope = "package"
                except ValueError:
                    reference = preview.relative_to(root).as_posix()
                    scope = "template-root"
                preview_refs = [{"ref": reference, "scope": scope, "format": "svg"}]
            records.append(_record("template." + summary["id"], "template", summary["purpose"],
                summary["relations"], family=family_id, variant=variant_id, capacity=summary["capacity"],
                label=summary["label"], description=summary["description"], preview_refs=preview_refs,
                catalog_revision=catalog.get("revision"), catalog_sha256=catalog_hash,
                compiler_ref="scripts/report_ppt.py", schema_scope="catalog-adapter-on-describe"))
    registry = read_json(SYSTEM / "registry.json")
    for record in registry["recipes"]:
        records.append(_record(record["id"], "recipe", record["purpose"], **{
            key: copy.deepcopy(value) for key, value in record.items() if key not in {"id", "kind", "purpose"}}))
    identity = profile_identity()
    records.append(_record("profile.report-14pt", "profile", "14pt正文、最低9pt、正文80%黑与注释35%黑",
        tokens_ref="assets/design-profiles/report-14pt.json", identity=identity,
        status_scope="available theme parameter profile; not a drawing child",
        compiler_ref="scripts/presentation_typography.py"))
    vocabulary = read_json(SYSTEM / "visual-vocabulary.json")
    for entry in vocabulary["entries"]:
        records.append(_record("chart-vocabulary." + entry["id"], "chart-vocabulary", entry["label"],
            entry["categories"], status=entry["readiness"], versions=entry["versions"],
            compiler_ref=None, schema_scope="vocabulary-mapping-not-an-executable-child",
            status_scope="data-expression mapping readiness; not an independent executable asset",
            editable_output=entry["editable_output"], limitations=entry["notes"],
            provenance={"license": vocabulary["license"], "sources": entry["source"]}))
    return records


def library(template=DEFAULT_TEMPLATE, *, identifier=None, kind=None, relationship=None,
            status=None, executable=None, query="", offset=0, limit=20):
    if kind is not None and kind not in KINDS:
        raise ValueError("unknown library kind")
    if status is not None and status not in STATUSES:
        raise ValueError("unknown library status")
    if executable is not None and type(executable) is not bool:
        raise ValueError("executable filter must be boolean")
    if type(offset) is not int or offset < 0 or type(limit) is not int or not 1 <= limit <= 100:
        raise ValueError("offset must be nonnegative and limit must be 1..100")
    if not isinstance(query, str) or len(query) > 256:
        raise ValueError("query must be text of at most 256 characters")
    if relationship is not None and (not isinstance(relationship, str) or len(relationship) > 100):
        raise ValueError("relationship must be text of at most 100 characters")
    include_icons = identifier.startswith("icon.") if isinstance(identifier, str) else kind in {None, "icon"}
    records = _records(template, include_icons=include_icons)
    if identifier is not None:
        record = next((record for record in records if record["id"] == identifier), None)
        if record is None:
            raise ValueError(f"unknown library ID {identifier!r}")
        return _describe(record, template)
    terms = query.casefold().split()
    matches = [record for record in records
               if (kind is None or record["kind"] == kind)
               and (status is None or record["status"] == status)
               and (executable is None or record["executable"] == executable)
               and (relationship is None or relationship in record["relations"])
               and all(term in json.dumps(record, ensure_ascii=False).casefold() for term in terms)]
    matches.sort(key=lambda record: record["id"])
    return {"library_version": "0.1", "total": len(matches), "offset": offset, "limit": limit,
            "next_offset": offset + limit if offset + limit < len(matches) else None,
            "items": matches[offset:offset + limit],
            "status_scope": "read status per kind; executable indicates an author entry, and evidence/quality maturity is separate"}


def _describe(record, template):
    result = copy.deepcopy(record)
    kind, identifier = record["kind"], record["id"].split(".", 1)[1]
    if kind == "primitive":
        from presentation_svg import scene_contracts
        result["contract"] = scene_contracts()[identifier]
    elif kind == "icon":
        from presentation_icons import icon_catalog
        result["contract"] = icon_catalog(identifier)
        result["usage"] = {"template": {"field": "icon_key", "value": identifier, "scope": "templates that expose an icon_key slot"},
                           "layout_leaf": {"type": "leaf", "id": "selected-icon", "height": 64, "aspect_ratio": 1,
                                           "element": {"type": "image", "path": record["asset_ref"], "fit": "contain"}},
                           "asset_root": "pass --assets <installed-Skill-directory> for package-relative image paths",
                           "native_editing": {"template_icon_key": record.get("editability"),
                                              "image_leaf": "SVG image object; internal paths are not individually editable PowerPoint shapes"}}
    elif kind == "component":
        from presentation_composition import component_catalog
        _, _, values = load_template(template)
        result["contract"] = component_catalog(identifier, values)
    elif kind == "template":
        _, catalog, _ = load_template(template)
        family = catalog["families"][record["family"]]
        result["contract"] = {"content_schema": family["content_schema"],
                              "variant": family["variants"][record["variant"]],
                              "prototype_content": family.get("prototype_content", {})}
    elif kind == "profile":
        from presentation_typography import typography_catalog
        values = read_json(profile_path(identifier))
        result["contract"] = typography_catalog(values)
        result["tokens"] = values
    elif kind == "recipe":
        result["schema"] = read_json(SYSTEM / "recipe-request.schema.json")
        result["example"] = read_json(SYSTEM / "examples/three-recipes.json")
    else:
        vocabulary = read_json(SYSTEM / "visual-vocabulary.json")
        result["definition"] = next(entry for entry in vocabulary["entries"] if entry["id"] == identifier)
        result["version_summary"] = vocabulary["summary"]
    return result
