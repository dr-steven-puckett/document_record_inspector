# TechVault Security Model

This document defines the canonical security vocabulary for TechVault tools.

## Canonical Security Levels

Use exactly this set:

- `public`
- `internal`
- `confidential`
- `secret`

No alternate labels are allowed. In particular, do not introduce values such as `protected`.

## Consistency Requirement

When a tool supports security-level classification, all layers must agree on the same vocabulary and semantics:

- `tool.toml` policy/configuration fields
- API schemas and validation enums
- service-layer validation logic
- DB constraints (for persisted records)
- docs and examples

If any layer diverges from the canonical set, the tool is non-compliant.

## Validation Requirement

For tools that accept or persist security-level values, enforce validation in three places:

1. Schema validation where appropriate.
2. Service-layer validation always (required before persistence).
3. DB-level constraint when persistence exists.

Service-layer validation is mandatory even when schema and DB constraints are present.

## Service-Layer Reference Pattern

```python
ALLOWED_SECURITY_LEVELS = {
    "public",
    "internal",
    "confidential",
    "secret",
}


def validate_security_level(value: str) -> str:
    normalized = value.strip().lower()
    if normalized not in ALLOWED_SECURITY_LEVELS:
        raise ValueError(f"Invalid security_level: {value}")
    return normalized
```

Use this pattern (or equivalent deterministic logic) in `core/service.py` before any write path.