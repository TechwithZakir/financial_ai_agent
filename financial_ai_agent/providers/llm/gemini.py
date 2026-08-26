from __future__ import annotations

from urllib.parse import quote

import httpx

from financial_ai_agent.ai.contracts import AIRequest, AIResponse, AIUsage, ToolCall
from financial_ai_agent.ai.exceptions import AIInvalidResponseError
from financial_ai_agent.providers.llm.base import BaseAIProvider
from financial_ai_agent.providers.llm.errors import translate_provider_error


class GeminiProvider(BaseAIProvider):
    provider_type = "Google Gemini"

    def generate(self, request: AIRequest) -> AIResponse:
        base = self.config.base_url or "https://generativelanguage.googleapis.com/v1beta"
        url = f"{base.rstrip('/')}/models/{quote(request.model, safe='')}:generateContent"
        contents = []
        for message in request.messages:
            role = "model" if message.get("role") == "assistant" else "user"
            contents.append({"role": role, "parts": [{"text": str(message.get("content", ""))}]})
        payload = {"contents": contents, "generationConfig": {
            "temperature": request.temperature, "maxOutputTokens": request.max_output_tokens}}
        if request.system_instruction:
            payload["systemInstruction"] = {"parts": [{"text": request.system_instruction}]}
        if request.tools:
            payload["tools"] = [{"functionDeclarations": request.tools}]
        try:
            response = httpx.post(url, headers={"x-goog-api-key": self.config.get_password("api_key"),
                                                "content-type": "application/json"},
                                  json=payload, timeout=request.timeout)
            response.raise_for_status()
            data = response.json()
            candidate = data["candidates"][0]
            parts = candidate["content"]["parts"]
        except Exception as exc:
            raise translate_provider_error(exc) from exc
        if not isinstance(parts, list):
            raise AIInvalidResponseError("Gemini returned invalid content")
        calls, text = [], []
        for part in parts:
            if "functionCall" in part:
                call = part["functionCall"]
                calls.append(ToolCall(id=call.get("id", ""), name=call["name"], arguments=call.get("args") or {}))
            elif part.get("text"):
                text.append(part["text"])
        usage = data.get("usageMetadata") or {}
        return AIResponse(text="\n".join(text), model=request.model, provider=self.config.name,
                          tool_calls=calls, usage=AIUsage(input_tokens=usage.get("promptTokenCount", 0),
                          output_tokens=usage.get("candidatesTokenCount", 0)),
                          finish_reason=candidate.get("finishReason"))

    def test_connection(self) -> dict:
        return {"ok": bool(self.config.get_password("api_key", raise_exception=False)), "provider": self.config.name}

    def capabilities(self) -> set[str]:
        return {"chat", "tools", "vision", "structured_output", "embeddings"}

