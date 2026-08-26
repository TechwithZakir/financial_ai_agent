import frappe

from financial_ai_agent.api.chat import _require_user
from financial_ai_agent.providers.crm.registry import get_crm_provider


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

