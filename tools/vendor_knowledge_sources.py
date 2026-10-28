#!/usr/bin/env python3
"""Maintenance-only text acquisition and offline Knowledge integrity checking.

`check` never accesses the network. `fetch` writes a review candidate, not the
canonical archive or its manifest; source/license changes require human review.
Python 3.10+, standard library only. This tool is not shipped inside Skills.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path, PurePosixPath
import re
import sys
from urllib.parse import urlsplit
import urllib.request

DEFAULT_ROOT = Path(__file__).resolve().parents[1] / "skill-src/shared/knowledge"
METHOD_ROOT = DEFAULT_ROOT.parent / "references/method-sources"
STATUSES = {"source_text", "partial_source_text", "original_summary"}
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}
BLOCK = {"article", "blockquote", "br", "div", "h1", "h2", "h3", "h4", "h5", "h6", "hr", "li", "p", "section", "table", "tr", "ul", "ol"}
SKIP = {"script", "style", "noscript", "svg", "nav", "button", "form"}


class SourceError(ValueError):
    pass


def require_https(url: str) -> None:
    parsed = urlsplit(url)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise SourceError("source acquisition requires an HTTPS URL without embedded credentials")


class HttpsOnlyRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, response, code, message, headers, newurl):
        require_https(newurl)
        return super().redirect_request(request, response, code, message, headers, newurl)


class TextParser(HTMLParser):
    """Extract one explicitly selected public body, retaining text order."""

    def __init__(self, selector: dict[str, str]):
        super().__init__(convert_charrefs=True)
        self.selector = selector
        self.stack: list[tuple[str, bool, bool]] = []
        self.parts: list[str] = []
        self.matches = 0

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        match = ((not self.selector.get("tag") or tag == self.selector["tag"])
                 and (not self.selector.get("id") or values.get("id") == self.selector["id"])
                 and (not self.selector.get("class") or self.selector["class"] in (values.get("class") or "").split()))
        parent_active = self.stack[-1][1] if self.stack else False
        parent_skip = self.stack[-1][2] if self.stack else False
        active = parent_active or match
        skip = parent_skip or tag in SKIP
        if match:
            self.matches += 1
        if active and not skip:
            if tag in BLOCK:
                self.parts.append("\n\n")
            elif tag in {"td", "th"}:
                self.parts.append(" | ")
            if tag == "li":
                self.parts.append("- ")
            if tag == "img" and values.get("alt"):
                self.parts.append(" [Image alt text: " + values["alt"] + "] ")
        if tag not in VOID:
            self.stack.append((tag, active, skip))

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index][0] == tag:
                active, skip = self.stack[index][1:]
                del self.stack[index:]
                if active and not skip and tag in BLOCK:
                    self.parts.append("\n\n")
                return

    def handle_data(self, data):
        if self.stack and self.stack[-1][1] and not self.stack[-1][2]:
            self.parts.append(re.sub(r"\s+", " ", data))

    def text(self):
        lines = [re.sub(r"[ \t]+", " ", line).strip() for line in "".join(self.parts).splitlines()]
        return re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip() + "\n"


def extract_html(html: str, selector: dict[str, str]) -> str:
    parser = TextParser(selector)
    parser.feed(html)
    if parser.matches != 1:
        raise SourceError(f"body selector matched {parser.matches} elements; review required")
    result = parser.text()
    if len(result.strip()) < 100:
        raise SourceError("body extraction is unexpectedly short")
    return result


def fetch_candidate(source: dict) -> tuple[str, dict]:
    if source.get("representation") == "original_summary":
        raise SourceError("This source has no approved full-text reuse; maintain its original summary manually")
    if source.get("representation") not in {"source_text", "partial_source_text"}:
        raise SourceError("unsupported source representation")
    if source.get("retrieval", {}).get("method") != "https_html_body":
        raise SourceError("This source uses a reviewed imported extraction; do not replace it silently")
    require_https(source["canonical_url"])
    request = urllib.request.Request(source["canonical_url"], headers={"User-Agent": "Mozilla/5.0", "Accept": "text/html"})
    opener = urllib.request.build_opener(HttpsOnlyRedirectHandler())
    with opener.open(request, timeout=40) as response:
        if "html" not in response.headers.get_content_type():
            raise SourceError("expected public HTML source")
        raw = response.read(4_000_001)
        if len(raw) > 4_000_000:
            raise SourceError("source exceeds bounded acquisition limit")
        encoding = response.headers.get_content_charset() or "utf-8"
        html = raw.decode(encoding)
        resolved_url = response.geturl()
        require_https(resolved_url)
    body = extract_html(html, source["retrieval"]["selector"])
    return body, {"fetched_at_utc": datetime.now(timezone.utc).isoformat(), "resolved_url": resolved_url,
                  "response_sha256": hashlib.sha256(raw).hexdigest(), "response_bytes": len(raw)}


def confined(root: Path, relative: str) -> Path:
    posix = PurePosixPath(relative)
    if not relative or "\\" in relative or posix.is_absolute() or ".." in posix.parts or ":" in relative:
        raise SourceError(f"unsafe source path: {relative}")
    path = root / relative
    if not path.resolve().is_relative_to(root.resolve()):
        raise SourceError(f"source escapes archive: {relative}")
    for part in [path, *path.parents]:
        if part == root.parent:
            break
        if part.is_symlink() or (part.exists() and getattr(part.lstat(), "st_file_attributes", 0) & 0x400):
            raise SourceError(f"linked archive path: {relative}")
    return path


def check(root: Path) -> list[str]:
    errors: list[str] = []
    try:
        manifest = json.loads(confined(root, "sources/manifest.json").read_text(encoding="utf-8"))
        if not isinstance(manifest, dict) or manifest.get("schema_version") != "1" or not isinstance(manifest.get("sources"), list):
            raise SourceError("unsupported source manifest")
        if manifest.get("runtime_network_required") is not False:
            raise SourceError("archive must explicitly declare runtime_network_required=false")
        if not isinstance(manifest.get("card_sources"), dict) or any(
            not isinstance(name, str) or not isinstance(values, list) or not values
            or any(not isinstance(value, str) for value in values)
            for name, values in manifest["card_sources"].items()
        ):
            raise SourceError("invalid card/source mapping")
    except (OSError, ValueError) as exc:
        return [str(exc)]
    ids, urls, paths = set(), set(), set()
    for item in manifest["sources"]:
        try:
            if not isinstance(item, dict):
                raise SourceError("source entry must be an object")
            for key in ("id", "title", "publisher", "canonical_url", "local_path", "fetched_at_utc", "scope", "sha256"):
                if not isinstance(item.get(key), str) or not item[key].strip():
                    raise SourceError(f"missing source metadata {key}")
            sid, url, relative = item["id"], item["canonical_url"], item["local_path"]
            if sid in ids or url in urls or relative.casefold() in paths:
                raise SourceError(f"duplicate source identity/url/path: {sid}")
            ids.add(sid); urls.add(url); paths.add(relative.casefold())
            if item.get("representation") not in STATUSES or not url.startswith("https://"):
                raise SourceError(f"invalid representation/url: {sid}")
            if not datetime.fromisoformat(item["fetched_at_utc"]).tzinfo:
                raise SourceError(f"unqualified retrieval time: {sid}")
            license_info = item.get("reuse", {})
            if not isinstance(license_info, dict) or not all(license_info.get(k) for k in ("license", "evidence_url", "attribution", "limitations")):
                raise SourceError(f"missing reuse record: {sid}")
            if not isinstance(item.get("retrieval"), dict) or not item["retrieval"].get("method") or not item.get("card_ids"):
                raise SourceError(f"missing retrieval/card scope: {sid}")
            path = confined(root, relative)
            raw = path.read_bytes()
            text = raw.decode("utf-8")
            if not text.strip() or "\ufffd" in text or "\x00" in text:
                raise SourceError(f"invalid source text: {sid}")
            if hashlib.sha256(raw).hexdigest() != item["sha256"]:
                raise SourceError(f"source hash mismatch: {sid}")
        except (OSError, ValueError, TypeError) as exc:
            errors.append(str(exc))
    actual = {f.relative_to(root).as_posix().casefold() for f in (root / "sources").rglob("*.txt")}
    if actual != paths:
        errors.append(f"source inventory mismatch: unregistered={sorted(actual-paths)}, missing={sorted(paths-actual)}")
    referenced = set()
    by_id = {s.get("id"): s.get("local_path", "").casefold() for s in manifest["sources"]
             if isinstance(s, dict) and isinstance(s.get("id"), str) and isinstance(s.get("local_path"), str)}
    for card in root.glob("*.md"):
        try:
            body = confined(root, card.name).read_text(encoding="utf-8")
        except (OSError, ValueError) as exc:
            errors.append(f"cannot read card {card.name}: {exc}")
            continue
        targets = re.findall(r"\]\((sources/[^)]+\.txt)\)", body)
        if re.search(r"\]\(https?://", body):
            errors.append(f"external body link in {card.name}; use a local source and manifest provenance")
        for target in targets:
            referenced.add(target.casefold())
            if target.casefold() not in paths:
                errors.append(f"unregistered local source in {card.name}: {target}")
        expected = manifest.get("card_sources", {}).get(card.name)
        if expected is not None:
            if any(sid not in by_id for sid in expected) or {by_id.get(sid) for sid in expected} != {t.casefold() for t in targets}:
                errors.append(f"card/source mapping mismatch: {card.name}")
        elif card.name != "index.md":
            errors.append(f"card missing source mapping: {card.name}")
    for name in manifest.get("card_sources", {}):
        try:
            if not confined(root, name).is_file():
                errors.append(f"missing registered card: {name}")
        except SourceError as exc:
            errors.append(str(exc))
    if paths - referenced:
        errors.append(f"unreferenced source texts: {sorted(paths-referenced)}")
    return errors


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("check", "fetch"))
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--source-id")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    if args.command == "check":
        errors = check(args.root)
        if args.root.resolve() == DEFAULT_ROOT.resolve():
            errors.extend("core methods: " + error for error in check(METHOD_ROOT))
        print(json.dumps({"valid": not errors, "errors": errors, "network_used": False}, ensure_ascii=False))
        return int(bool(errors))
    if not args.source_id or not args.output:
        parser.error("fetch requires --source-id and --output (new review candidate)")
    try:
        if args.output.resolve().is_relative_to(args.root.resolve()):
            raise SourceError("review candidate must be outside the canonical Knowledge archive")
        if args.output.exists() or args.output.is_symlink():
            raise SourceError("review candidate already exists; choose a new output file")
        if not args.output.parent.is_dir():
            raise SourceError("review candidate parent directory does not exist")
        manifest = json.loads(confined(args.root, "sources/manifest.json").read_text(encoding="utf-8"))
        source = next((s for s in manifest["sources"] if s["id"] == args.source_id), None)
        if source is None:
            raise SourceError("unknown source ID")
        body, receipt = fetch_candidate(source)
        with args.output.open("x", encoding="utf-8", newline="\n") as output:
            output.write(json.dumps(receipt, ensure_ascii=False) + "\n\n" + body)
        print(f"Wrote review candidate: {args.output}; canonical archive/manifest unchanged")
        return 0
    except (OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
