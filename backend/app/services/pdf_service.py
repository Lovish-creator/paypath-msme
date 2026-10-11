import io
import os
from datetime import date, datetime
from typing import Dict, Any, List

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
    KeepTogether,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY

from backend.app.models.case import Case
from backend.app.models.invoice import Invoice
from backend.app.models.business import BusinessProfile
from backend.app.services.legal_engine import LegalEngine


class PDFService:
    @staticmethod
    def generate_case_preparation_report(case: Case, business_profile: BusinessProfile) -> io.BytesIO:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            leftMargin=36,
            rightMargin=36,
            topMargin=36,
            bottomMargin=36,
        )

        styles = getSampleStyleSheet()
        
        # Custom palette
        primary_navy = colors.HexColor("#0F172A")
        slate_blue = colors.HexColor("#1E3A8A")
        slate_gray = colors.HexColor("#475569")
        emerald = colors.HexColor("#047857")
        light_bg = colors.HexColor("#F8FAFC")
        border_gray = colors.HexColor("#E2E8F0")
        accent_red = colors.HexColor("#DC2626")

        # Custom Typography
        title_style = ParagraphStyle(
            "DocTitle",
            parent=styles["Heading1"],
            fontSize=18,
            leading=22,
            textColor=primary_navy,
            fontName="Helvetica-Bold",
        )
        subtitle_style = ParagraphStyle(
            "DocSubTitle",
            parent=styles["Normal"],
            fontSize=10,
            leading=14,
            textColor=slate_gray,
        )
        section_style = ParagraphStyle(
            "SectionHeader",
            parent=styles["Heading2"],
            fontSize=12,
            leading=16,
            textColor=slate_blue,
            fontName="Helvetica-Bold",
            spaceBefore=8,
            spaceAfter=4,
        )
        body_style = ParagraphStyle(
            "DocBody",
            parent=styles["Normal"],
            fontSize=9,
            leading=13,
            textColor=primary_navy,
        )
        body_bold = ParagraphStyle(
            "DocBodyBold",
            parent=body_style,
            fontName="Helvetica-Bold",
        )
        body_muted = ParagraphStyle(
            "DocBodyMuted",
            parent=body_style,
            textColor=slate_gray,
            fontSize=8,
            leading=11,
        )
        disclaimer_style = ParagraphStyle(
            "DocDisclaimer",
            parent=body_style,
            fontSize=7.5,
            leading=10.5,
            textColor=slate_gray,
            alignment=TA_JUSTIFY,
        )

        story: List[Any] = []

        # Header Banner
        header_table = Table(
            [
                [
                    Paragraph("<b>PayPath MSME</b> | Pre-Litigation Case Preparation Report", title_style),
                    Paragraph(f"<b>Ref:</b> {case.reference_code}<br/><b>Date:</b> {date.today().strftime('%d %b %Y')}", ParagraphStyle("RightH", parent=body_style, alignment=TA_RIGHT)),
                ]
            ],
            colWidths=[360, 160],
        )
        header_table.setStyle(
            TableStyle([
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ])
        )
        story.append(header_table)
        story.append(Spacer(1, 4))
        story.append(HRFlowable(width="100%", thickness=1.5, color=slate_blue, spaceBefore=2, spaceAfter=8))

        # Executive Notice Box
        inv = case.invoice
        timeline = LegalEngine.calculate_timeline_and_interest(
            invoice_date=inv.invoice_date,
            delivery_date=inv.delivery_date,
            acceptance_date=inv.acceptance_date,
            has_objection=inv.has_objection,
            objection_date=inv.objection_date,
            objection_resolved_date=inv.objection_resolved_date,
            has_written_agreement=inv.has_written_agreement,
            agreed_credit_days=inv.agreed_credit_days,
            outstanding_principal=inv.outstanding_balance,
            enterprise_type=business_profile.enterprise_type,
            udyam_registered=bool(business_profile.udyam_number),
        )

        status_text = f"<b>CURRENT STAGE:</b> {case.stage_label.upper()} (Stage {case.current_stage}/8) &nbsp;|&nbsp; <b>STATUS:</b> {inv.status.upper()}"
        if timeline["is_overdue"]:
            status_text += f" &nbsp;|&nbsp; <font color='red'><b>OVERDUE BY {timeline['days_overdue']} DAYS</b></font>"

        exec_box = Table(
            [[Paragraph(status_text, body_style)]],
            colWidths=[520],
        )
        exec_box.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), light_bg),
                ("BOX", (0, 0), (-1, -1), 1, border_gray),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ])
        )
        story.append(exec_box)
        story.append(Spacer(1, 8))

        # Parties Information Table
        story.append(Paragraph("1. Commercial Parties Details", section_style))
        parties_data = [
            [
                Paragraph("<b>SUPPLIER / CREDITOR (Claimant)</b>", body_bold),
                Paragraph("<b>BUYER / DEBTOR (Respondent)</b>", body_bold),
            ],
            [
                Paragraph(
                    f"<b>Company:</b> {business_profile.name}<br/>"
                    f"<b>Classification:</b> {business_profile.enterprise_type.capitalize()} Enterprise<br/>"
                    f"<b>Udyam Reg No:</b> {business_profile.udyam_number or 'Not Recorded'}<br/>"
                    f"<b>State / District:</b> {business_profile.state}, {business_profile.district}<br/>"
                    f"<b>Contact:</b> {business_profile.contact_email} | {business_profile.contact_phone}",
                    body_style,
                ),
                Paragraph(
                    f"<b>Company:</b> {inv.buyer_name}<br/>"
                    f"<b>GSTIN:</b> {inv.buyer_gstin or 'Not provided'}<br/>"
                    f"<b>Email:</b> {inv.buyer_contact_email or 'Not recorded'}<br/>"
                    f"<b>Phone:</b> {inv.buyer_contact_phone or 'Not recorded'}<br/>"
                    f"<b>Agreed Terms:</b> {f'{inv.agreed_credit_days} days' if inv.has_written_agreement else 'No written agreement (15d default)'}",
                    body_style,
                ),
            ],
        ]
        parties_table = Table(parties_data, colWidths=[260, 260])
        parties_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EFF6FF")),
                ("BOX", (0, 0), (-1, -1), 0.5, border_gray),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, border_gray),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ])
        )
        story.append(parties_table)
        story.append(Spacer(1, 8))

        # Invoice & Claim Summary Table
        story.append(Paragraph("2. Financial Ledger & Statutory Claim Assessment", section_style))
        
        financial_rows = [
            [Paragraph("<b>Item Description</b>", body_bold), Paragraph("<b>Particulars / Value</b>", body_bold)],
            [Paragraph("Tax Invoice Number", body_style), Paragraph(str(inv.invoice_number), body_style)],
            [Paragraph("Invoice Date", body_style), Paragraph(str(inv.invoice_date), body_style)],
            [Paragraph("Delivery / Acceptance Reference Date", body_style), Paragraph(f"{timeline['reference_date']} ({timeline['reference_type'].replace('_', ' ').capitalize()})", body_style)],
            [Paragraph("Statutory Payment Term", body_style), Paragraph(f"{timeline['statutory_term_days']} days (Ref: {timeline['statutory_rule_citation']})", body_style)],
            [Paragraph("Statutory Due Date", body_style), Paragraph(str(timeline["calculated_due_date"]), body_style)],
            [Paragraph("Original Invoice Total Amount", body_style), Paragraph(f"₹{inv.total_amount:,.2f}", body_style)],
            [Paragraph("Recorded Payments Received", body_style), Paragraph(f"₹{inv.paid_amount:,.2f}", body_style)],
            [Paragraph("<b>Outstanding Principal Balance</b>", body_bold), Paragraph(f"<b>₹{inv.outstanding_balance:,.2f}</b>", body_bold)],
            [
                Paragraph("<b>Estimated Statutory Compound Interest</b><br/><font size='7' color='#475569'>Sec 16 MSMED Act: 3x RBI Bank Rate (20.25% p.a.) compounded monthly</font>", body_style),
                Paragraph(f"<b>₹{timeline['estimated_interest']:,.2f}</b>", body_bold),
            ],
            [
                Paragraph("<b>Total Estimated Claim Amount</b>", body_bold),
                Paragraph(f"<font color='#047857'><b>₹{timeline['total_claimable_amount']:,.2f}</b></font>", body_bold),
            ],
        ]
        
        fin_table = Table(financial_rows, colWidths=[280, 240])
        fin_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F1F5F9")),
                ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#ECFDF5")),
                ("BOX", (0, 0), (-1, -1), 0.5, border_gray),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, border_gray),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ])
        )
        story.append(fin_table)
        story.append(Spacer(1, 8))

        # Income Tax Sec 43B(h) Box
        sec_box = Table(
            [
                [
                    Paragraph(
                        f"<b>STATUTORY SECTION 43B(h) ASSESSMENT:</b><br/>{timeline['section_43b_h_impact']}",
                        body_style,
                    )
                ]
            ],
            colWidths=[520],
        )
        sec_box.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FFFBEB")),
                ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#F59E0B")),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ])
        )
        story.append(sec_box)
        story.append(Spacer(1, 8))

        # Evidence Checklist Table
        story.append(Paragraph("3. Evidence Completeness Audit (MSEFC Readiness)", section_style))
        ev_rows = [
            [
                Paragraph("<b>Required Evidence Artifact</b>", body_bold),
                Paragraph("<b>Category</b>", body_bold),
                Paragraph("<b>Status</b>", body_bold),
                Paragraph("<b>Audit Observation</b>", body_bold),
            ]
        ]
        for it in case.evidence_items:
            status_color = "#047857" if it.status == "provided" else ("#DC2626" if it.status == "missing" else "#D97706")
            ev_rows.append([
                Paragraph(it.title, body_style),
                Paragraph(it.category.replace("_", " ").title(), body_muted),
                Paragraph(f"<font color='{status_color}'><b>{it.status.upper()}</b></font>", body_style),
                Paragraph(it.notes or ("Attached & Verified" if it.status == "provided" else "Required for formal tribunal filing"), body_muted),
            ])
        
        ev_table = Table(ev_rows, colWidths=[200, 90, 80, 150])
        ev_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F1F5F9")),
                ("BOX", (0, 0), (-1, -1), 0.5, border_gray),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, border_gray),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
            ])
        )
        story.append(ev_table)
        story.append(Spacer(1, 8))

        # Chronological Event Log
        story.append(Paragraph("4. Chronological Communications & Follow-Up Log", section_style))
        events = sorted(case.follow_up_events, key=lambda x: x.performed_at)
        if events:
            ev_history_rows = [
                [
                    Paragraph("<b>Date / Time</b>", body_bold),
                    Paragraph("<b>Action Type</b>", body_bold),
                    Paragraph("<b>Summary & Evidence Log</b>", body_bold),
                    Paragraph("<b>Logged By</b>", body_bold),
                ]
            ]
            for ev in events:
                ev_history_rows.append([
                    Paragraph(ev.performed_at.strftime("%d-%b-%Y %H:%M"), body_muted),
                    Paragraph(ev.event_type.replace("_", " ").title(), body_style),
                    Paragraph(f"<b>{ev.summary}</b><br/>{ev.detail or ''}", body_style),
                    Paragraph(ev.recorded_by, body_muted),
                ])
            ev_hist_table = Table(ev_history_rows, colWidths=[90, 110, 240, 80])
            ev_hist_table.setStyle(
                TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F1F5F9")),
                    ("BOX", (0, 0), (-1, -1), 0.5, border_gray),
                    ("INNERGRID", (0, 0), (-1, -1), 0.5, border_gray),
                    ("TOPPADDING", (0, 0), (-1, -1), 3),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                    ("LEFTPADDING", (0, 0), (-1, -1), 5),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ])
            )
            story.append(ev_hist_table)
        else:
            story.append(Paragraph("No follow-up events recorded yet.", body_muted))
        story.append(Spacer(1, 8))

        # Recommended Next Steps & Legal Disclaimers
        story.append(Paragraph("5. Recommended Actionable Next Steps", section_style))
        next_steps = [
            "1. Deliver formal pre-litigation demand notice with 15-day cure window via Registered Post AD and Email.",
            "2. Complete upload of any missing delivery challan or customer signature to substantiate deemed acceptance.",
            "3. If debtor fails to discharge liability within 15 days, prepare formal statement of claim for filing on the official MSME Samadhaan Portal (samadhaan.msme.gov.in) under Section 18 of the MSMED Act, 2006.",
            "4. Inform debtor's statutory auditors regarding pending dues for consideration under Section 43B(h) and CARO 2020 reporting obligations.",
        ]
        for step in next_steps:
            story.append(Paragraph(step, body_style))
            story.append(Spacer(1, 2))

        story.append(Spacer(1, 6))
        story.append(HRFlowable(width="100%", thickness=0.5, color=border_gray, spaceBefore=4, spaceAfter=4))
        story.append(Paragraph(
            "<b>STATUTORY DISCLAIMER & LIMITATIONS OF AID:</b> This Case-Preparation Report is generated by PayPath MSME "
            "as a structured factual compilation and administrative preparation document. It does not constitute a certified legal opinion, "
            "formal judicial summons, or an official MSEFC decree. Calculated interest figures reflect statutory estimates under Section 16 "
            "compounded monthly at 3x the RBI Bank Rate (6.75%), subject to factual verification during Facilitation Council conciliation.",
            disclaimer_style,
        ))

        doc.build(story)
        buffer.seek(0)
        return buffer
