# 📑 TenderMind AI — Autonomous Bid/No-Bid Decision Engine

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](THIRD_PARTY_LICENSES.md)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-3776AB.svg?logo=python&logoColor=white)](https://python.org)
[![Groq Cloud](https://img.shields.io/badge/Groq-LLaMA--3.1--8B-F05A28.svg)](https://groq.com)
[![LangGraph](https://img.shields.io/badge/Orchestrator-LangGraph-FF4F00.svg)](https://github.com/langchain-ai/langgraph)

> **Autonomous procurement compliance extraction, quote verification, and bid suitability engine for public procurement in emerging markets.**

---

## 📌 Executive Summary & Problem Statement

In emerging markets like Pakistan, public procurement accounts for billions of dollars annually across departments like C&W, NHA, DHA, and WAPDA. However:
- **Over 60% of contractors** fail to bid or get disqualified due to dense, unstructured, 80+ page tender documents and tight compliance rules.
- Contractors spend **10 to 14 days** reviewing terms, only to discover disqualification due to a minor PEC code or bank guarantee restriction.
- Conventional LLM wrappers suffer from **hallucination risk**: inventing compliance codes or missing penalty clauses.

**TenderMind AI** turns a 3-day manual review into a **3-second deterministic decision**, backed by page-accurate verbatim quotes and plain-code anti-hallucination verification.

---

## 🏗️ Multi-Agent Architecture

```text
[ Upload PDF / Pick Benchmark ]
│
▼
[ Ingestion Agent: pypdfium2 + OCR ] ──► Extracted Page Map
│
▼
[ Retrieval Agent: BM25 Okapi ] ───────► Target Procurement Chunks
│
▼
[ Reasoning Node: Groq LLaMA 3.1 ] ────► Single-Pass Structured JSON
│
▼
[ Grounding Verifier Agent ] ──────────► Verbatim String & Digit Check (Rejects Hallucinations)
│
▼
[ Rules Engine: Deterministic ] ───────► PEC / Tax / Financial Checks ──► BID / NO-BID Verdict
│
▼
[ Streamlit Web UI ] ──────────────────► Interactive Trace + Audit Matrix + DOCX Bid Pack
```

### Key Pillars
1. **Single-Pass Groq Inference:** Replaces slow sequential LLM calls with a single multi-field extraction schema running on Groq Cloud (`llama-3.1-8b-instant`). Execution drops from 90 seconds to sub-3 seconds.
2. **Deterministic Anti-Hallucination Verifier:** Plain-code Verifier validates cited quotes against raw page strings and rejects ungrounded numbers.
3. **Deterministic Rules Engine:** Implements Pakistan Engineering Council (PEC) category hierarchy (C-6 to C-A), FBR Active Taxpayer (NTN/STRN), and financial capacity checks.
4. **Fail-Safe Offline Cache:** Pre-warmed disk cache for benchmark tenders ensures instant, reliable live demos even if API keys disconnect.

---

## 📂 Project Structure

```text
tendermind-ai/
├── .streamlit/
│   ├── config.toml           # Modern dark UI theme configuration
│   └── secrets.toml          # Groq Cloud API secrets
├── app/
│   ├── __init__.py
│   ├── ui.py                 # Streamlit frontend & multi-agent trace UI
│   ├── graph.py              # LangGraph StateGraph orchestrator
│   ├── llm.py                # High-speed Groq client + diskcache wrapper
│   ├── schemas.py            # Pydantic data schemas
│   ├── agents/
│   │   ├── extractor.py      # Single-pass multi-field extractor
│   │   ├── verifier.py       # Plain-code anti-hallucination verifier
│   │   └── rules.py          # Deterministic bid/no-bid rules engine
│   └── tools/
│       ├── pdf.py            # pypdfium2 + pytesseract OCR fallback
│       ├── retrieval.py      # Fast BM25 chunk retriever
│       └── export.py         # Executive DOCX bid pack generator
├── config/
│   ├── fields.yaml           # Procurement field definitions
│   └── company_profile.yaml  # Synthetic contractor profile
├── data/
│   └── samples/              # Pre-generated benchmark tender PDFs
├── scripts/
│   ├── generate_samples.py   # Script to generate benchmark tenders
│   └── warm_cache.py         # Script to pre-populate .llm_cache
├── tests/
│   └── test_pipeline.py      # End-to-end automated unit tests
├── .llm_cache/               # Pre-warmed diskcache store
├── packages.txt              # Debian packages for Streamlit Cloud (Tesseract OCR)
├── requirements.txt          # Python library dependencies
└── THIRD_PARTY_LICENSES.md   # Open-source compliance
```

---

## 🚀 Quickstart & Local Installation

### 1. Clone & Set Up Virtual Environment
```bash
git clone https://github.com/your-username/tendermind-ai.git
cd tendermind-ai
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Groq API Key (Optional for Samples)
Add your Groq API key in `.streamlit/secrets.toml`:
```toml
GROQ_API_KEY = "gsk_your_groq_api_key_here"
```
*(Or set `export GROQ_API_KEY="gsk_..."` or input it in the UI sidebar).*

### 4. Run the Application
```bash
streamlit run app/ui.py
```

### 5. Run the Test Suite
```bash
python -m unittest tests/test_pipeline.py
```

---

## ☁️ Streamlit Community Cloud Deployment

1. Push this repository to GitHub.
2. Log into [share.streamlit.io](https://share.streamlit.io) and click **"New app"**.
3. Select your repository, set the branch to `main`, and the main file path to:
   ```text
   app/ui.py
   ```
4. Click **Advanced settings...** and add your Groq API key to **Secrets**:
   ```toml
   GROQ_API_KEY = "gsk_your_groq_api_key_here"
   ```
5. Click **Deploy**. Streamlit Cloud detects `packages.txt` for Tesseract OCR, installs all packages from `requirements.txt`, and goes live in under 2 minutes.

---

## 🎤 4-Minute Presentation Pitch Script

- **0:00–0:45 (The Problem):** In emerging markets, over 60% of contractors fail to bid or get disqualified due to dense, unstructured 80-page tender documents and tight compliance rules. Finding out you are disqualified after spending weeks drafting a bid is an expensive disaster.
- **0:45–1:45 (The Solution & Agentic Architecture):** Meet TenderMind AI. Rather than being a superficial wrapper, it executes an autonomous multi-agent pipeline using LangGraph: Ingestion (pypdfium2/OCR) → BM25 Retrieval → Single-pass Groq LLaMA-3.1 → Deterministic Grounding Verifier → Procurement Rules Engine.
- **1:45–3:00 (Live Interactive Demo):** Demonstrate 1-click evaluation of a benchmark tender. Show real-time progress trace, glowing BID/NO-BID verdict, verified citations, and instant DOCX Bid Pack download.
- **3:00–4:00 (Business Model & Vision):** SaaS subscription for contractors and suppliers. TenderMind AI acts as the procurement gateway, turning a 3-day manual review into a 3-second verified decision.
