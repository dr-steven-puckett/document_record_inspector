"""document_record_inspector.core.service — thin facade over backend service.

The canonical document-inspection logic now lives in the TechVault backend:
  ``backend.techvault.app.services.document_inspection``

This module is a thin adapter / facade.  It:
  1. Re-exports all issue sentinel constants from the backend so that existing
     tool tests and callers can import them from their usual location.
  2. Re-exports ``assemble_inspection_record`` from the backend (same object),
     preserving its importability for tool-level unit tests.
  3. Keeps ``health_service()`` locally — it is not domain inspection logic.
  4. Exposes ``inspect_document(document_id, db)`` which behaves exactly as
     before:
       * ``db is None``  → standalone / no-database mode; returns a valid
         InspectionResponse with ``diagnostics.possible_issues`` containing
         ``"document_missing"`` and all collections empty.
       * ``db`` is a Session → delegates to the backend's
         ``inspect_document_record(db, document_id)``.

No fetch helpers (_fetch_document, _fetch_chunks, etc.) are defined here.
All DB access lives in the backend service.
"""

from __future__ import annotations

from backend.techvault.app.services.document_inspection import (  # noqa: F401
    ISSUE_CHUNKS_NO_EMBEDDINGS,  # noqa: F401
    ISSUE_CHUNKS_NO_SUMMARIES,  # noqa: F401
    ISSUE_DOCUMENT_MISSING,  # noqa: F401
    ISSUE_EMBEDDING_MISMATCH,  # noqa: F401
    ISSUE_MULTIPLE_INGEST_RUNS,  # noqa: F401
    ISSUE_NO_CHUNKS,  # noqa: F401
    ISSUE_NO_FILES,  # noqa: F401
    assemble_inspection_record,  # noqa: F401
)
from backend.techvault.app.services.document_inspection import (
    inspect_document_record as _backend_inspect,
)

__all__ = [
    "health_service",
    "assemble_inspection_record",
    "inspect_document",
    "ISSUE_DOCUMENT_MISSING",
    "ISSUE_NO_FILES",
    "ISSUE_NO_CHUNKS",
    "ISSUE_CHUNKS_NO_EMBEDDINGS",
    "ISSUE_CHUNKS_NO_SUMMARIES",
    "ISSUE_EMBEDDING_MISMATCH",
    "ISSUE_MULTIPLE_INGEST_RUNS",
]


def health_service() -> dict[str, str]:
    """Return a static health-check dict for the inspection service."""
    return {"status": "ok"}


def inspect_document(document_id: str, db: object = None) -> object:
    """Return an InspectionResponse for *document_id*.

    Parameters
    ----------
    document_id:
        The SHA-256 hex string primary key from the ``documents`` table.
    db:
        A SQLAlchemy ``Session``, or ``None`` for standalone / no-database
        mode (e.g. CLI dry-run).

    When ``db`` is ``None`` the returned response is valid: the document is
    reported as missing and all collection fields are empty arrays.

    Raises
    ------
    ValueError
        If ``document_id`` is blank.
    """
    if not document_id or not document_id.strip():
        raise ValueError("document_id must not be empty")
    document_id = document_id.strip()

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

    return _backend_inspect(db, document_id)
