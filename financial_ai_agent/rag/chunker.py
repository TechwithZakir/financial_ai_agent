from __future__ import annotations


def chunk_text(text: str, *, size: int = 1200, overlap: int = 150) -> list[dict]:
    if size < 200 or overlap < 0 or overlap >= size:
        raise ValueError("Invalid chunk configuration")
    clean = "\n".join(line.strip() for line in (text or "").splitlines() if line.strip())
    chunks, start, number = [], 0, 1
    while start < len(clean):
        end = min(start + size, len(clean))
        if end < len(clean):
            boundary = max(clean.rfind(". ", start, end), clean.rfind("\n", start, end))
            if boundary > start + size // 2:
                end = boundary + 1
        content = clean[start:end].strip()
        if content:
            chunks.append({"chunk_number": number, "content": content,
                           "start_offset": start, "end_offset": end})
            number += 1
        if end >= len(clean):
            break
        start = end - overlap
    return chunks

