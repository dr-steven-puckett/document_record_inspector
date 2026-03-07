# Phase 09 — Platform Registration

## Goal

Register `document_record_inspector` with the TechVault platform so it is
available via the HTTP API and the agent tool registry.

## Steps

### 1. Add git submodule

```bash
cd ~/projects/techvault/backend
git submodule add <REPO_URL> tools/document_record_inspector
git submodule update --init --recursive
```

### 2. Install the package

```bash
cd ~/projects/techvault/backend
pip install -e tools/document_record_inspector
```

### 3. Enable in platform config

Edit `~/projects/techvault/backend/platform/enabled_tools.toml`:

```toml
enabled = [
    "catalog_search",
    "notemanager",
    "taskmanager",
    "document_catalog_query",
    "document_record_inspector",   # ← add this line
]
```

### 4. Verify manifest loading

```python
from platform.tool_manifests import load_tool_manifest
m = load_tool_manifest("document_record_inspector")
assert m.name == "document_record_inspector"
assert m.requires_db is True
```

### 5. Restart API server

```bash
# Stop existing server, then:
uvicorn techvault.main:app --reload
```

### 6. Smoke test

```bash
curl http://localhost:8000/v1/tools/document_record_inspector/health
# Expected: {"status":"ok","tool_id":"document_record_inspector"}
```

## Rollback

To disable without removing:
- Remove `"document_record_inspector"` from `enabled_tools.toml`
- Restart server
