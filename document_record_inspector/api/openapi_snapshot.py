"""document_record_inspector.api.openapi_snapshot — OpenAPI snapshot generator.

Usage:
    python -m document_record_inspector.api.openapi_snapshot

Writes a deterministic JSON snapshot to <repo-root>/openapi.snapshot.json.
No TechVault imports. No sys.path manipulation.
"""
from __future__ import annotations

import json
from pathlib import Path

from fastapi import FastAPI

import document_record_inspector.api.router as _router_module


def build_app() -> FastAPI:
    """Create a minimal FastAPI app with only the document_record_inspector router."""
    app = FastAPI(title="document_record_inspector")
    app.include_router(_router_module.router)
    return app


def generate_openapi() -> dict:
    """Return the live OpenAPI schema dict."""
    return build_app().openapi()


def _repo_root() -> Path:
    """Walk up from this file until pyproject.toml is found."""
    current = Path(__file__).resolve().parent
    while current != current.parent:
        if (current / "pyproject.toml").exists():
            return current
        current = current.parent
    raise RuntimeError("Could not locate repo root (no pyproject.toml found)")


def main() -> None:
    schema = generate_openapi()
    snapshot_path = _repo_root() / "openapi.snapshot.json"
    with snapshot_path.open("w", encoding="utf-8") as f:
        json.dump(schema, f, indent=2, sort_keys=True, ensure_ascii=False)
        f.write("\n")
    print("Wrote openapi.snapshot.json")


if __name__ == "__main__":
    main()
