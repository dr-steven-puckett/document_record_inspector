"""API smoke tests for document_record_inspector."""
from __future__ import annotations

from fastapi.testclient import TestClient

from document_record_inspector.api import deps
from document_record_inspector.api.openapi_snapshot import build_app
from tests.conftest import DOC_ID


def _client() -> TestClient:
    app = build_app()
    app.dependency_overrides[deps.get_db] = lambda: None
    return TestClient(app)


# ---------------------------------------------------------------------------
# Health endpoint
# ---------------------------------------------------------------------------


def test_health_status_200() -> None:
    resp = _client().get("/health")
    assert resp.status_code == 200


def test_health_json_shape() -> None:
    resp = _client().get("/health")
    data = resp.json()
    assert "status" in data
    assert data["status"] == "ok"


# ---------------------------------------------------------------------------
# Inspect endpoint
# ---------------------------------------------------------------------------


def test_inspect_returns_200() -> None:
    resp = _client().get(f"/records/{DOC_ID}")
    assert resp.status_code == 200


def test_inspect_response_has_required_keys() -> None:
    resp = _client().get(f"/records/{DOC_ID}")
    data = resp.json()
    required = {"query", "document", "document_files", "chunks",
                "embeddings", "summaries", "ingest_runs", "diagnostics"}
    assert required.issubset(data.keys())


def test_inspect_diagnostics_has_required_keys() -> None:
    resp = _client().get(f"/records/{DOC_ID}")
    diag = resp.json()["diagnostics"]
    required = {
        "document_found", "has_files", "has_chunks", "has_embeddings",
        "has_summaries", "ingest_run_count", "chunk_count",
        "embedding_count", "summary_count", "file_count", "possible_issues",
    }
    assert required.issubset(diag.keys())


def test_inspect_query_echoes_document_id() -> None:
    doc_id = "test-document-123"
    resp = _client().get(f"/records/{doc_id}")
    assert resp.status_code == 200
    assert resp.json()["query"]["document_id"] == doc_id

