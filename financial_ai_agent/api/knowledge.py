import frappe

from financial_ai_agent.api.chat import _require_user
from financial_ai_agent.rag.citations import citation
from financial_ai_agent.rag.retriever import KeywordRetriever


@frappe.whitelist()
def queue_index(document: str):
    _require_user()
    doc = frappe.get_doc("AI Knowledge Document", document)
    doc.check_permission("write")
    doc.db_set("status", "Queued")
    frappe.db.set_value("AI Knowledge Base", doc.knowledge_base, "indexing_status", "Queued")
    frappe.enqueue(
        "financial_ai_agent.rag.ingestion.process_knowledge_document",
        queue="long", timeout=900, enqueue_after_commit=True, name=doc.name,
        job_id=f"financial-ai-knowledge-{doc.name}", deduplicate=True,
    )
    return {"queued": True, "document": doc.name}


@frappe.whitelist()
def search(knowledge_base: str, query: str, limit: int = 8):
    _require_user()
    query = (query or "").strip()
    if not query:
        frappe.throw("Query is required")
    rows = KeywordRetriever().search(knowledge_base, query, int(limit))
    return [{**row, "citation": citation(row)} for row in rows]

