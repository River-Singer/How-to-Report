"""Portable native OOXML configuration import and source-anchor reconstruction.

XML is an editable JSON node tree, never an opaque XML string. Shape transforms
and text are additionally exposed in slide configuration with checked bindings.
Unknown Office extensions remain trees; preserving them is not semantic support.
No Office process, model, network access, rasterization or source PPTX is used
when rebuilding a project. This is source reconstruction, not automatic reflow.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path, PurePosixPath
import posixpath
import re
import sys
import tempfile
from urllib.parse import unquote, urlsplit
from xml.dom import Node, minidom
from zipfile import BadZipFile, ZIP_DEFLATED, ZipFile
import zlib

from report_ppt import external_target

SCHEMA = "how-to-report.native-project.v1"
XML_SCHEMA = "how-to-report.native-xml.v1"
SLIDE_SCHEMA = "how-to-report.native-slide.v1"
P = "http://schemas.openxmlformats.org/presentationml/2006/main"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
REL = "http://schemas.openxmlformats.org/package/2006/relationships"
CT = "http://schemas.openxmlformats.org/package/2006/content-types"
MC = "http://schemas.openxmlformats.org/markup-compatibility/2006"
DGM = "http://schemas.openxmlformats.org/drawingml/2006/diagram"
SHAPES = {"sp", "grpSp", "pic", "cxnSp", "graphicFrame", "contentPart"}
MAX_PART_BYTES = 128 * 1024 * 1024
MAX_PACKAGE_BYTES = 1024 * 1024 * 1024
MAX_PARTS = 20000
MAX_TREE_DEPTH = 180
_HASH = re.compile(r"[0-9a-f]{64}\Z")


class NativeRoundtripError(ValueError):
    """Invalid input, unsafe destination or unsupported reconstruction scope."""


def _hash(data):
    return hashlib.sha256(data).hexdigest()


def _is_hash(value):
    return isinstance(value, str) and _HASH.fullmatch(value) is not None


def _tree_hash(tree):
    return _hash(json.dumps(tree, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8"))


def _json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode("utf-8")


def _finite(value, location="config", depth=0):
    if depth > MAX_TREE_DEPTH * 4:
        raise NativeRoundtripError(f"{location}: configuration nesting limit exceeded")
    if isinstance(value, float) and not math.isfinite(value):
        raise NativeRoundtripError(f"{location}: nonfinite number")
    if isinstance(value, dict):
        for key, child in value.items():
            _finite(child, f"{location}.{key}", depth + 1)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _finite(child, f"{location}[{index}]", depth + 1)


def _unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise NativeRoundtripError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _json_load(payload, label):
    try:
        data = json.loads(payload.decode("utf-8"), object_pairs_hook=_unique_pairs)
        _finite(data)
        return data
    except (UnicodeError, json.JSONDecodeError, RecursionError) as exc:
        raise NativeRoundtripError(f"cannot read configuration {label}: {exc}") from exc


def _read_json(path):
    try:
        return _json_load(path.read_bytes(), path)
    except OSError as exc:
        raise NativeRoundtripError(f"cannot read configuration {path}: {exc}") from exc


def _part_path(value):
    if (not isinstance(value, str) or not value or "\\" in value or "\x00" in value
            or value.startswith("/") or any(c in value for c in (":", "?", "#"))):
        raise NativeRoundtripError(f"unsafe package/local path: {value!r}")
    parts = value.split("/")
    if any(p in {"", ".", ".."} or p.endswith((" ", ".")) for p in parts):
        raise NativeRoundtripError(f"unsafe package/local path: {value!r}")
    if any(re.fullmatch(r"(?i)(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\..*)?", p) for p in parts):
        raise NativeRoundtripError(f"device package/local path: {value!r}")
    return value


def _local_file(root, relative):
    relative = _part_path(relative)
    path = root.joinpath(*PurePosixPath(relative).parts)
    for parent in (path, *path.parents):
        if os.path.lexists(parent):
            info = parent.lstat()
            if parent.is_symlink() or getattr(info, "st_file_attributes", 0) & 0x400:
                raise NativeRoundtripError(f"linked configuration input: {relative}")
    if not path.resolve().is_relative_to(root.resolve()):
        raise NativeRoundtripError(f"configuration path escapes project: {relative}")
    return path


def _new_output(path):
    try:
        output = external_target(path)
    except ValueError as exc:
        raise NativeRoundtripError(str(exc)) from exc
    if os.path.lexists(output):
        raise NativeRoundtripError(f"output already exists: {output}")
    return output


def _parse_xml(data, name):
    # OOXML has no DTD. Reject entities before minidom/Expat can expand any.
    probe = data.replace(b"\x00", b"").upper()
    if b"<!DOCTYPE" in probe or b"<!ENTITY" in probe:
        raise NativeRoundtripError(f"{name}: DTD/entity declarations are unsupported")
    try:
        return minidom.parseString(data)
    except Exception as exc:
        raise NativeRoundtripError(f"{name}: invalid XML: {exc}") from exc


def _to_tree(node, depth=0):
    if depth > MAX_TREE_DEPTH:
        raise NativeRoundtripError("XML nesting limit exceeded")
    if node.nodeType == Node.ELEMENT_NODE:
        # Expat/minidom reports xmlns="" as None on some Python versions.
        attrs = {attr.name: attr.value if attr.value is not None else "" for attr in node.attributes.values()}
        namespaces = {attr.name: attr.namespaceURI for attr in node.attributes.values() if attr.namespaceURI}
        return {"kind": "element", "tag": node.tagName, "ns": node.namespaceURI,
                "attrs": attrs, "attr_ns": namespaces,
                "children": [_to_tree(child, depth + 1) for child in node.childNodes]}
    if node.nodeType in (Node.TEXT_NODE, Node.CDATA_SECTION_NODE, Node.COMMENT_NODE):
        kind = {Node.TEXT_NODE: "text", Node.CDATA_SECTION_NODE: "cdata", Node.COMMENT_NODE: "comment"}[node.nodeType]
        return {"kind": kind, "value": node.data}
    if node.nodeType == Node.PROCESSING_INSTRUCTION_NODE:
        return {"kind": "pi", "target": node.target, "value": node.data}
    raise NativeRoundtripError(f"unsupported XML node type: {node.nodeType}")


def _xml_config(data, name):
    document = _parse_xml(data, name)
    try:
        return {"schema": XML_SCHEMA, "part": name, "version": document.version or "1.0",
                "standalone": document.standalone,
                "nodes": [_to_tree(node) for node in document.childNodes]}
    finally:
        document.unlink()


def _from_tree(document, tree, depth=0):
    if depth > MAX_TREE_DEPTH or not isinstance(tree, dict):
        raise NativeRoundtripError("invalid or excessively nested XML tree")
    kind = tree.get("kind")
    value = tree.get("value")
    if kind == "element":
        if not isinstance(tree.get("tag"), str) or not isinstance(tree.get("attrs"), dict):
            raise NativeRoundtripError("XML element needs a tag and attributes")
        element = document.createElementNS(tree.get("ns"), tree["tag"])
        namespaces = tree.get("attr_ns", {})
        if not isinstance(namespaces, dict) or set(namespaces) - set(tree["attrs"]):
            raise NativeRoundtripError("XML attribute namespace map does not match attributes")
        for name, attr in tree["attrs"].items():
            if not isinstance(attr, str):
                raise NativeRoundtripError(f"XML attribute {name} must be a string")
            element.setAttributeNS(namespaces.get(name), name, attr)
        if not isinstance(tree.get("children"), list):
            raise NativeRoundtripError("XML children must be an array")
        for child in tree["children"]:
            element.appendChild(_from_tree(document, child, depth + 1))
        return element
    if not isinstance(value, str):
        raise NativeRoundtripError("XML text/CDATA/comment/PI values must be strings")
    if kind == "text":
        return document.createTextNode(value)
    if kind == "cdata":
        return document.createCDATASection(value)
    if kind == "comment":
        return document.createComment(value)
    if kind == "pi" and isinstance(tree.get("target"), str):
        return document.createProcessingInstruction(tree["target"], value)
    raise NativeRoundtripError(f"unknown XML node kind: {kind}")


def _xml_bytes(config):
    if not isinstance(config, dict) or config.get("schema") != XML_SCHEMA or config.get("version") != "1.0":
        raise NativeRoundtripError("unsupported native XML configuration")
    standalone = config.get("standalone")
    if standalone is not None and not isinstance(standalone, bool):
        raise NativeRoundtripError("XML standalone must be boolean or null")
    document = minidom.Document()
    try:
        for node in config["nodes"]:
            document.appendChild(_from_tree(document, node))
        result = document.toxml(encoding="utf-8", standalone=standalone)
    except Exception as exc:
        if isinstance(exc, NativeRoundtripError):
            raise
        raise NativeRoundtripError(f"cannot serialize XML configuration: {exc}") from exc
    finally:
        document.unlink()
    # Prefix bindings, attribute syntax and XML characters are checked by a real parser.
    parsed = _parse_xml(result, config.get("part", "config"))
    canonical = [_to_tree(node) for node in parsed.childNodes]
    parsed.unlink()
    if canonical != config["nodes"]:
        raise NativeRoundtripError("XML tree namespace or text representation is inconsistent")
    return result


def _walk(config):
    def visit(node, path):
        yield path, node
        for index, child in enumerate(node.get("children", [])):
            yield from visit(child, path + [index])
    for index, node in enumerate(config["nodes"]):
        yield from visit(node, [index])


def _node(config, path):
    if not isinstance(path, list) or not path or len(path) > MAX_TREE_DEPTH + 1:
        raise NativeRoundtripError("invalid XML binding")
    children = config["nodes"]
    result = None
    for index in path:
        if type(index) is not int or not 0 <= index < len(children):
            raise NativeRoundtripError("XML binding is outside its node tree")
        result = children[index]
        children = result.get("children", [])
    return result


def _is(node, namespace, local):
    return node.get("kind") == "element" and node.get("ns") == namespace and node["tag"].split(":")[-1] == local


def _local(node):
    return node.get("tag", "").split(":")[-1]


def _owned(node, path):
    """Walk one shape, omitting the nested shapes owned by a child group."""
    for index, child in enumerate(node.get("children", [])):
        child_path = path + [index]
        if child.get("ns") == P and _local(child) in SHAPES:
            continue
        yield child_path, child
        yield from _owned(child, child_path)


def _branches(config, path):
    result = []
    for length in range(1, len(path)):
        container = _node(config, path[:length])
        if _is(container, MC, "AlternateContent"):
            branch = _node(config, path[:length + 1])
            if branch.get("ns") == MC and _local(branch) in {"Choice", "Fallback"}:
                result.append({"container_binding": path[:length], "branch_binding": path[:length + 1],
                               "kind": _local(branch), "requires": branch["attrs"].get("Requires")})
    return result


def _exclusive(config, left, right):
    """Repeated IDs in mutually exclusive mc branches are one native identity."""
    a = {tuple(b["container_binding"]): b["branch_binding"] for b in _branches(config, left)}
    b = {tuple(b["container_binding"]): b["branch_binding"] for b in _branches(config, right)}
    return any(a[key] != b[key] for key in a.keys() & b.keys())


def _primary_shape(config, path):
    # An OLE graphicFrame may contain a fallback p:pic with the *same* cNvPr ID.
    # It is a representation of that object, not another slide-tree object.
    for length in range(1, len(path)):
        ancestor = _node(config, path[:length])
        if ancestor.get("ns") == P and _local(ancestor) in SHAPES - {"grpSp"}:
            return False
    return True


def _primary_identity(config, path):
    ancestors = []
    for length in range(1, len(path)):
        ancestor = _node(config, path[:length])
        if ancestor.get("ns") == P and _local(ancestor) in SHAPES - {"grpSp"}:
            ancestors.append(path[:length])
    return len(ancestors) <= 1


def _int(value, label, minimum=-(2 ** 63), maximum=2 ** 63 - 1):
    if type(value) is not int or not minimum <= value <= maximum:
        raise NativeRoundtripError(f"{label}: integer outside supported domain")
    return value


def _transform(node, path):
    result = {"binding": path, "attributes": dict(node["attrs"]), "coordinates": {}}
    for child in node["children"]:
        local = _local(child)
        if child.get("ns") == A and local in {"off", "ext", "chOff", "chExt"}:
            keys = {"x", "y"} if local.endswith("Off") or local == "off" else {"cx", "cy"}
            if set(child["attrs"]) != keys or local in result["coordinates"]:
                raise NativeRoundtripError(f"invalid/duplicate transform coordinates {local}")
            try:
                result["coordinates"][local] = {k: int(v) for k, v in child["attrs"].items()}
            except ValueError as exc:
                raise NativeRoundtripError(f"invalid integer transform {local}") from exc
    return result


def _slide_objects(config):
    objects = []
    ancestor_by_path = {}
    ids = {}
    for path, node in _walk(config):
        if node.get("ns") != P or _local(node) not in SHAPES:
            continue
        if not _primary_shape(config, path):
            continue
        owned = list(_owned(node, path))
        identities = [(p, n) for p, n in owned if _is(n, P, "cNvPr")]
        if len(identities) != 1:
            raise NativeRoundtripError(f"shape at {path} must have exactly one identity")
        identity_path, identity = identities[0]
        object_id = identity["attrs"].get("id")
        if (not object_id or not object_id.isdecimal() or int(object_id) <= 0
                or any(not _exclusive(config, path, other) for other in ids.get(object_id, []))):
            raise NativeRoundtripError(f"duplicate or invalid shape ID: {object_id}")
        ids.setdefault(object_id, []).append(path)
        parent = next((ancestor_by_path[tuple(path[:i])] for i in range(len(path) - 1, 0, -1)
                       if tuple(path[:i]) in ancestor_by_path), None)
        ancestor_by_path[tuple(path)] = object_id
        hidden = identity["attrs"].get("hidden")
        if hidden is not None and hidden not in {"1", "0", "true", "false"}:
            raise NativeRoundtripError(f"invalid shape hidden flag: {hidden}")
        record = {"id": object_id, "name": identity["attrs"].get("name", ""), "type": _local(node),
                  "binding": path, "parent_id": parent, "z_order": len(objects),
                  "instance_id": "/".join(map(str, path)), "conditional_branches": _branches(config, path),
                  "hidden": hidden in {"1", "true"}, "hidden_attribute": hidden,
                  "identity_binding": identity_path, "transform": None, "text_runs": [],
                  "properties": {}, "connections": []}
        for child_path, child in owned:
            local = _local(child)
            if child.get("ns") in {A, P} and local == "xfrm":
                if record["transform"] is not None:
                    raise NativeRoundtripError(f"multiple transforms in object {object_id}")
                record["transform"] = _transform(child, child_path)
            if _is(child, A, "t"):
                value = "".join(n.get("value", "") for n in child["children"]
                                if n.get("kind") in {"text", "cdata"})
                record["text_runs"].append({"binding": child_path, "text": value})
            if child.get("ns") in {A, P} and local in {
                "custGeom", "prstGeom", "solidFill", "gradFill", "pattFill", "blipFill", "noFill", "grpFill",
                "ln", "effectLst", "effectDag", "style", "bodyPr", "lstStyle", "p", "pPr", "rPr",
                "endParaRPr", "ph", "spPr", "grpSpPr", "txBody", "srcRect", "extLst",
            }:
                record["properties"].setdefault(local, []).append(child_path)
            if _is(child, A, "stCxn") or _is(child, A, "endCxn"):
                record["connections"].append({"kind": local, "binding": child_path, **child["attrs"]})
        objects.append(record)
    for record in objects:
        for endpoint in record["connections"]:
            if endpoint.get("id") not in ids:
                raise NativeRoundtripError(f"connector {record['id']} has missing endpoint {endpoint.get('id')}")
    return objects


def _relationships(trees, names):
    result = {}
    for name, config in trees.items():
        if not name.endswith(".rels"):
            continue
        if name == "_rels/.rels":
            owner = ""
        elif "/_rels/" in name:
            prefix, leaf = name.rsplit("/_rels/", 1)
            owner = prefix + "/" + leaf[:-5]
        else:
            raise NativeRoundtripError(f"invalid relationship part location: {name}")
        if owner and owner not in names:
            raise NativeRoundtripError(f"relationship owner missing: {owner}")
        rels = {}
        for _, node in _walk(config):
            if not _is(node, REL, "Relationship"):
                continue
            attrs = node["attrs"]
            rid, target, relation_type = attrs.get("Id"), attrs.get("Target"), attrs.get("Type")
            if not rid or rid in rels or not target or not relation_type:
                raise NativeRoundtripError(f"invalid/duplicate relationship in {name}: {rid}")
            mode = attrs.get("TargetMode", "Internal")
            if mode not in {"Internal", "External"}:
                raise NativeRoundtripError(f"invalid relationship TargetMode in {name}")
            if mode == "External":
                # Preserve valid explicit external references, never fetch or execute them.
                if any(ord(c) < 32 for c in target):
                    raise NativeRoundtripError(f"invalid external relationship in {name}")
                rels[rid] = {"type": relation_type, "target": target, "external": True}
                continue
            parsed = urlsplit(target)
            if parsed.scheme or parsed.netloc or parsed.query or "\\" in target:
                raise NativeRoundtripError(f"illegal internal relationship in {name}: {target}")
            raw = unquote(parsed.path)
            resolved = posixpath.normpath(raw.lstrip("/") if raw.startswith("/")
                                         else posixpath.join(posixpath.dirname(owner), raw))
            resolved = _part_path(resolved)
            if resolved not in names:
                raise NativeRoundtripError(f"missing relationship target in {name}: {resolved}")
            rels[rid] = {"type": relation_type, "target": resolved, "external": False}
        result[owner] = rels
    return result


def _ordered_slides(trees, relationships):
    roots = [r["target"] for r in relationships.get("", {}).values()
             if r["type"] == R + "/officeDocument" and not r["external"]]
    if len(roots) != 1 or roots[0] not in trees:
        raise NativeRoundtripError("package needs exactly one internal presentation root")
    presentation = roots[0]
    result, seen = [], set()
    for _, node in _walk(trees[presentation]):
        if not _is(node, P, "sldId"):
            continue
        rid = next((v for k, v in node["attrs"].items()
                    if node.get("attr_ns", {}).get(k) == R and k.split(":")[-1] == "id"), None)
        rel = relationships.get(presentation, {}).get(rid)
        slide_id = node["attrs"].get("id")
        if (not rel or rel["external"] or rel["type"] != R + "/slide" or slide_id in seen
                or not slide_id or not slide_id.isdecimal()):
            raise NativeRoundtripError("invalid/duplicate presentation slide reference")
        seen.add(slide_id)
        if rel["target"] in result:
            raise NativeRoundtripError("duplicate presentation slide part")
        result.append(rel["target"])
    if not result:
        raise NativeRoundtripError("native project needs at least one slide")
    return presentation, result


def _inheritance(part, relationships):
    chain = []
    current = part
    for relation in ("slideLayout", "slideMaster", "theme"):
        matches = [r["target"] for r in relationships.get(current, {}).values()
                   if r["type"] == R + "/" + relation and not r["external"]]
        if not matches:
            break
        if len(matches) != 1:
            raise NativeRoundtripError(f"ambiguous {relation} inheritance for {current}")
        chain.append({"kind": relation, "part": matches[0]})
        current = matches[0]
    return {"chain": chain, "mode": "native-reference-preserved",
            "resolved_style_values": False,
            "note": "Layout/master/theme, placeholders, color maps and background remain native; no style flattening."}


def _content_types(trees, names):
    if "[Content_Types].xml" not in trees:
        raise NativeRoundtripError("missing content types configuration")
    defaults, overrides = {}, {}
    for _, node in _walk(trees["[Content_Types].xml"]):
        if _is(node, CT, "Default"):
            key = node["attrs"].get("Extension", "").lower()
            if not key or key in defaults:
                raise NativeRoundtripError("invalid/duplicate default content type")
            defaults[key] = node["attrs"].get("ContentType")
        if _is(node, CT, "Override"):
            key = unquote(node["attrs"].get("PartName", "").lstrip("/"))
            if not key or key in overrides or key not in names:
                raise NativeRoundtripError("invalid/duplicate/missing content type override")
            overrides[key] = node["attrs"].get("ContentType")
    result = {"[Content_Types].xml": "application/xml"}
    for name in names - {"[Content_Types].xml"}:
        result[name] = overrides.get(name, defaults.get(name.rsplit(".", 1)[-1].lower()))
        if not result[name]:
            raise NativeRoundtripError(f"missing content type for {name}")
    return result


def _xml_content_type(mime):
    return isinstance(mime, str) and (mime.endswith(("+xml", "/xml")) or "vmlDrawing" in mime)


def _validate_trees(trees, names):
    content_types = _content_types(trees, names)
    for name, mime in content_types.items():
        if (_xml_content_type(mime) or name.lower().endswith((".xml", ".rels", ".svg", ".vml"))) and name not in trees:
            raise NativeRoundtripError(f"XML part must be a configuration tree, not a binary asset: {name}")
    relationships = _relationships(trees, names)
    presentation, slides = _ordered_slides(trees, relationships)
    for name, tree in trees.items():
        ids = {}
        for path, node in _walk(tree):
            if _is(node, P, "cNvPr") and _primary_identity(tree, path):
                identity = node["attrs"].get("id")
                if (not identity or not identity.isdecimal()
                        or any(not _exclusive(tree, path, other) for other in ids.get(identity, []))):
                    raise NativeRoundtripError(f"duplicate/invalid object ID {identity} in {name}")
                ids.setdefault(identity, []).append(path)
            for attr, ns in node.get("attr_ns", {}).items():
                if ns == R and node["attrs"][attr] not in relationships.get(name, {}):
                    # SmartArt layout shapes can leave their optional image unset.
                    # The ISO example in Microsoft's LayoutNode docs uses r:blip="".
                    if (_is(node, DGM, "shape") and attr.split(":")[-1] == "blip"
                            and node["attrs"][attr] == ""):
                        continue
                    raise NativeRoundtripError(f"unresolved relationship {node['attrs'][attr]} in {name}")
    for part in slides:
        if part not in trees:
            raise NativeRoundtripError(f"slide has no XML tree: {part}")
        _slide_objects(trees[part])
    return presentation, slides, relationships


def _coverage(trees, slides, assets):
    counts = {}
    representation_counts = {}
    extensions = {}
    for part in slides:
        for path, node in _walk(trees[part]):
            if node.get("kind") != "element":
                continue
            if node.get("ns") == P and _local(node) in SHAPES:
                tally = counts if _primary_shape(trees[part], path) else representation_counts
                tally[_local(node)] = tally.get(_local(node), 0) + 1
            if node.get("ns") not in {P, A, R}:
                key = "{" + str(node.get("ns")) + "}" + _local(node)
                extensions[key] = extensions.get(key, 0) + 1
    return {"xml_part_count": len(trees), "binary_asset_count": len(assets), "slide_count": len(slides),
            "native_objects": counts, "nested_representation_objects": representation_counts,
            "extension_elements": extensions,
            "structured_editing": ["shape/group transform EMU", "text runs"],
            "tree_preserved": ["custom geometry paths/guides/holes", "fill/gradient/line/effects",
                               "paragraph and run properties", "connector identities/endpoints",
                               "layout/master/theme inheritance", "embedded fonts", "unknown XML extensions"],
            "not_claimed": ["semantic layout inference", "content reflow", "resolved inherited styles",
                            "unknown extension interpretation", "independent rendering", "visual equivalence"],
            "geometry_method": "source-anchor-replay-exact-EMU",
            "render_verification": "not_run"}


def _runtime_package_class():
    # Reuse the runtime's public package reader; DOM is separately needed to keep
    # namespace declarations used only in QName-valued extension attributes.
    runtime = Path(__file__).resolve().parents[1] / "runtime" / "ppt-engine" / "scripts"
    if str(runtime) not in sys.path:
        sys.path.insert(0, str(runtime))
    from pptx_to_svg.ooxml_loader import OoxmlPackage
    loaded = sys.modules["pptx_to_svg.ooxml_loader"]
    if Path(loaded.__file__).resolve() != (runtime / "pptx_to_svg/ooxml_loader.py").resolve():
        raise NativeRoundtripError("conflicting runtime package loaded; use the package CLI in a fresh process")
    return OoxmlPackage


def _zip_inventory(source):
    try:
        with ZipFile(source) as archive:
            infos = [i for i in archive.infolist() if not i.is_dir()]
            if len(infos) > MAX_PARTS or sum(i.file_size for i in infos) > MAX_PACKAGE_BYTES:
                raise NativeRoundtripError("PPTX exceeds configured package limits")
            names, folded = [], set()
            for info in infos:
                name = _part_path(info.filename)
                if name.casefold() in folded or info.file_size > MAX_PART_BYTES or info.flag_bits & 1:
                    raise NativeRoundtripError(f"duplicate, encrypted or oversized package part: {name}")
                if (info.external_attr >> 16) & 0o170000 == 0o120000:
                    raise NativeRoundtripError(f"linked ZIP member: {name}")
                folded.add(name.casefold())
                names.append(name)
            return names
    except (BadZipFile, OSError) as exc:
        raise NativeRoundtripError(f"cannot read source PPTX: {exc}") from exc


def extract_native_project(source, output, slides=None):
    """Import every native part; 1-based slides selects audit focus, never pruning."""
    output = _new_output(output)
    source = Path(source)
    if not source.is_file():
        raise NativeRoundtripError(f"source PPTX does not exist: {source}")
    source_hash = _hash(source.read_bytes())
    names = _zip_inventory(source)
    trees, assets, parts, payloads = {}, {}, [], {}
    # Parse XML securely before the runtime reader touches the file.
    try:
        with ZipFile(source) as archive:
            raw = {name: archive.read(name) for name in names}
    except (BadZipFile, OSError, RuntimeError, NotImplementedError, zlib.error) as exc:
        raise NativeRoundtripError(f"cannot read source package parts: {exc}") from exc
    if "[Content_Types].xml" not in raw:
        raise NativeRoundtripError("missing source content types")
    content_types = _content_types({"[Content_Types].xml": _xml_config(raw["[Content_Types].xml"], "[Content_Types].xml")}, set(names))
    for name, data in raw.items():
        is_xml = (_xml_content_type(content_types[name]) or name.lower().endswith((".xml", ".rels", ".vml", ".svg"))
                  or data.lstrip().startswith(b"<?xml"))
        if is_xml:
            config = _xml_config(data, name)
            trees[name] = config
            relative = "xml/" + name + ".json"
            payloads[relative] = _json_bytes(config)
            parts.append({"name": name, "kind": "xml", "config": relative, "source_sha256": _hash(data),
                          "source_tree_sha256": _tree_hash(config)})
        else:
            digest = _hash(data)
            relative = "assets/" + digest + ".bin"
            payloads[relative] = data
            assets[name] = data
            parts.append({"name": name, "kind": "asset", "asset": relative,
                          "sha256": digest, "source_sha256": digest})
    presentation, ordered, relationships = _validate_trees(trees, set(names))
    try:
        with _runtime_package_class()(source) as runtime:
            runtime_parts = [s.part.path for s in runtime.iter_slides()]
            if runtime_parts != ordered:
                raise NativeRoundtripError("runtime and configuration slide orders disagree")
            for name in names:
                if runtime.read_part_bytes(name) != raw[name]:
                    raise NativeRoundtripError("source changed during runtime import")
    except (RuntimeError, KeyError, ValueError, OSError) as exc:
        raise NativeRoundtripError(f"runtime source import failed: {exc}") from exc
    focus = list(range(1, len(ordered) + 1)) if slides is None else slides
    if (not isinstance(focus, list) or not focus or any(type(n) is not int or not 1 <= n <= len(ordered) for n in focus)
            or len(set(focus)) != len(focus)):
        raise NativeRoundtripError("slides must be unique 1-based indices within the source deck")
    slide_records = []
    for number, part in enumerate(ordered, 1):
        relative = f"slides/slide_{number:04d}.json"
        data = {"schema": SLIDE_SCHEMA, "number": number, "part": part,
                "geometry_method": "source-anchor-replay-exact-EMU",
                "objects": _slide_objects(trees[part]), "inheritance": _inheritance(part, relationships)}
        payloads[relative] = _json_bytes(data)
        slide_records.append({"number": number, "part": part, "config": relative, "focus": number in focus})
    manifest = {"schema": SCHEMA, "source": {"name": source.name, "sha256": source_hash},
                "presentation_part": presentation, "parts": parts, "slides": slide_records,
                "coverage": _coverage(trees, ordered, assets),
                "authority": {"xml": "all XML is rebuilt from editable JSON nodes",
                              "slide_overrides": "transform coordinates/attributes and text_runs override their bound XML nodes",
                              "assets": "verified binary dependencies; no generated slide image"}}
    payloads["native-project.json"] = _json_bytes(manifest)
    payloads["README.md"] = (
        "# Native PPTX configuration\n\n"
        "This directory is self-contained. The original PPTX path is neither stored nor needed.\n\n"
        "`native-project.json` maps OPC parts to XML JSON trees and SHA-256 binary assets. "
        "Every XML part is serialized from its tree on rebuild. No raw XML replay is used.\n\n"
        "`slides/slide_NNNN.json` exposes native object IDs, hierarchy, hidden states, exact "
        "local EMU transforms, text runs and bindings into the corresponding XML JSON tree. "
        "Edit `transform.coordinates` / `transform.attributes` or `text_runs[].text`; these "
        "override their bound tree values. Other styling/geometry/paragraph properties are "
        "editable in the XML JSON tree. Bindings and identities must remain stable. "
        "Other object metadata (including name/hidden state) is a checked read-only projection: "
        "editing the underlying XML to change it also requires synchronizing that projection. "
        "Changing the projection alone is rejected, never silently presented as an applied edit.\n\n"
        "Group coordinates remain local: a:off/ext/chOff/chExt are all preserved. "
        "Inherited styles remain references to layout/master/theme rather than flattened styles. "
        "This version does not infer semantic topology or reflow edited text.\n\n"
        "Unknown extensions are preserved structurally, not interpreted. Native render comparison "
        "must be performed in the same PowerPoint environment; successful rebuild alone is not visual acceptance.\n"
    ).encode("utf-8")
    if _hash(source.read_bytes()) != source_hash:
        raise NativeRoundtripError("source changed during extraction")
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".htr-native-import-", dir=output.parent) as temp:
        candidate = Path(temp) / "project"
        candidate.mkdir()
        for relative, data in payloads.items():
            target = candidate.joinpath(*PurePosixPath(relative).parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        summary = inspect_native_project(candidate)
        _new_output(output)
        os.rename(candidate, output)
    summary["project"] = str(output)
    return summary


def _apply_slide(trees, slide, record):
    if (not isinstance(slide, dict) or slide.get("schema") != SLIDE_SCHEMA
            or slide.get("part") != record["part"] or type(slide.get("number")) is not int
            or slide.get("number") != record["number"]):
        raise NativeRoundtripError("slide configuration identity does not match manifest")
    tree = trees[record["part"]]
    expected = _slide_objects(tree)
    objects = slide.get("objects")
    if not isinstance(objects, list) or len(objects) != len(expected):
        raise NativeRoundtripError("slide object inventory differs from its XML configuration")
    edits = []
    for actual, original in zip(objects, expected):
        if not isinstance(actual, dict):
            raise NativeRoundtripError("slide objects must be configuration objects")
        for key in ("id", "type", "binding", "parent_id", "identity_binding", "name", "hidden", "hidden_attribute",
                    "z_order", "instance_id", "conditional_branches"):
            if actual.get(key) != original[key]:
                raise NativeRoundtripError(f"object {original['id']}: changed or duplicate identity/binding")
        transform = actual.get("transform")
        baseline = original["transform"]
        if (transform is None) != (baseline is None):
            raise NativeRoundtripError("cannot create/remove a transform through scalar overrides")
        if transform is not None:
            if (not isinstance(transform, dict) or transform.get("binding") != baseline["binding"]
                    or set(transform.get("coordinates", {})) != set(baseline["coordinates"])):
                raise NativeRoundtripError("transform bindings/coordinate groups do not match")
            attrs = transform.get("attributes")
            if not isinstance(attrs, dict) or set(attrs) - {"rot", "flipH", "flipV"}:
                raise NativeRoundtripError("unsupported transform attributes")
            for attr, value in attrs.items():
                if not isinstance(value, str):
                    raise NativeRoundtripError("transform attributes must retain XML string values")
                if attr == "rot" and not re.fullmatch(r"[+-]?\d+", value):
                    raise NativeRoundtripError("rotation must be integer DrawingML angle units")
                if attr.startswith("flip") and value not in {"true", "false", "0", "1"}:
                    raise NativeRoundtripError("invalid transform flip value")
            target = _node(tree, transform["binding"])
            target["attrs"] = dict(attrs)
            target["attr_ns"] = {}
            for child in target["children"]:
                name = _local(child)
                if name not in baseline["coordinates"]:
                    continue
                coords = transform["coordinates"][name]
                if not isinstance(coords, dict) or set(coords) != set(baseline["coordinates"][name]):
                    raise NativeRoundtripError("transform coordinate keys do not match")
                for key, value in coords.items():
                    _int(value, f"object {actual['id']}.{name}.{key}", 0 if key in {"cx", "cy"} else -(2 ** 63))
                    child["attrs"][key] = str(value)
            if transform != baseline:
                edits.append({"object_id": actual["id"], "kind": "transform", "before": baseline, "after": transform})
        runs = actual.get("text_runs")
        if not isinstance(runs, list) or len(runs) != len(original["text_runs"]):
            raise NativeRoundtripError("text run inventory differs from XML configuration")
        for run, previous in zip(runs, original["text_runs"]):
            if not isinstance(run, dict) or run.get("binding") != previous["binding"] or not isinstance(run.get("text"), str):
                raise NativeRoundtripError("text run must have its original binding and a string value")
            if run["text"] != previous["text"]:
                _node(tree, run["binding"])["children"] = [{"kind": "text", "value": run["text"]}]
                edits.append({"object_id": actual["id"], "kind": "text", "binding": run["binding"],
                              "before": previous["text"], "after": run["text"]})
    return edits


def _load_project(project):
    root = Path(project)
    if root.name == "native-project.json":
        root = root.parent
    if not root.is_dir():
        raise NativeRoundtripError(f"native project directory not found: {root}")
    manifest_file = _local_file(root, "native-project.json")
    manifest_payload = manifest_file.read_bytes()
    manifest = _json_load(manifest_payload, manifest_file)
    if not isinstance(manifest, dict) or manifest.get("schema") != SCHEMA:
        raise NativeRoundtripError("unsupported native project schema")
    source = manifest.get("source")
    if not isinstance(source, dict) or not _is_hash(source.get("sha256")):
        raise NativeRoundtripError("native project requires a source SHA-256 identity")
    parts = manifest.get("parts")
    if not isinstance(parts, list) or not 0 < len(parts) <= MAX_PARTS:
        raise NativeRoundtripError("invalid package part inventory")
    trees, assets, folded, inputs, tree_edits = {}, {}, set(), {}, []
    inputs["native-project.json"] = _hash(manifest_payload)
    for part in parts:
        if not isinstance(part, dict):
            raise NativeRoundtripError("part must be an object")
        name = _part_path(part.get("name"))
        if name.casefold() in folded or not _is_hash(part.get("source_sha256")):
            raise NativeRoundtripError(f"duplicate part or invalid source identity: {name}")
        folded.add(name.casefold())
        key = "config" if part.get("kind") == "xml" else "asset"
        path = _local_file(root, part.get(key))
        try:
            payload = path.read_bytes()
        except OSError as exc:
            raise NativeRoundtripError(f"cannot read part dependency {path}: {exc}") from exc
        if len(payload) > MAX_PART_BYTES * 16:
            raise NativeRoundtripError(f"oversized configuration/asset: {path}")
        inputs[part[key]] = _hash(payload)
        if part.get("kind") == "xml":
            tree = _json_load(payload, path)
            if not isinstance(tree, dict) or tree.get("schema") != XML_SCHEMA or tree.get("part") != name:
                raise NativeRoundtripError(f"XML configuration identity mismatch: {name}")
            original_tree_hash = part.get("source_tree_sha256")
            if original_tree_hash is not None and not _is_hash(original_tree_hash):
                raise NativeRoundtripError(f"invalid XML source tree identity: {name}")
            if original_tree_hash is not None and original_tree_hash != _tree_hash(tree):
                tree_edits.append({"part": name, "source_tree_sha256": original_tree_hash,
                                   "current_tree_sha256": _tree_hash(tree)})
            trees[name] = tree
        elif part.get("kind") == "asset":
            if _hash(payload) != part.get("sha256"):
                raise NativeRoundtripError(f"asset hash mismatch: {name}")
            assets[name] = payload
        else:
            raise NativeRoundtripError(f"unknown package part kind: {part.get('kind')}")
    for tree in trees.values():
        _xml_bytes(tree)
    presentation, ordered, relationships = _validate_trees(trees, set(trees) | set(assets))
    records = manifest.get("slides")
    if (not isinstance(records, list) or any(not isinstance(r, dict) for r in records)
            or [r.get("part") for r in records] != ordered
            or manifest.get("presentation_part") != presentation):
        raise NativeRoundtripError("manifest slide order differs from presentation configuration")
    edits, summaries = [], []
    for index, record in enumerate(records, 1):
        if type(record.get("number")) is not int or record.get("number") != index or type(record.get("focus")) is not bool:
            raise NativeRoundtripError("invalid slide manifest number/focus")
        path = _local_file(root, record.get("config"))
        payload = path.read_bytes()
        slide = _json_load(payload, path)
        inputs[record["config"]] = _hash(payload)
        changes = _apply_slide(trees, slide, record)
        edits.extend({"slide": index, **change} for change in changes)
        objects = _slide_objects(trees[record["part"]])
        summaries.append({"number": index, "part": record["part"], "focus": record["focus"],
                          "object_count": len(objects), "hidden_count": sum(o["hidden"] for o in objects),
                          "text_run_count": sum(len(o["text_runs"]) for o in objects),
                          "inheritance": _inheritance(record["part"], relationships)})
    _validate_trees(trees, set(trees) | set(assets))
    entries = {name: _xml_bytes(tree) for name, tree in trees.items()}
    entries.update(assets)
    if sum(map(len, entries.values())) > MAX_PACKAGE_BYTES:
        raise NativeRoundtripError("rebuilt package exceeds size limit")
    fingerprint = _hash(json.dumps(inputs, sort_keys=True, separators=(",", ":")).encode())
    report = {"schema": "how-to-report.native-inspection.v1", "status": "pass", "project": str(root.resolve()),
              "generator": {"module": "presentation_native.py", "sha256": _hash(Path(__file__).read_bytes()),
                            "algorithm": "native-json-tree-source-anchors-v1"},
              "source": source, "configuration_sha256": fingerprint, "input_sha256": inputs,
              "slides": summaries, "coverage": _coverage(trees, ordered, assets), "edits": edits,
              "xml_tree_edits": tree_edits,
              "part_sha256": {name: _hash(data) for name, data in entries.items()},
              "scope": "configuration/package/identity validation; visual rendering remains not_run"}
    return root, report, entries


def inspect_native_project(project):
    """Read-only validation of configuration, dependencies and reconstruction."""
    return _load_project(project)[1]


def rebuild_native_project(project, output):
    """Build a new PPTX solely from validated configuration and binary assets."""
    output = _new_output(output)
    root, report, entries = _load_project(project)
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".htr-native-build-", dir=output.parent) as temporary:
        candidate = Path(temporary) / "presentation.pptx"
        with ZipFile(candidate, "w", compression=ZIP_DEFLATED) as archive:
            for name, payload in entries.items():
                archive.writestr(name, payload)
        with ZipFile(candidate) as archive:
            if archive.testzip() is not None or set(archive.namelist()) != set(entries):
                raise NativeRoundtripError("rebuilt ZIP verification failed")
        for relative, expected in report["input_sha256"].items():
            if _hash(_local_file(root, relative).read_bytes()) != expected:
                raise NativeRoundtripError("native configuration changed during rebuild")
        _new_output(output)
        # Same-volume no-replace publication. No half-written target is exposed.
        if os.name == "nt":
            os.rename(candidate, output)
        else:
            os.link(candidate, output)
        report.update({"schema": "how-to-report.native-build.v1", "output": str(output),
                       "sha256": _hash(output.read_bytes()), "source_required": False,
                       "xml_serialization": "all XML generated from JSON node trees"})
    return report
