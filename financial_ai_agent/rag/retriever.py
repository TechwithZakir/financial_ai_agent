from __future__ import annotations

import frappe


class KeywordRetriever:
    """Permission-aware baseline retriever; vector backends can replace this interface."""

    def search(self, knowledge_base: str, query: str, limit: int = 8) -> list[dict]:
        base = frappe.get_doc("AI Knowledge Base", knowledge_base)
        base.check_permission("read")
        terms = [term for term in query.split() if len(term) > 2][:8]
        if not terms:
            return []
        conditions = " or ".join(["content like %s"] * len(terms))
        values = [f"%{term}%" for term in terms]
        return frappe.db.sql(
            f"""select name, source_document, chunk_number, content, page, section_name as section
                from `tabAI Document Chunk`
                where knowledge_base=%s and ({conditions})
                order by modified desc limit %s""",
            [knowledge_base, *values, min(max(limit, 1), 20)], as_dict=True,
        )

