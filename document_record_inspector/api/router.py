from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ..core.service import ServiceContext, health_service


# Resource-level prefix only. TechVault platform mounts this router under
# /v1/tools/<tool-name>, so final paths become /v1/tools/<tool-name>/items.
router = APIRouter(prefix="/items", tags=["items"])


@router.get("/health")
def health() -> dict[str, str]:
    return health_service()


@router.get("")
def list_items(security_level: str = "internal") -> dict[str, object]:
    try:
        ctx = ServiceContext(security_level=security_level)
        return {"items": [], "meta": {"security_level": ctx.security_level}}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
