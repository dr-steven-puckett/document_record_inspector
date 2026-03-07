# Phase 01 — Schema Contracts

## Goal

Define all Pydantic v2 models for the API response and create the test fixture.
Write contract tests to verify model construction and field validation.

## Database Tables → Response Models

| Table | Pydantic Model |
|---|---|
| `documents` | `DocumentRow` |
| `document_files` | `DocumentFileRow` |
| `chunks` | `ChunkRow` (text: Optional[str]) |
| `embeddings` | `EmbeddingRow` (vector: Optional[Any], chunk_index: Optional[int]) |
| `summaries` | `SummaryRow` |
| `ingest_runs` | `IngestRunRow` |
| _(assembled)_ | `InspectionCounts` |
| _(assembled)_ | `InspectionResponse` |

## Deliverables

1. `document_record_inspector/api/schemas.py` — all 8+ models; `model_config = ConfigDict(from_attributes=True)`
2. `document_record_inspector/core/determinism.py` — `canonical_json(obj: Any) -> str`; `canonical_json_bytes(obj: Any) -> bytes`
3. `tests/fixtures/sample_record.json` — realistic fixture with:
   - 1 document row (DOC_ID = `aaaa1111...` × 4 segments)
   - 2 files in **non-alphabetical** order (aux before primary)
   - 2 chunks with `chunk_index` **reversed** in array (1 before 0)
   - 2 embeddings
   - 2 summaries in **non-alphabetical** order (general before executive)
   - 1 ingest_run
4. `tests/test_contract_schemas.py` — per-model tests

## Validation

```bash
pytest tests/test_contract_schemas.py -q
```
