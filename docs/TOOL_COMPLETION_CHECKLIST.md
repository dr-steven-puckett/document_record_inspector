# Tool Completion Checklist

Use this checklist before marking a TechVault tool as complete.

- [ ] Manifest validated (`tool.toml` valid and coherent)
- [ ] Router uses resource-level prefixes only (no `/v1/tools/...` hardcoding)
- [ ] Security values use canonical set only: `public`, `internal`, `confidential`, `secret`
- [ ] Service-layer validation implemented before DB persistence
- [ ] Idempotency behavior complete (lookup, insert attempt, `IntegrityError`, reload canonical row)
- [ ] Concurrency handling complete for uniqueness/idempotency paths
- [ ] DB constraints added where persistence/uniqueness applies
- [ ] Migrations implemented and tested where DB-backed
- [ ] Required tests implemented (service, router/API, security, idempotency, migration when relevant, OpenAPI snapshot)
- [ ] OpenAPI snapshot updated and verified
- [ ] `ruff check .` passes
- [ ] `ruff format .` applied (or no changes required)
- [ ] `platform tools verify <tool_name>` passes with `overall_ok: true`
