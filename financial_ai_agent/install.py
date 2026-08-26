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

