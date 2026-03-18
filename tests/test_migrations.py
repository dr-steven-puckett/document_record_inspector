import pytest


@pytest.mark.skip(reason="DB-backed tools only: verify alembic upgrade head / downgrade base.")
def test_migration_smoke() -> None:
    raise NotImplementedError
