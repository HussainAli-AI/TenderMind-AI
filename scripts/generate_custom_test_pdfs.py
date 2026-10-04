import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

styles = getSampleStyleSheet()

title_style = ParagraphStyle(
    'DocTitle',
    parent=styles['Heading1'],
    fontSize=15,
    leading=18,
    textColor=colors.HexColor('#0F172A'),
    alignment=1
)
h2_style = ParagraphStyle(
    'SectionHeader',
    parent=styles['Heading2'],
    fontSize=11,
    leading=15,
    textColor=colors.HexColor('#1E3A8A'),
    spaceBefore=10,
    spaceAfter=4
)
body_style = ParagraphStyle(
    'BodyTextCustom',
    parent=styles['Normal'],
    fontSize=9.5,
    leading=13.5,
    textColor=colors.HexColor('#334155')
)

# 1. Custom Tender A: WASA Water Treatment (C-5 Required -> Apex C-4 Qualifies)
path_a = "data/CUSTOM_TEST_TENDER_WASA_C5.pdf"
doc_a = SimpleDocTemplate(path_a, pagesize=letter)
elements_a = [
    Paragraph("WATER AND SANITATION AGENCY (WASA), FAISALABAD<br/>DEVELOPMENT & INFRASTRUCTURE WING", title_style),
    Spacer(1, 8),
    Paragraph("<b>INVITATION FOR BIDS (IFB) — TENDER NOTICE NO. WASA/ENG/2026-77</b>", ParagraphStyle('SubA', parent=title_style, fontSize=11, leading=14)),
    Spacer(1, 10),
    Paragraph("The Managing Director, WASA Faisalabad invites sealed bids from experienced engineering constructors registered with Pakistan Engineering Council for:", body_style),
    Spacer(1, 6),
    Paragraph("<b>Work Description:</b> Rehabilitation of Trunk Sewerage Lines and Modernization of 4 Water Filtration Facilities (Zone 3).", body_style),
    Paragraph("<b>Estimated Project Cost:</b> PKR 35,000,000/- (Pak Rupees Thirty-Five Million Only)", body_style),
    Paragraph("<b>Required PEC Category:</b> Category C-5 or above (Specialization Code CE-09 & CE-10).", body_style),
    Paragraph("<b>Earnest Money / Bid Security:</b> 2% of the estimated cost amounting to PKR 700,000/- in the shape of Call Deposit Receipt (CDR) in favor of Managing Director, WASA.", body_style),
    Paragraph("<b>Bid Submission Deadline:</b> November 05, 2026 at 11:00 AM PST. Technical proposals will be opened on the same day at 11:30 AM PST.", body_style),
    Spacer(1, 8),
    Paragraph("<b>MANDATORY EVALUATION & QUALIFICATION CRITERIA:</b>", h2_style),
    Paragraph("1. Valid PEC Registration Certificate in Category C-5 or higher valid for fiscal year 2026.", body_style),
    Paragraph("2. Active Taxpayer status with Federal Board of Revenue (FBR Active Taxpayer NTN) and Punjab Revenue Authority (PRA).", body_style),
    Paragraph("3. Audited Financial Statements (Last 3 Years) showing minimum cumulative turnover of PKR 40 Million.", body_style),
    Paragraph("4. Past Relevant Experience Proof of completing at least one similar municipal water or sewerage project valued over PKR 20 Million.", body_style),
    Paragraph("5. Bank Guarantee Capability Letter and credit line availability certificate from a scheduled commercial bank.", body_style),
    Paragraph("6. Undertaking on PKR 100 legal stamp paper that the firm has never been blacklisted by any government organization.", body_style),
    Spacer(1, 12),
    Paragraph("Bidding documents can be downloaded from WASA official portal or obtained from the office upon payment of PKR 3,000 tender fee.", body_style)
]
doc_a.build(elements_a)
print(f"Generated: {path_a}")

# 2. Custom Tender B: Sindh Hospital Complex (C-3 Required -> Apex C-4 Disqualifies unless upgraded)
path_b = "data/CUSTOM_TEST_TENDER_SINDH_HOSPITAL_C3.pdf"
doc_b = SimpleDocTemplate(path_b, pagesize=letter)
elements_b = [
    Paragraph("GOVERNMENT OF SINDH<br/>SPECIALIZED HEALTHCARE & MEDICAL EDUCATION DEPARTMENT", title_style),
    Spacer(1, 8),
    Paragraph("<b>INTERNATIONAL COMPETITIVE BIDDING (ICB) — NOTICE NO. SHC-MED/2026/102</b>", ParagraphStyle('SubB', parent=title_style, fontSize=11, leading=14)),
    Spacer(1, 10),
    Paragraph("The Project Director invites sealed technical and financial proposals for construction of a major regional medical facility:", body_style),
    Spacer(1, 6),
    Paragraph("<b>Name of Work:</b> Construction of 200-Bed Pediatric & Emergency Trauma Care Facility at Hyderabad.", body_style),
    Paragraph("<b>Estimated Procurement Value:</b> PKR 140,000,000/- (Pak Rupees One Hundred Forty Million Only)", body_style),
    Paragraph("<b>Required PEC Category:</b> Mandatory Category C-3 or above (Specialized in BC-01 Building Construction and CE-10).", body_style),
    Paragraph("<b>Bid Security / Guarantee:</b> Fixed amount of PKR 2,800,000/- (Two Million Eight Hundred Thousand PKR) via unconditional Bank Guarantee.", body_style),
    Paragraph("<b>Submission Deadline:</b> December 10, 2026 at 01:30 PM PST. Late submissions will not be entertained.", body_style),
    Spacer(1, 8),
    Paragraph("<b>STATUTORY QUALIFICATION REQUIREMENTS:</b>", h2_style),
    Paragraph("1. Valid PEC Category C-3 or above license. Firms holding C-4, C-5 or lower are non-responsive and disqualified.", body_style),
    Paragraph("2. Active registration on FBR Active Taxpayer list (NTN) and Sindh Revenue Board (SRB) Sales Tax list.", body_style),
    Paragraph("3. Audited Financial Statements for the last three years showing average annual financial turnover of at least PKR 100 Million.", body_style),
    Paragraph("4. Past Relevant Experience Proof with at least two institutional hospital or commercial multi-story building projects completed.", body_style),
    Paragraph("5. Bank Guarantee Capability Letter and verified working capital letter of PKR 10 Million.", body_style)
]
doc_b.build(elements_b)
print(f"Generated: {path_b}")
