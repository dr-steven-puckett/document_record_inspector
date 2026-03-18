from __future__ import annotations

from dataclasses import dataclass

try:
    from sqlalchemy.exc import IntegrityError
except Exception:  # pragma: no cover - SQLAlchemy may not be installed in early scaffold stage
    class IntegrityError(Exception):
        pass


ALLOWED_SECURITY_LEVELS = {
    "public",
    "internal",
    "confidential",
    "secret",
}


@dataclass(frozen=True)
class ServiceContext:
    security_level: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "security_level", validate_security_level(self.security_level))


def validate_security_level(value: str) -> str:
    normalized = value.strip().lower()
    if normalized not in ALLOWED_SECURITY_LEVELS:
        raise ValueError(f"Invalid security_level: {value}")
    return normalized


def health_service() -> dict[str, str]:
    return {"status": "ok"}


def create_with_idempotency(
    *,
    idempotency_key: str,
    lookup_by_idempotency_key,
    insert_row,
) -> object:
    if not idempotency_key:
        raise ValueError("idempotency_key is required")

    # Required deterministic flow for concurrent create paths:
    # 1) lookup existing, 2) insert attempt, 3) catch IntegrityError,
    # 4) reload canonical row, 5) return canonical row.
    existing = lookup_by_idempotency_key(idempotency_key)
    if existing is not None:
        return existing

    try:
        return insert_row(idempotency_key)
    except IntegrityError:
        canonical = lookup_by_idempotency_key(idempotency_key)
        if canonical is None:
            raise ValueError("Idempotent create conflict without canonical row")
        return canonical
