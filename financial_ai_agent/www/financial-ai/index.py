import frappe

no_cache = 1


def get_context(context):
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/login?redirect-to=/financial-ai"
        raise frappe.Redirect
    roles = set(frappe.get_roles())
    if not {"Financial AI User", "Financial AI Manager", "System Manager"}.intersection(roles):
        frappe.throw("Financial AI role required", frappe.PermissionError)
    context.no_cache = 1
    context.show_sidebar = False
    context.agents = frappe.get_all("AI Agent", filters={"enabled": 1}, fields=["name", "description"])
    context.csrf_token = frappe.sessions.get_csrf_token()
    return context

