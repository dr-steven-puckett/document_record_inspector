# Phase 07 — API Smoke Tests (FastAPI TestClient)

## Goal

End-to-end HTTP-level smoke tests using FastAPI's `TestClient`.
No real database needed — the `get_db` dependency is overridden to return fixture data.

## Pattern

```python
from fastapi import FastAPI
from fastapi.testclient import TestClient
from document_record_inspector.api.router import router
from document_record_inspector.api.deps import get_db

fixture = load_fixture("tests/fixtures/sample_record.json")
app = FastAPI()
app.include_router(router)
app.dependency_overrides[get_db] = lambda: iter([fixture])
client = TestClient(app)
```

The router's service calls delegate to `inspect_from_db`, which is patched (or via
dependency injection) to use fixture mode when a dict is passed instead of a Session.

## Required Test Cases

| Test | Expected |
|---|---|
| `GET /health` | 200, `{"status": "ok", "tool_id": "document_record_inspector"}` |
| `GET /documents/{DOC_ID}` | 200, all 7 top-level keys |
| `GET /documents/{MISSING}` | 404 |
| Default `include_text` | All `chunk.text` are null |
| `?include_text=true` | At least one `chunk.text` non-null |
| Default `include_vectors` | All `embedding.vector` are null |
| Files sorted by role | `roles == sorted(roles)` |
| Chunks sorted by index | `indexes == sorted(indexes)` |
| Byte-identical repeat | Two identical calls return identical JSON |

## Validation

```bash
pytest tests/test_api_smoke.py -q
```
