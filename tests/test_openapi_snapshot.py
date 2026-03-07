"""test_openapi_snapshot — drift detection for the OpenAPI schema.

Normal run:   compare generate_openapi() output against the saved
              openapi.snapshot.json file.  Any drift fails the test.

Update mode:  UPDATE_OPENAPI_SNAPSHOT=1 pytest tests/test_openapi_snapshot.py
              regenerates the snapshot file in-place.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from document_record_inspector.api.openapi_snapshot import generate_openapi

REPO_ROOT = Path(__file__).parent.parent
SNAPSHOT_FILE = REPO_ROOT / "openapi.snapshot.json"


@pytest.fixture(scope="module")
def live_schema() -> dict:
    return generate_openapi()


# ---------------------------------------------------------------------------
# Update mode — regenerate snapshot
# ---------------------------------------------------------------------------


def test_update_snapshot_when_env_set(live_schema):
    """Write snapshot when UPDATE_OPENAPI_SNAPSHOT=1, then skip comparison."""
    if os.environ.get("UPDATE_OPENAPI_SNAPSHOT") != "1":
        pytest.skip("UPDATE_OPENAPI_SNAPSHOT not set")

    SNAPSHOT_FILE.write_text(
        json.dumps(live_schema, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    assert SNAPSHOT_FILE.exists()


# ---------------------------------------------------------------------------
# Comparison mode — snapshot must match live schema
# ---------------------------------------------------------------------------


def test_snapshot_file_exists():
    assert SNAPSHOT_FILE.exists(), (
        f"openapi.snapshot.json not found at {SNAPSHOT_FILE}. "
        "Run: UPDATE_OPENAPI_SNAPSHOT=1 pytest tests/test_openapi_snapshot.py"
    )


def test_snapshot_is_valid_json():
    raw = SNAPSHOT_FILE.read_text(encoding="utf-8")
    data = json.loads(raw)
    assert isinstance(data, dict)


def test_snapshot_matches_live_schema(live_schema):
    if os.environ.get("UPDATE_OPENAPI_SNAPSHOT") == "1":
        pytest.skip("Running in update mode — skipping comparison")

    if not SNAPSHOT_FILE.exists():
        pytest.skip("Snapshot file not yet generated")

    saved = json.loads(SNAPSHOT_FILE.read_text(encoding="utf-8"))

    if saved == {}:
        pytest.skip("Snapshot is placeholder {}; run UPDATE_OPENAPI_SNAPSHOT=1 first")

    assert live_schema == saved, (
        "OpenAPI schema has drifted from snapshot.\n"
        "Re-run with UPDATE_OPENAPI_SNAPSHOT=1 to update, "
        "or revert the schema change."
    )


# ---------------------------------------------------------------------------
# Schema structure sanity
# ---------------------------------------------------------------------------


def test_live_schema_has_openapi_key(live_schema):
    assert "openapi" in live_schema


def test_live_schema_has_paths(live_schema):
    assert "paths" in live_schema
    assert len(live_schema["paths"]) >= 2


def test_live_schema_contains_health_path(live_schema):
    paths = live_schema["paths"]
    health_paths = [p for p in paths if "health" in p]
    assert len(health_paths) >= 1


def test_live_schema_contains_documents_path(live_schema):
    paths = live_schema["paths"]
    doc_paths = [p for p in paths if "documents" in p]
    assert len(doc_paths) >= 1


def test_live_schema_deterministic(live_schema):
    """Calling generate_openapi() twice must return identical output."""
    second = generate_openapi()
    assert live_schema == second
