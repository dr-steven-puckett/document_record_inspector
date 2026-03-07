"""document_record_inspector.core.service — deterministic business logic.

All public functions follow the service exception boundary:
  - Only ValueError and PermissionError may escape.
  - Unexpected exceptions are wrapped as ValueError("Unexpected error: <ClassName>: <msg>").

Dual-mode design:
  - Standalone / test mode: caller passes a pre-loaded fixture dict (from catalog_loader).
  - Live DB mode: caller passes a SQLAlchemy Session; this module issues explicit
    ordered queries against the canonical TechVault schema.

The sorting, projection, and gating logic (include_text / include_vectors) is
identical in both modes.
"""
from __future__ import annotations

from typing import Any, Optional


# ---------------------------------------------------------------------------
# Sort helpers
# ---------------------------------------------------------------------------


def _str_key(val: Any) -> str:
    """Return a stable string sort key; None sorts as empty string (smallest)."""
    if val is None:
        return ""
    return str(val)


# ---------------------------------------------------------------------------
# Projection helpers — strip or preserve optional large fields
# ---------------------------------------------------------------------------


def _project_chunk(row: dict, include_text: bool) -> dict:
    """Project a chunks row, gating 'text' behind include_text."""
    out = dict(row)
    if not include_text:
        out["text"] = None
    return out


def _project_embedding(row: dict, include_vectors: bool) -> dict:
    """Project an embeddings row, gating 'vector' behind include_vectors."""
    out = dict(row)
    if not include_vectors:
        out["vector"] = None
    return out


# ---------------------------------------------------------------------------
# Sorting
# ---------------------------------------------------------------------------


def _sort_files(rows: list[dict]) -> list[dict]:
    """Sort document_files: role ASC, rel_path ASC, id ASC."""
    return sorted(
        rows,
        key=lambda r: (_str_key(r.get("role")), _str_key(r.get("rel_path")), _str_key(r.get("id"))),
    )


def _sort_chunks(rows: list[dict]) -> list[dict]:
    """Sort chunks: chunk_index ASC, id ASC."""
    return sorted(
        rows,
        key=lambda r: (int(r["chunk_index"]) if r.get("chunk_index") is not None else 0, _str_key(r.get("id"))),
    )


def _sort_embeddings(rows: list[dict]) -> list[dict]:
    """Sort embeddings: chunk_index ASC, embedding_model ASC, id ASC.

    Rows must carry 'chunk_index' from the join to chunks.
    """
    return sorted(
        rows,
        key=lambda r: (
            int(r["chunk_index"]) if r.get("chunk_index") is not None else 0,
            _str_key(r.get("embedding_model")),
            _str_key(r.get("id")),
        ),
    )


def _sort_summaries(rows: list[dict]) -> list[dict]:
    """Sort summaries: output_type ASC, created_at ASC, id ASC."""
    return sorted(
        rows,
        key=lambda r: (
            _str_key(r.get("output_type")),
            _str_key(r.get("created_at")),
            _str_key(r.get("id")),
        ),
    )


def _sort_ingest_runs(rows: list[dict]) -> list[dict]:
    """Sort ingest_runs: started_at ASC, id ASC."""
    return sorted(
        rows,
        key=lambda r: (_str_key(r.get("started_at")), _str_key(r.get("id"))),
    )


# ---------------------------------------------------------------------------
# Core inspect logic (shared by both modes)
# ---------------------------------------------------------------------------


def _build_result(
    document: Optional[dict],
    files: list[dict],
    chunks: list[dict],
    embeddings: list[dict],
    summaries: list[dict],
    ingest_runs: list[dict],
    include_text: bool,
    include_vectors: bool,
) -> dict:
    """Sort, project, and assemble the final inspection payload."""
    sorted_files = _sort_files(files)
    sorted_chunks = _sort_chunks(chunks)
    sorted_embeddings = _sort_embeddings(embeddings)
    sorted_summaries = _sort_summaries(summaries)
    sorted_runs = _sort_ingest_runs(ingest_runs)

    projected_chunks = [_project_chunk(c, include_text) for c in sorted_chunks]
    projected_embeddings = [_project_embedding(e, include_vectors) for e in sorted_embeddings]

    return {
        "document": document,
        "files": sorted_files,
        "chunks": projected_chunks,
        "embeddings": projected_embeddings,
        "summaries": sorted_summaries,
        "ingest_runs": sorted_runs,
        "counts": {
            "files": len(sorted_files),
            "chunks": len(sorted_chunks),
            "embeddings": len(sorted_embeddings),
            "summaries": len(sorted_summaries),
            "ingest_runs": len(sorted_runs),
        },
    }


# ---------------------------------------------------------------------------
# Standalone mode (fixture dict from catalog_loader)
# ---------------------------------------------------------------------------


def inspect_from_fixture(
    fixture: dict,
    document_id: str,
    *,
    include_text: bool = False,
    include_vectors: bool = False,
) -> dict:
    """Inspect from a pre-loaded fixture dict (standalone / test mode).

    Parameters
    ----------
    fixture:
        Dict returned by catalog_loader.load_fixture().
    document_id:
        The document_id to look up. If the fixture's document does not match,
        raises ValueError("document not found: <id>").
    include_text:
        Whether to include chunk text in output.
    include_vectors:
        Whether to include embedding vectors in output.

    Raises
    ------
    ValueError
        If document_id is empty, or not found in fixture.
    """
    try:
        if not document_id or not document_id.strip():
            raise ValueError("document_id must be a non-empty string")

        doc = fixture.get("document")
        if doc is None or doc.get("document_id") != document_id:
            raise ValueError(f"document not found: {document_id!r}")

        return _build_result(
            document=doc,
            files=list(fixture.get("files", [])),
            chunks=list(fixture.get("chunks", [])),
            embeddings=list(fixture.get("embeddings", [])),
            summaries=list(fixture.get("summaries", [])),
            ingest_runs=list(fixture.get("ingest_runs", [])),
            include_text=include_text,
            include_vectors=include_vectors,
        )
    except (ValueError, PermissionError):
        raise
    except Exception as exc:
        raise ValueError(f"Unexpected error: {type(exc).__name__}: {exc}") from exc


# ---------------------------------------------------------------------------
# Live DB mode (SQLAlchemy Session)
# ---------------------------------------------------------------------------


def inspect_from_db(
    db: Any,
    document_id: str,
    *,
    include_text: bool = False,
    include_vectors: bool = False,
) -> dict:
    """Inspect a document from a live SQLAlchemy Session.

    Issues explicit ORDER BY queries against the canonical TechVault tables.
    No ORM models required — uses raw SQL via db.execute() for portability.

    Parameters
    ----------
    db:
        SQLAlchemy Session (or compatible execute()-capable object).
    document_id:
        The SHA-256 document_id to inspect.
    include_text:
        Whether to include chunk text.
    include_vectors:
        Whether to include embedding vectors.

    Raises
    ------
    ValueError
        If document_id is empty or not found in the documents table.
    """
    try:
        from sqlalchemy import text  # noqa: PLC0415

        if not document_id or not document_id.strip():
            raise ValueError("document_id must be a non-empty string")

        # ── documents ───────────────────────────────────────────────────────
        doc_row = db.execute(
            text(
                "SELECT document_id, library_id::text, group_id::text, "
                "security_level, doc_type, original_filename, title, author, "
                "source_uri, ingested_at::text, ingest_version, content_sha256, "
                "size_bytes, mime_type, page_count, language, status "
                "FROM documents WHERE document_id = :document_id"
            ),
            {"document_id": document_id},
        ).mappings().first()

        if doc_row is None:
            raise ValueError(f"document not found: {document_id!r}")

        document = dict(doc_row)

        # ── document_files ───────────────────────────────────────────────────
        files_rows = db.execute(
            text(
                "SELECT id::text, document_id, role, rel_path, file_ext, "
                "sha256, size_bytes, created_at::text "
                "FROM document_files "
                "WHERE document_id = :document_id "
                "ORDER BY role ASC, rel_path ASC, id ASC"
            ),
            {"document_id": document_id},
        ).mappings().all()
        files = [dict(r) for r in files_rows]

        # ── chunks ────────────────────────────────────────────────────────────
        chunks_rows = db.execute(
            text(
                "SELECT id::text, document_id, chunk_index, chunk_id, "
                + ("text, " if include_text else "NULL AS text, ")
                + "token_count, char_count, page_start, page_end, "
                "section_path, created_at::text "
                "FROM chunks "
                "WHERE document_id = :document_id "
                "ORDER BY chunk_index ASC, id ASC"
            ),
            {"document_id": document_id},
        ).mappings().all()
        chunks = [dict(r) for r in chunks_rows]

        # ── embeddings ───────────────────────────────────────────────────────
        vector_select = "e.vector::text" if include_vectors else "NULL AS vector"
        embeddings_rows = db.execute(
            text(
                f"SELECT e.id::text, e.chunk_id::text, e.embedding_model, "
                f"e.embedding_dim, {vector_select}, e.created_at::text, "
                f"c.chunk_index "
                f"FROM embeddings e "
                f"JOIN chunks c ON c.id = e.chunk_id "
                f"WHERE c.document_id = :document_id "
                f"ORDER BY c.chunk_index ASC, e.embedding_model ASC, e.id ASC"
            ),
            {"document_id": document_id},
        ).mappings().all()
        embeddings = [dict(r) for r in embeddings_rows]

        # ── summaries ────────────────────────────────────────────────────────
        summaries_rows = db.execute(
            text(
                "SELECT id::text, document_id, summary_prompt_id::text, "
                "output_type, model_used, provider, security_level, "
                "content, content_sha256, created_at::text "
                "FROM summaries "
                "WHERE document_id = :document_id "
                "ORDER BY output_type ASC, created_at ASC, id ASC"
            ),
            {"document_id": document_id},
        ).mappings().all()
        summaries = [dict(r) for r in summaries_rows]

        # ── ingest_runs ──────────────────────────────────────────────────────
        runs_rows = db.execute(
            text(
                "SELECT id::text, document_id, library_id::text, group_id::text, "
                "security_level, requested_by, status, error_message, "
                "started_at::text, ended_at::text, metrics_json::text "
                "FROM ingest_runs "
                "WHERE document_id = :document_id "
                "ORDER BY started_at ASC, id ASC"
            ),
            {"document_id": document_id},
        ).mappings().all()
        ingest_runs = [dict(r) for r in runs_rows]

        # ── assemble ─────────────────────────────────────────────────────────
        # DB queries already return correct order; _build_result re-sorts in
        # memory as the canonical determinism guarantee (no reliance on DB order).
        return _build_result(
            document=document,
            files=files,
            chunks=chunks,
            embeddings=embeddings,
            summaries=summaries,
            ingest_runs=ingest_runs,
            include_text=include_text,
            include_vectors=include_vectors,
        )

    except (ValueError, PermissionError):
        raise
    except Exception as exc:
        raise ValueError(f"Unexpected error: {type(exc).__name__}: {exc}") from exc


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------


def health() -> dict:
    """Return a deterministic health response."""
    return {"status": "ok", "tool_id": "document_record_inspector"}
