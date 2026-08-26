from __future__ import annotations

import frappe

from financial_ai_agent.ai.orchestrator import FinancialAIOrchestrator


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
         model: str | None = None, classification: str = "Internal"):
    user = _require_user()
    message = (message or "").strip()
    if not message or len(message) > 20000:
        frappe.throw("Message must contain between 1 and 20,000 characters")
    try:
        return FinancialAIOrchestrator(agent, user).run(message, session, model, classification)
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

