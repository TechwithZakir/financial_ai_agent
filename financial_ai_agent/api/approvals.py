from __future__ import annotations

import json
import time

import frappe
from frappe.utils import now_datetime

from financial_ai_agent.api.chat import _require_user
from financial_ai_agent.security.sanitization import redact
from financial_ai_agent.tools.registry import RiskLevel, registry

REVIEW_ROLES = {"Financial AI Manager", "Financial AI Compliance Reviewer", "System Manager"}


def _reviewer() -> str:
    user = _require_user()
    if not REVIEW_ROLES.intersection(frappe.get_roles(user)):
        frappe.throw("Reviewer role required", frappe.PermissionError)
    return user


@frappe.whitelist()
def decide(approval: str, decision: str, comment: str | None = None):
    user = _reviewer()
    if decision not in {"Approved", "Rejected"}:
        frappe.throw("Decision must be Approved or Rejected")
    doc = frappe.get_doc("AI Approval Request", approval)
    doc.check_permission("write")
    if doc.status != "Pending":
        frappe.throw("This request is no longer pending")
    if doc.requested_by == user:
        frappe.throw("A requester cannot approve their own action")
    if doc.risk_level == RiskLevel.RED.value and not {
        "Financial AI Compliance Reviewer", "System Manager"
    }.intersection(frappe.get_roles(user)):
        frappe.throw("Red-risk actions require a compliance reviewer")
    doc.status = decision
    doc.reviewed_by = user
    doc.reviewed_at = now_datetime()
    if comment:
        doc.add_comment("Comment", text=comment[:1000])
    doc.save()
    return {"approval": doc.name, "status": doc.status}


@frappe.whitelist()
def execute(approval: str):
    user = _reviewer()
    doc = frappe.get_doc("AI Approval Request", approval)
    doc.check_permission("write")
    if doc.status in {"Executed", "Failed"}:
        return {"approval": doc.name, "status": doc.status,
                "result": json.loads(doc.execution_result or "{}")}
    if doc.status != "Approved":
        frappe.throw("Only approved requests can be executed")
    definition = registry.get(doc.tool)
    if definition.risk == RiskLevel.PROHIBITED:
        frappe.throw("This tool is prohibited")
    roles = set(frappe.get_roles(user))
    if definition.roles and not roles.intersection(definition.roles):
        frappe.throw("Executor does not have the tool's required role", frappe.PermissionError)
    arguments = json.loads(doc.proposed_changes or "{}")
    started = time.monotonic()
    try:
        result = definition.function(**arguments)
        safe_result = redact(result)
        doc.execution_result = json.dumps({
            "result": safe_result, "duration_ms": round((time.monotonic() - started) * 1000)
        }, default=str)
        doc.status = "Executed"
        doc.save()
    except Exception:
        reference = frappe.generate_hash(length=12)
        frappe.log_error(frappe.get_traceback(), f"Approved AI action failed {reference}")
        doc.execution_result = json.dumps({"error": f"Execution failed. Reference: {reference}"})
        doc.status = "Failed"
        doc.save()
    return {"approval": doc.name, "status": doc.status,
            "result": json.loads(doc.execution_result or "{}")}

