"""Router/API tests for document_record_inspector.

All tests exercise the FastAPI router via TestClient.  The ``get_db``
dependency is overridden to avoid requiring a real database:
- standalone path: ``get_db`` yields ``None``  → service returns empty result
- data path: ``get_db`` yields a mock whose inspect path is further patched
  to return pre-built InspectionResponse objects.
"""
from __future__ import annotations

from fastapi.testclient import TestClient

from document_record_inspector.api import deps
from document_record_inspector.api.openapi_snapshot import build_app
from document_record_inspector.api.schemas import InspectionResponse
from document_record_inspector.core.service import (
    ISSUE_DOCUMENT_MISSING,
    assemble_inspection_record,
)
from tests.conftest import DOC_ID


def _standalone_client() -> TestClient:
    """Client with no DB (db=None path)."""
    app = build_app()
    app.dependency_overrides[deps.get_db] = lambda: None
    return TestClient(app)


def _data_client(data: dict) -> TestClient:
    """Client that patches inspect_document to return a pre-built response."""
    import document_record_inspector.api.router as _router_mod  # noqa: PLC0415

    prebuilt = assemble_inspection_record(**data)

    app = build_app()
    app.dependency_overrides[deps.get_db] = lambda: None

    # Monkeypatch inspect_document to return prebuilt regardless of db
    original = _router_mod.inspect_document

    def _patched(document_id: str, db):
        return prebuilt

    _router_mod.inspect_document = _patched
    try:
        return TestClient(app)
    finally:
        _router_mod.inspect_document = original


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------


def test_health_returns_200(api_client) -> None:
    resp = api_client.get("/health")
    assert resp.status_code == 200


def test_health_body(api_client) -> None:
    resp = api_client.get("/health")
    assert resp.json() == {"status": "ok"}


# ---------------------------------------------------------------------------
# GET /records/{document_id} -- standalone mode (db=None)
# ---------------------------------------------------------------------------


def test_inspect_standalone_returns_200() -> None:
    client = _standalone_client()
    resp = client.get(f"/records/{DOC_ID}")
    assert resp.status_code == 200


def test_inspect_standalone_document_null() -> None:
    client = _standalone_client()
    resp = client.get(f"/records/{DOC_ID}")
    data = resp.json()
    assert data["document"] is None


def test_inspect_standalone_document_missing_issue() -> None:
    client = _standalone_client()
    resp = client.get(f"/records/{DOC_ID}")
    data = resp.json()
    assert ISSUE_DOCUMENT_MISSING in data["diagnostics"]["possible_issues"]


def test_inspect_standalone_empty_collections() -> None:
    client = _standalone_client()
    resp = client.get(f"/records/{DOC_ID}")
    data = resp.json()
    assert data["document_files"] == []
    assert data["chunks"] == []
    assert data["embeddings"] == []
    assert data["summaries"] == []
    assert data["ingest_runs"] == []


def test_inspect_standalone_query_echo() -> None:
    client = _standalone_client()
    resp = client.get(f"/records/{DOC_ID}")
    data = resp.json()
    assert data["query"]["document_id"] == DOC_ID


def test_inspect_response_validates_as_schema() -> None:
    client = _standalone_client()
    resp = client.get(f"/records/{DOC_ID}")
    # Must parse cleanly into the response model
    InspectionResponse(**resp.json())


# ---------------------------------------------------------------------------
# GET /records/{document_id} -- data mode (patched inspect_document)
# ---------------------------------------------------------------------------


def test_inspect_with_data_returns_200(full_data) -> None:
    import document_record_inspector.api.router as _router_mod  # noqa: PLC0415

    prebuilt = assemble_inspection_record(**full_data)
    original = _router_mod.inspect_document
    _router_mod.inspect_document = lambda doc_id, db: prebuilt
    try:
        client = _standalone_client()
        resp = client.get(f"/records/{DOC_ID}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["document"] is not None
        assert data["diagnostics"]["chunk_count"] == 2
    finally:
        _router_mod.inspect_document = original


def test_inspect_response_is_deterministic(full_data) -> None:
    """Two identical requests must return identical JSON bodies."""
    import document_record_inspector.api.router as _router_mod  # noqa: PLC0415

    prebuilt = assemble_inspection_record(**full_data)
    original = _router_mod.inspect_document
    _router_mod.inspect_document = lambda doc_id, db: prebuilt
    try:
        client = _standalone_client()
        r1 = client.get(f"/records/{DOC_ID}").json()
        r2 = client.get(f"/records/{DOC_ID}").json()
        assert r1 == r2
    finally:
        _router_mod.inspect_document = original


# ---------------------------------------------------------------------------
# Error cases
# ---------------------------------------------------------------------------


def test_inspect_empty_id_segment_not_found() -> None:
    """Router returns 404 on missing path segment (FastAPI routing)."""
    client = _standalone_client()
    resp = client.get("/records/")
    assert resp.status_code in (404, 405)


def test_health_response_is_deterministic(api_client) -> None:
    r1 = api_client.get("/health").json()
    r2 = api_client.get("/health").json()
    assert r1 == r2

