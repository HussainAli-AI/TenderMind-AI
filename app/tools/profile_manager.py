import os
import json

CUSTOM_PROFILES_FILE = "config/custom_profiles.json"

DEFAULT_PROFILES = {
    "Apex Engineering & Tech (PEC C-4)": {
        "company_name": "Apex Engineering & Tech Solutions Pvt Ltd",
        "licence_category": "C-4",
        "turnover_pkr": 85000000,
        "max_bid_security_pkr": 3000000,
        "registrations": [
            "FBR Active Taxpayer (NTN)",
            "Sales Tax Registration (STRN)",
            "PEC Registered (Pakistan Engineering Council)"
        ],
        "documents": [
            "Company Registration Certificate",
            "FBR Tax Clearance Certificate",
            "PEC Valid License",
            "Audited Financial Statements (Last 3 Years)",
            "Past Relevant Experience Proof",
            "Bank Guarantee Capability Letter"
        ],
        "is_custom": False
    },
    "Pioneer Heavy Constructors (PEC C-2)": {
        "company_name": "Pioneer Heavy Constructors Ltd",
        "licence_category": "C-2",
        "turnover_pkr": 350000000,
        "max_bid_security_pkr": 15000000,
        "registrations": [
            "FBR Active Taxpayer (NTN)",
            "Sales Tax Registration (STRN)",
            "PEC Registered (Pakistan Engineering Council)"
        ],
        "documents": [
            "Company Registration Certificate",
            "FBR Tax Clearance Certificate",
            "PEC Valid License",
            "Audited Financial Statements (Last 3 Years)",
            "Past Relevant Experience Proof",
            "Bank Guarantee Capability Letter",
            "Machinery Ownership Proof",
            "5-Year Audited Balance Sheets"
        ],
        "is_custom": False
    },
    "Novice Local Services (PEC C-6)": {
        "company_name": "Novice Local Services LLP",
        "licence_category": "C-6",
        "turnover_pkr": 8000000,
        "max_bid_security_pkr": 500000,
        "registrations": [
            "FBR Active Taxpayer (NTN)"
        ],
        "documents": [
            "Company Registration Certificate",
            "FBR Tax Clearance Certificate"
        ],
        "is_custom": False
    }
}

def load_custom_profiles() -> dict:
    if os.path.exists(CUSTOM_PROFILES_FILE):
        try:
            with open(CUSTOM_PROFILES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def get_all_profiles() -> dict:
    profiles = dict(DEFAULT_PROFILES)
    custom = load_custom_profiles()
    profiles.update(custom)
    return profiles

def save_custom_profile(key: str, profile_data: dict) -> None:
    os.makedirs(os.path.dirname(CUSTOM_PROFILES_FILE), exist_ok=True)
    custom = load_custom_profiles()
    profile_data["is_custom"] = True
    custom[key] = profile_data
    with open(CUSTOM_PROFILES_FILE, "w", encoding="utf-8") as f:
        json.dump(custom, f, indent=2)

def delete_custom_profile(key: str) -> bool:
    custom = load_custom_profiles()
    if key in custom:
        del custom[key]
        with open(CUSTOM_PROFILES_FILE, "w", encoding="utf-8") as f:
            json.dump(custom, f, indent=2)
        return True
    return False
