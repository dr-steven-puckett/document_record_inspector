"""Deterministic ordering invariant tests for document_record_inspector.

The service contract guarantees:
  document_files : ASC id
  chunks         : ASC chunk_index, ASC id
  embeddings     : ASC chunk_id (== chunks.id), ASC id
  summaries      : ASC id
  ingest_runs    : DESC started_at, ASC id  (newest first)

These tests verify the contract by supplying data in NON-canonical order and
checking that assemble_inspection_record preserves the order at which the
service layer must deliver data (i.e. tests verify the schema contract, not
sorting inside assemble_inspection_record which trusts its inputs).
"""
from __future__ import annotations

from document_record_inspector.core.service import assemble_inspection_record
from tests.conftest import (
    CHUNK_1,
    CHUNK_2,
    DOC_ID,
    DOCUMENT_DICT,
    EMBEDDING_1,
    EMBEDDING_2,
    FILE_1,
    FILE_2,
    INGEST_RUN_1,
    INGEST_RUN_2,
    SUMMARY_1,
)

# ---------------------------------------------------------------------------
# document_files ordering
# ---------------------------------------------------------------------------


def test_document_files_order_preserved() -> None:
    """assemble_inspection_record preserves input list order for document_files.

    The service layer (SQL ORDER BY id ASC) is responsible for sorting;
    assemble_inspection_record trusts its inputs.  We verify output order
    matches input order.
    """
    # FILE_1.id < FILE_2.id (aaaabbbb... < ccccdddd...)
    result = assemble_inspection_record(
        document_id=DOC_ID,
        document=dict(DOCUMENT_DICT),
        document_files=[dict(FILE_1), dict(FILE_2)],
        chunks=[],
        embeddings=[],
        summaries=[],
        ingest_runs=[],
    )
    assert result.document_files[0].id == FILE_1["id"]
    assert result.document_files[1].id == FILE_2["id"]


def test_document_files_reversed_input_preserved() -> None:
    """If the caller reverses the input, output is reversed (service, not assembler, sorts)."""
    result = assemble_inspection_record(
        document_id=DOC_ID,
        document=dict(DOCUMENT_DICT),
        document_files=[dict(FILE_2), dict(FILE_1)],
        chunks=[],
        embeddings=[],
        summaries=[],
        ingest_runs=[],
    )
    assert result.document_files[0].id == FILE_2["id"]
    assert result.document_files[1].id == FILE_1["id"]


# ---------------------------------------------------------------------------
# chunks ordering
# ---------------------------------------------------------------------------


def test_chunks_order_preserved() -> None:
    """Chunks are output in the same order as the input list (chunk_index ASC)."""
    result = assemble_inspection_record(
        document_id=DOC_ID,
        document=dict(DOCUMENT_DICT),
        document_files=[dict(FILE_1)],
        chunks=[dict(CHUNK_1), dict(CHUNK_2)],
        embeddings=[],
        summaries=[],
        ingest_runs=[],
    )
    assert result.chunks[0].chunk_index == 0
    assert result.chunks[1].chunk_index == 1


# ---------------------------------------------------------------------------
# embeddings ordering
# ---------------------------------------------------------------------------


def test_embeddings_order_preserved() -> None:
    """Embeddings are output in input order (ascending chunk_id then id)."""
    result = assemble_inspection_record(
        document_id=DOC_ID,
        document=dict(DOCUMENT_DICT),
        document_files=[dict(FILE_1)],
        chunks=[dict(CHUNK_1), dict(CHUNK_2)],
        embeddings=[dict(EMBEDDING_1), dict(EMBEDDING_2)],
        summaries=[],
        ingest_runs=[],
    )
    # EMBEDDING_1.chunk_id == CHUNK_1.id (cccccccc-0001-...)
    # EMBEDDING_2.chunk_id == CHUNK_2.id (cccccccc-0002-...)
    assert result.embeddings[0].chunk_id == CHUNK_1["id"]
    assert result.embeddings[1].chunk_id == CHUNK_2["id"]


# ---------------------------------------------------------------------------
# ingest_runs ordering (newest first)
# ---------------------------------------------------------------------------


def test_ingest_runs_order_preserved() -> None:
    """Ingest runs are output newest-first (DESC started_at) matching input order."""
    # INGEST_RUN_1 started_at 2026 > INGEST_RUN_2 started_at 2025
    result = assemble_inspection_record(
        document_id=DOC_ID,
        document=dict(DOCUMENT_DICT),
        document_files=[dict(FILE_1)],
        chunks=[dict(CHUNK_1)],
        embeddings=[dict(EMBEDDING_1)],
        summaries=[dict(SUMMARY_1)],
        ingest_runs=[dict(INGEST_RUN_1), dict(INGEST_RUN_2)],
    )
    # Newest run should be first
    assert result.ingest_runs[0].started_at > result.ingest_runs[1].started_at
    assert result.ingest_runs[0].id == INGEST_RUN_1["id"]
    assert result.ingest_runs[1].id == INGEST_RUN_2["id"]


# ---------------------------------------------------------------------------
# possible_issues is always sorted
# ---------------------------------------------------------------------------


def test_possible_issues_always_sorted() -> None:
    """Regardless of which issues are triggered, possible_issues must be sorted."""
    result = assemble_inspection_record(
        document_id=DOC_ID,
        document=dict(DOCUMENT_DICT),
        document_files=[],          # ISSUE_NO_FILES
        chunks=[dict(CHUNK_1)],
        embeddings=[],              # ISSUE_CHUNKS_NO_EMBEDDINGS
        summaries=[],              # ISSUE_CHUNKS_NO_SUMMARIES
        ingest_runs=[dict(INGEST_RUN_1), dict(INGEST_RUN_2)],  # ISSUE_MULTIPLE_INGEST_RUNS
    )
    issues = result.diagnostics.possible_issues
    assert issues == sorted(issues), f"Issues not sorted: {issues}"
    assert len(issues) >= 3

