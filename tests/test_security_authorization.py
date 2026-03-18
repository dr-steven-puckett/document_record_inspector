"""Security and authorization tests for document_record_inspector.

This tool is a read-only forensic inspector with no user-facing auth layer
beyond TechVault's platform-level access controls.  Security_level filtering
is the platform's responsibility; the tool returns all rows for a given
document_id regardless of security level.

The tests here verify the schema contract around security_level fields (which
are present in DocumentRow, SummaryRow, IngestRunRow, etc.) to confirm they
are not dropped or mutated.
"""
from __future__ import annotations

from document_record_inspector.core.service import assemble_inspection_record
from tests.conftest import DOC_ID, DOCUMENT_DICT, INGEST_RUN_1, SUMMARY_1


def test_document_row_preserves_security_level() -> None:
    result = assemble_inspection_record(
        document_id=DOC_ID,
        document=dict(DOCUMENT_DICT),
        document_files=[],
        chunks=[],
        embeddings=[],
        summaries=[],
        ingest_runs=[],
    )
    assert result.document is not None
    assert result.document.security_level == "internal"


def test_summary_row_preserves_security_level() -> None:
    result = assemble_inspection_record(
        document_id=DOC_ID,
        document=dict(DOCUMENT_DICT),
        document_files=[],
        chunks=[],
        embeddings=[],
        summaries=[dict(SUMMARY_1)],
        ingest_runs=[],
    )
    assert result.summaries[0].security_level == "internal"


def test_ingest_run_preserves_security_level() -> None:
    result = assemble_inspection_record(
        document_id=DOC_ID,
        document=dict(DOCUMENT_DICT),
        document_files=[],
        chunks=[],
        embeddings=[],
        summaries=[],
        ingest_runs=[dict(INGEST_RUN_1)],
    )
    assert result.ingest_runs[0].security_level == "internal"


def test_security_level_not_mutated_by_service() -> None:
    """The service must not normalise, modify, or strip security_level values."""
    secret_doc = dict(DOCUMENT_DICT)
    secret_doc["security_level"] = "secret"
    result = assemble_inspection_record(
        document_id=DOC_ID,
        document=secret_doc,
        document_files=[],
        chunks=[],
        embeddings=[],
        summaries=[],
        ingest_runs=[],
    )
    assert result.document is not None
    assert result.document.security_level == "secret"

