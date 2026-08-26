from __future__ import annotations

import frappe

from financial_ai_agent.providers.crm.registry import get_crm_provider
from financial_ai_agent.tools.registry import RiskLevel, tool

CRM_ROLES = ("Financial AI User", "Financial AI Manager", "System Manager")


def _provider(connector: str, operation: str):
    doc = frappe.get_doc("CRM Connector", connector)
    if not doc.enabled:
        frappe.throw("CRM Connector is disabled")
    flag = {
        "read": "read_enabled", "create": "create_enabled",
        "update": "update_enabled", "delete": "delete_enabled",
    }[operation]
    if not doc.get(flag):
        frappe.throw(f"CRM {operation} operations are disabled")
    return get_crm_provider(doc)


@tool(
    name="crm.search", description="Search canonical CRM records using provider permissions.",
    schema={"type":"object","properties":{
        "connector":{"type":"string"}, "object_type":{"type":"string","enum":["Lead","Contact","Account","Deal","Task","Note"]},
        "query":{"type":"string"}, "filters":{"type":"object"}, "limit":{"type":"integer","minimum":1,"maximum":100}},
        "required":["connector","object_type"]}, roles=CRM_ROLES,
)
def search(connector: str, object_type: str, query=None, filters=None, limit=20):
    return _provider(connector, "read").search(object_type, query, filters, int(limit))


@tool(
    name="crm.get", description="Get one canonical CRM record.",
    schema={"type":"object","properties":{"connector":{"type":"string"},"object_type":{"type":"string"},"record_id":{"type":"string"}},
            "required":["connector","object_type","record_id"]}, roles=CRM_ROLES,
)
def get(connector: str, object_type: str, record_id: str):
    return _provider(connector, "read").get(object_type, record_id)


@tool(
    name="crm.create", description="Create a canonical CRM record after human approval.",
    schema={"type":"object","properties":{"connector":{"type":"string"},"object_type":{"type":"string"},"values":{"type":"object"}},
            "required":["connector","object_type","values"]}, risk=RiskLevel.AMBER, roles=CRM_ROLES,
)
def create(connector: str, object_type: str, values: dict):
    return _provider(connector, "create").create(object_type, values)


@tool(
    name="crm.update", description="Update a canonical CRM record after human approval.",
    schema={"type":"object","properties":{"connector":{"type":"string"},"object_type":{"type":"string"},"record_id":{"type":"string"},"values":{"type":"object"}},
            "required":["connector","object_type","record_id","values"]}, risk=RiskLevel.AMBER, roles=CRM_ROLES,
)
def update(connector: str, object_type: str, record_id: str, values: dict):
    return _provider(connector, "update").update(object_type, record_id, values)

