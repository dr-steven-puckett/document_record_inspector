"""document_record_inspector.core.determinism — canonical JSON serialization.

Identical inputs must produce byte-identical outputs across all platforms and
Python versions.  This is the sole JSON serialisation entry-point for the
tool; nowhere else should json.dumps be called with custom options.
"""
from __future__ import annotations

import json


def canonical_json(obj: object) -> str:
    """Serialize *obj* to deterministic, compact JSON.

    Rules enforced:
    - Keys sorted alphabetically at every nesting level.
    - No extra whitespace (compact ``separators``).
    - ASCII-safe=False preserves non-ASCII characters verbatim.

    A single trailing newline is intentionally NOT added here; callers that
    write to stdout or files should append ``\\n`` themselves.
    """
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

