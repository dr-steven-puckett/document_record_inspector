"""Service layer tests for document_record_inspector.

All tests exercise ``assemble_inspection_record`` (pure, no DB) and
``inspect_document(id, None)`` (standalone mode, no DB).
"""
from __future__ import annotations

import pytest

from document_record_inspector.core.service import (
    ISSUE_CHUNKS_NO_EMBEDDINGS,
    ISSUE_CHUNKS_NO_SUMMARIES,
    ISSUE_DOCUMENT_MISSING,
    ISSUE_EMBEDDING_MISMATCH,
    ISSUE_MULTIPLE_INGEST_RUNS,
    ISSUE_NO_CHUNKS,
    ISSUE_NO_FILES,
    assemble_inspection_record,
    health_service,
    inspect_document,
)
from tests.conftest import (
    CHUNK_1,
    CHUNK_2,
    DOC_ID,
    DOCUMENT_DICT,
    EMBEDDING_1,
    EMBEDDING_2,
    FILE_1,
    INGEST_RUN_1,
    INGEST_RUN_2,
    SUMMARY_1,
)

# ---------------------------------------------------------------------------
# health_service
# ---------------------------------------------------------------------------


def test_health_returns_ok() -> None:
    assert health_service() == {"status": "ok"}


# ---------------------------------------------------------------------------
# Scenario 1: fully populated document
# ---------------------------------------------------------------------------


def test_fully_populated_document(full_data) -> None:
    result = assemble_inspection_record(**full_data)
    assert result.document is not None
    assert result.document.document_id == DOC_ID
    assert result.diagnostics.document_found is True
    assert result.diagnostics.chunk_count == 2
    assert result.diagnostics.embedding_count == 2
    assert result.diagnostics.summary_count == 1
    assert result.diagnostics.file_count == 2
    assert result.diagnostics.ingest_run_count == 2
    assert result.diagnostics.possible_issues == sorted(
        [ISSUE_MULTIPLE_INGEST_RUNS]
    )


def test_fully_populated_query_echo(full_data) -> None:
    result = assemble_inspection_record(**full_data)
    assert result.query.document_id == DOC_ID


# ---------------------------------------------------------------------------
# Scenario 2: document exists but no files
# ---------------------------------------------------------------------------


def test_no_files_issue() -> None:
    result = assemble_inspection_record(
        document_id=DOC_ID,
        document=dict(DOCUMENT_DICT),
        document_files=[],
        chunks=[dict(CHUNK_1)],
        embeddings=[dict(EMBEDDING_1)],
        summaries=[dict(SUMMARY_1)],
        ingest_runs=[dict(INGEST_RUN_1)],
    )
    assert ISSUE_NO_FILES in result.diagnostics.possible_issues
    assert result.diagnostics.has_files is False
    assert result.diagnostics.file_count == 0


# ---------------------------------------------------------------------------
# Scenario 3: document exists, no chunks
# ---------------------------------------------------------------------------


def test_no_chunks_issue() -> None:
    result = assemble_inspection_record(
        document_id=DOC_ID,
        document=dict(DOCUMENT_DICT),
        document_files=[dict(FILE_1)],
        chunks=[],
        embeddings=[],
        summaries=[],
        ingest_runs=[dict(INGEST_RUN_1)],
    )
    assert ISSUE_NO_CHUNKS in result.diagnostics.possible_issues
    assert result.diagnostics.has_chunks is False
    assert result.diagnostics.chunk_count == 0
    # No embedding/summary issues when there are no chunks to embed/summarise
    assert ISSUE_CHUNKS_NO_EMBEDDINGS not in result.diagnostics.possible_issues
    assert ISSUE_CHUNKS_NO_SUMMARIES not in result.diagnostics.possible_issues


# ---------------------------------------------------------------------------
# Scenario 4: chunks present, embeddings missing
# ---------------------------------------------------------------------------


def test_chunks_but_no_embeddings() -> None:
    result = assemble_inspection_record(
        document_id=DOC_ID,
        document=dict(DOCUMENT_DICT),
        document_files=[dict(FILE_1)],
        chunks=[dict(CHUNK_1), dict(CHUNK_2)],
        embeddings=[],
        summaries=[dict(SUMMARY_1)],
        ingest_runs=[dict(INGEST_RUN_1)],
    )
    assert ISSUE_CHUNKS_NO_EMBEDDINGS in result.diagnostics.possible_issues
    assert result.diagnostics.has_embeddings is False
    assert result.diagnostics.embedding_count == 0
    # MISMATCH should not appear when embeddings are entirely absent
    assert ISSUE_EMBEDDING_MISMATCH not in result.diagnostics.possible_issues


# ---------------------------------------------------------------------------
# Scenario 5: chunks present, summaries missing
# ---------------------------------------------------------------------------


def test_chunks_but_no_summaries() -> None:
    result = assemble_inspection_record(
        document_id=DOC_ID,
        document=dict(DOCUMENT_DICT),
        document_files=[dict(FILE_1)],
        chunks=[dict(CHUNK_1), dict(CHUNK_2)],
        embeddings=[dict(EMBEDDING_1), dict(EMBEDDING_2)],
        summaries=[],
        ingest_runs=[dict(INGEST_RUN_1)],
    )
    assert ISSUE_CHUNKS_NO_SUMMARIES in result.diagnostics.possible_issues
    assert result.diagnostics.has_summaries is False
    assert result.diagnostics.summary_count == 0


# ---------------------------------------------------------------------------
# Scenario 6: multiple ingest runs
# ---------------------------------------------------------------------------


def test_multiple_ingest_runs() -> None:
    result = assemble_inspection_record(
        document_id=DOC_ID,
        document=dict(DOCUMENT_DICT),
        document_files=[dict(FILE_1)],
        chunks=[dict(CHUNK_1)],
        embeddings=[dict(EMBEDDING_1)],
        summaries=[dict(SUMMARY_1)],
        ingest_runs=[dict(INGEST_RUN_1), dict(INGEST_RUN_2)],
    )
    assert ISSUE_MULTIPLE_INGEST_RUNS in result.diagnostics.possible_issues
    assert result.diagnostics.ingest_run_count == 2


# ---------------------------------------------------------------------------
# Scenario 7: nonexistent document
# ---------------------------------------------------------------------------


def test_nonexistent_document() -> None:
    result = assemble_inspection_record(
        document_id="does-not-exist",
        document=None,
        document_files=[],
        chunks=[],
        embeddings=[],
        summaries=[],
        ingest_runs=[],
    )
    assert result.document is None
    assert result.diagnostics.document_found is False
    assert result.diagnostics.possible_issues == [ISSUE_DOCUMENT_MISSING]
    assert result.diagnostics.chunk_count == 0
    assert result.diagnostics.embedding_count == 0


# ---------------------------------------------------------------------------
# Embedding count mismatch
# ---------------------------------------------------------------------------


def test_embedding_mismatch_issue() -> None:
    # 2 chunks, only 1 embedding
    result = assemble_inspection_record(
        document_id=DOC_ID,
        document=dict(DOCUMENT_DICT),
        document_files=[dict(FILE_1)],
        chunks=[dict(CHUNK_1), dict(CHUNK_2)],
        embeddings=[dict(EMBEDDING_1)],  # only 1 of 2
        summaries=[dict(SUMMARY_1)],
        ingest_runs=[dict(INGEST_RUN_1)],
    )
    assert ISSUE_EMBEDDING_MISMATCH in result.diagnostics.possible_issues
    assert ISSUE_CHUNKS_NO_EMBEDDINGS not in result.diagnostics.possible_issues
    assert result.diagnostics.chunk_count == 2
    assert result.diagnostics.embedding_count == 1


# ---------------------------------------------------------------------------
# Diagnostic count invariants
# ---------------------------------------------------------------------------


def test_diagnostics_counts_match_collection_lengths(full_data) -> None:
    result = assemble_inspection_record(**full_data)
    assert result.diagnostics.chunk_count == len(result.chunks)
    assert result.diagnostics.embedding_count == len(result.embeddings)
    assert result.diagnostics.summary_count == len(result.summaries)
    assert result.diagnostics.file_count == len(result.document_files)
    assert result.diagnostics.ingest_run_count == len(result.ingest_runs)


# ---------------------------------------------------------------------------
# possible_issues is always sorted
# ---------------------------------------------------------------------------


def test_possible_issues_sorted() -> None:
    # Document exists, no files, no chunks -> two issues that must be sorted
    result = assemble_inspection_record(
        document_id=DOC_ID,
        document=dict(DOCUMENT_DICT),
        document_files=[],
        chunks=[],
        embeddings=[],
        summaries=[],
        ingest_runs=[],
    )
    issues = result.diagnostics.possible_issues
    assert issues == sorted(issues)


# ---------------------------------------------------------------------------
# inspect_document standalone mode (db=None)
# ---------------------------------------------------------------------------


def test_inspect_document_standalone_returns_empty() -> None:
    result = inspect_document(DOC_ID, None)
    assert result.document is None
    assert result.document_files == []
    assert result.chunks == []
    assert result.embeddings == []
    assert result.summaries == []
    assert result.ingest_runs == []
    assert ISSUE_DOCUMENT_MISSING in result.diagnostics.possible_issues


def test_inspect_document_empty_id_raises() -> None:
    with pytest.raises(ValueError, match="document_id must not be empty"):
        inspect_document("", None)


def test_inspect_document_whitespace_id_raises() -> None:
    with pytest.raises(ValueError, match="document_id must not be empty"):
        inspect_document("   ", None)


# ---------------------------------------------------------------------------
# DocumentRow field validation
# ---------------------------------------------------------------------------


def test_document_row_fields(full_data) -> None:
    result = assemble_inspection_record(**full_data)
    doc = result.document
    assert doc is not None
    assert doc.document_id == DOC_ID
    assert doc.doc_type == "pdf"
    assert doc.status == "active"
    assert doc.page_count == 20
    assert doc.size_bytes == 204800


def test_ingest_run_metrics_json_is_dict(full_data) -> None:
    result = assemble_inspection_record(**full_data)
    for run in result.ingest_runs:
        assert isinstance(run.metrics_json, dict)

