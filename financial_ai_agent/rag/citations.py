from __future__ import annotations


def citation(chunk: dict) -> dict:
    return {
        "document": chunk.get("source_document"),
        "title": chunk.get("title"),
        "page": chunk.get("page"),
        "section": chunk.get("section"),
        "chunk": chunk.get("chunk_number"),
    }

