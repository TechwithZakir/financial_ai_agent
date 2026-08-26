import frappe
from frappe.model.document import Document


class AIModel(Document):
    def validate(self):
        if self.fallback_model == self.name:
            frappe.throw("A model cannot use itself as fallback")
        if int(self.context_window or 0) < 1:
            frappe.throw("Context Window must be positive")

