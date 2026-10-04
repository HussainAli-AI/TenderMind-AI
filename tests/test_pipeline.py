import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("."))

from app.schemas import ExtractedField, TenderExtraction, RuleResult
from app.tools.pdf import extract_pdf_pages, PageData
from app.tools.retrieval import FastBM25Retriever
from app.agents.verifier import run_verifier, verify_single_field
from app.agents.rules import evaluate_eligibility
from app.graph import build_tender_graph
from app.tools.export import generate_bid_pack_docx

class TestTenderMindAI(unittest.TestCase):

    def test_schemas(self):
        f = ExtractedField(value="PKR 1,500,000", page=1, quote="amounting to PKR 1,500,000")
        self.assertEqual(f.value, "PKR 1,500,000")
        self.assertEqual(f.page, 1)

    def test_pdf_extraction(self):
        sample_path = "data/samples/Tender_01_Civil_Infrastructure_C4_Qualified.pdf"
        self.assertTrue(os.path.exists(sample_path), "Sample 1 must exist")
        with open(sample_path, "rb") as f:
            file_bytes = f.read()
        pages = extract_pdf_pages(file_bytes)
        self.assertGreater(len(pages), 0)
        self.assertIn("COMMUNICATION & WORKS DEPARTMENT", pages[0].text)

    def test_bm25_retrieval(self):
        pages = [PageData(page_num=1, text="The required PEC Category is C-4. Bid security is 2%.", method="text")]
        retriever = FastBM25Retriever(pages)
        chunks = retriever.retrieve("PEC Category C-4")
        self.assertGreater(len(chunks), 0)
        self.assertIn("PEC Category", chunks[0]["text"])

    def test_verifier_anti_hallucination(self):
        pages = [PageData(page_num=1, text="Earnest money is PKR 1,500,000 payable to Executive Engineer.", method="text")]
        page_map = {1: pages[0]}

        # Legitimate grounded field
        good_field = {"value": "PKR 1,500,000", "page": 1, "quote": "Earnest money is PKR 1,500,000"}
        v_good = verify_single_field(good_field, page_map)
        self.assertEqual(v_good["status"], "verified")

        # Hallucinated quote (not in document)
        fake_quote = {"value": "USD 50,000,000", "page": 1, "quote": "International World Bank grant of 50 million"}
        v_fake = verify_single_field(fake_quote, page_map)
        self.assertEqual(v_fake["status"], "ungrounded")

        # Hallucinated digits (digits not in page)
        fake_digit = {"value": "PKR 9,999,999", "page": 1, "quote": "Earnest money is PKR 9,999,999"}
        v_digit = verify_single_field(fake_digit, page_map)
        self.assertEqual(v_digit["status"], "ungrounded")

    def test_rules_engine_scenarios(self):
        profile = {
            "company_name": "Apex Engineering",
            "licence_category": "C-4",
            "registrations": ["FBR Active Taxpayer (NTN)", "Sales Tax Registration (STRN)"],
            "max_bid_security_pkr": 3000000,
            "documents": ["PEC Valid License", "Company Registration Certificate", "FBR Tax Clearance Certificate"]
        }

        # Scenario 1: Qualified C-4
        verified_1 = {
            "required_pec_category": {"value": "C-4", "status": "verified", "quote": "Category C-4"},
            "tax_requirements": [{"value": "FBR NTN", "status": "verified", "quote": "FBR NTN"}],
            "bid_security": {"value": "PKR 1,500,000", "status": "verified", "quote": "PKR 1,500,000"},
            "required_documents": [{"value": "PEC Valid License", "status": "verified"}]
        }
        verdict_1, _ = evaluate_eligibility(verified_1, profile)
        self.assertIn("BID (Qualified)", verdict_1)

        # Scenario 2: Disqualified (requires C-2, profile only has C-4)
        verified_2 = {
            "required_pec_category": {"value": "C-2", "status": "verified", "quote": "Category C-2 or above"},
            "tax_requirements": [{"value": "FBR NTN", "status": "verified", "quote": "FBR NTN"}],
            "bid_security": {"value": "PKR 5,000,000", "status": "verified", "quote": "PKR 5,000,000"}
        }
        verdict_2, _ = evaluate_eligibility(verified_2, profile)
        self.assertEqual(verdict_2, "NO-BID")

        # Scenario 3: Clarification Required (PEC missing / unverified)
        verified_3 = {
            "required_pec_category": {"value": "Not Specified", "status": "missing", "quote": ""},
            "tax_requirements": [{"value": "FBR NTN", "status": "verified", "quote": "FBR NTN"}],
            "bid_security": {"value": "PKR 500,000", "status": "verified", "quote": "PKR 500,000"}
        }
        verdict_3, _ = evaluate_eligibility(verified_3, profile)
        self.assertIn("BID IF", verdict_3)

    def test_docx_export(self):
        bio = generate_bid_pack_docx(
            verdict="BID (Qualified)",
            verified_fields={"required_pec_category": {"value": "C-4", "page": 1, "quote": "PEC C-4", "status": "verified"}},
            rule_results=[{"rule_id": "R1", "name": "PEC Check", "severity": "hard", "status": "PASS", "reason": "Matches C-4"}]
        )
        self.assertGreater(bio.getbuffer().nbytes, 1000)

    def test_langgraph_pipeline_execution(self):
        sample_path = "data/samples/Tender_01_Civil_Infrastructure_C4_Qualified.pdf"
        with open(sample_path, "rb") as f:
            file_bytes = f.read()
        pages = extract_pdf_pages(file_bytes)
        profile = {
            "company_name": "Apex Engineering",
            "licence_category": "C-4",
            "registrations": ["FBR Active Taxpayer (NTN)", "Sales Tax Registration (STRN)"],
            "max_bid_security_pkr": 3000000,
            "documents": ["PEC Valid License", "Company Registration Certificate", "FBR Tax Clearance Certificate"]
        }
        initial_state = {
            "pages": pages,
            "profile": profile,
            "retriever": None,
            "raw_extraction": {},
            "verified_extraction": {},
            "verdict": "",
            "rule_results": []
        }
        graph = build_tender_graph()
        final_state = graph.invoke(initial_state)
        self.assertIn("verdict", final_state)
        self.assertIn("BID", final_state["verdict"])
        self.assertGreater(len(final_state["rule_results"]), 0)

if __name__ == "__main__":
    unittest.main()
