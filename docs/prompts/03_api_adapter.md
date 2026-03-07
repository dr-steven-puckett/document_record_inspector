# Phase 03 — API Adapter (FastAPI Router)

## Goal

Wire the service layer to a FastAPI router.  The router is a **thin adapter only** —
all logic lives in `core/service.py`.

## Deliverables

1. `document_record_inspector/api/router.py`:
   - `prefix = "/v1/tools/document_record_inspector"`
   - `GET /health` → `operation_id="document_record_inspector_health"`
   - `GET /documents/{document_id}` → `operation_id="document_record_inspector_inspect"`
   - `_handle_error(e)` maps exceptions to HTTP status codes:
     - `PermissionError` → 403
     - `ValueError` with "not found" in message → 404
     - `ValueError` → 400
     - all others → 500
   - Query params: `include_text: bool = False`, `include_vectors: bool = False`
   - DB dependency via `Depends(get_db)`

2. `document_record_inspector/api/deps.py`:
   - `get_db()` generator using `DATABASE_URL` env var
   - Yields a SQLAlchemy `Session`

## Invariants

- Router must not import from `core` directly — only call `service.*` functions
- No Pydantic model construction in router — use `InspectionResponse.model_validate(result)`

## Validation

```bash
pytest tests/test_api_smoke.py -q
```
