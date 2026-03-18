# Prompt 04 — API Interface

## Goal
Implement a thin FastAPI adapter that delegates directly to the service layer.

## Inputs
- `docs/TOOL_TEMPLATE_SOT.md`
- `api/schemas.py`
- `core/service.py`

## Requirements
- Router must declare resource-level prefix only (for example `router = APIRouter(prefix="/items", tags=["items"])`).
- Do not hardcode platform prefixes such as `/v1/tools/...` in tool routers.
- Platform mounting owns the tool prefix. Example final path: `/v1/tools/<tool-name>/items`.
- Call service layer directly with no duplicated logic.
- Map `PermissionError` to HTTP 403.
- Map `ValueError` containing `not found` to HTTP 404.
- Map other `ValueError` to HTTP 400.
- Keep API as a thin adapter only.
- Ensure API response semantics match CLI outputs for equivalent logical inputs.
- Add or update `tests/test_api_smoke.py` for basic route behavior.

## Checkpoint
- `tests/test_api_smoke.py` passes for success and error mapping paths.
