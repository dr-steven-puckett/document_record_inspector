"""document_record_inspector.api.deps — FastAPI dependency stubs.

In standalone / test mode ``get_db`` yields ``None``.  The TechVault platform
overrides this via the ``[[techvault.adapters]]`` entry in ``tool.toml`` by
substituting a real SQLAlchemy Session from the shared database.
"""
from __future__ import annotations

from collections.abc import Generator


def get_db() -> Generator[None, None, None]:
    """Yield ``None`` in standalone mode.

    Replaced at runtime by the platform adapter that yields a TechVault DB
    session.  Tests override this dependency via
    ``app.dependency_overrides[get_db]``.
    """
    yield None

