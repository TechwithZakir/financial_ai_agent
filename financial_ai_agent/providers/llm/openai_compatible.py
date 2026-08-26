from __future__ import annotations

import json

from openai import OpenAI

from financial_ai_agent.ai.contracts import AIRequest, AIResponse, AIUsage, ToolCall
from financial_ai_agent.ai.exceptions import AIInvalidResponseError
from financial_ai_agent.providers.llm.base import BaseAIProvider
from financial_ai_agent.providers.llm.errors import translate_provider_error


class OpenAICompatibleProvider(BaseAIProvider):
    provider_type = "OpenAI Compatible"

    def __init__(self, provider_doc):
        super().__init__(provider_doc)
        key = provider_doc.get_password("api_key", raise_exception=False) or "local-no-key"
        kwargs = {
            "api_key": key,
            "timeout": max(5, int(provider_doc.timeout or 60)),
            "max_retries": 0,
        }
        if provider_doc.base_url:
            kwargs["base_url"] = provider_doc.base_url.rstrip("/")
        self.client = OpenAI(**kwargs)

    def generate(self, request: AIRequest) -> AIResponse:
        messages = list(request.messages)
        if request.system_instruction:
            messages.insert(0, {"role": "system", "content": request.system_instruction})
        payload = {
            "model": request.model,
            "messages": messages,
            "max_completion_tokens": request.max_output_tokens,
        }
        if request.temperature is not None:
            payload["temperature"] = request.temperature
        if request.tools:
            payload["tools"] = [
                {"type": "function", "function": tool} for tool in request.tools
            ]
            payload["tool_choice"] = "auto"
        if request.response_schema:
            payload["response_format"] = {
                "type": "json_schema",
                "json_schema": {"name": "financial_ai_response", "schema": request.response_schema},
            }
        try:
            result = self.client.chat.completions.create(**payload)
        except Exception as exc:
            raise translate_provider_error(exc) from exc
        if not result.choices:
            raise AIInvalidResponseError("The provider returned no choices")
        choice = result.choices[0]
        message = choice.message
        calls = []
        for call in message.tool_calls or []:
            try:
                arguments = json.loads(call.function.arguments or "{}")
            except (TypeError, ValueError) as exc:
                raise AIInvalidResponseError("The provider returned invalid tool arguments") from exc
            calls.append(ToolCall(id=call.id, name=call.function.name, arguments=arguments))
        structured = None
        if request.response_schema and message.content:
            try:
                structured = json.loads(message.content)
            except ValueError as exc:
                raise AIInvalidResponseError("The provider returned invalid structured output") from exc
        usage = result.usage
        return AIResponse(
            text=message.content or "",
            model=result.model or request.model,
            provider=self.config.name,
            tool_calls=calls,
            structured_output=structured,
            usage=AIUsage(
                input_tokens=getattr(usage, "prompt_tokens", 0) or 0,
                output_tokens=getattr(usage, "completion_tokens", 0) or 0,
                cached_tokens=getattr(
                    getattr(usage, "prompt_tokens_details", None), "cached_tokens", 0
                ) or 0,
            ),
            finish_reason=choice.finish_reason,
        )

    def embed(self, texts: list[str], model: str) -> list[list[float]]:
        try:
            response = self.client.embeddings.create(model=model, input=texts)
        except Exception as exc:
            raise translate_provider_error(exc) from exc
        return [item.embedding for item in response.data]

    def test_connection(self) -> dict:
        try:
            self.client.models.list()
        except Exception as exc:
            raise translate_provider_error(exc) from exc
        return {"ok": True, "provider": self.config.name}

    def capabilities(self) -> set[str]:
        return {"chat", "tools", "structured_output", "embeddings"}

