import streamlit as st
import yaml
import os
import sys
import json
import textwrap
from io import BytesIO

# Ensure app is discoverable on python path
sys.path.insert(0, os.path.abspath("."))

from app.tools.pdf import extract_pdf_pages
from app.graph import build_tender_graph
from app.tools.export import generate_bid_pack_docx
from app.llm import get_groq_api_key
from app.tools.profile_manager import get_all_profiles, save_custom_profile, delete_custom_profile

st.set_page_config(
    page_title="TenderMind AI — Autonomous Bid/No-Bid Decision Engine",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# High-End Dark Theme Styling
st.markdown(textwrap.dedent("""
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
        padding: 2rem 2.2rem;
        background: linear-gradient(135deg, rgba(22, 31, 48, 0.75) 0%, rgba(11, 15, 23, 0.95) 100%);
        border: 1px solid rgba(59, 130, 246, 0.25);
        border-radius: 20px;
        margin-bottom: 2rem;
        box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.7), inset 0 1px 0 rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(16px);
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
        backdrop-filter: blur(12px);
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
</style>
"""), unsafe_allow_html=True)

# Load All Company Profiles (Presets + User Custom Profiles)
all_profiles = get_all_profiles()

# Sidebar: Enterprise Branding & Company Profile Manager
with st.sidebar:
    st.markdown(textwrap.dedent("""
    <div style="background: linear-gradient(135deg, rgba(59,130,246,0.15), rgba(99,102,241,0.25)); border: 1px solid rgba(99,102,241,0.35); padding: 16px; border-radius: 14px; margin-bottom: 1.2rem;">
        <div style="display: flex; align-items: center; gap: 10px;">
            <div style="font-size: 1.8rem; background: rgba(59,130,246,0.2); padding: 6px; border-radius: 10px; border: 1px solid rgba(59,130,246,0.4);">🏛️</div>
            <div>
                <div style="font-family: 'Outfit', sans-serif; font-weight: 800; font-size: 1.2rem; color: #F8FAFC;">TenderMind AI</div>
                <div style="font-size: 0.72rem; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600;">Autonomous Bid Intelligence</div>
            </div>
        </div>
        <div style="display: flex; align-items: center; gap: 8px; margin-top: 12px; padding-top: 10px; border-top: 1px solid rgba(255,255,255,0.08);">
            <span style="height: 8px; width: 8px; background-color: #10B981; border-radius: 50%; display: inline-block; box-shadow: 0 0 10px #10B981;"></span>
            <span style="font-size: 0.75rem; color: #34D399; font-weight: 700;">SWARM ENGINE READY</span>
        </div>
    </div>
    """), unsafe_allow_html=True)

    st.markdown("#### 🏢 Active Contractor Profile")
    
    # Selected Profile Key in Session State
    if "selected_profile_key" not in st.session_state or st.session_state["selected_profile_key"] not in all_profiles:
        st.session_state["selected_profile_key"] = list(all_profiles.keys())[0]

    selected_preset = st.selectbox(
        "Select Active Contractor Profile:",
        list(all_profiles.keys()),
        index=list(all_profiles.keys()).index(st.session_state["selected_profile_key"]),
        key="profile_selector"
    )
    st.session_state["selected_profile_key"] = selected_preset
    profile = all_profiles[selected_preset]
    
    # Clean Native Profile Container (Zero raw HTML leak)
    with st.container(border=True):
        st.caption("COMPANY LEGAL NAME")
        st.markdown(f"**{profile['company_name']}**")
        st.divider()
        col_pec, col_cap = st.columns(2)
        with col_pec:
            st.caption("PEC LICENSE")
            st.markdown(f"🏷️ `{profile['licence_category']}`")
        with col_cap:
            st.caption("MAX SECURITY")
            st.markdown(f"PKR {profile['max_bid_security_pkr']/1e6:.1f}M")
        st.caption("ANNUAL TURNOVER")
        st.markdown(f"PKR {profile['turnover_pkr']:,}")

    with st.expander("📁 Verified Credentials & Vault", expanded=False):
        st.markdown("**Tax Registrations:**")
        for r in profile.get("registrations", []):
            st.markdown(f"• `{r}`")
        st.markdown("**Documents in Vault:**")
        for d in profile.get("documents", []):
            st.markdown(f"• `{d}`")
            
        if profile.get("is_custom", False):
            st.divider()
            if st.button("🗑️ Delete This Custom Profile", type="secondary", use_container_width=True):
                delete_custom_profile(selected_preset)
                st.session_state["selected_profile_key"] = list(get_all_profiles().keys())[0]
                st.success("Profile deleted!")
                st.rerun()

    # Form to Add New Company Profile
    with st.expander("➕ Add New Company Profile", expanded=False):
        st.markdown("##### 📝 Create New Contractor Identity")
        with st.form("new_profile_form", clear_on_submit=True):
            new_comp_name = st.text_input("Company Legal Name", placeholder="e.g. Allied Builders & Tech Pvt Ltd")
            
            new_pec_cat = st.selectbox(
                "PEC Category",
                [
                    "C-A (Unlimited)",
                    "C-B (Up to PKR 4,000M)",
                    "C-1 (Up to PKR 2,500M)",
                    "C-2 (Up to PKR 1,000M)",
                    "C-3 (Up to PKR 500M)",
                    "C-4 (Up to PKR 200M)",
                    "C-5 (Up to PKR 65M)",
                    "C-6 (Up to PKR 25M)"
                ],
                index=5 # default C-4
            )
            # Extract short code (e.g. C-4)
            pec_code = new_pec_cat.split(" ")[0]
            
            new_turnover = st.number_input(
                "Annual Financial Turnover (PKR)",
                min_value=1000000,
                max_value=10000000000,
                value=50000000,
                step=5000000
            )
            
            new_security = st.number_input(
                "Max Bid Security / Guarantee Capacity (PKR)",
                min_value=100000,
                max_value=1000000000,
                value=2500000,
                step=500000
            )
            
            new_regs = st.multiselect(
                "Active Tax & Statutory Registrations",
                [
                    "FBR Active Taxpayer (NTN)",
                    "Sales Tax Registration (STRN)",
                    "PEC Registered (Pakistan Engineering Council)",
                    "Punjab Revenue Authority (PRA)",
                    "Sindh Revenue Board (SRB)",
                    "Khyber Pakhtunkhwa Revenue Authority (KPRA)",
                    "Balochistan Revenue Authority (BRA)"
                ],
                default=["FBR Active Taxpayer (NTN)", "Sales Tax Registration (STRN)", "PEC Registered (Pakistan Engineering Council)"]
            )
            
            new_docs = st.multiselect(
                "Mandatory Qualification Documents in Repository",
                [
                    "Company Registration Certificate",
                    "FBR Tax Clearance Certificate",
                    "PEC Valid License",
                    "Audited Financial Statements (Last 3 Years)",
                    "Past Relevant Experience Proof",
                    "Bank Guarantee Capability Letter",
                    "Machinery & Equipment Ownership Proof",
                    "Non-Blacklisting Legal Affidavit",
                    "5-Year Audited Balance Sheets"
                ],
                default=[
                    "Company Registration Certificate",
                    "FBR Tax Clearance Certificate",
                    "PEC Valid License",
                    "Audited Financial Statements (Last 3 Years)",
                    "Past Relevant Experience Proof",
                    "Bank Guarantee Capability Letter"
                ]
            )
            
            submitted = st.form_submit_button("💾 Save & Activate Profile", type="primary", use_container_width=True)
            if submitted:
                if not new_comp_name.strip():
                    st.error("Please enter a valid company name.")
                else:
                    profile_key = f"{new_comp_name.strip()} (PEC {pec_code})"
                    new_profile_dict = {
                        "company_name": new_comp_name.strip(),
                        "licence_category": pec_code,
                        "turnover_pkr": int(new_turnover),
                        "max_bid_security_pkr": int(new_security),
                        "registrations": new_regs,
                        "documents": new_docs
                    }
                    save_custom_profile(profile_key, new_profile_dict)
                    st.session_state["selected_profile_key"] = profile_key
                    st.success(f"✅ Created & Activated: {new_comp_name}")
                    st.rerun()

    st.markdown(textwrap.dedent("""
    <div style="margin-top: 1.5rem; padding: 12px; background: rgba(15,23,42,0.6); border-radius: 10px; border: 1px solid rgba(255,255,255,0.05); font-size: 0.72rem; color: #64748B; line-height: 1.6;">
        <b style="color: #94A3B8;">Multi-Agent Swarm Pipeline:</b><br/>
        1. <b>Ingestion:</b> pypdfium2 / OCR<br/>
        2. <b>Retrieval:</b> BM25 Okapi Chunker<br/>
        3. <b>Reasoning:</b> Cloud Inference Node<br/>
        4. <b>Grounding:</b> Verifier (Anti-Hallucination)<br/>
        5. <b>Rules:</b> Statutory Deterministic Matcher
    </div>
    """), unsafe_allow_html=True)

# Main Hero Header
st.markdown(textwrap.dedent("""
<div class="hero-container">
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
"""), unsafe_allow_html=True)

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
    with st.container(border=True):
        c_name, c_ready = st.columns([3, 1])
        with c_name:
            st.markdown(f"**Active Document:** `{active_filename}` ({len(active_bytes):,} bytes)")
        with c_ready:
            st.markdown("<span style='color: #34D399; font-weight: 700;'>● Ready for Swarm</span>", unsafe_allow_html=True)
    
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
        st.markdown(textwrap.dedent(f"""
        <div class="verdict-banner-pass">
            <div style="font-size: 0.85rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; color: #6EE7B7; margin-bottom: 6px;">Executive Evaluation Complete</div>
            <h2 style="margin: 0; font-family: 'Outfit', sans-serif; font-size: 2.4rem; font-weight: 800; letter-spacing: -0.01em;">🟢 VERDICT: BID (QUALIFIED)</h2>
            <p style="margin: 0.6rem 0 0 0; font-size: 1.15rem; color: #D1FAE5; max-width: 800px; margin-left: auto; margin-right: auto;">
                All mandatory statutory, technical (PEC {prof['licence_category']}), and financial guarantee conditions verified with 100% confidence.
            </p>
        </div>
        """), unsafe_allow_html=True)
    elif "NO-BID" in verdict:
        st.markdown(textwrap.dedent(f"""
        <div class="verdict-banner-fail">
            <div style="font-size: 0.85rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; color: #FCA5A5; margin-bottom: 6px;">Executive Evaluation Complete</div>
            <h2 style="margin: 0; font-family: 'Outfit', sans-serif; font-size: 2.4rem; font-weight: 800; letter-spacing: -0.01em;">🔴 VERDICT: NO-BID (DISQUALIFIED)</h2>
            <p style="margin: 0.6rem 0 0 0; font-size: 1.15rem; color: #FEE2E2; max-width: 800px; margin-left: auto; margin-right: auto;">
                Critical non-compliance or capacity disqualifications identified. Submitting a bid without remediation will lead to statutory forfeiture.
            </p>
        </div>
        """), unsafe_allow_html=True)
    else:
        st.markdown(textwrap.dedent(f"""
        <div class="verdict-banner-warn">
            <div style="font-size: 0.85rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; color: #FDE68A; margin-bottom: 6px;">Executive Evaluation Complete</div>
            <h2 style="margin: 0; font-family: 'Outfit', sans-serif; font-size: 2.4rem; font-weight: 800; letter-spacing: -0.01em;">🟡 VERDICT: BID IF (CLARIFICATION REQUIRED)</h2>
            <p style="margin: 0.6rem 0 0 0; font-size: 1.15rem; color: #FEF3C7; max-width: 800px; margin-left: auto; margin-right: auto;">
                Core contractor criteria pass, but ambiguous specifications require formal pre-bid clarification with the procuring agency.
            </p>
        </div>
        """), unsafe_allow_html=True)

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
        st.markdown(textwrap.dedent(f"""
        <div class="metric-card">
            <div class="metric-label">Rules Evaluation</div>
            <div class="metric-val">{pass_rules_count} / {total_rules}</div>
        </div>
        """), unsafe_allow_html=True)

    with kpi2:
        st.markdown(textwrap.dedent(f"""
        <div class="metric-card">
            <div class="metric-label">Grounding Confidence</div>
            <div class="metric-val">{verif_rate:.0f}%</div>
        </div>
        """), unsafe_allow_html=True)

    with kpi3:
        pec_stat = next((r["status"] for r in rules if r["rule_id"] == "R1"), "N/A")
        color = "#34D399" if pec_stat == "PASS" else ("#F87171" if pec_stat == "FAIL" else "#FBBF24")
        st.markdown(textwrap.dedent(f"""
        <div class="metric-card">
            <div class="metric-label">PEC Match ({prof['licence_category']})</div>
            <div class="metric-val" style="color: {color};">{pec_stat}</div>
        </div>
        """), unsafe_allow_html=True)

    with kpi4:
        doc_stat = next((r["status"] for r in rules if r["rule_id"] == "R4"), "N/A")
        st.markdown(textwrap.dedent(f"""
        <div class="metric-card">
            <div class="metric-label">Document Readiness</div>
            <div class="metric-val">{doc_stat}</div>
        </div>
        """), unsafe_allow_html=True)

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
            
            with st.container(border=True):
                c_hd, c_bd = st.columns([3, 1])
                with c_hd:
                    st.markdown(f"**{status_icon} [{r['rule_id']}] {r['name']}**")
                with c_bd:
                    st.markdown(f"<span style='color: {sev_color}; font-weight: 700; font-size: 0.75rem; border: 1px solid {sev_color}; padding: 2px 8px; border-radius: 9999px;'>{sev_badge}</span>", unsafe_allow_html=True)
                st.markdown(f"<div style='color: #CBD5E1; margin: 4px 0;'>{r['reason']}</div>", unsafe_allow_html=True)
                if r.get("evidence"):
                    st.markdown(f"<div class='quote-box'><b>Grounding Evidence:</b> {r['evidence']}</div>", unsafe_allow_html=True)

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
    with st.container(border=True):
        st.markdown("<h3 style='margin-top: 0; font-family: Outfit, sans-serif; text-align: center;'>📥 Export Official Executive Bid Pack</h3>", unsafe_allow_html=True)
        st.markdown("<p style='color: #94A3B8; text-align: center; max-width: 650px; margin: 0 auto 1.5rem auto;'>Generate an official audit document in Microsoft Word (.docx) format containing the compliance statement, verbatim quote citations, and rule assessment.</p>", unsafe_allow_html=True)
        
        docx_stream = generate_bid_pack_docx(verdict, verified, rules, prof)
        st.download_button(
            label="📥 Download Official Bid Pack (.docx)",
            data=docx_stream,
            file_name=f"TenderMind_Bid_Pack_{active_filename.replace('.pdf', '')}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            type="primary",
            use_container_width=True
        )
