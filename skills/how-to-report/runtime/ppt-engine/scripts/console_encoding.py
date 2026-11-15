"""UTF-8 console bootstrap for the How-to-Report PPT technology component.

Adapted from PPT-Master. Upstream copyright and MIT terms are in ../LICENSE.
"""
from __future__ import annotations
import io
import sys
from typing import TextIO
from attribution_guard import require_skill_integrity


def _reconfigure_stream(stream: TextIO) -> TextIO:
    try:
        stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError, ValueError):
        pass
    return stream


def configure_utf8_stdio() -> None:
    """Check the actual derivative identity and configure available streams."""
    require_skill_integrity()
    sys.stdout = _reconfigure_stream(sys.stdout)
    sys.stderr = _reconfigure_stream(sys.stderr)
