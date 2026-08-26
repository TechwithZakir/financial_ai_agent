from __future__ import annotations

import httpx

from financial_ai_agent.ai.contracts import AIRequest, AIResponse, AIUsage, ToolCall
from financial_ai_agent.ai.exceptions import AIInvalidResponseError
from financial_ai_agent.providers.llm.base import BaseAIProvider
from financial_ai_agent.providers.llm.errors import translate_provider_error


class AnthropicProvider(BaseAIProvider):
    provider_type = "Anthropic"
    endpoint = "https://api.anthropic.com/v1/messages"

    def generate(self, request: AIRequest) -> AIResponse:
        payload = {"model": request.model, "messages": request.messages,
                   "max_tokens": request.max_output_tokens, "temperature": request.temperature}
        if request.system_instruction:
            payload["system"] = request.system_instruction
        if request.tools:
            payload["tools"] = [{"name": t["name"], "description": t.get("description", ""),
                                 "input_schema": t.get("parameters", {})} for t in request.tools]
        try:
            response = httpx.post(
                self.config.base_url or self.endpoint,
                headers={"x-api-key": self.config.get_password("api_key"),
                         "anthropic-version": "2023-06-01", "content-type": "application/json"},
                json=payload, timeout=request.timeout,
            )
            response.raise_for_status()
            data = response.json()
        except Exception as exc:
            raise translate_provider_error(exc) from exc
        if not isinstance(data.get("content"), list):
            raise AIInvalidResponseError("Anthropic returned invalid content")
        calls = [ToolCall(id=b["id"], name=b["name"], arguments=b.get("input") or {})
                 for b in data["content"] if b.get("type") == "tool_use"]
        text = "\n".join(b.get("text", "") for b in data["content"] if b.get("type") == "text")
        usage = data.get("usage") or {}
        return AIResponse(text=text, model=data.get("model") or request.model, provider=self.config.name,
                          tool_calls=calls, usage=AIUsage(input_tokens=usage.get("input_tokens", 0),
                          output_tokens=usage.get("output_tokens", 0)), finish_reason=data.get("stop_reason"))

    def test_connection(self) -> dict:
        return {"ok": bool(self.config.get_password("api_key", raise_exception=False)), "provider": self.config.name}

    def capabilities(self) -> set[str]:
        return {"chat", "tools", "vision", "structured_output"}

