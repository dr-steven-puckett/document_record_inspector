# Prompt 07 — Final Gate

## Goal
Run the final quality gate for template compliance.

## Inputs
- `docs/TOOL_TEMPLATE_SOT.md`
- Full test suite

## Requirements
- Execute the full test suite.
- Run static checks: `ruff check .`.
- Run formatting pass: `ruff format .`.
- Confirm standalone CLI mode works using `--catalog-file`.
- Confirm API and CLI outputs remain contract-aligned.
- Confirm OpenAPI snapshot is stable via `pytest tests/test_openapi_snapshot.py`.
- If intentional API-schema changes occurred, regenerate snapshot via `UPDATE_OPENAPI_SNAPSHOT=1 pytest` and re-run verification.
- Confirm determinism checks pass.
- Confirm `response_hash` checks pass when hash is enabled.
- Confirm `techvault-tool-validate <repo_path>` exits 0.
- Confirm `techvault-tool-security-scan <repo_path>` exits 0.
- For DB-backed tools, confirm migration verification succeeds (`alembic upgrade head` then `alembic downgrade base`).
- Confirm `platform tools verify <tool_name>` reports `overall_ok: true`.

## Checkpoint
- `pytest -q` is fully green.
- `ruff check .` passes.
- `ruff format .` applied (or no changes required).
