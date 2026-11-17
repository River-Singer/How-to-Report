"""Compile a versioned author document to a portable native-PPT project."""
from __future__ import annotations

import copy
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import shutil
import tempfile

from report_ppt import (DEFAULT_TEMPLATE, TemplateInputError, external_target, fingerprint,
                        load_template, read_json, render_page, validate_document as validate_template)
from presentation_svg import SceneRenderer
from presentation_composition import expand_page


def _write_json(path, value):
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+"\n",encoding="utf-8")


def _tree_identity(root):
    records = {}
    for path in sorted(root.rglob("*")):
        if "__pycache__" in path.parts or path.suffix in {".pyc",".pyo"}:
            continue
        if path.is_symlink() or getattr(path.lstat(),"st_file_attributes",0) & 0x400:
            raise TemplateInputError(f"linked template dependency is unsupported: {path}")
        if path.is_file():
            records[path.relative_to(root).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return fingerprint(records)


def _compiler_identity():
    names=("presentation_compiler.py","presentation_composition.py","presentation_svg.py","presentation_document.py","presentation_typography.py",
           "report_ppt.py","report_ppt_layouts.py","report_ppt_source.py",
           "presentation_library.py","presentation_recipes.py","presentation_layout.py","presentation_topology.py","presentation_chart_assets.py","presentation_palette.py",
           "presentation_content_diagnostics.py","presentation_text_profile.py")
    directory=Path(__file__).resolve().parent
    return {name:hashlib.sha256((directory/name).read_bytes()).hexdigest() for name in names}


def _template_text_parts(value, facts, path):
    """Resolve the explicit plain-text wrapper without accepting arbitrary objects."""
    from presentation_document import resolve_text
    if set(value) != {"parts"} or not isinstance(value["parts"], list):
        raise TemplateInputError(f"{path}: text wrapper requires only a parts array")
    for index, part in enumerate(value["parts"]):
        location = f"{path}.parts.{index}"
        if isinstance(part, dict):
            if "parts" in part:
                _template_text_parts(part, facts, location)
            elif "ref" not in part or not set(part).issubset({"ref", "format"}):
                raise TemplateInputError(f"{location}: expected text or a fact reference")
        elif isinstance(part, bool) or not isinstance(part, (str, int, float)):
            raise TemplateInputError(f"{location}: expected text or a fact reference")
    try:
        return resolve_text(value, facts)
    except ValueError as exc:
        raise TemplateInputError(f"{path}: {exc}") from exc


def _resolve_template_text(value, schema, facts, path):
    """Join explicit text parts only where the catalog declares a string slot."""
    if not isinstance(schema, dict):
        return value
    field_type = schema.get("type")
    accepts_text = field_type == "string" or isinstance(field_type, list) and "string" in field_type
    if accepts_text and isinstance(value, dict) and "parts" in value:
        return _template_text_parts(value, facts, path)
    if isinstance(value, dict):
        properties = schema.get("properties", {})
        additional = schema.get("additionalProperties", {})
        if not isinstance(additional, dict):
            additional = {}
        return {key: _resolve_template_text(item, properties.get(key, additional), facts, f"{path}.{key}")
                for key, item in value.items()}
    if isinstance(value, list):
        item_schema = schema.get("items", {})
        return [_resolve_template_text(item, item_schema, facts, f"{path}.{index}")
                for index, item in enumerate(value)]
    return value


def _template_parameters(template, catalog, facts, path):
    """Bind template content using its declared text types before normal validation."""
    from presentation_document import resolve_value
    parameters = resolve_value(template, facts)
    if not isinstance(parameters, dict):
        raise TemplateInputError(f"{path}: expected a template object")
    family_id = parameters.get("family")
    family = catalog["families"].get(family_id, {}) if isinstance(family_id, str) else {}
    schema = copy.deepcopy(family.get("content_schema", {}))
    variant_id = parameters.get("variant")
    if variant_id is None:
        content = parameters.get("content", {})
        items = content.get(family.get("array_key"), []) if isinstance(content, dict) else []
        count = len(items) if isinstance(items, list) else 0
        variant_id = family.get("auto_variant_by_items", {}).get(str(count), family.get("default_variant"))
    variant = family.get("variants", {}).get(variant_id, {}) if isinstance(variant_id, str) else {}
    if variant.get("renderer") == "source-diagram":
        properties = schema.get("properties", {})
        # The source renderer validates these maps with the catalog's chart/image types.
        if "charts" in properties:
            properties["charts"]["additionalProperties"] = catalog["families"]["chart"]["content_schema"]
        if "visuals" in properties:
            properties["visuals"]["additionalProperties"] = catalog["families"]["image"]["content_schema"]["properties"]["images"]["items"]
    if "content" in parameters:
        parameters["content"] = _resolve_template_text(parameters["content"], schema, facts, path + ".content")
    return parameters


def build_project(document, output, template_root=DEFAULT_TEMPLATE, tokens=None, asset_root=None, *, geometry_policy="legacy-replay"):
    """Validate and render every page before publishing a new project."""
    from presentation_document import validate_document, evaluate_facts, resolve_text, resolve_value
    source = Path(document).resolve() if isinstance(document,(str,Path)) else None
    data = read_json(source) if source else copy.deepcopy(document)
    if geometry_policy not in {"computed", "legacy-replay"}:
        raise TemplateInputError("geometry_policy must be computed or legacy-replay")
    validate_document(data)
    from presentation_library import resolve_profile_tokens
    tokens = resolve_profile_tokens(data, tokens)
    profile_snapshot = None
    if data.get("brief", {}).get("design_profile") is not None:
        profile_snapshot = Path(tokens).read_bytes()
        if hashlib.sha256(profile_snapshot).hexdigest() != data["brief"]["design_profile"]["sha256"]:
            raise TemplateInputError("profile bytes changed after verification")
    output = external_target(output)
    if output.exists():
        raise TemplateInputError(f"output already exists: {output}")
    from ppt_runtime import ENGINE, _runtime_fingerprint
    runtime_hash = _runtime_fingerprint()
    compiler_identity = _compiler_identity()
    template_hash = _tree_identity(Path(template_root).resolve())
    root, catalog, values = load_template(template_root,tokens)
    if profile_snapshot is not None and fingerprint(values) != fingerprint(json.loads(profile_snapshot.decode("utf-8"))):
        raise TemplateInputError("loaded tokens differ from declared profile snapshot")
    facts = evaluate_facts(data)
    if not data["pages"]:
        raise TemplateInputError("pages: provide at least one page")
    assets_root = asset_root or (source.parent if source else None)
    rendered=[]
    content_diagnostics = []
    layout_results = {}
    data_snapshots = {}
    palette_id = data.get("brief", {}).get("palette_id")
    from presentation_palette import PALETTES, apply_palette
    palette_bytes = PALETTES.read_bytes()
    data_snapshots[PALETTES] = palette_bytes
    if palette_id is not None:
        values = apply_palette(values, palette_id)
        snapshot = values.get("color", {}).get("palette")
        if snapshot and snapshot["registry_sha256"] != hashlib.sha256(palette_bytes).hexdigest():
            raise TemplateInputError("palette registry changed during resolution")
    recipe_schema = None
    page_usage = {}
    family_counts, variant_counts, component_counts = Counter(), Counter(), Counter()
    kind_counts = Counter()
    for number_index,page in enumerate(data["pages"],1):
        expanded = None
        if not re.fullmatch(r"[A-Za-z0-9_][A-Za-z0-9_.-]*", page["id"]):
            raise TemplateInputError(f"{page['id']}: page ID must be a safe stable filename identifier")
        if page.get("kind","scene") == "template":
            parameters=_template_parameters(page.get("template",{}),catalog,facts,f"pages.{number_index-1}.template")
            parameters.update({"id":page["id"],"notes":resolve_text(page.get("notes",""),facts)})
            wrapper={"schema_version":1,"template_id":catalog["template_id"],"pages":[parameters]}
            valid=validate_template(wrapper,catalog,root)["pages"][0]
            page_usage[page["id"]] = {"kind": "template", "template": {"family": valid["family"], "variant": valid["variant"]}}
            family_counts[valid["family"]] += 1
            variant_counts[f"{valid['family']}/{valid['variant']}"] += 1
            svg,mapping,assets=render_page(valid,catalog,values,root,number_index,assets_root)
        elif page.get("kind","scene") in {"scene", "layout"}:
            kind = page.get("kind", "scene")
            canvas = (values["canvas"]["width"], values["canvas"]["height"])
            scene = page
            if kind == "scene" and geometry_policy == "computed":
                if not isinstance(page.get("recipe_source"), dict):
                    error = TemplateInputError(f"{page['id']}: computed geometry requires a layout tree or saved recipe source; raw scene frames require explicit legacy-replay")
                    error.diagnostic = {"code": "computed_geometry_required", "node_id": page["id"],
                                        "path": f"pages[{number_index-1}]", "reason": "raw scene geometry has no replayable algorithm source",
                                        "suggestions": ["migrate content to kind=layout", "compose a supported recipe and preserve recipe_source",
                                                        "use --geometry-policy legacy-replay only to reproduce historical artifacts"]}
                    raise error
                from presentation_library import SYSTEM
                from presentation_recipes import lower_recipe_page
                if recipe_schema is None:
                    schema_path = SYSTEM / "recipe-request.schema.json"
                    raw_schema = schema_path.read_bytes()
                    data_snapshots[schema_path] = raw_schema
                    recipe_schema = json.loads(raw_schema.decode("utf-8"))
                if page["recipe_source"].get("id") != page["id"]:
                    raise TemplateInputError(f"{page['id']}: recipe_source.id must match page ID")
                scene = lower_recipe_page(page["recipe_source"], values, facts, number_index, len(data["pages"]), schema=recipe_schema)
                page = {**page, "notes": scene["notes"], "job": scene["job"]}
                if "intent" in scene:
                    page["intent"] = scene["intent"]
                layout_results[page["id"]] = (scene, {"algorithm_version": "recipe-0.1", "recipe": page["recipe_source"]["recipe"],
                                                      "source": "recipe_source replay; cached elements ignored"})
            if kind == "layout":
                from presentation_layout import lower_layout_page
                scene, report = lower_layout_page(page, facts, canvas, values)
                layout_results[page["id"]] = (scene, report)
            expanded=expand_page(scene,facts,canvas, values)
            if kind == "layout":
                layout_results[page["id"]] = (expanded, report)
            elif page["id"] in layout_results:
                layout_results[page["id"]] = (expanded, layout_results[page["id"]][1])
            renderer=SceneRenderer(expanded,values,assets_root,resolve_text,resolve_value,facts)
            svg,mapping,assets=renderer.render()
            counts = Counter()
            pending = list(scene.get("elements", []))
            while pending:
                item = pending.pop()
                if item.get("type") == "component":
                    counts[item["component"]] += 1
                pending.extend(item.get("children", []))
                if isinstance(item.get("element"), dict):
                    pending.append(item["element"])
                for field in ("layout", "interior"):
                    if isinstance(item.get(field), dict):
                        pending.append(item[field])
            page_usage[page["id"]] = {"kind": kind, "components": dict(sorted(counts.items()))}
            component_counts.update(counts)
        else:
            raise TemplateInputError(f"{page['id']}: unsupported page kind")
        kind_counts[page_usage[page["id"]]["kind"]] += 1
        from presentation_text_profile import validate_profile_text_floor
        validate_profile_text_floor(data, page, svg, geometry_policy)
        from presentation_content_diagnostics import analyze_page, VERSION as DIAGNOSTICS_VERSION
        layout_report = layout_results.get(page["id"], (None, None))[1]
        content_diagnostics.append(analyze_page(page, expanded, values, facts,
                                               layout_report=layout_report, rendered_svg=svg))
        rendered.append((page,svg,mapping,assets))
    asset_usage = {"scene_pages": kind_counts["scene"], "template_pages": kind_counts["template"],
                   "families": dict(sorted(family_counts.items())), "variants": dict(sorted(variant_counts.items())),
                   "components": dict(sorted(component_counts.items()))}
    if kind_counts["layout"]:
        asset_usage["layout_pages"] = kind_counts["layout"]
    output.parent.mkdir(parents=True,exist_ok=True)
    temporary=Path(tempfile.mkdtemp(prefix=".presentation-build-",dir=output.parent))
    try:
        for folder in ("svg_output","notes","inputs"):
            (temporary/folder).mkdir()
        page_receipts=[]
        prefix_width=max(2,len(str(len(rendered))))
        for index,(page,svg,mapping,assets) in enumerate(rendered,1):
            stem=f"{index:0{prefix_width}d}_{page['id']}"
            (temporary/"svg_output"/(stem+".svg")).write_text(svg,encoding="utf-8")
            (temporary/"notes"/(stem+".md")).write_text(resolve_text(page.get("notes",""),facts),encoding="utf-8")
            for relative,payload in assets.items():
                target=temporary/relative
                target.parent.mkdir(parents=True,exist_ok=True)
                if target.exists() and target.read_bytes()!=payload:
                    raise TemplateInputError(f"asset collision: {relative}")
                target.write_bytes(payload)
            page_receipt = {"id":page["id"],**page_usage[page["id"]],"svg":f"svg_output/{stem}.svg",
                "svg_sha256":hashlib.sha256(svg.encode()).hexdigest(),"objects":mapping}
            if page["id"] in layout_results:
                scene, report = layout_results[page["id"]]
                (temporary / "layout").mkdir(exist_ok=True)
                scene_ref = f"layout/{stem}.scene.json"
                report_ref = f"layout/{stem}.report.json"
                solved = {"project_id": data["project_id"], "revision": data["revision"],
                          "source_page_id": page["id"], "input_sha256": fingerprint(data),
                          "source_page_sha256": fingerprint(data["pages"][index-1]), "facts_sha256": fingerprint(facts),
                          "tokens_sha256": fingerprint(values), "compiler_files": compiler_identity,
                          "geometry_policy": geometry_policy,
            "palette_id": palette_id,
                          "data_dependencies": {path.relative_to(Path(__file__).resolve().parent.parent).as_posix(): hashlib.sha256(raw).hexdigest()
                                                for path, raw in data_snapshots.items()}}
                _write_json(temporary / scene_ref, {**solved, "scene": scene})
                _write_json(temporary / report_ref, {**solved, "report": report})
                page_receipt["layout"] = {"scene_ref": scene_ref, "report_ref": report_ref,
                                          "scene_sha256": hashlib.sha256((temporary / scene_ref).read_bytes()).hexdigest(),
                                          "report_sha256": hashlib.sha256((temporary / report_ref).read_bytes()).hexdigest()}
            page_receipts.append(page_receipt)
        notes="\n\n".join(f"# {i+1}. {page['id']}\n\n{resolve_text(page.get('notes',''),facts)}" for i,(page,*_) in enumerate(rendered))
        (temporary/"notes"/"total.md").write_text(notes+"\n",encoding="utf-8")
        _write_json(temporary/"inputs"/"presentation.project.json",data)
        _write_json(temporary/"tokens.json",values)
        _write_json(temporary/"object-map.json",{"project_id":data["project_id"],"revision":data["revision"],
                                               "asset_usage": asset_usage,"pages":page_receipts})
        _write_json(temporary/"resolved-facts.json",facts)
        diagnostics_payload = {"version": DIAGNOSTICS_VERSION, "project_id": data["project_id"], "revision": data["revision"],
            "input_sha256": fingerprint(data), "tokens_sha256": fingerprint(values), "geometry_policy": geometry_policy,
            "semantic_quality": "not_assessed", "audience": "author and reviewer only; never slide content",
            "review_required": any(p["review_required"] for p in content_diagnostics), "pages": content_diagnostics}
        _write_json(temporary/"content-diagnostics.json", diagnostics_payload)
        runtime_identity=read_json(ENGINE/"provenance.json")
        receipt={"schema_version":"0.1","project_id":data["project_id"],"revision":data["revision"],
            "input_sha256":fingerprint(data),"catalog_sha256":fingerprint(catalog),"tokens_sha256":fingerprint(values),
            "runtime_manifest_sha256":fingerprint(runtime_identity),"runtime_sha256":runtime_hash,
            "template_tree_sha256":template_hash,"measurement":"runtime DrawingML estimator",
            "compiler_files":compiler_identity,
            "geometry_policy": geometry_policy,
            "palette_id": palette_id,
            "content_diagnostics": {"ref": "content-diagnostics.json", "sha256": hashlib.sha256((temporary/"content-diagnostics.json").read_bytes()).hexdigest(),
                "review_required": diagnostics_payload["review_required"], "semantic_quality": "not_assessed"},
            "data_dependencies": {path.relative_to(Path(__file__).resolve().parent.parent).as_posix(): hashlib.sha256(raw).hexdigest()
                                  for path, raw in data_snapshots.items()},
            "pages":page_receipts,"page_count":len(rendered),"asset_usage":asset_usage}
        _write_json(temporary/"engine-receipt.json",receipt)
        if profile_snapshot is not None and Path(tokens).read_bytes() != profile_snapshot:
            raise TemplateInputError("profile bytes changed during compilation")
        if any(path.read_bytes() != raw for path, raw in data_snapshots.items()):
            raise TemplateInputError("recipe schema bytes changed during compilation")
        if _runtime_fingerprint() != runtime_hash or _tree_identity(root) != template_hash or _compiler_identity() != compiler_identity:
            raise TemplateInputError("compiler, runtime or template dependencies changed during compilation")
        # rename refuses a target created by a concurrent writer.
        temporary.rename(output)
        return receipt
    finally:
        if temporary.exists():
            shutil.rmtree(temporary)
