from urllib.parse import quote

import frappe

from financial_ai_agent.api.chat import _require_user
from financial_ai_agent.services.salesforce_oauth import CONNECTION_DOCTYPE, SalesforceOAuthService


@frappe.whitelist()
def get_connection_status(connector: str):
    user = _require_user()
    name = frappe.db.exists(CONNECTION_DOCTYPE, {"frappe_user": user, "connector": connector})
    connection = frappe.get_doc(CONNECTION_DOCTYPE, name) if name else None
    return {"installed": True, "connected": bool(connection and connection.connected),
            "salesforce_username": connection.salesforce_username if connection else None,
            "instance_url": connection.salesforce_instance_url if connection else None}


@frappe.whitelist()
def start_oauth(connector: str):
    user = _require_user()
    return {"authorization_url": SalesforceOAuthService(connector).authorization_url(user)}


@frappe.whitelist(allow_guest=True)
def salesforce_callback(code=None, state=None, error=None, error_description=None):
    redirect = "/app/financial-ai-assistant"
    try:
        if error:
            raise RuntimeError(error_description or error)
        if not code or not state:
            raise RuntimeError("Salesforce returned an incomplete OAuth response.")
        state_data = SalesforceOAuthService.consume_state(state)
        service = SalesforceOAuthService(state_data["connector"])
        service.save_connection(state_data["user"], service.exchange_code(code, state_data["verifier"]))
        redirect += "?salesforce_connected=1"
    except Exception as exc:
        frappe.log_error(frappe.get_traceback(), "Financial AI Salesforce OAuth callback failed")
        redirect += f"?salesforce_error={quote(str(exc)[:300])}"
    frappe.local.response["type"] = "redirect"
    frappe.local.response["location"] = redirect


@frappe.whitelist()
def disconnect(connector: str):
    user = _require_user()
    name = frappe.db.exists(CONNECTION_DOCTYPE, {"frappe_user": user, "connector": connector})
    if name:
        frappe.delete_doc(CONNECTION_DOCTYPE, name, ignore_permissions=True)
        frappe.db.commit()
    return {"connected": False}
