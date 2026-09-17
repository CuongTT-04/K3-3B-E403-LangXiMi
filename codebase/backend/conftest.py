"""Test bootstrap: make ``app`` importable regardless of the invocation cwd,
and make stdout/stderr tolerant of non-ASCII text on consoles whose default
codepage is not UTF-8 (observed on Windows), so a failing assertion never
turns into an unrelated UnicodeEncodeError.
"""
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

for _stream_name in ("stdout", "stderr"):
    _stream = getattr(sys, _stream_name)
    if hasattr(_stream, "reconfigure"):
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
