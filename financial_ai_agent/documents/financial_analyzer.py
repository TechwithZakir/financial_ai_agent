from __future__ import annotations

from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Iterable


def money(value) -> Decimal:
    try:
        return Decimal(str(value or 0)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    except (InvalidOperation, ValueError) as exc:
        raise ValueError("Invalid monetary value") from exc


def debt_service_ratio(monthly_debt, gross_monthly_income) -> Decimal | None:
    income = money(gross_monthly_income)
    if income <= 0:
        return None
    return (money(monthly_debt) / income * 100).quantize(Decimal("0.01"))


def loan_to_value(loan_amount, property_value) -> Decimal | None:
    value = money(property_value)
    if value <= 0:
        return None
    return (money(loan_amount) / value * 100).quantize(Decimal("0.01"))


def monthly_cash_flow(transactions: Iterable[dict]) -> list[dict]:
    buckets: dict[str, dict[str, Decimal]] = {}
    for item in transactions:
        month = str(item.get("date", ""))[:7]
        if len(month) != 7:
            continue
        bucket = buckets.setdefault(month, {"inflow": Decimal("0"), "outflow": Decimal("0")})
        amount = money(item.get("amount"))
        bucket["inflow" if amount >= 0 else "outflow"] += abs(amount)
    return [
        {"month": month, "inflow": values["inflow"], "outflow": values["outflow"],
         "net": values["inflow"] - values["outflow"]}
        for month, values in sorted(buckets.items())
    ]


def detect_missing_fields(extraction: dict, required_fields: Iterable[str]) -> list[str]:
    return [field for field in required_fields if extraction.get(field) in (None, "", [])]

