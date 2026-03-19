"""Facade contract tests for document_record_inspector.

These tests prove that the tool is a correct, transparent facade over the
TechVault backend's canonical document-inspection implementation.  No database
is required; all tests run against in-process imports only.

Assertions
----------
1. Schema classes exported by the tool are **the same objects** as those
   defined in the backend schemas module (identity check, not just
   structural equality).
2. Issue sentinel constants are re-exported from the tool service module and
   match the backend service's definitions.
3. ``assemble_inspection_record`` in the tool service *is* the backend
   function (same object identity).
4. ``inspect_document(id, None)`` (standalone / CLI mode) works without a
   database and returns a valid InspectionResponse.
5. ``health_service()`` still returns ``{"status": "ok"}``.
6. The tool's service module does NOT define any ``_fetch_*`` helpers
   locally — all DB access lives in the backend.
"""

from __future__ import annotations

import types

import backend.techvault.app.schemas.document_inspection as backend_schemas
import backend.techvault.app.services.document_inspection as backend_svc
import pytest

import document_record_inspector.api.schemas as tool_schemas
import document_record_inspector.core.service as tool_svc
from document_record_inspector.core.service import (
    assemble_inspection_record,
    inspect_document,
)

# ---------------------------------------------------------------------------
# Schema identity
# ---------------------------------------------------------------------------


def test_tool_schemas_are_backend_classes() -> None:
    """Every schema class re-exported by the tool is the identical backend class."""
    for name in [
        "ChunkRow",
        "DiagnosticsModel",
        "DocumentFileRow",
        "DocumentRow",
        "EmbeddingRow",
        "IngestRunRow",
        "InspectionResponse",
        "QueryInfo",
        "SummaryRow",
    ]:
        backend_cls = getattr(backend_schemas, name)
        tool_cls = getattr(tool_schemas, name)
        assert tool_cls is backend_cls, (
            f"tool_schemas.{name} is a different object from "
            f"backend_schemas.{name}; expected identical class objects."
        )


# ---------------------------------------------------------------------------
# Issue constant re-exports
# ---------------------------------------------------------------------------


def test_tool_issue_constants_importable() -> None:
    """All issue sentinel constants are importable from the tool service module."""
    expected = {
        "ISSUE_DOCUMENT_MISSING": "document_missing",
        "ISSUE_NO_FILES": "document_has_no_files",
        "ISSUE_NO_CHUNKS": "document_has_no_chunks",
        "ISSUE_CHUNKS_NO_EMBEDDINGS": "chunks_present_but_embeddings_missing",
        "ISSUE_CHUNKS_NO_SUMMARIES": "chunks_present_but_summaries_missing",
        "ISSUE_EMBEDDING_MISMATCH": "embedding_count_mismatch_with_chunk_count",
        "ISSUE_MULTIPLE_INGEST_RUNS": "multiple_ingest_runs_present",
    }
    for attr, value in expected.items():
        assert hasattr(tool_svc, attr), f"tool service missing constant: {attr}"
        assert getattr(tool_svc, attr) == value, (
            f"tool service constant {attr!r} has wrong value "
            f"{getattr(tool_svc, attr)!r}; expected {value!r}"
        )


def test_tool_issue_constants_match_backend() -> None:
    """Tool service constants are identical to the backend service constants."""
    constants = [
        "ISSUE_DOCUMENT_MISSING",
        "ISSUE_NO_FILES",
        "ISSUE_NO_CHUNKS",
        "ISSUE_CHUNKS_NO_EMBEDDINGS",
        "ISSUE_CHUNKS_NO_SUMMARIES",
        "ISSUE_EMBEDDING_MISMATCH",
        "ISSUE_MULTIPLE_INGEST_RUNS",
    ]
    for name in constants:
        assert getattr(tool_svc, name) == getattr(backend_svc, name), (
            f"Constant {name} differs between tool and backend service."
        )


# ---------------------------------------------------------------------------
# assemble_inspection_record identity
# ---------------------------------------------------------------------------


def test_tool_assemble_is_backend_function() -> None:
    """tool service's assemble_inspection_record is the exact backend function."""
    assert assemble_inspection_record is backend_svc.assemble_inspection_record, (
        "tool service's assemble_inspection_record must be the same function "
        "object as the backend's. The tool must not redefine it locally."
    )


# ---------------------------------------------------------------------------
# inspect_document standalone mode (db=None)
# ---------------------------------------------------------------------------


def test_tool_inspect_document_standalone_mode() -> None:
    """inspect_document(id, None) works without a DB and returns a valid response."""
    result = inspect_document("deadbeef" * 8, None)  # 64-char hex-like string
    assert isinstance(result, backend_schemas.InspectionResponse)
    assert result.document is None
    assert result.document_files == []
    assert result.chunks == []
    assert result.embeddings == []
    assert result.summaries == []
    assert result.ingest_runs == []
    assert result.diagnostics.document_found is False
    assert "document_missing" in result.diagnostics.possible_issues


def test_tool_inspect_document_blank_id_raises() -> None:
    """inspect_document('', None) raises ValueError for blank document_id."""
    with pytest.raises(ValueError, match="document_id must not be empty"):
        inspect_document("", None)


# ---------------------------------------------------------------------------
# health_service
# ---------------------------------------------------------------------------


def test_tool_health_service_is_local() -> None:
    """health_service() returns {"status": "ok"}."""
    assert tool_svc.health_service() == {"status": "ok"}


# ---------------------------------------------------------------------------
# No local fetch helpers
# ---------------------------------------------------------------------------


def test_tool_service_does_not_own_fetch_helpers() -> None:
    """The tool service module must not define any _fetch_* functions locally.

    All DB fetch logic lives in the backend service.  If a _fetch_* helper
    appears in the tool service namespace it means the fetch logic was
    accidentally duplicated, violating the single-source-of-truth contract.
    """
    fetch_helpers = [
        name
        for name in dir(tool_svc)
        if name.startswith("_fetch_") and isinstance(getattr(tool_svc, name), types.FunctionType)
    ]
    assert fetch_helpers == [], (
        f"Tool service defines _fetch_* helpers that should live only in the "
        f"backend service: {fetch_helpers}"
    )
