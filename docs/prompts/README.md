# Build Prompts — document_record_inspector

This directory contains the ordered phase prompts used to construct the tool
following the TechVault Tool Factory pipeline.

| File | Phase | Description |
|---|---|---|
| `00_scaffold_repo.md` | 0 | Create repo skeleton, config files, __init__.py files |
| `01_schema_contracts.md` | 1 | Define Pydantic models + contract tests |
| `02_service_layer.md` | 2 | Implement dual-mode service logic |
| `03_api_adapter.md` | 3 | Wire service to FastAPI router |
| `04_cli_adapter.md` | 4 | Wire service to argparse CLI |
| `05_openapi_snapshot.md` | 5 | Generate and lock OpenAPI schema |
| `06_determinism_tests.md` | 6 | Prove byte-identical + gating invariants |
| `07_api_smoke_tests.md` | 7 | FastAPI TestClient smoke tests |
| `08_cli_smoke_tests.md` | 8 | Subprocess CLI smoke tests |
| `09_platform_registration.md` | 9 | Register with TechVault platform |
| `10_sot_invariant_check.md` | 10 | Final SOT + template conformance check |
