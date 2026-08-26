from __future__ import annotations

from typing import Type

from financial_ai_agent.providers.llm.base import BaseAIProvider
from financial_ai_agent.providers.llm.openai_compatible import OpenAICompatibleProvider
from financial_ai_agent.providers.llm.anthropic import AnthropicProvider
from financial_ai_agent.providers.llm.gemini import GeminiProvider

_PROVIDERS: dict[str, Type[BaseAIProvider]] = {
    "OpenAI": OpenAICompatibleProvider,
    "Anthropic": AnthropicProvider,
    "Google Gemini": GeminiProvider,
    "OpenAI Compatible": OpenAICompatibleProvider,
    "Alibaba Qwen": OpenAICompatibleProvider,
    "Hosted AI": OpenAICompatibleProvider,
}


def register_provider(provider_type: str, provider_class: Type[BaseAIProvider]) -> None:
    if not issubclass(provider_class, BaseAIProvider):
        raise TypeError("provider_class must inherit BaseAIProvider")
    _PROVIDERS[provider_type] = provider_class


def get_provider(provider_doc) -> BaseAIProvider:
    try:
        provider_class = _PROVIDERS[provider_doc.provider_type]
    except KeyError as exc:
        raise ValueError(f"Unsupported AI provider type: {provider_doc.provider_type}") from exc
    return provider_class(provider_doc)
