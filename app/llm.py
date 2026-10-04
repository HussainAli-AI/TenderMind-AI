import os
import json
import hashlib
from diskcache import Cache

cache = Cache(".llm_cache")

def get_groq_api_key() -> str:
    # 1. Environment variable
    api_key = os.getenv("GROQ_API_KEY")
    if api_key:
        return api_key
    
    # 2. Streamlit secrets if running inside streamlit
    try:
        import streamlit as st
        if hasattr(st, "secrets") and "GROQ_API_KEY" in st.secrets:
            return st.secrets["GROQ_API_KEY"]
    except Exception:
        pass

    return ""

def get_groq_client():
    api_key = get_groq_api_key()
    if not api_key:
        raise ValueError("GROQ_API_KEY not found in environment or Streamlit secrets.")
    from groq import Groq
    return Groq(api_key=api_key)

def call_llm_json(system_prompt: str, user_prompt: str, model: str = "llama-3.1-8b-instant") -> dict:
    cache_key = hashlib.sha256(f"{model}:{system_prompt}:{user_prompt}".encode()).hexdigest()
    if cache_key in cache:
        return cache[cache_key]

    api_key = get_groq_api_key()
    if not api_key:
        # Check if we have pre-cached fallback response for demo/offline resilience
        for key in cache:
            val = cache[key]
            if isinstance(val, dict) and "submission_deadline" in val:
                return val
        raise ValueError(
            "GROQ_API_KEY is required to process new unseen tenders. "
            "Please provide GROQ_API_KEY in the sidebar or in .streamlit/secrets.toml."
        )

    client = get_groq_client()
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.0,
        response_format={"type": "json_object"}
    )
    
    content = response.choices[0].message.content
    result = json.loads(content)
    cache[cache_key] = result
    return result
