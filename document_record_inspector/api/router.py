"""document_record_inspector.api.router — FastAPI router.

Mount prefix (set in tool.toml): /tools/document-record-inspector

Endpoints
---------
GET  /health                  → {"status": "ok"}
GET  /records/{document_id}   → InspectionResponse

Error mapping
-------------
ValueError (empty document_id) → HTTP 400
All other ValueError           → HTTP 400

A document that does not exist in TechVault returns HTTP 200 with
``document: null`` and ``diagnostics.possible_issues`` containing
``"document_missing"``.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from ..api.schemas import InspectionResponse
from ..core.service import health_service, inspect_document
from .deps import get_db

# Resource-level prefix only.  The platform mounts this router under
# /tools/document-record-inspector, so final paths become:
#   /tools/document-record-inspector/health
#   /tools/document-record-inspector/records/{document_id}
router = APIRouter(tags=["tools:document_record_inspector"])


@router.get("/health")
def health() -> dict[str, str]:
    return health_service()


@router.get("/records/{document_id}", response_model=InspectionResponse)
def inspect(
    document_id: str,
    db=Depends(get_db),  # noqa: B008
) -> InspectionResponse:
    """Return the canonical inspection record for *document_id*.

    Always returns HTTP 200.  When the document does not exist the response
    has ``document: null`` and ``diagnostics.possible_issues`` contains
    ``"document_missing"``.
    """
    try:
        return inspect_document(document_id, db)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

