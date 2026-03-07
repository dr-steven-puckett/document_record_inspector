# Phase 05 — OpenAPI Snapshot

## Goal

Capture and lock the OpenAPI schema to detect any accidental drift.

## Deliverables

1. `document_record_inspector/api/openapi_snapshot.py`:
   - `build_app() -> FastAPI` — minimal app with router included
   - `generate_openapi() -> dict` — returns the OpenAPI schema dict
   - `main()` — writes `openapi.snapshot.json` to repo root

2. `openapi.snapshot.json` at repo root — populated by update command

3. `tests/test_openapi_snapshot.py`:
   - Normal mode: compare `generate_openapi()` against saved file
   - Update mode (`UPDATE_OPENAPI_SNAPSHOT=1`): write new file, skip comparison
   - Skip if snapshot is placeholder `{}`
   - Sanity tests: schema has `openapi` key, `paths` key, health path, documents path

## Update Command

```bash
UPDATE_OPENAPI_SNAPSHOT=1 pytest tests/test_openapi_snapshot.py -q
```

## Validation

```bash
# After running update command:
pytest tests/test_openapi_snapshot.py -q
# All tests should pass
```
