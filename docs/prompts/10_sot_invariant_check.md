# Phase 10 — SOT Invariant Check

## Goal

Final verification that the built tool fully conforms to the SOT and template requirements.
Run this checklist before marking the tool as complete.

---

## File Checklist

```
[ ] tool.toml — all 6 required sections present
[ ] pyproject.toml — entry_points set, all deps listed
[ ] pytest.ini — testpaths = tests
[ ] README.md — exists and non-empty
[ ] TEMPLATE_MANIFEST.json — all required_files listed
[ ] openapi.snapshot.json — NOT a placeholder {} (must have been regenerated)
[ ] document_record_inspector/__init__.py
[ ] document_record_inspector/api/__init__.py
[ ] document_record_inspector/core/__init__.py
[ ] document_record_inspector/cli/__init__.py
[ ] document_record_inspector/api/deps.py
[ ] document_record_inspector/api/router.py
[ ] document_record_inspector/api/schemas.py
[ ] document_record_inspector/api/openapi_snapshot.py
[ ] document_record_inspector/core/catalog_loader.py
[ ] document_record_inspector/core/determinism.py
[ ] document_record_inspector/core/service.py
[ ] document_record_inspector/cli/main.py
[ ] document_record_inspector/tool.py
[ ] tests/__init__.py
[ ] tests/fixtures/sample_record.json
[ ] tests/test_contract_schemas.py
[ ] tests/test_ordering_pagination.py
[ ] tests/test_determinism_json.py
[ ] tests/test_api_smoke.py
[ ] tests/test_cli_smoke.py
[ ] tests/test_openapi_snapshot.py
[ ] docs/TOOL_DOCUMENT_RECORD_INSPECTOR_SOT.md
[ ] docs/TOOL_DOCUMENT_RECORD_INSPECTOR_EXECUTION_PLAN.md
[ ] docs/TOOL_DOCUMENT_RECORD_INSPECTOR_ROADMAP.md
[ ] docs/TOOL_TEMPLATE.md
[ ] docs/prompts/README.md
[ ] docs/prompts/00_scaffold_repo.md — 10_sot_invariant_check.md (11 files)
```

---

## Test Suite Invariant

```bash
cd ~/projects/tools/document_record_inspector
pip install -e ".[test]"
pytest -q
# Expected: all tests PASS, 0 failures
```

---

## OpenAPI Snapshot Invariant

```bash
UPDATE_OPENAPI_SNAPSHOT=1 pytest tests/test_openapi_snapshot.py -q
pytest tests/test_openapi_snapshot.py -q
# Expected: snapshot matches live schema
```

---

## Determinism Invariant

Run the full test suite twice — outputs must be identical:

```bash
pytest tests/test_determinism_json.py -q  # first run
pytest tests/test_determinism_json.py -q  # second run
# All tests pass both times
```

---

## SOT Compliance Checks

| Check | Command / Verification |
|---|---|
| No LLM calls | `grep -r "openai\|anthropic\|llm\|chat" document_record_inspector/` — must be empty |
| No write operations | `grep -r "INSERT\|UPDATE\|DELETE\|commit\|flush" document_record_inspector/core/` — must be empty |
| No network calls in service | `grep -r "requests\|httpx\|urllib" document_record_inspector/core/` — must be empty |
| sort_keys used everywhere | `grep -r "json.dumps" document_record_inspector/` — all must include `sort_keys=True` |
| Canonical JSON used for output | `grep -r "_emit\|canonical_json" document_record_inspector/cli/` — present |

---

## Sign-off

When all boxes are checked and all tests pass, update `TEMPLATE_MANIFEST.json`:

```json
{
  "conformance_status": "COMPLETE",
  "sign_off_date": "YYYY-MM-DD"
}
```
