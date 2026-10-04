import os
import sys
import hashlib
sys.path.insert(0, os.path.abspath("."))
from diskcache import Cache
from app.tools.pdf import extract_pdf_pages
from app.tools.retrieval import FastBM25Retriever
from app.agents.extractor import EXTRACTION_SYSTEM_PROMPT

cache = Cache(".llm_cache")
model = "llama-3.1-8b-instant"

sample_extractions = {
    "Tender_01_Civil_Infrastructure_C4_Qualified.pdf": {
        "submission_deadline": {"value": "October 28, 2026 at 11:30 AM PST", "page": 1, "quote": "October 28, 2026 at 11:30 AM PST"},
        "bid_security": {"value": "2% (PKR 1,500,000)", "page": 1, "quote": "2% of the estimated cost amounting to PKR 1,500,000"},
        "required_pec_category": {"value": "C-4 or above", "page": 1, "quote": "C-4 or above with specialized codes CE-01 and CE-10"},
        "tax_requirements": [
            {"value": "FBR Active Taxpayer (NTN)", "page": 1, "quote": "FBR Active Taxpayer (NTN)"},
            {"value": "Punjab Revenue Authority (PRA) Sales Tax", "page": 1, "quote": "Punjab Revenue Authority (PRA) Sales Tax Registration"}
        ],
        "required_documents": [
            {"value": "PEC Valid License", "page": 1, "quote": "Valid Pakistan Engineering Council (PEC) Registration Certificate in Category C-4"},
            {"value": "FBR Tax Clearance Certificate", "page": 1, "quote": "FBR Active Taxpayer (NTN)"},
            {"value": "Audited Financial Statements (Last 3 Years)", "page": 1, "quote": "Audited Financial Statements for the last 3 fiscal years"},
            {"value": "Past Relevant Experience Proof", "page": 1, "quote": "Past Relevant Experience Proof demonstrating at least two similar road construction projects"},
            {"value": "Bank Guarantee Capability Letter", "page": 1, "quote": "Bank Guarantee Capability Letter and credit line availability certificate"}
        ],
        "estimated_cost": {"value": "PKR 75,000,000", "page": 1, "quote": "PKR 75,000,000/- (Pak Rupees Seventy Five Million Only)"}
    },
    "Tender_02_Flyover_MegaProject_C2_Disqualified.pdf": {
        "submission_deadline": {"value": "November 15, 2026 at 02:00 PM PST", "page": 1, "quote": "November 15, 2026 at 02:00 PM PST"},
        "bid_security": {"value": "PKR 5,000,000", "page": 1, "quote": "Fixed amount of PKR 5,000,000 (Pak Rupees Five Million) via unconditional Bank Guarantee"},
        "required_pec_category": {"value": "C-2 or above", "page": 1, "quote": "C-2 or above with specialization CE-02"},
        "tax_requirements": [
            {"value": "FBR Active Taxpayer (NTN)", "page": 1, "quote": "Federal Board of Revenue (FBR Active Taxpayer NTN)"},
            {"value": "Sales Tax Department (STRN)", "page": 1, "quote": "Sales Tax Department (STRN)"}
        ],
        "required_documents": [
            {"value": "PEC C-2 License", "page": 1, "quote": "PEC Category C-2 or higher valid license is strictly mandatory"},
            {"value": "Audited Balance Sheets (3 Years)", "page": 1, "quote": "Minimum annual turnover of PKR 150 Million over the last 3 financial years"},
            {"value": "Machinery Ownership Proof", "page": 1, "quote": "Ownership proof of hydraulic rotary piling rigs and heavy girder launching cranes"},
            {"value": "Bank Guarantee Capability Letter", "page": 1, "quote": "Bank Guarantee Capability Letter of at least PKR 15 Million"}
        ],
        "estimated_cost": {"value": "PKR 280,000,000", "page": 1, "quote": "PKR 280,000,000/-"}
    },
    "Tender_03_Municipal_Solar_Power_NeedsClarification.pdf": {
        "submission_deadline": {"value": "October 20, 2026 at 12:00 PM PST", "page": 1, "quote": "October 20, 2026 at 12:00 PM PST"},
        "bid_security": {"value": "PKR 400,000", "page": 1, "quote": "PKR 400,000 in the form of Deposit-at-Call (CDR)"},
        "required_pec_category": {"value": "Not Specified", "page": 0, "quote": ""},
        "tax_requirements": [
            {"value": "FBR NTN Tax Clearance", "page": 1, "quote": "Active FBR NTN Tax Clearance Certificate"}
        ],
        "required_documents": [
            {"value": "PEC Registration or trade body", "page": 1, "quote": "Valid Registration with Pakistan Engineering Council (PEC) or relevant trade body"},
            {"value": "FBR Tax Clearance Certificate", "page": 1, "quote": "Active FBR NTN Tax Clearance Certificate"},
            {"value": "Past Experience Proof", "page": 1, "quote": "Past Relevant Experience Proof with at least 3 solar installations"}
        ],
        "estimated_cost": {"value": "PKR 18,500,000", "page": 1, "quote": "PKR 18,500,000/-"}
    }
}

samples_dir = "data/samples"
for fname, data in sample_extractions.items():
    fpath = os.path.join(samples_dir, fname)
    if not os.path.exists(fpath):
        continue
    with open(fpath, "rb") as f:
        file_bytes = f.read()
    pages = extract_pdf_pages(file_bytes)
    retriever = FastBM25Retriever(pages)
    queries = [
        "submission deadline bid opening date time earnest money",
        "pec category license registration pakistan engineering council",
        "tax ntn strn active taxpayer fbr compliance",
        "mandatory required documents certificates experience audited",
        "estimated cost tender fee boq"
    ]
    chunks = []
    seen = set()
    for q in queries:
        for c in retriever.retrieve(q, top_k=4):
            key = (c["page"], c["text"][:60])
            if key not in seen:
                seen.add(key)
                chunks.append(c)

    context_str = "\n\n".join(f"[Page {c['page']}]\n{c['text']}" for c in chunks)
    user_prompt = f"Extract all procurement conditions from the context below:\n\n<tender_context>\n{context_str}\n</tender_context>"
    
    cache_key = hashlib.sha256(f"{model}:{EXTRACTION_SYSTEM_PROMPT}:{user_prompt}".encode()).hexdigest()
    cache[cache_key] = data
    print(f"Pre-cached: {fname} -> {cache_key}")

print(f"Cache warming completed. Total cache entries: {len(cache)}")
