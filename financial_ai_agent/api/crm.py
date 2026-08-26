import frappe

from financial_ai_agent.api.chat import _require_user
from financial_ai_agent.providers.crm.registry import get_crm_provider


def _salesforce_api():
    if "salesforce_mcp_ai" not in frappe.get_installed_apps():
        frappe.throw("Salesforce MCP AI is not installed on this site")
    from salesforce_mcp_ai.api import auth as salesforce_auth
    return salesforce_auth


@frappe.whitelist()
def test_connection(connector: str):
    _require_user()
    if not {"Financial AI Manager", "System Manager"}.intersection(frappe.get_roles()):
        frappe.throw("Manager role required", frappe.PermissionError)
    doc = frappe.get_doc("CRM Connector", connector)
    doc.check_permission("write")
    if not doc.enabled:
        frappe.throw("CRM Connector is disabled")
    return get_crm_provider(doc).test_connection()


@frappe.whitelist()
def salesforce_status():
    _require_user()
    if "salesforce_mcp_ai" not in frappe.get_installed_apps():
        return {"installed": False, "connected": False,
                "message": "Salesforce MCP AI is not installed"}
    try:
        result = _salesforce_api().get_connection_status()
        result["installed"] = True
        return result
    except frappe.PermissionError:
        return {"installed": True, "connected": False,
                "message": "Assign Salesforce MCP User or Salesforce MCP Manager to connect"}


@frappe.whitelist()
def start_salesforce_oauth():
    _require_user()
    return _salesforce_api().start_salesforce_oauth()


@frappe.whitelist()
def disconnect_salesforce():
    _require_user()
    return _salesforce_api().disconnect_salesforce()
