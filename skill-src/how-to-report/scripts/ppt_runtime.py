#!/usr/bin/env python3
"""Check and export local SVG projects with the extracted PPT technology.

The component is package-local. All visible template assets come from the
selected user template. Output files belong outside the installed Skill.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import os
import posixpath
from pathlib import Path
import re
import sys
import tempfile
from xml.etree import ElementTree as ET
from zipfile import BadZipFile, ZipFile

from write_boundary import require_external_write

SKILL_ROOT = Path(__file__).resolve().parents[1]
ENGINE = SKILL_ROOT / "runtime" / "ppt-engine"
THEME_SLOTS = ("dk1", "lt1", "dk2", "lt2", "accent1", "accent2", "accent3",
               "accent4", "accent5", "accent6", "hlink", "folHlink")
NS = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main",
      "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
      "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"}


class PptRuntimeError(ValueError):
    """A supplied project or its current evidence cannot be exported."""


def _engine_modules():
    script_root = ENGINE / "scripts"
    for source in script_root.rglob("*.py"):
        parts = list(source.relative_to(script_root).with_suffix("").parts)
        if parts[-1] == "__init__":
            parts.pop()
        loaded = sys.modules.get(".".join(parts))
        if loaded is not None and Path(getattr(loaded, "__file__", "")).resolve() != source.resolve():
            raise PptRuntimeError("conflicting PPT module already loaded; use the package CLI in a fresh process")
    scripts = str(script_root)
    if scripts not in sys.path:
        sys.path.insert(0, scripts)
    from svg_quality.checker import SVGQualityChecker
    from svg_quality import checker as checker_module
    required_helpers = (
        "_unsafe_exported_font_faces", "_estimate_single_line_text_frame_width",
        "_parse_project_font_weight", "_parse_project_geometry_length",
        "_parse_project_text_anchor", "_resolve_project_font_sizes",
        "_resolve_project_letter_spacings",
    )
    missing = [name for name in required_helpers if getattr(checker_module, name, None) is None]
    if missing:
        raise PptRuntimeError(f"required font/measurement helpers unavailable: {missing}")
    from svg_to_pptx.pptx_package.builder import create_pptx_with_native_svg
    from svg_to_pptx.drawingml.theme_colors import ThemeColorSpec
    from svg_to_pptx.drawingml.theme_fonts import (
        MasterTextStyleSpec, ThemeFontFace, ThemeFontSpec,
    )
    return (SVGQualityChecker, create_pptx_with_native_svg, ThemeColorSpec,
            ThemeFontFace, ThemeFontSpec, MasterTextStyleSpec)


def _json_hash(value):
    data = json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def _read_tokens(tokens):
    if isinstance(tokens, (str, Path)):
        tokens = json.loads(Path(tokens).read_text(encoding="utf-8"))
    if not isinstance(tokens, dict):
        raise PptRuntimeError("tokens must be a JSON object or a JSON file")
    return copy.deepcopy(tokens)


def _canvas(tokens):
    canvas = tokens.get("canvas", tokens.get("layout", {}).get("canvas", {}))
    width, height = canvas.get("width", 1280), canvas.get("height", 720)
    for name, value in (("width", width), ("height", height)):
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
            raise PptRuntimeError(f"canvas.{name} must be finite and positive")
    if abs(width / height - 16 / 9) > 0.000001:
        raise PptRuntimeError("canvas must use the confirmed 16:9 ratio")
    return width, height


def _theme_values(tokens):
    slots = tokens.get("theme", {}).get("slots")
    if not isinstance(slots, dict) or set(slots) != set(THEME_SLOTS):
        raise PptRuntimeError("theme.slots must contain all twelve PowerPoint color slots")
    colors = {}
    for key, value in slots.items():
        if not isinstance(value, str) or not re.fullmatch(r"#?[0-9a-fA-F]{6}", value):
            raise PptRuntimeError(f"theme.slots.{key} must be a six-digit HEX color")
        colors[key] = value.lstrip("#").upper()
    font = tokens.get("font", {})
    families = font.get("families", {})
    title = families.get("title", families.get("heading"))
    body = families.get("body")
    latin = families.get("latin", body)
    if any(not isinstance(value, str) or not value.strip() for value in (title, body, latin)):
        raise PptRuntimeError("font.families requires title, body and a usable latin family")
    sizes = font.get("sizes", {})
    title_size, body_size = sizes.get("title"), sizes.get("body")
    for name, value in (("title", title_size), ("body", body_size)):
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
            raise PptRuntimeError(f"font.sizes.{name} must be finite and positive")
    return colors, title, body, latin, title_size, body_size


def _project(project):
    root = require_external_write(project)
    if not root.is_dir() or not (root / "svg_output").is_dir():
        raise PptRuntimeError("project must contain svg_output/")
    return root


def _svg_files(project):
    files = sorted((project / "svg_output").glob("*.svg"))
    if not files:
        raise PptRuntimeError("svg_output contains no SVG slides")
    return files


def _fingerprint(project, excluded=()):
    """Bind sources, local assets, sidecars and notes while excluding results."""
    ignored = {"validation", "exports", ".preview", ".review", ".runtime", "__pycache__"}
    resources = set()
    from resource_paths import external_image_reference_path
    for svg in _svg_files(project):
        for item in ET.parse(svg).getroot().iter():
            if item.tag.rsplit("}", 1)[-1] != "image":
                continue
            href = item.get("href") or item.get("{http://www.w3.org/1999/xlink}href") or ""
            candidate = external_image_reference_path(svg.parent, href, project_root=project)
            if candidate is not None:
                resources.add(candidate)
    excluded = {Path(path) for path in excluded}
    records = {}
    for path in sorted(project.rglob("*")):
        relative = path.relative_to(project)
        if any(path == directory or directory in path.parents for directory in excluded):
            continue
        if (relative.parts[0] in ignored or "__pycache__" in relative.parts) and path.resolve() not in resources:
            continue
        if path.is_symlink() or getattr(path.lstat(), "st_file_attributes", 0) & 0x400:
            raise PptRuntimeError(f"linked source path is unsupported: {relative}")
        if path.is_file():
            records[relative.as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return records


def _runtime_fingerprint():
    files = {"scripts/ppt_runtime.py": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    for path in sorted(ENGINE.rglob("*")):
        if path.is_file() and "__pycache__" not in path.parts and path.suffix not in {".pyc", ".pyo"}:
            files[path.relative_to(ENGINE).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return _json_hash(files)


def _source_snapshot(root, destination, sources):
    """Compile verified immutable copies, including project-local image inputs."""
    destination.mkdir()
    for relative, expected_hash in sources.items():
        data = (root / relative).read_bytes()
        if hashlib.sha256(data).hexdigest() != expected_hash:
            raise PptRuntimeError("project changed while copying export inputs")
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    return destination


def _write_json(path, value):
    path = require_external_write(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", prefix=".htr-json-",
                                     dir=path.parent, delete=False) as temporary:
        candidate = Path(temporary.name)
        try:
            temporary.write(json.dumps(value, ensure_ascii=False, indent=2) + "\n")
            temporary.flush()
            os.fsync(temporary.fileno())
        except BaseException:
            temporary.close()
            candidate.unlink(missing_ok=True)
            raise
    try:
        os.replace(candidate, path)
    finally:
        candidate.unlink(missing_ok=True)


def _notes(root, supplied=None):
    notes = supplied if supplied is not None else {
        path.stem: path.read_text(encoding="utf-8")
        for path in (root / "notes").glob("*.md") if path.stem != "total"
    }
    if not isinstance(notes, dict) or any(not isinstance(key, str) or not isinstance(value, str)
                                          for key, value in notes.items()):
        raise PptRuntimeError("notes must map slide stems to text")
    return copy.deepcopy(notes)


def _publish_candidate(candidate, output):
    """Publish a complete file without replacing another exporter's file."""
    if os.name == "nt":
        # Windows rename fails when the destination exists.
        os.rename(candidate, output)
    else:
        # Linking is an atomic, no-replace publication on POSIX.
        os.link(candidate, output)


def _check_canvas_background(path, width, height):
    root = ET.parse(path).getroot()
    found = False
    for item in root.iter():
        if item.tag.rsplit("}", 1)[-1] != "rect":
            continue
        try:
            full = (float(item.get("x", 0)) == 0 and float(item.get("y", 0)) == 0
                    and float(item.get("width", 0)) == width and float(item.get("height", 0)) == height)
        except ValueError:
            continue
        if full:
            fill = item.get("fill", "").upper()
            opaque = item.get("opacity", "1") == "1" and item.get("fill-opacity", "1") == "1"
            if fill not in {"#FFFFFF", "#FFF", "WHITE"} or not opaque or item.get("transform"):
                raise PptRuntimeError(f"{path.name}: full-canvas background must be white")
            found = True
    if not found:
        raise PptRuntimeError(f"{path.name}: missing explicit white canvas rectangle")


def check_project(project, tokens=None, notes=None):
    """Run the retained checker and record exact current input fingerprints."""
    root = _project(project)
    token_source = tokens if tokens is not None else root / "tokens.json"
    token_data = _read_tokens(token_source)
    note_data = _notes(root, notes)
    _theme_values(token_data)
    width, height = _canvas(token_data)
    checker_class, *_ = _engine_modules()
    runtime_identity = _runtime_fingerprint()
    before = _fingerprint(root)
    checker = checker_class()
    checker.scan_banner = False
    from svg_to_pptx.pptx_package.template_structure import parse_template_slides
    parse_template_slides(_svg_files(root))
    results = []
    for path in _svg_files(root):
        _check_canvas_background(path, width, height)
        results.append(checker.check_file(str(path), expected_viewbox=f"0 0 {width:g} {height:g}"))
    errors = [{"file": r["file"], "errors": r["errors"]} for r in results if r["errors"]]
    report = {"schema": "how-to-report.ppt-check.v1", "status": "fail" if errors else "pass",
              "sources": before, "tokens_sha256": _json_hash(token_data),
              "notes_sha256": _json_hash(note_data),
              "runtime_sha256": runtime_identity,
              "files": results, "errors": errors,
              "scope": "SVG contracts, canvas and exact local inputs; visual review is separate"}
    if before != _fingerprint(root):
        raise PptRuntimeError("project changed during checking")
    if token_data != _read_tokens(token_source) or note_data != _notes(root, notes):
        raise PptRuntimeError("tokens or notes changed during checking")
    if runtime_identity != _runtime_fingerprint():
        raise PptRuntimeError("PPT runtime changed during checking")
    _write_json(root / "validation" / "ppt-check.json", report)
    if errors:
        raise PptRuntimeError(json.dumps(errors, ensure_ascii=False))
    return report


def inspect_pptx(pptx, tokens=None):
    """Read actual OOXML, including every theme, canvas, text and shape frame."""
    errors = []
    themes, slides, masters, media = [], [], [], []
    table_counts = {}
    token_data = _read_tokens(tokens) if tokens is not None else None
    expected = _theme_values(token_data) if token_data else None
    with ZipFile(pptx) as package:
        presentation = ET.fromstring(package.read("ppt/presentation.xml"))
        size = presentation.find("p:sldSz", NS)
        if size is None:
            raise PptRuntimeError("PPTX presentation is missing its canvas size")
        dimensions = {"cx": int(size.get("cx")), "cy": int(size.get("cy"))}
        relationships = ET.fromstring(package.read("ppt/_rels/presentation.xml.rels"))
        targets = {rel.get("Id"): posixpath.normpath(posixpath.join("ppt", rel.get("Target", ""))).lstrip("/")
                   for rel in relationships if rel.get("TargetMode") != "External"}
        ordered_parts = []
        for slide in presentation.findall("p:sldIdLst/p:sldId", NS):
            part = targets.get(slide.get(f"{{{NS['r']}}}id"))
            if not part or part not in package.namelist():
                raise PptRuntimeError("PPTX slide order references a missing slide part")
            ordered_parts.append(part)
        if token_data:
            width, height = _canvas(token_data)
            if dimensions != {"cx": round(width * 9525), "cy": round(height * 9525)}:
                errors.append("PPTX canvas differs from tokens")
        for name in sorted(package.namelist()):
            part_xml = ET.fromstring(package.read(name)) if name.startswith("ppt/") and name.endswith(".xml") else None
            if part_xml is not None:
                directions = [(node, "ang") for node in part_xml.findall(".//a:lin", NS)]
                directions.extend((node, "dir") for node in part_xml.findall(".//a:outerShdw", NS))
                for direction, attribute in directions:
                    try:
                        angle = int(direction.get(attribute, "0"))
                    except ValueError:
                        angle = -1
                    if not 0 <= angle < 21600000:
                        errors.append(f"{name}: DrawingML angle violates ST_PositiveFixedAngle (0..21599999)")
            if re.fullmatch(r"ppt/theme/theme\d+\.xml", name):
                xml = part_xml
                scheme = xml.find("a:themeElements/a:clrScheme", NS)
                colors = {}
                for slot in scheme:
                    child = next(iter(slot), None)
                    colors[slot.tag.rsplit("}", 1)[-1]] = child.get("val") if child.tag.endswith("srgbClr") else child.get("lastClr")
                fonts = {}
                for key in ("major", "minor"):
                    el = xml.find(f"a:themeElements/a:fontScheme/a:{key}Font", NS)
                    fonts[key] = {part: el.find(f"a:{part}", NS).get("typeface") for part in ("latin", "ea", "cs")}
                themes.append({"part": name, "colors": colors, "fonts": fonts})
                if expected:
                    colors_expected, title, body, latin, *_ = expected
                    if colors != colors_expected:
                        errors.append(f"{name}: color slots differ from tokens")
                    for key, family in (("major", title), ("minor", body)):
                        if fonts[key] != {"latin": latin, "ea": family, "cs": latin}:
                            errors.append(f"{name}: {key} fonts differ from tokens")
            elif re.fullmatch(r"ppt/slideMasters/slideMaster\d+\.xml", name):
                xml = part_xml
                sizes = {}
                for key in ("title", "body"):
                    run = xml.find(f"p:txStyles/p:{key}Style/a:lvl1pPr/a:defRPr", NS)
                    sizes[key] = int(run.get("sz")) if run is not None and run.get("sz") else None
                masters.append({"part": name, "level1_font_sizes_hpt": sizes})
                if expected:
                    title_size, body_size = expected[-2:]
                    if sizes != {"title": round(title_size * 75), "body": round(body_size * 75)}:
                        errors.append(f"{name}: master title/body sizes differ from tokens")
            elif re.fullmatch(r"ppt/slides/slide\d+\.xml", name):
                xml = part_xml
                table_counts[name] = len(xml.findall(".//a:tbl", NS))
                shapes = []
                for shape in xml.findall("p:cSld/p:spTree/*", NS):
                    identity = shape.find(".//p:cNvPr", NS)
                    frame = shape.find(".//a:xfrm", NS)
                    if frame is None:
                        frame = shape.find("p:xfrm", NS)
                    geometry = None
                    if frame is not None:
                        offset, extent = frame.find("a:off", NS), frame.find("a:ext", NS)
                        if offset is not None and extent is not None:
                            geometry = {"x": int(offset.get("x")) / 9525,
                                        "y": int(offset.get("y")) / 9525,
                                        "width": int(extent.get("cx")) / 9525,
                                        "height": int(extent.get("cy")) / 9525}
                    shapes.append({"name": identity.get("name") if identity is not None else None,
                                   "text": [t.text or "" for t in shape.findall(".//a:t", NS)],
                                   "geometry_px": geometry,
                                   "font_sizes_pt": sorted({int(t.get("sz")) / 100 for t in shape.findall(".//a:rPr", NS) if t.get("sz")}),
                                   "typefaces": sorted({t.get("typeface") for t in shape.findall(".//a:latin", NS) + shape.findall(".//a:ea", NS) if t.get("typeface")}),
                                   "frame": ET.tostring(frame, encoding="unicode") if frame is not None else None})
                slides.append({"part": name, "shapes": shapes})
            elif name.startswith("ppt/media/"):
                media.append({"part": name, "sha256": hashlib.sha256(package.read(name)).hexdigest()})
        external = []
        for name in package.namelist():
            if name.endswith(".rels"):
                for rel in ET.fromstring(package.read(name)):
                    if rel.get("TargetMode") == "External":
                        external.append({"part": name, "target": rel.get("Target")})
        slides_by_part = {slide["part"]: slide for slide in slides}
        orphan_slide_parts = sorted(set(slides_by_part) - set(ordered_parts))
        slides = [slides_by_part[name] for name in ordered_parts]
        counts = {"slides": len(slides),
                  "masters": sum(bool(re.fullmatch(r"ppt/slideMasters/slideMaster\d+\.xml", n)) for n in package.namelist()),
                  "layouts": sum(bool(re.fullmatch(r"ppt/slideLayouts/slideLayout\d+\.xml", n)) for n in package.namelist())}
        chart_parts = [n for n in package.namelist() if re.fullmatch(r"ppt/charts/(?:chart|chartEx)\d+\.xml", n)]
    return {"schema": "how-to-report.ppt-inspect.v1", "status": "fail" if errors else "pass",
            "sha256": hashlib.sha256(Path(pptx).read_bytes()).hexdigest(),
            "canvas": dimensions, "counts": counts, "themes": themes,
            "slides": slides, "masters": masters, "media": media,
            "native_objects": {"charts": len(chart_parts), "tables": sum(table_counts.get(name, 0) for name in ordered_parts)},
            "orphan_slide_parts": orphan_slide_parts,
            "external_relationships": external, "errors": errors}


def export_project(project, output, tokens, notes=None):
    """Export only current checked sources, then compare the actual theme."""
    root = _project(project)
    output = require_external_write(output)
    if output.exists():
        raise PptRuntimeError(f"output already exists: {output}")
    token_data = _read_tokens(tokens)
    note_data = _notes(root, notes)
    report_path = root / "validation" / "ppt-check.json"
    if not report_path.is_file():
        raise PptRuntimeError("run check before export")
    report = json.loads(report_path.read_text(encoding="utf-8"))
    _, builder, colors_class, face_class, font_class, style_class = _engine_modules()
    current = _fingerprint(root)
    runtime_identity = _runtime_fingerprint()
    if (report.get("status") != "pass" or report.get("sources") != current
            or report.get("tokens_sha256") != _json_hash(token_data)
            or report.get("notes_sha256") != _json_hash(note_data)
            or report.get("runtime_sha256") != runtime_identity):
        raise PptRuntimeError("current sources, tokens, notes or runtime differ from the passed check")
    colors, title, body, latin, title_size, body_size = _theme_values(token_data)
    roles = {"bg": colors["lt1"], "text": colors["dk1"], "primary": colors["accent1"]}
    color_spec = colors_class(colors, roles, {"bg": "lt1", "text": "dk1", "primary": "accent1"})
    font_spec = font_class(face_class(latin, title, latin), face_class(latin, body, latin), title, body)
    text_style = style_class(round(title_size * 75), round(body_size * 75))
    width, height = _canvas(token_data)
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".htr-ppt-", dir=output.parent) as temporary:
        candidate = Path(temporary) / "result.pptx"
        snapshot = _source_snapshot(root, Path(temporary) / "sources", current)
        ok = builder(_svg_files(snapshot), candidate, resource_root=snapshot,
                     verbose=False, transition=None, native_objects=True, notes=note_data,
                     theme_color_spec=color_spec, theme_font_spec=font_spec,
                     master_text_style_spec=text_style, expected_viewbox=f"0 0 {width:g} {height:g}",
                     workers=1, primary_language="zh-CN")
        if not ok:
            raise PptRuntimeError("native PPTX compiler did not complete")
        inspection = inspect_pptx(candidate, token_data)
        if inspection["status"] != "pass":
            raise PptRuntimeError(json.dumps(inspection["errors"], ensure_ascii=False))
        inspection["checked_inputs"] = {"sources": current, "tokens_sha256": _json_hash(token_data),
                                        "notes_sha256": _json_hash(note_data),
                                        "runtime_sha256": runtime_identity}
        if current != _fingerprint(root, excluded=(Path(temporary),)):
            raise PptRuntimeError("project changed during export")
        if token_data != _read_tokens(tokens) or note_data != _notes(root, notes):
            raise PptRuntimeError("tokens or notes changed during export")
        if runtime_identity != _runtime_fingerprint():
            raise PptRuntimeError("PPT runtime changed during export")
        _publish_candidate(candidate, output)
        published_stat = output.stat()
        try:
            _write_json(root / "validation" / "ppt-export.json", inspection)
        except BaseException:
            # Roll back only the artifact published by this call.
            if output.exists() and os.path.samestat(published_stat, output.stat()):
                output.unlink()
            raise
    return inspection


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for command in ("check", "export", "inspect"):
        child = commands.add_parser(command)
        child.add_argument("target", type=Path)
        child.add_argument("--tokens", type=Path, required=command == "export")
        if command == "export":
            child.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "check":
            result = check_project(args.target, args.tokens)
        elif args.command == "export":
            result = export_project(args.target, args.output, args.tokens)
        else:
            result = inspect_pptx(args.target, args.tokens)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result["status"] == "pass" else 1
    except (OSError, ValueError, RuntimeError, ImportError, BadZipFile, ET.ParseError) as exc:
        print(json.dumps({"status": "fail", "error": str(exc)}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
