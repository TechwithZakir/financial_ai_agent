from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from financial_ai_agent.documents.classifier import classify
from financial_ai_agent.documents.parser import parse_file
from financial_ai_agent.rag.chunker import chunk_text


class TestDocuments(TestCase):
    sample_dir = Path(__file__).resolve().parents[2] / "sample_data"
    def test_classifies_bank_statement(self):
        self.assertEqual(classify("statement.pdf", "Bank statement opening balance closing balance"),
                         "Bank Statement")

    def test_rejects_unknown_extension(self):
        with self.assertRaises(ValueError):
            classify("payload.exe")

    def test_parses_plain_text(self):
        with TemporaryDirectory() as folder:
            path = Path(folder) / "sample.txt"
            path.write_text("Financial statement", encoding="utf-8")
            self.assertEqual(parse_file(str(path))["text"], "Financial statement")

    def test_chunk_overlap_and_sequence(self):
        chunks = chunk_text("Sentence. " * 100, size=220, overlap=20)
        self.assertGreater(len(chunks), 1)
        self.assertEqual([item["chunk_number"] for item in chunks], list(range(1, len(chunks) + 1)))

    def test_bundled_pdf_fixture(self):
        parsed = parse_file(str(self.sample_dir / "synthetic_financial_statements_2025.pdf"))
        self.assertIn("Statement of profit or loss", parsed["text"])
        self.assertGreaterEqual(len(parsed["pages"]), 2)

    def test_bundled_docx_fixture(self):
        parsed = parse_file(str(self.sample_dir / "synthetic_credit_application_summary.docx"))
        self.assertIn("Financial snapshot", parsed["text"])

    def test_bundled_xlsx_fixture(self):
        parsed = parse_file(str(self.sample_dir / "synthetic_financial_test_pack.xlsx"))
        self.assertIn("Northstar Trading Ltd.", parsed["text"])

    def test_bundled_csv_and_text_fixtures(self):
        statement = parse_file(str(self.sample_dir / "synthetic_bank_statement.csv"))
        payslip = parse_file(str(self.sample_dir / "synthetic_payslip.txt"))
        self.assertIn("Customer receipt", statement["text"])
        self.assertEqual(classify("statement.csv", statement["text"]), "Bank Statement")
        self.assertEqual(classify("payslip.txt", payslip["text"]), "Payslip")

