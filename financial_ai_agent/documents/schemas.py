from __future__ import annotations

from pydantic import BaseModel, Field


class FinancialExtraction(BaseModel):
    document_type: str
    account_holder: str | None = None
    institution: str | None = None
    currency: str | None = None
    period_start: str | None = None
    period_end: str | None = None
    gross_income: float | None = None
    net_income: float | None = None
    opening_balance: float | None = None
    closing_balance: float | None = None
    transactions: list[dict] = Field(default_factory=list)
    assets: list[dict] = Field(default_factory=list)
    liabilities: list[dict] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)

