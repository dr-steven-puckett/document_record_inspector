"""Contract/schema tests for document_record_inspector Pydantic models."""
from __future__ import annotations

import pytest
from pydantic import ValidationError

from document_record_inspector.api.schemas import (
    ChunkRow,
    DiagnosticsModel,
    DocumentFileRow,
    DocumentRow,
    EmbeddingRow,
    IngestRunRow,
    InspectionResponse,
    QueryInfo,
    SummaryRow,
)
from document_record_inspector.core.service import assemble_inspection_record
from tests.conftest import (
    CHUNK_1,
    DOC_ID,
    DOCUMENT_DICT,
    EMBEDDING_1,
    FILE_1,
    INGEST_RUN_1,
    SUMMARY_1,
)

# ---------------------------------------------------------------------------
# QueryInfo
# ---------------------------------------------------------------------------


def test_query_info_round_trip() -> None:
    q = QueryInfo(document_id="abc")
    assert q.document_id == "abc"


# ---------------------------------------------------------------------------
# DocumentRow
# ---------------------------------------------------------------------------


def test_document_row_required_fields() -> None:
    doc = DocumentRow(**DOCUMENT_DICT)
    assert doc.document_id == DOC_ID
    assert doc.security_level == "internal"
    assert doc.doc_type == "pdf"


def test_document_row_optional_none() -> None:
    data = dict(DOCUMENT_DICT)
    data["title"] = None
    data["author"] = None
    data["source_uri"] = None
    data["original_filename"] = None
    doc = DocumentRow(**data)
    assert doc.title is None
    assert doc.author is None


# ---------------------------------------------------------------------------
# DocumentFileRow
# ---------------------------------------------------------------------------


def test_document_file_row_round_trip() -> None:
    f = DocumentFileRow(**FILE_1)
    assert f.role == "source"
    assert f.file_ext == "pdf"


# ---------------------------------------------------------------------------
# ChunkRow
# ---------------------------------------------------------------------------


def test_chunk_row_round_trip() -> None:
    c = ChunkRow(**CHUNK_1)
    assert c.chunk_index == 0
    assert c.char_count == 41


# ---------------------------------------------------------------------------
# EmbeddingRow
# ---------------------------------------------------------------------------


def test_embedding_row_has_no_vector_field() -> None:
    """The vector field must NOT appear in EmbeddingRow (intentionally excluded)."""
    e = EmbeddingRow(**EMBEDDING_1)
    data = e.model_dump()
    assert "vector" not in data
    assert e.embedding_dim == 2048


# ---------------------------------------------------------------------------
# SummaryRow
# ---------------------------------------------------------------------------


def test_summary_row_round_trip() -> None:
    s = SummaryRow(**SUMMARY_1)
    assert s.output_type == "general"
    assert s.provider == "ollama"


# ---------------------------------------------------------------------------
# IngestRunRow
# ---------------------------------------------------------------------------


def test_ingest_run_row_round_trip() -> None:
    r = IngestRunRow(**INGEST_RUN_1)
    assert r.status == "completed"
    assert isinstance(r.metrics_json, dict)


def test_ingest_run_nullable_document_id() -> None:
    data = dict(INGEST_RUN_1)
    data["document_id"] = None
    r = IngestRunRow(**data)
    assert r.document_id is None


# ---------------------------------------------------------------------------
# DiagnosticsModel
# ---------------------------------------------------------------------------


def test_diagnostics_ge_zero() -> None:
    d = DiagnosticsModel(
        document_found=True,
        has_files=True,
        has_chunks=True,
        has_embeddings=True,
        has_summaries=True,
        ingest_run_count=1,
        chunk_count=5,
        embedding_count=5,
        summary_count=1,
        file_count=2,
        possible_issues=[],
    )
    assert d.chunk_count == 5


def test_diagnostics_negative_count_rejected() -> None:
    with pytest.raises(ValidationError):
        DiagnosticsModel(
            document_found=True,
            has_files=False,
            has_chunks=False,
            has_embeddings=False,
            has_summaries=False,
            ingest_run_count=-1,  # invalid
            chunk_count=0,
            embedding_count=0,
            summary_count=0,
            file_count=0,
            possible_issues=[],
        )


# ---------------------------------------------------------------------------
# InspectionResponse round-trip via assemble_inspection_record
# ---------------------------------------------------------------------------


def test_full_response_is_inspection_response(full_data) -> None:
    result = assemble_inspection_record(**full_data)
    assert isinstance(result, InspectionResponse)
    # Serialise and re-parse to confirm JSON round-trip
    as_dict = result.model_dump()
    rebuilt = InspectionResponse(**as_dict)
    assert rebuilt == result


def test_response_document_none_is_valid() -> None:
    result = assemble_inspection_record(
        document_id="missing",
        document=None,
        document_files=[],
        chunks=[],
        embeddings=[],
        summaries=[],
        ingest_runs=[],
    )
    assert isinstance(result, InspectionResponse)
    assert result.document is None

