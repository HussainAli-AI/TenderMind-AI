# TenderMind AI — Fast-Track Technical Implementation & Deployment Plan

**Target Build Time:** 4–5 Hours (Antigravity-optimized)  
**Deployment Target:** Streamlit Community Cloud + GitHub  
**Runtime Engine:** Groq Cloud API (`llama-3.1-8b-instant`) with local disk caching fallback  

---

## 1. Zero-Bottleneck Architecture & Strategy

To build, verify, and deploy within a fast hackathon window, all non-essential architectural friction is eliminated:

1. **Unified Extraction Call:** Replaces sequential single-field calls with a single multi-field extraction schema. Execution drops from 90 seconds to under 3 seconds.
2. **Cloud Inference via Groq:** Bypasses local model memory issues entirely. Runs effortlessly within Streamlit Cloud’s 1 GB RAM limit with zero timeout risk.
3. **Streamlit Cloud OCR Ready:** Includes `packages.txt` so Tesseract installs cleanly in the Debian container.
4. **Deterministic Anti-Hallucination:** Plain-code Verifier validates quotes against raw page strings and blocks ungrounded numbers.
5. **Fail-Safe Sample Cache:** Pre-caches sample tenders into `.llm_cache` so the live demo runs instantly even if API keys disconnect or rate-limit during judging.

```text
[ Upload PDF / Pick Sample ]
│
▼
[ pypdfium2 / OCR ] ──► Extracted Page Map
│
▼
[ Hybrid BM25 ] ────► Top Relevant Chunks
│
▼
[ Groq LLM Node ] ───► Single-Pass JSON (Fields + Page + Quote)
│
▼
[ Verifier Agent ] ───► Plain-Code Grounding Check (Rejects Hallucinations)
│
▼
[ Rules Engine ] ────► Hard/Soft Constraints ──► BID / NO-BID Verdict
│
▼
[ Streamlit UI ] ────► Visual Trace + Document Checklist + DOCX Export
```

---

## 2. Repository Layout

```text
tendermind-ai/
├── .streamlit/
│   ├── config.toml       # Modern dark theme & typography
│   └── secrets.toml      # Local secrets (GROQ_API_KEY)
├── app/
│   ├── __init__.py
│   ├── ui.py             # Streamlit Frontend & trace renderer
│   ├── graph.py          # LangGraph flow orchestrator
│   ├── llm.py            # Groq client + diskcache wrapper
│   ├── schemas.py        # Pydantic data schemas
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── extractor.py  # Single-pass multi-field extractor
│   │   ├── verifier.py   # Deterministic grounding validator
│   │   └── rules.py      # Bid/No-Bid deterministic engine
│   └── tools/
│       ├── __init__.py
│       ├── pdf.py        # pypdfium2 + pytesseract fallback
│       ├── retrieval.py  # BM25 fast retriever
│       └── export.py     # python-docx bid pack generator
├── config/
│   ├── fields.yaml       # Extracted fields & prompt definitions
│   └── company_profile.yaml # Synthetic contractor eligibility profile
├── data/
│   └── samples/          # Sample tender PDFs
├── .llm_cache/           # Pre-warmed cache directory
├── packages.txt          # Linux dependencies for Streamlit Cloud
├── requirements.txt      # Python dependencies
├── README.md             # Setup guide and investor overview
└── THIRD_PARTY_LICENSES.md # Open-source compliance
```
