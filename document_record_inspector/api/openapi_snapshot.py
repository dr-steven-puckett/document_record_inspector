"""document_record_inspector.api.openapi_snapshot — deterministic OpenAPI schema generator.

Used by the snapshot test and by tooling that needs to introspect the schema
without starting a full server.
"""
from __future__ import annotations

from fastapi import FastAPI

from .router import router


def build_app() -> FastAPI:
    """Build a minimal FastAPI application with the inspector router mounted."""
    app = FastAPI(
        title="document_record_inspector",
        version="0.1.0",
        description="Deterministic forensic inspection of a single TechVault document record.",
    )
    app.include_router(router)
    return app


def generate_openapi() -> dict:
    """Generate and return the OpenAPI schema dict deterministically."""
    return build_app().openapi()

