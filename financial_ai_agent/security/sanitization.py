from __future__ import annotations

import re
from typing import Any

SECRET_KEYS = re.compile(r"(api.?key|secret|access.?token|refresh.?token|password)", re.I)
INJECTION_PATTERNS = (
    re.compile(r"ignore (all |the )?(previous|prior|system) instructions", re.I),
    re.compile(r"reveal (the )?(system prompt|credentials|secrets)", re.I),
    re.compile(r"execute (arbitrary )?(python|sql|shell)", re.I),
)


def redact(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: "[REDACTED]" if SECRET_KEYS.search(str(key)) else redact(item) for key, item in value.items()}
    if isinstance(value, list):
        return [redact(item) for item in value]
    text = str(value) if value is not None else value
    if isinstance(text, str):
        return re.sub(r"(?i)bearer\s+[A-Za-z0-9._~+/-]+=*", "Bearer [REDACTED]", text)[:10000]
    return text


def detect_prompt_injection(text: str) -> list[str]:
    return [pattern.pattern for pattern in INJECTION_PATTERNS if pattern.search(text or "")]

