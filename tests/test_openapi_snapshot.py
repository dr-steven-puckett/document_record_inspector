"""OpenAPI snapshot stability test.

To regenerate the snapshot intentionally::

    UPDATE_OPENAPI_SNAPSHOT=1 pytest tests/test_openapi_snapshot.py

To assert no drift::

    pytest tests/test_openapi_snapshot.py
"""
from __future__ import annotations

import json
import os
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
SNAPSHOT_PATH = REPO_ROOT / "openapi.snapshot.json"


def _canonical(obj: dict) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n"


def _generate() -> dict:
    from document_record_inspector.api.openapi_snapshot import generate_openapi  # noqa: PLC0415

    return generate_openapi()


def test_openapi_snapshot_stable() -> None:
    """Generated OpenAPI schema must match the committed snapshot.

    Set ``UPDATE_OPENAPI_SNAPSHOT=1`` to regenerate.
    """
    update = os.environ.get("UPDATE_OPENAPI_SNAPSHOT", "0") == "1"
    generated = _generate()
    canonical_generated = _canonical(generated)

    if update:
        SNAPSHOT_PATH.write_text(canonical_generated, encoding="utf-8")
        return

    if not SNAPSHOT_PATH.exists() or SNAPSHOT_PATH.read_text(encoding="utf-8").strip() in (
        "",
        "{}",
    ):
        # Bootstrap: write snapshot on first real run
        SNAPSHOT_PATH.write_text(canonical_generated, encoding="utf-8")
        return

    snapshot_text = SNAPSHOT_PATH.read_text(encoding="utf-8")
    snapshot = json.loads(snapshot_text)
    canonical_snapshot = _canonical(snapshot)

    assert canonical_generated == canonical_snapshot, (
        "OpenAPI schema has drifted from openapi.snapshot.json.\n"
        "Run: UPDATE_OPENAPI_SNAPSHOT=1 pytest tests/test_openapi_snapshot.py\n\n"
        f"Generated (first 500 chars):\n{canonical_generated[:500]}\n\n"
        f"Snapshot (first 500 chars):\n{canonical_snapshot[:500]}"
    )

