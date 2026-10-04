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
    page_title="TenderMind AI — Autonomous Bid/No-Bid Decision Engine",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# High-End Aesthetics & Custom Design Tokens
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    .stApp {
        background: radial-gradient(circle at 15% 15%, #0d1527 0%, #070a12 100%);
        color: #F1F5F9;
    }
    
    /* Top Brand Hero */
    .hero-container {
        padding: 2.2rem 2.5rem;
        background: linear-gradient(135deg, rgba(22, 31, 48, 0.75) 0%, rgba(11, 15, 23, 0.95) 100%);
        border: 1px solid rgba(59, 130, 246, 0.25);
        border-radius: 20px;
        margin-bottom: 2rem;
        box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.7), inset 0 1px 0 rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(16px);
        position: relative;
        overflow: hidden;
    }
    .hero-container::after {
        content: "";
        position: absolute;
        top: -60px;
        right: -60px;
        width: 180px;
        height: 180px;
        background: radial-gradient(circle, rgba(59, 130, 246, 0.3) 0%, rgba(0,0,0,0) 70%);
        border-radius: 50%;
        pointer-events: none;
    }
    
    .badge-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 5px 14px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        margin-right: 8px;
        margin-bottom: 6px;
    }
    .badge-primary { 
        background: rgba(59, 130, 246, 0.18); 
        color: #93C5FD; 
        border: 1px solid rgba(99, 102, 241, 0.35); 
        box-shadow: 0 0 12px rgba(59, 130, 246, 0.2);
    }
    .badge-success { 
        background: rgba(16, 185, 129, 0.18); 
        color: #6EE7B7; 
        border: 1px solid rgba(16, 185, 129, 0.35); 
        box-shadow: 0 0 12px rgba(16, 185, 129, 0.15);
    }
    .badge-purple { 
        background: rgba(168, 85, 247, 0.18); 
        color: #D8B4FE; 
        border: 1px solid rgba(168, 85, 247, 0.35); 
        box-shadow: 0 0 12px rgba(168, 85, 247, 0.15);
    }
    
    /* Executive Metric Tiles */
    .metric-card {
        background: linear-gradient(145deg, rgba(22, 31, 48, 0.8) 0%, rgba(15, 23, 42, 0.95) 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 1.4rem;
        text-align: center;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4);
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        backdrop-filter: blur(12px);
    }
    .metric-card:hover {
        transform: translateY(-4px);
        border-color: rgba(99, 102, 241, 0.5);
        box-shadow: 0 15px 30px -5px rgba(59, 130, 246, 0.25);
    }
    .metric-val {
        font-family: 'Outfit', sans-serif;
        font-size: 2.1rem;
        font-weight: 800;
        color: #F8FAFC;
        margin-top: 4px;
        letter-spacing: -0.02em;
    }
    .metric-label {
        font-size: 0.75rem;
        color: #94A3B8;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }
    
    /* Glowing Hero Verdict Banners */
    .verdict-banner-pass {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.18) 0%, rgba(5, 46, 35, 0.4) 100%);
        border: 1.5px solid #10B981;
        border-radius: 18px;
        padding: 2rem;
        text-align: center;
        color: #34D399;
        margin: 2rem 0;
        box-shadow: 0 0 35px rgba(16, 185, 129, 0.25), inset 0 1px 0 rgba(255, 255, 255, 0.15);
    }
    .verdict-banner-fail {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.18) 0%, rgba(69, 10, 10, 0.4) 100%);
        border: 1.5px solid #EF4444;
        border-radius: 18px;
        padding: 2rem;
        text-align: center;
        color: #F87171;
        margin: 2rem 0;
        box-shadow: 0 0 35px rgba(239, 68, 68, 0.25), inset 0 1px 0 rgba(255, 255, 255, 0.15);
    }
    .verdict-banner-warn {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.18) 0%, rgba(69, 26, 3, 0.4) 100%);
        border: 1.5px solid #F59E0B;
        border-radius: 18px;
        padding: 2rem;
        text-align: center;
        color: #FBBF24;
        margin: 2rem 0;
        box-shadow: 0 0 35px rgba(245, 158, 11, 0.25), inset 0 1px 0 rgba(255, 255, 255, 0.15);
    }
    
    /* Code quote box */
    .quote-box {
        background: #0B1120;
        border-left: 3px solid #3B82F6;
        padding: 12px 16px;
        border-radius: 0 10px 10px 0;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.85rem;
        color: #E2E8F0;
        margin: 8px 0;
        line-height: 1.5;
        border-top: 1px solid rgba(255,255,255,0.04);
        border-bottom: 1px solid rgba(255,255,255,0.04);
        border-right: 1px solid rgba(255,255,255,0.04);
    }
    
    /* Sidebar Profile Card */
    .profile-card {
        background: linear-gradient(145deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.9) 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 1rem 1.2rem;
        margin: 1rem 0;
    }
    
    /* Glass Panel */
    .glass-panel {
        background: rgba(22, 31, 48, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 14px;
        padding: 1.2rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Contractor Profiles
PRESET_PROFILES = {
    "Apex Engineering & Tech (PEC C-4)": {
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
    "Pioneer Heavy Constructors (PEC C-2)": {
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
    "Novice Local Services (PEC C-6)": {
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

# Sidebar: Enterprise Brand & Contractor Profile Vault
with st.sidebar:
    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(59,130,246,0.15), rgba(99,102,241,0.25)); border: 1px solid rgba(99,102,241,0.35); padding: 16px; border-radius: 14px; margin-bottom: 1.2rem; box-shadow: 0 4px 15px rgba(0,0,0,0.3);">
        <div style="display: flex; align-items: center; gap: 10px;">
            <div style="font-size: 1.8rem; background: rgba(59,130,246,0.2); padding: 6px; border-radius: 10px; border: 1px solid rgba(59,130,246,0.4);">🏛️</div>
            <div>
                <div style="font-family: 'Outfit', sans-serif; font-weight: 800; font-size: 1.25rem; color: #F8FAFC; letter-spacing: -0.01em;">TenderMind AI</div>
                <div style="font-size: 0.72rem; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600;">Autonomous Bid Intelligence</div>
            </div>
        </div>
        <div style="display: flex; align-items: center; gap: 8px; margin-top: 12px; padding-top: 10px; border-top: 1px solid rgba(255,255,255,0.08);">
            <span style="height: 8px; width: 8px; background-color: #10B981; border-radius: 50%; display: inline-block; box-shadow: 0 0 10px #10B981;"></span>
            <span style="font-size: 0.75rem; color: #34D399; font-weight: 700; letter-spacing: 0.03em;">SWARM ENGINE READY</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("#### 🏢 Active Contractor Profile")
    selected_preset = st.selectbox(
        "Switch Contractor Identity:",
        list(PRESET_PROFILES.keys()),
        index=0,
        label_visibility="collapsed"
    )
    profile = PRESET_PROFILES[selected_preset]
    
    st.markdown(f"""
    <div class="profile-card">
        <div style="font-size: 0.8rem; color: #94A3B8; font-weight: 600; text-transform: uppercase;">Company Name</div>
        <div style="font-weight: 700; font-size: 0.95rem; color: #F8FAFC; margin-bottom: 8px;">{profile['company_name']}</div>
        
        <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 6px; padding: 6px 0; border-top: 1px solid rgba(255,255,255,0.06);">
            <span style="font-size: 0.8rem; color: #94A3B8;">PEC License:</span>
            <span style="font-weight: 800; color: #60A5FA; background: rgba(59,130,246,0.15); padding: 2px 8px; border-radius: 6px; font-size: 0.85rem; border: 1px solid rgba(59,130,246,0.3);">{profile['licence_category']}</span>
        </div>
        <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 4px;">
            <span style="font-size: 0.8rem; color: #94A3B8;">Max Bid Security:</span>
            <span style="font-weight: 600; color: #E2E8F0; font-size: 0.85rem;">PKR {profile['max_bid_security_pkr']:,}</span>
        </div>
        <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 4px;">
            <span style="font-size: 0.8rem; color: #94A3B8;">Annual Turnover:</span>
            <span style="font-weight: 600; color: #E2E8F0; font-size: 0.85rem;">PKR {profile['turnover_pkr']:,}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander("📁 Verified Credentials & Vault Repository", expanded=False):
        st.markdown("**Tax Registrations:**")
        for r in profile["registrations"]:
            st.markdown(f"• `{r}`")
        st.markdown("**Documents in Vault:**")
        for d in profile["documents"]:
            st.markdown(f"• `{d}`")

    st.markdown("""
    <div style="margin-top: 1.5rem; padding: 12px; background: rgba(15,23,42,0.6); border-radius: 10px; border: 1px solid rgba(255,255,255,0.05); font-size: 0.72rem; color: #64748B; line-height: 1.6;">
        <b style="color: #94A3B8;">LangGraph Multi-Agent Stack:</b><br/>
        1. <b>Ingestion:</b> pypdfium2 / OCR<br/>
        2. <b>Retrieval:</b> BM25 Okapi Chunker<br/>
        3. <b>Reasoning:</b> Cloud Inference Node<br/>
        4. <b>Grounding:</b> Verifier (Zero-Hallucination)<br/>
        5. <b>Rules:</b> Statutory Deterministic Matcher
    </div>
    """, unsafe_allow_html=True)

# Main Hero Header
st.markdown("""
<div class="hero-container">
    <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 1rem;">
        <div>
            <div>
                <span class="badge-pill badge-primary">⚡ LangGraph Swarm</span>
                <span class="badge-pill badge-success">🛡️ Zero Hallucination Guarantee</span>
                <span class="badge-pill badge-purple">⚖️ PPRA & PEC Compliant</span>
            </div>
            <h1 style="margin: 0.8rem 0 0.3rem 0; font-family: 'Outfit', sans-serif; font-size: 2.5rem; font-weight: 800; color: #F8FAFC; letter-spacing: -0.02em;">
                TenderMind AI
            </h1>
            <p style="margin: 0; color: #94A3B8; font-size: 1.1rem; max-width: 800px; line-height: 1.5;">
                Autonomous Bid/No-Bid Decision Engine. Ingests procurement documents, verifies verbatim grounding quotes, and checks statutory constraints in seconds.
            </p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Ingestion Source Switcher
st.markdown("### 1. Select or Upload Tender Documentation")

source_mode = st.radio(
    "Choose Tender Ingestion Mode:",
    ["⚡ Curated Benchmark Tenders", "📁 Upload Custom Tender PDF"],
    horizontal=True
)

active_bytes = None
active_filename = ""

if source_mode == "⚡ Curated Benchmark Tenders":
    sample_options = {
        "Sample 1: Civil Highway Works (C-4 Required) -> Expected: BID (Qualified)": "data/samples/Tender_01_Civil_Infrastructure_C4_Qualified.pdf",
        "Sample 2: Elevated Flyover Mega Project (C-2 Required) -> Expected: NO-BID (Disqualified)": "data/samples/Tender_02_Flyover_MegaProject_C2_Disqualified.pdf",
        "Sample 3: Municipal Solar Power Micro-Grid -> Expected: BID IF (Clarification)": "data/samples/Tender_03_Municipal_Solar_Power_NeedsClarification.pdf",
        "Test Custom 1: WASA Water Filtration Project (C-5 Required)": "data/CUSTOM_TEST_TENDER_WASA_C5.pdf",
        "Test Custom 2: Sindh Pediatric Hospital Trauma Complex (C-3 Required)": "data/CUSTOM_TEST_TENDER_SINDH_HOSPITAL_C3.pdf"
    }
    selected_sample_label = st.selectbox("Select Benchmark Tender Document:", list(sample_options.keys()))
    sample_path = sample_options[selected_sample_label]
    if os.path.exists(sample_path):
        with open(sample_path, "rb") as f:
            active_bytes = f.read()
        active_filename = os.path.basename(sample_path)
else:
    uploaded_file = st.file_uploader("Upload RFP, IFB, or Tender Notice (PDF)", type=["pdf"])
    if uploaded_file is not None:
        active_bytes = uploaded_file.read()
        active_filename = uploaded_file.name

if active_bytes:
    st.markdown(f"""
    <div class="glass-panel" style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <span style="font-weight: 700; color: #F8FAFC;">Active Document:</span> <code>{active_filename}</code>
            <span style="color: #64748B; margin-left: 10px;">({len(active_bytes):,} bytes)</span>
        </div>
        <div>
            <span style="color: #34D399; font-weight: 600; font-size: 0.85rem;">● Document Ready for Multi-Agent Swarm</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🚀 Run Autonomous Bid Assessment", type="primary", use_container_width=True):
        progress_bar = st.progress(0, text="Initializing Multi-Agent LangGraph Swarm...")
        
        with st.status("Executing Multi-Agent Decision Graph...", expanded=True) as status_box:
            # Step 1: Ingestion
            status_box.write("📄 **[Ingestion Agent]** Parsing document pages & OCR text layout...")
            progress_bar.progress(20, text="Extracting page text and layout...")
            pages = extract_pdf_pages(active_bytes)
            status_box.write(f"✅ Ingested **{len(pages)} page(s)** into memory.")
            
            # Step 2: Retrieval
            status_box.write("🔍 **[Retrieval Agent]** Building BM25 Okapi chunk index & retrieving procurement sections...")
            progress_bar.progress(45, text="Indexing chunks via BM25...")
            
            # Step 3: LLM Reasoning
            status_box.write("🧠 **[Reasoning Agent]** Performing single-pass procurement criteria extraction on Cloud Engine...")
            progress_bar.progress(70, text="Executing single-pass structured extraction...")
            
            # Step 4 & 5: Verifier and Rules
            status_box.write("🛡️ **[Grounding Verifier]** Enforcing zero-hallucination quote and digit checks...")
            status_box.write("⚖️ **[Rules Engine]** Auditing statutory PEC category hierarchy, Tax (FBR/STRN), and bank security...")
            progress_bar.progress(90, text="Auditing compliance rules against company vault...")
            
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

        st.session_state["tender_results"] = {
            "final_state": final_state,
            "filename": active_filename,
            "profile": profile
        }

# Render Results
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
            <div style="font-size: 0.85rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; color: #6EE7B7; margin-bottom: 6px;">Executive Evaluation Complete</div>
            <h2 style="margin: 0; font-family: 'Outfit', sans-serif; font-size: 2.4rem; font-weight: 800; letter-spacing: -0.01em;">🟢 VERDICT: BID (QUALIFIED)</h2>
            <p style="margin: 0.6rem 0 0 0; font-size: 1.15rem; color: #D1FAE5; max-width: 800px; margin-left: auto; margin-right: auto;">
                All mandatory statutory, technical (PEC {prof['licence_category']}), and financial guarantee conditions verified with 100% confidence.
            </p>
        </div>
        """, unsafe_allow_html=True)
    elif "NO-BID" in verdict:
        st.markdown(f"""
        <div class="verdict-banner-fail">
            <div style="font-size: 0.85rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; color: #FCA5A5; margin-bottom: 6px;">Executive Evaluation Complete</div>
            <h2 style="margin: 0; font-family: 'Outfit', sans-serif; font-size: 2.4rem; font-weight: 800; letter-spacing: -0.01em;">🔴 VERDICT: NO-BID (DISQUALIFIED)</h2>
            <p style="margin: 0.6rem 0 0 0; font-size: 1.15rem; color: #FEE2E2; max-width: 800px; margin-left: auto; margin-right: auto;">
                Critical non-compliance or capacity disqualifications identified. Submitting a bid without remediation will lead to statutory forfeiture.
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="verdict-banner-warn">
            <div style="font-size: 0.85rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; color: #FDE68A; margin-bottom: 6px;">Executive Evaluation Complete</div>
            <h2 style="margin: 0; font-family: 'Outfit', sans-serif; font-size: 2.4rem; font-weight: 800; letter-spacing: -0.01em;">🟡 VERDICT: BID IF (CLARIFICATION REQUIRED)</h2>
            <p style="margin: 0.6rem 0 0 0; font-size: 1.15rem; color: #FEF3C7; max-width: 800px; margin-left: auto; margin-right: auto;">
                Core contractor criteria pass, but ambiguous specifications require formal pre-bid clarification with the procuring agency.
            </p>
        </div>
        """, unsafe_allow_html=True)

    # 2. Executive KPI Cards
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    
    pass_rules_count = sum(1 for r in rules if r["status"] == "PASS")
    total_rules = len(rules)
    
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
        "⚖️ Compliance Rules Matrix",
        "🛡️ Grounded Evidence & Quotes",
        "📁 Document Readiness Vault",
        "🔍 LangGraph Execution Trace"
    ])

    with tab_rules:
        st.markdown("#### Deterministic Compliance Rule Checks")
        for r in rules:
            status_icon = "🟢" if r["status"] == "PASS" else ("🔴" if r["status"] == "FAIL" else "🟡")
            sev_badge = "HARD CONSTRAINT" if r["severity"] == "hard" else "SOFT CONSTRAINT"
            sev_color = "#EF4444" if r["severity"] == "hard" else "#3B82F6"
            
            with st.container():
                st.markdown(f"""
                <div class="glass-panel" style="margin-bottom: 0.8rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-weight: 700; font-size: 1.05rem; color: #F8FAFC;">{status_icon} [{r['rule_id']}] {r['name']}</span>
                        <span style="font-size: 0.75rem; font-weight: 700; color: {sev_color}; background: rgba(255,255,255,0.06); padding: 3px 10px; border-radius: 9999px;">{sev_badge}</span>
                    </div>
                    <div style="margin: 8px 0; color: #CBD5E1; font-size: 0.95rem;">{r['reason']}</div>
                    {f'<div class="quote-box"><b>Grounding Evidence:</b> {r["evidence"]}</div>' if r.get('evidence') else ''}
                </div>
                """, unsafe_allow_html=True)

    with tab_evidence:
        st.markdown("#### Anti-Hallucination Grounding Audit")
        st.caption("Every procurement fact must be grounded in raw PDF text with page number and verbatim excerpt.")
        
        for k, v in verified.items():
            clean_title = k.replace("_", " ").title()
            if isinstance(v, dict):
                st_badge = v.get("status", "N/A")
                icon = "✅" if st_badge == "verified" else ("❌" if st_badge == "ungrounded" else "⚪")
                
                with st.expander(f"{icon} {clean_title}: {v.get('value', 'Not Specified')} (Page {v.get('page')}) [{st_badge.upper()}]"):
                    st.write(f"**Extracted Value:** `{v.get('value')}`")
                    st.write(f"**Cited Page:** {v.get('page')}")
                    st.write(f"**Verification Status:** `{st_badge.upper()}`")
                    if v.get("quote"):
                        st.markdown(f"**Verbatim Excerpt from Page {v.get('page')}:**")
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
        st.markdown("#### Mandatory Tender Documents vs. Company Repository")
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
        st.markdown("#### LangGraph Multi-Agent Execution State")
        st.json(state["raw_extraction"])

    # 4. Export Bid Pack
    st.divider()
    st.markdown("""
    <div class="glass-panel" style="text-align: center; padding: 2rem;">
        <h3 style="margin-top: 0; font-family: 'Outfit', sans-serif;">📥 Export Official Executive Bid Pack</h3>
        <p style="color: #94A3B8; max-width: 650px; margin: 0 auto 1.5rem auto;">
            Generate an official audit document in Microsoft Word (.docx) format containing the compliance statement, verbatim quote citations, and rule assessment.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    docx_stream = generate_bid_pack_docx(verdict, verified, rules, prof)
    st.download_button(
        label="📥 Download Official Bid Pack (.docx)",
        data=docx_stream,
        file_name=f"TenderMind_Bid_Pack_{active_filename.replace('.pdf', '')}.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        type="primary",
        use_container_width=True
    )
