# Phase 08 — CLI Smoke Tests (subprocess)

## Goal

End-to-end subprocess tests for the CLI.  All tests use `--catalog-file` (fixture mode)
so no `DATABASE_URL` is needed.

## Pattern

```python
import subprocess, sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
PYTHON = sys.executable
FIXTURE = "tests/fixtures/sample_record.json"

def _run(args):
    return subprocess.run(
        [PYTHON, "-m", "document_record_inspector.cli.main"] + args,
        capture_output=True, text=True, cwd=REPO_ROOT,
    )
```

## Required Test Cases

| Subcommand + flags | Exit code | stdout | stderr |
|---|---|---|---|
| `health` | 0 | valid JSON `{"status":"ok",...}` | empty |
| `health` (twice) | 0 | byte-identical | — |
| `inspect --document-id DOC_ID --catalog-file FIXTURE` | 0 | valid JSON, all 7 keys | empty |
| `inspect` (twice) | 0 | byte-identical | — |
| `inspect --include-text` | 0 | at least one chunk.text non-null | — |
| `inspect --include-vectors` | 0 | at least one embedding.vector non-null | — |
| Chunks sorted by index | — | indexes == sorted(indexes) | — |
| Files sorted by role | — | roles == sorted(roles) | — |
| `inspect --document-id MISSING --catalog-file FIXTURE` | non-zero | empty | non-empty |
| `inspect --document-id "" --catalog-file FIXTURE` | non-zero | empty | non-empty |

## Validation

```bash
pytest tests/test_cli_smoke.py -q
```
