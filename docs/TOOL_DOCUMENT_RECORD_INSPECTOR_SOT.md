# Document Record Inspector — Source of Truth

## Purpose

`document_record_inspector` is a read-only, deterministic TechVault tool that returns the
complete database record for a single document.  Given a `document_id` it assembles and returns
data from all six related tables:

| Table | Alias in response |
|---|---|
| `documents` | `document` |
| `document_files` | `files` |
| `chunks` | `chunks` |
| `embeddings` | `embeddings` |
| `summaries` | `summaries` |
| `ingest_runs` | `ingest_runs` |

The tool makes **no LLM calls**, issues **no writes**, and has **no side effects**.

---

## Canonical Endpoint

```
GET /v1/tools/document_record_inspector/documents/{document_id}
    ?include_text=false
    ?include_vectors=false
```

### Query parameters

| Parameter | Default | Effect |
|---|---|---|
| `include_text` | `false` | When `false`, `chunk.text` is `null` in response |
| `include_vectors` | `false` | When `false`, `embedding.vector` is `null` in response |

### Response shape

```json
{
  "document": { ... },
  "files": [ ... ],
  "chunks": [ ... ],
  "embeddings": [ ... ],
  "summaries": [ ... ],
  "ingest_runs": [ ... ],
  "counts": {
    "files": 0,
    "chunks": 0,
    "embeddings": 0,
    "summaries": 0,
    "ingest_runs": 0
  }
}
```

### Error codes

| Code | Condition |
|---|---|
| 400 | Empty or invalid `document_id` |
| 404 | No document with that ID |
| 403 | Path traversal / security violation in fixture mode |
| 500 | Unexpected internal error |

---

## Determinism Contract

1. All list fields return rows in a **stable, deterministic order** regardless of input order.  
2. JSON output uses `json.dumps(sort_keys=True)` + compact separators.  
3. Calling the same endpoint twice with identical inputs MUST produce **byte-identical** responses.

### Sort orders

| Collection | Primary | Secondary | Tertiary |
|---|---|---|---|
| `files` | `role` ASC | `rel_path` ASC | `id` ASC |
| `chunks` | `chunk_index` ASC | `id` ASC | — |
| `embeddings` | `chunk_index` ASC | `embedding_model` ASC | `id` ASC |
| `summaries` | `output_type` ASC | `created_at` ASC | `id` ASC |
| `ingest_runs` | `started_at` ASC | `id` ASC | — |

---

## Service Layer

Two modes are supported:

| Mode | Entry point | Use case |
|---|---|---|
| Fixture / standalone | `inspect_from_fixture(fixture, doc_id, ...)` | CLI `--catalog-file`, tests |
| Live DB | `inspect_from_db(db, doc_id, ...)` | FastAPI endpoint with real Postgres |

The service layer performs an **in-memory re-sort** after data retrieval to guarantee determinism
even if the database returns rows in a different order.

---

## Platform Integration

| Field | Value |
|---|---|
| `tool.toml [api].router_import` | `document_record_inspector.api.router:router` |
| `tool.toml [api].mount_prefix` | `""` (router defines `/v1/tools/document_record_inspector` itself) |
| `tool.toml [policy].requires_db` | `true` |
| Enable in platform | Add `"document_record_inspector"` to `enabled_tools.toml` |

---

## CLI

```bash
# Health check (no DB needed)
python -m document_record_inspector.cli.main health

# Inspect via fixture (no DB needed)
python -m document_record_inspector.cli.main inspect \
    --document-id <ID> \
    --catalog-file tests/fixtures/sample_record.json

# Inspect via live DB (DATABASE_URL must be set)
python -m document_record_inspector.cli.main inspect --document-id <ID>
```

---

## OpenAPI Snapshot

`openapi.snapshot.json` at the repository root captures the full OpenAPI schema.

To regenerate after any schema change:
```bash
UPDATE_OPENAPI_SNAPSHOT=1 pytest tests/test_openapi_snapshot.py -q
```

---

## Template Version

Built against TechVault Tool Factory **v2.0.0**.  
Reference implementation: `document_catalog_query`.
