from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterator

from financial_ai_agent.ai.contracts import AIRequest, AIResponse, StreamEvent
from financial_ai_agent.ai.exceptions import AICapabilityNotSupportedError


class BaseAIProvider(ABC):
    provider_type: str

    def __init__(self, provider_doc):
        self.config = provider_doc

    @abstractmethod
    def generate(self, request: AIRequest) -> AIResponse:
        raise NotImplementedError

    def generate_structured(self, request: AIRequest) -> AIResponse:
        if not request.response_schema:
            raise ValueError("response_schema is required")
        return self.generate(request)

    def stream(self, request: AIRequest) -> Iterator[StreamEvent]:
        raise AICapabilityNotSupportedError(f"{self.provider_type} does not support streaming")

    def embed(self, texts: list[str], model: str) -> list[list[float]]:
        raise AICapabilityNotSupportedError(f"{self.provider_type} does not support embeddings")

    @abstractmethod
    def test_connection(self) -> dict:
        raise NotImplementedError

    def capabilities(self) -> set[str]:
        return set()

