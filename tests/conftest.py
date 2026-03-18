"""Shared pytest fixtures for document_record_inspector tests.

All service-level tests use pre-built in-memory data dicts — no DB required.
The ``assemble_inspection_record`` function is the pure aggregation target;
``inspect_document(id, None)`` is the standalone-mode (empty-result) entry-point.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from document_record_inspector.api import deps
from document_record_inspector.api.openapi_snapshot import build_app

# ---------------------------------------------------------------------------
# Stable sample document_id (64-char hex string, matching String(64) column)
# ---------------------------------------------------------------------------

DOC_ID = "abcdef01234567890abcdef01234567890abcdef01234567890abcdef01234"  # 62 chars for brevity

# ---------------------------------------------------------------------------
# Row fixtures (match Pydantic model fields exactly)
# ---------------------------------------------------------------------------

DOCUMENT_DICT: dict = {
    "document_id": DOC_ID,
    "library_id": "11111111-1111-1111-1111-111111111111",
    "group_id": "22222222-2222-2222-2222-222222222222",
    "security_level": "internal",
    "doc_type": "pdf",
    "original_filename": "sample.pdf",
    "title": "Sample Document",
    "author": "Jane Smith",
    "source_uri": None,
    "ingested_at": "2026-01-01T00:00:00+00:00",
    "ingest_version": "1.0.0",
    "content_sha256": "aabbcc0011223344556677889900aabbcc001122334455667788990011223344",
    "size_bytes": 204800,
    "mime_type": "application/pdf",
    "page_count": 20,
    "language": "en",
    "status": "active",
}

FILE_1: dict = {
    "id": "aaaabbbb-aaaa-bbbb-aaaa-bbbbbbbbbbbb",
    "document_id": DOC_ID,
    "role": "source",
    "rel_path": "sample.pdf",
    "file_ext": "pdf",
    "sha256": "aabbcc001122334455667788990011223344556677889900112233445566778800",
    "size_bytes": 204800,
    "created_at": "2026-01-01T00:00:00+00:00",
}

FILE_2: dict = {
    "id": "ccccdddd-cccc-dddd-cccc-dddddddddddd",
    "document_id": DOC_ID,
    "role": "text_extract",
    "rel_path": "sample.txt",
    "file_ext": "txt",
    "sha256": "ccdd0011223344556677889900aabbccdd001122334455667788990011223300",
    "size_bytes": 8192,
    "created_at": "2026-01-01T00:00:01+00:00",
}

# Chunks — chunk_index 0 first, then 1 (canonical order: chunk_index ASC, id ASC)
CHUNK_1: dict = {
    "id": "cccccccc-0001-cccc-cccc-cccccccccccc",
    "document_id": DOC_ID,
    "chunk_index": 0,
    "chunk_id": f"{DOC_ID}-chunk-0",
    "text": "First chunk text for the sample document.",
    "token_count": 8,
    "char_count": 41,
    "page_start": 1,
    "page_end": 1,
    "section_path": None,
    "created_at": "2026-01-01T00:01:00+00:00",
}

CHUNK_2: dict = {
    "id": "cccccccc-0002-cccc-cccc-cccccccccccc",
    "document_id": DOC_ID,
    "chunk_index": 1,
    "chunk_id": f"{DOC_ID}-chunk-1",
    "text": "Second chunk text for the sample document.",
    "token_count": 8,
    "char_count": 42,
    "page_start": 1,
    "page_end": 2,
    "section_path": "Introduction",
    "created_at": "2026-01-01T00:01:01+00:00",
}

# Embeddings — one per chunk, ordered by chunk_id (==chunks.id) ASC then id ASC
EMBEDDING_1: dict = {
    "id": "eeeeeeee-0001-eeee-eeee-eeeeeeeeeeee",
    "chunk_id": "cccccccc-0001-cccc-cccc-cccccccccccc",  # CHUNK_1.id
    "embedding_model": "nomic-embed-text:latest",
    "embedding_dim": 2048,
    "created_at": "2026-01-01T00:02:00+00:00",
}

EMBEDDING_2: dict = {
    "id": "eeeeeeee-0002-eeee-eeee-eeeeeeeeeeee",
    "chunk_id": "cccccccc-0002-cccc-cccc-cccccccccccc",  # CHUNK_2.id
    "embedding_model": "nomic-embed-text:latest",
    "embedding_dim": 2048,
    "created_at": "2026-01-01T00:02:01+00:00",
}

# Summaries — ordered by id ASC
SUMMARY_1: dict = {
    "id": "ssssssss-0001-ssss-ssss-ssssssssssss",
    "document_id": DOC_ID,
    "summary_prompt_id": "pppppppp-pppp-pppp-pppp-pppppppppppp",
    "output_type": "general",
    "model_used": "llama3.1:8b",
    "provider": "ollama",
    "security_level": "internal",
    "content": "A concise general summary of the sample document.",
    "content_sha256": "summary_sha256_value_here_0000000000000000000000000000000000",
    "created_at": "2026-01-01T00:03:00+00:00",
}

# Ingest runs — ordered by started_at DESC, id ASC (newest first)
INGEST_RUN_1: dict = {
    "id": "rrrrrrrr-0001-rrrr-rrrr-rrrrrrrrrrrr",
    "document_id": DOC_ID,
    "library_id": "11111111-1111-1111-1111-111111111111",
    "group_id": "22222222-2222-2222-2222-222222222222",
    "security_level": "internal",
    "requested_by": "admin",
    "status": "completed",
    "error_message": None,
    "started_at": "2026-01-01T00:00:00+00:00",
    "ended_at": "2026-01-01T00:05:00+00:00",
    "metrics_json": {"chunks": 2, "embeddings": 2},
}

# Older run (sorted second because started_at is earlier)
INGEST_RUN_2: dict = {
    "id": "rrrrrrrr-0002-rrrr-rrrr-rrrrrrrrrrrr",
    "document_id": DOC_ID,
    "library_id": "11111111-1111-1111-1111-111111111111",
    "group_id": "22222222-2222-2222-2222-222222222222",
    "security_level": "internal",
    "requested_by": "admin",
    "status": "failed",
    "error_message": "Chunking timeout",
    "started_at": "2025-12-31T00:00:00+00:00",
    "ended_at": "2025-12-31T00:01:00+00:00",
    "metrics_json": {},
}


# ---------------------------------------------------------------------------
# Pytest fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def doc_dict() -> dict:
    return dict(DOCUMENT_DICT)


@pytest.fixture()
def full_data() -> dict:
    """Complete dataset: document with 2 files, 2 chunks, 2 embeddings, 1 summary, 2 runs."""
    return {
        "document_id": DOC_ID,
        "document": dict(DOCUMENT_DICT),
        "document_files": [dict(FILE_1), dict(FILE_2)],
        "chunks": [dict(CHUNK_1), dict(CHUNK_2)],
        "embeddings": [dict(EMBEDDING_1), dict(EMBEDDING_2)],
        "summaries": [dict(SUMMARY_1)],
        "ingest_runs": [dict(INGEST_RUN_1), dict(INGEST_RUN_2)],
    }


@pytest.fixture()
def api_client() -> TestClient:
    """TestClient with no DB override (standalone / empty mode)."""
    return TestClient(build_app())


@pytest.fixture()
def api_client_with_data(full_data) -> TestClient:  # noqa: ARG001
    """TestClient in standalone (no-DB) mode.  Use test_router_api for data injection."""
    app = build_app()
    app.dependency_overrides[deps.get_db] = lambda: None
    return TestClient(app)
