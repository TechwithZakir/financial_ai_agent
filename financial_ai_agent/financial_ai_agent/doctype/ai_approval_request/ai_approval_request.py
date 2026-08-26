import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime


class AIApprovalRequest(Document):
    def validate(self):
        if self.is_new():
            self.requested_by = self.requested_by or frappe.session.user
            self.requested_at = self.requested_at or now_datetime()
        if not self.is_new() and self.has_value_changed("status"):
            allowed = {"Pending": {"Approved", "Rejected", "Expired"}, "Approved": {"Executed", "Failed"}}
            before = self.get_doc_before_save()
            previous = before.status if before else "Pending"
            if self.status not in allowed.get(previous, set()):
                frappe.throw(f"Invalid approval transition: {previous} to {self.status}")

