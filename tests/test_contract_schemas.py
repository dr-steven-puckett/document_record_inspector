"""Tests for Pydantic request/response schema contracts."""
from __future__ import annotations

import pytest
from pydantic import ValidationError

from document_record_inspector.api.schemas import (
    ChunkRow,
    DocumentFileRow,
    DocumentRow,
    EmbeddingRow,
    HealthResponse,
    IngestRunRow,
    InspectionCounts,
    InspectionResponse,
    SummaryRow,
)


DOC_ID = "aaaa1111bbbb2222cccc3333dddd4444eeee5555ffff6666aaaa1111bbbb2222"


class TestHealthResponse:
    def test_required_fields(self):
        h = HealthResponse(status="ok", tool_id="document_record_inspector")
        assert h.status == "ok"
        assert h.tool_id == "document_record_inspector"

    def test_model_dump_keys(self):
        h = HealthResponse(status="ok", tool_id="document_record_inspector")
        assert set(h.model_dump().keys()) == {"status", "tool_id"}

    def test_missing_status_raises(self):
        with pytest.raises(ValidationError):
            HealthResponse(tool_id="document_record_inspector")  # type: ignore[call-arg]

    def test_missing_tool_id_raises(self):
        with pytest.raises(ValidationError):
            HealthResponse(status="ok")  # type: ignore[call-arg]


class TestInspectionCounts:
    def test_all_fields(self):
        c = InspectionCounts(files=1, chunks=2, embeddings=2, summaries=1, ingest_runs=1)
        assert c.files == 1
        assert c.chunks == 2
        assert c.embeddings == 2
        assert c.summaries == 1
        assert c.ingest_runs == 1

    def test_model_dump_keys(self):
        c = InspectionCounts(files=0, chunks=0, embeddings=0, summaries=0, ingest_runs=0)
        assert set(c.model_dump().keys()) == {"files", "chunks", "embeddings", "summaries", "ingest_runs"}


class TestDocumentRow:
    def test_required_field(self):
        d = DocumentRow(document_id=DOC_ID)
        assert d.document_id == DOC_ID

    def test_missing_document_id_raises(self):
        with pytest.raises(ValidationError):
            DocumentRow()  # type: ignore[call-arg]

    def test_optional_fields_default_none(self):
        d = DocumentRow(document_id=DOC_ID)
        for field in ("title", "author", "status", "language", "mime_type"):
            assert getattr(d, field) is None


class TestChunkRow:
    def test_text_defaults_none(self):
        c = ChunkRow()
        assert c.text is None

    def test_text_present_when_given(self):
        c = ChunkRow(text="hello")
        assert c.text == "hello"


class TestEmbeddingRow:
    def test_vector_defaults_none(self):
        e = EmbeddingRow()
        assert e.vector is None

    def test_chunk_index_present(self):
        e = EmbeddingRow(chunk_index=3)
        assert e.chunk_index == 3


class TestInspectionResponse:
    def test_empty_defaults(self):
        r = InspectionResponse()
        assert r.document is None
        assert r.files == []
        assert r.chunks == []
        assert r.embeddings == []
        assert r.summaries == []
        assert r.ingest_runs == []
        assert r.counts.files == 0

    def test_top_level_keys(self):
        r = InspectionResponse()
        keys = set(r.model_dump().keys())
        assert keys == {"document", "files", "chunks", "embeddings", "summaries", "ingest_runs", "counts"}

    def test_with_document(self):
        doc = DocumentRow(document_id=DOC_ID, title="Test", status="active")
        r = InspectionResponse(document=doc)
        assert r.document is not None
        assert r.document.document_id == DOC_ID

    def test_counts_included(self):
        r = InspectionResponse(
            counts=InspectionCounts(files=2, chunks=3, embeddings=3, summaries=1, ingest_runs=1),
        )
        assert r.counts.files == 2
        assert r.counts.chunks == 3


class TestRowProjections:
    def test_document_file_row(self):
        f = DocumentFileRow(id="uuid-1", role="primary", rel_path="docs/a.pdf")
        assert f.id == "uuid-1"
        assert f.role == "primary"
        assert f.sha256 is None

    def test_summary_row(self):
        s = SummaryRow(output_type="executive", content="exec summary")
        assert s.output_type == "executive"
        assert s.content == "exec summary"
        assert s.model_used is None

    def test_ingest_run_row(self):
        r = IngestRunRow(status="succeeded")
        assert r.status == "succeeded"
        assert r.error_message is None
