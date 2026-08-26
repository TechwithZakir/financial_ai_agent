from __future__ import annotations

import frappe

ROLES = (
    "Financial AI User",
    "Financial AI Manager",
    "Financial AI Compliance Reviewer",
)


def after_install() -> None:
    for role_name in ROLES:
        if not frappe.db.exists("Role", role_name):
            frappe.get_doc(
                {"doctype": "Role", "role_name": role_name, "desk_access": 1}
            ).insert(ignore_permissions=True)


def after_migrate() -> None:
    """Ensure navigation artifacts are refreshed even when a prior Workspace exists."""
    frappe.reload_doc("financial_ai_agent", "page", "financial_ai_assistant", force=True)
    frappe.reload_doc("financial_ai_agent", "workspace", "financial_ai_agent", force=True)

