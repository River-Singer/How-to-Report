#!/usr/bin/env python3
"""Build/check two self-contained Skills using Python 3.10+ standard library.

Static dependency checks cover Markdown inline/reference-definition links outside
fenced code blocks. They do not prove arbitrary Python or host runtime behavior.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import posixpath
import re
import shutil
import stat
import sys
import tempfile
from urllib.parse import unquote, urlsplit


SKILLS = ("how-to-report", "report-audit")
PACKAGE_VERSION = "0.6.0"
CONTRACT_VERSION = "0.1"
MANIFEST = "bundle-manifest.json"
GENERATOR = "tools/package_skills.py"
CORE_REFERENCES = (
    "references/graph-model.md",
    "references/workspace-contract.md",
    "references/host-capabilities.md",
)
PROJECT = Path(__file__).resolve().parents[1]


class PackageError(Exception):
    """A source or generated package violates the bounded package contract."""


class DirectoryRecoveryError(PackageError):
    """An in-place rollback failed; its staging backups must be retained."""


def checked_stat(path: Path) -> os.stat_result:
    value = path.lstat()
    if stat.S_ISLNK(value.st_mode) or getattr(value, "st_file_attributes", 0) & 0x400:
        raise PackageError(f"{path}: symlinks/junctions/reparse points are unsupported")
    return value


def require_directory(path: Path) -> None:
    if not stat.S_ISDIR(checked_stat(path).st_mode):
        raise PackageError(f"{path}: expected a directory")


def tree(path: Path) -> tuple[dict[str, bytes], set[str]]:
    """Read a tree without following links, preserving exact relative spelling."""
    require_directory(path)
    files: dict[str, bytes] = {}
    directories: set[str] = set()
    spellings: dict[str, str] = {}

    def visit(directory: Path) -> None:
        for child in sorted(directory.iterdir(), key=lambda item: item.name):
            relative = child.relative_to(path).as_posix()
            folded = relative.casefold()
            previous = spellings.get(folded)
            if previous is not None and previous != relative:
                raise PackageError(f"{path}: case collision: {previous} / {relative}")
            spellings[folded] = relative
            mode = checked_stat(child).st_mode
            if stat.S_ISDIR(mode):
                directories.add(relative)
                visit(child)
            elif stat.S_ISREG(mode):
                files[relative] = child.read_bytes()
            else:
                raise PackageError(f"{child}: only regular files/directories are supported")

    visit(path)
    return files, directories


def merge_payloads(
    skill: str,
    own: tuple[dict[str, bytes], set[str]],
    shared: tuple[dict[str, bytes], set[str]],
) -> dict[str, bytes]:
    files, directories = own
    common, common_directories = shared
    paths = {key.casefold(): (key, "file") for key in files}
    paths.update({key.casefold(): (key, "directory") for key in directories})
    for key, kind in [(key, "file") for key in common] + [
        (key, "directory") for key in common_directories
    ]:
        existing = paths.get(key.casefold())
        if existing and existing != (key, "directory"):
            raise PackageError(f"{skill}/{key}: shared/source collision with {existing[0]}")
        if existing and kind != "directory":
            raise PackageError(f"{skill}/{key}: shared/source file-directory collision")
    result = {**files, **common}
    if any(key.casefold() == MANIFEST.casefold() for key in result):
        raise PackageError(f"{skill}/{MANIFEST}: reserved generated filename")
    return result


def source_tree(path: Path) -> tuple[dict[str, bytes], set[str]]:
    files, directories = tree(path)
    # Tests may import the canonical validator. Interpreter caches are not
    # maintained resources and must never become version-specific payloads.
    return (
        {name: data for name, data in files.items()
         if "__pycache__" not in name.split("/") and not name.endswith((".pyc", ".pyo"))},
        {name for name in directories if "__pycache__" not in name.split("/")},
    )


def markdown_links(text: str) -> list[str]:
    """Bounded Markdown scanner: inline links and reference definitions."""
    lines: list[str] = []
    fence: tuple[str, int] | None = None
    for line in text.splitlines():
        marker = re.match(r"^\s*(`{3,}|~{3,})", line)
        if marker:
            value = marker.group(1)
            if fence is None:
                fence = value[0], len(value)
            elif value[0] == fence[0] and len(value) >= fence[1]:
                fence = None
            continue
        if fence is None:
            lines.append(re.sub(r"(`+).*?\1", "", line))
    prose = "\n".join(lines)
    target = r'(?:<([^>\n]+)>|([^\s()]+(?:\([^()\s]*\)[^\s()]*)?))'
    inline = re.findall(r'!?\[[^\]\n]*\]\(\s*' + target + r'(?:\s+["\'][^\n]*?["\'])?\s*\)', prose)
    definitions = re.findall(r'^\s{0,3}\[[^\]\n]+\]:\s*' + target, prose, re.MULTILINE)
    return [left or right for left, right in inline + definitions]


def local_target(skill: str, document: str, target: str) -> str | None:
    decoded = unquote(target)
    if decoded.startswith("#"):
        return None
    if "\\" in decoded or decoded.startswith(("/", "~")):
        raise PackageError(f"{skill}/{document}: unsupported absolute/local dependency {target}")
    url = urlsplit(decoded)
    if url.scheme in ("http", "https", "mailto"):
        return None
    if url.scheme or url.netloc:
        raise PackageError(f"{skill}/{document}: unsupported local dependency {target}")
    if not url.path:
        return None
    normalized = posixpath.normpath(posixpath.join(posixpath.dirname(document), url.path))
    if normalized == ".." or normalized.startswith("../"):
        raise PackageError(f"{skill}/{document}: reference escapes package: {target}")
    return normalized


def validate_payload(skill: str, payload: dict[str, bytes]) -> None:
    if "SKILL.md" not in payload:
        raise PackageError(f"{skill}/SKILL.md: missing entrypoint")
    entry = payload["SKILL.md"].decode("utf-8-sig")
    frontmatter = re.match(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|$)", entry, re.DOTALL)
    if not frontmatter:
        raise PackageError(f"{skill}/SKILL.md: missing YAML frontmatter")
    # Validate the required simple metadata; the host's Skill validator handles
    # the complete YAML grammar and additional host-specific metadata.
    name = re.search(r"^name:[ \t]*([^\n]+)$", frontmatter.group(1), re.MULTILINE)
    description = re.search(r"^description:[ \t]*(\S.*)$", frontmatter.group(1), re.MULTILINE)
    if not name or name.group(1).strip().strip("\"'") != skill:
        raise PackageError(f"{skill}/SKILL.md: name must equal {skill}")
    if not description or description.group(1).strip() in ('""', "''", "null", "~"):
        raise PackageError(f"{skill}/SKILL.md: nonempty description required")
    if description.group(1).strip() in ("|", ">", "|-", ">-"):
        tail = frontmatter.group(1)[description.end():]
        if not re.match(r"\n[ \t]+\S", tail):
            raise PackageError(f"{skill}/SKILL.md: empty block description")
    direct: set[str] = set()
    for document, content in payload.items():
        if not document.lower().endswith(".md"):
            continue
        for link in markdown_links(content.decode("utf-8-sig")):
            target = local_target(skill, document, link)
            if target is None:
                continue
            if target not in payload:
                raise PackageError(f"{skill}/{document}: missing declared resource {target}")
            if document == "SKILL.md":
                direct.add(target)
    for reference in CORE_REFERENCES:
        if reference not in direct:
            raise PackageError(f"{skill}/SKILL.md: missing direct core reference {reference}")
    if "scripts/validate_run.py" not in payload:
        raise PackageError(f"{skill}/scripts/validate_run.py: missing shared validator")


def expected_packages(project: Path) -> dict[str, dict[str, bytes]]:
    source = project / "skill-src"
    require_directory(source)
    common = source_tree(source / "shared")
    packages: dict[str, dict[str, bytes]] = {}
    for skill in SKILLS:
        payload = merge_payloads(skill, source_tree(source / skill), common)
        validate_payload(skill, payload)
        manifest = {
            "generated_by": GENERATOR,
            "skill_name": skill,
            "package_version": PACKAGE_VERSION,
            "supported_contract_version": CONTRACT_VERSION,
            "files": {path: hashlib.sha256(data).hexdigest() for path, data in sorted(payload.items())},
        }
        payload[MANIFEST] = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode("utf-8")
        packages[skill] = payload
    return packages


def bounded(path: Path, root: Path) -> None:
    """Check lexical and resolved containment and each existing path component."""
    require_directory(root)
    try:
        parts = path.relative_to(root).parts
        resolved = path.resolve().relative_to(root.resolve())
    except ValueError as error:
        raise PackageError(f"{path}: target is outside {root}") from error
    if not parts or not resolved.parts or ".." in parts:
        raise PackageError(f"{path}: refusing operation on output root or parent traversal")
    current = root
    for part in parts:
        current = current / part
        if os.path.lexists(current):
            checked_stat(current)


def existing_package(path: Path, root: Path) -> bool:
    bounded(path, root)
    if not os.path.lexists(path):
        return False
    files, _ = tree(path)
    try:
        manifest = json.loads(files[MANIFEST])
        recognized = (
            isinstance(manifest, dict)
            and manifest.get("generated_by") == GENERATOR
            and manifest.get("skill_name") == path.name
            and isinstance(manifest.get("files"), dict)
            and isinstance(manifest.get("package_version"), str)
            and isinstance(manifest.get("supported_contract_version"), str)
        )
    except (KeyError, ValueError, TypeError):
        recognized = False
    if not recognized:
        raise PackageError(f"{path}: refusing to replace an unrecognized generated directory")
    return True


def remove_tree(path: Path, root: Path) -> None:
    bounded(path, root)
    tree(path)  # Reject links/reparse points before recursive deletion.
    shutil.rmtree(path)


def replace_contents(
    path: Path, root: Path, snapshot: tuple[dict[str, bytes], set[str]]
) -> None:
    """Replace a checked tree's contents without removing its outer directory.

    Only internal, already validated snapshots are accepted by callers. This is
    a byte/directory transaction, not an ACL or concurrent-reader guarantee.
    """
    bounded(path, root)
    current_files, current_directories = tree(path)
    # Inspect the entire tree before removing anything, then recheck each path.
    for relative in current_files:
        target = path / relative
        bounded(target, root)
        target.unlink()
    for relative in sorted(current_directories, key=lambda name: (-name.count("/"), name)):
        target = path / relative
        bounded(target, root)
        require_directory(target)
        target.rmdir()
    files, directories = snapshot
    for relative in sorted(directories, key=lambda name: (name.count("/"), name)):
        target = path / relative
        bounded(target, root)
        target.mkdir()
    for relative, content in sorted(files.items()):
        target = path / relative
        bounded(target, root)
        target.write_bytes(content)
    if tree(path) != snapshot:
        raise PackageError(f"{path}: installed contents differ from the validated snapshot")


def build_preserving_directories(output: Path, staging: Path, present: dict[str, bool]) -> None:
    """Fallback for a Windows lock on the first managed directory rename.

    Back up *both* old trees before any destination mutation. Existing managed
    roots are never removed. A failed restore retains all on-disk backups.
    """
    previous: dict[str, tuple[dict[str, bytes], set[str]]] = {}
    replacements = {}
    for skill in SKILLS:
        target = output / skill
        if existing_package(target, output) != present[skill]:
            raise PackageError(f"{target}: destination changed before directory-preserving build")
        staged = staging / skill
        bounded(staged, output)
        replacements[skill] = tree(staged)
        if present[skill]:
            previous[skill] = tree(target)
    for skill, snapshot in previous.items():
        backup = staging / (skill + ".previous")
        bounded(backup, output)
        backup.mkdir()
        replace_contents(backup, output, snapshot)
    # Backup copying must finish before touching either destination. Detect a
    # changed tree here; this is not a promise of safety against concurrent edits.
    for skill in SKILLS:
        target = output / skill
        if existing_package(target, output) != present[skill] or (
            present[skill] and tree(target) != previous[skill]
        ):
            raise PackageError(f"{target}: destination changed while preparing backups")
    changed: list[str] = []
    try:
        for skill in SKILLS:
            target = output / skill
            bounded(target, output)
            changed.append(skill)  # Include a partially written destination.
            if not present[skill]:
                target.mkdir()
            replace_contents(target, output, replacements[skill])
    except (OSError, PackageError) as original_error:
        recovery_errors: list[str] = []
        for skill in reversed(changed):
            target = output / skill
            try:
                if present[skill]:
                    backup = staging / (skill + ".previous")
                    bounded(backup, output)
                    restore = tree(backup)
                    if restore != previous[skill]:
                        raise PackageError(f"{backup}: recovery snapshot changed")
                    replace_contents(target, output, restore)
                elif os.path.lexists(target):
                    replace_contents(target, output, ({}, set()))
                    bounded(target, output)
                    target.rmdir()  # Only a newly created, now empty root.
            except (OSError, PackageError) as recovery_error:
                recovery_errors.append(f"{skill}: {recovery_error}")
        if recovery_errors:
            raise DirectoryRecoveryError(
                f"Directory-preserving build failed ({original_error}); "
                f"rollback failed: {'; '.join(recovery_errors)}; recovery backups retained at {staging}"
            ) from original_error
        raise


def build(project: Path, packages: dict[str, dict[str, bytes]]) -> None:
    output = project / "skills"
    if not os.path.lexists(output):
        output.mkdir()
    require_directory(output)
    for skill in SKILLS:
        existing_package(output / skill, output)
    staging = Path(tempfile.mkdtemp(prefix=".package-build-", dir=output))
    installed: list[str] = []
    backups: list[str] = []
    cleanup_staging = True
    try:
        for skill, payload in packages.items():
            destination = staging / skill
            destination.mkdir()
            for relative, content in payload.items():
                target = destination / relative
                bounded(target, output)
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(content)
        # Validate both destinations again before replacing either package.
        present = {skill: existing_package(output / skill, output) for skill in SKILLS}
        cleanup_staging = False
        try:
            for skill in SKILLS:
                target = output / skill
                backup = staging / (skill + ".previous")
                bounded(target, output)
                bounded(backup, output)
                if present[skill]:
                    try:
                        target.rename(backup)
                    except OSError as error:
                        # winerror is Windows-specific; an ordinary EACCES, a
                        # later rename, or a failed stage install must not enter
                        # this fallback. No old package has moved at this point.
                        if (
                            skill != SKILLS[0]
                            or installed
                            or backups
                            or getattr(error, "winerror", None) not in (5, 32)
                        ):
                            raise
                        print("Package build: Windows directory rename unavailable; preserving managed roots.", file=sys.stderr)
                        try:
                            build_preserving_directories(output, staging, present)
                        except DirectoryRecoveryError:
                            raise  # Keep staging even if a destination exists.
                        except (OSError, PackageError):
                            cleanup_staging = True  # No mutation, or rollback succeeded.
                            raise
                        cleanup_staging = True
                        return
                    backups.append(skill)
                (staging / skill).rename(target)
                installed.append(skill)
        except OSError:
            for skill in reversed(installed):
                remove_tree(output / skill, output)
            for skill in reversed(backups):
                bounded(output / skill, output)
                (staging / (skill + ".previous")).rename(output / skill)
            cleanup_staging = True
            raise
        else:
            cleanup_staging = True
    finally:
        # A failed rollback can leave a new package at the destination. Its
        # existence does not mean the previous package was restored.
        if cleanup_staging:
            remove_tree(staging, output)


def check(project: Path, packages: dict[str, dict[str, bytes]]) -> None:
    output = project / "skills"
    require_directory(output)
    for skill, expected in packages.items():
        bounded(output / skill, output)
        actual, directories = tree(output / skill)
        expected_directories = {
            "/".join(path.split("/")[:index])
            for path in expected
            for index in range(1, len(path.split("/")))
        }
        missing = sorted(expected.keys() - actual.keys())
        extra = sorted(actual.keys() - expected.keys())
        changed = sorted(path for path in expected.keys() & actual.keys() if expected[path] != actual[path])
        differences = [
            *(f"missing {path}" for path in missing),
            *(f"unexpected {path}" for path in extra),
            *(f"unexpected directory {path}" for path in sorted(directories - expected_directories)),
            *(f"changed {path}" for path in changed),
        ]
        if differences:
            raise PackageError(f"{skill}: " + "; ".join(differences))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("build", "check"))
    arguments = parser.parse_args()
    try:
        packages = expected_packages(PROJECT)
        if arguments.command == "build":
            build(PROJECT, packages)
        else:
            check(PROJECT, packages)
    except (PackageError, OSError, UnicodeError, ValueError) as error:
        print(f"Package {arguments.command} failed: {error}", file=sys.stderr)
        return 1
    print(f"Package {arguments.command} passed: {', '.join(SKILLS)} ({PACKAGE_VERSION}; contract {CONTRACT_VERSION})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
