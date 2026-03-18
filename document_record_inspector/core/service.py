"""document_record_inspector.core.service -- canonical inspection logic.

Public API
----------
  health_service()                   -> dict[str, str]
  assemble_inspection_record(...)    -> InspectionResponse   (pure, no DB)
  inspect_document(document_id, db)  -> InspectionResponse   (DB-backed)

Design
------
``assemble_inspection_record`` is a pure deterministic function: given
pre-fetched row dicts it builds the typed response and computes diagnostics.
It receives no DB session and performs no I/O, which makes it trivially
testable with in-memory fixtures.

``inspect_document`` is the production entry-point.  It accepts a SQLAlchemy
Session (or None in standalone mode) and delegates to private fetch helpers
before handing results to ``assemble_inspection_record``.

When ``db`` is ``None`` (standalone / no-database mode) all collections are
empty and ``diagnostics.possible_issues`` will contain ``"document_missing"``.

Exception boundary
------------------
Only ``ValueError`` may escape this module.  Unexpected exceptions are
wrapped as ``ValueError("Unexpected error: <ClassName>: <msg>")``.

Ordering rules (all enforced in the SQL ORDER BY clauses)
---------------------------------------------------------
document_files : ASC id
chunks         : ASC chunk_index, ASC id
embeddings     : ASC chunk_id (== chunks.id), ASC id
summaries      : ASC id
ingest_runs    : DESC started_at, ASC id   (newest first, id as tie-breaker)
"""
from __future__ import annotations

from typing import Any

from ..api.schemas import (
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

# ---------------------------------------------------------------------------
# Issue sentinel strings (kept as module constants for test assertions)
# ---------------------------------------------------------------------------

ISSUE_DOCUMENT_MISSING = "document_missing"
ISSUE_NO_FILES = "document_has_no_files"
ISSUE_NO_CHUNKS = "document_has_no_chunks"
ISSUE_CHUNKS_NO_EMBEDDINGS = "chunks_present_but_embeddings_missing"
ISSUE_CHUNKS_NO_SUMMARIES = "chunks_present_but_summaries_missing"
ISSUE_EMBEDDING_MISMATCH = "embedding_count_mismatch_with_chunk_count"
ISSUE_MULTIPLE_INGEST_RUNS = "multiple_ingest_runs_present"


# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------


def health_service() -> dict[str, str]:
    return {"status": "ok"}


def assemble_inspection_record(
    *,
    document_id: str,
    document: dict[str, Any] | None,
    document_files: list[dict[str, Any]],
    chunks: list[dict[str, Any]],
    embeddings: list[dict[str, Any]],
    summaries: list[dict[str, Any]],
    ingest_runs: list[dict[str, Any]],
) -> InspectionResponse:
    """Build a deterministic InspectionResponse from pre-fetched row dicts.

    All input lists must already be in canonical sort order (enforced by the
    SQL ORDER BY in ``_fetch_*`` helpers or by callers in test scenarios).
    This function computes diagnostics and assembles the typed response; it
    does not re-sort, filter, or hit the database.
    """
    chunk_count = len(chunks)
    embedding_count = len(embeddings)
    summary_count = len(summaries)
    file_count = len(document_files)
    ingest_run_count = len(ingest_runs)

    document_found = document is not None
    possible_issues: list[str] = []

    if not document_found:
        possible_issues.append(ISSUE_DOCUMENT_MISSING)
    else:
        if file_count == 0:
            possible_issues.append(ISSUE_NO_FILES)
        if chunk_count == 0:
            possible_issues.append(ISSUE_NO_CHUNKS)
        else:
            if embedding_count == 0:
                possible_issues.append(ISSUE_CHUNKS_NO_EMBEDDINGS)
            elif embedding_count != chunk_count:
                possible_issues.append(ISSUE_EMBEDDING_MISMATCH)
            if summary_count == 0:
                possible_issues.append(ISSUE_CHUNKS_NO_SUMMARIES)
        if ingest_run_count > 1:
            possible_issues.append(ISSUE_MULTIPLE_INGEST_RUNS)

    possible_issues.sort()

    diagnostics = DiagnosticsModel(
        document_found=document_found,
        has_files=file_count > 0,
        has_chunks=chunk_count > 0,
        has_embeddings=embedding_count > 0,
        has_summaries=summary_count > 0,
        ingest_run_count=ingest_run_count,
        chunk_count=chunk_count,
        embedding_count=embedding_count,
        summary_count=summary_count,
        file_count=file_count,
        possible_issues=possible_issues,
    )

    doc_model = DocumentRow(**document) if document else None
    file_models = [DocumentFileRow(**f) for f in document_files]
    chunk_models = [ChunkRow(**c) for c in chunks]
    embedding_models = [EmbeddingRow(**e) for e in embeddings]
    summary_models = [SummaryRow(**s) for s in summaries]
    ingest_run_models = [IngestRunRow(**r) for r in ingest_runs]

    return InspectionResponse(
        query=QueryInfo(document_id=document_id),
        document=doc_model,
        document_files=file_models,
        chunks=chunk_models,
        embeddings=embedding_models,
        summaries=summary_models,
        ingest_runs=ingest_run_models,
        diagnostics=diagnostics,
    )


def inspect_document(document_id: str, db: Any) -> InspectionResponse:
    """Fetch all pipeline rows for *document_id* and return an InspectionResponse.

    When *db* is ``None`` (standalone / test mode) an empty but valid response
    is returned immediately without any DB access.

    Only ``ValueError`` may escape; unexpected errors are wrapped.
    """
    if not document_id or not document_id.strip():
        raise ValueError("document_id must not be empty")
    document_id = document_id.strip()

    try:
        return _inspect(document_id, db)
    except ValueError:
        raise
    except Exception as exc:  # noqa: BLE001
        raise ValueError(f"Unexpected error: {type(exc).__name__}: {exc}") from exc


# ---------------------------------------------------------------------------
# Internal implementation
# ---------------------------------------------------------------------------


def _inspect(document_id: str, db: Any) -> InspectionResponse:
    if db is None:
        return assemble_inspection_record(
            document_id=document_id,
            document=None,
            document_files=[],
            chunks=[],
            embeddings=[],
            summaries=[],
            ingest_runs=[],
        )

    document = _fetch_document(document_id, db)
    if document is None:
        return assemble_inspection_record(
            document_id=document_id,
            document=None,
            document_files=[],
            chunks=[],
            embeddings=[],
            summaries=[],
            ingest_runs=[],
        )

    document_files = _fetch_document_files(document_id, db)
    chunks = _fetch_chunks(document_id, db)
    embeddings = _fetch_embeddings(document_id, db)
    summaries = _fetch_summaries(document_id, db)
    ingest_runs = _fetch_ingest_runs(document_id, db)

    return assemble_inspection_record(
        document_id=document_id,
        document=document,
        document_files=document_files,
        chunks=chunks,
        embeddings=embeddings,
        summaries=summaries,
        ingest_runs=ingest_runs,
    )


# ---------------------------------------------------------------------------
# DB fetch helpers (raw SQL — no ORM import avoids heavy dependency in tests)
# ---------------------------------------------------------------------------


def _row_to_dict(row: Any) -> dict[str, Any]:
    """Convert a SQLAlchemy RowMapping to a plain dict."""
    return dict(row)


def _fetch_document(document_id: str, db: Any) -> dict[str, Any] | None:
    from sqlalchemy import text as sa_text  # noqa: PLC0415

    result = db.execute(
        sa_text(
            "SELECT"
            "  document_id,"
            "  library_id::text,"
            "  group_id::text,"
            "  security_level::text,"
            "  doc_type::text,"
            "  original_filename,"
            "  title,"
            "  author,"
            "  source_uri,"
            "  ingested_at::text,"
            "  ingest_version,"
            "  content_sha256,"
            "  size_bytes,"
            "  mime_type,"
            "  page_count,"
            "  language,"
            "  status"
            " FROM documents"
            " WHERE document_id = :doc_id"
        ),
        {"doc_id": document_id},
    ).mappings().first()
    return _row_to_dict(result) if result is not None else None


def _fetch_document_files(document_id: str, db: Any) -> list[dict[str, Any]]:
    from sqlalchemy import text as sa_text  # noqa: PLC0415

    rows = db.execute(
        sa_text(
            "SELECT"
            "  id::text,"
            "  document_id,"
            "  role,"
            "  rel_path,"
            "  file_ext,"
            "  sha256,"
            "  size_bytes,"
            "  created_at::text"
            " FROM document_files"
            " WHERE document_id = :doc_id"
            " ORDER BY id ASC"
        ),
        {"doc_id": document_id},
    ).mappings()
    return [_row_to_dict(r) for r in rows]


def _fetch_chunks(document_id: str, db: Any) -> list[dict[str, Any]]:
    from sqlalchemy import text as sa_text  # noqa: PLC0415

    rows = db.execute(
        sa_text(
            "SELECT"
            "  id::text,"
            "  document_id,"
            "  chunk_index,"
            "  chunk_id,"
            "  text,"
            "  token_count,"
            "  char_count,"
            "  page_start,"
            "  page_end,"
            "  section_path,"
            "  created_at::text"
            " FROM chunks"
            " WHERE document_id = :doc_id"
            " ORDER BY chunk_index ASC, id ASC"
        ),
        {"doc_id": document_id},
    ).mappings()
    return [_row_to_dict(r) for r in rows]


def _fetch_embeddings(document_id: str, db: Any) -> list[dict[str, Any]]:
    """Fetch embeddings for all chunks belonging to *document_id*.

    Embeddings are linked to chunks via ``chunk_id`` (FK to ``chunks.id``),
    not directly to documents.  A JOIN is required to scope by document.

    The vector column is intentionally excluded from the SELECT.
    """
    from sqlalchemy import text as sa_text  # noqa: PLC0415

    rows = db.execute(
        sa_text(
            "SELECT"
            "  e.id::text,"
            "  e.chunk_id::text,"
            "  e.embedding_model,"
            "  e.embedding_dim,"
            "  e.created_at::text"
            " FROM embeddings e"
            " JOIN chunks c ON c.id = e.chunk_id"
            " WHERE c.document_id = :doc_id"
            " ORDER BY e.chunk_id ASC, e.id ASC"
        ),
        {"doc_id": document_id},
    ).mappings()
    return [_row_to_dict(r) for r in rows]


def _fetch_summaries(document_id: str, db: Any) -> list[dict[str, Any]]:
    from sqlalchemy import text as sa_text  # noqa: PLC0415

    rows = db.execute(
        sa_text(
            "SELECT"
            "  id::text,"
            "  document_id,"
            "  summary_prompt_id::text,"
            "  output_type::text,"
            "  model_used,"
            "  provider,"
            "  security_level::text,"
            "  content,"
            "  content_sha256,"
            "  created_at::text"
            " FROM summaries"
            " WHERE document_id = :doc_id"
            " ORDER BY id ASC"
        ),
        {"doc_id": document_id},
    ).mappings()
    return [_row_to_dict(r) for r in rows]


def _fetch_ingest_runs(document_id: str, db: Any) -> list[dict[str, Any]]:
    """Fetch ingest_runs associated with this document, newest first.

    Only rows with an explicit ``document_id`` match are returned; runs that
    have not yet been linked to a document (``document_id IS NULL``) are
    excluded.
    """
    from sqlalchemy import text as sa_text  # noqa: PLC0415

    rows = db.execute(
        sa_text(
            "SELECT"
            "  id::text,"
            "  document_id,"
            "  library_id::text,"
            "  group_id::text,"
            "  security_level::text,"
            "  requested_by,"
            "  status,"
            "  error_message,"
            "  started_at::text,"
            "  ended_at::text,"
            "  metrics_json"
            " FROM ingest_runs"
            " WHERE document_id = :doc_id"
            " ORDER BY started_at DESC, id ASC"
        ),
        {"doc_id": document_id},
    ).mappings()
    return [_row_to_dict(r) for r in rows]

