#!/usr/bin/env python3
"""Validate/display the current content designs, reusing the historical input checker."""
from pathlib import Path
import importlib.util
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("content_cases_shared", HERE / "validate_cases.py")
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)
checker.ROOT = HERE.parent / "content-0.6.0"

if __name__ == "__main__":
    sys.exit(checker.main())
