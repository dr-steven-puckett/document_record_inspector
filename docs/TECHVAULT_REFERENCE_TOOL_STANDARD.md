# TechVault Reference Tool Standard

This document is the reference-quality completion standard for all TechVault tool repositories generated from this template.

## 1. Manifest Correctness

- `tool.toml` must be present and valid.
- `tool_id`, `entrypoint`, capabilities, and activation posture must be coherent.
- Template stamp fields must be valid and current for the selected manifest baseline.

## 2. Router Mounting Rules

- Tool routers must define resource-level prefixes only.
- Tool routers must not hardcode platform prefixes such as `/v1/tools/...`.
- Platform mounting owns the final tool path.

Required pattern:

```python
router = APIRouter(prefix="/items")
```

Platform mount example:

- Platform mount prefix: `/v1/tools/<tool-name>`
- Final route path: `/v1/tools/<tool-name>/items`

## 3. Security Model Consistency

- The only valid security levels are `public`, `internal`, `confidential`, `secret`.
- No alternative vocabulary is allowed.
- Manifest, schema, service, DB constraints, and docs must use the same set.

## 4. Service Validation Requirements

- Service layer is the canonical validation boundary.
- Invalid values must be rejected in service code before DB persistence.
- Schema-level checks are recommended where appropriate.
- DB-level constraints are required for persisted fields where applicable.

## 5. Idempotency Requirements

For create operations with `idempotency_key`, deterministic behavior is required:

1. Lookup by `idempotency_key`.
2. Attempt insert.
3. Catch `IntegrityError`.
4. Reload canonical row.
5. Return deterministic canonical result.

This is required behavior, not optional guidance.

## 6. Concurrency Safety

- DB uniqueness constraints are required where uniqueness/idempotency applies.
- Service layer must handle uniqueness conflicts deterministically.
- Concurrent callers must not observe nondeterministic duplicate-create behavior.

## 7. Migration Requirements

For DB-backed tools:

- Migrations must exist for schema changes.
- Migration verification must be part of completion and CI where available.
- Minimum smoke workflow:

```bash
alembic upgrade head
alembic downgrade base
```

## 8. Required Test Categories

Each completed tool must include tests for relevant categories:

- service tests
- router/API tests
- security/authorization tests
- idempotency tests
- migration tests (DB-backed tools)
- OpenAPI snapshot tests
- manifest/platform verification tests where supported by the repo

## 9. OpenAPI Snapshot Expectations

- `openapi.snapshot.json` is required.
- Snapshot verification must be deterministic and part of normal testing.
- Standard commands:

```bash
pytest tests/test_openapi_snapshot.py
UPDATE_OPENAPI_SNAPSHOT=1 pytest
```

## 10. Documentation Completeness

Each tool must include and maintain:

- tool-specific SoT
- execution plan
- roadmap
- prompt pack
- README usage examples for API and CLI

Documentation must match actual behavior.

## 11. Final Platform Verification

The completion gate must include platform verification:

```bash
pytest -q
ruff check .
ruff format .
platform tools verify <tool_name>
```

Core expected result:

```bash
platform tools verify <tool_name>
```

Expected outcome:

- `overall_ok: true`

No tool is complete until this gate passes.