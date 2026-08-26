import frappe
from frappe.model.document import Document


class ClientDocument(Document):
    def before_insert(self):
        self.uploaded_by = self.uploaded_by or frappe.session.user

    def validate(self):
        if self.uploaded_by != frappe.session.user and "System Manager" not in frappe.get_roles():
            frappe.throw("Uploaded By cannot be changed", frappe.PermissionError)

