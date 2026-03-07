# document_record_inspector

Deterministic read-only inspection tool for returning the full record-level view
of a single TechVault document, including all related ingestion artifacts.

## Purpose

Returns one deterministic JSON object for a given `document_id`, aggregating:

- `documents` row
- `document_files`
- `chunks`
- `embeddings`
- `summaries`
- `ingest_runs`
- `counts`

## Canonical invocation (CLI)

```bash
# inspect a document (no text or vectors by default)
python -m document_record_inspector.cli.main inspect --document-id <ID>

# include chunk text
python -m document_record_inspector.cli.main inspect --document-id <ID> --include-text

# include embedding vectors
python -m document_record_inspector.cli.main inspect --document-id <ID> --include-vectors

# standalone / test mode (fixture file instead of live DB)
python -m document_record_inspector.cli.main inspect --document-id <ID> --catalog-file tests/fixtures/sample_record.json

# health check
python -m document_record_inspector.cli.main health
```

## API endpoint

```
GET /v1/tools/document_record_inspector/documents/{document_id}
    ?include_text=false
    ?include_vectors=false
```

Status codes: `200` success · `404` document not found · `422` validation error

## Environment

| Variable       | Purpose                                  |
|----------------|------------------------------------------|
| `DATABASE_URL` | PostgreSQL connection string (required for live DB mode) |

## Determinism guarantees

- Explicit sort order on every collection (no DB default ordering relied upon)
- `include_text=false` always omits chunk text (returns `null`)
- `include_vectors=false` always omits embedding vectors (returns `null`)
- Byte-identical JSON for identical database state

## Required sort orders

| Collection   | Sort keys                                     |
|--------------|-----------------------------------------------|
| files        | role ASC, rel_path ASC, id ASC                |
| chunks       | chunk_index ASC, id ASC                       |
| embeddings   | chunk_index ASC, embedding_model ASC, id ASC  |
| summaries    | output_type ASC, created_at ASC, id ASC       |
| ingest_runs  | started_at ASC, id ASC                        |

## Development

```bash
# install in editable mode
pip install -e ".[test]"

# run tests
pytest -q

# regenerate OpenAPI snapshot
UPDATE_OPENAPI_SNAPSHOT=1 pytest tests/test_openapi_snapshot.py -q
```

## Registration

Add `"document_record_inspector"` to `backend/platform/enabled_tools.toml` to enable.
