import frappe


def execute():
    old_name = "Local Frappe CRM Demo"
    new_name = "Local ERPNext CRM Demo"
    if frappe.db.exists("CRM Connector", old_name) and not frappe.db.exists("CRM Connector", new_name):
        frappe.rename_doc("CRM Connector", old_name, new_name, force=True)
    if frappe.db.exists("CRM Connector", new_name):
        frappe.db.set_value(
            "CRM Connector", new_name, "connector_name", new_name, update_modified=False
        )
    frappe.db.set_value(
        "CRM Connector",
        {"crm_type": "Frappe CRM"},
        "crm_type",
        "ERPNext CRM",
        update_modified=False,
    )
