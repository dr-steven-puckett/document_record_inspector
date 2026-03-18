"""Idempotency tests — not applicable to document_record_inspector.

document_record_inspector is a read-only inspection tool.  It has no create,
update, or delete operations and therefore no idempotency surface to test.
This module is kept as an explicit record of that decision.
"""
from __future__ import annotations

import pytest


@pytest.mark.skip(
    reason=(
        "document_record_inspector is read-only; no create/write operations exist "
        "so idempotency testing is not applicable to this tool."
    )
)
def test_idempotent_create_flow() -> None:
    pass  # not applicable

