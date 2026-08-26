from __future__ import annotations

import random
import time

import frappe

from financial_ai_agent.ai.contracts import AIRequest, AIResponse
from financial_ai_agent.ai.exceptions import AIProviderError
from financial_ai_agent.providers.llm.registry import get_provider


class ModelRouter:
    def select_model(
        self, *, capability: str, classification: str, preferred_model: str | None = None
    ):
        filters = {"enabled": 1}
        if preferred_model:
            filters["name"] = preferred_model
        names = frappe.get_all("AI Model", filters=filters, pluck="name", order_by="priority asc")
        for name in names:
            model = frappe.get_doc("AI Model", name)
            capabilities = {value.strip() for value in (model.capabilities or "").split("\n") if value.strip()}
            allowed = {value.strip() for value in (model.allowed_data_classes or "").split("\n") if value.strip()}
            if capability in capabilities and (not allowed or classification in allowed):
                return model
        frappe.throw(
            f"No enabled AI model permits {capability} for {classification}",
            exc=frappe.ValidationError,
        )

    def generate(
        self, request: AIRequest, *, capability: str = "chat", preferred_model: str | None = None
    ) -> AIResponse:
        primary = self.select_model(
            capability=capability,
            classification=request.data_classification.value,
            preferred_model=preferred_model,
        )
        candidates = [primary]
        if primary.fallback_model:
            fallback = frappe.get_doc("AI Model", primary.fallback_model)
            if fallback.enabled:
                candidates.append(fallback)
        last_error = None
        for index, model in enumerate(candidates):
            provider_doc = frappe.get_doc("AI Provider", model.provider)
            provider = get_provider(provider_doc)
            routed_request = request.model_copy(update={"model": model.model_id})
            retries = max(0, min(int(provider_doc.retries or 0), 3))
            for attempt in range(retries + 1):
                try:
                    response = provider.generate(routed_request)
                    response.raw_reference = "fallback" if index else "primary"
                    return response
                except AIProviderError as exc:
                    last_error = exc
                    if attempt < retries:
                        time.sleep(min(2 ** attempt + random.random(), 4))
        raise last_error or RuntimeError("No AI provider could serve the request")

