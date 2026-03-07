"""test_cli_smoke — subprocess smoke tests for the CLI entry point.

Tests run the CLI as a subprocess so the argparse layer, _emit(), and
_die() are all exercised exactly as end users would see them.  No
DATABASE_URL is needed because tests pass --catalog-file.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
PYTHON = sys.executable
FIXTURE = "tests/fixtures/sample_record.json"
DOC_ID = "aaaa1111bbbb2222cccc3333dddd4444eeee5555ffff6666aaaa1111bbbb2222"
MISSING_ID = "0000000000000000000000000000000000000000000000000000000000000000"


def _run(args: list[str], env: dict | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        [PYTHON, "-m", "document_record_inspector.cli.main"] + args,
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        env=env,
    )


# ---------------------------------------------------------------------------
# health
# ---------------------------------------------------------------------------


def test_health_exits_0():
    result = _run(["health"])
    assert result.returncode == 0, result.stderr


def test_health_stdout_is_valid_json():
    result = _run(["health"])
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["status"] == "ok"


def test_health_no_stderr():
    result = _run(["health"])
    assert result.stderr == ""


def test_health_byte_identical_repeat():
    r1 = _run(["health"])
    r2 = _run(["health"])
    assert r1.stdout == r2.stdout


# ---------------------------------------------------------------------------
# inspect — success path
# ---------------------------------------------------------------------------


def test_inspect_exits_0():
    result = _run(["inspect", "--document-id", DOC_ID, "--catalog-file", FIXTURE])
    assert result.returncode == 0, result.stderr


def test_inspect_stdout_is_valid_json():
    result = _run(["inspect", "--document-id", DOC_ID, "--catalog-file", FIXTURE])
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert isinstance(data, dict)


def test_inspect_response_top_level_keys():
    result = _run(["inspect", "--document-id", DOC_ID, "--catalog-file", FIXTURE])
    data = json.loads(result.stdout)
    assert set(data.keys()) == {"document", "files", "chunks", "embeddings", "summaries", "ingest_runs", "counts"}


def test_inspect_document_id_matches():
    result = _run(["inspect", "--document-id", DOC_ID, "--catalog-file", FIXTURE])
    data = json.loads(result.stdout)
    assert data["document"]["document_id"] == DOC_ID


def test_inspect_no_stderr_on_success():
    result = _run(["inspect", "--document-id", DOC_ID, "--catalog-file", FIXTURE])
    assert result.stderr == ""


def test_inspect_byte_identical_repeat():
    r1 = _run(["inspect", "--document-id", DOC_ID, "--catalog-file", FIXTURE])
    r2 = _run(["inspect", "--document-id", DOC_ID, "--catalog-file", FIXTURE])
    assert r1.stdout == r2.stdout


# ---------------------------------------------------------------------------
# inspect — text / vector gating
# ---------------------------------------------------------------------------


def test_inspect_text_suppressed_by_default():
    result = _run(["inspect", "--document-id", DOC_ID, "--catalog-file", FIXTURE])
    data = json.loads(result.stdout)
    for chunk in data["chunks"]:
        assert chunk["text"] is None


def test_inspect_text_included_with_flag():
    result = _run(["inspect", "--document-id", DOC_ID, "--catalog-file", FIXTURE, "--include-text"])
    assert result.returncode == 0
    data = json.loads(result.stdout)
    texts = [c["text"] for c in data["chunks"]]
    assert any(t is not None for t in texts)


def test_inspect_vectors_suppressed_by_default():
    result = _run(["inspect", "--document-id", DOC_ID, "--catalog-file", FIXTURE])
    data = json.loads(result.stdout)
    for emb in data["embeddings"]:
        assert emb["vector"] is None


def test_inspect_vectors_included_with_flag():
    result = _run(["inspect", "--document-id", DOC_ID, "--catalog-file", FIXTURE, "--include-vectors"])
    assert result.returncode == 0
    data = json.loads(result.stdout)
    vectors = [e["vector"] for e in data["embeddings"]]
    assert any(v is not None for v in vectors)


# ---------------------------------------------------------------------------
# inspect — ordering
# ---------------------------------------------------------------------------


def test_inspect_chunks_sorted_by_chunk_index():
    result = _run(["inspect", "--document-id", DOC_ID, "--catalog-file", FIXTURE])
    data = json.loads(result.stdout)
    indexes = [c["chunk_index"] for c in data["chunks"]]
    assert indexes == sorted(indexes)


def test_inspect_files_sorted_by_role():
    result = _run(["inspect", "--document-id", DOC_ID, "--catalog-file", FIXTURE])
    data = json.loads(result.stdout)
    roles = [f["role"] for f in data["files"]]
    assert roles == sorted(roles)


# ---------------------------------------------------------------------------
# inspect — error path
# ---------------------------------------------------------------------------


def test_inspect_missing_doc_exits_nonzero():
    result = _run(["inspect", "--document-id", MISSING_ID, "--catalog-file", FIXTURE])
    assert result.returncode != 0


def test_inspect_missing_doc_stderr_not_empty():
    result = _run(["inspect", "--document-id", MISSING_ID, "--catalog-file", FIXTURE])
    assert len(result.stderr.strip()) > 0


def test_inspect_missing_doc_stdout_empty():
    result = _run(["inspect", "--document-id", MISSING_ID, "--catalog-file", FIXTURE])
    assert result.stdout.strip() == ""


def test_inspect_empty_document_id_exits_nonzero():
    result = _run(["inspect", "--document-id", "", "--catalog-file", FIXTURE])
    assert result.returncode != 0
