import json

import frappe
from frappe.model.document import Document

from financial_ai_agent.documents.schemas import FinancialExtraction


class AIDocumentExtraction(Document):
    def validate(self):
        if self.validation_status == "Validated":
            try:
                payload = json.loads(self.extracted_json or "{}")
                FinancialExtraction.model_validate(payload)
            except (ValueError, TypeError) as exc:
                frappe.throw(f"Extraction does not match the financial schema: {exc}")
            if self.human_review_status != "Approved":
                frappe.throw("Human review must be approved before validation")

