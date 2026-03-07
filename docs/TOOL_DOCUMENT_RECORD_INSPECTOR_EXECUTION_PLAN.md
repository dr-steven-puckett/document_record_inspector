# Document Record Inspector — Execution Plan

This document records the ordered build phases used to construct this tool
following the TechVault Tool Factory pipeline (v2.0.0).

---

## Phase 0 — Scaffold Repository

**Goal:** Create the canonical directory skeleton and all configuration files.

**Deliverables:**
- `tool.toml` — platform manifest
- `pyproject.toml` — package build config + deps
- `pytest.ini` — test runner config
- `README.md` — top-level README
- `TEMPLATE_MANIFEST.json` — tracks template conformance
- `openapi.snapshot.json` — placeholder `{}`
- All `__init__.py` files in `document_record_inspector/`, `api/`, `core/`, `cli/`, `tests/`

**Status:** ✅ Complete

---

## Phase 1 — Schema Contracts

**Goal:** Define all Pydantic models and verify them with tests.

**Deliverables:**
- `document_record_inspector/api/schemas.py` — 8 models: `HealthResponse`, `DocumentRow`,
  `DocumentFileRow`, `ChunkRow`, `EmbeddingRow`, `SummaryRow`, `IngestRunRow`,
  `InspectionCounts`, `InspectionResponse`
- `document_record_inspector/core/determinism.py` — `canonical_json()`, `canonical_json_bytes()`
- `tests/fixtures/sample_record.json` — realistic test fixture (all 6 tables, intentionally
  unordered arrays)
- `tests/test_contract_schemas.py` — per-model construction + field validation

**Status:** ✅ Complete

---

## Phase 2 — Service Layer

**Goal:** Implement all business logic with dual-mode (fixture + DB) support.

**Deliverables:**
- `document_record_inspector/core/catalog_loader.py` — safe fixture loader with path checks
- `document_record_inspector/core/service.py` — `inspect_from_fixture()`, `inspect_from_db()`,
  sort helpers, projection helpers, `health()`
- `tests/test_ordering_pagination.py` — ordering invariants for all 5 collections

**Status:** ✅ Complete

---

## Phase 3 — API + CLI Adapters

**Goal:** Wire the service layer to FastAPI and argparse.

**Deliverables:**
- `document_record_inspector/api/router.py` — thin adapter; prefix
  `/v1/tools/document_record_inspector`; operation IDs; error mapping
- `document_record_inspector/api/deps.py` — `get_db()` using `DATABASE_URL`
- `document_record_inspector/cli/main.py` — argparse; `health` + `inspect` subcommands;
  `_emit()` + `_die()`
- `document_record_inspector/tool.py` — `TOOL_SPEC` + stub `run()`

**Status:** ✅ Complete

---

## Phase 4 — OpenAPI Snapshot

**Goal:** Capture and lock the OpenAPI schema for drift detection.

**Deliverables:**
- `document_record_inspector/api/openapi_snapshot.py` — `generate_openapi()`, `main()`
- `openapi.snapshot.json` — populated by `UPDATE_OPENAPI_SNAPSHOT=1 pytest`
- `tests/test_openapi_snapshot.py` — comparison + update mode tests

**Status:** ⚠️ `openapi.snapshot.json` is a placeholder `{}` — run update command after
`pip install -e ".[test]"` to populate it.

---

## Phase 5 — Determinism Tests

**Goal:** Prove byte-identical output and gating controls.

**Deliverables:**
- `tests/test_determinism_json.py` — `canonical_json` unit tests, include_text/include_vectors
  gating, shuffle independence, 404 path, empty-id validation

**Status:** ✅ Complete

---

## Phase 6 — Smoke Tests

**Goal:** End-to-end validation via TestClient and subprocess.

**Deliverables:**
- `tests/test_api_smoke.py` — FastAPI TestClient; health + inspect success + 404 + gating
- `tests/test_cli_smoke.py` — `subprocess.run` tests; health + inspect + error paths

**Status:** ✅ Complete

---

## Phase 7 — Platform Registration

**Goal:** Register the tool with the TechVault platform.

**Steps:**
1. Add this repo as a git submodule:
   ```bash
   cd ~/projects/techvault/backend
   git submodule add <REPO_URL> tools/document_record_inspector
   ```
2. Add `"document_record_inspector"` to `backend/platform/enabled_tools.toml`
3. Run `pip install -e tools/document_record_inspector`
4. Restart the backend API server
5. Verify `GET /v1/tools/document_record_inspector/health` returns 200

**Status:** ❌ Not started (requires platform environment)

---

## Validation Commands

```bash
cd ~/projects/tools/document_record_inspector
pip install -e ".[test]"
pytest -q                                                          # full suite
UPDATE_OPENAPI_SNAPSHOT=1 pytest tests/test_openapi_snapshot.py   # regenerate snapshot
pytest -q                                                          # verify snapshot test passes
```
