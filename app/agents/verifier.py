import re
from rapidfuzz import fuzz

def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()

def extract_numbers(text: str) -> set:
    return set(re.findall(r"\d+", text))

def verify_single_field(field_data: dict, page_map: dict) -> dict:
    if not isinstance(field_data, dict):
        return {"value": str(field_data), "page": 0, "quote": "", "status": "missing"}

    page_num = field_data.get("page", 0)
    quote = field_data.get("quote", "").strip()
    value = field_data.get("value", "").strip()

    if page_num == 0 or not quote or value.lower() in ("not specified", "none", "n/a", ""):
        field_data["status"] = "missing"
        return field_data

    page = page_map.get(page_num)
    if not page:
        field_data["status"] = "ungrounded"
        return field_data

    page_clean = normalize(page.text)
    quote_clean = normalize(quote)

    # 1. Fuzzy match quote on cited page
    match_ratio = fuzz.partial_ratio(quote_clean, page_clean)
    if match_ratio < 75:
        field_data["status"] = "ungrounded"
        return field_data

    # 2. Hard check: Digits in the quote must exist in raw page text
    quote_digits = extract_numbers(quote)
    page_digits = extract_numbers(page.text)
    if not quote_digits.issubset(page_digits):
        field_data["status"] = "ungrounded"
        return field_data

    field_data["status"] = "verified"
    return field_data

def run_verifier(raw_fields: dict, pages: list) -> dict:
    page_map = {p.page_num: p for p in pages}
    verified_fields = {}

    for k, v in raw_fields.items():
        if isinstance(v, list):
            verified_fields[k] = [verify_single_field(item, page_map) for item in v if isinstance(item, dict)]
        elif isinstance(v, dict):
            verified_fields[k] = verify_single_field(v, page_map)
        else:
            verified_fields[k] = v

    return verified_fields
