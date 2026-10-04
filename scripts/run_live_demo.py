import os, sys
sys.path.insert(0, os.path.abspath("."))
from app.tools.pdf import extract_pdf_pages
from app.graph import build_tender_graph

# Read sample PDF (Sample 3: Solar)
with open("data/samples/Tender_03_Municipal_Solar_Power_NeedsClarification.pdf", "rb") as f:
    pages = extract_pdf_pages(f.read())

profile = {
    "company_name": "Apex Engineering & Tech Solutions Pvt Ltd",
    "licence_category": "C-4",
    "max_bid_security_pkr": 3000000,
    "registrations": ["FBR Active Taxpayer (NTN)", "Sales Tax Registration (STRN)"],
    "documents": [
        "Company Registration Certificate",
        "FBR Tax Clearance Certificate",
        "PEC Valid License",
        "Audited Financial Statements (Last 3 Years)",
        "Past Relevant Experience Proof",
        "Bank Guarantee Capability Letter"
    ]
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

print("Running LangGraph Autonomous Multi-Agent Swarm against Groq Cloud...")
graph = build_tender_graph()
final_state = graph.invoke(initial_state)

print("\n=== LIVE AGENTIC PIPELINE EXECUTION COMPLETED ===")
print("Verdict:", final_state["verdict"])
print("\n--- Verified Requirements ---")
for k, v in final_state["verified_extraction"].items():
    if isinstance(v, dict):
        print(f"• {k}: {v.get('value')} (Status: {v.get('status')})")
        if v.get('quote'):
            print(f"   Excerpt: \"{v.get('quote')}\"")

print("\n--- Rule Evaluation Results ---")
for r in final_state["rule_results"]:
    print(f"[{r['status']}] {r['name']} ({r['severity']}): {r['reason']}")
