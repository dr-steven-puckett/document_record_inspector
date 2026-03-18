from __future__ import annotations

from fastapi import FastAPI

from .router import router


def build_app() -> FastAPI:
    app = FastAPI(title="TechVault Tool")
    app.include_router(router)
    return app


def generate_openapi() -> dict[str, object]:
    return build_app().openapi()
