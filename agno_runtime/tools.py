from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Callable


def now_utc() -> str:
    """Return current UTC time in ISO-8601 format."""
    return datetime.now(timezone.utc).isoformat()


def read_text_file(path: str) -> str:
    """Read UTF-8 text from a given path."""
    return Path(path).read_text(encoding="utf-8")


def write_text_file(path: str, content: str) -> str:
    """Write UTF-8 text to a given path."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    return f"written:{target}"


BUILTIN_TOOL_REGISTRY: dict[str, Callable] = {
    "now_utc": now_utc,
    "read": read_text_file,
    "write": write_text_file,
    "edit": write_text_file,
}
