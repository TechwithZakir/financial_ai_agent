from __future__ import annotations

import json
import time

import frappe
from pydantic import TypeAdapter, ValidationError

from financial_ai_agent.ai.exceptions import ApprovalRequiredError, ToolPermissionError
from financial_ai_agent.tools.registry import RiskLevel, registry


class ToolExecutor:
    def execute(self, name: str, arguments: dict, *, session: str, correlation_id: str):
        definition = registry.get(name)
        roles = set(frappe.get_roles(frappe.session.user))
        if definition.roles and not roles.intersection(definition.roles):
            raise ToolPermissionError("You do not have permission to use this tool")
        if definition.risk == RiskLevel.PROHIBITED:
            raise ToolPermissionError("This action is prohibited")
        try:
            TypeAdapter(dict).validate_python(arguments)
        except ValidationError as exc:
            raise ValueError("Tool arguments must be an object") from exc
        if definition.risk in {RiskLevel.AMBER, RiskLevel.RED}:
            approval = frappe.get_doc({
                "doctype": "AI Approval Request",
                "action": name,
                "session": session,
                "requested_by": frappe.session.user,
                "tool": name,
                "proposed_changes": json.dumps(arguments),
                "risk_level": definition.risk.value,
                "status": "Pending",
                "correlation_id": correlation_id,
            }).insert()
            raise ApprovalRequiredError(approval.name)
        started = time.monotonic()
        result = definition.function(**arguments)
        return {"result": result, "duration_ms": round((time.monotonic() - started) * 1000)}

