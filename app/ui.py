import streamlit as st
import yaml
import os
import sys
import json
from io import BytesIO

# Ensure app is discoverable on python path
sys.path.insert(0, os.path.abspath("."))

from app.tools.pdf import extract_pdf_pages
from app.graph import build_tender_graph
from app.tools.export import generate_bid_pack_docx
from app.llm import get_groq_api_key

st.set_page_config(
    page_title="TenderMind AI — Autonomous Bid Decision Engine",
    page_icon="📑",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom High-End Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    .stApp {
        background-color: #0B0F17;
    }
    
    /* Hero Banner */
    .hero-container {
        padding: 1.5rem 2rem;
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.9) 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5);
    }
    
    .badge-pill {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        margin-right: 8px;
    }
    .badge-primary { background: rgba(59, 130, 246, 0.2); color: #60A5FA; border: 1px solid rgba(59, 130, 246, 0.3); }
    .badge-success { background: rgba(16, 185, 129, 0.2); color: #34D399; border: 1px solid rgba(16, 185, 129, 0.3); }
    .badge-warning { background: rgba(245, 158, 11, 0.2); color: #FBBF24; border: 1px solid rgba(245, 158, 11, 0.3); }
    .badge-danger { background: rgba(239, 68, 68, 0.2); color: #F87171; border: 1px solid rgba(239, 68, 68, 0.3); }
    
    /* Metric Cards */
    .metric-card {
        background: #161F30;
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 12px;
        padding: 1.2rem;
        text-align: center;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        border-color: rgba(59, 130, 246, 0.4);
    }
    .metric-val {
        font-size: 1.8rem;
        font-weight: 800;
        color: #F8FAFC;
        margin-top: 4px;
    }
    .metric-label {
        font-size: 0.8rem;
        color: #94A3B8;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* Verdict Glow Banners */
    .verdict-banner-pass {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(6, 78, 59, 0.25) 100%);
        border: 1px solid #10B981;
        border-radius: 14px;
        padding: 1.5rem;
        text-align: center;
        color: #34D399;
        margin: 1.5rem 0;
        box-shadow: 0 0 25px rgba(16, 185, 129, 0.2);
    }
    .verdict-banner-fail {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.15) 0%, rgba(127, 29, 29, 0.25) 100%);
        border: 1px solid #EF4444;
        border-radius: 14px;
        padding: 1.5rem;
        text-align: center;
        color: #F87171;
        margin: 1.5rem 0;
        box-shadow: 0 0 25px rgba(239, 68, 68, 0.2);
    }
    .verdict-banner-warn {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.15) 0%, rgba(120, 53, 15, 0.25) 100%);
        border: 1px solid #F59E0B;
        border-radius: 14px;
        padding: 1.5rem;
        text-align: center;
        color: #FBBF24;
        margin: 1.5rem 0;
        box-shadow: 0 0 25px rgba(245, 158, 11, 0.2);
    }
    
    /* Code quote box */
    .quote-box {
        background: #0F172A;
        border-left: 3px solid #3B82F6;
        padding: 10px 14px;
        border-radius: 0 8px 8px 0;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.85rem;
        color: #CBD5E1;
        margin: 6px 0;
    }
</style>
""", unsafe_allow_html=True)

# Default Contractor Profiles
PRESET_PROFILES = {
    "Apex Engineering & Tech (Category C-4)": {
        "company_name": "Apex Engineering & Tech Solutions Pvt Ltd",
        "licence_category": "C-4",
        "turnover_pkr": 85000000,
        "max_bid_security_pkr": 3000000,
        "registrations": ["FBR Active Taxpayer (NTN)", "Sales Tax Registration (STRN)", "PEC Registered (Pakistan Engineering Council)"],
        "documents": [
            "Company Registration Certificate",
            "FBR Tax Clearance Certificate",
            "PEC Valid License",
            "Audited Financial Statements (Last 3 Years)",
            "Past Relevant Experience Proof",
            "Bank Guarantee Capability Letter"
        ]
    },
    "Pioneer Heavy Constructors (Category C-2)": {
        "company_name": "Pioneer Heavy Constructors Ltd",
        "licence_category": "C-2",
        "turnover_pkr": 350000000,
        "max_bid_security_pkr": 15000000,
        "registrations": ["FBR Active Taxpayer (NTN)", "Sales Tax Registration (STRN)", "PEC Registered (Pakistan Engineering Council)"],
        "documents": [
            "Company Registration Certificate",
            "FBR Tax Clearance Certificate",
            "PEC Valid License",
            "Audited Financial Statements (Last 3 Years)",
            "Past Relevant Experience Proof",
            "Bank Guarantee Capability Letter",
            "Machinery Ownership Proof",
            "5-Year Audited Balance Sheets"
        ]
    },
    "Novice Contracting Services (Category C-6)": {
        "company_name": "Novice Local Services LLP",
        "licence_category": "C-6",
        "turnover_pkr": 8000000,
        "max_bid_security_pkr": 500000,
        "registrations": ["FBR Active Taxpayer (NTN)"],
        "documents": [
            "Company Registration Certificate",
            "FBR Tax Clearance Certificate"
        ]
    }
}

# Sidebar
with st.sidebar:
    st.markdown("### 🏢 Contractor Profile Vault")
    selected_preset = st.selectbox(
        "Select Company Profile Preset:",
        list(PRESET_PROFILES.keys()),
        index=0
    )
    profile = PRESET_PROFILES[selected_preset]
    
    st.markdown(f"**Entity:** `{profile['company_name']}`")
    st.markdown(f"**PEC License:** `{profile['licence_category']}`")
    st.markdown(f"**Max Bid Security:** `PKR {profile['max_bid_security_pkr']:,}`")
    
    with st.expander("📁 Verified Credentials & Vault", expanded=False):
        st.caption("Active Registrations:")
        for r in profile["registrations"]:
            st.markdown(f"• {r}")
        st.caption("Document Repository:")
        for d in profile["documents"]:
            st.markdown(f"• {d}")

    st.divider()
    st.markdown("### ⚙️ Engine Settings")
    existing_key = get_groq_api_key()
    groq_api_key_input = st.text_input(
        "Groq Cloud API Key",
        value=existing_key if existing_key else "",
        type="password",
        help="Enter your Groq API key (starts with gsk_). Pre-cached samples work even without a key."
    )
    if groq_api_key_input:
        os.environ["GROQ_API_KEY"] = groq_api_key_input
        st.success("🟢 Groq API Connected (LLaMA-3.1-8B)")
    else:
        st.info("🟡 Running in Fail-Safe Mode (Pre-cached samples enabled)")

    st.markdown("""
    <div style='font-size: 0.75rem; color: #64748B; margin-top: 1rem;'>
    TenderMind AI Agentic Pipeline:
    <br/>• <b>Ingestion:</b> pypdfium2 + Tesseract OCR
    <br/>• <b>Retrieval:</b> BM25 Okapi Lexical Chunker
    <br/>• <b>Reasoning:</b> Groq LLaMA 3.1
    <br/>• <b>Grounding:</b> Deterministic String/Digit Verifier
    <br/>• <b>Orchestration:</b> LangGraph
    </div>
    """, unsafe_allow_html=True)

# Main Page Header
st.markdown("""
<div class="hero-container">
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
        <div>
            <span class="badge-pill badge-primary">LangGraph Multi-Agent</span>
            <span class="badge-pill badge-success">Zero Hallucination</span>
            <span class="badge-pill badge-warning">Groq LLaMA-3.1</span>
            <h1 style="margin: 0.5rem 0 0.2rem 0; font-size: 2.2rem; font-weight: 800; color: #F8FAFC;">
                📑 TenderMind AI
            </h1>
            <p style="margin: 0; color: #94A3B8; font-size: 1.05rem;">
                Autonomous Bid/No-Bid Decision Engine with Verbatim Grounding & DOCX Pack Generation
            </p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Tender Selection or Upload
st.subheader("1. Select or Upload Tender Documentation")
col_src1, col_src2 = st.columns([1, 1])

with col_src1:
    st.markdown("##### 📂 Choose Pre-Warmed Benchmark Tender")
    sample_options = {
        "Sample 1: Civil Highway Works (C-4 Required) -> Expected BID": "data/samples/Tender_01_Civil_Infrastructure_C4_Qualified.pdf",
        "Sample 2: Elevated Flyover Mega Project (C-2 Required) -> Expected NO-BID": "data/samples/Tender_02_Flyover_MegaProject_C2_Disqualified.pdf",
        "Sample 3: Municipal Solar Power Micro-Grid -> Expected BID IF (Clarification)": "data/samples/Tender_03_Municipal_Solar_Power_NeedsClarification.pdf"
    }
    selected_sample_label = st.selectbox("Pre-loaded Tenders for Instant Evaluation:", list(sample_options.keys()))
    use_sample = st.checkbox("Use selected sample tender", value=True)

with col_src2:
    st.markdown("##### 📤 Or Upload Custom Tender PDF")
    uploaded_file = st.file_uploader("Upload RFP, IFB, or Tender Notice (PDF)", type=["pdf"])

# Determine active file bytes and name
active_bytes = None
active_filename = ""

if not use_sample and uploaded_file is not None:
    active_bytes = uploaded_file.read()
    active_filename = uploaded_file.name
elif use_sample:
    sample_path = sample_options[selected_sample_label]
    if os.path.exists(sample_path):
        with open(sample_path, "rb") as f:
            active_bytes = f.read()
        active_filename = os.path.basename(sample_path)
    else:
        st.error(f"Sample file not found at {sample_path}")

if active_bytes:
    st.markdown(f"**Loaded Document:** `{active_filename}` ({len(active_bytes):,} bytes)")
    
    if st.button("🚀 Analyze Tender with Multi-Agent Swarm", type="primary", use_container_width=True):
        progress_bar = st.progress(0, text="Initializing Multi-Agent Graph...")
        
        with st.status("Executing Autonomous LangGraph Orchestration...", expanded=True) as status_box:
            # Step 1: Ingestion
            status_box.write("📄 **[Ingestion Agent]** Parsing document structure via pypdfium2 / OCR...")
            progress_bar.progress(20, text="Ingesting document pages...")
            pages = extract_pdf_pages(active_bytes)
            status_box.write(f"✅ Ingested **{len(pages)} page(s)** into memory.")
            
            # Step 2 & 3: Retrieval & Extraction via LangGraph
            status_box.write("🔍 **[Retrieval Agent]** Indexing chunks via BM25 Okapi & extracting target sections...")
            progress_bar.progress(45, text="Running BM25 retrieval & Groq LLaMA-3.1 inference...")
            
            status_box.write("⚡ **[LLM Node]** Executing single-pass multi-field extraction on Groq Cloud...")
            progress_bar.progress(70, text="Executing single-pass JSON extraction...")
            
            # Step 4: Grounding Verifier & Rules
            status_box.write("🛡️ **[Grounding Verifier]** Enforcing zero-hallucination verbatim string & digit checks...")
            status_box.write("⚖️ **[Rules Engine]** Auditing statutory PEC, Tax (FBR/STRN), and financial constraints...")
            progress_bar.progress(90, text="Auditing compliance rules...")
            
            initial_state = {
                "pages": pages,
                "profile": profile,
                "retriever": None,
                "raw_extraction": {},
                "verified_extraction": {},
                "verdict": "",
                "rule_results": []
            }
            
            graph = build_tender_graph()
            final_state = graph.invoke(initial_state)
            
            progress_bar.progress(100, text="Analysis Complete!")
            status_box.update(label="Autonomous Decision Pipeline Executed Successfully!", state="complete", expanded=False)

        # Stash in session state for tab switches
        st.session_state["tender_results"] = {
            "final_state": final_state,
            "filename": active_filename,
            "profile": profile
        }

# Render Results if available
if "tender_results" in st.session_state:
    res = st.session_state["tender_results"]
    state = res["final_state"]
    verdict = state["verdict"]
    verified = state["verified_extraction"]
    rules = state["rule_results"]
    prof = res["profile"]
    
    st.divider()
    
    # 1. Glowing Hero Verdict Banner
    if "BID (Qualified)" in verdict:
        st.markdown(f"""
        <div class="verdict-banner-pass">
            <h2 style="margin: 0; font-size: 2rem; font-weight: 800;">🟢 VERDICT: BID (QUALIFIED)</h2>
            <p style="margin: 0.5rem 0 0 0; font-size: 1.1rem; color: #A7F3D0;">
                All mandatory statutory, technical (PEC {prof['licence_category']}), and financial constraints verified successfully.
            </p>
        </div>
        """, unsafe_allow_html=True)
    elif "NO-BID" in verdict:
        st.markdown(f"""
        <div class="verdict-banner-fail">
            <h2 style="margin: 0; font-size: 2rem; font-weight: 800;">🔴 VERDICT: NO-BID (DISQUALIFIED)</h2>
            <p style="margin: 0.5rem 0 0 0; font-size: 1.1rem; color: #FECACA;">
                Disqualifying criteria detected. Bidding without rectification will lead to statutory forfeiture or technical rejection.
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="verdict-banner-warn">
            <h2 style="margin: 0; font-size: 2rem; font-weight: 800;">🟡 VERDICT: BID IF (CLARIFICATION REQUIRED)</h2>
            <p style="margin: 0.5rem 0 0 0; font-size: 1.1rem; color: #FDE68A;">
                Core qualifications pass, but ambiguous specifications require formal pre-bid clarification.
            </p>
        </div>
        """, unsafe_allow_html=True)

    # 2. Executive KPI Cards
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    
    pass_rules_count = sum(1 for r in rules if r["status"] == "PASS")
    total_rules = len(rules)
    
    # Verification Ratio
    total_fields = 0
    verified_fields_count = 0
    for k, v in verified.items():
        if isinstance(v, dict):
            total_fields += 1
            if v.get("status") == "verified":
                verified_fields_count += 1
        elif isinstance(v, list):
            for item in v:
                if isinstance(item, dict):
                    total_fields += 1
                    if item.get("status") == "verified":
                        verified_fields_count += 1

    verif_rate = (verified_fields_count / total_fields * 100) if total_fields else 100

    with kpi1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Rules Evaluation</div>
            <div class="metric-val">{pass_rules_count} / {total_rules}</div>
        </div>
        """, unsafe_allow_html=True)

    with kpi2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Grounding Confidence</div>
            <div class="metric-val">{verif_rate:.0f}%</div>
        </div>
        """, unsafe_allow_html=True)

    with kpi3:
        pec_stat = next((r["status"] for r in rules if r["rule_id"] == "R1"), "N/A")
        color = "#34D399" if pec_stat == "PASS" else ("#F87171" if pec_stat == "FAIL" else "#FBBF24")
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">PEC Match ({prof['licence_category']})</div>
            <div class="metric-val" style="color: {color};">{pec_stat}</div>
        </div>
        """, unsafe_allow_html=True)

    with kpi4:
        doc_stat = next((r["status"] for r in rules if r["rule_id"] == "R4"), "N/A")
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Document Readiness</div>
            <div class="metric-val">{doc_stat}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br/>", unsafe_allow_html=True)

    # 3. Tabbed Deep-Dive Sections
    tab_rules, tab_evidence, tab_docs, tab_raw = st.tabs([
        "⚖️ Eligibility Rules Audit",
        "🛡️ Grounded Evidence & Quotes",
        "📁 Document Readiness Vault",
        "🔍 Raw Execution Trace"
    ])

    with tab_rules:
        st.subheader("Deterministic Rule-Engine Breakdown")
        for r in rules:
            status_icon = "🟢" if r["status"] == "PASS" else ("🔴" if r["status"] == "FAIL" else "🟡")
            sev_badge = "HARD CONSTRAINT" if r["severity"] == "hard" else "SOFT CONSTRAINT"
            
            with st.container():
                c_head, c_status = st.columns([4, 1])
                c_head.markdown(f"**{status_icon} [{r['rule_id']}] {r['name']}** — `{sev_badge}`")
                c_status.markdown(f"**Status:** `{r['status']}`")
                st.write(f"**Audit Findings:** {r['reason']}")
                if r.get("evidence"):
                    st.markdown(f"<div class='quote-box'>Grounding Evidence: {r['evidence']}</div>", unsafe_allow_html=True)
                st.divider()

    with tab_evidence:
        st.subheader("Anti-Hallucination Grounding Audit")
        st.caption("Every procurement fact must be grounded in raw PDF text with page number and verbatim excerpt.")
        
        for k, v in verified.items():
            clean_title = k.replace("_", " ").title()
            if isinstance(v, dict):
                st_badge = v.get("status", "N/A")
                icon = "✅" if st_badge == "verified" else ("❌" if st_badge == "ungrounded" else "⚪")
                
                with st.expander(f"{icon} {clean_title}: {v.get('value', 'Not Specified')} (Page {v.get('page')}) [{st_badge.upper()}]"):
                    st.write(f"**Value:** `{v.get('value')}`")
                    st.write(f"**Page Number:** {v.get('page')}")
                    st.write(f"**Grounding Status:** `{st_badge.upper()}`")
                    if v.get("quote"):
                        st.markdown(f"**Verbatim Quote from Page {v.get('page')}:**")
                        st.markdown(f"<div class='quote-box'>\"{v.get('quote')}\"</div>", unsafe_allow_html=True)
            elif isinstance(v, list):
                st.markdown(f"##### {clean_title} ({len(v)} Items)")
                for item in v:
                    if isinstance(item, dict):
                        st_badge = item.get("status", "N/A")
                        icon = "✅" if st_badge == "verified" else ("❌" if st_badge == "ungrounded" else "⚪")
                        st.markdown(f"- {icon} **{item.get('value')}** (Page {item.get('page')}) — `{st_badge.upper()}`")
                        if item.get("quote"):
                            st.markdown(f"<div class='quote-box'>\"{item.get('quote')}\"</div>", unsafe_allow_html=True)

    with tab_docs:
        st.subheader("Mandatory Tender Documents vs. Company Repository")
        req_docs = verified.get("required_documents", [])
        if isinstance(req_docs, dict):
            req_docs = [req_docs]
            
        c_req, c_repo = st.columns(2)
        with c_req:
            st.markdown("##### 📄 Required in Tender Notice")
            if req_docs:
                for idx, doc_item in enumerate(req_docs):
                    if isinstance(doc_item, dict):
                        st.checkbox(f"{doc_item.get('value')}", value=True, key=f"req_doc_{idx}")
            else:
                st.info("No specific mandatory document list specified.")

        with c_repo:
            st.markdown(f"##### 🗄️ Available in {prof['company_name']}")
            for p_doc in prof.get("documents", []):
                st.markdown(f"✅ `{p_doc}`")

    with tab_raw:
        st.subheader("Inspection & Graph Execution Trace")
        st.json(state["raw_extraction"])

    # 4. Export Bid Pack
    st.divider()
    st.subheader("📥 Export Official Bid Submission Pack")
    st.write("Generate an executive compliance document in `.docx` format containing all verified data, rule audits, and statutory compliance declarations.")
    
    docx_stream = generate_bid_pack_docx(verdict, verified, rules, prof)
    st.download_button(
        label="📥 Download Executive Bid Pack (.docx)",
        data=docx_stream,
        file_name=f"TenderMind_Bid_Pack_{active_filename.replace('.pdf', '')}.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        type="primary"
    )
