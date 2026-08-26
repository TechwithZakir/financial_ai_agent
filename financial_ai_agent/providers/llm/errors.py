from __future__ import annotations

from financial_ai_agent.ai.exceptions import (
    AIContextLimitError,
    AIModelNotFoundError,
    AIProviderAuthenticationError,
    AIProviderRateLimitError,
    AIProviderTimeoutError,
    AIProviderUnavailableError,
)


def translate_provider_error(exc: Exception) -> Exception:
    name = exc.__class__.__name__.lower()
    text = str(exc).lower()
    if "authentication" in name or "unauthorized" in text or "api key" in text:
        return AIProviderAuthenticationError("AI provider authentication failed")
    if "ratelimit" in name or "rate limit" in text or "429" in text:
        return AIProviderRateLimitError("AI provider rate limit exceeded")
    if "timeout" in name or "timed out" in text:
        return AIProviderTimeoutError("AI provider request timed out")
    if "notfound" in name or "model not found" in text:
        return AIModelNotFoundError("Configured AI model was not found")
    if "context" in text and ("limit" in text or "length" in text):
        return AIContextLimitError("AI model context limit exceeded")
    return AIProviderUnavailableError("AI provider is unavailable")

