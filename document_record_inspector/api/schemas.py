"""document_record_inspector.api.schemas — re-export facade.

All canonical document-inspection schema classes are now defined in the
TechVault backend (``backend.techvault.app.schemas.document_inspection``).
This module re-exports them so that all existing imports within this tool
package and any external callers continue to work unchanged.

The tool is a facade; the backend is the source of truth.
"""

from __future__ import annotations

from backend.techvault.app.schemas.document_inspection import (  # noqa: F401
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

__all__ = [
    "ChunkRow",
    "DiagnosticsModel",
    "DocumentFileRow",
    "DocumentRow",
    "EmbeddingRow",
    "IngestRunRow",
    "InspectionResponse",
    "QueryInfo",
    "SummaryRow",
]
