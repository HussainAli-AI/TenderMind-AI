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

def get_best_model(client) -> str:
    try:
        available = [m.id for m in client.models.list().data]
        priority_models = [
            "qwen/qwen3.8-27b",
            "openai/gpt-oss-120b",
            "allam-2-7b",
            "openai/gpt-oss-20b",
            "llama-3.1-8b-instant",
            "llama-3.3-70b-versatile"
        ]
        for p in priority_models:
            if p in available:
                return p
        if available:
            return available[0]
    except Exception:
        pass
    return "qwen/qwen3.8-27b"

def call_llm_json(system_prompt: str, user_prompt: str, model: str = None) -> dict:
    cache_key = hashlib.sha256(f"{system_prompt}:{user_prompt}".encode()).hexdigest()
    if cache_key in cache:
        return cache[cache_key]

    api_key = get_groq_api_key()
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY is required to process tender documents live. "
            "Please provide GROQ_API_KEY in .streamlit/secrets.toml."
        )

    client = get_groq_client()
    
    # Query live available models from Groq
    available = []
    try:
        available = [m.id for m in client.models.list().data]
    except Exception:
        pass

    candidates = []
    if model and model in available:
        candidates.append(model)
    
    preferred_order = [
        "qwen/qwen3.8-27b",
        "openai/gpt-oss-120b",
        "allam-2-7b",
        "openai/gpt-oss-20b",
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant"
    ]
    for p in preferred_order:
        if p in available and p not in candidates:
            candidates.append(p)
    
    # Fallback to any remaining available chat model
    for a in available:
        if a not in candidates and ("whisper" not in a and "guard" not in a):
            candidates.append(a)
            
    if not candidates:
        candidates = ["qwen/qwen3.8-27b", "openai/gpt-oss-20b", "llama-3.1-8b-instant"]

    last_err = None
    for selected_model in candidates:
        try:
            response = client.chat.completions.create(
                model=selected_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.0,
                response_format={"type": "json_object"}
            )
            content = response.choices[0].message.content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            
            result = json.loads(content.strip())
            cache[cache_key] = result
            return result
        except Exception as e:
            last_err = e
            continue

    raise RuntimeError(f"All candidate Groq models failed. Last error: {last_err}")
