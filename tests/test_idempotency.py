import pytest


@pytest.mark.skip(reason="Implement idempotency tests: lookup -> insert -> IntegrityError -> reload flow.")
def test_idempotent_create_flow() -> None:
    raise NotImplementedError
