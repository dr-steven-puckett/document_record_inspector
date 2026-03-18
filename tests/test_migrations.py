"""Migration tests — not applicable to document_record_inspector.

document_record_inspector is a read-only tool that queries existing TechVault
tables (documents, document_files, chunks, embeddings, summaries, ingest_runs).
It owns no Alembic-managed tables and therefore has no migrations to test.
"""
from __future__ import annotations

import pytest


@pytest.mark.skip(
    reason=(
        "document_record_inspector owns no database tables; no Alembic migrations "
        "exist for this tool.  The tool is read-only over shared TechVault schema."
    )
)
def test_migration_smoke() -> None:
    pass  # not applicable

