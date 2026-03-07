"""test_api_smoke — FastAPI TestClient smoke tests.

Uses the tool's own fixture file in standalone catalog mode via a test
override of the db dependency, so no DATABASE_URL is needed.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from document_record_inspector.api.router import router
from document_record_inspector.api.deps import get_db
from document_record_inspector.core import service
from document_record_inspector.core.catalog_loader import load_fixture

FIXTURE = "tests/fixtures/sample_record.json"
DOC_ID = "aaaa1111bbbb2222cccc3333dddd4444eeee5555ffff6666aaaa1111bbbb2222"
MISSING_ID = "0000000000000000000000000000000000000000000000000000000000000000"


# ---------------------------------------------------------------------------
# Test db dependency — uses fixture data instead of a real DB
# ---------------------------------------------------------------------------


class _FixtureSession:
    """Minimal fake Session that serves fixture data for inspect_from_db calls."""

    def __init__(self, fixture: dict):
        self._fixture = fixture

    def execute(self, *args, **kwargs):
        raise NotImplementedError("FixtureSession does not support raw SQL")


def _override_get_db_for_fixture(fixture: dict):
    """Return a FastAPI dependency override that yields a fixture-backed callable."""

    def _dep():
        yield fixture

    return _dep


@pytest.fixture(scope="module")
def client():
    """TestClient with get_db overridden to call inspect_from_fixture."""
    fixture = load_fixture(FIXTURE)

    # Patch service.inspect_from_db to delegate to inspect_from_fixture
    # when a dict is passed instead of a Session (test mode).
    original_inspect = service.inspect_from_db

    def _patched_inspect(db, document_id, *, include_text=False, include_vectors=False):
        if isinstance(db, dict):
            return service.inspect_from_fixture(
                db, document_id,
                include_text=include_text,
                include_vectors=include_vectors,
            )
        return original_inspect(db, document_id, include_text=include_text, include_vectors=include_vectors)

    service.inspect_from_db = _patched_inspect

    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_db] = lambda: fixture

    yield TestClient(app)

    service.inspect_from_db = original_inspect


# ---------------------------------------------------------------------------
# GET /v1/tools/document_record_inspector/health
# ---------------------------------------------------------------------------


def test_health_status_ok(client):
    resp = client.get("/v1/tools/document_record_inspector/health")
    assert resp.status_code == 200


def test_health_response_shape(client):
    data = client.get("/v1/tools/document_record_inspector/health").json()
    assert data["status"] == "ok"
    assert data["tool_id"] == "document_record_inspector"


def test_health_only_expected_keys(client):
    data = client.get("/v1/tools/document_record_inspector/health").json()
    assert set(data.keys()) == {"status", "tool_id"}


# ---------------------------------------------------------------------------
# GET /v1/tools/document_record_inspector/documents/{document_id}
# ---------------------------------------------------------------------------


def test_inspect_success_200(client):
    resp = client.get(f"/v1/tools/document_record_inspector/documents/{DOC_ID}")
    assert resp.status_code == 200


def test_inspect_response_top_level_keys(client):
    data = client.get(f"/v1/tools/document_record_inspector/documents/{DOC_ID}").json()
    assert set(data.keys()) == {"document", "files", "chunks", "embeddings", "summaries", "ingest_runs", "counts"}


def test_inspect_document_present(client):
    data = client.get(f"/v1/tools/document_record_inspector/documents/{DOC_ID}").json()
    assert data["document"]["document_id"] == DOC_ID


def test_inspect_counts_shape(client):
    data = client.get(f"/v1/tools/document_record_inspector/documents/{DOC_ID}").json()
    counts = data["counts"]
    assert set(counts.keys()) == {"files", "chunks", "embeddings", "summaries", "ingest_runs"}
    for v in counts.values():
        assert isinstance(v, int)


def test_inspect_not_found_404(client):
    resp = client.get(f"/v1/tools/document_record_inspector/documents/{MISSING_ID}")
    assert resp.status_code == 404


def test_inspect_text_suppressed_by_default(client):
    data = client.get(f"/v1/tools/document_record_inspector/documents/{DOC_ID}").json()
    for chunk in data["chunks"]:
        assert chunk["text"] is None


def test_inspect_text_included_when_requested(client):
    data = client.get(
        f"/v1/tools/document_record_inspector/documents/{DOC_ID}?include_text=true"
    ).json()
    texts = [c["text"] for c in data["chunks"]]
    assert any(t is not None for t in texts)


def test_inspect_vectors_suppressed_by_default(client):
    data = client.get(f"/v1/tools/document_record_inspector/documents/{DOC_ID}").json()
    for emb in data["embeddings"]:
        assert emb["vector"] is None


def test_inspect_files_sorted(client):
    data = client.get(f"/v1/tools/document_record_inspector/documents/{DOC_ID}").json()
    files = data["files"]
    roles = [f["role"] for f in files]
    # aux before primary
    assert roles == sorted(roles)


def test_inspect_chunks_sorted_by_index(client):
    data = client.get(f"/v1/tools/document_record_inspector/documents/{DOC_ID}").json()
    indexes = [c["chunk_index"] for c in data["chunks"]]
    assert indexes == sorted(indexes)


def test_inspect_response_deterministic(client):
    r1 = client.get(f"/v1/tools/document_record_inspector/documents/{DOC_ID}").json()
    r2 = client.get(f"/v1/tools/document_record_inspector/documents/{DOC_ID}").json()
    assert r1 == r2
