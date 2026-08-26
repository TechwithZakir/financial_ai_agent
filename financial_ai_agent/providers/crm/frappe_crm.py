from __future__ import annotations

import frappe

from financial_ai_agent.providers.crm.base import BaseCRMProvider

CANONICAL_TYPES = {
    "Lead": "CRM Lead",
    "Contact": "Contact",
    "Account": "CRM Organization",
    "Deal": "CRM Deal",
    "Task": "ToDo",
    "Note": "Note",
}


class FrappeCRMProvider(BaseCRMProvider):
    def _doctype(self, object_type: str) -> str:
        doctype = CANONICAL_TYPES.get(object_type)
        if not doctype or not frappe.db.exists("DocType", doctype):
            frappe.throw(f"Canonical CRM object is unavailable: {object_type}")
        return doctype

    def search(self, object_type, query=None, filters=None, limit=20):
        doctype = self._doctype(object_type)
        if not frappe.has_permission(doctype, "read"):
            frappe.throw("Not permitted", frappe.PermissionError)
        filters = dict(filters or {})
        or_filters = None
        if query:
            title = frappe.get_meta(doctype).get_title_field() or "name"
            or_filters = [[doctype, title, "like", f"%{query}%"]]
        return frappe.get_list(
            doctype, filters=filters, or_filters=or_filters, fields=["*"], limit_page_length=min(limit, 100)
        )

    def get(self, object_type, record_id):
        doctype = self._doctype(object_type)
        doc = frappe.get_doc(doctype, record_id)
        doc.check_permission("read")
        return doc.as_dict(no_nulls=True)

    def create(self, object_type, values):
        doctype = self._doctype(object_type)
        if not frappe.has_permission(doctype, "create"):
            frappe.throw("Not permitted", frappe.PermissionError)
        return frappe.get_doc({"doctype": doctype, **values}).insert().as_dict(no_nulls=True)

    def update(self, object_type, record_id, values):
        doc = frappe.get_doc(self._doctype(object_type), record_id)
        doc.check_permission("write")
        doc.update(values)
        doc.save()
        return doc.as_dict(no_nulls=True)

    def create_note(self, object_type, record_id, note):
        return self.create("Note", {"title": f"{object_type} {record_id}", "content": note})

    def test_connection(self):
        return {"ok": bool(frappe.db.exists("DocType", "CRM Lead")), "mode": "local"}

