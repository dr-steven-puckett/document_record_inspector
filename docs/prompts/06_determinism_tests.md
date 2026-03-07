# Phase 06 — Determinism Tests

## Goal

Prove the core invariants of the tool's determinism contract.

## Deliverables

`tests/test_determinism_json.py` covering:

### canonical_json unit tests
- `sort_keys=True` (dict with unordered keys must serialize in alphabetical order)
- Nested objects also sorted
- Compact separators (no extra spaces)
- Trailing newline present
- `canonical_json_bytes` returns UTF-8 encoded form

### Byte-identical repeat tests
- `inspect_from_fixture()` called twice with same args → identical output
- Including `include_text=True` and `include_vectors=True` variants

### Gating tests
- `include_text=False` (default): all `chunk.text` are `None`
- `include_text=True`: at least one `chunk.text` is non-None
- `include_vectors=False` (default): all `embedding.vector` are `None`
- `include_vectors=True`: at least one `embedding.vector` is non-None

### Shuffle independence
- Call `inspect_from_fixture()` once with fixture
- Shuffle all arrays in fixture
- Call again — output must be byte-identical

### Error path tests
- Unknown document_id → `ValueError` with "not found"
- Empty document_id → `ValueError` with "empty"

## Validation

```bash
pytest tests/test_determinism_json.py -q
```
