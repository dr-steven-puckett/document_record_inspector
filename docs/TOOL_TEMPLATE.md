# Document Record Inspector — Tool Template Reference

This file records the template version and conventions used to build this tool.

**Template version:** TechVault Tool Factory v2.0.0  
**Reference implementation:** `document_catalog_query`  
**Build date:** 2025

---

## Directory Structure

```
document_record_inspector/
├── tool.toml                          # Platform manifest
├── pyproject.toml                     # Package config + deps
├── pytest.ini                         # Test runner config
├── README.md                          # Top-level README
├── TEMPLATE_MANIFEST.json             # Template conformance tracker
├── openapi.snapshot.json              # Locked OpenAPI schema
├── document_record_inspector/
│   ├── __init__.py
│   ├── tool.py                        # TOOL_SPEC + stub run()
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py                    # get_db() FastAPI dependency
│   │   ├── router.py                  # FastAPI router (thin adapter)
│   │   ├── schemas.py                 # Pydantic request/response models
│   │   └── openapi_snapshot.py        # Schema generator + writer
│   ├── core/
│   │   ├── __init__.py
│   │   ├── catalog_loader.py          # Safe fixture loader
│   │   ├── determinism.py             # canonical_json helpers
│   │   └── service.py                 # All business logic
│   └── cli/
│       ├── __init__.py
│       └── main.py                    # argparse entry point
├── tests/
│   ├── __init__.py
│   ├── fixtures/
│   │   └── sample_record.json        # Test fixture (all 6 tables)
│   ├── test_contract_schemas.py
│   ├── test_ordering_pagination.py
│   ├── test_determinism_json.py
│   ├── test_api_smoke.py
│   ├── test_cli_smoke.py
│   └── test_openapi_snapshot.py
└── docs/
    ├── TOOL_DOCUMENT_RECORD_INSPECTOR_SOT.md
    ├── TOOL_DOCUMENT_RECORD_INSPECTOR_EXECUTION_PLAN.md
    ├── TOOL_DOCUMENT_RECORD_INSPECTOR_ROADMAP.md
    ├── TOOL_TEMPLATE.md               # (this file)
    └── prompts/
        ├── README.md
        ├── 00_scaffold_repo.md
        ├── 01_schema_contracts.md
        ├── 02_service_layer.md
        ├── 03_api_adapter.md
        ├── 04_cli_adapter.md
        ├── 05_openapi_snapshot.md
        ├── 06_determinism_tests.md
        ├── 07_api_smoke_tests.md
        ├── 08_cli_smoke_tests.md
        ├── 09_platform_registration.md
        └── 10_sot_invariant_check.md
```

---

## Conventions

### tool.toml

- `name` must match the Python package name exactly
- `mount_prefix = ""` — the router defines the full prefix internally
- `requires_db = true` for any tool that issues DB queries
- `router_import` format: `"package.api.router:router"`
- `tool_import` + `run_import` format: `"package.tool:SYMBOL"`

### Service Layer

- All public functions accept only plain Python types + SQLAlchemy Session or dict
- No FastAPI or Pydantic imports in `core/`
- Strict exception boundary: only `ValueError` and `PermissionError` propagate; all others
  are re-raised as `RuntimeError` with context

### API Router

- One file: `api/router.py`
- `_handle_error(e)` centralises status-code mapping
- All routes have explicit `operation_id`
- No business logic in the router — delegate everything to `service.*`

### Determinism

- All list fields MUST have a documented, stable sort order
- Service layer MUST perform an in-memory re-sort after data retrieval
- `canonical_json()` MUST be used for all JSON serialisation
- Tests MUST verify byte-identical output on repeated calls
