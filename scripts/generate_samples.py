import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

os.makedirs('data/samples', exist_ok=True)

styles = getSampleStyleSheet()
title_style = ParagraphStyle(
    'DocTitle',
    parent=styles['Heading1'],
    fontSize=16,
    leading=20,
    textColor=colors.HexColor('#0F172A'),
    alignment=1
)
h2_style = ParagraphStyle(
    'SectionHeader',
    parent=styles['Heading2'],
    fontSize=12,
    leading=16,
    textColor=colors.HexColor('#1E3A8A'),
    spaceBefore=8,
    spaceAfter=4
)
body_style = ParagraphStyle(
    'BodyTextCustom',
    parent=styles['Normal'],
    fontSize=10,
    leading=14,
    textColor=colors.HexColor('#334155')
)

# 1. Qualified Sample
doc1 = SimpleDocTemplate('data/samples/Tender_01_Civil_Infrastructure_C4_Qualified.pdf', pagesize=letter)
elements1 = [
    Paragraph('GOVERNMENT OF THE PUNJAB<br/>COMMUNICATION & WORKS DEPARTMENT', title_style),
    Spacer(1, 10),
    Paragraph('<b>INVITATION FOR BIDS (IFB) — TENDER NOTICE NO. CWD-2026/89</b>', ParagraphStyle('Sub', parent=title_style, fontSize=12, leading=15)),
    Spacer(1, 12),
    Paragraph('The Executive Engineer, Highways Division, invites sealed tenders from eligible engineering firms for the following infrastructure work:', body_style),
    Spacer(1, 8),
    Paragraph('<b>Project Title:</b> Rehabilitation and Dualization of Access Highway Route 4B (Length: 12.4 Km)', body_style),
    Paragraph('<b>Estimated Project Cost:</b> PKR 75,000,000/- (Pak Rupees Seventy Five Million Only)', body_style),
    Paragraph('<b>Required PEC Category:</b> C-4 or above with specialized codes CE-01 and CE-10.', body_style),
    Paragraph('<b>Earnest Money / Bid Security:</b> 2% of the estimated cost amounting to PKR 1,500,000 in the shape of CDR/Bank Guarantee in favor of Executive Engineer.', body_style),
    Paragraph('<b>Submission Deadline:</b> October 28, 2026 at 11:30 AM PST. Bids will be opened publicly on the same date at 12:00 PM PST.', body_style),
    Spacer(1, 10),
    Paragraph('<b>MANDATORY ELIGIBILITY & STATUTORY REQUIREMENTS:</b>', h2_style),
    Paragraph('1. Valid Pakistan Engineering Council (PEC) Registration Certificate in Category C-4 or above for Year 2026.', body_style),
    Paragraph('2. FBR Active Taxpayer (NTN) and Punjab Revenue Authority (PRA) Sales Tax Registration Certificate.', body_style),
    Paragraph('3. Audited Financial Statements for the last 3 fiscal years from a certified chartered accountant.', body_style),
    Paragraph('4. Past Relevant Experience Proof demonstrating at least two similar road construction projects completed in the past 5 years.', body_style),
    Paragraph('5. Bank Guarantee Capability Letter and credit line availability certificate from a scheduled bank.', body_style),
    Paragraph('6. An affidavit on legal stamp paper declaring that the firm has never been blacklisted by any government authority.', body_style),
    Spacer(1, 15),
    Paragraph('Interested bidders may obtain tender documents from the office during working hours upon payment of a non-refundable tender fee of PKR 5,000.', body_style)
]
doc1.build(elements1)

# 2. Disqualified Sample (Requires C-2, High Security)
doc2 = SimpleDocTemplate('data/samples/Tender_02_Flyover_MegaProject_C2_Disqualified.pdf', pagesize=letter)
elements2 = [
    Paragraph('NATIONAL HIGHWAY AUTHORITY (NHA)<br/>MINISTRY OF COMMUNICATIONS', title_style),
    Spacer(1, 10),
    Paragraph('<b>EXPRESSION OF INTEREST / BIDDING NOTICE — NHA/HQ/2026/04</b>', ParagraphStyle('Sub2', parent=title_style, fontSize=12, leading=15)),
    Spacer(1, 12),
    Paragraph('The National Highway Authority invites sealed technical and financial bids from reputed constructors for mega grade-separated flyover construction:', body_style),
    Spacer(1, 8),
    Paragraph('<b>Project Title:</b> Construction of Multi-Span Pre-Stressed Elevated Flyover and Interchange System', body_style),
    Paragraph('<b>Estimated Cost:</b> PKR 280,000,000/-', body_style),
    Paragraph('<b>Required PEC Category:</b> C-2 or above with specialization CE-02 (Heavy Bridges).', body_style),
    Paragraph('<b>Bid Security:</b> Fixed amount of PKR 5,000,000 (Pak Rupees Five Million) via unconditional Bank Guarantee.', body_style),
    Paragraph('<b>Submission Deadline:</b> November 15, 2026 at 02:00 PM PST. Late bids will be rejected without consideration.', body_style),
    Spacer(1, 10),
    Paragraph('<b>TECHNICAL & QUALIFICATION CRITERIA:</b>', h2_style),
    Paragraph('1. PEC Category C-2 or higher valid license is strictly mandatory. Firms holding C-3, C-4 or lower are non-responsive.', body_style),
    Paragraph('2. Registered with Federal Board of Revenue (FBR Active Taxpayer NTN) and Sales Tax Department (STRN).', body_style),
    Paragraph('3. Minimum annual turnover of PKR 150 Million over the last 3 financial years.', body_style),
    Paragraph('4. Ownership proof of hydraulic rotary piling rigs and heavy girder launching cranes.', body_style),
    Paragraph('5. Bank Guarantee Capability Letter of at least PKR 15 Million.', body_style)
]
doc2.build(elements2)

# 3. Clarification Sample (PEC Unspecified)
doc3 = SimpleDocTemplate('data/samples/Tender_03_Municipal_Solar_Power_NeedsClarification.pdf', pagesize=letter)
elements3 = [
    Paragraph('DISTRICT HEALTH & MUNICIPAL AUTHORITY<br/>SPECIALIZED HEALTHCARE INITIATIVE', title_style),
    Spacer(1, 10),
    Paragraph('<b>TENDER INVITATION — SOLAR POWER CONVERSION PROJECT</b>', ParagraphStyle('Sub3', parent=title_style, fontSize=12, leading=15)),
    Spacer(1, 12),
    Paragraph('Sealed tenders are invited under single-stage two-envelope procedure from registered engineering suppliers:', body_style),
    Spacer(1, 8),
    Paragraph('<b>Project Title:</b> Supply, Installation & Commissioning of 250 kW Solar Hybrid Power Plant at DHQ Complex', body_style),
    Paragraph('<b>Estimated Cost:</b> PKR 18,500,000/-', body_style),
    Paragraph('<b>Required PEC Category:</b> Registered engineering firms with relevant specialization (Category not explicitly specified).', body_style),
    Paragraph('<b>Bid Security:</b> PKR 400,000 in the form of Deposit-at-Call (CDR) from a scheduled Pakistani bank.', body_style),
    Paragraph('<b>Submission Deadline:</b> October 20, 2026 at 12:00 PM PST.', body_style),
    Spacer(1, 10),
    Paragraph('<b>SUBMISSION CHECKLIST:</b>', h2_style),
    Paragraph('1. Valid Registration with Pakistan Engineering Council (PEC) or relevant trade body.', body_style),
    Paragraph('2. Active FBR NTN Tax Clearance Certificate.', body_style),
    Paragraph('3. Past Relevant Experience Proof with at least 3 solar installations in public or private hospitals.', body_style),
    Paragraph('4. Bank Account Statement / Financial Stability Certificate for last 12 months.', body_style)
]
doc3.build(elements3)

print("Generated 3 sample tender PDFs in data/samples/ successfully.")
