from __future__ import annotations

from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field


class DataClassification(str, Enum):
    PUBLIC = "Public"
    INTERNAL = "Internal"
    CONFIDENTIAL = "Confidential"
    SENSITIVE_FINANCIAL = "Sensitive Financial Data"
    PII = "PII"


class ToolCall(BaseModel):
    id: str
    name: str
    arguments: dict[str, Any] = Field(default_factory=dict)


class AIUsage(BaseModel):
    input_tokens: int = 0
    output_tokens: int = 0
    cached_tokens: int = 0


class AIRequest(BaseModel):
    messages: list[dict[str, Any]]
    model: str
    system_instruction: str = ""
    tools: list[dict[str, Any]] = Field(default_factory=list)
    response_schema: dict[str, Any] | None = None
    temperature: float = 0.2
    max_output_tokens: int = 4000
    correlation_id: str
    data_classification: DataClassification = DataClassification.INTERNAL
    timeout: float = 60


class AIResponse(BaseModel):
    text: str = ""
    model: str
    provider: str
    tool_calls: list[ToolCall] = Field(default_factory=list)
    structured_output: dict[str, Any] | None = None
    usage: AIUsage = Field(default_factory=AIUsage)
    finish_reason: str | None = None
    raw_reference: str | None = None


class StreamEvent(BaseModel):
    type: Literal[
        "text_delta", "tool_call_started", "tool_call_completed", "response_completed", "error"
    ]
    data: dict[str, Any] = Field(default_factory=dict)

