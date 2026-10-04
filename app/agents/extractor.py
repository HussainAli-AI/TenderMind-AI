from app.llm import call_llm_json

EXTRACTION_SYSTEM_PROMPT = """
You are a senior government procurement expert. Extract procurement facts strictly from the provided tender context.
Never assume, guess, or extrapolate.
If a requirement is not mentioned or found in the text, set value to "Not Specified", page to 0, and quote to "".

Return JSON matching this exact structure:
{
  "submission_deadline": {"value": "...", "page": 1, "quote": "..."},
  "bid_security": {"value": "...", "page": 1, "quote": "..."},
  "required_pec_category": {"value": "...", "page": 1, "quote": "..."},
  "tax_requirements": [{"value": "...", "page": 1, "quote": "..."}],
  "required_documents": [{"value": "...", "page": 1, "quote": "..."}],
  "estimated_cost": {"value": "...", "page": 1, "quote": "..."}
}

Every 'quote' MUST be an exact verbatim substring from the cited page text (max 25 words).
"""

def run_extractor(context_chunks: list) -> dict:
    context_str = "\n\n".join(f"[Page {c['page']}]\n{c['text']}" for c in context_chunks)
    user_prompt = f"Extract all procurement conditions from the context below:\n\n<tender_context>\n{context_str}\n</tender_context>"
    return call_llm_json(EXTRACTION_SYSTEM_PROMPT, user_prompt)
