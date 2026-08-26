from __future__ import annotations

import frappe
from pathlib import Path
from frappe.utils.file_manager import save_file

DEMO_NOTICE = "Synthetic demonstration data - not for real financial decisions"


def generate_test_data() -> dict:
    """Create an idempotent, clearly labelled local demo configuration."""
    _require_administrator()
    provider = _ensure(
        "AI Provider", "Local Demo AI",
        {"provider_name": "Local Demo AI", "provider_type": "OpenAI Compatible",
         "enabled": 1, "base_url": "http://127.0.0.1:11434/v1", "timeout": 120,
         "retries": 0, "configuration_json": '{"demo": true}'},
    )
    model = _ensure(
        "AI Model", "Local Demo Financial Model",
        {"model_name": "Local Demo Financial Model", "provider": provider,
         "model_id": "qwen2.5:7b", "enabled": 1, "priority": 100,
         "capabilities": "chat\ntools\nstructured_output",
         "allowed_data_classes": "Public\nInternal\nConfidential\nSensitive Financial Data\nPII",
         "context_window": 32768, "max_output_tokens": 4000},
    )
    connector = _ensure(
        "CRM Connector", "Local ERPNext CRM Demo",
        {"connector_name": "Local ERPNext CRM Demo", "enabled": 1,
         "crm_type": "ERPNext CRM", "is_default": 1, "mode": "Local",
         "authentication_type": "Local Session", "timeout": 60, "retries": 0,
         "read_enabled": 1, "create_enabled": 1, "update_enabled": 1,
         "delete_enabled": 0, "approval_policy": '{"writes": "Amber"}'},
    )
    knowledge = _ensure(
        "AI Knowledge Base", "Demo Financial Policies",
        {"title": "Demo Financial Policies", "enabled": 1, "description": DEMO_NOTICE,
         "access_roles": "Financial AI User\nFinancial AI Manager\nSystem Manager",
         "status": "Active", "indexing_status": "Not Indexed"},
    )
    agent = _ensure(
        "AI Agent", "Financial Assistant Demo",
        {"agent_name": "Financial Assistant Demo", "enabled": 1,
         "description": DEMO_NOTICE,
         "system_instruction": (
             "You are a financial-services assistant operating on synthetic demo data. "
             "Use registered tools only, cite knowledge sources, never invent financial facts, "
             "and require human approval for mutations."
         ),
         "default_model": model, "default_crm_connector": connector,
         "knowledge_base": knowledge, "allow_user_model_selection": 0,
         "require_approval": 1, "max_tool_calls": 8, "memory_enabled": 1},
    )
    lead = _demo_lead()
    files = _demo_files(knowledge)
    frappe.db.commit()
    return {"provider": provider, "model": model, "connector": connector,
            "knowledge_base": knowledge, "agent": agent, "lead": lead, "files": files,
            "warning": "Requires an OpenAI-compatible server at 127.0.0.1:11434 using qwen2.5:7b."}


def _ensure(doctype: str, name: str, values: dict) -> str:
    if frappe.db.exists(doctype, name):
        doc = frappe.get_doc(doctype, name)
        doc.update(values)
        doc.save(ignore_permissions=True)
        return doc.name
    return frappe.get_doc({"doctype": doctype, **values}).insert(ignore_permissions=True).name


def _demo_lead() -> str | None:
    if not frappe.db.exists("DocType", "Lead"):
        return None
    existing = frappe.db.get_value("Lead", {"company_name": "Northstar Trading Demo"}, "name")
    if existing:
        return existing
    meta = frappe.get_meta("Lead")
    values = {"doctype": "Lead"}
    candidates = {
        "company_name": "Northstar Trading Demo", "first_name": "Amina", "last_name": "Rahman",
        "email_id": "amina.rahman@example.invalid", "mobile_no": "+8801700000000",
    }
    for field, value in candidates.items():
        if meta.has_field(field):
            values[field] = value
    try:
        return frappe.get_doc(values).insert(ignore_permissions=True).name
    except Exception:
        frappe.log_error(frappe.get_traceback(), "Could not create optional ERPNext Lead")
        return None


def _demo_files(knowledge_base: str) -> list[dict]:
    sample_dir = Path(frappe.get_app_path("financial_ai_agent")).parent / "sample_data"
    created = []
    client_fixtures = [
        "synthetic_financial_statements_2025.pdf", "synthetic_credit_application_summary.docx",
        "synthetic_financial_test_pack.xlsx", "synthetic_bank_statement.csv", "synthetic_payslip.txt",
    ]
    for filename in client_fixtures:
        path = sample_dir / filename
        if not path.is_file():
            continue
        existing = frappe.db.get_value("Client Document", {"file": ["like", f"%/{filename}"]}, "name")
        if existing:
            created.append({"type": "Client Document", "name": existing})
            continue
        file_doc = save_file(filename, path.read_bytes(), None, None, is_private=1)
        document = frappe.get_doc({
            "doctype": "Client Document", "file": file_doc.file_url,
            "uploaded_by": frappe.session.user, "document_type": "Unclassified",
            "processing_status": "Uploaded", "extraction_status": "Not Started",
        }).insert(ignore_permissions=True)
        frappe.db.set_value("File", file_doc.name, {
            "attached_to_doctype": "Client Document", "attached_to_name": document.name,
            "attached_to_field": "file",
        }, update_modified=False)
        created.append({"type": "Client Document", "name": document.name})
    policy = sample_dir / "synthetic_credit_policy.md"
    if policy.is_file():
        existing = frappe.db.get_value("AI Knowledge Document", {"title": "Synthetic SME Credit Policy"}, "name")
        if existing:
            created.append({"type": "AI Knowledge Document", "name": existing})
        else:
            file_doc = save_file(policy.name, policy.read_bytes(), None, None, is_private=1)
            document = frappe.get_doc({
                "doctype": "AI Knowledge Document", "knowledge_base": knowledge_base,
                "file": file_doc.file_url, "title": "Synthetic SME Credit Policy",
                "document_type": "Markdown", "version": "1.0", "status": "Uploaded",
            }).insert(ignore_permissions=True)
            frappe.db.set_value("File", file_doc.name, {
                "attached_to_doctype": "AI Knowledge Document", "attached_to_name": document.name,
                "attached_to_field": "file",
            }, update_modified=False)
            created.append({"type": "AI Knowledge Document", "name": document.name})
    return created


def _require_administrator() -> None:
    if frappe.session.user not in {"Administrator"} and "System Manager" not in frappe.get_roles():
        frappe.throw("System Manager role required", frappe.PermissionError)
