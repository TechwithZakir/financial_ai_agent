from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ResponseBlock(BaseModel):
    type: str
    title: str | None = None
    data: Any


class RichResponse(BaseModel):
    summary: str
    blocks: list[ResponseBlock] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    sources: list[dict[str, Any]] = Field(default_factory=list)
    actions: list[dict[str, Any]] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    def add(self, block_type: str, data: Any, title: str | None = None) -> "RichResponse":
        self.blocks.append(ResponseBlock(type=block_type, title=title, data=data))
        return self

