"""CLI smoke tests for document_record_inspector.

All tests run in standalone mode (no DATABASE_URL).  In this mode:
- ``health`` always returns {"status":"ok"}
- ``inspect`` returns a valid empty response with document=null
"""
from __future__ import annotations

import json
import subprocess
import sys

PYTHON = sys.executable
CLI = [PYTHON, "-m", "document_record_inspector.cli"]


def _run(args: list[str], env: dict | None = None) -> subprocess.CompletedProcess:
    import os  # noqa: PLC0415

    run_env = dict(os.environ)
    if env:
        run_env.update(env)
    # Ensure no DATABASE_URL leaks into standalone test
    run_env.pop("DATABASE_URL", None)
    return subprocess.run(
        CLI + args,
        capture_output=True,
        text=True,
        env=run_env,
    )


# ---------------------------------------------------------------------------
# health
# ---------------------------------------------------------------------------


def test_health_exits_zero() -> None:
    result = _run(["health"])
    assert result.returncode == 0, result.stderr


def test_health_stdout_is_valid_json() -> None:
    result = _run(["health"])
    data = json.loads(result.stdout)
    assert data["status"] == "ok"


def test_health_no_stderr() -> None:
    result = _run(["health"])
    assert result.stderr == ""


def test_health_byte_identical_on_repeat() -> None:
    r1 = _run(["health"]).stdout
    for _ in range(4):
        assert _run(["health"]).stdout == r1


def test_health_no_traceback_in_stderr() -> None:
    result = _run(["health"])
    assert "Traceback" not in result.stderr


# ---------------------------------------------------------------------------
# inspect -- standalone mode (no DATABASE_URL)
# ---------------------------------------------------------------------------


def test_inspect_exits_zero() -> None:
    result = _run(["inspect", "--document-id", "test-doc-id"])
    assert result.returncode == 0, result.stderr


def test_inspect_stdout_is_valid_json() -> None:
    result = _run(["inspect", "--document-id", "test-doc-id"])
    data = json.loads(result.stdout)
    assert "query" in data
    assert "document" in data
    assert "diagnostics" in data


def test_inspect_document_null_in_standalone() -> None:
    result = _run(["inspect", "--document-id", "test-doc-id"])
    data = json.loads(result.stdout)
    assert data["document"] is None


def test_inspect_query_echoes_document_id() -> None:
    doc_id = "my-unique-doc-id"
    result = _run(["inspect", "--document-id", doc_id])
    data = json.loads(result.stdout)
    assert data["query"]["document_id"] == doc_id


def test_inspect_byte_identical_on_repeat() -> None:
    r1 = _run(["inspect", "--document-id", "repeat-doc-id"]).stdout
    for _ in range(4):
        assert _run(["inspect", "--document-id", "repeat-doc-id"]).stdout == r1


def test_inspect_no_traceback_in_stderr() -> None:
    result = _run(["inspect", "--document-id", "any-doc"])
    assert "Traceback" not in result.stderr


def test_inspect_missing_document_issue_present() -> None:
    result = _run(["inspect", "--document-id", "does-not-exist"])
    data = json.loads(result.stdout)
    assert "document_missing" in data["diagnostics"]["possible_issues"]


# ---------------------------------------------------------------------------
# CLI/API parity
# ---------------------------------------------------------------------------


def test_cli_api_parity_for_same_document_id() -> None:
    """CLI and API must return the same diagnostics for the same document_id in standalone mode."""
    from fastapi.testclient import TestClient  # noqa: PLC0415

    from document_record_inspector.api import deps  # noqa: PLC0415
    from document_record_inspector.api.openapi_snapshot import build_app  # noqa: PLC0415

    doc_id = "parity-check-doc-id"

    app = build_app()
    app.dependency_overrides[deps.get_db] = lambda: None
    api_data = TestClient(app).get(f"/records/{doc_id}").json()

    cli_result = _run(["inspect", "--document-id", doc_id])
    cli_data = json.loads(cli_result.stdout)

    # Diagnostics must match
    assert api_data["diagnostics"] == cli_data["diagnostics"]
    assert api_data["document"] == cli_data["document"]

