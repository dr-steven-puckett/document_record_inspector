"""Byte-identical canonical JSON determinism tests."""
from __future__ import annotations

from document_record_inspector.core.determinism import canonical_json
from document_record_inspector.core.service import assemble_inspection_record
from tests.conftest import DOC_ID


def _serialize(data: dict) -> str:
    result = assemble_inspection_record(**data)
    return canonical_json(result.model_dump())


# ---------------------------------------------------------------------------
# canonical_json unit tests
# ---------------------------------------------------------------------------


def test_canonical_json_sort_keys() -> None:
    out = canonical_json({"z": 1, "a": 2, "m": 3})
    assert out == '{"a":2,"m":3,"z":1}'


def test_canonical_json_no_whitespace() -> None:
    out = canonical_json({"key": "value"})
    assert " " not in out


def test_canonical_json_nested_keys_sorted() -> None:
    out = canonical_json({"outer": {"z": 1, "a": 2}})
    assert out == '{"outer":{"a":2,"z":1}}'


def test_canonical_json_list_preserved_order() -> None:
    # Lists must NOT be re-sorted by canonical_json; sorting is the service's job.
    out = canonical_json({"items": [3, 1, 2]})
    assert out == '{"items":[3,1,2]}'


def test_canonical_json_null() -> None:
    out = canonical_json({"x": None})
    assert out == '{"x":null}'


# ---------------------------------------------------------------------------
# Repeated call byte-identity
# ---------------------------------------------------------------------------


def test_repeated_calls_byte_identical(full_data) -> None:
    first = _serialize(full_data)
    for _ in range(5):
        assert _serialize(full_data) == first


def test_empty_result_byte_identical() -> None:
    data = {
        "document_id": DOC_ID,
        "document": None,
        "document_files": [],
        "chunks": [],
        "embeddings": [],
        "summaries": [],
        "ingest_runs": [],
    }
    first = _serialize(data)
    for _ in range(5):
        assert _serialize(data) == first


# ---------------------------------------------------------------------------
# inspect_document standalone mode determinism
# ---------------------------------------------------------------------------


def test_inspect_document_standalone_byte_identical() -> None:
    from document_record_inspector.core.service import inspect_document  # noqa: PLC0415

    r1 = canonical_json(inspect_document(DOC_ID, None).model_dump())
    r2 = canonical_json(inspect_document(DOC_ID, None).model_dump())
    assert r1 == r2


# ---------------------------------------------------------------------------
# Standalone-mode response is deterministic regardless of document_id input
# ---------------------------------------------------------------------------


def test_different_doc_ids_produce_different_outputs() -> None:
    from document_record_inspector.core.service import inspect_document  # noqa: PLC0415

    r1 = canonical_json(inspect_document("doc-aaa", None).model_dump())
    r2 = canonical_json(inspect_document("doc-bbb", None).model_dump())
    # Different document_ids must produce different canonical outputs
    assert r1 != r2

