# Phase 02 — Service Layer

## Goal

Implement all business logic in `core/service.py`.  The service must support two modes:

1. **Fixture mode** (`inspect_from_fixture`) — used by CLI `--catalog-file` and all tests
2. **Live DB mode** (`inspect_from_db`) — used by the FastAPI endpoint with a real Postgres connection

## Sort Orders (determinism invariant)

| Collection | Sort keys (in order) |
|---|---|
| `files` | `role ASC`, `rel_path ASC`, `id ASC` |
| `chunks` | `chunk_index ASC`, `id ASC` |
| `embeddings` | `chunk_index ASC`, `embedding_model ASC`, `id ASC` |
| `summaries` | `output_type ASC`, `created_at ASC`, `id ASC` |
| `ingest_runs` | `started_at ASC`, `id ASC` |

## Deliverables

1. `document_record_inspector/core/catalog_loader.py`:
   - `load_fixture(catalog_file: str | Path) -> dict`
   - Path safety: reject absolute paths, `..` segments, null bytes
   - Validate required keys: `{document, files, chunks, embeddings, summaries, ingest_runs}`

2. `document_record_inspector/core/service.py`:
   - `health() -> dict`
   - `inspect_from_fixture(fixture, document_id, *, include_text, include_vectors) -> dict`
   - `inspect_from_db(db, document_id, *, include_text, include_vectors) -> dict`
   - `_sort_files()`, `_sort_chunks()`, `_sort_embeddings()`, `_sort_summaries()`, `_sort_ingest_runs()`
   - `_project_chunk()` — gates `text` field
   - `_project_embedding()` — gates `vector` field
   - `_build_result()` — assembles final payload

3. `tests/test_ordering_pagination.py` — ordering invariants for all 5 collections

## Strict Exception Boundary

| Exception | Meaning |
|---|---|
| `ValueError("document not found: ...")` | Unknown document_id |
| `ValueError("document_id cannot be empty")` | Empty string given |
| `PermissionError(...)` | Path traversal violation in fixture mode |
| `RuntimeError(...)` | Any unexpected internal error |

## Validation

```bash
pytest tests/test_ordering_pagination.py -q
```
