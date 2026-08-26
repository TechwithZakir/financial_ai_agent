from __future__ import annotations

import frappe
from frappe.utils import now_datetime

from financial_ai_agent.api.chat import _require_user


@frappe.whitelist()
def queue_client_document(document: str):
    user = _require_user()
    doc = frappe.get_doc("Client Document", document)
    doc.check_permission("write")
    if doc.uploaded_by != user and "Financial AI Manager" not in frappe.get_roles(user):
        frappe.throw("Not permitted", frappe.PermissionError)
    if doc.processing_status in {"Queued", "Processing"}:
        return {"queued": True, "document": doc.name}
    doc.db_set("processing_status", "Queued")
    frappe.enqueue(
        "financial_ai_agent.documents.processor.process_client_document",
        queue="long", timeout=900, enqueue_after_commit=True, name=doc.name,
        job_id=f"financial-ai-client-document-{doc.name}", deduplicate=True,
    )
    return {"queued": True, "document": doc.name}


@frappe.whitelist()
def review_extraction(extraction: str, decision: str):
    _require_user()
    allowed_roles = {"Financial AI Manager", "Financial AI Compliance Reviewer", "System Manager"}
    if not allowed_roles.intersection(frappe.get_roles()):
        frappe.throw("Reviewer role required", frappe.PermissionError)
    if decision not in {"Approved", "Rejected"}:
        frappe.throw("Decision must be Approved or Rejected")
    doc = frappe.get_doc("AI Document Extraction", extraction)
    doc.check_permission("write")
    doc.human_review_status = decision
    doc.reviewed_by = frappe.session.user
    doc.reviewed_at = now_datetime()
    doc.validation_status = "Validated" if decision == "Approved" else "Invalid"
    doc.save()
    frappe.db.set_value(
        "Client Document", doc.client_document, "extraction_status",
        "Validated" if decision == "Approved" else "Failed",
    )
    return {"status": decision}

