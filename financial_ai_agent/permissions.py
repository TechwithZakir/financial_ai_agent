from __future__ import annotations

import frappe

MANAGER_ROLES = {"System Manager", "Financial AI Manager", "Financial AI Compliance Reviewer"}


def _is_manager(user: str) -> bool:
    return bool(MANAGER_ROLES.intersection(frappe.get_roles(user)))


def _owned_query(user: str | None, field: str) -> str:
    user = user or frappe.session.user
    if _is_manager(user):
        return ""
    return f"`tab{{doctype}}`.`{field}` = {frappe.db.escape(user)}"


def session_query(user=None):
    return _owned_query(user, "user").format(doctype="AI Agent Session")


def message_query(user=None):
    user = user or frappe.session.user
    if _is_manager(user):
        return ""
    escaped = frappe.db.escape(user)
    return (
        "exists (select 1 from `tabAI Agent Session` s "
        f"where s.name=`tabAI Message`.session and s.user={escaped})"
    )


def approval_query(user=None):
    return _owned_query(user, "requested_by").format(doctype="AI Approval Request")


def usage_query(user=None):
    return _owned_query(user, "user").format(doctype="AI Usage Log")


def _owned_permission(doc, user: str | None, field: str) -> bool:
    user = user or frappe.session.user
    return _is_manager(user) or getattr(doc, field, None) == user


def session_permission(doc, user=None, **kwargs):
    return _owned_permission(doc, user, "user")


def message_permission(doc, user=None, **kwargs):
    user = user or frappe.session.user
    if _is_manager(user):
        return True
    return frappe.db.get_value("AI Agent Session", doc.session, "user") == user


def approval_permission(doc, user=None, **kwargs):
    return _owned_permission(doc, user, "requested_by")


def usage_permission(doc, user=None, **kwargs):
    return _owned_permission(doc, user, "user")

