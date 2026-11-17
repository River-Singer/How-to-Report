"""Versioned presentation authoring data, fact evaluation and immutable patches."""
from __future__ import annotations

from copy import deepcopy
from decimal import Decimal, InvalidOperation, localcontext
import hashlib
import json
import math
import re


SCHEMA_VERSION = "0.1"
FORMAT = re.compile(r",?\.([0-6])[f%]\Z")
PROTECTED_FIELDS = {"schema_version", "project_id", "revision", "_patch_history"}


def document_hash(document):
    """Hash the actual JSON state, including its revision and patch receipts."""
    try:
        data = json.dumps(document, ensure_ascii=False, sort_keys=True,
                          separators=(",", ":"), allow_nan=False).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise ValueError(f"document is not finite JSON: {exc}") from exc
    return hashlib.sha256(data).hexdigest()


def _text(value, where):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{where}: expected nonempty text")


def _number(value, where):
    if type(value) not in (int, float, Decimal):
        raise ValueError(f"{where}: expected a finite number")
    try:
        number = Decimal(str(value))
    except InvalidOperation as exc:
        raise ValueError(f"{where}: invalid number") from exc
    if not number.is_finite():
        raise ValueError(f"{where}: expected a finite number")
    return number


def _json_number(value, where):
    if value == value.to_integral_value():
        return int(value)
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{where}: result exceeds finite JSON number range")
    return result


def fact_dependencies(document):
    """Return explicit calculation inputs. These are separate from semantic links."""
    facts = document.get("facts", {})
    if not isinstance(facts, dict):
        raise ValueError("facts: expected an object keyed by stable fact ID")
    dependencies = {}
    for identifier, fact in facts.items():
        _text(identifier, "facts ID")
        if not isinstance(fact, dict) or (("value" in fact) == ("derived" in fact)):
            raise ValueError(f"facts.{identifier}: require exactly one of value or derived")
        derived = fact.get("derived")
        dependencies[identifier] = []
        if "derived" in fact:
            if not isinstance(derived, dict) or set(derived) - {"op", "args", "scale"}:
                raise ValueError(f"facts.{identifier}.derived: unsupported expression shape")
            operator = derived.get("op")
            args = derived.get("args")
            if operator not in ("sum", "difference", "product", "ratio"):
                raise ValueError(f"facts.{identifier}.derived.op: unsupported operator")
            if not isinstance(args, list) or not args or not all(isinstance(x, str) and x for x in args):
                raise ValueError(f"facts.{identifier}.derived.args: expected fact IDs")
            if operator in ("difference", "ratio") and len(args) != 2:
                raise ValueError(f"facts.{identifier}: {operator} requires two inputs")
            if "scale" in derived:
                _number(derived["scale"], f"facts.{identifier}.derived.scale")
            dependencies[identifier] = args
    return dependencies


def evaluate_facts(document):
    """Evaluate the bounded declared arithmetic graph using Decimal internally."""
    dependencies = fact_dependencies(document)
    definitions = document.get("facts", {})
    values = {}
    visiting = []

    def evaluate(identifier):
        if identifier in values:
            return values[identifier]
        if identifier not in definitions:
            raise ValueError(f"facts: unknown reference {identifier!r}")
        if identifier in visiting:
            raise ValueError("facts: cyclic calculation " + " -> ".join(visiting + [identifier]))
        visiting.append(identifier)
        fact = definitions[identifier]
        if "value" in fact:
            value = fact["value"]
            if type(value) in (int, float):
                value = _number(value, f"facts.{identifier}.value")
            elif not isinstance(value, str):
                raise ValueError(f"facts.{identifier}.value: expected number or text")
        else:
            expression = fact["derived"]
            args = [_number(evaluate(arg), f"facts.{identifier} input {arg}")
                    for arg in dependencies[identifier]]
            with localcontext() as context:
                context.prec = 40
                operator = expression["op"]
                if operator == "sum":
                    value = sum(args, Decimal(0))
                elif operator == "difference":
                    value = args[0] - args[1]
                elif operator == "product":
                    value = Decimal(1)
                    for arg in args:
                        value *= arg
                else:
                    if args[1] == 0:
                        raise ValueError(f"facts.{identifier}: division by zero")
                    value = args[0] / args[1]
                value *= _number(expression.get("scale", 1), f"facts.{identifier}.scale")
        visiting.pop()
        values[identifier] = value
        return value

    for identifier in definitions:
        evaluate(identifier)
    return {key: _json_number(value, f"facts.{key}") if isinstance(value, Decimal) else value
            for key, value in values.items()}


def _format(value, specification):
    if specification is None:
        return value
    if specification == "text":
        return str(value)
    number = _number(value, "reference format")
    if specification == "integer":
        return format(number, ",.0f")
    if specification == "number":
        return format(number, ",f").rstrip("0").rstrip(".") if number % 1 else format(number, ",.0f")
    if specification == "percent":
        return format(number, ".1%")
    if not isinstance(specification, str) or not FORMAT.fullmatch(specification):
        raise ValueError(f"unsupported fact format {specification!r}")
    return format(number, specification)


def resolve_value(value, facts):
    """Resolve exact {ref, format?} values while preserving ordinary JSON objects."""
    if isinstance(value, dict):
        if "ref" in value and set(value).issubset({"ref", "format"}):
            identifier = value["ref"]
            if not isinstance(identifier, str) or identifier not in facts:
                raise ValueError(f"unknown fact reference {identifier!r}")
            return _format(facts[identifier], value.get("format"))
        return {key: resolve_value(item, facts) for key, item in value.items()}
    if isinstance(value, list):
        return [resolve_value(item, facts) for item in value]
    return value


def resolve_text(value, facts):
    """Resolve a text scalar, a parts array, or a styled text wrapper."""
    if isinstance(value, list):
        return "".join(resolve_text(part, facts) for part in value)
    if isinstance(value, dict) and "parts" in value:
        return resolve_text(value["parts"], facts)
    if isinstance(value, dict) and "text" in value:
        return resolve_text(value["text"], facts)
    resolved = resolve_value(value, facts)
    if isinstance(resolved, (str, int, float)) and not isinstance(resolved, bool):
        return str(resolved)
    raise ValueError("text: expected text, a fact reference or a parts array")


def _references(value):
    if isinstance(value, dict):
        if "ref" in value and set(value).issubset({"ref", "format"}):
            yield value["ref"]
        else:
            for item in value.values():
                yield from _references(item)
    elif isinstance(value, list):
        for item in value:
            yield from _references(item)


def _pointer(path):
    if not isinstance(path, str) or not path.startswith("/"):
        raise ValueError("patch path must be a nonempty JSON Pointer")
    tokens = path[1:].split("/")
    if any(re.search(r"~(?![01])", token) for token in tokens):
        raise ValueError(f"invalid JSON Pointer escape: {path}")
    return [token.replace("~1", "/").replace("~0", "~") for token in tokens]


def _read_pointer(document, path):
    value = document
    for token in _pointer(path):
        if isinstance(value, list):
            if not token.isdigit() or str(int(token)) != token or int(token) >= len(value):
                raise ValueError(f"missing JSON Pointer {path}")
            value = value[int(token)]
        elif isinstance(value, dict) and token in value:
            value = value[token]
        else:
            raise ValueError(f"missing JSON Pointer {path}")
    return value


def _locks(document):
    locks = document.get("locks", [])
    if isinstance(locks, dict):
        locks = [{"path": path, "value": value} for path, value in locks.items()]
    if not isinstance(locks, list):
        raise ValueError("locks: expected a path/value list or object")
    seen = set()
    for lock in locks:
        if not isinstance(lock, dict) or "value" not in lock:
            raise ValueError("locks: require path and value")
        path = lock.get("path")
        _pointer(path)
        if path in seen:
            raise ValueError(f"duplicate lock path {path}")
        seen.add(path)
        yield path, lock["value"]


def validate_document(document):
    """Validate common authoring invariants. Scene details belong to the compiler."""
    if not isinstance(document, dict) or document.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("unsupported presentation schema_version")
    _text(document.get("project_id"), "project_id")
    if type(document.get("revision")) is not int or document["revision"] < 1:
        raise ValueError("revision must be a positive integer")
    if not isinstance(document.get("brief"), dict):
        raise ValueError("brief must be an object")
    if "palette_id" in document["brief"]:
        from presentation_palette import describe_palette
        describe_palette(document["brief"]["palette_id"])
    if not isinstance(document.get("pages"), list):
        raise ValueError("pages must be an array")
    if not isinstance(document.get("sources", []), list):
        raise ValueError("sources must be an array")
    document_hash(document)
    facts = evaluate_facts(document)
    identifiers = set()

    def register(identifier, where):
        _text(identifier, where)
        if identifier in identifiers:
            raise ValueError(f"duplicate object ID {identifier!r} at {where}")
        identifiers.add(identifier)

    for identifier in facts:
        register(identifier, "facts ID")
    source_ids = set()
    for source in document.get("sources", []):
        if not isinstance(source, dict):
            raise ValueError("sources: expected source objects")
        register(source.get("id"), "source ID")
        source_ids.add(source["id"])
    for identifier, fact in document.get("facts", {}).items():
        reference = fact.get("source_ref")
        if reference is not None:
            source_id = None
            if isinstance(reference, dict):
                source_id = reference.get("id")
            elif isinstance(reference, str):
                source_id = reference.split("#", 1)[0]
            if source_id not in source_ids:
                raise ValueError(f"facts.{identifier}.source_ref: unknown source")

    def objects(items, where):
        if not isinstance(items, list):
            raise ValueError(f"{where}: expected an array")
        for index, item in enumerate(items):
            location = f"{where}[{index}]"
            if not isinstance(item, dict):
                raise ValueError(f"{location}: expected an object")
            object_payload(item, location)

    def object_payload(item, location, *, register_id=True):
        if register_id:
            register(item.get("id"), location + ".id")
        for field in ("elements", "children", "components"):
            if field in item:
                objects(item[field], location + "." + field)
        # A leaf's ID belongs to its layout node; the element payload has no
        # independent identity. Topology interiors use the same layout tree.
        for field in ("layout", "interior"):
            child = item.get(field)
            if isinstance(child, dict):
                object_payload(child, location + "." + field)
        if "element" in item:
            child = item["element"]
            if not isinstance(child, dict):
                raise ValueError(f"{location}.element: expected an object")
            object_payload(child, location + ".element", register_id=False)

    for page in document["pages"]:
        if isinstance(page, dict):
            from presentation_content_diagnostics import validate_page_intent
            validate_page_intent(page)
        if isinstance(page, dict) and page.get("kind") == "layout":
            from presentation_layout import validate_layout_page
            validate_layout_page(page)
    objects(document["pages"], "pages")
    relations = document.get("relations", [])
    if not isinstance(relations, list):
        raise ValueError("relations must be an array")
    for relation in relations:
        if not isinstance(relation, dict):
            raise ValueError("relations: expected relation objects")
        register(relation.get("id"), "relation ID")
        _text(relation.get("type"), "relation.type")
    for relation in relations:
        if ("from" in relation) != ("to" in relation):
            raise ValueError(f"relation {relation['id']}: require both from and to")
        for endpoint in ("from", "to"):
            if endpoint in relation:
                target = relation[endpoint]
                if not isinstance(target, str) or target not in identifiers:
                    raise ValueError(f"relation {relation['id']}.{endpoint}: unknown object ID {target!r}")
    for reference in _references(document["pages"]):
        if not isinstance(reference, str) or reference not in facts:
            raise ValueError(f"pages: unknown fact reference {reference!r}")
    resolve_value(document["pages"], facts)
    for path, expected in _locks(document):
        if document_hash(_read_pointer(document, path)) != document_hash(expected):
            raise ValueError(f"lock does not match current value at {path}")


def _apply_operation(document, operation):
    if not isinstance(operation, dict) or operation.get("op") not in ("add", "replace", "remove", "test"):
        raise ValueError("patch requires add, replace, remove or test operations")
    tokens = _pointer(operation.get("path"))
    if tokens[0] in PROTECTED_FIELDS:
        raise ValueError(f"patch cannot change managed field {tokens[0]}")
    action = operation["op"]
    if action != "remove" and "value" not in operation:
        raise ValueError(f"patch {action} requires value")
    if action == "test":
        if document_hash(_read_pointer(document, operation["path"])) != document_hash(operation["value"]):
            raise ValueError(f"patch test failed at {operation['path']}")
        return
    parent = document
    for token in tokens[:-1]:
        if isinstance(parent, list):
            if not token.isdigit() or str(int(token)) != token or int(token) >= len(parent):
                raise ValueError(f"missing patch parent {operation['path']}")
            parent = parent[int(token)]
        elif isinstance(parent, dict) and token in parent:
            parent = parent[token]
        else:
            raise ValueError(f"missing patch parent {operation['path']}")
    key = tokens[-1]
    if isinstance(parent, list):
        if key == "-" and action == "add":
            parent.append(deepcopy(operation["value"]))
            return
        if not key.isdigit() or str(int(key)) != key:
            raise ValueError(f"invalid array index at {operation['path']}")
        index = int(key)
        if index > len(parent) or (index == len(parent) and action != "add"):
            raise ValueError(f"missing patch index {operation['path']}")
        if action == "add":
            parent.insert(index, deepcopy(operation["value"]))
        elif action == "replace":
            parent[index] = deepcopy(operation["value"])
        else:
            del parent[index]
    elif isinstance(parent, dict):
        if key not in parent and action != "add":
            raise ValueError(f"missing patch path {operation['path']}")
        if action == "remove":
            del parent[key]
        else:
            parent[key] = deepcopy(operation["value"])
    else:
        raise ValueError(f"patch parent is not a container: {operation['path']}")


def _affected_pages(before, after):
    old_facts = evaluate_facts(before)
    new_facts = evaluate_facts(after)
    changed = {key for key in old_facts.keys() | new_facts.keys()
               if old_facts.get(key) != new_facts.get(key)
               or before.get("facts", {}).get(key) != after.get("facts", {}).get(key)}
    dependencies = fact_dependencies(after)
    pending = list(changed)
    while pending:
        dependency = pending.pop()
        for identifier, inputs in dependencies.items():
            if dependency in inputs and identifier not in changed:
                changed.add(identifier)
                pending.append(identifier)
    old_pages = {page["id"]: page for page in before["pages"]}
    global_change = any(before.get(key) != after.get(key)
                        for key in ("brief", "theme", "assets", "sources", "relations", "output_contract"))
    affected = []
    for index, page in enumerate(after["pages"]):
        old = old_pages.get(page["id"])
        position_changed = index >= len(before["pages"]) or before["pages"][index]["id"] != page["id"]
        if global_change or position_changed or old != page or changed.intersection(_references(page)):
            affected.append(page["id"])
    affected.extend(page["id"] for page in before["pages"] if page["id"] not in {p["id"] for p in after["pages"]})
    return affected


def apply_patch_to_document(document, operations, expected_revision, operation_id, *, unlock_paths=()):
    """Apply an optimistic, immutable JSON-Pointer patch and retain replay receipts."""
    validate_document(document)
    if type(expected_revision) is not int or expected_revision < 1:
        raise ValueError("expected_revision must be a positive integer")
    _text(operation_id, "operation_id")
    if not isinstance(operations, list) or not operations:
        raise ValueError("operations must be a nonempty array")
    if not isinstance(unlock_paths, (list, tuple)) or not all(isinstance(x, str) for x in unlock_paths):
        raise ValueError("unlock_paths must contain JSON Pointers")
    request_hash = document_hash({"operations": operations, "expected_revision": expected_revision,
                                  "unlock_paths": list(unlock_paths)})
    history = document.get("_patch_history", [])
    if not isinstance(history, list):
        raise ValueError("invalid patch history")
    for index, entry in enumerate(history):
        if entry.get("operation_id") == operation_id:
            if entry.get("request_hash") != request_hash:
                raise ValueError("operation_id already used for a different patch")
            result = deepcopy(entry["result_snapshot"])
            result["_patch_history"] = deepcopy(history[:index + 1])
            return result
    if document["revision"] != expected_revision:
        raise ValueError(f"revision conflict: expected {expected_revision}, current {document['revision']}")
    result = deepcopy(document)
    for operation in operations:
        _apply_operation(result, operation)
    remaining_locks = dict(_locks(result))
    for path, value in _locks(document):
        if path not in unlock_paths:
            if path not in remaining_locks or document_hash(remaining_locks[path]) != document_hash(value):
                raise ValueError(f"patch violates lock definition at {path}")
            if document_hash(_read_pointer(result, path)) != document_hash(value):
                raise ValueError(f"patch violates lock at {path}")
    result["revision"] += 1
    validate_document(result)
    snapshot = {key: deepcopy(value) for key, value in result.items() if key != "_patch_history"}
    receipt = {"operation_id": operation_id, "request_hash": request_hash,
               "input_revision": expected_revision, "result_revision": result["revision"],
               "affected_pages": _affected_pages(document, result), "result_snapshot": snapshot}
    result["_patch_history"] = deepcopy(history) + [receipt]
    return result
