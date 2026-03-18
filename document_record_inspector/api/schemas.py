from __future__ import annotations

from pydantic import BaseModel, Field


class ItemCreateRequest(BaseModel):
    name: str = Field(min_length=1)
    idempotency_key: str = Field(min_length=1)
    security_level: str = Field(min_length=1)


class ItemResponse(BaseModel):
    item_id: str
    name: str
    security_level: str
