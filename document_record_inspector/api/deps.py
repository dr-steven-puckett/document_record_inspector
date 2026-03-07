"""document_record_inspector.api.deps — FastAPI dependencies.

Provides:
  get_db() — yields a SQLAlchemy Session (engine cached at module scope)

No TechVault platform imports. Host applications may override get_db()
when mounting the router into their own FastAPI app.
"""
from __future__ import annotations

import os
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

_engine = None
_SessionLocal = None


def _get_engine():
    global _engine, _SessionLocal
    if _engine is None:
        url = os.environ.get("DATABASE_URL")
        if not url:
            raise RuntimeError(
                "DATABASE_URL environment variable is not set. "
                "Export it before starting document_record_inspector, e.g.:\n"
                "  export DATABASE_URL=postgresql+psycopg://user:pass@host/db"
            )
        _engine = create_engine(url, pool_pre_ping=True)
        _SessionLocal = sessionmaker(bind=_engine, expire_on_commit=False)
    return _engine, _SessionLocal


def get_db() -> Generator[Session, None, None]:
    """Yield a database session; close it when the request is done."""
    _, SessionLocal = _get_engine()
    assert SessionLocal is not None
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
