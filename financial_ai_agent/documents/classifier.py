from __future__ import annotations

from pathlib import Path

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".xlsx", ".csv", ".txt", ".md", ".png", ".jpg", ".jpeg"}


def classify(filename: str, text_sample: str = "") -> str:
    extension = Path(filename).suffix.lower()
    if extension not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported document type: {extension or 'unknown'}")
    sample = (text_sample or "").lower()
    if "bank statement" in sample or ("opening balance" in sample and "closing balance" in sample):
        return "Bank Statement"
    if "payslip" in sample or ("gross pay" in sample and "net pay" in sample):
        return "Payslip"
    if "balance sheet" in sample or "income statement" in sample or "profit and loss" in sample:
        return "Financial Statements"
    if extension in {".png", ".jpg", ".jpeg"}:
        return "Image"
    return "General Financial Document"

