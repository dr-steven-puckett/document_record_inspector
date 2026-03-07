# Document Record Inspector — Roadmap

This roadmap tracks planned enhancements.  The tool is intentionally scoped
to a read-only, deterministic, single-document inspection primitive.
Expansions beyond that scope are deferred to separate tools.

---

## Current Version: v0.1.0

Capabilities delivered:
- Full record assembly for all 6 tables
- Dual-mode (fixture + live DB)
- `include_text` and `include_vectors` gating
- Deterministic sort + JSON serialization
- OpenAPI snapshot drift detection
- CLI + HTTP API

---

## Planned

### v0.2.0 — Pagination for large documents

Large documents can have hundreds of chunks and thousands of embeddings.
Add pagination query parameters to the chunks and embeddings collections:

```
?chunks_offset=0&chunks_limit=100
?embeddings_offset=0&embeddings_limit=100
```

Count fields in `counts` must remain the total count regardless of pagination.

### v0.3.0 — Field projection

Allow callers to request only a subset of top-level keys to reduce payload size:

```
?include=document,files,counts
```

### v0.4.0 — Ingest run filtering

Allow filtering ingest_runs by status:

```
?ingest_run_status=completed
```

### v0.5.0 — Batch inspection

Multi-document inspection in a single request:

```
POST /v1/tools/document_record_inspector/batch
{ "document_ids": ["id1", "id2"] }
```

---

## Out of Scope (deferred to other tools)

| Feature | Rationale |
|---|---|
| Full-text search | Covered by `document_catalog_query` |
| Embedding similarity search | Separate vector-search tool |
| Write operations | Tool is strictly read-only |
| LLM summarization | Out of scope by design (deterministic tool) |
