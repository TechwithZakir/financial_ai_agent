import frappe

from financial_ai_agent.providers.llm.registry import get_provider


@frappe.whitelist()
def test_connection(provider: str):
    if not {"Financial AI Manager", "System Manager"}.intersection(frappe.get_roles()):
        frappe.throw("Not permitted", frappe.PermissionError)
    doc = frappe.get_doc("AI Provider", provider)
    doc.check_permission("write")
    return get_provider(doc).test_connection()

