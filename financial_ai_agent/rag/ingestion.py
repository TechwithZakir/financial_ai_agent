from __future__ import annotations

import hashlib
import json

import frappe
from frappe.utils import now_datetime

from financial_ai_agent.documents.classifier import classify
from financial_ai_agent.documents.parser import parse_file
from financial_ai_agent.rag.chunker import chunk_text


def process_knowledge_document(name: str) -> None:
    document = frappe.get_doc("AI Knowledge Document", name)
    document.db_set("status", "Processing")
    try:
        file_doc = frappe.get_doc("File", {"file_url": document.file})
        parsed = parse_file(file_doc.get_full_path(), file_doc.file_name)
        if parsed["requires_vision"]:
            raise ValueError("Image knowledge documents require a configured vision workflow")
        checksum = hashlib.sha256(parsed["text"].encode("utf-8")).hexdigest()
        if document.checksum == checksum and document.indexed:
            document.db_set("status", "Ready")
            return
        frappe.db.delete("AI Document Chunk", {"source_document": document.name})
        page_lookup = _page_lookup(parsed.get("pages") or [])
        for item in chunk_text(parsed["text"]):
            page = page_lookup(item["start_offset"])
            frappe.get_doc({
                "doctype": "AI Document Chunk", "knowledge_base": document.knowledge_base,
                "source_document": document.name, "chunk_number": item["chunk_number"],
                "content": item["content"], "page": page,
                "metadata_json": json.dumps({"start": item["start_offset"], "end": item["end_offset"]}),
            }).insert(ignore_permissions=True)
        document.db_set("document_type", classify(file_doc.file_name, parsed["text"][:5000]))
        document.db_set("checksum", checksum)
        document.db_set("indexed", 1)
        document.db_set("last_indexed", now_datetime())
        document.db_set("status", "Ready")
        frappe.db.set_value("AI Knowledge Base", document.knowledge_base, "indexing_status", "Ready")
    except Exception:
        reference = frappe.generate_hash(length=12)
        frappe.log_error(frappe.get_traceback(), f"Knowledge indexing failed {reference}")
        document.db_set("status", "Failed")
        frappe.db.set_value("AI Knowledge Base", document.knowledge_base, "indexing_status", "Failed")


def _page_lookup(pages: list[dict]):
    boundaries, offset = [], 0
    for page in pages:
        offset += len(page.get("text") or "") + 2
        boundaries.append((offset, page.get("page")))
    def lookup(position: int):
        return next((page for boundary, page in boundaries if position < boundary), None)
    return lookup

