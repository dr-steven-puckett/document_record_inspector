# Phase 00 — Scaffold Repository

## Goal

Create the complete repository skeleton for `document_record_inspector` following the
TechVault Tool Factory v2.0.0 template.

## Reference

Use `document_catalog_query` as the canonical pattern reference.
Template location: `~/projects/tools/techvault_tool_template/`

## Deliverables

1. `tool.toml` with sections: `[tool]`, `[api]`, `[agent_tool]`, `[policy]`, `[capabilities]`, `[template]`
2. `pyproject.toml` with entry_points and all runtime + test deps
3. `pytest.ini` pointing at `tests/`
4. `README.md` with tool overview
5. `TEMPLATE_MANIFEST.json` tracking all required files
6. `openapi.snapshot.json` — placeholder `{}`
7. Package `__init__.py` files:
   - `document_record_inspector/__init__.py`
   - `document_record_inspector/api/__init__.py`
   - `document_record_inspector/core/__init__.py`
   - `document_record_inspector/cli/__init__.py`
   - `tests/__init__.py`

## key Values

```toml
[tool]
name = "document_record_inspector"

[api]
router_import = "document_record_inspector.api.router:router"
mount_prefix = ""

[policy]
requires_db = true
```

## Validation

- `find . -name "*.py" -path "*/document_record_inspector/*"` shows all package files
- `python -c "import document_record_inspector"` exits 0 after `pip install -e .`
