from __future__ import annotations

from typing import Any

TOOL_SPEC: dict[str, Any] = {
    "name": "document_record_inspector",
    "description": "Agent callable contract for document_record_inspector.",
}


def run(*_args: Any, **_kwargs: Any) -> dict[str, Any]:
    raise NotImplementedError("Agent mode is disabled by default")
