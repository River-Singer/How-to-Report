"""Identity and retained attribution for the extracted HTR technology component.

Adapted from PPT-Master. Its complete distribution identity is distinct from
this derivative component. Original copyright and license remain in ../LICENSE.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
_LICENSE_SHA256 = "80cefc234c1ec12a8cece4344f16300c634fa03df7891686fcf979e3828f0921"


def require_skill_integrity() -> None:
    """Verify the component identity and retained upstream attribution."""
    try:
        metadata = json.loads((_ROOT / "provenance.json").read_text(encoding="utf-8"))
        retained_license = (_ROOT / "LICENSE").read_bytes().decode("utf-8").replace("\r\n", "\n")
        valid = metadata.get("component") == "how-to-report.ppt-engine" and hashlib.sha256(retained_license.encode()).hexdigest() == _LICENSE_SHA256
    except (OSError, UnicodeError, ValueError):
        valid = False
    if not valid:
        raise RuntimeError("PPT component identity or retained upstream LICENSE is missing or changed")
