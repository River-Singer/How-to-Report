"""Read-only write destination guard shared by independently installed Skills."""
from pathlib import Path
import os
import stat
import re


def require_external_write(path, known_roots=()) -> Path:
    """Reject network/device, linked and recognized installed-package paths.

    Inspect only the destination ancestry and explicitly supplied package roots.
    This does not create files or promise a transaction against unrelated writers.
    Callers must separately enforce new outputs / controlled Run mutations.
    """
    path = Path(path)
    if str(path).startswith(("\\\\", "//")):
        raise ValueError("expected a local write path, not UNC or device path")
    for component in path.parts:
        if component == "..":
            raise ValueError("write path must not contain parent traversal")
        if component == path.anchor:
            continue
        if ":" in component or re.fullmatch(r"(?i)(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\..*)?", component.rstrip(" .")):
            raise ValueError("write path contains a device name or alternate stream")
    absolute = path.absolute()
    for part in (absolute, *absolute.parents):
        if os.path.lexists(part):
            info = part.lstat()
            if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
                raise ValueError("write path contains a link/reparse point")
        if any(os.path.lexists(part / marker) for marker in ("SKILL.md", "bundle-manifest.json")):
            raise ValueError("write destination must be outside installed Skill directories")
    try:
        resolved = absolute.resolve()
    except RuntimeError as exc:
        raise ValueError("cannot resolve write destination") from exc
    if str(resolved).startswith(("\\\\", "//")):
        raise ValueError("expected a local write path, not UNC or device path")
    if any(resolved.is_relative_to(Path(root).resolve()) for root in known_roots):
        raise ValueError("write destination must be outside the installed Skill")
    return resolved
