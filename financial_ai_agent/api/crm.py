import frappe

from financial_ai_agent.api.chat import _require_user
from financial_ai_agent.providers.crm.registry import get_crm_provider


@frappe.whitelist()
def test_connection(connector: str):
    _require_user()
    doc = frappe.get_doc("CRM Connector", connector)
    if not doc.enabled:
        frappe.throw("CRM Connector is disabled")
    try:
        return get_crm_provider(doc).test_connection()
    except ValueError as exc:
        return {"ok": False, "message": str(exc), "crm_type": doc.crm_type}


@frappe.whitelist()
def available_connectors():
    _require_user()
    return frappe.get_all(
        "CRM Connector", filters={"enabled": 1},
        fields=["name", "connector_name", "crm_type", "mode", "is_default",
                "read_enabled", "create_enabled", "update_enabled"],
        order_by="is_default desc, connector_name asc",
    )


@frappe.whitelist()
def salesforce_status(connector: str):
    from financial_ai_agent.api.salesforce import get_connection_status
    return get_connection_status(connector)


@frappe.whitelist()
def start_salesforce_oauth(connector: str):
    from financial_ai_agent.api.salesforce import start_oauth
    return start_oauth(connector)


@frappe.whitelist()
def disconnect_salesforce(connector: str):
    from financial_ai_agent.api.salesforce import disconnect
    return disconnect(connector)
