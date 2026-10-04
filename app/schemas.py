from pydantic import BaseModel, Field
from typing import List, Optional

class ExtractedField(BaseModel):
    value: str = Field(description="Exact value extracted from the text.")
    page: int = Field(default=0, description="1-based page number where the fact was found.")
    quote: str = Field(default="", description="Exact verbatim quote (max 25 words) from the page.")
    status: str = Field(default="unverified", description="verified, ungrounded, or missing")

class TenderExtraction(BaseModel):
    submission_deadline: ExtractedField
    bid_security: ExtractedField
    required_pec_category: ExtractedField
    tax_requirements: List[ExtractedField] = []
    required_documents: List[ExtractedField] = []
    estimated_cost: Optional[ExtractedField] = None

class RuleResult(BaseModel):
    rule_id: str
    rule_name: str
    severity: str  # "hard" or "soft"
    status: str    # "PASS", "FAIL", "NEEDS_CONFIRMATION"
    reason: str
    evidence_quote: Optional[str] = None
