"""document_record_inspector.api.router — FastAPI router.

Prefix  : /v1/tools/document_record_inspector
Tags    : ["tools:document_record_inspector"]

Endpoints
---------
GET  /health                           → HealthResponse
GET  /documents/{document_id}          → InspectionResponse

Query parameters for /documents/{document_id}:
  include_text=false    — include chunk text in response
  include_vectors=false — include embedding vectors in response

Error mapping:
  PermissionError           → HTTP 403
  ValueError("not found")  → HTTP 404
  ValueError (other)       → HTTP 400
"""
from __future__ import annotations

from typing import NoReturn

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from document_record_inspector.api.deps import get_db
from document_record_inspector.api.schemas import HealthResponse, InspectionResponse
from document_record_inspector.core import service

router = APIRouter(
    prefix="/v1/tools/document_record_inspector",
    tags=["tools:document_record_inspector"],
)


# ---------------------------------------------------------------------------
# Exception translation
# ---------------------------------------------------------------------------


def _handle_service_error(exc: Exception) -> NoReturn:
    """Convert service-layer exceptions to FastAPI HTTPException."""
    if isinstance(exc, PermissionError):
        raise HTTPException(status_code=403, detail=str(exc))
    if isinstance(exc, ValueError):
        if "not found" in str(exc).lower():
            raise HTTPException(status_code=404, detail=str(exc))
        raise HTTPException(status_code=400, detail=str(exc))
    raise exc


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.get(
    "/health",
    response_model=HealthResponse,
    operation_id="document_record_inspector_health",
)
def document_record_inspector_health() -> HealthResponse:
    """Return tool health status."""
    return HealthResponse(**service.health())


@router.get(
    "/documents/{document_id}",
    response_model=InspectionResponse,
    operation_id="document_record_inspector_inspect",
    responses={
        404: {"description": "Document not found"},
        422: {"description": "Validation error"},
    },
)
def document_record_inspector_inspect(
    document_id: str,
    include_text: bool = Query(default=False, description="Include chunk text in response"),
    include_vectors: bool = Query(default=False, description="Include embedding vectors in response"),
    db: Session = Depends(get_db),
) -> InspectionResponse:
    """Return the full record view for one document.

    Aggregates: documents row, document_files, chunks, embeddings, summaries,
    and ingest_runs for the given document_id.
    """
    try:
        result = service.inspect_from_db(
            db,
            document_id,
            include_text=include_text,
            include_vectors=include_vectors,
        )
        return InspectionResponse(**result)
    except (ValueError, PermissionError) as exc:
        _handle_service_error(exc)
