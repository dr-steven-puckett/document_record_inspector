# Phase 04 — CLI Adapter (argparse)

## Goal

Wire the service layer to an argparse CLI.  The CLI must support both fixture mode
(for offline use + tests) and live DB mode (when `DATABASE_URL` is set).

## Deliverables

`document_record_inspector/cli/main.py` with:

### Subcommands

#### `health`
```bash
python -m document_record_inspector.cli.main health
```
- Calls `service.health()`
- Emits canonical JSON to stdout
- Exits 0

#### `inspect`
```bash
python -m document_record_inspector.cli.main inspect \
    --document-id <ID>
    [--catalog-file PATH]      # fixture mode
    [--include-text]           # flag: include chunk text
    [--include-vectors]        # flag: include embedding vectors
```
- If `--catalog-file` given: load fixture → `service.inspect_from_fixture()`
- Else: `DATABASE_URL` must be set → `service.inspect_from_db()`
- Emits canonical JSON to stdout
- Exits 0 on success; exits 1 on error

### Helpers

- `_emit(data: dict)` — writes `canonical_json(data)` to stdout
- `_die(msg: str)` — writes error to stderr, exits 1

## Validation

```bash
pytest tests/test_cli_smoke.py -q
```
