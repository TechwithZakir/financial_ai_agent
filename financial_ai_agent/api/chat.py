from __future__ import annotations

import uuid

import frappe

from financial_ai_agent.ai.contracts import AIRequest, DataClassification
from financial_ai_agent.ai.orchestrator import FinancialAIOrchestrator
from financial_ai_agent.providers.llm.registry import get_provider


def _require_user() -> str:
    if frappe.session.user == "Guest":
        frappe.throw("Authentication required", frappe.AuthenticationError)
    if not {"Financial AI User", "Financial AI Manager", "System Manager"}.intersection(
        frappe.get_roles(frappe.session.user)
    ):
        frappe.throw("Financial AI role required", frappe.PermissionError)
    return frappe.session.user


@frappe.whitelist()
def chat(message: str, agent: str, session: str | None = None,
         model: str | None = None, classification: str = "Internal",
         crm_connector: str | None = None):
    user = _require_user()
    message = (message or "").strip()
    if not message or len(message) > 20000:
        frappe.throw("Message must contain between 1 and 20,000 characters")
    try:
        return FinancialAIOrchestrator(agent, user).run(
            message, session, model, classification, crm_connector=crm_connector
        )
    except frappe.ValidationError:
        raise
    except Exception:
        correlation = frappe.generate_hash(length=12)
        frappe.log_error(frappe.get_traceback(), f"Financial AI request failed {correlation}")
        frappe.throw(f"The AI request failed. Reference: {correlation}")


@frappe.whitelist()
def available_models(agent: str):
    _require_user()
    doc = frappe.get_doc("AI Agent", agent)
    if not doc.allow_user_model_selection:
        return []
    return frappe.get_all("AI Model", filters={"enabled": 1}, fields=["name", "provider", "capabilities"])


@frappe.whitelist()
def available_agents():
    _require_user()
    return frappe.get_all(
        "AI Agent", filters={"enabled": 1}, fields=["name", "description"], order_by="agent_name asc"
    )


@frappe.whitelist()
def test_agent_connection(agent: str):
    _require_user()
    agent_doc = frappe.get_doc("AI Agent", agent)
    if not agent_doc.enabled:
        return {"ok": False, "message": "The selected AI Agent is disabled."}
    if not agent_doc.default_model:
        return {"ok": False, "message": "The AI Agent has no default model."}
    model = frappe.get_doc("AI Model", agent_doc.default_model)
    if not model.enabled:
        return {"ok": False, "message": "The agent's default AI Model is disabled."}
    provider = frappe.get_doc("AI Provider", model.provider)
    if not provider.enabled:
        return {"ok": False, "message": "The model's AI Provider is disabled."}
    try:
        response = get_provider(provider).generate(AIRequest(
            messages=[{"role": "user", "content": "Reply OK."}],
            model=model.model_id,
            system_instruction="This is a connection health check. Reply only OK.",
            max_output_tokens=8,
            correlation_id=str(uuid.uuid4()),
            data_classification=DataClassification.PUBLIC,
        ))
        return {
            "ok": True,
            "agent": agent_doc.name,
            "provider": provider.provider_name,
            "model": model.model_id,
            "message": "AI provider and configured model responded successfully.",
        }
    except Exception:
        correlation = frappe.generate_hash(length=12)
        frappe.log_error(frappe.get_traceback(), f"AI connection test failed {correlation}")
        return {
            "ok": False,
            "provider": provider.provider_name,
            "model": model.model_id,
            "message": f"AI provider is unavailable. Reference: {correlation}",
        }
