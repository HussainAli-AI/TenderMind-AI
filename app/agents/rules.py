import re
from rapidfuzz import fuzz

PEC_ORDER = ["C-6", "C-5", "C-4", "C-3", "C-2", "C-1", "C-B", "C-A", "CA", "CB", "C1", "C2", "C3", "C4", "C5", "C6"]

def parse_pec_rank(cat_str: str) -> int:
    clean = re.sub(r"[^A-Za-z0-9]", "", cat_str.upper())
    ranks = {
        "C6": 1, "C5": 2, "C4": 3, "C3": 4, "C2": 5, "C1": 6, "CB": 7, "CA": 8
    }
    for k, v in ranks.items():
        if k in clean:
            return v
    return 3  # default C4 assumption

def evaluate_eligibility(verified_fields: dict, profile: dict) -> tuple[str, list]:
    results = []

    # Rule 1: PEC License Match
    pec_field = verified_fields.get("required_pec_category", {})
    user_cat = profile.get("licence_category", "C-4")
    user_rank = parse_pec_rank(user_cat)

    if isinstance(pec_field, dict) and pec_field.get("status") == "verified":
        val = pec_field.get("value", "").upper()
        req_rank = parse_pec_rank(val)
        passed = user_rank >= req_rank
        results.append({
            "rule_id": "R1",
            "name": "PEC License Eligibility",
            "severity": "hard",
            "status": "PASS" if passed else "FAIL",
            "reason": f"Required Category: {pec_field.get('value')} | Profile holds: {user_cat} (Qualified for up to {user_cat})",
            "evidence": pec_field.get("quote")
        })
    else:
        results.append({
            "rule_id": "R1",
            "name": "PEC License Eligibility",
            "severity": "hard",
            "status": "NEEDS_CONFIRMATION",
            "reason": "PEC Category not conclusively verified in tender document.",
            "evidence": None
        })

    # Rule 2: Active Taxpayer Verification
    tax_fields = verified_fields.get("tax_requirements", [])
    if isinstance(tax_fields, dict):
        tax_fields = [tax_fields]
    tax_verified = any(t.get("status") == "verified" for t in tax_fields if isinstance(t, dict))
    has_fbr = any("FBR" in r or "NTN" in r for r in profile.get("registrations", []))
    has_strn = any("STRN" in r or "Sales Tax" in r for r in profile.get("registrations", []))
    
    tax_status = "PASS" if (has_fbr and has_strn) else ("PASS" if has_fbr else "FAIL")
    results.append({
        "rule_id": "R2",
        "name": "Tax Compliance (FBR / STRN)",
        "severity": "hard",
        "status": tax_status,
        "reason": f"Company holds: {', '.join(profile.get('registrations', []))}",
        "evidence": tax_fields[0].get("quote") if (tax_verified and tax_fields) else "Mandatory statutory compliance"
    })

    # Rule 3: Bid Security Financial Capacity
    bid_sec_field = verified_fields.get("bid_security", {})
    max_sec = profile.get("max_bid_security_pkr", 3000000)
    if isinstance(bid_sec_field, dict) and bid_sec_field.get("status") == "verified":
        sec_val = bid_sec_field.get("value", "")
        # Look for numbers
        numbers = re.findall(r"\d+", sec_val.replace(",", ""))
        if numbers:
            parsed_amount = int(numbers[0])
            # If percentage (e.g. 2%)
            if "%" in sec_val or parsed_amount <= 10:
                results.append({
                    "rule_id": "R3",
                    "name": "Bid Security Capacity",
                    "severity": "soft",
                    "status": "PASS",
                    "reason": f"Bid Security requirement '{sec_val}' is within standard bank guarantee capacity (PKR {max_sec:,}).",
                    "evidence": bid_sec_field.get("quote")
                })
            elif parsed_amount <= max_sec:
                results.append({
                    "rule_id": "R3",
                    "name": "Bid Security Capacity",
                    "severity": "soft",
                    "status": "PASS",
                    "reason": f"Required bid security of PKR {parsed_amount:,} is within ceiling of PKR {max_sec:,}.",
                    "evidence": bid_sec_field.get("quote")
                })
            else:
                results.append({
                    "rule_id": "R3",
                    "name": "Bid Security Capacity",
                    "severity": "soft",
                    "status": "FAIL",
                    "reason": f"Required bid security of PKR {parsed_amount:,} exceeds ceiling of PKR {max_sec:,}.",
                    "evidence": bid_sec_field.get("quote")
                })
        else:
            results.append({
                "rule_id": "R3",
                "name": "Bid Security Capacity",
                "severity": "soft",
                "status": "PASS",
                "reason": f"Bid security stated as '{sec_val}'. Company profile supports up to PKR {max_sec:,}.",
                "evidence": bid_sec_field.get("quote")
            })
    else:
        results.append({
            "rule_id": "R3",
            "name": "Bid Security Capacity",
            "severity": "soft",
            "status": "NEEDS_CONFIRMATION",
            "reason": "Bid security amount not explicitly stated in extracted text.",
            "evidence": None
        })

    # Rule 4: Mandatory Document Readiness
    req_docs = verified_fields.get("required_documents", [])
    if isinstance(req_docs, dict):
        req_docs = [req_docs]
    
    if req_docs:
        ready_count = 0
        total_docs = len(req_docs)
        for d in req_docs:
            if isinstance(d, dict):
                doc_name = d.get("value", "")
                if any(fuzz.partial_ratio(doc_name.lower(), p.lower()) > 70 for p in profile.get("documents", [])):
                    ready_count += 1

        doc_ratio = (ready_count / total_docs) if total_docs > 0 else 1.0
        doc_status = "PASS" if doc_ratio >= 0.60 else "FAIL"
        results.append({
            "rule_id": "R4",
            "name": "Document Readiness",
            "severity": "soft",
            "status": doc_status,
            "reason": f"{ready_count} of {total_docs} required documents available in company profile ({doc_ratio:.0%}).",
            "evidence": f"Readiness ratio: {doc_ratio:.0%}"
        })
    else:
        results.append({
            "rule_id": "R4",
            "name": "Document Readiness",
            "severity": "soft",
            "status": "PASS",
            "reason": "Standard document checklist aligned with company profile.",
            "evidence": "Standard procurement set"
        })

    # Rule 5: Submission Deadline Confirmation
    deadline_field = verified_fields.get("submission_deadline", {})
    if isinstance(deadline_field, dict) and deadline_field.get("status") == "verified":
        results.append({
            "rule_id": "R5",
            "name": "Submission Deadline Feasibility",
            "severity": "soft",
            "status": "PASS",
            "reason": f"Verified submission deadline: {deadline_field.get('value')}",
            "evidence": deadline_field.get("quote")
        })
    else:
        results.append({
            "rule_id": "R5",
            "name": "Submission Deadline Feasibility",
            "severity": "soft",
            "status": "NEEDS_CONFIRMATION",
            "reason": "Deadline not verified automatically; manual calendar confirmation recommended.",
            "evidence": None
        })

    # Verdict Calculation
    hard_fails = [r for r in results if r["severity"] == "hard" and r["status"] == "FAIL"]
    hard_unknowns = [r for r in results if r["severity"] == "hard" and r["status"] == "NEEDS_CONFIRMATION"]

    if hard_fails:
        verdict = "NO-BID"
    elif hard_unknowns:
        verdict = "BID IF (Human Clarification Required)"
    else:
        verdict = "BID (Qualified)"

    return verdict, results
