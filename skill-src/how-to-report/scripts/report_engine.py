#!/usr/bin/env python3
"""Discover presentation assets, compile author documents, and retain revisions."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import uuid

from report_ppt import DEFAULT_TEMPLATE, external_target, load_template, read_json
from presentation_assets import asset_summary, inventory_assets, query_assets


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode("utf-8")


def write_new_json(destination, value):
    """Publish a new result without replacing an existing file."""
    destination = external_target(destination)
    data = encoded(value)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("xb") as stream:
        try:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        except BaseException:
            stream.close()
            destination.unlink(missing_ok=True)
            raise
    return destination


def mutate_control(path, expected, transform):
    """Serialize cooperating writers and retain the exact previous state."""
    path = external_target(path)
    history = external_target(path.parent / (path.stem + "-history"))
    lock_path = external_target(path.with_name(path.name + ".lock"))
    temporary = external_target(path.with_name("." + path.name + "-" + uuid.uuid4().hex + ".tmp"))
    lock = lock_path.open("xb")
    try:
        with lock:
            lock.write(b"presentation control writer\n")
        raw = path.read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        if digest != expected:
            raise ValueError("stale control SHA-256, inspect the current state before retrying")
        current = json.loads(raw.decode("utf-8"))
        updated = transform(current)
        data = encoded(updated)
        history.mkdir(exist_ok=True)
        previous = external_target(history / (digest + ".json"))
        if previous.exists():
            if previous.read_bytes() != raw:
                raise ValueError("control history does not match its recorded identity")
        else:
            with previous.open("xb") as stream:
                stream.write(raw)
        with temporary.open("xb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise ValueError("control changed during the operation")
        os.replace(temporary, path)
        return updated
    finally:
        temporary.unlink(missing_ok=True)
        lock_path.unlink(missing_ok=True)


def controller_action(state, action):
    import presentation_controller as controller
    action = dict(action)
    name = action.pop("action", None)
    allowed = {"reserve_call", "record_call", "start_repair", "sync_document", "bind_artifact",
               "record_check", "record_finding", "resolve_finding"}
    if name not in allowed:
        raise ValueError("unknown control action")
    return getattr(controller, name)(state, **action)


def parser():
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--template", type=Path, default=DEFAULT_TEMPLATE)
    commands = result.add_subparsers(dest="command", required=True)
    commands.add_parser("capabilities")
    catalog_import = commands.add_parser("catalog-import", help="Atomize native projects into an engine asset catalog")
    catalog_import.add_argument("--sources", required=True, type=Path)
    catalog_import.add_argument("--output", required=True, type=Path)
    catalog = commands.add_parser("catalog", help="Discover native pages, groups and atoms")
    catalog.add_argument("identifier", nargs="?")
    catalog.add_argument("--catalog", required=True, type=Path)
    catalog.add_argument("--query")
    catalog.add_argument("--kind")
    catalog.add_argument("--source")
    catalog.add_argument("--offset", type=int, default=0)
    catalog.add_argument("--limit", type=int, default=50)
    catalog.add_argument("--include-hidden", action="store_true")
    catalog_build = commands.add_parser("catalog-build", help="Instantiate registered native assets using engine layout")
    catalog_build.add_argument("--catalog", required=True, type=Path)
    catalog_build.add_argument("--request", required=True, type=Path)
    catalog_build.add_argument("--pptx", required=True, type=Path)
    palettes = commands.add_parser("palettes", help="Discover global semantic colour standards and provenance")
    palettes.add_argument("identifier", nargs="?")
    charts = commands.add_parser("chart-assets", help="Discover data chart contracts and readiness")
    charts.add_argument("identifier", nargs="?")
    charts.add_argument("--category")
    charts.add_argument("--query", default="")
    charts.add_argument("--executable", choices=("true", "false"))
    charts.add_argument("--offset", type=int, default=0)
    charts.add_argument("--limit", type=int, default=50)
    chart_build = commands.add_parser("chart-build", help="Compile registered chart data through computed layout")
    chart_build.add_argument("--request", required=True, type=Path)
    chart_build.add_argument("--output", required=True, type=Path)
    chart_build.add_argument("--pptx", type=Path)
    storybook = commands.add_parser("storybook-export", help="Export an offline engine component browser")
    storybook.add_argument("--catalog", type=Path)
    storybook.add_argument("--output", required=True, type=Path)
    storybook.add_argument("--title", default="PPT Storybook")
    native_import = commands.add_parser("native-import", help="Extract a PPTX into a self-contained native configuration")
    native_import.add_argument("--input", required=True, type=Path)
    native_import.add_argument("--output", required=True, type=Path)
    native_import.add_argument("--slides", nargs="+", type=int,
                               help="1-based review focus; all slides and dependencies remain in the project")
    native_inspect = commands.add_parser("native-inspect", help="Validate and summarize a native project without writing")
    native_inspect.add_argument("--project", required=True, type=Path)
    native_build = commands.add_parser("native-build", help="Reconstruct a PPTX from native configuration")
    native_build.add_argument("--project", required=True, type=Path)
    native_build.add_argument("--pptx", required=True, type=Path)
    components = commands.add_parser("components")
    components.add_argument("name", nargs="?")
    components.add_argument("--tokens", type=Path)
    layouts = commands.add_parser("layouts")
    layouts.add_argument("name", nargs="?")
    layouts.add_argument("--tokens", type=Path)
    icons = commands.add_parser("icons")
    icons.add_argument("key", nargs="?")
    icons.add_argument("--tokens", type=Path)
    icons.add_argument("--query", default="")
    icons.add_argument("--offset", type=int, default=0)
    icons.add_argument("--limit", type=int, default=20)
    typography = commands.add_parser("typography")
    typography_source = typography.add_mutually_exclusive_group()
    typography_source.add_argument("--tokens", type=Path)
    typography_source.add_argument("--profile")
    typography.add_argument("--example", action="store_true")
    library = commands.add_parser("library")
    library.add_argument("identifier", nargs="?")
    for field in ("kind", "relationship", "status", "query"):
        library.add_argument("--" + field)
    library.add_argument("--executable", choices=("true", "false"))
    library.add_argument("--offset", type=int, default=0)
    library.add_argument("--limit", type=int, default=20)
    compose = commands.add_parser("compose")
    compose.add_argument("--input", required=True, type=Path)
    compose.add_argument("--output", required=True, type=Path)
    compose.add_argument("--profile")
    compose.add_argument("--tokens", type=Path)
    compose.add_argument("--assets", type=Path)
    inventory = commands.add_parser("inventory")
    inventory.add_argument("--family")
    inventory.add_argument("--variants", action="store_true")
    inventory.add_argument("--offset", type=int, default=0)
    inventory.add_argument("--limit", type=int, default=20)
    query = commands.add_parser("query")
    query.add_argument("--task", default="")
    query.add_argument("--limit", type=int, default=5)
    query.add_argument("--variants", action="store_true")
    describe = commands.add_parser("describe")
    describe.add_argument("family")
    describe.add_argument("--variant")
    for name in ("validate", "facts", "build", "patch", "control-init"):
        command = commands.add_parser(name)
        command.add_argument("--input", required=True, type=Path)
        if name in {"build", "patch", "control-init"}:
            command.add_argument("--output", required=True, type=Path)
    build = commands.choices["build"]
    build.add_argument("--assets", type=Path)
    build.add_argument("--tokens", type=Path)
    build.add_argument("--pptx", type=Path)
    build.add_argument("--geometry-policy", choices=("computed", "legacy-replay"), default="computed")
    patch = commands.choices["patch"]
    patch.add_argument("--patch", required=True, type=Path)
    patch.add_argument("--expected-revision", required=True, type=int)
    patch.add_argument("--operation-id", required=True)
    initial = commands.choices["control-init"]
    initial.add_argument("--max-calls", type=int, default=40)
    initial.add_argument("--max-repairs", type=int, default=2)
    initial.add_argument("--max-seconds", type=float, default=1800)
    initial.add_argument("--required-check", action="append", default=[])
    control = commands.add_parser("control")
    control.add_argument("--state", required=True, type=Path)
    control.add_argument("--expected-sha256", required=True)
    control.add_argument("--action", required=True, type=Path)
    status = commands.add_parser("status")
    status.add_argument("--state", required=True, type=Path)
    status.add_argument("--input", type=Path)
    return result


def build_author(source, args, *, asset_root=None):
    """Use the same compiler/export path for authored decks and registered chart stories."""
    external_target(args.output)
    if args.pptx:
        target = external_target(args.pptx)
        if target.exists():
            raise ValueError("PPTX output already exists")
    import presentation_compiler as compiler
    import ppt_runtime
    receipt = compiler.build_project(source, args.output, template_root=args.template,
                                     tokens=args.tokens, asset_root=asset_root,
                                     geometry_policy=args.geometry_policy)
    project = args.output.resolve()
    result = {"project": str(project), "project_id": receipt["project_id"],
              "revision": receipt["revision"], "page_count": receipt["page_count"],
              "input_sha256": receipt["input_sha256"], "runtime_sha256": receipt["runtime_sha256"],
              "tokens_sha256": receipt["tokens_sha256"], "geometry_policy": receipt["geometry_policy"],
              "receipt_ref": str(project / "engine-receipt.json"), "object_map_ref": str(project / "object-map.json")}
    if "asset_usage" in receipt:
        result["asset_usage"] = receipt["asset_usage"]
    if args.pptx:
        check = ppt_runtime.check_project(args.output)
        inspection = ppt_runtime.export_project(args.output, args.pptx, args.output / "tokens.json")
        result.update(pptx=str(args.pptx.resolve()), check_status=check["status"],
                      check_ref=str(project / "validation" / "ppt-check.json"),
                      inspection={"status": inspection["status"], "counts": inspection["counts"],
                                  "detail_ref": str(project / "validation" / "ppt-export.json")})
    return result


def execute(args):
    if args.command == "catalog-import":
        from presentation_native_catalog import build_native_catalog
        sources = read_json(args.sources)
        if isinstance(sources, dict):
            if set(sources) != {"sources"}:
                raise ValueError("catalog sources object requires only sources")
            sources = sources["sources"]
        if not isinstance(sources, list):
            raise ValueError("catalog sources must be a list")
        return build_native_catalog(sources, args.output)
    if args.command == "catalog":
        from presentation_native_catalog import list_native_assets, describe_native_asset
        if args.identifier:
            return describe_native_asset(args.catalog, args.identifier)
        return list_native_assets(args.catalog, query=args.query, kind=args.kind, source=args.source,
                                  offset=args.offset, limit=args.limit, include_hidden=args.include_hidden)
    if args.command == "catalog-build":
        from presentation_native_catalog import instantiate_native_assets
        request = read_json(args.request)
        if not isinstance(request, dict) or set(request) - {"asset_ids", "columns", "texts"} or "asset_ids" not in request:
            raise ValueError("catalog request requires asset_ids and optional columns/texts; arbitrary geometry is not accepted")
        return instantiate_native_assets(args.catalog, request["asset_ids"], args.pptx,
                                         columns=request.get("columns"), texts=request.get("texts"))
    if args.command == "palettes":
        from presentation_palette import palette_catalog, describe_palette
        if args.identifier:
            return describe_palette(args.identifier)
        records = palette_catalog()
        return {"total": len(records), "items": records}
    if args.command == "chart-assets":
        from presentation_chart_assets import chart_assets, describe_chart_asset
        if args.identifier:
            return describe_chart_asset(args.identifier)
        if args.offset < 0 or not 1 <= args.limit <= 100:
            raise ValueError("chart-assets offset must be nonnegative and limit 1..100")
        if len(args.query) > 256:
            raise ValueError("chart-assets query must be at most 256 characters")
        wanted = None if args.executable is None else args.executable == "true"
        terms = args.query.casefold().split()
        records = [r for r in chart_assets() if
                   (wanted is None or r["executable"] == wanted) and
                   (args.category is None or args.category in r["categories"]) and
                   all(t in json.dumps(r, ensure_ascii=False).casefold() for t in terms)]
        return {"total": len(records), "offset": args.offset, "limit": args.limit,
                "items": records[args.offset:args.offset + args.limit]}
    if args.command == "chart-build":
        from presentation_chart_assets import chart_story
        request = read_json(args.request)
        if not isinstance(request, dict) or set(request) - {"asset", "data", "options", "palette_id"} or not {"asset", "data"} <= set(request):
            raise ValueError("chart request requires asset/data and optional options/palette_id")
        author = chart_story(request["asset"], data=request["data"], options=request.get("options"))
        if "palette_id" in request:
            author["brief"]["palette_id"] = request["palette_id"]
        args.tokens, args.assets, args.geometry_policy = None, None, "computed"
        return build_author(author, args, asset_root=args.request.parent)
    if args.command == "storybook-export":
        from presentation_storybook import build_storybook
        return build_storybook(args.catalog, args.output, template=args.template, title=args.title)
    if args.command == "native-import":
        from presentation_native import extract_native_project
        return extract_native_project(args.input, args.output, slides=args.slides)
    if args.command == "native-inspect":
        from presentation_native import inspect_native_project
        return inspect_native_project(args.project)
    if args.command == "native-build":
        from presentation_native import rebuild_native_project
        return rebuild_native_project(args.project, args.pptx)
    if args.command == "library":
        from presentation_library import library
        return library(args.template, identifier=args.identifier, kind=args.kind,
                       relationship=args.relationship, status=args.status, query=args.query or "",
                       executable=None if args.executable is None else args.executable == "true",
                       offset=args.offset, limit=args.limit)
    if args.command == "compose":
        target = external_target(args.output)
        if target.exists():
            raise ValueError("author output already exists")
        from presentation_recipes import compose_document
        author = compose_document(read_json(args.input), template_root=args.template,
                                  tokens=args.tokens, profile=args.profile,
                                  asset_root=args.assets or args.input.parent)
        output = write_new_json(args.output, author)
        return {"output": str(output), "project_id": author["project_id"], "revision": author["revision"],
                "page_count": len(author["pages"]), "sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
                "design_profile": author["brief"]["design_profile"],
                "recipe_usage": author["brief"]["recipe_usage"], "validation": "normal compiler measured all lowered scenes"}
    if args.command == "capabilities":
        from presentation_composition import COMPONENTS
        return {"schema_version": "0.1", "author_document": "0.1",
                "page_kinds": ["scene", "template", "layout"],
                "storybook": {"export": "storybook-export --catalog CATALOG --output NEW_SITE",
                    "native_discovery": "catalog [ID] --catalog CATALOG [--kind page|group|atom]",
                    "native_import": "catalog-import --sources SOURCES_JSON --output NEW_CATALOG",
                    "native_build": "catalog-build --catalog CATALOG --request REQUEST_JSON --pptx NEW_PPTX",
                    "chart_discovery": "chart-assets [ID] [--category TYPE] [--executable true]",
                    "palette_discovery": "palettes [ID]; author brief.palette_id or chart request palette_id",
                    "chart_build": "chart-build --request REQUEST_JSON --output NEW_PROJECT [--pptx NEW_PPTX]",
                    "new_author_rule": "select registered assets and provide content/data/constraints; all drawing is computed by engine",
                    "offline_browser": "search, source-region/engine previews, parameter requests; generation via normal CLI"},
                "native_roundtrip": {
                    "import": "native-import --input SOURCE_PPTX --output NEW_PROJECT [--slides 4]",
                    "inspect": "native-inspect --project PROJECT",
                    "build": "native-build --project PROJECT --pptx NEW_PPTX",
                    "scope": "full-package XML configuration replay with native geometry/text edits; no automatic reflow",
                    "source_required_for_rebuild": False,
                    "acceptance": "requires same-renderer visual comparison and target-operation evidence"},
                "geometry_policy": {"default": "computed", "historical_reproduction": "--geometry-policy legacy-replay",
                                    "computed_sources": ["layout tree", "parameterized template", "saved recipe_source replay"],
                                    "raw_scene_frames": "rejected in computed mode"},
                "layouts": {"command": "layouts [name] [--tokens PATH]", "layout_version": "0.1",
                            "source": "persistent author tree, re-solved on each build", "output": "layout/*.report.json and *.scene.json"},
                "icons": "icons [key] [--query TEXT] [--offset N --limit N] [--tokens PATH]",
                "design_preferences": {"automatic_fill": "solid", "gradient": "lowest preference",
                                       "scope": "layout/topology defaults; no general design scoring optimizer"},
                "scene_elements": ["text", "shape", "chart", "image", "connector", "group", "component"],
                "components": {"command": "components [name] [--tokens PATH]", "contract": "0.1",
                               "names": list(COMPONENTS)},
                "typography": {"command": "typography [--tokens PATH | --profile report-14pt] [--example]",
                               "units": "SVG px; named profile also reports native pt", "global_field": "brief.design_profile"},
                "library": "library [ID] [--kind KIND] [--relationship TYPE] [--status STATUS] [--query TEXT] [--offset N --limit N]",
                "compose": "compose --input REQUEST --output NEW_AUTHOR [--profile report-14pt] [--tokens PATH]",
                "asset_discovery": {"inventory": "inventory [--variants] [--family ID] [--offset N] [--limit N]",
                                    "query": "query --task TEXT [--variants] [--limit N]",
                                    "detail": "describe FAMILY [--variant ID]",
                                    "match_method": "declared metadata word and Chinese-bigram overlap"},
                "workflow": "host-driven, checks and budgets cover registered operations",
                "template": str(args.template), "native_editing": "requires target-operation evidence"}
    if args.command == "components":
        from presentation_composition import component_catalog
        _, _, values = load_template(args.template, args.tokens)
        return component_catalog(args.name, values)
    if args.command == "layouts":
        from presentation_layout import layout_catalog
        _, _, values = load_template(args.template, args.tokens)
        return layout_catalog(args.name, values)
    if args.command == "icons":
        from presentation_icons import icon_catalog
        _, _, values = load_template(args.template, args.tokens)
        return icon_catalog(args.key, values, offset=args.offset, limit=args.limit, query=args.query)
    if args.command == "typography":
        if args.profile:
            from presentation_text_profile import describe_text_profile, text_profile_story
            return text_profile_story(args.profile) if args.example else describe_text_profile(args.profile)
        if args.example:
            raise ValueError("typography --example requires --profile")
        from presentation_typography import typography_catalog
        _, _, values = load_template(args.template, args.tokens)
        return typography_catalog(values)
    if args.command == "inventory":
        return inventory_assets(args.template, family=args.family, variants=args.variants,
                                offset=args.offset, limit=args.limit)
    if args.command == "query":
        return query_assets(args.template, args.task, args.limit, variants=args.variants)
    if args.command == "describe":
        root, catalog, _ = load_template(args.template)
        family = catalog["families"][args.family]
        if args.variant:
            return {"family": args.family, "variant": args.variant,
                    "definition": family["variants"][args.variant],
                    "prototype_content": family.get("prototype_content", {})}
        return {**asset_summary(root, catalog, args.family, family), "definition": family}
    if args.command == "control":
        state = mutate_control(args.state, args.expected_sha256,
                               lambda current: controller_action(current, read_json(args.action)))
        import presentation_controller as controller
        return {"state": str(args.state), "sha256": hashlib.sha256(args.state.read_bytes()).hexdigest(),
                "release": controller.evaluate_release(state)}
    if args.command == "status":
        import presentation_controller as controller
        state = read_json(args.state)
        result = controller.evaluate_release(state, read_json(args.input) if args.input else None)
        result["state_sha256"] = hashlib.sha256(args.state.read_bytes()).hexdigest()
        return result

    import presentation_document as document
    source = read_json(args.input)
    document.validate_document(source)
    if args.command == "validate":
        return {"valid": True, "project_id": source["project_id"], "revision": source["revision"],
                "pages": len(source["pages"])}
    if args.command == "facts":
        return {"facts": document.evaluate_facts(source)}
    if args.command == "patch":
        updated = document.apply_patch_to_document(source, read_json(args.patch),
                                                   args.expected_revision, args.operation_id)
        output = write_new_json(args.output, updated)
        return {"output": str(output), "revision": updated["revision"],
                "sha256": hashlib.sha256(output.read_bytes()).hexdigest()}
    if args.command == "control-init":
        import presentation_controller as controller
        state = controller.new_control_state(source, max_calls=args.max_calls,
                                             max_repairs=args.max_repairs, max_seconds=args.max_seconds,
                                             required_checks=args.required_check or None)
        output = write_new_json(args.output, state)
        return {"state": str(output), "sha256": hashlib.sha256(output.read_bytes()).hexdigest()}
    if args.command == "build":
        return build_author(source, args, asset_root=args.assets or args.input.parent)
    raise ValueError("unknown engine command")


def main(argv=None):
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    args = parser().parse_args(argv)
    try:
        print(json.dumps(execute(args), ensure_ascii=False, indent=2, allow_nan=False))
        return 0
    except (ValueError, KeyError, TypeError, OSError) as exc:
        result = {"valid": False, "error": str(exc)}
        if isinstance(getattr(exc, "diagnostic", None), dict):
            result["diagnostic"] = exc.diagnostic
        print(json.dumps(result, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
