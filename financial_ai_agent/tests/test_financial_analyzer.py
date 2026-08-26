from decimal import Decimal
from unittest import TestCase

from financial_ai_agent.documents.financial_analyzer import (
    debt_service_ratio, detect_missing_fields, loan_to_value, monthly_cash_flow,
)


class TestFinancialAnalyzer(TestCase):
    def test_ratios_are_deterministic(self):
        self.assertEqual(debt_service_ratio("1200", "5000"), Decimal("24.00"))
        self.assertEqual(loan_to_value("320000", "400000"), Decimal("80.00"))
        self.assertIsNone(debt_service_ratio(10, 0))

    def test_cash_flow_groups_by_month(self):
        result = monthly_cash_flow([
            {"date": "2026-01-01", "amount": "1000"},
            {"date": "2026-01-12", "amount": "-250.50"},
        ])
        self.assertEqual(result[0]["net"], Decimal("749.50"))

    def test_missing_fields(self):
        self.assertEqual(detect_missing_fields({"name": "A", "income": None}, ["name", "income"]), ["income"])

