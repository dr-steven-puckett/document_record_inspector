# document_record_inspector

## Tool Overview

Deterministic TechVault tool scaffold generated from the standard template.

This tool is a standalone repository. It is integrated into TechVault by:
1. placing the repo as a git submodule at `backend/tools/document_record_inspector`
2. providing a valid `tool.toml` — TechVault discovers the tool automatically from this file
3. activation is controlled by local operator overrides first, then `enabled_by_default` in `tool.toml`

## API Usage

Router entrypoint:

- `document_record_inspector.api.router:router`

## CLI Usage

Run CLI commands using module invocation:

- `python -m document_record_inspector.cli <command>`

## Standalone Mode (--catalog-file)

Example:

- `python -m document_record_inspector.cli search --catalog-file catalog.json`

## Determinism Guarantees

- explicit sorting
- stable pagination
- canonical JSON serialization
- byte-identical outputs for identical inputs
- input-order independence

## Testing

Run standalone tests (no TechVault runtime required):

- `pytest -q`

OpenAPI snapshot workflow:

- `pytest tests/test_openapi_snapshot.py`
- `UPDATE_OPENAPI_SNAPSHOT=1 pytest` (only for intentional API changes)

## Quality Gates

Run these before completion:

- `pytest -q`
- `ruff check .`
- `ruff format .`
- `platform tools verify document_record_inspector`

Expected platform verification result:

- `overall_ok: true`

## TechVault Platform v2 Host Integration

This template targets the manifest-driven TechVault platform flow.

Required host-side steps:

1. Add the tool as a submodule under `backend/tools/document_record_inspector`.
2. Ensure the tool package is installed in the TechVault runtime environment (editable install).
3. Keep `tool.toml` as the source of truth for router discovery and activation.

If you declare `[[techvault.adapters]]` entries in `tool.toml`, you must also add matching
host adapter factories in TechVault at:

- `backend/platform/tool_adapters/document_record_inspector.py`

Each declared `override_factory_import` must resolve to an existing callable in that file.
