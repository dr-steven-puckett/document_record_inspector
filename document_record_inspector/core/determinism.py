"""document_record_inspector.core.determinism — canonical JSON serialization helpers."""
from __future__ import annotations

import json


def canonical_json(obj: dict) -> str:
    """Return a canonical JSON string for *obj*.

    Contract:
    - json.dumps with sort_keys=True, separators=(',', ':'), ensure_ascii=False
    - exactly one trailing newline appended
    - UTF-8 safe (ensure_ascii=False)
    """
    return (
        json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        + "\n"
    )


def canonical_json_bytes(obj: dict) -> bytes:
    """Return canonical_json(obj) encoded as UTF-8 bytes."""
    return canonical_json(obj).encode("utf-8")
